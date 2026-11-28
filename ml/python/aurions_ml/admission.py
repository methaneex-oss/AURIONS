"""Fail-closed dataset admission check for the training boundary.

This callable gate is not yet wired to a C++ worker dispatcher. It validates
persisted governance and sealed-manifest records; it does not replace
cross-store recovery, artifact-byte verification, or worker-side revalidation.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

_HEX_256 = re.compile(r"^[0-9a-f]{64}$")
_PURPOSES = {
    "foundation_pretraining",
    "instruction_sft",
    "preference_training",
    "outcome_training",
    "evaluation",
}


class AdmissionDenied(RuntimeError):
    """The dataset cannot be proven eligible for the requested training job."""


@dataclass(frozen=True)
class AdmittedSource:
    source_ref: str
    source_content_sha256: str
    authorization_id: str
    authorization_record_digest: str
    approval_decision_ref: str
    source_artifact_ref: str
    transformation_lineage_refs: tuple[str, ...]


@dataclass(frozen=True)
class DatasetSplit:
    split_type: str
    artifact_ref: str
    content_sha256: str


@dataclass(frozen=True)
class AdmissionResult:
    manifest_id: str
    manifest_digest: str
    owner_ref: str
    model_family_ref: str
    training_purpose: str
    policy_version_ref: str
    sources: tuple[AdmittedSource, ...]
    splits: tuple[DatasetSplit, ...]
    derived_artifact_refs: tuple[str, ...]


def _connect_read_only(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise AdmissionDenied(f"required database is missing: {path}")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _uuid_bytes(value: str) -> tuple[str, bytes]:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError) as error:
        raise AdmissionDenied("manifest_id must be a UUID") from error
    return str(parsed), parsed.bytes


def _digest(value: object, field: str) -> str:
    if not isinstance(value, str) or not _HEX_256.fullmatch(value):
        raise AdmissionDenied(f"invalid {field}")
    return value


def admit_dataset(
    governance_db: Path,
    memory_db: Path,
    manifest_id: str,
    *,
    owner_ref: str,
    model_family_ref: str,
    training_purpose: str,
    project_ref: str,
    dataset_scope_ref: str,
    policy_version_ref: str,
    rights_policy_snapshot_ref: str,
    rights_policy_snapshot_digest: str,
    now_ms: int | None = None,
) -> AdmissionResult:
    """Return immutable source scope only if every rights check succeeds."""
    normalized_id, manifest_key = _uuid_bytes(manifest_id)
    if training_purpose not in _PURPOSES:
        raise AdmissionDenied("unsupported training purpose")
    if not all((owner_ref, model_family_ref, project_ref, dataset_scope_ref,
                policy_version_ref, rights_policy_snapshot_ref)):
        raise AdmissionDenied("owner, model, project, dataset and policy scopes are required")
    expected_policy_digest = _digest(rights_policy_snapshot_digest, "expected rights policy digest")
    checked_at = int(time.time() * 1000) if now_ms is None else now_ms

    governance: sqlite3.Connection | None = None
    memory: sqlite3.Connection | None = None
    try:
        governance = _connect_read_only(governance_db)
        memory = _connect_read_only(memory_db)
    except sqlite3.Error as error:
        if governance is not None:
            governance.close()
        raise AdmissionDenied("governance or memory database is unavailable") from error

    try:
        manifest = memory.execute(
            """SELECT m.manifest_id, m.owner_ref, m.model_family_ref, m.training_purpose,
                      m.manifest_digest, m.rights_policy_snapshot_ref,
                      m.rights_policy_snapshot_digest, m.lifecycle,
                      m.manifest_artifact_ref, m.preprocessing_pipeline_ref,
                      m.deduplication_report_ref, m.quality_report_ref,
                      m.language_domain_classification_ref, m.curriculum_config_ref,
                      m.derived_artifact_refs_json,
                      s.manifest_digest AS sealed_digest, s.authorization_check_digest
               FROM dataset_manifests m
               JOIN dataset_manifest_seals s ON s.manifest_id=m.manifest_id
               WHERE m.manifest_id=?""",
            (manifest_key,),
        ).fetchone()
        if manifest is None:
            raise AdmissionDenied("manifest is missing or has no seal")
        if manifest["lifecycle"] != "sealed":
            raise AdmissionDenied("manifest lifecycle is not sealed")
        if manifest["owner_ref"] != owner_ref or manifest["model_family_ref"] != model_family_ref:
            raise AdmissionDenied("manifest owner/model scope mismatch")
        if manifest["training_purpose"] != training_purpose:
            raise AdmissionDenied("manifest training purpose mismatch")
        manifest_digest = _digest(manifest["manifest_digest"], "manifest_digest")
        if _digest(manifest["sealed_digest"], "sealed manifest digest") != manifest_digest:
            raise AdmissionDenied("manifest seal digest mismatch")
        _digest(manifest["authorization_check_digest"], "authorization_check_digest")
        actual_policy_digest = _digest(
            manifest["rights_policy_snapshot_digest"], "rights_policy_snapshot_digest"
        )
        if (manifest["rights_policy_snapshot_ref"] != rights_policy_snapshot_ref or
                actual_policy_digest != expected_policy_digest):
            raise AdmissionDenied("manifest rights-policy snapshot does not match the active policy")
        required_manifest_refs = (
            "rights_policy_snapshot_ref", "manifest_artifact_ref",
            "preprocessing_pipeline_ref", "deduplication_report_ref",
            "quality_report_ref", "language_domain_classification_ref",
            "curriculum_config_ref",
        )
        if any(not manifest[field] for field in required_manifest_refs):
            raise AdmissionDenied("manifest is missing a required artifact/policy reference")
        try:
            derived_artifact_refs = json.loads(manifest["derived_artifact_refs_json"])
        except (TypeError, json.JSONDecodeError) as error:
            raise AdmissionDenied("manifest derived-artifact lineage is invalid") from error
        if (not isinstance(derived_artifact_refs, list) or
                any(not isinstance(ref, str) or not ref for ref in derived_artifact_refs)):
            raise AdmissionDenied("manifest derived-artifact lineage must be a string array")

        split_rows = memory.execute(
            "SELECT split_type, split_ref, split_digest FROM dataset_manifest_splits WHERE manifest_id=?",
            (manifest_key,),
        ).fetchall()
        if {row["split_type"] for row in split_rows} != {"train", "validation", "held_out"} or len(split_rows) != 3:
            raise AdmissionDenied("manifest must contain train, validation and held_out splits")
        admitted_splits: list[DatasetSplit] = []
        for row in split_rows:
            digest = _digest(row["split_digest"], f"{row['split_type']} split digest")
            if not row["split_ref"]:
                raise AdmissionDenied(f"{row['split_type']} split artifact reference is missing")
            admitted_splits.append(DatasetSplit(row["split_type"], row["split_ref"], digest))

        lifecycle = memory.execute(
            """SELECT lifecycle_state FROM dataset_manifest_lifecycle_events
               WHERE manifest_id=?""",
            (manifest_key,),
        ).fetchall()
        if any(row["lifecycle_state"] in {"superseded", "quarantined", "revoked_impact_pending"} for row in lifecycle):
            raise AdmissionDenied("manifest has a blocking lifecycle event")

        expected_source_count = memory.execute(
            "SELECT count(*) FROM dataset_manifest_sources WHERE manifest_id=?",
            (manifest_key,),
        ).fetchone()[0]
        sources = memory.execute(
            """SELECT source_ref, source_content_sha256, authorization_id,
                      authorization_record_digest, license_or_terms_digest,
                      source_artifact_ref, transformation_lineage_refs_json,
                      owner_ref AS source_owner_ref, model_family_ref AS source_model_ref
               FROM dataset_manifest_sources WHERE manifest_id=?""",
            (manifest_key,),
        ).fetchall()
        if not sources or len(sources) != expected_source_count:
            raise AdmissionDenied("manifest contains an empty or incomplete source set")

        admitted: list[AdmittedSource] = []
        for source in sources:
            content_digest = _digest(source["source_content_sha256"], "source content digest")
            terms_digest = _digest(source["license_or_terms_digest"], "manifest terms digest")
            record_digest = _digest(
                source["authorization_record_digest"], "manifest authorization digest"
            )
            if source["source_owner_ref"] != owner_ref:
                raise AdmissionDenied("source authorization owner mismatch")
            if source["source_model_ref"] != model_family_ref:
                raise AdmissionDenied("source authorization model-family mismatch")
            authorization = governance.execute(
                """SELECT authorization_revision, owner_ref, source_ref, source_content_sha256,
                          source_origin_json, record_digest, license_or_terms_ref,
                          license_or_terms_digest, authorization_basis,
                          permitted_purposes_json, training_permission, memory_retention_permission,
                          private_data_classification, private_data_authorization_ref,
                          project_ref, model_family_ref, dataset_scope_ref, policy_version_ref,
                          valid_from_ms, expires_at_ms, status, revoked_at_ms,
                          approval_request_id, decision_ref
                   FROM dataset_source_authorizations
                   WHERE authorization_id=? AND record_digest=?""",
                (source["authorization_id"], record_digest),
            ).fetchone()
            if authorization is None:
                raise AdmissionDenied("manifest source has no matching governance authorization")
            if authorization["authorization_revision"] < 1:
                raise AdmissionDenied("authorization revision is invalid")
            try:
                origin = json.loads(authorization["source_origin_json"])
            except (TypeError, json.JSONDecodeError) as error:
                raise AdmissionDenied("source origin provenance is invalid") from error
            if not isinstance(origin, dict):
                raise AdmissionDenied("source origin provenance must be an object")
            auth_content_digest = _digest(
                authorization["source_content_sha256"], "authorized source digest"
            )
            auth_terms_digest = _digest(
                authorization["license_or_terms_digest"], "authorized terms digest"
            )
            if content_digest != auth_content_digest or terms_digest != auth_terms_digest:
                raise AdmissionDenied("source content or license terms digest mismatch")
            if authorization["owner_ref"] != owner_ref:
                raise AdmissionDenied("source authorization owner mismatch")
            if authorization["model_family_ref"] != model_family_ref:
                raise AdmissionDenied("source authorization model-family mismatch")
            if authorization["source_ref"] != source["source_ref"]:
                raise AdmissionDenied("source identity mismatch")
            if authorization["status"] != "active" or authorization["revoked_at_ms"] is not None:
                raise AdmissionDenied("source authorization is not active")
            if authorization["training_permission"] != "allow":
                raise AdmissionDenied("source training permission is not allow")
            if authorization["memory_retention_permission"] not in {"allow", "deny"}:
                raise AdmissionDenied("invalid memory-retention permission")
            if authorization["authorization_basis"] not in {
                "license", "contract", "public_domain_determination",
                "explicit_owner_authorization", "statutory_exception",
            }:
                raise AdmissionDenied("source rights basis is not approved")
            try:
                permitted = json.loads(authorization["permitted_purposes_json"])
                lineage = json.loads(source["transformation_lineage_refs_json"])
            except (TypeError, json.JSONDecodeError) as error:
                raise AdmissionDenied("source purpose or transformation lineage is invalid") from error
            if not isinstance(permitted, list) or training_purpose not in permitted:
                raise AdmissionDenied("authorization does not permit the requested purpose")
            if (not isinstance(lineage, list) or
                    any(not isinstance(ref, str) or not ref for ref in lineage)):
                raise AdmissionDenied("transformation lineage must be a string array")
            if (authorization["private_data_classification"] != "public" and
                    not authorization["private_data_authorization_ref"]):
                raise AdmissionDenied("private/personal source lacks explicit authorization")
            if not authorization["license_or_terms_ref"]:
                raise AdmissionDenied("source license/terms reference is missing")
            if authorization["project_ref"] != project_ref:
                raise AdmissionDenied("source project scope mismatch")
            if authorization["dataset_scope_ref"] != dataset_scope_ref:
                raise AdmissionDenied("source dataset scope mismatch")
            if authorization["policy_version_ref"] != policy_version_ref:
                raise AdmissionDenied("source policy version mismatch")

            approval = governance.execute(
                """SELECT request_id, owner_ref, operation_digest, requested_at_ms,
                          expires_at_ms, state
                   FROM approval_requests WHERE request_id=?""",
                (authorization["approval_request_id"],),
            ).fetchone()
            if approval is None or approval["owner_ref"] != owner_ref:
                raise AdmissionDenied("source authorization has no matching owner approval request")
            if approval["state"] != "approved" or approval["expires_at_ms"] <= checked_at:
                raise AdmissionDenied("source authorization approval is not currently valid")
            operation_digest = _digest(approval["operation_digest"], "approval operation digest")
            decision = governance.execute(
                """SELECT authenticated_owner_ref, decision, approved_digest,
                          decided_at_ms, authentication_context_ref
                   FROM approval_decisions WHERE request_id=?""",
                (authorization["approval_request_id"],),
            ).fetchone()
            if decision is None or decision["decision"] != "approved":
                raise AdmissionDenied("source authorization lacks an approved decision record")
            if decision["authenticated_owner_ref"] != owner_ref:
                raise AdmissionDenied("source authorization approval owner mismatch")
            if decision["approved_digest"] != operation_digest:
                raise AdmissionDenied("source authorization approval digest mismatch")
            if not (approval["requested_at_ms"] <= decision["decided_at_ms"] < approval["expires_at_ms"]):
                raise AdmissionDenied("source authorization approval decision is outside its validity window")
            if not authorization["decision_ref"] or not decision["authentication_context_ref"]:
                raise AdmissionDenied("source authorization decision evidence is incomplete")
            if authorization["valid_from_ms"] > checked_at:
                raise AdmissionDenied("source authorization is not yet valid")
            if authorization["expires_at_ms"] is not None and authorization["expires_at_ms"] <= checked_at:
                raise AdmissionDenied("source authorization has expired")
            revoked = governance.execute(
                """SELECT 1 FROM dataset_source_authorization_revocations
                   WHERE authorization_id=? AND authorization_record_digest=? LIMIT 1""",
                (source["authorization_id"], record_digest),
            ).fetchone()
            if revoked is not None:
                raise AdmissionDenied("source authorization has a committed revocation")
            if not source["source_artifact_ref"]:
                raise AdmissionDenied("source artifact reference is missing")
            admitted.append(AdmittedSource(
                source_ref=source["source_ref"],
                source_content_sha256=content_digest,
                authorization_id=str(uuid.UUID(bytes=source["authorization_id"])),
                authorization_record_digest=record_digest,
                approval_decision_ref=authorization["decision_ref"],
                source_artifact_ref=source["source_artifact_ref"],
                transformation_lineage_refs=tuple(lineage),
            ))

        return AdmissionResult(
            manifest_id=normalized_id,
            manifest_digest=manifest_digest,
            owner_ref=owner_ref,
            model_family_ref=model_family_ref,
            training_purpose=training_purpose,
            policy_version_ref=policy_version_ref,
            sources=tuple(admitted),
            splits=tuple(sorted(admitted_splits, key=lambda split: split.split_type)),
            derived_artifact_refs=tuple(derived_artifact_refs),
        )
    except sqlite3.Error as error:
        raise AdmissionDenied("required governance or manifest records are unavailable") from error
    finally:
        if governance is not None:
            governance.close()
        if memory is not None:
            memory.close()



def record_admission_decision(
    memory_db: Path,
    result: AdmissionResult,
    *,
    policy_version_ref: str,
    worker_job_ref: str | None = None,
    checked_at_ms: int | None = None,
) -> str:
    """Persist the successful admission result in the append-only memory ledger.

    This records the gate result; it does not itself dispatch or authorize a worker.
    """
    if not memory_db.is_file():
        raise AdmissionDenied("memory database is unavailable for admission evidence")
    if not policy_version_ref:
        raise AdmissionDenied("policy_version_ref is required for admission evidence")
    if policy_version_ref != result.policy_version_ref:
        raise AdmissionDenied("admission evidence policy version does not match the admitted policy")
    if worker_job_ref is not None and not worker_job_ref:
        raise AdmissionDenied("worker_job_ref must be non-empty when supplied")
    checked_at = int(time.time() * 1000) if checked_at_ms is None else checked_at_ms
    admission_id = uuid.uuid4()
    manifest_id = uuid.UUID(result.manifest_id)
    evidence_refs = [
        {"kind": "manifest", "ref": result.manifest_id, "digest": result.manifest_digest},
    ]
    evidence_refs.extend(
        {"kind": "derived_artifact", "artifact_ref": ref}
        for ref in result.derived_artifact_refs
    )
    evidence_refs.extend(
        {
            "kind": "dataset_split",
            "split_type": split.split_type,
            "artifact_ref": split.artifact_ref,
            "content_digest": split.content_sha256,
        }
        for split in result.splits
    )
    evidence_refs.extend(
        {
            "kind": "source_authorization",
            "source_ref": source.source_ref,
            "authorization_id": source.authorization_id,
            "record_digest": source.authorization_record_digest,
            "decision_ref": source.approval_decision_ref,
            "content_digest": source.source_content_sha256,
            "transformation_lineage_refs": list(source.transformation_lineage_refs),
        }
        for source in result.sources
    )
    authorization_id = (
        uuid.UUID(result.sources[0].authorization_id).bytes if len(result.sources) == 1 else None
    )
    connection = sqlite3.connect(memory_db)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        manifest = connection.execute(
            """SELECT m.owner_ref, m.model_family_ref, m.training_purpose, m.manifest_digest,
                      m.lifecycle, s.manifest_digest
               FROM dataset_manifests m
               JOIN dataset_manifest_seals s ON s.manifest_id=m.manifest_id
               WHERE m.manifest_id=?""",
            (manifest_id.bytes,),
        ).fetchone()
        if manifest is None or manifest[3] != result.manifest_digest or manifest[5] != result.manifest_digest:
            raise AdmissionDenied("manifest changed or lost its seal before admission recording")
        if (manifest[0] != result.owner_ref or manifest[1] != result.model_family_ref or
                manifest[2] != result.training_purpose or manifest[4] != "sealed"):
            raise AdmissionDenied("manifest scope changed before admission recording")
        connection.execute(
            """INSERT INTO dataset_admission_decisions
            (admission_id,manifest_id,owner_ref,model_family_ref,training_purpose,
             outcome,denial_reason,authorization_id,policy_version_ref,worker_job_ref,
             evidence_refs_json,checked_at_ms)
            VALUES (?,?,?,?,?,'admitted',NULL,?,?,?,?,?)""",
            (admission_id.bytes, manifest_id.bytes, result.owner_ref, result.model_family_ref,
             result.training_purpose, authorization_id, policy_version_ref, worker_job_ref,
             json.dumps(evidence_refs, sort_keys=True, separators=(",", ":")), checked_at),
        )
        connection.commit()
        return str(admission_id)
    except AdmissionDenied:
        connection.rollback()
        raise
    except sqlite3.Error as error:
        connection.rollback()
        raise AdmissionDenied("could not durably record the admission decision") from error
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--governance-db", type=Path, required=True)
    parser.add_argument("--memory-db", type=Path, required=True)
    parser.add_argument("--manifest-id", required=True)
    parser.add_argument("--owner-ref", required=True)
    parser.add_argument("--model-family-ref", required=True)
    parser.add_argument("--training-purpose", choices=sorted(_PURPOSES), required=True)
    parser.add_argument("--project-ref", required=True)
    parser.add_argument("--dataset-scope-ref", required=True)
    parser.add_argument("--policy-version-ref", required=True)
    parser.add_argument("--rights-policy-snapshot-ref", required=True)
    parser.add_argument("--rights-policy-snapshot-digest", required=True)
    parser.add_argument("--worker-job-ref")
    args = parser.parse_args()
    result = admit_dataset(
        args.governance_db, args.memory_db, args.manifest_id,
        owner_ref=args.owner_ref,
        model_family_ref=args.model_family_ref,
        training_purpose=args.training_purpose,
        project_ref=args.project_ref,
        dataset_scope_ref=args.dataset_scope_ref,
        policy_version_ref=args.policy_version_ref,
        rights_policy_snapshot_ref=args.rights_policy_snapshot_ref,
        rights_policy_snapshot_digest=args.rights_policy_snapshot_digest,
    )
    admission_id = record_admission_decision(
        args.memory_db, result, policy_version_ref=args.policy_version_ref,
        worker_job_ref=args.worker_job_ref,
    )
    print(json.dumps({"admission_id": admission_id, "admission": asdict(result)}, sort_keys=True))


if __name__ == "__main__":
    main()
