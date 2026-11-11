# AURIONS — Planning Completion Register

- **Branch:** `docs/complete-system-architecture`
- **Purpose:** Track planning-layer completion using evidence, not document existence or optimistic labels.
- **Current phase:** Architecture planning and technical design, with implementation planning in progress.
- **Implementation authorization:** Not granted.
- **Last builder audit:** 2026-11-11 (event payload/schema coverage expansion and repository reconciliation).
- **Authority:** Existing owner decision register in `INITIAL-ENGINEERING-SPECIFICATION.md`; this register tracks completion and does not replace owner decisions.

## 1. Completion semantics

Every planning layer has exactly one status:

- **NOT STARTED** — no substantive work exists.
- **IN PROGRESS** — substantive work exists, but one or more required design, consistency or verification criteria remain open.
- **BLOCKED** — progress depends on a named external input, owner decision or prerequisite.
- **COMPLETE — VERIFIED** — all defined design criteria are addressed, cross-document consistency is checked, traceability is present, and evidence supports the completion claim.

The following do not qualify as completion: a page exists; a section has been drafted; a checklist is ticked; an independent reviewer accepted an earlier revision; or a proposal is described as implementation-ready.

Use separate evidence labels:
- **SPECIFIED** — written as a design/proposal.
- **REVIEWED** — examined for internal and cross-document consistency.
- **VALIDATED** — tested against executable schemas, tools, platform or measured environment.
- **IMPLEMENTED** — exists in code/configuration.
- **VERIFIED** — acceptance evidence demonstrates the stated requirement.

A design can be specified without being validated or implemented. Do not collapse these states.

## 2. Planning-layer status

No layer is currently marked COMPLETE — VERIFIED. This is deliberate: the current planning baseline has not passed the full audit and consistency criteria below.

| Planning layer | Current status | Existing work | Remaining builder work |
|---|---|---|---|
| Product identity, purpose and non-goals | IN PROGRESS | Mission and first-release product proposal exist. | Reconcile every product statement with owner decisions, no-hardcoding principle, actual release targets and architecture; distinguish committed requirements from proposals. |
| Foundational principles and authority rules | IN PROGRESS | Owner decision register and governance principles exist. | Convert principles into enforceable architectural invariants and trace them through components, contracts, acceptance criteria and change control. |
| System architecture | IN PROGRESS | Logical layers, ownership, deployment direction and dependency rules are documented. | Complete architecture-wide reconciliation; resolve incomplete/contradictory boundaries and prove every major responsibility has an owner and contract. |
| Cognitive architecture | IN PROGRESS | Dedicated mechanism/interaction architecture plus a 17-domain contract crosswalk exist. | Complete concrete payload schemas, state-transition/causal version semantics, executable fixtures and full architecture consistency audit. |
| Experience, representation and context | IN PROGRESS | Owners, persistence tables, API families and CM/CG tests are mapped in the contract matrix. | Define machine-readable payload schemas, immutable revision semantics, context invalidation and causal/staleness handling; add fixtures. |
| Memory, knowledge and belief | IN PROGRESS | Domain ownership, DDL entities, evidence/revision concepts and verification mapping are documented. | Reconcile payload schemas, lifecycle/retention/retrieval semantics, indexes and deletion lineage; distinguish storage from learning. |
| Prediction, appraisal, attention and reasoning | IN PROGRESS | Mechanism responsibilities, durable appraisal/reasoning records, transient attention ownership and test IDs are mapped. | Specify payload schemas, prediction immutability, attention replay/restart semantics and evidence-driven allocation fixtures. |
| Goals, planning and decision | IN PROGRESS | Goal/plan/decision persistence and command/event families are mapped; proposed memory v3 adds typed plan-step contracts. | Complete plan supersession/checkpoint/stale-input semantics, exact decision schemas and replan/recovery fixtures. |
| Capability discovery and action architecture | IN PROGRESS | Dedicated Android mechanism architecture and crosswalk cover observation, discovery, descriptors, evidence, planning, governance, execution, verification and learning. | Complete machine-readable descriptor/operation schemas, provider trust/lifecycle contracts, executable AD/CAP fixtures and platform-specific validation plan. No fixed operation catalogue. |
| Learning, training, self-model and evolution | IN PROGRESS | Learning categories, worker boundaries, held-out evaluation, self-model/evolution ownership and proposed typed learning-update details are mapped. | Complete machine-readable experiment/update manifests, causal attribution limits, candidate lifecycle schemas and executable evidence fixtures. |
| Governance, security and privacy | IN PROGRESS | R0–R5, exact-operation approval, default-deny and threat categories are specified. | Complete architecture-level traceability and identify unresolved authenticator, key custody, platform trust and enforcement contracts. Implementation security review remains a later evidence gate. |
| Persistence, artifacts and recovery | IN PROGRESS | Three-store design, initial DDL, proposed additive artifact/capability/cognitive-state schema migration, outbox and recovery contracts exist; none has been executed. | Reconcile migration version/checksum, table ownership, indexes, FKs, artifact/capability lineage, retention and cross-store transaction rules; prepare executable migration/fault fixtures. SQL execution is a validation gate, not a documentation substitute. |
| Android platform architecture | IN PROGRESS | A dedicated mechanism-oriented Android environment/capability architecture has been drafted; contract ownership, cross-document integration and validation remain open. | Reconcile the dedicated Android architecture with component ownership, concrete contracts, cognitive mechanisms, product acceptance and test catalogue; validate Android-specific API, permission and lifecycle assumptions separately. |
| Cloud and offline-mobile architecture | IN PROGRESS | Owner decision requires concurrent cloud and offline-capable mobile targets with shared contracts/core. | Define topology, authority, local/remote boundaries, degraded modes, sync expectations, trust boundaries and deployment/update strategy. |
| Model/inference and compute routing | IN PROGRESS | Model-independent inference and local/external options are specified. | Reconcile provider/capability metadata, routing, privacy, resource constraints and model lifecycle contracts. Device performance validation remains external evidence. |
| Multi-device and synchronization | IN PROGRESS | Domain classification, change envelopes, conflict/deletion rules and tests are specified. | Cross-check against authoritative store ownership, governance and offline-mobile first-release requirements; implementation and SY tests are later gates. |
| Technical contracts and component boundaries | IN PROGRESS | Component ownership and command/query/event families are mapped to all cognitive domains and Android capability responsibilities. | Complete exact message-body schemas, C++/Python generated types, fixture corpus, error/cancellation semantics and dependency graph verification. |
| Implementation planning and work packages | IN PROGRESS | Canonical WP-00…WP-16 dependency roadmap exists and cognitive/capability mechanisms map to work packages. | Complete full component-to-WP trace, validate dependency graph acyclicity, resolve concurrent cloud/offline-mobile state/topology contract and verify measurable exits. |
| Validation and testing planning | IN PROGRESS | Test catalogue and device/dependency/security procedures exist. | Trace every requirement to a test/evidence method; distinguish design review from executable tests; define coverage and first-release gate dependencies. |
| Planning documentation and decision traceability | IN PROGRESS | Core planning documents and review records exist. | Initial stale status claims and false Android action record have been corrected; root README, planning index and PR description updated. Remaining: complete full branch-wide search for stale claims, verify every link/status and re-fetch the final PR diff. |
| Final planning baseline | BLOCKED | Prior independent review exists for an earlier revision and accepted it with required corrections. | Complete builder-owned design work, reconcile current baseline, obtain independent re-review of exact final revision, resolve findings, then obtain explicit owner planning-exit approval. |

## 3. Builder-owned work remaining

These are the main-builder's responsibilities, not owner testing or independent-review work.

### B-01 — Complete the Android environment and capability architecture
- A dedicated Android architecture now defines environment observation, general discovery, dynamic descriptors, capability knowledge, planning, permission/governance separation, execution, verification and learning. A component/contract/state/test crosswalk has now been added. The canonical Android environment/discovery/capability payload semantics have now been specified in the implementation contract and reconciled to the contract matrix. Remaining: define machine-readable JSON Schema/IDL and fixture artifacts, map all scenarios into executable fixtures, and reconcile deployment/state ownership.
- Define general discovery mechanisms and adapters rather than a hardcoded list of operations.
- Define capability descriptions as data: identity/version, source, interface/schema, preconditions, effects, constraints, permission requirements, risk, reversibility, resource needs, cancellation, verification and lifecycle.
- Define how discovered capabilities are validated, compared, selected, invoked and re-discovered when the environment changes.
- Define how AURIONS learns from capability-use outcomes and revises capability knowledge without treating a failed attempt as a universal prohibition or a success as unconditional permission.
- Define OS permission and independent AURIONS governance as separate gates.
- Define limits honestly: discovery cannot manufacture OS privileges, bypass sandboxing or guarantee arbitrary access.

### B-02 — Complete the cognitive mechanism contracts
- A new [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) maps all 17 cognitive domains and the Android discovery/execution responsibilities to ownership, persistence, contract families, work packages and tests.
The canonical matrix is the single mechanism-to-component/persistence/event/test crosswalk; the dedicated architecture document links to it rather than duplicating it. Remaining: specify exact per-mechanism input/output/error/state-transition schemas, reconcile concurrency and causal version semantics, and ensure every CM-* case has a concrete fixture and assertion.
- Specify data/state transitions, provenance, uncertainty and temporal relationships.
- Define iterative, concurrent, interruptible and feedback interactions; do not turn the cycle into a rigid pipeline.
- Specify how prediction/outcome evaluation changes memory, beliefs, strategies and later decisions.
- Specify testable experience-dependent change without hardcoded stimulus-to-behaviour mappings.

### B-03 — Operationalize the no-hardcoding principle
- The principle is explicitly defined across the dedicated architecture documents and completion register. NHC-001…NHC-008 regression acceptance checks have now been added to the contract test catalogue. Remaining: trace the invariant through all product requirements, work packages, review criteria and fixtures, then execute code-level checks after implementation.
- Separate engineered mechanisms/invariants from data and behaviour learned or discovered through experience.
- Permit explicit safety invariants, schemas, protocols, resource limits and policy constraints; these are not learned behaviour.
- Require provenance, confidence/uncertainty and evaluation for acquired capability knowledge.


### B-04 — Reconcile architecture, product and platform boundaries
- The architecture and canonical roadmap distinguish CLI first interface from concurrent cloud/offline-mobile operation. A roadmap note and a dedicated topology decision analysis now separate shared implementation from live state/synchronization and compare three deployment options. Remaining: builder recommendation must be reconciled with the first-release product boundary; owner approval is required only if the recommendation changes the synchronization/continuity scope. WP-15 is not implementation-ready until this is resolved.
- Ensure Android integration is not deferred wholesale if offline mobile is a concurrent first-release target.
- Separate first-release integration requirements from later expansion (voice, multi-device, broader providers) without narrowing the underlying capability architecture.
- Align C++ core, platform adapters, inference, Python workers and governance boundaries.

### B-05 — Reconcile persistence, contracts and recovery
- Contract-to-DDL audit identified seven explicit gaps (CCM-01…CCM-07) in the [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md).
- Proposed memory migration v3 adds typed plan-step contracts and learning-update details; proposed events migration v2 adds exact operation details and per-attempt receipts. The proposed base operation-state constraints and outcome operation ID representation were also aligned with the operation lifecycle and UUID convention.
- These are documentation-level design corrections only; DDL has not been executed. Proposed event migration v2 binds task checkpoints to plan/context/capability/dependency versions; cognitive architecture §6.1 specifies attention restart reconstruction. Both require executable fixtures and migration validation. The canonical Draft 2020-12 schema set now contains the common envelope, extensible capability descriptor and 47 generic domain/operational payload fixtures, including context invalidation, outcome observation, representation revisions, approval requests, experiment completion, candidate lifecycle, artifact manifests, disclosure, retention/deletion, sync conflicts and worker request/progress/result/failure. A current custom structural subset check is still required after this expansion; it is not a full JSON Schema Draft 2020-12 validation. A custom structural subset check passed for all 32 positive domain payload fixtures, the capability descriptor fixture and the common envelope fixture; all five negative fixtures were rejected for their intended structural violations. This is not a full JSON Schema Draft 2020-12 validation. Remaining: verify every event-to-payload binding against semantics; define stable error/compatibility payloads and any uncovered event bodies; expand negative fixtures; choose/pin a full validator and generator; establish C++/Python conformance; reconcile canonical entities with proposed DDL; and add CI enforcement.
- Resolve duplicated or conflicting definitions and schema ownership.
- Ensure cross-store references, outbox delivery, idempotency, recovery, artifact lineage, deletion and sync rules agree.
- Produce a single source of truth for each contract. The canonical schema directory includes the common envelope, capability descriptor and expanded domain/operational payload set; it is not yet complete or toolchain-validated.
- Complete CCM-04 schema/fixture/conformance coverage; execute CCM-01…CCM-07 migration, transition, checkpoint and attention-recovery verification; execute migration syntax/integrity/fault validation only when the target SQLite baseline is pinned.

### B-06 — Reconcile implementation work packages and roadmap
- The canonical roadmap reconciles the historical WP tables. PR #1 was inspected: it is a minimal version-library/build/CI smoke scaffold, contains no cognitive or capability behaviour, and keeps C++20 explicitly provisional. No scaffold changes are recommended before planning exit. The WP-00…WP-16 prerequisite graph has been checked and is acyclic; one valid topological ordering is recorded in the roadmap. Remaining: verify component ownership and acceptance criteria for every package, reconcile first-release topology, then rebase/reconcile PR #1 only after the planning baseline is approved.
- Correct sequencing so shared contracts, persistence, runtime, cognition, capability discovery, action governance and Android integration are properly dependent.
- Keep implementation scope evidence-driven; no fixed operation catalogue.
- Ensure concurrent cloud/offline mobile direction is reflected in work packages and gates.

### B-07 — Complete architecture-wide consistency and completeness audit
- A [Owner Decision Traceability Matrix](OWNER-DECISION-TRACEABILITY-MATRIX.md) now maps MP-01…MP-06, IP-01…IP-10, UQ-01…UQ-17 and operational-authority decisions to architecture, contracts, roadmap and test IDs. It is a traceability baseline, not validation evidence.
- First focused crosswalk completed for cognitive/capability state ownership and persistence; the seven resulting CCM findings are recorded with severity and required resolution.
- Verify every trace in the owner decision matrix against the exact current source files; extend the audit to every architectural invariant, product requirement, failure path and dependency.
- Check component ownership, allowed/forbidden dependencies, state ownership and authority boundaries.
- Check all critical paths, failure modes, recovery, privacy, security and resource assumptions.
- Record every finding with severity, disposition and evidence; no silent assumptions.

### B-08 — Finalize planning baseline and review package
- Correct stale and contradictory documentation.
- Publish the canonical completion matrix and unresolved-gate register.
- Re-fetch and verify the exact branch revision, file contents, PR metadata and status.
- Prepare the exact final revision for independent re-review.
- Do not merge PRs or authorize implementation without the required review and owner approval.

## 4. External and owner-dependent gates (not builder completion claims)

The builder can prepare procedures and contracts, but cannot fabricate these results:
- Target-device sustained inference, memory, thermal, battery, storage and Android lifecycle measurements.
- Actual SQL DDL/migration execution and fault-injection results.
- Selected dependency/license/SBOM audit evidence after versions are chosen.
- Security validation of implemented key, IPC, update and data-flow mechanisms.
- Independent review of the exact final planning revision.
- Explicit owner approval of the planning exit and implementation transition.
- Any genuinely owner-reserved product/authority decision.

## 5. No-hardcoding invariant

For this project, "no hardcoding" means:

**Do not encode desired intelligence, acquired behaviour, capability scope or task-to-action conclusions as fixed developer-authored mappings. Engineer the mechanisms through which AURIONS observes, discovers, represents, evaluates, learns and adapts.**

This does not prohibit explicit engineering invariants such as message schemas, safety rules, permission boundaries, cryptographic protocols, resource budgets or deterministic validation logic. Those constrain and protect the system; they must not be confused with preprogramming its learned behaviour.

Examples supplied by the owner are scenarios to help design and test general mechanisms. They are not an exhaustive list, implementation scope or permission to hardcode those examples.

## 6. Exit criteria

Planning can be marked COMPLETE — VERIFIED only when:
1. Every planning layer in Section 2 has passed its defined design and consistency checks or is explicitly staged by an owner-approved decision.
2. Every owner decision is traceable and no proposal is misrepresented as an owner decision.
3. Cognitive and capability-discovery mechanisms have complete contracts and testable interactions.
4. The no-hardcoding invariant is operationalized across architecture, contracts, roadmap and tests.
5. Product, architecture, platform, persistence, governance, contracts and roadmap are mutually consistent.
6. One canonical implementation roadmap exists with dependency-aware work packages and measurable exit criteria.
7. Every requirement has an acceptance/evidence method and known limitations are recorded.
8. Builder-owned review findings are resolved and exact revision is re-fetched/verified.
9. Independent re-review of that exact revision is complete and required corrections are resolved.
10. External validation gates are passed or explicitly staged/accepted by the owner with clear restrictions on what implementation may proceed.
11. The owner explicitly approves planning exit and the next authorized implementation scope.

Until then, planning remains IN PROGRESS or BLOCKED as recorded above. No implementation authorization is implied.

## 7. Builder audit findings from 2026-11-11

The following findings were identified during the current cross-document pass. Corrections are recorded; unresolved items remain open rather than being labelled complete.

| ID | Severity | Finding | Disposition | Remaining evidence/work |
|---|---|---|---|---|
| BA-001 | Medium | Product decision list reused item number 3, making owner decisions ambiguous. | Corrected numbering in the product definition. | Re-fetch and confirm final content. |
| BA-002 | High | Product scope row named Native Android UI even though the owner selected CLI as first user-facing interface and did not select a native mobile UI technology. | Reframed as offline-capable Android platform integration; explicitly states that the row does not select a native UI. | Reconcile with deployment topology and first-release acceptance. |
| BA-003 | High | Concurrent cloud and offline-mobile targets plus deferred multi-device synchronization did not explicitly define whether shared contracts meant shared live state, independent runtimes or cross-context continuity. | Added a dedicated topology decision analysis comparing independent runtimes, selective synchronization and cloud-compute-service options; the roadmap and product acceptance now explicitly identify the unresolved state-ownership choice. | Builder recommendation and any required owner approval must be resolved before WP-15 is implementation-ready. |
| BA-004 | Medium | The builder initially added duplicated crosswalk tables to the Android and cognitive architecture documents even though a canonical Cognitive and Capability Contract Matrix already existed. | Removed the duplicated tables; both architecture documents now point to the matrix as the single traceability source and to the implementation contract as the payload source. | Verify the matrix against DDL and schema sources; turn scenarios into executable fixtures. |
| BA-005 | Medium | No-hardcoding had scenario tests but lacked a named regression family covering extensibility, generic planning, scoped evidence updates and authority invariance. | Added NHC-001 through NHC-008 to the implementation-contract test catalogue. | Tests are specified, not executed; code-level review and behavioural fixtures remain future validation. |
| BA-006 | Medium | The contract matrix mapped the Decision subsystem to decision.recorded.v1, but the implementation-contract event catalogue and domain schema initially lacked a complete event-body definition. | Added decision.recorded.v1 to the event catalogue and added a decisionRecorded payload schema plus a generic deferred-decision fixture. | Validate schema/fixture with the selected toolchain and add negative fixtures. |
| BA-007 | Medium | The roadmap's first-release integration exit did not explicitly bind the cloud and offline-mobile targets to separate acceptance evidence. | Bound WP-15 to product acceptance PR-15…PR-18: cloud runtime, shared contract compatibility, offline mobile operation and local authority/state boundaries. | Execute these acceptance cases in both required deployment contexts after implementation. |

These findings do not establish completion of any planning layer. They document specific corrections and remaining work discovered by the builder audit.
