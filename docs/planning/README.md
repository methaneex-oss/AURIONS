# AURIONS — Planning Documentation

This directory contains the canonical planning mirror, technical contracts, owner-decision traceability and evidence-based planning status. The current phase is architecture/technical planning. Runtime implementation is not authorized.

## Governance and source of truth

- [Project Directorship and Team Operating Standard](../governance/PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md) — authority, milestone gates, builder/reviewer/tester responsibilities and acceptance.
- [Builder Operating Protocol](../governance/BUILDER-OPERATING-PROTOCOL.md) — required builder execution, self-review, correction and evidence practices.
- [Initial Engineering Specification](INITIAL-ENGINEERING-SPECIFICATION.md) — canonical planning mirror and owner-decision register.
- [Owner Decision Traceability Matrix](OWNER-DECISION-TRACEABILITY-MATRIX.md) — maps owner decisions to architecture, contracts, tests, work packages and remaining gates.
- [Planning Exit Owner Decision Packet](PLANNING-EXIT-OWNER-DECISION-PACKET.md) — consolidates product-definition approval, cloud/mobile continuity, first Android action, command/query subset and planning-exit gates. It records no decisions on the owner's behalf.
- [Planning Completion Register](PLANNING-COMPLETION-REGISTER.md) — layer-by-layer status, builder-owned work, external/owner gates and strict completion criteria.

## Product, architecture and roadmap

- [First Usable Release Definition](../product/FIRST-USABLE-RELEASE-DEFINITION.md) — proposed PR-01…PR-18 acceptance baseline.
- [Cloud and Offline-Mobile Runtime Topology Decision](../architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md) — compares independent histories, selective synchronization and cloud-compute options; continuity remains an owner decision.
- [Canonical Implementation Roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md) — WP-00…WP-16 sequence and dependency boundaries.
- [Work-Package Traceability and Exit Matrix](WORK-PACKAGE-TRACEABILITY-AND-EXIT-MATRIX.md) — owners, inputs/outputs, acceptance, recovery evidence and external gates.
- [First-Release Acceptance Traceability Matrix](FIRST-RELEASE-ACCEPTANCE-TRACEABILITY-MATRIX.md) — traces PR-01…PR-18 to contracts, work packages, scenarios and evidence.
- [Semantic Architecture Reconciliation Report](SEMANTIC-ARCHITECTURE-RECONCILIATION-REPORT.md) — maps concepts, state ownership, command/query/event surfaces, work packages and evidence.

## Technical contract matrices

- [Implementation-Ready Planning Contracts](IMPLEMENTATION-READY-PLANNING-CONTRACTS.md) — component boundaries, message contracts, worker isolation, authorization, recovery, persistence, sync/deletion and test requirements.
- [Command/Query Registry](../../schemas/command-query-registry.v1.json) — 54 command records (52 mapped, two deferred) and 29 query records; all remain design-only/non-dispatchable.
- [Query Semantics and Security Contract Matrix](QUERY-SEMANTICS-AND-SECURITY-CONTRACT-MATRIX.md) — per-query scope, classification/redaction, consistency, ordering/cursor, freshness/cache and resource-budget rules.
- [Query Projection and Persistence Reconciliation](QUERY-PROJECTION-AND-PERSISTENCE-RECONCILIATION.md) — proposed source/derivation mapping for all 310 query result fields; SQL handlers and behavioural projection tests remain open.
- [Event Registry](../../schemas/event-registry.v1.json) — 89 design-only event contracts.
- [Event Producer and Consumer Semantics Matrix](EVENT-PRODUCER-AND-CONSUMER-SEMANTICS-MATRIX.md) — producer origins, owner transitions, consumer contracts, ordering/idempotency and failure/recovery for all 89 events.
- [Event Ingress and Internal Producer Trigger Matrix](EVENT-INGRESS-AND-INTERNAL-PRODUCER-TRIGGER-MATRIX.md) — exact internal/trusted-ingress triggers for 37 events without command producers: 15 Action Gateway lifecycle events and 22 other non-command events.
- [Operation Lifecycle Transition Matrix](OPERATION-LIFECYCLE-TRANSITION-MATRIX.md) — Action Gateway lifecycle predecessor, trigger and effect constraints.
- [Store-Local Outbox and Cross-Store Saga Matrix](STORE-LOCAL-OUTBOX-AND-CROSS-STORE-SAGA-MATRIX.md) — per-store transactional outboxes and the three explicitly specified cross-store evolution sagas.
- [Error Handler Contract Matrix](ERROR-HANDLER-CONTRACT-MATRIX.md) — 35-code seed registry, 13 category-owned handler contracts and code-specific recovery assertions.

## Schemas, fixtures and validation

- [Schema and fixture index](../../schemas/README.md) — schema source and validation inventory.
- [Integrated Scenario Contract Fixture](../../schemas/fixtures/scenario-contracts.fixture.json) — **47 design specifications**: INT-001…003, CM-001…029 and AD-001…015; **287 ordered steps and 53 negative controls**. These are not executed runtime tests and confer no execution authority.
- [Scenario Contract JSON Schema](../../schemas/scenario-contracts.v1.schema.json) — validates scenario shape and non-executable status.
- [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) — maps cognitive/world/interaction/platform responsibilities to state ownership, persistence, contracts, work packages and scenario evidence.
- [Android/Termux Target Validation Protocol](../platform/ANDROID-TERMUX-TARGET-VALIDATION-PROTOCOL.md) — read-only target collector and required empirical validation.
- CI validator: `scripts/validate_schemas.py`.
- Work-package graph validator: `scripts/validate_planning_traceability.py`.

## Review records

- [Main Builder Pre-Review Audit](../reviews/MAIN-BUILDER-PRE-REVIEW-AUDIT-2026-11-12.md) — append-only builder findings, corrections and exact-head evidence. It is not an independent review.
- [Independent Architecture Re-Review](../reviews/INDEPENDENT-ARCHITECTURE-REVIEW-RE-REVIEW.md) — applies only to the exact revision identified in that review; it does not cover later changes.
- [Governance Standard Validation Results](../reviews/GOVERNANCE-STANDARD-VALIDATION-RESULTS-2026-11-12.md) — CI structural validation of mandatory governance documents.

## Evidence and authority boundary

The current planning fixture/schema CI has passed on scenario-expansion code HEAD `a38494b4610a0fa9870908950a1a7336dcb4c2b2` (workflow run [43440727107](https://github.com/methaneex-oss/AURIONS/actions/runs/43440727107)). It validates schemas/fixtures, governance document structure, work-package graph structure, host SQLite DDL/migration smoke tests and Android probe shell syntax. It does not prove production handlers, executed cognitive behaviour, cross-store saga recovery, target Android/Termux behaviour, C++/Python conformance, production security or independent review.

The builder recommendation is not an owner decision. The first Android action, cloud/mobile history topology, first-release product definition and first-release command/query subset remain subject to owner resolution. Target-device, toolchain, dependency and security evidence must be passed or explicitly staged with restrictions. Planning exit and implementation require separate explicit owner approval. PR #2 remains draft/open/unmerged.
