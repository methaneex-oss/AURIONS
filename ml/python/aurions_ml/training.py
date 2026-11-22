"""Train a quarantined AURIONS model candidate from an admitted dataset manifest."""

from __future__ import annotations

import io
from dataclasses import dataclass

import torch
import torch.nn.functional as F

from .admission import AdmissionResult
from .artifact_store import ArtifactIntegrityError, ArtifactRef, ArtifactStore
from .model import ByteTokenizer, DecoderConfig, DecoderOnlyTransformer


@dataclass(frozen=True)
class TrainingResult:
    checkpoint: ArtifactRef
    candidate_status: str
    activation_eligible: bool
    parameter_count: int
    steps: int
    initial_validation_loss: float
    final_validation_loss: float
    initial_held_out_loss: float
    held_out_loss: float
    admission_manifest_id: str
    admission_id: str


def _make_windows(text: str, tokenizer: ByteTokenizer, context: int) -> tuple[torch.Tensor, torch.Tensor]:
    tokens = torch.tensor(tokenizer.encode(text), dtype=torch.long)
    if tokens.numel() <= context + 1:
        raise ValueError("dataset split is too short for the configured context")
    starts = torch.arange(tokens.numel() - context)
    inputs = torch.stack([tokens[index : index + context] for index in starts])
    targets = torch.stack([tokens[index + 1 : index + context + 1] for index in starts])
    return inputs, targets


def _evaluate(
    model: DecoderOnlyTransformer,
    inputs: torch.Tensor,
    targets: torch.Tensor,
) -> float:
    model.eval()
    with torch.no_grad():
        batch_inputs = inputs[: min(32, len(inputs))]
        batch_targets = targets[: len(batch_inputs)]
        logits = model(batch_inputs)
        return float(F.cross_entropy(logits.reshape(-1, model.config.vocab_size), batch_targets.reshape(-1)))


def train_admitted_dataset(
    admission: AdmissionResult,
    artifact_store: ArtifactStore,
    *,
    admission_id: str,
    steps: int = 60,
    seed: int = 1729,
) -> TrainingResult:
    """Verify admitted artifact bytes, train next-token prediction, and store a candidate.

    All three manifest splits are mandatory. Source artifacts are independently
    re-hashed before training. The result remains quarantined and non-activatable.
    """
    if admission.training_purpose != "foundation_pretraining":
        raise ValueError("only the foundation_pretraining objective is implemented")
    if steps < 2 or steps > 500:
        raise ValueError("steps must be between 2 and 500")
    if not admission_id:
        raise ValueError("admission_id is required")
    split_map = {split.split_type: split for split in admission.splits}
    if set(split_map) != {"train", "validation", "held_out"} or len(split_map) != 3:
        raise ValueError("admitted manifest must contain exactly train, validation and held_out splits")
    split_refs = {split.artifact_ref for split in admission.splits}
    declared_derived = set(admission.derived_artifact_refs)
    source_lineage_refs = {
        ref for source in admission.sources for ref in source.transformation_lineage_refs
    }
    if not split_refs.issubset(declared_derived) or not split_refs.issubset(source_lineage_refs):
        raise ValueError("dataset split artifacts are not bound to source and manifest lineage")

    source_lineage = []
    for source in admission.sources:
        artifact_store.get_bytes(
            source.source_artifact_ref, expected_sha256=source.source_content_sha256
        )
        source_lineage.append({
            "source_ref": source.source_ref,
            "source_content_sha256": source.source_content_sha256,
            "source_artifact_ref": source.source_artifact_ref,
            "authorization_id": source.authorization_id,
            "authorization_record_digest": source.authorization_record_digest,
            "approval_decision_ref": source.approval_decision_ref,
            "transformation_lineage_refs": list(source.transformation_lineage_refs),
        })

    split_text: dict[str, str] = {}
    split_lineage = []
    for split_type in ("train", "validation", "held_out"):
        split = split_map[split_type]
        content = artifact_store.get_bytes(split.artifact_ref, expected_sha256=split.content_sha256)
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ArtifactIntegrityError(f"{split_type} split is not valid UTF-8 text") from error
        if not decoded.strip():
            raise ValueError(f"{split_type} split is empty")
        split_text[split_type] = decoded
        split_lineage.append({
            "split_type": split_type,
            "artifact_ref": split.artifact_ref,
            "content_sha256": split.content_sha256,
        })

    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    tokenizer = ByteTokenizer()
    config = DecoderConfig(
        context_length=64, width=48, heads=4, layers=2, feed_forward_width=128
    )
    train_x, train_y = _make_windows(split_text["train"], tokenizer, config.context_length)
    validation_x, validation_y = _make_windows(
        split_text["validation"], tokenizer, config.context_length
    )
    held_out_x, held_out_y = _make_windows(
        split_text["held_out"], tokenizer, config.context_length
    )

    model = DecoderOnlyTransformer(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.01)
    initial_validation_loss = _evaluate(model, validation_x, validation_y)
    initial_held_out_loss = _evaluate(model, held_out_x, held_out_y)

    model.train()
    for step in range(steps):
        index = (step * 7) % max(1, len(train_x) - 16)
        batch_x = train_x[index : index + 16]
        batch_y = train_y[index : index + 16]
        optimizer.zero_grad(set_to_none=True)
        logits = model(batch_x)
        loss = F.cross_entropy(logits.reshape(-1, config.vocab_size), batch_y.reshape(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    final_validation_loss = _evaluate(model, validation_x, validation_y)
    held_out_loss = _evaluate(model, held_out_x, held_out_y)
    if not final_validation_loss < initial_validation_loss:
        raise RuntimeError(
            "training failed to improve validation loss: "
            f"{initial_validation_loss:.6f} -> {final_validation_loss:.6f}"
        )
    if not held_out_loss < initial_held_out_loss:
        raise RuntimeError(
            "training failed to improve held-out loss: "
            f"{initial_held_out_loss:.6f} -> {held_out_loss:.6f}"
        )

    payload = {
        "format": "aurions-model-checkpoint-v1",
        "artifact_kind": "dataset-trained-candidate",
        "candidate_status": "quarantined",
        "activation_eligible": False,
        "activation_block_reason": "candidate evaluation and owner activation are not implemented",
        "initialization": "random",
        "objective": "autoregressive-next-token-prediction",
        "tokenizer": {"name": tokenizer.VERSION, "vocab_size": tokenizer.VOCAB_SIZE},
        "architecture": model.architecture_manifest(),
        "dataset_lineage": {
            "manifest_id": admission.manifest_id,
            "manifest_digest": admission.manifest_digest,
            "admission_id": admission_id,
            "owner_ref": admission.owner_ref,
            "model_family_ref": admission.model_family_ref,
            "training_purpose": admission.training_purpose,
            "sources": source_lineage,
            "splits": split_lineage,
            "derived_artifact_refs": list(admission.derived_artifact_refs),
        },
        "training": {
            "seed": seed,
            "steps": steps,
            "initial_validation_loss": initial_validation_loss,
            "final_validation_loss": final_validation_loss,
            "initial_held_out_loss": initial_held_out_loss,
            "held_out_loss": held_out_loss,
            "corpus_kind": "admitted-manifest-artifacts",
            "data_scope": "manifest-authorized-splits-only",
        },
        "state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "torch_rng_state": torch.get_rng_state(),
    }
    buffer = io.BytesIO()
    torch.save(payload, buffer)
    checkpoint = artifact_store.put_bytes(buffer.getvalue())
    stored = artifact_store.get_bytes(checkpoint.uri, expected_sha256=checkpoint.sha256)
    loaded = torch.load(io.BytesIO(stored), map_location="cpu", weights_only=True)
    if (loaded.get("dataset_lineage", {}).get("manifest_digest") != admission.manifest_digest or
            loaded.get("activation_eligible") is not False):
        raise RuntimeError("stored checkpoint failed lineage/quarantine verification")

    return TrainingResult(
        checkpoint=checkpoint,
        candidate_status="quarantined",
        activation_eligible=False,
        parameter_count=sum(parameter.numel() for parameter in model.parameters()),
        steps=steps,
        initial_validation_loss=initial_validation_loss,
        final_validation_loss=final_validation_loss,
        initial_held_out_loss=initial_held_out_loss,
        held_out_loss=held_out_loss,
        admission_manifest_id=admission.manifest_id,
        admission_id=admission_id,
    )
