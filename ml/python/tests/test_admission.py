import hashlib
import json
import sqlite3
import uuid
from pathlib import Path

import pytest

from aurions_ml.admission import AdmissionDenied, _connect_read_only, admit_dataset
from aurions_ml.artifact_store import ArtifactStore
from aurions_ml.training import train_admitted_dataset

OWNER = "owner:aurions-test"
MODEL = "model:aurions-base"
PURPOSE = "foundation_pretraining"
MANIFEST = uuid.UUID("f6e8bb55-8a73-4ef1-87c6-0f9f7a8f2a10")
AUTHORIZATION = uuid.UUID("4b8d98c7-6e25-4e2d-91d5-6f0a3c3f1011")
APPROVAL = uuid.UUID("c9f5f0bd-4f17-4a5d-a2c7-16e63b2a9001")
DECISION = uuid.UUID("2f0c3c5a-0e83-4c4d-9d7f-22bb1cce0002")
DIGEST = "a" * 64
TERMS = "b" * 64
POLICY = "c" * 64
PROJECT = "project:aurions"
DATASET_SCOPE = "scope:foundation"
POLICY_REF = "policy:v1"


def build_databases(tmp_path: Path, *, status="active", expires_at=None, training="allow",
                    terms_digest=TERMS, lifecycle="sealed", seal=True, revoked=False,
                    private_classification="public", private_auth=None, include_auth=True,
                    artifact_store: ArtifactStore | None = None):
    governance_path = tmp_path / "governance.db"
    memory_path = tmp_path / "memory.db"
    source_bytes = ("Authorized synthetic source for AURIONS model tests. " * 80).encode("utf-8")
    source_digest = hashlib.sha256(source_bytes).hexdigest() if artifact_store else DIGEST
    source_artifact_ref = artifact_store.put_bytes(source_bytes).uri if artifact_store else "artifact:source-one"
    split_artifacts = {}
    for split_type, sentence in {
        "train": "AURIONS learns from authorized training experience. ",
        "validation": "AURIONS evaluates predictions on validation experience. ",
        "held_out": "AURIONS is evaluated on held out experience. ",
    }.items():
        split_bytes = (sentence * 100).encode("utf-8")
        split_artifacts[split_type] = (
            artifact_store.put_bytes(split_bytes).uri,
            hashlib.sha256(split_bytes).hexdigest(),
        ) if artifact_store else (f"split:{split_type}", DIGEST)
    g = sqlite3.connect(governance_path)
    g.executescript("""
        CREATE TABLE dataset_source_authorizations (
            authorization_id BLOB, authorization_revision INTEGER, owner_ref TEXT,
            source_ref TEXT, source_content_sha256 TEXT, source_origin_json TEXT,
            authorization_basis TEXT, license_or_terms_ref TEXT, license_or_terms_digest TEXT,
            permitted_purposes_json TEXT, training_permission TEXT,
            memory_retention_permission TEXT, private_data_classification TEXT,
            private_data_authorization_ref TEXT, project_ref TEXT, model_family_ref TEXT,
            dataset_scope_ref TEXT, policy_version_ref TEXT, valid_from_ms INTEGER,
            expires_at_ms INTEGER, status TEXT, revoked_at_ms INTEGER, record_digest TEXT,
            approval_request_id BLOB, decision_ref TEXT
        );
        CREATE TABLE approval_requests (
            request_id BLOB, owner_ref TEXT, operation_digest TEXT, requested_at_ms INTEGER,
            expires_at_ms INTEGER, state TEXT
        );
        CREATE TABLE approval_decisions (
            decision_id BLOB, request_id BLOB, authenticated_owner_ref TEXT, decision TEXT,
            approved_digest TEXT, decided_at_ms INTEGER, authentication_context_ref TEXT
        );
        CREATE TABLE dataset_source_authorization_revocations (
            authorization_id BLOB, authorization_record_digest TEXT
        );
    """)
    if include_auth:
        g.execute("""INSERT INTO dataset_source_authorizations VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            AUTHORIZATION.bytes, 1, OWNER, "source:one", source_digest, "{}", "license",
            "license:permissive", terms_digest, json.dumps([PURPOSE]), training, "deny",
            private_classification, private_auth, PROJECT, MODEL, DATASET_SCOPE, POLICY_REF,
            1, expires_at, status, None, DIGEST, APPROVAL.bytes, "decision:dataset-approval",
        ))
        g.execute("INSERT INTO approval_requests VALUES (?,?,?,?,?,?)", (
            APPROVAL.bytes, OWNER, DIGEST, 1, 1000, "approved",
        ))
        g.execute("INSERT INTO approval_decisions VALUES (?,?,?,?,?,?,?)", (
            DECISION.bytes, APPROVAL.bytes, OWNER, "approved", DIGEST, 2, "session:owner",
        ))
    if revoked:
        g.execute("INSERT INTO dataset_source_authorization_revocations VALUES (?,?)",
                  (AUTHORIZATION.bytes, DIGEST))
    g.commit()
    g.close()

    m = sqlite3.connect(memory_path)
    m.executescript("""
        CREATE TABLE dataset_manifests (
            manifest_id BLOB, owner_ref TEXT, model_family_ref TEXT, training_purpose TEXT,
            manifest_digest TEXT, rights_policy_snapshot_ref TEXT, rights_policy_snapshot_digest TEXT,
            lifecycle TEXT, manifest_artifact_ref TEXT, preprocessing_pipeline_ref TEXT,
            deduplication_report_ref TEXT, quality_report_ref TEXT,
            language_domain_classification_ref TEXT, curriculum_config_ref TEXT,
            derived_artifact_refs_json TEXT
        );
        CREATE TABLE dataset_manifest_seals (
            manifest_id BLOB, manifest_digest TEXT, authorization_check_digest TEXT
        );
        CREATE TABLE dataset_manifest_splits (manifest_id BLOB, split_type TEXT, split_ref TEXT, split_digest TEXT);
        CREATE TABLE dataset_manifest_lifecycle_events (manifest_id BLOB, lifecycle_state TEXT);
        CREATE TABLE dataset_manifest_sources (
            manifest_id BLOB, source_ref TEXT, source_content_sha256 TEXT, authorization_id BLOB,
            authorization_record_digest TEXT, license_or_terms_digest TEXT, source_artifact_ref TEXT,
            transformation_lineage_refs_json TEXT, owner_ref TEXT, model_family_ref TEXT
        );
    """)
    m.execute("""INSERT INTO dataset_manifests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        MANIFEST.bytes, OWNER, MODEL, PURPOSE, DIGEST, "rights-snapshot:v1", POLICY,
        lifecycle, "manifest:one", "preprocess:v1", "dedup:v1", "quality:v1",
        "language-domain:v1", "curriculum:v1",
        json.dumps([item[0] for item in split_artifacts.values()] if artifact_store else []),
    ))
    if seal:
        m.execute("INSERT INTO dataset_manifest_seals VALUES (?,?,?)", (MANIFEST.bytes, DIGEST, TERMS))
    for split in ("train", "validation", "held_out"):
        m.execute("INSERT INTO dataset_manifest_splits VALUES (?,?,?,?)", (
            MANIFEST.bytes, split, split_artifacts[split][0], split_artifacts[split][1]
        ))
    if lifecycle != "sealed":
        m.execute("INSERT INTO dataset_manifest_lifecycle_events VALUES (?,?)", (MANIFEST.bytes, lifecycle))
    m.execute("""INSERT INTO dataset_manifest_sources VALUES (?,?,?,?,?,?,?,?,?,?)""", (
        MANIFEST.bytes, "source:one", source_digest, AUTHORIZATION.bytes, DIGEST, TERMS,
        source_artifact_ref,
        json.dumps([item[0] for item in split_artifacts.values()] if artifact_store else []),
        OWNER, MODEL,
    ))
    m.commit()
    m.close()
    return governance_path, memory_path


def admit(paths):
    return admit_dataset(
        *paths, str(MANIFEST), owner_ref=OWNER, model_family_ref=MODEL,
        training_purpose=PURPOSE, project_ref=PROJECT, dataset_scope_ref=DATASET_SCOPE,
        policy_version_ref=POLICY_REF, rights_policy_snapshot_ref="rights-snapshot:v1",
        rights_policy_snapshot_digest=POLICY, now_ms=100,
    )


def test_admits_current_authorized_sealed_manifest_read_only(tmp_path: Path):
    paths = build_databases(tmp_path)
    result = admit(paths)
    assert result.manifest_id == str(MANIFEST)
    assert len(result.sources) == 1
    assert result.sources[0].source_ref == "source:one"
    assert result.sources[0].source_artifact_ref == "artifact:source-one"
    for path in paths:
        connection = _connect_read_only(path)
        assert connection.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            connection.execute("INSERT INTO dataset_source_authorization_revocations VALUES (?,?)",
                               (AUTHORIZATION.bytes, DIGEST)) if path == paths[0] else connection.execute(
                                   "INSERT INTO dataset_manifest_splits VALUES (?,?,?,?)",
                                   (MANIFEST.bytes, "x", "split:x", DIGEST),
                               )
        connection.close()


@pytest.mark.parametrize("overrides,reason", [
    ({"status": "revoked"}, "not active"),
    ({"expires_at": 100}, "expired"),
    ({"training": "deny"}, "permission"),
    ({"terms_digest": "d" * 64}, "terms digest"),
    ({"revoked": True}, "revocation"),
    ({"lifecycle": "quarantined"}, "lifecycle"),
    ({"seal": False}, "seal"),
    ({"include_auth": False}, "matching governance authorization"),
    ({"private_classification": "private"}, "explicit authorization"),
])
def test_denies_invalid_or_unproven_dataset(tmp_path: Path, overrides, reason):
    with pytest.raises(AdmissionDenied, match=reason):
        admit(build_databases(tmp_path, **overrides))


def test_denies_wrong_owner_scope(tmp_path: Path):
    paths = build_databases(tmp_path)
    with pytest.raises(AdmissionDenied, match="scope mismatch"):
        admit_dataset(
            *paths, str(MANIFEST), owner_ref="owner:other", model_family_ref=MODEL,
            training_purpose=PURPOSE, project_ref=PROJECT, dataset_scope_ref=DATASET_SCOPE,
            policy_version_ref=POLICY_REF, rights_policy_snapshot_ref="rights-snapshot:v1",
            rights_policy_snapshot_digest=POLICY, now_ms=100,
        )


def test_denies_project_dataset_and_policy_scope_mismatch(tmp_path: Path):
    paths = build_databases(tmp_path)
    with pytest.raises(AdmissionDenied, match="project scope mismatch"):
        admit_dataset(
            *paths, str(MANIFEST), owner_ref=OWNER, model_family_ref=MODEL,
            training_purpose=PURPOSE, project_ref="project:other",
            dataset_scope_ref=DATASET_SCOPE, policy_version_ref=POLICY_REF,
            rights_policy_snapshot_ref="rights-snapshot:v1",
            rights_policy_snapshot_digest=POLICY, now_ms=100,
        )


def test_denies_manifest_from_different_active_policy_snapshot(tmp_path: Path):
    paths = build_databases(tmp_path)
    with pytest.raises(AdmissionDenied, match="rights-policy snapshot"):
        admit_dataset(
            *paths, str(MANIFEST), owner_ref=OWNER, model_family_ref=MODEL,
            training_purpose=PURPOSE, project_ref=PROJECT,
            dataset_scope_ref=DATASET_SCOPE, policy_version_ref=POLICY_REF,
            rights_policy_snapshot_ref="rights-snapshot:v1",
            rights_policy_snapshot_digest="e" * 64, now_ms=100,
        )


def test_admitted_artifacts_train_and_emit_quarantined_checkpoint(tmp_path: Path):
    artifact_store = ArtifactStore(tmp_path / "artifacts")
    paths = build_databases(tmp_path, artifact_store=artifact_store)
    admission = admit(paths)
    result = train_admitted_dataset(
        admission, artifact_store, admission_id="admission:verified-test", steps=30, seed=29,
    )
    assert result.candidate_status == "quarantined"
    assert result.activation_eligible is False
    assert result.final_validation_loss < result.initial_validation_loss
    stored = artifact_store.get_bytes(
        result.checkpoint.uri, expected_sha256=result.checkpoint.sha256
    )
    import io
    import torch
    checkpoint = torch.load(io.BytesIO(stored), map_location="cpu", weights_only=True)
    assert checkpoint["dataset_lineage"]["manifest_id"] == str(MANIFEST)
    assert checkpoint["dataset_lineage"]["admission_id"] == "admission:verified-test"
    assert len(checkpoint["dataset_lineage"]["sources"]) == 1
    assert {item["split_type"] for item in checkpoint["dataset_lineage"]["splits"]} == {
        "train", "validation", "held_out"
    }

    # The admitted-data checkpoint is now consumable by the local model path,
    # but remains quarantined and cannot enter the active-model path.
    from aurions_ml.inference import generate, load_candidate_model

    candidate_path = tmp_path / "candidate.pt"
    candidate_path.write_bytes(stored)
    loaded_model, _ = load_candidate_model(candidate_path)
    assert loaded_model.training is False
    generated = generate(candidate_path, "AURIONS", max_new_tokens=8)
    assert generated.startswith("AURIONS")


def test_training_rejects_unimplemented_objective(tmp_path: Path):
    from dataclasses import replace

    artifact_store = ArtifactStore(tmp_path / "artifacts")
    admission = admit(build_databases(tmp_path, artifact_store=artifact_store))
    with pytest.raises(ValueError, match="only the foundation_pretraining"):
        train_admitted_dataset(
            replace(admission, training_purpose="instruction_sft"), artifact_store,
            admission_id="admission:test", steps=5,
        )


def test_training_rejects_missing_source_to_split_lineage(tmp_path: Path):
    from dataclasses import replace

    artifact_store = ArtifactStore(tmp_path / "artifacts")
    admission = admit(build_databases(tmp_path, artifact_store=artifact_store))
    source = replace(admission.sources[0], transformation_lineage_refs=())
    with pytest.raises(ValueError, match="not bound to source and manifest lineage"):
        train_admitted_dataset(
            replace(admission, sources=(source,)), artifact_store,
            admission_id="admission:test", steps=5,
        )
