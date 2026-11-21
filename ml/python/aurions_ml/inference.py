"""Local greedy inference for an AURIONS model checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from .model import ByteTokenizer, DecoderConfig, DecoderOnlyTransformer


def load_smoke_model(checkpoint: Path) -> tuple[DecoderOnlyTransformer, ByteTokenizer]:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if payload.get("format") != "aurions-model-checkpoint-v1":
        raise ValueError("unsupported checkpoint format")
    if payload.get("artifact_kind") != "synthetic-training-smoke-only":
        raise ValueError("this inference path only accepts smoke-test checkpoints")
    if payload.get("activation_eligible") is not False:
        raise ValueError("smoke checkpoint must remain non-activatable")
    tokenizer_metadata = payload.get("tokenizer", {})
    tokenizer = ByteTokenizer()
    if tokenizer_metadata != {"name": tokenizer.VERSION, "vocab_size": tokenizer.VOCAB_SIZE}:
        raise ValueError("checkpoint tokenizer identity does not match this runtime")
    architecture = dict(payload.get("architecture", {}))
    if architecture.pop("architecture", None) != "decoder-only-causal-transformer":
        raise ValueError("unsupported model architecture")
    model = DecoderOnlyTransformer(DecoderConfig(**architecture))
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model, tokenizer


def generate(checkpoint: Path, prompt: str, *, max_new_tokens: int = 32) -> str:
    if not prompt:
        raise ValueError("prompt must not be empty")
    if max_new_tokens < 1 or max_new_tokens > 128:
        raise ValueError("max_new_tokens must be between 1 and 128")
    model, tokenizer = load_smoke_model(checkpoint)
    generated = tokenizer.encode(prompt)
    with torch.no_grad():
        for _ in range(max_new_tokens):
            context = torch.tensor(
                [generated[-model.config.context_length :]], dtype=torch.long
            )
            next_id = int(model(context)[0, -1].argmax().item())
            if next_id == tokenizer.EOS:
                break
            generated.append(next_id)
    return tokenizer.decode(generated)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=32)
    args = parser.parse_args()
    print(generate(args.checkpoint, args.prompt, max_new_tokens=args.max_new_tokens))


if __name__ == "__main__":
    main()
