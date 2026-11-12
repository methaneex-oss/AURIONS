# AURIONS — Canonical Implementation Roadmap

- **Status:** Proposed canonical dependency plan; not implementation authorization.
- **Phase:** Planning.
- **Authority:** Existing owner decisions and the planning completion register.
- **Purpose:** Reconcile earlier work-package tables into one dependency-aware roadmap.
- **Important:** This roadmap defines engineering order and evidence gates. It does not authorize starting any work package.

## 1. Reconciliation decisions

Earlier planning records contain different work-package numbering and sequencing. In particular:
- The original WP-00…WP-16 table and the later WP-00…WP-13 detailed table do not map one-to-one.
- One older table deferred Android integration to an expansion package, while the owner subsequently established cloud operation and offline-capable mobile operation as concurrent first-release targets.
- Android cannot be deferred wholesale if offline-capable mobile is a first-release target.
- The CLI is the owner-selected first user-facing interface. This does not remove the requirement for offline-capable mobile and cloud operation in the first-release deployment direction.
- The foundational architecture is objective-led and open-world. It must not be organized around Android, devices, platforms, connectors or a closed capability registry. Android discovery is one platform-specific realization beneath the general world/interaction model; it is not a fixed list of device operations or the boundary of possible means.

This roadmap supersedes the earlier work-package tables for future planning. Historical tables remain for provenance but must be labelled as superseded where referenced.

## 2. Work packages

| WP | Work package | Scope and outputs | Dependencies | Exit criteria |
|---|---|---|---|---|
| WP-00 | Repository and build foundation | Reproducible repository layout, C++ build, CI, toolchain inventory, clean build instructions. | Planning exit approval | Clean host and target build path; CI; documented toolchain; PR #1 reconciled. |
| WP-01 | Shared contracts and schemas | Stable IDs/time/errors, versioned envelopes, command/query/event schemas, C++ interfaces, Python process contracts, shared fixtures. | WP-00 | Valid/invalid fixtures pass; compatibility rules and ownership explicit; no contract cycles. |
| WP-02 | Persistence and artifact foundation | Three SQLite stores, DDL/migrations, artifact registry, local outboxes/inboxes, backups, retention/deletion foundations. | WP-01 | Integrity, migration, crash, restore, deletion and cross-store fault tests pass. |
| WP-03 | Runtime, scheduler and operation continuity | Lifecycle, event dispatch, durable operation state, versioned task-run transitions and control requests, checkpoints, budgets, cancellation, deadlines, supervision and reconciliation. | WP-01, WP-02 | Task-run revision and event atomicity, safe-point pause/cancel, stale-control rejection, restart/replay, lost-run reconciliation and uncertain-side-effect tests pass; bounded scheduling demonstrated. |
| WP-04 | Identity, governance and security enforcement | Owner session/authentication, policy engine, R0–R5, permission grants, exact-operation approval, audit, key interfaces and data-egress controls. | WP-01, WP-02, WP-03 | Default-deny and authorization/replay/revocation tests pass; SEC-001…SEC-011 key separation/rotation/recovery, backup, update-signing, egress and worker-isolation checks pass; model cannot self-authorize. |
| WP-05 | Inference and model abstraction | Model/provider interface, capability metadata, local inference adapter, optional authorized remote inference, resource/privacy routing. | WP-01, WP-03, WP-04 | Backend can be changed without cognitive-module rewrites; provider data boundaries tested. |
| WP-06 | World understanding and means discovery | Open-ended situation/entity/relationship representation; evidence and provenance; context-sensitive affordance and means hypotheses; discovery and evaluation mechanisms; revisable world/capability knowledge. Platform/provider integrations are subordinate realizations, including Android where relevant. No closed task, environment or capability catalogue. | WP-01, WP-02, WP-03, WP-04 | New capability providers can be discovered without adding hardcoded task-to-action branches; stale/revoked/unknown capabilities handled safely. |
| WP-07 | Experience, representation and context | Observation ingestion, source provenance, multiple representations, contextual state, uncertainty and lifecycle. | WP-01, WP-02, WP-03, WP-06 | Experiences and representations survive restart with provenance and uncertainty; no observation silently becomes fact. |
| WP-08 | Memory, knowledge and belief | Working/long-term memory, retrieval, association, evidence, provisional beliefs, revision/consolidation and deletion. | WP-02, WP-07 | Provenance-aware retrieval and contradictory-evidence revision pass repeatable tests. |
| WP-09 | Prediction, appraisal, attention and reasoning | Prediction generation/evaluation, attention allocation, appraisal, reasoning, uncertainty and context-sensitive mechanism interactions. | WP-05, WP-07, WP-08 | Integrated traces show evidence-dependent reasoning and prediction evaluation; no fixed stimulus-to-behaviour mapping. |
| WP-10 | Goals, planning and decision | Goal lifecycle, versioned plans, dependencies, resource budgets, replanning, interruption, decision records and permission handoff. | WP-03, WP-04, WP-06, WP-09 | Goals/plans persist; revisions preserve history; plans cannot bypass governance. |
| WP-11 | Interaction execution and context-specific realizations | Governed interaction contracts and exact-effect enforcement; context-specific protocols/providers; receipts, independent postcondition observation, uncertain-outcome handling and recovery. Android is one realization, not the universal execution model. | WP-03, WP-04, WP-06, WP-10 | Allowed/denied/uncertain action tests pass; Android OS permission and AURIONS policy both enforced. |
| WP-12 | Outcome feedback and learning | Prediction/outcome comparison, capability/strategy learning, controlled experiments, held-out evaluation, regression detection and reversible activation. | WP-07…WP-11 | Repeatable improvement evidence against frozen baseline; no memory-only or training-loss-only learning claims. |
| WP-13 | Self-model and governed evolution | Capability/limitation/confidence/resource model, change proposals, isolated candidates, impact analysis, approval, activation and rollback. | WP-04, WP-05, WP-06, WP-12 | Self-assessments calibrated against outcomes; candidates cannot self-approve; rollback verified. |
| WP-14 | Python workers and training infrastructure | Isolated worker supervisor, datasets, training/fine-tuning, evaluation jobs, artifact provenance, budgets, cancellation and reproducibility. | WP-01, WP-02, WP-03, WP-12 | Worker crash/retry/cancel safe; outputs validated and quarantined; no direct live-state or policy mutation. |
| WP-15 | First-release integration and hardening | Integrate the cognitive core and first-release workflows. CLI is the first user-facing interface. Deliver cloud operation and offline-capable mobile operation as concurrent first-release targets using shared contracts and authoritative core. Includes resource, security, privacy, recovery and release validation. | WP-00…WP-13; platform spikes and owner decisions. Model fine-tuning is not required by PR-01…PR-18; if the owner adds training to first-release scope, its worker/training prerequisites must be completed before claiming that added scope. | First-release acceptance protocol PR-01…PR-18 passes. PR-15 proves cloud runtime operation; PR-16 proves shared contract compatibility across cloud/mobile builds; PR-17 proves required mobile workflows work with network disabled; PR-18 proves cloud cannot authorize mobile-local operations and state ownership is explicit. Reproducible security/resource/recovery evidence is required in both contexts. |
| WP-16 | Later ecosystem expansion | Voice and continuous sensing, multi-device synchronization/handoff, broader external providers, expanded multimodal interfaces and additional compute topologies. | WP-15 accepted; separate platform/security/privacy approvals | Each expansion has a scoped proposal, permission model, tests and owner approval. |

The foundational [Open-World Interaction and Means Architecture](../architecture/OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md) governs objective-led understanding and interaction across contexts. The cognitive mechanism specification is [Cognitive Mechanism and Interaction Architecture](../architecture/COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md). The [Android Platform Interaction Realization](../architecture/ANDROID-ENVIRONMENT-AND-CAPABILITY-ARCHITECTURE.md) specifies one Android context only. Their state ownership, persistence, contract families, work-package and verification mapping is tracked in the [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md). All three remain IN PROGRESS until the mapped contracts and tests are fully reconciled and verified.

### 2.1 Deployment semantics that must not be conflated

The owner-approved requirement is concurrent first-release availability of cloud operation and offline-capable mobile operation. It does not, by itself, specify a single shared live process, a cloud-dependent mobile client, automatic state replication or first-release multi-device synchronization.

The architecture must distinguish:
- **Shared implementation:** both deployment contexts use the same versioned contracts and authoritative cognitive-core implementation/semantics; they are not separate intelligence designs.
- **Runtime authority:** each runtime must enforce policy at the boundary where an operation is executed. A remote planner cannot authorize a local Android action.
- **Offline independence:** the mobile runtime must complete its required local workflows without a cloud connection.
- **State ownership and continuity:** the authoritative location of user state, cloud/mobile continuity, conflict handling and whether any subset of data is synchronized must be explicitly specified before implementation. Do not infer that shared contracts mean shared live state.
- **Synchronization scope:** the existing decision to defer multi-device synchronization remains distinct from the requirement to deliver cloud and offline-mobile operation concurrently. Any required first-release cross-context continuity must be stated explicitly and reconciled with that deferred scope.

The builder's provisional recommendation is Option B (selective synchronization) if one continuous cognitive history is required; Option A remains the no-sync alternative with separate histories. The owner must resolve this before WP-15 implementation authorization. See the [topology decision record](../architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md).

### 2.2 Dependency-graph audit

The declared WP-00…WP-16 prerequisite edges were checked as a directed graph. WP-15 depends on WP-00…WP-13; WP-14 is optional for the first release because model fine-tuning is not required by PR-01…PR-18. The graph is acyclic; one valid topological ordering is:

`WP-00 → WP-01 → WP-02 → WP-03 → WP-04 → WP-05 → WP-06 → WP-07 → WP-08 → WP-09 → WP-10 → WP-11 → WP-12 → WP-13 → WP-14 → WP-15 → WP-16`

This is a valid ordering, not a required serial schedule. Independent packages may proceed concurrently once their prerequisites and interfaces are stable (for example, WP-05 and WP-06 after their common prerequisites, and WP-14 can proceed independently of WP-15 once its WP-12 prerequisites are met). WP-00 also has the separate external gate of planning-exit approval. The graph audit checks only dependency cycles; it does not prove that every package has complete component ownership, machine-readable contracts, executable acceptance fixtures or authorization to start.

## 3. Dependency principles

- Work packages describe dependency constraints, not a rigid serial waterfall. Independent tasks may proceed concurrently once their contracts and prerequisites are stable.
- Governance is established before any action gateway or external disclosure path can be considered complete.
- Capability discovery and environment representation precede reliable capability selection and execution.
- Experience, representation and provenance precede claims about memory or learning.
- Prediction and observed outcome must be independently represented; the system cannot rewrite a prediction after seeing the result.
- Learning evaluation depends on a stable baseline, data provenance and repeatable task fixtures.
- Android integration is a first-release platform requirement because offline-capable mobile is a concurrent first-release target. The capability architecture remains broader than the first-release set of validated scenarios.
- Cloud and offline mobile share contracts and the authoritative cognitive core. Cloud must not become a hidden dependency for offline mobile or a remote bypass of local authorization.
- General multi-device synchronization, voice/continuous sensing and broad external integrations remain later expansions unless the owner changes scope. If the owner accepts the builder's Option B recommendation, only the explicitly approved first-release continuity subset moves into WP-15; broad device handoff remains WP-16.
- No WP can use a fixed task-to-action catalogue as a substitute for discovery, reasoning or learning.

## 4. First-release scope boundary

The first release demonstrates the real end-to-end cognitive and operational loop with a deliberately bounded, evidence-backed subset of available capabilities. The subset is selected through architecture, platform feasibility, permission and owner approval—not hardcoded as the complete future capability scope.

The first-release acceptance scenario must verify general mechanisms:
- Environment and capability discovery.
- Capability representation with provenance and constraints.
- Objective decomposition and planning using discovered interfaces.
- Independent local authorization and platform permission checks.
- Execution, verification and uncertain-outcome recovery.
- Outcome evaluation and persistent use of evidence in a later related task.
- Offline operation without cloud dependency.
- Shared contracts and consistent cognitive semantics across CLI, cloud and mobile contexts.

No specific Android operation is selected by this roadmap. The separate first permitted local action remains an owner-reserved acceptance decision.

## 4.1 No-hardcoding invariant — work-package verification crosswalk

The NHC regression family is a release-spanning architectural invariant, not a single feature test. The mapping below assigns where each test must be implemented and executed; the examples are test stimuli, not an exhaustive capability list.

| Test | Required work packages | What the test must prove |
|---|---|---|
| NHC-001 | WP-01, WP-06, WP-11 | A new context, actor, resource or schema-compatible provider is encountered and represented without a task-specific core branch or closed ontology change. |
| NHC-002 | WP-06, WP-09, WP-10, WP-11 | The same objective under different situations and available means (including human-mediated and non-device means) leads to evidence-based route reasoning, not a fixed objective-to-operation mapping or platform priority. |
| NHC-003 | WP-06, WP-09, WP-10 | Incomplete observation or means evidence remains unknown; the system can ask, observe, wait, delegate or report limits rather than inventing an entity, affordance, interface or route. |
| NHC-004 | WP-07, WP-12 | Failure evidence changes knowledge only within its supported context and does not become a universal prohibition. |
| NHC-005 | WP-04, WP-11, WP-12 | Success does not create permission, universal competence or authority to repeat an action in a new scope. |
| NHC-006 | WP-06, WP-15 | Removing or changing an illustrative platform/tool example does not alter the open-world model or define its boundary. |
| NHC-007 | WP-02, WP-12, WP-15 | An accepted evidence-backed update persists across restart and changes a later related task with traceable evaluation provenance. |
| NHC-008 | WP-04, WP-11, WP-13 | Repeated successful actions cannot weaken authorization, risk classification, approval or owner authority. |

A work package cannot claim its no-hardcoding obligation is met by passing only its local unit tests. The integration suite must execute the relevant NHC tests against unseen objectives, entities, relationships, contexts and means—including non-device/human-mediated cases—and unseen task variations, not merely a new capability descriptor. Explicit schemas, protocols, permission checks, resource limits and safety invariants are engineered constraints, not hardcoded behavioural substitutes.

## 5. Work-package status discipline

For each WP, record separately:
- **Specified:** scope, contracts, dependencies and acceptance criteria are documented.
- **Ready:** prerequisites and required design reviews are complete.
- **Authorized:** owner has explicitly approved starting that WP.
- **Implemented:** code/configuration exists.
- **Validated:** executable tests or platform measurements pass.
- **Accepted:** exit criteria and required approvals are satisfied.

A WP cannot inherit completion from an earlier similarly numbered WP in a superseded table. PR #1 is a foundation scaffold proposal only; it does not mean WP-00 is accepted.

## 6. Roadmap completion criteria

This roadmap itself becomes COMPLETE — VERIFIED only when:
1. All prior WP tables are reconciled or clearly marked historical/superseded.
2. Every package maps to the architecture component and contract owners.
3. Dependencies form an acyclic, justified graph.
4. First-release targets and owner decisions are reflected without contradiction.
5. Every WP has measurable deliverables, test/evidence requirements and an exit gate.
6. The independent reviewer has assessed the final roadmap revision.
7. The owner approves the planning exit and implementation authorization separately.

**Current status:** IN PROGRESS. This roadmap is a builder proposal and does not authorize implementation.
