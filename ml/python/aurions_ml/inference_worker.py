"""Versioned JSONL worker for bounded inference with quarantined candidates.

The parent process validates requests, bounds IPC and enforces a timeout. The
worker's application protocol restricts it to artifact preview and prevents
model activation or direct cognitive-state mutation. This is NOT an OS sandbox:
the Python process still runs with the launching user's filesystem and network
permissions unless the deployment adds platform-specific isolation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import BinaryIO

from .artifact_store import ArtifactIntegrityError, ArtifactStore
from .inference import generate_from_bytes

PROTOCOL_VERSION = "1.0"
JOB_TYPE = "candidate_inference_preview"
_ARTIFACT_REF = re.compile(r"^artifact://sha256/([0-9a-f]{64})$")
_REQUIRED_FIELDS = {
    "protocol_version",
    "job_id",
    "job_type",
    "candidate_artifact_ref",
    "prompt",
    "max_new_tokens",
}
MAX_PROMPT_BYTES = 8192
MAX_OUTPUT_BYTES = 65536


class InvalidRequest(ValueError):
    """A JSONL request does not match the worker protocol."""


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidRequest("duplicate JSON object key")
        result[key] = value
    return result


def _parse_request(line: bytes) -> dict[str, object]:
    try:
        decoded = line.decode("utf-8")
        request = json.loads(decoded, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InvalidRequest("request must be one UTF-8 JSON object") from error
    if not isinstance(request, dict) or set(request) != _REQUIRED_FIELDS:
        raise InvalidRequest("request fields do not match protocol version 1.0")
    if request["protocol_version"] != PROTOCOL_VERSION:
        raise InvalidRequest("unsupported protocol version")
    if request["job_type"] != JOB_TYPE:
        raise InvalidRequest("unsupported worker job type")
    job_id = request["job_id"]
    if not isinstance(job_id, str):
        raise InvalidRequest("job_id must be a UUID string")
    try:
        if str(uuid.UUID(job_id)) != job_id:
            raise ValueError("non-canonical UUID")
    except ValueError as error:
        raise InvalidRequest("job_id must be a canonical UUID string") from error
    artifact_ref = request["candidate_artifact_ref"]
    if not isinstance(artifact_ref, str) or _ARTIFACT_REF.fullmatch(artifact_ref) is None:
        raise InvalidRequest("candidate_artifact_ref must be a SHA-256 artifact URI")
    prompt = request["prompt"]
    if not isinstance(prompt, str) or not prompt:
        raise InvalidRequest("prompt must be a non-empty string")
    try:
        prompt_bytes = prompt.encode("utf-8")
    except UnicodeEncodeError as error:
        raise InvalidRequest("prompt contains invalid Unicode") from error
    if len(prompt_bytes) > MAX_PROMPT_BYTES:
        raise InvalidRequest("prompt exceeds the 8192-byte limit")
    max_new_tokens = request["max_new_tokens"]
    if isinstance(max_new_tokens, bool) or not isinstance(max_new_tokens, int):
        raise InvalidRequest("max_new_tokens must be an integer")
    if not 1 <= max_new_tokens <= 128:
        raise InvalidRequest("max_new_tokens must be between 1 and 128")
    return request


def _error(job_id: str | None, code: str) -> dict[str, object]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "job_id": job_id,
        "status": "failed",
        "error_code": code,
    }


def _handle_line(line: bytes, artifact_store: ArtifactStore) -> dict[str, object]:
    try:
        request = _parse_request(line)
    except InvalidRequest:
        return _error(None, "invalid_request")

    job_id = str(request["job_id"])
    artifact_ref = str(request["candidate_artifact_ref"])
    match = _ARTIFACT_REF.fullmatch(artifact_ref)
    assert match is not None
    digest = match.group(1)
    try:
        checkpoint = artifact_store.get_bytes(artifact_ref, expected_sha256=digest)
    except ArtifactIntegrityError:
        return _error(job_id, "artifact_unavailable")

    try:
        generated = generate_from_bytes(
            checkpoint,
            str(request["prompt"]),
            max_new_tokens=int(request["max_new_tokens"]),
        )
    except (ValueError, RuntimeError):
        return _error(job_id, "candidate_rejected")
    except Exception:
        print("candidate inference failed", file=sys.stderr)
        return _error(job_id, "inference_failed")

    return {
        "protocol_version": PROTOCOL_VERSION,
        "job_id": job_id,
        "status": "completed",
        "candidate_status": "quarantined",
        "candidate_artifact_sha256": digest,
        "generated_text": generated,
        "max_new_tokens": int(request["max_new_tokens"]),
    }


def _write_response(output_stream: BinaryIO, response: dict[str, object]) -> None:
    encoded = json.dumps(
        response, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    if len(encoded) > MAX_OUTPUT_BYTES:
        encoded = json.dumps(
            _error(response.get("job_id") if isinstance(response.get("job_id"), str) else None,
                   "response_too_large"),
            separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
    output_stream.write(encoded + b"\n")
    output_stream.flush()


def serve(
    artifact_store: ArtifactStore,
    input_stream: BinaryIO = sys.stdin.buffer,
    output_stream: BinaryIO = sys.stdout.buffer,
    *,
    max_message_bytes: int = 16384,
) -> None:
    if max_message_bytes < 256 or max_message_bytes > 1_048_576:
        raise ValueError("max_message_bytes must be between 256 and 1048576")
    while True:
        line = input_stream.readline(max_message_bytes + 1)
        if not line:
            break
        if len(line) > max_message_bytes:
            while line and not line.endswith(b"\n"):
                line = input_stream.readline(max_message_bytes + 1)
            _write_response(output_stream, _error(None, "request_too_large"))
            continue
        if line.endswith(b"\n"):
            line = line[:-1]
        if line.endswith(b"\r"):
            line = line[:-1]
        _write_response(output_stream, _handle_line(line, artifact_store))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-store", type=Path, required=True)
    parser.add_argument("--max-message-bytes", type=int, default=16384)
    args = parser.parse_args()
    import torch

    torch.set_num_threads(1)
    serve(
        ArtifactStore(args.artifact_store),
        max_message_bytes=args.max_message_bytes,
    )


if __name__ == "__main__":
    main()
