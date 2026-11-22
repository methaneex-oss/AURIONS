"""Local candidate inference for quarantined AURIONS model checkpoints.

This path is for controlled preview/evaluation only. It never activates a
candidate or treats its output as trusted authority.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any

import torch

from .model import ByteTokenizer, DecoderConfig, DecoderOnlyTransformer


def _validate_dataset_lineage(lineage: Any) -> None:
    if not isinstance(lineage, dict):
        raise ValueError("dataset-trained candidate is missing dataset lineage")
    for field in ("manifest_id", "manifest_digest", "admission_id", "owner_ref", "model_family_ref"):
        if not isinstance(lineage.get(field), str) or not lineage[field]:
            raise ValueError(f"candidate dataset lineage is missing {field}")
    if re.fullmatch(r"[0-9a-f]{64}", lineage["manifest_digest"]) is None:
        raise ValueError("candidate manifest digest is invalid")
    sources = lineage.get("sources")
    splits = lineage.get("splits")
    if not isinstance(sources, list) or not sources:
        raise ValueError("candidate dataset lineage has no admitted sources")
    if not isinstance(splits, list) or {item.get("split_type") for item in splits if isinstance(item, dict)} != {
        "train", "validation", "held_out"
    } or len(splits) != 3:
        raise ValueError("candidate dataset lineage must contain exactly three declared splits")
    for source in sources:
        if not isinstance(source, dict) or not all(
            isinstance(source.get(field), str) and source[field]
            for field in ("source_ref", "source_content_sha256", "source_artifact_ref",
                          "authorization_id", "authorization_record_digest")
        ):
            raise ValueError("candidate source lineage is incomplete")
    for split in splits:
        if not isinstance(split, dict) or not all(
            isinstance(split.get(field), str) and split[field]
            for field in ("split_type", "artifact_ref", "content_sha256")
        ):
            raise ValueError("candidate split lineage is incomplete")
        if re.fullmatch(r"[0-9a-f]{64}", split["content_sha256"]) is None:
            raise ValueError("candidate split digest is invalid")


def load_candidate_model(checkpoint: Path) -> tuple[DecoderOnlyTransformer, ByteTokenizer]:
    """Load a quarantined smoke or admitted-data candidate for preview only."""
    payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if not isinstance(payload, dict) or payload.get("format") != "aurions-model-checkpoint-v1":
        raise ValueError("unsupported checkpoint format")
    artifact_kind = payload.get("artifact_kind")
    if artifact_kind not in {"synthetic-training-smoke-only", "dataset-trained-candidate"}:
        raise ValueError("unsupported candidate artifact kind")
    if payload.get("candidate_status") != "quarantined" or payload.get("activation_eligible") is not False:
        raise ValueError("candidate preview requires a quarantined, non-activatable checkpoint")
    if artifact_kind == "dataset-trained-candidate":
        _validate_dataset_lineage(payload.get("dataset_lineage"))
        training = payload.get("training")
        if not isinstance(training, dict):
            raise ValueError("dataset-trained candidate is missing training evidence")
        for field in ("initial_validation_loss", "final_validation_loss",
                      "initial_held_out_loss", "held_out_loss"):
            value = training.get(field)
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"candidate training evidence has invalid {field}")
        if not training["final_validation_loss"] < training["initial_validation_loss"]:
            raise ValueError("candidate has no demonstrated validation-loss improvement")
        if not training["held_out_loss"] < training["initial_held_out_loss"]:
            raise ValueError("candidate has no demonstrated held-out-loss improvement")
    tokenizer_metadata = payload.get("tokenizer", {})
    tokenizer = ByteTokenizer()
    if tokenizer_metadata != {"name": tokenizer.VERSION, "vocab_size": tokenizer.VOCAB_SIZE}:
        raise ValueError("checkpoint tokenizer identity does not match this runtime")
    architecture = dict(payload.get("architecture", {}))
    if architecture.pop("architecture", None) != "decoder-only-causal-transformer":
        raise ValueError("unsupported model architecture")
    model = DecoderOnlyTransformer(DecoderConfig(**architecture))
    state_dict = payload.get("state_dict")
    if not isinstance(state_dict, dict):
        raise ValueError("checkpoint is missing model weights")
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return model, tokenizer


def generate(checkpoint: Path, prompt: str, *, max_new_tokens: int = 32) -> str:
    if not prompt:
        raise ValueError("prompt must not be empty")
    if max_new_tokens < 1 or max_new_tokens > 128:
        raise ValueError("max_new_tokens must be between 1 and 128")
    model, tokenizer = load_candidate_model(checkpoint)
    # A prompt is a prefix, not a completed training sample: append BOS but
    # never EOS before asking the model to predict the next token.
    generated = [tokenizer.BOS, *tokenizer.encode(prompt, add_boundaries=False)]
    with torch.inference_mode():
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
