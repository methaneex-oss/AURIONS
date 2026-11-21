import pytest

from aurions_ml.artifact_store import ArtifactIntegrityError, ArtifactStore


def test_content_addressed_artifact_round_trip_and_digest_binding(tmp_path):
    store = ArtifactStore(tmp_path / "objects")
    content = b"immutable artifact payload"
    reference = store.put_bytes(content)
    assert reference.uri == f"artifact://sha256/{reference.sha256}"
    assert store.get_bytes(reference.uri, expected_sha256=reference.sha256) == content
    with pytest.raises(ArtifactIntegrityError, match="expected digest"):
        store.get_bytes(reference.uri, expected_sha256="0" * 64)


def test_content_addressed_artifact_detects_corruption(tmp_path):
    store = ArtifactStore(tmp_path / "objects")
    reference = store.put_bytes(b"original")
    digest_path = store.root / "sha256" / reference.sha256[:2] / reference.sha256
    digest_path.write_bytes(b"tampered")
    with pytest.raises(ArtifactIntegrityError, match="content digest mismatch"):
        store.get_bytes(reference.uri, expected_sha256=reference.sha256)


def test_artifact_reference_cannot_escape_store(tmp_path):
    store = ArtifactStore(tmp_path / "objects")
    with pytest.raises(ArtifactIntegrityError, match="unsupported artifact reference"):
        store.get_bytes("../../etc/passwd", expected_sha256="0" * 64)
