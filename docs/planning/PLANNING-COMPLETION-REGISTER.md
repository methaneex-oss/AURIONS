# AURIONS — Planning Completion Register

- **Branch:** `docs/complete-system-architecture`
- **Purpose:** Track planning-layer completion using evidence, not document existence or optimistic labels.
- **Current phase:** Architecture planning and technical design, with implementation planning in progress.
- **Implementation authorization:** Not granted.
- **Last builder audit:** 2026-11-11.
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
| Cognitive architecture | IN PROGRESS | A dedicated mechanism/interaction architecture now specifies responsibilities, state ownership, invariants, feedback, concurrency and verification scenarios. | Specify mechanism-level state, inputs/outputs, interactions, concurrency/interrupts, feedback, learning pathways and testable behavioural change without fixed behaviour mappings. |
| Experience, representation and context | IN PROGRESS | Concepts and some contracts are described. | Specify observation provenance, representation alternatives, context lifecycle, uncertainty, updates and links into memory/belief/prediction. |
| Memory, knowledge and belief | IN PROGRESS | Domain ownership, entities, evidence and revision concepts are documented. | Reconcile schemas and contracts; define lifecycle/retention/retrieval semantics and traceability; distinguish storage from learning. |
| Prediction, appraisal, attention and reasoning | IN PROGRESS | Logical responsibilities and some cognitive-cycle tests exist. | Define mechanism contracts and their interactions; ensure appraisal/attention are not hardcoded stimulus-to-state/action tables. |
| Goals, planning and decision | IN PROGRESS | Goal/plan records, dependencies, budgets and decision boundaries are described. | Complete plan/decision contracts, revision semantics, interruption/replanning, uncertainty handling and governance interaction. |
| Capability discovery and action architecture | IN PROGRESS | Generic tool/action security lifecycle exists; Android capability direction has been corrected at a high level. | Design a general environment/capability discovery architecture: observation, discovery sources, capability descriptions, constraints, provenance, validation, permission negotiation, planning, execution, verification, learning and capability change. Do not define a fixed phone-operation catalogue. |
| Learning, training, self-model and evolution | IN PROGRESS | Learning categories, worker boundaries, held-out evaluation and candidate lifecycle are documented. | Specify feedback/mechanism-learning interfaces, self-model update evidence, candidate isolation and activation boundaries; reconcile tests with cognitive mechanisms. |
| Governance, security and privacy | IN PROGRESS | R0–R5, exact-operation approval, default-deny and threat categories are specified. | Complete architecture-level traceability and identify unresolved authenticator, key custody, platform trust and enforcement contracts. Implementation security review remains a later evidence gate. |
| Persistence, artifacts and recovery | IN PROGRESS | Three-store design, DDL proposals, outbox, artifact lifecycle and recovery contracts exist. | Reconcile all schema versions and transaction rules; correct source inconsistencies; prepare executable migration/fault fixtures. SQL execution is a validation gate, not a documentation substitute. |
| Android platform architecture | IN PROGRESS | A dedicated mechanism-oriented Android environment/capability architecture has been drafted; contract ownership, cross-document integration and validation remain open. | Reconcile the dedicated Android architecture with component ownership, concrete contracts, cognitive mechanisms, product acceptance and test catalogue; validate Android-specific API, permission and lifecycle assumptions separately. |
| Cloud and offline-mobile architecture | IN PROGRESS | Owner decision requires concurrent cloud and offline-capable mobile targets with shared contracts/core. | Define topology, authority, local/remote boundaries, degraded modes, sync expectations, trust boundaries and deployment/update strategy. |
| Model/inference and compute routing | IN PROGRESS | Model-independent inference and local/external options are specified. | Reconcile provider/capability metadata, routing, privacy, resource constraints and model lifecycle contracts. Device performance validation remains external evidence. |
| Multi-device and synchronization | IN PROGRESS | Domain classification, change envelopes, conflict/deletion rules and tests are specified. | Cross-check against authoritative store ownership, governance and offline-mobile first-release requirements; implementation and SY tests are later gates. |
| Technical contracts and component boundaries | IN PROGRESS | Command/query/event, worker, authorization and operation contracts are drafted. | Check every architecture component against concrete contract ownership; remove ambiguous/duplicate definitions; resolve compatibility/versioning and missing schemas/fixtures. |
| Implementation planning and work packages | IN PROGRESS | A canonical dependency-driven roadmap is drafted; adoption and dependency audit across every planning document remain open. | Historical WP tables are now marked superseded in the source specification and contract supplement; architecture sequence points to the canonical roadmap. Remaining: verify component ownership, dependency graph acyclicity, concurrent cloud/offline-mobile integration and measurable exit criteria. |
| Validation and testing planning | IN PROGRESS | Test catalogue and device/dependency/security procedures exist. | Trace every requirement to a test/evidence method; distinguish design review from executable tests; define coverage and first-release gate dependencies. |
| Planning documentation and decision traceability | IN PROGRESS | Core planning documents and review records exist. | Initial stale status claims and false Android action record have been corrected; root README, planning index and PR description updated. Remaining: complete full branch-wide search for stale claims, verify every link/status and re-fetch the final PR diff. |
| Final planning baseline | BLOCKED | Prior independent review exists for an earlier revision and accepted it with required corrections. | Complete builder-owned design work, reconcile current baseline, obtain independent re-review of exact final revision, resolve findings, then obtain explicit owner planning-exit approval. |

## 3. Builder-owned work remaining

These are the main-builder's responsibilities, not owner testing or independent-review work.

### B-01 — Complete the Android environment and capability architecture
- A dedicated Android architecture now defines environment observation, general discovery, dynamic descriptors, capability knowledge, planning, permission/governance separation, execution, verification and learning. Remaining: map every responsibility to concrete components/contracts/tests and reconcile with the product and deployment architecture.
- Define general discovery mechanisms and adapters rather than a hardcoded list of operations.
- Define capability descriptions as data: identity/version, source, interface/schema, preconditions, effects, constraints, permission requirements, risk, reversibility, resource needs, cancellation, verification and lifecycle.
- Define how discovered capabilities are validated, compared, selected, invoked and re-discovered when the environment changes.
- Define how AURIONS learns from capability-use outcomes and revises capability knowledge without treating a failed attempt as a universal prohibition or a success as unconditional permission.
- Define OS permission and independent AURIONS governance as separate gates.
- Define limits honestly: discovery cannot manufacture OS privileges, bypass sandboxing or guarantee arbitrary access.

### B-02 — Complete the cognitive mechanism contracts
- Reconcile the dedicated cognitive mechanism architecture with concrete C++ ownership, versioned contracts, authoritative persistence, Android capability discovery, canonical roadmap and acceptance tests.
- Specify data/state transitions, provenance, uncertainty and temporal relationships.
- Define iterative, concurrent, interruptible and feedback interactions; do not turn the cycle into a rigid pipeline.
- Specify how prediction/outcome evaluation changes memory, beliefs, strategies and later decisions.
- Specify testable experience-dependent change without hardcoded stimulus-to-behaviour mappings.

### B-03 — Operationalize the no-hardcoding principle
- The principle is now explicitly defined in the completion register and both dedicated architecture documents. Remaining: trace it through all product requirements, implementation contracts, work packages, review criteria and test fixtures.
- Separate engineered mechanisms/invariants from data and behaviour learned or discovered through experience.
- Permit explicit safety invariants, schemas, protocols, resource limits and policy constraints; these are not learned behaviour.
- Require provenance, confidence/uncertainty and evaluation for acquired capability knowledge.
- Add architecture and test checks that detect regressions toward hardcoded behaviour.

### B-04 — Reconcile architecture, product and platform boundaries
- The architecture and canonical roadmap now distinguish CLI first interface from concurrent cloud/offline-mobile operation. Remaining: verify exact topology, interface scope, local authority and deployment dependencies without making cloud mandatory for offline mobile.
- Ensure Android integration is not deferred wholesale if offline mobile is a concurrent first-release target.
- Separate first-release integration requirements from later expansion (voice, multi-device, broader providers) without narrowing the underlying capability architecture.
- Align C++ core, platform adapters, inference, Python workers and governance boundaries.

### B-05 — Reconcile persistence, contracts and recovery
- Initial cross-mapping has been added for cognitive and capability mechanisms. Remaining: compare canonical entity definitions, proposed DDL, event contracts, worker contracts and implementation-ready contracts; resolve duplicate/missing schemas and state ownership.
- Resolve duplicated or conflicting definitions and schema ownership.
- Ensure cross-store references, outbox delivery, idempotency, recovery, artifact lineage, deletion and sync rules agree.
- Produce a single source of truth for each contract.

### B-06 — Reconcile implementation work packages and roadmap
- Reconcile the differing WP tables in the source specification, architecture and planning-contract supplement to the canonical roadmap; verify component owners and dependencies.
- Correct sequencing so shared contracts, persistence, runtime, cognition, capability discovery, action governance and Android integration are properly dependent.
- Keep implementation scope evidence-driven; no fixed operation catalogue.
- Ensure concurrent cloud/offline mobile direction is reflected in work packages and gates.

### B-07 — Complete architecture-wide consistency and completeness audit
- Trace each owner decision and foundational invariant into architecture, product, contracts, roadmap and tests.
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
