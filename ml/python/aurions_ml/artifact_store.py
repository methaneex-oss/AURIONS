"""Immutable local content-addressed artifact storage with digest verification."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

_REFERENCE = re.compile(r"^artifact://sha256/([0-9a-f]{64})$")


class ArtifactIntegrityError(RuntimeError):
    """An artifact reference, file or expected digest is invalid."""


@dataclass(frozen=True)
class ArtifactRef:
    uri: str
    sha256: str
    size_bytes: int


class ArtifactStore:
    """Local immutable artifact store; paths are derived only from SHA-256 IDs."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    @staticmethod
    def _digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _path_for_digest(self, digest: str) -> Path:
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ArtifactIntegrityError("invalid SHA-256 digest")
        return self.root / "sha256" / digest[:2] / digest

    def put_bytes(self, data: bytes) -> ArtifactRef:
        if not isinstance(data, bytes):
            raise TypeError("artifact content must be bytes")
        digest = self._digest(data)
        destination = self._path_for_digest(digest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            existing = destination.read_bytes()
            if self._digest(existing) != digest:
                raise ArtifactIntegrityError("existing content-addressed artifact is corrupt")
        else:
            temporary_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    dir=destination.parent, prefix=".artifact-", delete=False
                ) as handle:
                    temporary_path = Path(handle.name)
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                try:
                    os.link(temporary_path, destination)
                except FileExistsError:
                    if self._digest(destination.read_bytes()) != digest:
                        raise ArtifactIntegrityError("concurrent artifact write produced corrupt content")
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)
        return ArtifactRef(f"artifact://sha256/{digest}", digest, len(data))

    def get_bytes(self, artifact_ref: str, *, expected_sha256: str) -> bytes:
        match = _REFERENCE.fullmatch(artifact_ref or "")
        if match is None:
            raise ArtifactIntegrityError("unsupported artifact reference")
        reference_digest = match.group(1)
        if reference_digest != expected_sha256:
            raise ArtifactIntegrityError("artifact reference does not match expected digest")
        path = self._path_for_digest(reference_digest)
        try:
            data = path.read_bytes()
        except OSError as error:
            raise ArtifactIntegrityError("artifact content is unavailable") from error
        if self._digest(data) != expected_sha256:
            raise ArtifactIntegrityError("artifact content digest mismatch")
        return data
