# AURIONS — Planning Completion Register

- **Branch:** `docs/complete-system-architecture`
- **Purpose:** Track planning-layer completion using evidence, not document existence or optimistic labels.
- **Current phase:** Architecture planning and technical design, with implementation planning in progress.
- **Implementation authorization:** Not granted.
- **Last builder audit:** 2026-11-11 (error/compatibility contract completion and full changed-Markdown link/status scan).
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
| Cognitive architecture | IN PROGRESS | Dedicated mechanism/interaction architecture plus a 17-domain contract crosswalk exist. | Canonical payload schemas now cover the 17 cognitive domains and major operational/protocol families. Remaining: complete per-mechanism command/query/error and state-transition semantics, causal/version concurrency rules, executable CM fixtures and full architecture consistency audit. |
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
| Planning documentation and decision traceability | IN PROGRESS | Core planning documents and review records exist. | Initial stale status claims and the false Android action record have been corrected; root README, planning index and PR description updated. A repository audit of all 17 Markdown files changed in PR #2 found no missing relative Markdown links. A targeted stale-claim scan found only two benign matches: the initial specification's explicit statement that it does not authorize implementation, and the planning index's explicit statement that implementation is not authorized. No stale schema-count, Android-action, first-interface or premature-authorization claim was found by the targeted scan. This is a bounded static scan, not a semantic proof of all 37 changed files. Remaining: complete requirement-to-source trace verification, audit non-Markdown contracts/schemas/fixtures/DDL and re-fetch the final PR diff. |
| Final planning baseline | BLOCKED | Prior independent review exists for an earlier revision and accepted it with required corrections. | Complete builder-owned design work, reconcile current baseline, obtain independent re-review of exact final revision, resolve findings, then obtain explicit owner planning-exit approval. |

## 3. Builder-owned work remaining

These are the main-builder's responsibilities, not owner testing or independent-review work.

### B-01 — Complete the Android environment and capability architecture
- A dedicated Android architecture now defines environment observation, general discovery, dynamic descriptors, capability knowledge, planning, permission/governance separation, execution, verification and learning. A component/contract/state/test crosswalk has now been added. The canonical Android environment/discovery/capability payload semantics have been specified and reconciled to the contract matrix. Machine-readable descriptor, discovery, capability-knowledge, plan-step, operation and lifecycle payload schemas/fixtures now exist. Provider identity/trust lifecycle, discovery/provider error classes, retry/side-effect interpretation and capability invalidation interactions have now been specified in Android architecture §6.1–6.3. Added canonical `providerLifecycle`, `providerFailure` and `compatibilityNegotiationState` definitions to `schemas/domain-payloads.v1.schema.json`, with a generic fixture and normative Android lifecycle/failure binding in §6.4. Remaining: map every AD/CAP scenario to an executable fixture; complete event binding semantics; reconcile deployment/state ownership; and perform Android API/permission/lifecycle validation against a target Android baseline.
- Define general discovery mechanisms and adapters rather than a hardcoded list of operations.
- Define capability descriptions as data: identity/version, source, interface/schema, preconditions, effects, constraints, permission requirements, risk, reversibility, resource needs, cancellation, verification and lifecycle.
- Define how discovered capabilities are validated, compared, selected, invoked and re-discovered when the environment changes.
- Define how AURIONS learns from capability-use outcomes and revises capability knowledge without treating a failed attempt as a universal prohibition or a success as unconditional permission.
- Define OS permission and independent AURIONS governance as separate gates.
- Define limits honestly: discovery cannot manufacture OS privileges, bypass sandboxing or guarantee arbitrary access.

### B-02 — Complete the cognitive mechanism contracts
- A new [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) maps all 17 cognitive domains and the Android discovery/execution responsibilities to ownership, persistence, contract families, work packages and tests.
The canonical matrix is the single mechanism-to-component/persistence/event/test crosswalk; the dedicated architecture document links to it rather than duplicating it. Remaining: reconcile the canonical payload definitions with each mechanism's exact input/output/error/state transitions, map the newly specified causal/version concurrency rules to command/query/event schemas and DDL, and ensure every CM-* case has a concrete fixture and assertion.
- Data/state transitions, provenance, uncertainty and temporal relationships are described in the mechanism contracts. §6.2 now defines expected-revision checks, dependency-version validation, per-store ordering, optimistic concurrency, domain-specific conflict handling and cancellation/dispatch races. Remaining: bind these rules to each exact command/query/event schema and proposed DDL, then create executable conflict/replay/cancellation fixtures.
- Define iterative, concurrent, interruptible and feedback interactions; do not turn the cycle into a rigid pipeline.
- Specify how prediction/outcome evaluation changes memory, beliefs, strategies and later decisions.
- Specify testable experience-dependent change without hardcoded stimulus-to-behaviour mappings.

### B-03 — Operationalize the no-hardcoding principle
- The principle is explicitly defined across the dedicated architecture documents and completion register. NHC-001…NHC-008 regression acceptance checks have been added to the contract test catalogue and mapped to the responsible WP-01/WP-04/WP-06/WP-07/WP-09/WP-10/WP-11/WP-12/WP-13/WP-15 packages in the canonical roadmap. Remaining: trace the invariant against every product requirement and review criterion, ensure each mapped WP's fixtures are concrete, and execute code-level checks after implementation.
- Separate engineered mechanisms/invariants from data and behaviour learned or discovered through experience.
- Permit explicit safety invariants, schemas, protocols, resource limits and policy constraints; these are not learned behaviour.
- Require provenance, confidence/uncertainty and evaluation for acquired capability knowledge.


### B-04 — Reconcile architecture, product and platform boundaries
- The architecture and canonical roadmap distinguish CLI first interface from concurrent cloud/offline-mobile operation. A dedicated topology decision analysis compares three deployment options and now recommends Option B (dual runtime with selective domain synchronization) if one continuous personal cognitive history is required. This is a builder recommendation, not an owner decision. Remaining: obtain the owner's resolution on whether that limited synchronization scope belongs in the first release or whether separate cloud/mobile histories (Option A) are acceptable. WP-15 is not implementation-ready until this is resolved.
- Ensure Android integration is not deferred wholesale if offline mobile is a concurrent first-release target.
- Separate first-release integration requirements from later expansion (voice, multi-device, broader providers) without narrowing the underlying capability architecture.
- Align C++ core, platform adapters, inference, Python workers and governance boundaries.

### B-05 — Reconcile persistence, contracts and recovery
- The event catalogue now has an explicit event-family-to-payload-definition map. The operation event family was reconciled to the full 19-state operation projection; `accepted` is a command response, not an operation state, and `running` replaces the ambiguous `started` event. Added operational payload contracts for context invalidation, outcome observation, representation revision, approval request, experiment completion, candidate lifecycle, artifact manifest, external disclosure, retention/deletion, sync conflicts, Python worker request/progress/result/failure, command/query envelopes, command responses, compatibility negotiation and structured errors. Positive fixtures now total 52; negative fixtures total 13. The limited custom structural subset check passed the 52 positive payload fixtures plus the separate descriptor, envelope and decision fixtures, and rejected all 13 negative fixtures. This is not full Draft 2020-12 validation or cross-language conformance.
- Contract-to-DDL audit identified eight explicit gaps (CCM-01…CCM-08) in the [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md).
- Proposed memory migration v3 adds typed plan-step contracts and learning-update details; proposed events migration v2 adds exact operation details and per-attempt receipts. The proposed base operation-state constraints and outcome operation ID representation were also aligned with the operation lifecycle and UUID convention.
- These are documentation-level design corrections only; DDL has not been executed. Proposed event migration v2 binds task checkpoints to plan/context/capability/dependency versions; the event-store base DDL now assigns durable local `event_sequence` values to support `event_consumers.last_sequence`; cognitive architecture §6.1 specifies attention restart reconstruction. Both require executable fixtures and migration validation. The canonical Draft 2020-12 schema set now contains the common envelope, extensible capability descriptor and 52 generic domain/protocol/operational payload fixtures, including context invalidation, outcome observation, representation revisions, approval requests, experiment completion, candidate lifecycle, artifact manifests, disclosure, retention/deletion, sync conflicts and worker request/progress/result/failure. A custom structural subset check passed for all 52 positive domain/protocol/operational payload fixtures, the separate capability descriptor fixture, the common envelope fixture and the decision-recorded fixture. All 13 negative fixtures were rejected for their intended structural violations. The checker covers selected structural constraints and selected conditionals only; it is not a full JSON Schema Draft 2020-12 validator. Remaining: independently verify every event-to-payload binding against event semantics; define and schema every family-specific command request/response and query input/result (the generic envelopes are not sufficient); the provider lifecycle, typed provider failure and compatibility-negotiation state contracts now have machine-readable definitions and a generic fixture; turn the remaining application-wide error-code registry, family-specific command/query schemas and complete registry semantics into machine-readable contracts and fixtures; select/pin a full validator and generator; establish C++/Python conformance; reconcile canonical entities with proposed DDL; and add CI enforcement.
- Resolve duplicated or conflicting definitions and schema ownership.
- Ensure cross-store references, outbox delivery, idempotency, recovery, artifact lineage, deletion and sync rules agree.
- Produce a single source of truth for each contract. The canonical schema directory includes the common envelope, capability descriptor and expanded domain/operational payload set; it is not yet complete or toolchain-validated.
- Complete CCM-04 schema/fixture/conformance coverage, including family-specific command/query payload schemas; execute CCM-01…CCM-08 migration, transition, event-sequence, checkpoint and attention-recovery verification; execute migration syntax/integrity/fault validation only when the target SQLite baseline is pinned.

### B-06 — Reconcile implementation work packages and roadmap
- The canonical roadmap reconciles the historical WP tables. PR #1 was inspected: it is a minimal version-library/build/CI smoke scaffold, contains no cognitive or capability behaviour, and keeps C++20 explicitly provisional. No scaffold changes are recommended before planning exit. The WP-00…WP-16 prerequisite graph has been rechecked after removing an unintended WP-14→WP-15 dependency: it has 59 edges, is acyclic, and has no missing prerequisite nodes. WP-15 requires WP-00…WP-13; Python training/fine-tuning infrastructure is not a first-release prerequisite because product acceptance explicitly excludes that requirement. Remaining: verify component ownership and acceptance criteria for every package, resolve cloud/mobile state continuity, then rebase/reconcile PR #1 only after the planning baseline is approved.
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
| BA-006 | Medium | The contract matrix mapped the Decision subsystem to decision.recorded.v1, but the implementation-contract event catalogue and domain schema initially lacked a complete event-body definition. | Added decision.recorded.v1 to the event catalogue, decisionRecorded payload schema and generic deferred-decision fixture; the later event-body map now binds the event to that schema. | Full schema/toolchain validation and C++/Python conformance remain open. |
| BA-007 | Medium | The roadmap's first-release integration exit did not explicitly bind the cloud and offline-mobile targets to separate acceptance evidence. | Bound WP-15 to product acceptance PR-15…PR-18: cloud runtime, shared contract compatibility, offline mobile operation and local authority/state boundaries. | Execute these acceptance cases in both required deployment contexts after implementation. |
| BA-008 | High | Operational/event payload families were only partially machine-readable; worker, artifact, disclosure, retention, sync-conflict and several event lifecycle bodies lacked explicit schemas or event-to-body bindings. | Added 14 operational/event payload definitions and five command/query/error/negotiation protocol definitions, explicit event-family bindings, and generic positive fixtures; total positive payload fixtures are now 52. Added eight negative fixtures; all 13 negative fixtures were rejected by the custom structural subset checker. | Full JSON Schema Draft 2020-12 validation, semantic review of every event binding, final error-code/compatibility semantics, C++/Python conformance and CI enforcement remain open. |
| BA-009 | HIGH | The generic command/query envelopes did not explicitly identify command/query types; the command envelope also treated operation/capability references as mandatory for all commands. | Added open namespaced `command_type` and `query_type` identifiers resolved by versioned registries, made operation/capability references optional where not applicable, and echoed command type/version in responses. Added positive fixtures and a negative missing-command-type fixture. | Family-specific command request and query input/result schemas, complete registry semantics and executable consumer validation remain open. |
| BA-010 | HIGH | Event consumers stored `last_sequence`, but the proposed `events` table had no explicit append sequence; causal ordering could not be implemented as documented. | Added store-local `event_sequence INTEGER PRIMARY KEY AUTOINCREMENT`, retained immutable `event_id` as unique identity, and specified append/receipt/consumer checkpoint semantics with EV-001…EV-004. | Proposed SQL has not been executed; monotonic sequence, crash atomicity, duplicate handling and consumer replay require migration/fault tests. |

These findings do not establish completion of any planning layer. They document specific corrections and remaining work discovered by the builder audit.
