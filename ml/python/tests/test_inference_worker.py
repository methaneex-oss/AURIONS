import io
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import torch

from aurions_ml.artifact_store import ArtifactStore
from aurions_ml.smoke_train import run_smoke_training


def _candidate_artifact(tmp_path: Path) -> tuple[ArtifactStore, str]:
    checkpoint_path = tmp_path / "candidate.pt"
    run_smoke_training(checkpoint_path, steps=30)
    store = ArtifactStore(tmp_path / "artifacts")
    reference = store.put_bytes(checkpoint_path.read_bytes())
    return store, reference.uri


def _request(artifact_ref: str, **overrides) -> dict:
    request = {
        "protocol_version": "1.0",
        "job_id": str(uuid.uuid4()),
        "job_type": "candidate_inference_preview",
        "candidate_artifact_ref": artifact_ref,
        "prompt": "AURIONS",
        "max_new_tokens": 8,
    }
    request.update(overrides)
    return request


def _run_worker(store: ArtifactStore, input_text: str, *, max_message_bytes: int = 16384):
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", "ml/python")
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "aurions_ml.inference_worker",
            "--artifact-store",
            str(store.root),
            "--max-message-bytes",
            str(max_message_bytes),
        ],
        input=input_text,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_jsonl_worker_returns_bounded_quarantined_candidate_preview(tmp_path: Path):
    store, artifact_ref = _candidate_artifact(tmp_path)
    request = _request(artifact_ref)
    completed = _run_worker(store, json.dumps(request) + "\\n")

    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response["protocol_version"] == "1.0"
    assert response["job_id"] == request["job_id"]
    assert response["status"] == "completed"
    assert response["candidate_status"] == "quarantined"
    assert response["candidate_artifact_sha256"] == artifact_ref.rsplit("/", 1)[1]
    assert response["generated_text"].startswith("AURIONS")
    assert len(response["generated_text"].encode("utf-8")) <= 8192 + 128 * 4


def test_jsonl_worker_rejects_unknown_fields_and_duplicate_keys(tmp_path: Path):
    store, artifact_ref = _candidate_artifact(tmp_path)
    request = _request(artifact_ref, unexpected="must be rejected")
    duplicate = (
        '{"protocol_version":"1.0","protocol_version":"1.0",'
        f'"job_id":"{uuid.uuid4()}","job_type":"candidate_inference_preview",'
        f'"candidate_artifact_ref":"{artifact_ref}","prompt":"AURIONS","max_new_tokens":8}}'
    )
    completed = _run_worker(store, json.dumps(request) + "\\n" + duplicate + "\\n")

    assert completed.returncode == 0, completed.stderr
    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert len(responses) == 2
    assert all(item["status"] == "failed" for item in responses)
    assert all(item["error_code"] == "invalid_request" for item in responses)


def test_jsonl_worker_refuses_candidate_marked_activation_eligible(tmp_path: Path):
    store, artifact_ref = _candidate_artifact(tmp_path)
    digest = artifact_ref.rsplit("/", 1)[1]
    payload = torch.load(
        io.BytesIO(store.get_bytes(artifact_ref, expected_sha256=digest)),
        map_location="cpu",
        weights_only=True,
    )
    payload["activation_eligible"] = True
    buffer = io.BytesIO()
    torch.save(payload, buffer)
    active_ref = store.put_bytes(buffer.getvalue()).uri
    completed = _run_worker(store, json.dumps(_request(active_ref)) + "\\n")

    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response["status"] == "failed"
    assert response["error_code"] == "candidate_rejected"


def test_jsonl_worker_bounds_oversized_messages(tmp_path: Path):
    store, artifact_ref = _candidate_artifact(tmp_path)
    oversized = json.dumps(_request(artifact_ref)) + (" " * 400) + "\\n"
    completed = _run_worker(store, oversized, max_message_bytes=256)

    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response["status"] == "failed"
    assert response["error_code"] == "request_too_large"
