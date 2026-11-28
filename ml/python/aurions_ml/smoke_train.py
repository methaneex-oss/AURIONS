"""Reproducible, synthetic-data-only training proof for the owned baseline.

This intentionally cannot ingest user, web, private, or external corpus data.
It verifies random initialization, next-token optimization and resumable
checkpoint reload. It is not a production dataset admission or activation path.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import json
import os
import tempfile
from pathlib import Path

import torch
import torch.nn.functional as F

from .model import ByteTokenizer, DecoderConfig, DecoderOnlyTransformer


SYNTHETIC_CORPUS = (
    "AURIONS learns patterns from experience. "
    "Evidence changes what the system predicts. "
    "Memory preserves useful context across time. "
) * 48


def _windows(tokens: torch.Tensor, context: int) -> tuple[torch.Tensor, torch.Tensor]:
    if tokens.numel() <= context:
        raise ValueError("training stream is shorter than context")
    starts = torch.arange(tokens.numel() - context)
    x = torch.stack([tokens[i : i + context] for i in starts])
    y = torch.stack([tokens[i + 1 : i + context + 1] for i in starts])
    return x, y


def run_smoke_training(
    output: Path, *, steps: int = 60, seed: int = 1729, resume_from: Path | None = None
) -> dict:
    if steps < 2 or steps > 500:
        raise ValueError("steps must be between 2 and 500")
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)

    tokenizer = ByteTokenizer()
    encoded = tokenizer.encode(SYNTHETIC_CORPUS)
    corpus_digest = hashlib.sha256(SYNTHETIC_CORPUS.encode("utf-8")).hexdigest()
    tokens = torch.tensor(encoded, dtype=torch.long)
    split = int(tokens.numel() * 0.9)
    train_x, train_y = _windows(tokens[:split], 64)
    eval_x, eval_y = _windows(tokens[split - 1 :], 64)

    config = DecoderConfig(context_length=64, width=48, heads=4, layers=2, feed_forward_width=128)
    model = DecoderOnlyTransformer(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.01)

    def evaluate(x: torch.Tensor, y: torch.Tensor) -> float:
        model.eval()
        if len(x) == 0 or len(x) != len(y):
            raise ValueError("evaluation windows must be non-empty and aligned")
        sample_count = min(8, len(x))
        indices = [0] if sample_count == 1 else [
            index * (len(x) - 1) // (sample_count - 1)
            for index in range(sample_count)
        ]
        total_loss = 0.0
        total_tokens = 0
        with torch.no_grad():
            for index in indices:
                logits = model(x[index:index + 1])
                target = y[index:index + 1]
                total_loss += float(F.cross_entropy(
                    logits.reshape(-1, config.vocab_size),
                    target.reshape(-1), reduction="sum"
                ))
                total_tokens += target.numel()
        return total_loss / total_tokens

    initial_eval_loss = evaluate(eval_x, eval_y)
    start_step = 0
    if resume_from is not None:
        previous = torch.load(resume_from, map_location="cpu", weights_only=True)
        expected = {
            "format": "aurions-model-checkpoint-v1",
            "artifact_kind": "synthetic-training-smoke-only",
            "initialization": "random",
            "objective": "autoregressive-next-token-prediction",
            "architecture": model.architecture_manifest(),
        }
        for key, value in expected.items():
            if previous.get(key) != value:
                raise ValueError(f"checkpoint is incompatible: {key}")
        if previous.get("training", {}).get("seed") != seed:
            raise ValueError("checkpoint is incompatible: seed")
        if previous.get("training", {}).get("corpus_sha256") != corpus_digest:
            raise ValueError("checkpoint is incompatible: corpus_sha256")
        model.load_state_dict(previous["state_dict"])
        optimizer.load_state_dict(previous["optimizer_state_dict"])
        start_step = int(previous["training"]["completed_steps"])
        if steps <= start_step:
            raise ValueError("target steps must exceed checkpoint completed_steps")
        initial_eval_loss = float(previous["training"]["initial_heldout_loss"])
        torch.set_rng_state(previous["torch_rng_state"])

    model.train()
    batch_size = min(16, len(train_x))
    start_positions = len(train_x) - batch_size + 1
    stride = 7
    while math.gcd(stride, start_positions) != 1:
        stride += 1
    for step in range(start_step, steps):
        index = (step * stride) % start_positions
        batch_x = train_x[index : index + batch_size]
        batch_y = train_y[index : index + batch_size]
        optimizer.zero_grad(set_to_none=True)
        logits = model(batch_x)
        loss = F.cross_entropy(logits.reshape(-1, config.vocab_size), batch_y.reshape(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    final_eval_loss = evaluate(eval_x, eval_y)
    if not final_eval_loss < initial_eval_loss:
        raise RuntimeError(
            f"smoke training did not improve held-out synthetic loss: "
            f"{initial_eval_loss:.6f} -> {final_eval_loss:.6f}"
        )

    payload = {
        "format": "aurions-model-checkpoint-v1",
        "artifact_kind": "synthetic-training-smoke-only",
        "candidate_status": "quarantined",
        "activation_eligible": False,
        "initialization": "random",
        "objective": "autoregressive-next-token-prediction",
        "corpus_sha256": corpus_digest,
        "tokenizer": {"name": tokenizer.VERSION, "vocab_size": tokenizer.VOCAB_SIZE},
        "architecture": model.architecture_manifest(),
        "training": {
            "seed": seed,
            "steps": steps,
            "completed_steps": steps,
            "corpus_sha256": corpus_digest,
            "corpus_kind": "generated-test-fixture",
            "initial_heldout_loss": initial_eval_loss,
            "final_heldout_loss": final_eval_loss,
        },
        "state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "torch_rng_state": torch.get_rng_state(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, prefix=output.name, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        torch.save(payload, temporary)
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    reloaded = torch.load(output, map_location="cpu", weights_only=True)
    restored = DecoderOnlyTransformer(config)
    restored.load_state_dict(reloaded["state_dict"])
    restored.eval()
    model.eval()
    probe = torch.tensor([tokenizer.encode("AURIONS learns")[:-1]], dtype=torch.long)
    with torch.no_grad():
        max_reload_delta = float((model(probe) - restored(probe)).abs().max())
    if max_reload_delta != 0.0:
        raise RuntimeError("checkpoint reload changed model output")

    return {
        "artifact": str(output),
        "artifact_kind": payload["artifact_kind"],
        "candidate_status": payload["candidate_status"],
        "activation_eligible": payload["activation_eligible"],
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "steps": steps,
        "initial_heldout_loss": initial_eval_loss,
        "final_heldout_loss": final_eval_loss,
        "max_reload_logit_delta": max_reload_delta,
        "corpus_sha256": corpus_digest,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=60)
    parser.add_argument("--resume-from", type=Path)
    args = parser.parse_args()
    print(json.dumps(
        run_smoke_training(args.output, steps=args.steps, resume_from=args.resume_from),
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
