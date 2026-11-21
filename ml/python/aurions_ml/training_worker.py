"""Standalone training worker: admit, record, verify artifacts, train, quarantine."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .admission import admit_dataset, record_admission_decision
from .artifact_store import ArtifactStore
from .training import train_admitted_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--governance-db", type=Path, required=True)
    parser.add_argument("--memory-db", type=Path, required=True)
    parser.add_argument("--artifact-store", type=Path, required=True)
    parser.add_argument("--manifest-id", required=True)
    parser.add_argument("--owner-ref", required=True)
    parser.add_argument("--model-family-ref", required=True)
    parser.add_argument("--training-purpose", choices=["foundation_pretraining"], required=True)
    parser.add_argument("--project-ref", required=True)
    parser.add_argument("--dataset-scope-ref", required=True)
    parser.add_argument("--policy-version-ref", required=True)
    parser.add_argument("--rights-policy-snapshot-ref", required=True)
    parser.add_argument("--rights-policy-snapshot-digest", required=True)
    parser.add_argument("--worker-job-ref", required=True)
    parser.add_argument("--steps", type=int, default=60)
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()

    admission = admit_dataset(
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
        args.memory_db, admission,
        policy_version_ref=args.policy_version_ref,
        worker_job_ref=args.worker_job_ref,
    )
    result = train_admitted_dataset(
        admission, ArtifactStore(args.artifact_store),
        admission_id=admission_id, steps=args.steps, seed=args.seed,
    )
    print(json.dumps({
        "admission_id": admission_id,
        "training_result": {
            **asdict(result),
            "checkpoint": asdict(result.checkpoint),
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
