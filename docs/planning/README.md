# Planning documentation

This directory contains the canonical planning mirror and the detailed contracts required before implementation.

## Canonical source and planning baseline

- [Initial engineering specification](INITIAL-ENGINEERING-SPECIFICATION.md) — owner decisions, architecture, proposed database DDL, event/worker contracts, governance, security, testing, roadmap and historical decision record.
- [Implementation-ready planning contracts](IMPLEMENTATION-READY-PLANNING-CONTRACTS.md) — component ownership, versioned contracts, worker boundary, authorization, operation recovery, persistence, synchronization/deletion, test catalogue, threat model, validation procedures and implementation work packages.
- [Notion project control center](https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204) — original planning source and decision history.

The architecture and first-release product definition are maintained under `docs/architecture/` and `docs/product/`. Review records are under `docs/reviews/`, including the [independent architecture re-review](../reviews/INDEPENDENT-ARCHITECTURE-REVIEW-RE-REVIEW.md) for the current PR #2 revision.

## Status discipline

A documented proposal is not an owner decision, a validated result or an implementation. Every item must be marked as specified, validated or implemented with evidence. The planning supplement closes design omissions only; it does not claim that SQL has been executed, target-device measurements have been performed, dependencies have been audited, security has been penetration-tested, or implementation exists.

## Remaining evidence and approval gates

Before implementation, the project still requires:
- Execute and fault-test the three actual SQLite DDLs and migration paths.
- Complete the real dependency/license/SBOM audit after technology versions are selected.
- Reconcile WP-00 PR #1, achieve clean reproducible host/Termux builds and green CI.
- Measure target-device performance, memory, thermals, battery, storage and background lifecycle.
- Prototype JNI/shared-library versus IPC and validate platform choices.
- Review actual security implementation, key lifecycle, IPC, update chain and data flows.
- Implement and execute the contract, governance, operation, cognitive-cycle, learning, sync and recovery tests.
- Resolve owner-reserved first UI and first permitted local action.
- Reconcile the independent re-review's required corrections and obtain explicit owner approval before implementation.

No implementation or merge is authorized merely by these documents.

## Editorial note

The imported source preserves historical wording and decision provenance. Its repeated section numbering and historical status notes are not silently rewritten. Use the current status and change log when reconciling older statements.
