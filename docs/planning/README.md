# Planning documentation

This directory contains the canonical planning mirror, detailed technical contracts and the evidence-based planning completion register.

## Canonical source and planning baseline

- [Mandatory Project Directorship and Team Operating Standard](../governance/PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md) — mandatory director/builder/reviewer/tester responsibilities, sequential handoff gates, scope control and evidence-based acceptance.
- [Mandatory Builder Operating Protocol](../governance/BUILDER-OPERATING-PROTOCOL.md) — detailed builder execution, self-review, test and correction obligations.

- [Initial engineering specification](INITIAL-ENGINEERING-SPECIFICATION.md)
- [Owner decision traceability matrix](OWNER-DECISION-TRACEABILITY-MATRIX.md) — maps each owner decision to architecture, contracts, tests, roadmap and remaining evidence.
- [Machine-readable contract schemas](../../schemas/README.md)
- [Integrated scenario contract fixtures](../../schemas/fixtures/scenario-contracts.fixture.json) — 39 multi-step design scenarios (INT, CM and AD) with 172 steps, 45 negative controls and restart/replay/concurrency/fault/held-out controls; CI validates structure and registry references, not runtime behaviour.
- [Event producer and consumer semantics matrix](EVENT-PRODUCER-AND-CONSUMER-SEMANTICS-MATRIX.md) — bidirectional command-to-event producer bindings for all 89 event entries; explicitly records 38 events without command producers and keeps consumer/owner-transition semantics unresolved.
- [Query semantics and security contract matrix](QUERY-SEMANTICS-AND-SECURITY-CONTRACT-MATRIX.md) — per-query owner/actor scope, classification/redaction, consistency, ordering/cursor, resource-budget rules, freshness/cache semantics and executable acceptance cases for all 29 query registry entries; numerical budgets and handler tests remain open.
- [Command/query registry baseline](../../schemas/command-query-registry.v1.json) — 51 mapped command types, two deferred device commands and 29 query types; explicitly non-dispatchable pending per-entry semantics and fixtures. — proposed JSON Schema source for the common envelope, extensible capability descriptor and 89 reusable domain-schema definitions; the Python-host Draft 2020-12 corpus validation is CI-enforced (10 schema documents, 8 registry/fixture pairs, 81 positive domain payloads and 29 negative controls). C++ validator equivalence and C++/Python conformance remain open.
- [Implementation-ready planning contracts](IMPLEMENTATION-READY-PLANNING-CONTRACTS.md) — component ownership, versioned contracts, worker boundary, authorization, operation recovery, persistence, synchronization/deletion, test catalogue, threat model, validation procedures and implementation work packages.
- [Error handler contract matrix](ERROR-HANDLER-CONTRACT-MATRIX.md) — maps the 35-code seed registry to 13 category-owned recovery contracts, 35 code-specific recovery assertions and schema-shaped payload fixtures; assertions are specified, not executed runtime handlers.
- [Planning completion register](PLANNING-COMPLETION-REGISTER.md) — authoritative layer-by-layer status, builder-owned remaining work, external gates and strict completion criteria. This register replaces informal terms such as “substantially complete.”
- [Canonical implementation roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md)
- [Work-package traceability and exit matrix](WORK-PACKAGE-TRACEABILITY-AND-EXIT-MATRIX.md) — per-package logical owners, inputs, outputs/contracts, acceptance evidence, failure/recovery tests and external/owner gates.
- [Cloud/offline-mobile topology decision](../architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md) — explicit analysis of shared implementation, shared state and synchronization; the first-release continuity choice remains unresolved.
- [Notion project control center](https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204) — original planning source and decision history.

CI also runs `scripts/validate_planning_traceability.py` to enforce the 17-package roadmap/matrix inventory, dependency references, acyclic graph and first-release WP-15 boundary; this is structural validation only. The [machine-readable contract schemas](../../schemas/README.md) include a common message envelope, extensible capability descriptor and 78 domain/protocol/command/query/operational payload definitions. The current Python-host Draft 2020-12 schema/fixture corpus passes CI, including 78 positive domain payloads and 29 negative controls. C++ validator equivalence, C++/Python conformance and runtime integration remain open; schemas remain design contracts, not dispatch authorization. The [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) maps each cognitive mechanism and Android capability responsibility to state ownership, persistence, contract families, work packages and verification; it also records unresolved schema reconciliation findings. The [Cloud and Offline-Mobile Runtime Topology Decision](../architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md) records the unresolved trade-off between concurrent cloud/mobile runtimes, shared cognitive state and deferred synchronization; it presents a builder recommendation for selective synchronization, but the owner has not selected a topology. The architecture and first-release product definition are maintained under `docs/architecture/` and `docs/product/`. The [Cognitive Mechanism and Interaction Architecture](../architecture/COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md) specifies mechanism ownership, state domains, interactions, learning pathways, concurrency, anti-hardcoding invariants and verification scenarios. The [Android environment and capability architecture](../architecture/ANDROID-ENVIRONMENT-AND-CAPABILITY-ARCHITECTURE.md) defines the mechanism-based approach to Android environment discovery, capability knowledge, governed execution and experience-driven improvement. Review records are under `docs/reviews/`, including the [independent architecture re-review](../reviews/INDEPENDENT-ARCHITECTURE-REVIEW-RE-REVIEW.md). The recorded independent review applies to its stated historical revision; it is not a review of every subsequent correction or the current final baseline.

## Status discipline

A documented proposal is not an owner decision, a validated result or an implementation. Every item must be marked as specified, validated or implemented with evidence. The planning supplement closes design omissions only; it does not claim that SQL has been executed, target-device measurements have been performed, dependencies have been audited, security has been penetration-tested, or implementation exists.

## Current phase

**Architecture planning and technical design; implementation planning is in progress.** No implementation is authorized. Consult the planning completion register for the exact status of each layer and remaining builder-owned task.

## Remaining evidence and approval gates

Before implementation, the project still requires:
- Host SQLite execution of the three base schemas and five additive migrations is now automated and passed. Still validate the actual target Termux/Android SQLite library and run crash/interruption, rollback/restart, restore, disk-full, locked/corrupt-store, outbox/inbox and cross-store recovery tests.
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
