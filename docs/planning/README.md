# Planning documentation

This directory contains the canonical planning mirror, detailed technical contracts and the evidence-based planning completion register.

## Canonical source and planning baseline

- [Initial engineering specification](INITIAL-ENGINEERING-SPECIFICATION.md) — owner decisions, architecture, proposed database DDL, event/worker contracts, governance, security, testing, roadmap and historical decision record.
- [Machine-readable contract schemas](../../schemas/README.md) — proposed JSON Schema source for the common envelope and extensible capability descriptor; currently partial and not yet toolchain-validated.
- [Implementation-ready planning contracts](IMPLEMENTATION-READY-PLANNING-CONTRACTS.md) — component ownership, versioned contracts, worker boundary, authorization, operation recovery, persistence, synchronization/deletion, test catalogue, threat model, validation procedures and implementation work packages.
- [Planning completion register](PLANNING-COMPLETION-REGISTER.md) — authoritative layer-by-layer status, builder-owned remaining work, external gates and strict completion criteria. This register replaces informal terms such as “substantially complete.”
- [Canonical implementation roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md)
- [Cloud/offline-mobile topology decision](../architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md) — explicit analysis of shared implementation, shared state and synchronization; owner clarification remains open. — reconciled work packages, dependencies, concurrent first-release targets and measurable exit criteria. It supersedes earlier conflicting work-package tables.
- [Owner decision traceability matrix](OWNER-DECISION-TRACEABILITY-MATRIX.md) — maps MP/IP/UQ and operational-authority decisions to architecture, contracts, work packages and tests without replacing the source decision register.
- [Notion project control center](https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204) — original planning source and decision history.

The initial language-neutral [domain payload schema source](../../contracts/schemas/v1/domain-contracts.schema.json) defines the common envelope and core cognitive/capability payloads; its coverage and remaining fixture/conformance work are tracked in the contract matrix. The [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) maps each cognitive mechanism and Android capability responsibility to state ownership, persistence, contract families, work packages and verification; it also records unresolved schema reconciliation findings. The architecture and first-release product definition are maintained under `docs/architecture/` and `docs/product/`. The [Cognitive Mechanism and Interaction Architecture](../architecture/COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md) specifies mechanism ownership, state domains, interactions, learning pathways, concurrency, anti-hardcoding invariants and verification scenarios. The [Android environment and capability architecture](../architecture/ANDROID-ENVIRONMENT-AND-CAPABILITY-ARCHITECTURE.md) defines the mechanism-based approach to Android environment discovery, capability knowledge, governed execution and experience-driven improvement. Review records are under `docs/reviews/`, including the [independent architecture re-review](../reviews/INDEPENDENT-ARCHITECTURE-REVIEW-RE-REVIEW.md). The recorded independent review applies to its stated historical revision; it is not a review of every subsequent correction or the current final baseline.

## Status discipline

A documented proposal is not an owner decision, a validated result or an implementation. Every item must be marked as specified, validated or implemented with evidence. The planning supplement closes design omissions only; it does not claim that SQL has been executed, target-device measurements have been performed, dependencies have been audited, security has been penetration-tested, or implementation exists.

## Current phase

**Architecture planning and technical design; implementation planning is in progress.** No implementation is authorized. Consult the planning completion register for the exact status of each layer and remaining builder-owned task.

## Remaining evidence and approval gates

Before implementation, the project still requires:
- Execute and fault-test the three actual SQLite DDLs and migration paths.
- Complete the real dependency/license/SBOM audit after technology versions are selected.
- Reconcile WP-00 PR #1, achieve clean reproducible host/Termux builds and green CI.
- Measure target-device performance, memory, thermals, battery, storage and background lifecycle.
- Prototype JNI/shared-library versus IPC and validate platform choices.
- Review actual security implementation, key lifecycle, IPC, update chain and data flows.
- Implement and execute the contract, governance, operation, cognitive-cycle, learning, sync and recovery tests.
- The CLI first-interface and concurrent cloud/offline-mobile direction are recorded owner decisions. The exact first permitted local action remains a separate unresolved first-release decision; it must not be inferred from illustrative Android examples.
- Complete builder-owned design corrections, obtain independent re-review of the exact final revision, resolve required findings and obtain explicit owner approval before implementation.

No implementation or merge is authorized merely by these documents.

## Editorial note

The imported source preserves historical wording and decision provenance. Its repeated section numbering and historical status notes are not silently rewritten. Use the current status and change log when reconciling older statements.
