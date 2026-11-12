# AURIONS — Planning Completion Register

- **Branch:** `docs/complete-system-architecture`
- **Purpose:** Track planning-layer completion using evidence, not document existence or optimistic labels.
- **Mandatory governance standard:** [Project Directorship and Team Operating Standard](../governance/PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md) (effective 2026-11-12), governing role authority, milestone workflow, handoffs, scope control and director acceptance.
- **Mandatory builder standard:** [Builder Operating Protocol](../governance/BUILDER-OPERATING-PROTOCOL.md); builders must satisfy its self-review, testing, correction and evidence requirements.
- **Current phase:** Architecture planning and technical design, with implementation planning in progress.
- **Implementation authorization:** Not granted.
- **Last builder audit:** 2026-11-12 (task-run revision/event reconciliation, schema/fixture crosswalk and repository contract scan).
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

### B-00 — Open-world contract and persistence reconciliation (new builder work)
- Added `schemas/world-interaction.v1.schema.json` with owner-scoped, versioned objective, entity, relationship, situation, evidence, affordance hypothesis, interaction proposal and interaction outcome definitions. Added `schemas/event-registry.v1.json` plus its schema, keyed by all 84 event names with payload-schema and fixture references.
- Added a positive fixture covering a possible human custodian and a non-executed request; added a negative entity fixture missing evidence.
- Proposed `aurion_memory.migration_v4.sql` for owner-scoped, versioned world entities, relationships, situation snapshots, affordance hypotheses, interaction proposals and outcomes. Updated schema and persistence indexes.
- Remaining: validate JSON Schema Draft 2020-12 with an approved validator, execute the SQL migration on the pinned SQLite baseline, reconcile IDs/references/retention, and bind the new contracts to events, commands, queries, C++ owners, work packages and scenario tests. The new contracts remain design-only and are not dispatchable. A bounded custom structural check accepted the positive world-interaction fixture and rejected the negative entity fixture; this is not official JSON Schema Draft 2020-12 validation.


No layer is currently marked COMPLETE — VERIFIED. This is deliberate: the current planning baseline has not passed the full audit and consistency criteria below.

| Planning layer | Current status | Existing work | Remaining builder work |
|---|---|---|---|
| Product identity, purpose and non-goals | IN PROGRESS | Mission and first-release product proposal exist. | Reconcile every product statement with owner decisions, no-hardcoding principle, actual release targets and architecture; distinguish committed requirements from proposals. |
| Foundational principles and authority rules | IN PROGRESS | Owner decision register and governance principles exist. | Convert principles into enforceable architectural invariants and trace them through components, contracts, acceptance criteria and change control. |
| System architecture | IN PROGRESS | Logical layers, ownership, deployment direction and dependency rules are documented. | Complete architecture-wide reconciliation; resolve incomplete/contradictory boundaries and prove every major responsibility has an owner and contract. |
| Cognitive architecture | IN PROGRESS | Dedicated mechanism/interaction architecture plus a 17-domain contract crosswalk exist; the new objective/world/means architecture is now referenced as foundational. | Canonical payload schemas now cover the 17 cognitive domains and major operational/protocol families. Remaining: complete per-mechanism command/query/error and state-transition semantics, causal/version concurrency rules, executable CM fixtures and full architecture consistency audit. |
| World, entity, relationship and situation understanding | IN PROGRESS | Foundational objective-led architecture, initial context-independent JSON Schema contracts, a human-mediated positive fixture and proposed memory migration v4 now define an initial representation independent of device/platform models. | Define machine-readable payload schemas, immutable revision semantics, context invalidation and causal/staleness handling; add fixtures. |
| Memory, knowledge and belief | IN PROGRESS | Domain ownership, DDL entities, evidence/revision concepts and verification mapping are documented. | Reconcile payload schemas, lifecycle/retention/retrieval semantics, indexes and deletion lineage; distinguish storage from learning. |
| Prediction, appraisal, attention and reasoning | IN PROGRESS | Mechanism responsibilities, durable appraisal/reasoning records, transient attention ownership and test IDs are mapped. | Specify payload schemas, prediction immutability, attention replay/restart semantics and evidence-driven allocation fixtures. |
| Goals, planning and decision | IN PROGRESS | Goal/plan/decision persistence and command/event families are mapped; proposed memory v3 adds typed plan-step contracts. | Complete plan supersession/checkpoint/stale-input semantics, exact decision schemas and replan/recovery fixtures. |
| Means, affordance and interaction architecture | IN PROGRESS | Context-dependent affordance hypotheses and interaction proposals are now distinguished from device capability descriptors; initial schemas/fixtures and proposed persistence mapping exist. | Complete semantic ID/reference rules, event/command/query bindings, owner and state transitions, authorization and execution linkage, outcome attribution, retention/deletion and multi-context acceptance tests. Prove no universal capability registry is required. |
| Platform-specific interaction realizations | IN PROGRESS | Android is explicitly one context-specific realization; its discovery and permission model no longer defines the general action model. | Complete Android-specific contracts and empirical platform validation separately. Desktop, iOS, human-mediated, physical and other contexts remain representable possibilities, not implemented or assumed targets. |
| Learning, training, self-model and evolution | IN PROGRESS | Learning categories, worker boundaries, held-out evaluation, self-model/evolution ownership and proposed typed learning-update details are mapped. | Complete machine-readable experiment/update manifests, causal attribution limits, candidate lifecycle schemas and executable evidence fixtures. |
| Governance, security and privacy | IN PROGRESS | R0–R5, exact-operation approval, default-deny and threat categories are specified. | Complete architecture-level traceability and identify unresolved authenticator, key custody, platform trust and enforcement contracts. Implementation security review remains a later evidence gate. |
| Persistence, artifacts and recovery | IN PROGRESS | Three-store design, initial DDL, proposed additive artifact/capability/cognitive-state schema migration, outbox and recovery contracts exist; none has been executed. | Reconcile migration version/checksum, table ownership, indexes, FKs, artifact/capability lineage, retention and cross-store transaction rules; prepare executable migration/fault fixtures. SQL execution is a validation gate, not a documentation substitute. |
| Open-world interaction and means architecture | IN PROGRESS | A foundational objective-led architecture has now been added, separating objectives, world/situation, entities/actors, evidence, beliefs, affordances, authority, interactions and outcomes. Android is explicitly subordinated as one context-specific realization. | Reconcile the foundational model across product, cognition, contracts, payloads, events, persistence, governance, work packages and tests. Add semantic ownership/contracts and task-led verification for novel, human-mediated, non-device and multi-context cases. Builder semantic review remains open. |
| Android platform interaction realization | IN PROGRESS | Existing Android environment/discovery/capability mechanisms are retained but explicitly scoped as an Android-specific realization under the open-world architecture. | Reconcile Android payloads/events/ownership with the general interaction model; validate actual Android API, permission, lifecycle and device assumptions separately. Do not treat Android capability descriptors as universal means or the sole capability architecture. |
| Cloud and offline-mobile architecture | IN PROGRESS | Owner decision requires concurrent cloud and offline-capable mobile targets with shared contracts/core. | Define topology, authority, local/remote boundaries, degraded modes, sync expectations, trust boundaries and deployment/update strategy. |
| Model/inference and compute routing | IN PROGRESS | Model-independent inference and local/external options are specified. | Reconcile provider/capability metadata, routing, privacy, resource constraints and model lifecycle contracts. Device performance validation remains external evidence. |
| Multi-device and synchronization | IN PROGRESS | Domain classification, change envelopes, conflict/deletion rules and tests are specified. | Cross-check against authoritative store ownership, governance and offline-mobile first-release requirements; implementation and SY tests are later gates. |
| Technical contracts and component boundaries | IN PROGRESS | Component ownership and command/query/event families are mapped to all cognitive domains and Android capability responsibilities. | Complete exact message-body schemas, C++/Python generated types, fixture corpus, error/cancellation semantics and dependency graph verification. |
| Implementation planning and work packages | IN PROGRESS | Canonical WP-00…WP-16 dependency roadmap exists and cognitive/capability mechanisms map to work packages. | Complete full component-to-WP trace, validate dependency graph acyclicity, resolve concurrent cloud/offline-mobile state/topology contract and verify measurable exits. |
| Validation and testing planning | IN PROGRESS | Test catalogue and device/dependency/security procedures exist. | Trace every requirement to a test/evidence method; distinguish design review from executable tests; define coverage and first-release gate dependencies. |
| Planning documentation and decision traceability | IN PROGRESS | Core planning documents and review records exist. | Initial stale status claims and the false Android action record have been corrected; root README, planning index and PR description updated. A prior repository audit of all 17 Markdown files on the then-current 56-file PR snapshot found no missing relative Markdown links. The PR has since grown to 69 changed files; the newly added builder-audit link resolves, but the full current 69-file Markdown/link audit has not yet been rerun. A targeted stale-claim scan found only two benign matches in the earlier snapshot: the initial specification's explicit statement that it does not authorize implementation, and the planning index's explicit statement that implementation is not authorized. No stale schema-count, Android-action, first-interface or premature-authorization claim was found by that bounded scan. This is not a semantic proof of the current 69-file diff. Remaining: complete requirement-to-source trace verification, audit non-Markdown contracts/schemas/fixtures/DDL and re-fetch the final PR diff. |
| Final planning baseline | BLOCKED | Prior independent review exists for an earlier revision and accepted it with required corrections. | Complete builder-owned design work, reconcile current baseline, obtain independent re-review of exact final revision, resolve findings, then obtain explicit owner planning-exit approval. |

## 3. Builder-owned work remaining

### B-00 — Reconcile the foundational open-world interaction model
- A new objective-led architecture now establishes the world/situation, entity/actor, evidence/belief, affordance/means, authority/consent, interaction/effect and outcome distinctions. It explicitly rejects a device/platform-first system model and makes Android a subordinate realization.
- Remaining: reconcile all dependent product, cognitive, contract, schema, fixture, event registry/handlers, command/query, persistence, governance, work-package, acceptance and test artifacts. The new architecture is not yet COMPLETE — VERIFIED; this first pass is a structural correction, not proof that all dependent contracts are semantically closed.


These are the main-builder's responsibilities, not owner testing or independent-review work.

### B-01 — Complete the Android-specific interaction realization
- The Android-specific architecture retains environment observation, Android discovery, descriptors, capability knowledge, planning, permission/governance separation, execution, verification and learning, but is now explicitly subordinate to the open-world interaction architecture. A component/contract/state/test crosswalk has now been added. The canonical Android environment/discovery/capability payload semantics have been specified and reconciled to the contract matrix. Machine-readable descriptor, discovery, capability-knowledge, plan-step, operation and lifecycle payload schemas/fixtures now exist. Provider identity/trust lifecycle, discovery/provider error classes, retry/side-effect interpretation and capability invalidation interactions have now been specified in Android architecture §6.1–6.3. Added canonical `providerLifecycle`, `providerFailure` and `compatibilityNegotiationState` definitions to `schemas/domain-payloads.v1.schema.json`, with neutral validated-provider and enabled-provider positive fixtures, a dispatched-blind-retry negative fixture, and normative Android lifecycle/failure binding in §6.4. All 15 AD scenarios are now individually crosswalked in the canonical matrix to payload definitions and related contract checks. Remaining: create executable multi-step scenario fixtures/assertions in the owning implementation packages; semantically verify provider/discovery event bindings; reconcile deployment/state ownership; and perform Android API/permission/lifecycle validation against a pinned target Android baseline.
- Define general discovery mechanisms and adapters rather than a hardcoded list of operations.
- Define capability descriptions as data: identity/version, source, interface/schema, preconditions, effects, constraints, permission requirements, risk, reversibility, resource needs, cancellation, verification and lifecycle.
- Define how discovered capabilities are validated, compared, selected, invoked and re-discovered when the environment changes.
- Define how AURIONS learns from capability-use outcomes and revises capability knowledge without treating a failed attempt as a universal prohibition or a success as unconditional permission.
- Define OS permission and independent AURIONS governance as separate gates.
- Define limits honestly: discovery cannot manufacture OS privileges, bypass sandboxing or guarantee arbitrary access.

### B-02 — Complete the cognitive mechanism contracts
- A new [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) maps all 17 cognitive domains and the Android discovery/execution responsibilities to ownership, persistence, contract families, work packages and tests.
The canonical matrix is the single mechanism-to-component/persistence/event/test crosswalk; the dedicated architecture document links to it rather than duplicating it. All 21 CM scenarios are now individually crosswalked in the canonical matrix to payload definitions and related contract checks. Remaining: create executable multi-step scenario fixtures/assertions in the owning implementation packages; bind exact per-mechanism input/output/error/state-transition semantics to command/query/event registry entries and proposed DDL; and verify causal/version concurrency rules.
- Data/state transitions, provenance, uncertainty and temporal relationships are described in the mechanism contracts. §6.2 now defines expected-revision checks, dependency-version validation, per-store ordering, optimistic concurrency, domain-specific conflict handling and cancellation/dispatch races. Remaining: bind these rules to each exact command/query/event schema and proposed DDL, then create executable conflict/replay/cancellation fixtures.
- Define iterative, concurrent, interruptible and feedback interactions; do not turn the cycle into a rigid pipeline.
- Specify how prediction/outcome evaluation changes memory, beliefs, strategies and later decisions.
- Specify testable experience-dependent change without hardcoded stimulus-to-behaviour mappings.

### B-03 — Operationalize the no-hardcoding principle
- The principle is explicitly defined across the dedicated architecture documents and completion register. NHC-001…NHC-016 regression acceptance checks and CM-022…CM-029 open-world cognitive scenarios have been added to the contract test catalogue and mapped to the responsible WP-01/WP-04/WP-06/WP-07/WP-09/WP-10/WP-11/WP-12/WP-13/WP-15 packages in the canonical roadmap. Remaining: trace the invariant against every product requirement and review criterion, ensure each mapped WP's fixtures are concrete, and execute code-level checks after implementation.
- Separate engineered mechanisms/invariants from data and behaviour learned or discovered through experience.
- Permit explicit safety invariants, schemas, protocols, resource limits and policy constraints; these are not learned behaviour.
- Require provenance, confidence/uncertainty and evaluation for acquired capability knowledge.


### B-04 — Reconcile architecture, product and platform boundaries
- The architecture and canonical roadmap distinguish CLI first interface from concurrent cloud/offline-mobile operation. A dedicated topology decision analysis compares three deployment options and now recommends Option B (dual runtime with selective domain synchronization) if one continuous personal cognitive history is required. This is a builder recommendation, not an owner decision. Remaining: obtain the owner's resolution on whether that limited synchronization scope belongs in the first release or whether separate cloud/mobile histories (Option A) are acceptable. WP-15 is not implementation-ready until this is resolved.
- Ensure Android integration is not deferred wholesale if offline mobile is a concurrent first-release target.
- Separate first-release integration requirements from later expansion (voice, multi-device, broader providers) without narrowing the underlying capability architecture.
- Align C++ core, platform adapters, inference, Python workers and governance boundaries.

### B-05 — Reconcile persistence, contracts and recovery

- **Machine-readable API inventory:** added `schemas/command-query-registry.v1.schema.json` and `schemas/command-query-registry.v1.json`. The registry contains 45 command records (43 request-payload mappings and two deferred device commands) and 21 query records. All command/query records bind the common envelope; the 43 mapped commands and 21 queries bind payload/result schemas and generic payload-shape fixtures. Common authorization, idempotency-key/deadline fields, side-effect vocabulary, query authorization/scope, consistency modes and schema-level result bounds are recorded. All entries remain non-dispatchable.
- **Per-entry semantics still open:** per-command owner/device scope and risk classification, expected revisions beyond task control, idempotency scope/digest/replay, safe cancellation, side-effect/reconciliation, error mapping, emitted events and per-entry conflict/replay/recovery fixtures remain incomplete. Per-query field-level classification/redaction, deterministic ordering/cursors, timeout/byte limits, freshness/cache behavior and corresponding fixtures remain incomplete. Task-control commands additionally bind `task_runs.revision`, safe-point cancellation/reconciliation, no direct external side effect, `task.control.requested.v1` and `task.run.transitioned.v1`.
- **Proposed DDL table binding:** each of the 43 mapped commands and 21 queries now maps to exact proposed SQL table names and one or more owning stores through `table_bindings`. Static comparison against source-spec Sections 26.2–26.5.2 verified all referenced table names exist and are assigned to the correct store; 51 distinct proposed tables are referenced. The registry marks these mappings `mapped_to_proposed_ddl_not_executed`; they do not prove read/write transaction semantics or SQL validity.
- **Machine-readable DDL:** extracted the three base schemas and three additive migrations into `schemas/persistence/`: memory base, memory migration v2, memory migration v3, events base, events migration v2 and governance base. The source specification now links to these files instead of duplicating inline SQL. Static inventory finds 57 table definitions (20 memory base, 10 event base, 9 governance base, 13 memory v2, 2 memory v3, 3 event v2). A code-block FK audit found no missing or cross-store foreign-key targets. Proposed SQLite minimum is 3.38.0 because the DDL uses `STRICT` and built-in JSON functions; the actual Termux/Android build and compile options remain unverified. **No SQL has been executed.**
- **Event binding:** a static crosswalk extracted 76 unique event names and found 76 unique mappings, with no missing/extra/duplicate event names and no missing payload definitions. This proves mapping coverage and reference existence only; event semantics, outbox consumer behavior and DDL transaction atomicity remain to be verified.
- **Migration reference order:** static checks found all foreign-key targets available within each store's base schema and prior migrations: memory base → v2 → v3 (35 tables), events base → v2 (13 tables), governance base (9 tables). No missing FK targets were found in the proposed migration order. This is not SQLite parsing/execution, index validation, or fault testing.
- **Scenario traceability:** the canonical contract matrix individually crosswalks all 21 CM and 15 AD scenarios to payload definitions and related test-catalogue checks. Multi-step scenario fixtures and executable state assertions do not yet exist.
- **Fixture checks performed:** all 78 positive domain payload examples, all three provider lifecycle examples, the command/query registry against its schema, the error registry against its schema and all 35 `contractError` payload fixtures passed bounded structural subset checks. Three newly added negative fixtures (missing task-run revision, dispatched-provider blind retry, incomplete error-registry entry) were rejected as expected. The prior custom checker rejected the original 25 negative fixtures, but those 25 were not rerun in this audit. This is not full Draft 2020-12 conformance.
- **Error handling:** the 35-code/13-category seed registry has category-owned handler contracts and one schema-shaped `contractError` fixture per code. Entries remain `seed` and non-dispatchable until runtime handlers, code-specific recovery branches and executable recovery tests exist.
- **Validator/tooling:** Corvus C API 0.1.7 / Rust evaluator 0.2.2 and Rust-backed Python binding 0.2.2 are a proposed Apache-2.0 Draft 2020-12 validator pairing. The published artifacts do not include Android/Bionic builds; target cross-compilation, full transitive license/SBOM audit and C++/Python equivalence remain gates. No code generator is selected for the initial baseline; hand-authored typed adapters preserve open extension data.
- **Remaining builder work:** complete per-entry command/query semantics and fixtures; semantically verify all event mappings; complete error-code recovery tests; create multi-step CM/AD/CAP/AU/OP/DB/SY/LE scenario fixtures; execute base DDL and migrations against the proposed SQLite minimum and target Termux build; run migration, integrity, crash, backup/restore and fault tests; complete C++/Python validator conformance and CI; and reconcile all CCM-01…CCM-11 findings. No planning or persistence layer is marked complete or verified.

### B-06 — Reconcile implementation work packages and roadmap
- The canonical roadmap reconciles the historical WP tables. PR #1 was inspected at head `742232599a5dc37f48ea33cd9fef77924e060a38` (nine changed files); it is a minimal version-library/build/CI smoke scaffold, contains no cognitive or capability behaviour, and keeps C++20 explicitly provisional. Its latest head has a successful hosted `C++ Core` configure/build/test workflow, run [43104192873](https://github.com/methaneex-oss/AURIONS/actions/runs/43104192873). This is host CI only; no local clean build or Termux/Android build has been performed. No scaffold changes are recommended before planning exit. The WP-00…WP-16 prerequisite graph has 59 edges, is acyclic and has no missing prerequisite nodes. WP-15 requires WP-00…WP-13; Python training/fine-tuning infrastructure is not a first-release prerequisite. Remaining: complete component ownership and acceptance criteria for every package, resolve cloud/mobile state continuity, and after planning approval rebase/reconcile PR #1, pin `actions/checkout` by full commit SHA and pin/record the runner/toolchain, add host plus actual Termux/Android validation, and add schema/fixture CI only after the validator adoption gate passes.
- Correct sequencing so shared contracts, persistence, runtime, cognition, capability discovery, action governance and Android integration are properly dependent.
- Keep implementation scope evidence-driven; no fixed operation catalogue.
- Ensure concurrent cloud/offline mobile direction is reflected in work packages and gates.

### B-07 — Complete architecture-wide consistency and completeness audit
- A bounded identifier audit found all 33 source decision IDs represented in the owner-decision matrix and all 18 PR acceptance IDs in the product definition. This checks identifier presence only; semantic requirement-by-requirement reconciliation remains open.
- A [Owner Decision Traceability Matrix](OWNER-DECISION-TRACEABILITY-MATRIX.md) now maps MP-01…MP-06, IP-01…IP-10, UQ-01…UQ-17 and operational-authority decisions to architecture, contracts, roadmap and test IDs. It is a traceability baseline, not validation evidence.
- First focused crosswalk completed for cognitive/capability state ownership and persistence; the seven resulting CCM findings are recorded with severity and required resolution.
- A bounded identifier audit found all 33 source decision IDs (MP-01…06, IP-01…10, UQ-01…17) represented in the owner-decision matrix, and the product definition contains PR-01…PR-18. The canonical contract matrix now crosswalks all 21 CM and 15 AD scenarios to payload definitions and related catalogue checks. Remaining: semantically verify each decision and scenario against source requirements and exact handler/event/DDL semantics; extend the audit to every architectural invariant, product requirement, failure path and dependency. These identifier checks are trace evidence, not proof of semantic completeness.
- Check component ownership, allowed/forbidden dependencies, state ownership and authority boundaries.
- Check all critical paths, failure modes, recovery, privacy, security and resource assumptions.
- Record every finding with severity, disposition and evidence; no silent assumptions.

### B-08 — Finalize planning baseline and review package
- The main-builder pre-review audit is recorded at [MAIN-BUILDER-PRE-REVIEW-AUDIT-2026-11-12.md](../reviews/MAIN-BUILDER-PRE-REVIEW-AUDIT-2026-11-12.md). Its verdict is NOT READY; it is a closure ledger, not a final builder review or independent review.
- Current machine-readable inventory: 86 reusable domain-schema definitions; 78 named positive payload examples; 45 command records (43 mapped and two deferred); 21 query records; 35 error-registry entries. All 45 command and 21 query records retain unresolved handler bindings; all 35 error entries remain seed. These are inventory/reference-integrity checks, not semantic conformance or runtime evidence.
- Structural crosschecks currently recorded in the audit: schema/fixture references resolve; 84 event types now have a machine-readable registry with unique names, payload-schema references and fixture references; runtime handlers/consumers and semantic event validation remain outstanding to declared payload definitions; all 51 distinct command/query table references exist in their declared store; all 35 error entries reference a handler-contract section and an in-range fixture. Semantic correctness, SQL execution and handler behaviour remain unverified.
- Builder-owned closure remains: per-entry command/query semantics; code-specific error recovery; executable multi-step scenario contracts; semantic event/state/DDL reconciliation; validator and CI selection; security and key-lifecycle contract reconciliation; work-package/scaffold traceability; final 69-file repository and cross-document audit.
- Correct all stale and contradictory claims found during the final bounded audit. Re-run the entire changed-file and cross-reference scan after the last edit.
- Perform a separate final builder review of the exact final revision. Do not use the pre-review audit as a substitute for that review.
- Only after builder closure and final builder review, request the main independent reviewer to review that exact revision.
- Keep PR #2 draft/open/unmerged; do not authorize implementation or merge by implication.

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

## 7. Builder audit findings through 2026-11-12

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
| BA-008 | High | Operational/event payload families were only partially machine-readable; worker, artifact, disclosure, retention, sync-conflict and several event lifecycle bodies lacked explicit schemas or event-to-body bindings. | Added 14 operational/event payload definitions and five command/query/error/negotiation protocol definitions, explicit event-family bindings, and generic positive fixtures. The domain-payload fixture contains 78 named examples; the separate world-interaction fixture contains eight context-independent examples; the negative corpus now contains 29 files. Historical validation evidence is limited to the original 25 negative fixtures plus three subsequently added negative fixtures being rejected in bounded structural checks; do not infer that every current negative fixture has been rerun after all later edits. | Full JSON Schema Draft 2020-12 validation, semantic review of every event binding, final error-code/compatibility semantics, C++/Python conformance and CI enforcement remain open. |
| BA-009 | HIGH | The generic command/query envelopes did not explicitly identify command/query types; the command envelope also treated operation/capability references as mandatory for all commands. | Added open namespaced `command_type` and `query_type` identifiers resolved by versioned registries, made operation/capability references optional where not applicable, and echoed command type/version in responses. Added positive fixtures and a negative missing-command-type fixture. | Initial first-release command/query payload families are now mapped to versioned schemas and fixtures; device pairing/revocation remain explicitly deferred. Handler-specific transition/authorization/error semantics and executable consumer validation remain open. |
| BA-011 | HIGH | Provider lifecycle and typed discovery/provider failure semantics were described in prose but were not bound to canonical machine-readable payload contracts. | Added `providerLifecycle`, `providerFailure` and `compatibilityNegotiationState` definitions; added neutral validated-provider and enabled-provider fixtures; required validation/trust evidence for validated providers and separate governance plus current platform-permission evidence for enabled providers; made diagnostic-reference presence explicit; and aligned dispatched/unknown retry restrictions with the schema. | JSON parsing and local reference integrity are verified for the current fixtures; full Draft 2020-12 validation, transition-graph validation, event/command binding, provider-state runtime enforcement and Android platform validation remain open. |
| BA-012 | HIGH | `taskControlRequest.expected_version` had no matching persisted task-run revision, `taskRunStatus` exposed no version, and task control/state changes had no event-body binding. | Added `task_runs.revision` in proposed event/recovery migration v2; added the revision to `taskRunStatus`; defined `task.control.requested.v1` and `task.run.transitioned.v1`, the `taskRunTransition` payload/fixture, a task-run state graph and TS-001…TS-007. | The new fixtures have only been JSON-parsed/reference-checked; rerun the structural checker, full Draft 2020-12 validation, DDL migration/fault tests, atomic event/projection tests, scheduler replay and cancellation/recovery tests. |
| BA-013 | HIGH | Provider failure prose allowed a dispatch-possible state to be paired with ordinary retry, and the provider `enabled` state did not require machine-readable evidence of a separate governance decision and current platform permission. | Aligned Android failure semantics with `not_dispatched` / `dispatched` / `unknown` / `not_applicable`; schema now requires `reconcile_before_retry` for `dispatched` or `unknown`, requires explicit diagnostic-reference presence, and conditionally requires trust/validation evidence and governance/platform permission references for `enabled`. Added an enabled-provider positive fixture and a dispatched-blind-retry negative fixture; changed the generic provider example to neutral fixture identifiers. | New fixtures are JSON-parsed and references resolve; full schema validation, lifecycle transition validation, provider/OS integration tests and runtime enforcement remain open. |
| BA-014 | MEDIUM | The error taxonomy had stable representative codes and recovery prose but no versioned machine-readable registry artifact or schema. | Added `error-registry.v1.schema.json` and a 35-code/13-category `error-registry.v1.json` seed. Entries bind code/category, default side-effect and retry posture, recovery action and intervention policy; all remain `seed` with null handler mappings. Added an incomplete-entry negative fixture. | JSON parsing, 35 unique codes across 13 categories and local schema-reference integrity are verified; no full JSON Schema validation, handler mapping, code-specific recovery test or production registration is claimed. |
| BA-016 | HIGH | Threat model named assets, boundaries and key lifecycle but did not provide explicit security/key-lifecycle acceptance IDs or package traceability. | Added SEC-001…SEC-011 covering platform key provenance/separation, envelope encryption/rotation, device revocation, recovery, backup/restore, update signing, redaction, KMS failure, worker isolation and data egress; mapped to WP-00, WP-02, WP-03, WP-04, WP-05, WP-06, WP-13, WP-14 and WP-15. | Host-fake and actual Android/Termux/cloud execution; hardware-backed key evidence; KMS provider choice; recovery policy; signing chain; security implementation review and residual-risk acceptance. |
| BA-015 | HIGH | Command and query payload families were listed in prose tables but lacked a machine-readable per-type inventory and explicit dispatch status. | Added `schemas/command-query-registry.v1.schema.json` and `schemas/command-query-registry.v1.json` with 43 schema-mapped command types, two deferred device commands and 21 typed queries; owner/aggregate and persistence mappings are recorded. Every entry is explicitly non-dispatchable and unresolved handler semantics are explicit. | Complete per-entry revision/transition, authorization/data scope, idempotency, deadline/cancellation, side-effect, event/error, query redaction/consistency/ordering/limits/freshness bindings; add entry-specific fixtures and runtime consumer validation. |
| BA-010 | HIGH | Event consumers stored `last_sequence`, but the proposed `events` table had no explicit append sequence; causal ordering could not be implemented as documented. | Added store-local `event_sequence INTEGER PRIMARY KEY AUTOINCREMENT`, retained immutable `event_id` as unique identity, and specified append/receipt/consumer checkpoint semantics with EV-001…EV-004. | Proposed SQL has not been executed; monotonic sequence, crash atomicity, duplicate handling and consumer replay require migration/fault tests. |

These findings do not establish completion of any planning layer. They document specific corrections and remaining work discovered by the builder audit.


## 4. Builder follow-up — task-control contract reconciliation

**Status: IN PROGRESS — specified, not validated or implemented.**

The four scheduler controls (`task.start`, `task.pause`, `task.resume`, `task.cancel`) now have an explicit owner/task-run scope, actor authorization requirement, no-device/no-provider boundary, RFC 8785 canonical request digest and idempotency scope, replay/collision behaviour, local event-store transaction boundary, legacy-owner safety gate, and twelve acceptance cases in §4.2.3 of the implementation-ready contracts.

A proposed `aurion_events.migration_v3.sql` adds nullable ownership to legacy task rows, rejects new task rows without a non-empty owner, and adds a durable task-control receipt ledger. Legacy rows are intentionally not assigned an inferred owner. The migration is added to the persistence README sequence.

Registry entries for those four commands now carry the task-specific authorization and idempotency semantics; two corresponding generic unresolved bindings were removed. Their per-entry conflict/replay/recovery assertions remain unresolved, and they remain non-dispatchable.

**Not verified:** SQLite migration execution, trigger/DDL compatibility, lifecycle transition legality against every task state, RFC 8785 digest equivalence across C++/Python, receipt retention/tombstone policy, executable fault-injection/replay tests, and runtime handlers. This is a bounded design closure, not task-control completion.


### Migration v3 smoke-test evidence

An in-memory SQLite 3.46.1 smoke test of the v3 statements against prerequisite-compatible task/event tables passed selected invariants: legacy NULL-owner preservation and verified backfill, rejection of new ownerless task rows, rejection of reassignment after owner binding, unique receipt-scope enforcement, empty foreign-key check and `integrity_check=ok`. The complete base DDL/migration chain, target SQLite, crash/rollback, restore, concurrency, canonical digest equivalence and runtime handlers remain untested. Status remains IN PROGRESS.


The v3 receipt digest column additionally rejects values that are not exactly 64 lowercase hexadecimal characters. A focused SQLite 3.46.1 constraint test accepted a valid 64-character lowercase hexadecimal value and rejected non-hex, uppercase and wrong-length values. This remains a constraint smoke test, not proof that a C++/Python implementation computes RFC 8785 + SHA-256 identically.


## 8. Builder validation increment — JSON Schema corpus

**Status:** VERIFIED COMPLETE for the Python-host schema/fixture validation subtask only.

The repository now pins `jsonschema[format]==4.26.0` in `requirements-validation.txt`, provides `scripts/validate_schemas.py`, and runs it through `.github/workflows/schema-validation.yml`. Successful CI run #7 on revision `cda9023de34172679f8d5a01dddbdf54457956de` passed:
- 8 Draft 2020-12 schema meta-schema checks.
- 7 registry/fixture schema pairs.
- 78 positive domain payloads validated against same-named reusable definitions.
- 29 negative controls rejected as intended.

The test-development failures were investigated and corrected: the pip cache dependency path was explicit, and external schema references were normalized to canonical URNs. The final result is recorded in `docs/reviews/SCHEMA-VALIDATION-RESULTS-2026-11-12.md`.

**Not closed:** C++ validator equivalence, C++/Python serialization compatibility, Android/Termux dependency feasibility, runtime contract/handler validation, and semantic completeness of the registries. No registry is made dispatchable by schema validation.
