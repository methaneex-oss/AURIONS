"""Exercise the admission gate against the repository's real SQLite migrations."""

import json
import sqlite3
import uuid
from pathlib import Path

import pytest

from aurions_ml.admission import AdmissionDenied, admit_dataset, record_admission_decision

ROOT = Path(__file__).resolve().parents[3]
DDL = ROOT / "schemas" / "persistence"
OWNER = "owner-dataset"
MODEL = "model-family"
PROJECT = "project:one"
DATASET_SCOPE = "dataset:one"
POLICY_REF = "policy:v1"
PURPOSE = "foundation_pretraining"
MANIFEST_ID = uuid.UUID("f6e8bb55-8a73-4ef1-87c6-0f9f7a8f2a10")
AUTHORIZATION_ID = uuid.UUID("4b8d98c7-6e25-4e2d-91d5-6f0a3c3f1011")
APPROVAL_ID = uuid.UUID("c9f5f0bd-4f17-4a5d-a2c7-16e63b2a9001")
OPERATION_ID = uuid.UUID("e3d3db77-8e41-4bc0-8b4d-64d27e4c0003")
SOURCE_DIGEST = "b" * 64
TERMS_DIGEST = "c" * 64
AUTH_DIGEST = "d" * 64
MANIFEST_DIGEST = "e" * 64
POLICY_DIGEST = "f" * 64


def apply_chain(path: Path, store: str, versions: int) -> None:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript((DDL / f"aurion_{store}.base.sql").read_text(encoding="utf-8"))
    for version in range(2, versions + 1):
        filename = DDL / f"aurion_{store}.migration_v{version}.sql"
        connection.executescript(filename.read_text(encoding="utf-8"))
    connection.close()


def build_canonical_stores(tmp_path: Path, *, authorization_expiry=900,
                           manifest_terms_digest=TERMS_DIGEST,
                           training_permission="allow") -> tuple[Path, Path]:
    governance_path = tmp_path / "aurion_governance.db"
    memory_path = tmp_path / "aurion_memory.db"
    apply_chain(governance_path, "governance", 5)
    apply_chain(memory_path, "memory", 10)

    governance = sqlite3.connect(governance_path)
    governance.execute("PRAGMA foreign_keys=ON")
    governance.execute(
        """INSERT INTO approval_requests
        (request_id,operation_id,requester_id,operation_digest,operation_summary,risk_class,
         data_categories_json,policy_version_ref,requested_at_ms,expires_at_ms,state,
         owner_ref,owner_session_ref)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (APPROVAL_ID.bytes, OPERATION_ID.bytes, OWNER, "a" * 64,
         "authorize training source", "R5", '["training_data"]', POLICY_REF,
         1, 2000, "pending", OWNER, "owner-session:dataset"),
    )
    governance.execute(
        """INSERT INTO approval_decisions
        (decision_id,request_id,authenticated_owner_ref,decision,approved_digest,
         decided_at_ms,authentication_context_ref)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([45]) * 16, APPROVAL_ID.bytes, OWNER, "approved", "a" * 64,
         2, "owner-session:dataset"),
    )
    governance.execute(
        """INSERT INTO dataset_source_authorizations
        (authorization_id,authorization_revision,owner_ref,source_ref,source_content_sha256,
         source_origin_json,rights_holder_ref,authorization_basis,license_or_terms_ref,
         license_or_terms_digest,permitted_purposes_json,training_permission,
         memory_retention_permission,private_data_classification,private_data_authorization_ref,
         project_ref,model_family_ref,dataset_scope_ref,policy_version_ref,valid_from_ms,
         expires_at_ms,status,revoked_at_ms,revocation_ref,approval_request_id,decision_ref,
         supersedes_authorization_id,created_at_ms,record_digest)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (AUTHORIZATION_ID.bytes, 1, OWNER, "source:one", SOURCE_DIGEST,
         json.dumps({"acquisition_method": "licensed_export", "origin_ref": "source-origin:one",
                     "acquired_at": "2026-11-16T20:00:00Z"}),
         "rights-holder:one", "license", "license:one", TERMS_DIGEST,
         json.dumps([PURPOSE]), training_permission, "deny", "public", None,
         PROJECT, MODEL, DATASET_SCOPE, POLICY_REF, 1, authorization_expiry,
         "active", None, None, APPROVAL_ID.bytes, "decision:dataset-approval",
         None, 3, AUTH_DIGEST),
    )
    governance.commit()
    governance.close()

    memory = sqlite3.connect(memory_path)
    memory.execute("PRAGMA foreign_keys=ON")
    memory.execute(
        """INSERT INTO dataset_manifests
        (manifest_id,schema_version,owner_ref,model_family_ref,training_purpose,
         model_generation_ref,tokenizer_artifact_ref,manifest_artifact_ref,
         preprocessing_pipeline_ref,preprocessing_config_digest,deduplication_report_ref,
         quality_report_ref,language_domain_classification_ref,curriculum_config_ref,
         curriculum_config_digest,manifest_digest,rights_policy_snapshot_ref,
         rights_policy_snapshot_digest,lifecycle,derived_artifact_refs_json,
         authorization_evaluated_at_ms,created_at_ms)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (MANIFEST_ID.bytes, "1.0", OWNER, MODEL, PURPOSE, "generation:one",
         "tokenizer:one", "manifest:one", "preprocess:one", "1" * 64,
         "dedup:one", "quality:one", "language-domain:one", "curriculum:one",
         "2" * 64, MANIFEST_DIGEST, "rights-snapshot:one", POLICY_DIGEST,
         "sealed", "[]", 10, 10),
    )
    memory.execute(
        """INSERT INTO dataset_manifest_sources
        (manifest_id,source_ref,source_content_sha256,authorization_id,
         authorization_record_digest,license_or_terms_digest,source_artifact_ref,
         transformation_lineage_refs_json,owner_ref,model_family_ref)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (MANIFEST_ID.bytes, "source:one", SOURCE_DIGEST, AUTHORIZATION_ID.bytes,
         AUTH_DIGEST, manifest_terms_digest, "artifact:source-one", "[]", OWNER, MODEL),
    )
    for split_type in ("train", "validation", "held_out"):
        memory.execute(
            """INSERT INTO dataset_manifest_splits
            (manifest_id,split_type,split_ref,split_digest) VALUES (?,?,?,?)""",
            (MANIFEST_ID.bytes, split_type, f"split:{split_type}", "9" * 64),
        )
    memory.execute(
        """INSERT INTO dataset_manifest_seals
        (manifest_id,manifest_digest,authorization_check_digest,sealed_at_ms,supervisor_ref)
        VALUES (?,?,?,?,?)""",
        (MANIFEST_ID.bytes, MANIFEST_DIGEST, "8" * 64, 20, "supervisor:trusted"),
    )
    memory.commit()
    memory.close()
    return governance_path, memory_path


def admit(paths, now_ms=100):
    return admit_dataset(
        *paths, str(MANIFEST_ID), owner_ref=OWNER, model_family_ref=MODEL,
        training_purpose=PURPOSE, project_ref=PROJECT,
        dataset_scope_ref=DATASET_SCOPE, policy_version_ref=POLICY_REF,
        rights_policy_snapshot_ref="rights-snapshot:one",
        rights_policy_snapshot_digest=POLICY_DIGEST, now_ms=now_ms,
    )


def test_admission_reads_actual_governance_and_memory_migrations(tmp_path: Path):
    paths = build_canonical_stores(tmp_path)
    result = admit(paths)
    assert result.manifest_id == str(MANIFEST_ID)
    assert result.sources[0].source_ref == "source:one"
    assert result.sources[0].approval_decision_ref == "decision:dataset-approval"


def test_actual_authorization_expiry_blocks_dispatch(tmp_path: Path):
    paths = build_canonical_stores(tmp_path, authorization_expiry=900)
    with pytest.raises(AdmissionDenied, match="expired"):
        admit(paths, now_ms=900)


def test_actual_governance_revocation_blocks_dispatch(tmp_path: Path):
    paths = build_canonical_stores(tmp_path)
    governance = sqlite3.connect(paths[0])
    governance.execute("PRAGMA foreign_keys=ON")
    governance.execute(
        """INSERT INTO dataset_source_authorization_revocations
        (revocation_id,authorization_id,authorization_record_digest,owner_ref,actor_identity,
         approval_request_id,operation_id,reason_ref,policy_version_ref,revoked_at_ms,revocation_digest)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([44]) * 16, AUTHORIZATION_ID.bytes, AUTH_DIGEST, OWNER,
         "owner-session:dataset", APPROVAL_ID.bytes, bytes([43]) * 16,
         "reason:withdrawn", POLICY_REF, 50, "7" * 64),
    )
    governance.commit()
    governance.close()
    with pytest.raises(AdmissionDenied, match="revocation"):
        admit(paths)


def test_actual_manifest_terms_digest_must_match_governance(tmp_path: Path):
    paths = build_canonical_stores(tmp_path, manifest_terms_digest="0" * 64)
    with pytest.raises(AdmissionDenied, match="terms digest"):
        admit(paths)


def test_actual_training_permission_is_independent_of_memory_retention(tmp_path: Path):
    paths = build_canonical_stores(tmp_path, training_permission="deny")
    with pytest.raises(AdmissionDenied, match="training permission"):
        admit(paths)


def test_successful_admission_is_persisted_append_only(tmp_path: Path):
    paths = build_canonical_stores(tmp_path)
    result = admit(paths)
    admission_id = record_admission_decision(
        paths[1], result, policy_version_ref=POLICY_REF,
        worker_job_ref="worker-job:one", checked_at_ms=100,
    )
    connection = sqlite3.connect(paths[1])
    row = connection.execute(
        """SELECT outcome,owner_ref,model_family_ref,training_purpose,worker_job_ref,
                  evidence_refs_json FROM dataset_admission_decisions WHERE admission_id=?""",
        (uuid.UUID(admission_id).bytes,),
    ).fetchone()
    assert row[:5] == ("admitted", OWNER, MODEL, PURPOSE, "worker-job:one")
    evidence = json.loads(row[5])
    assert any(item.get("kind") == "manifest" for item in evidence)
    with pytest.raises(sqlite3.IntegrityError, match="append_only"):
        connection.execute(
            "UPDATE dataset_admission_decisions SET outcome='blocked' WHERE admission_id=?",
            (uuid.UUID(admission_id).bytes,),
        )
    with pytest.raises(sqlite3.IntegrityError, match="append_only"):
        connection.execute(
            "DELETE FROM dataset_admission_decisions WHERE admission_id=?",
            (uuid.UUID(admission_id).bytes,),
        )
    connection.close()
