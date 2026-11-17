# First-Release Command/Query Scope and Gap Analysis

**Status:** Builder technical analysis; D-01 accepted, D-02 Option B selected, and D-04 exact §12 command/query classification owner-accepted on 2026-11-17. No registry entry is dispatchable and this is not implementation authorization.  
**Applies to:** BR-001 and BR-002 in the 2026-11-12 main-builder pre-review audit.  
**Source revision examined:** PR #2 branch `docs/complete-system-architecture`, head `8884f51b82c350d9a0db98af9903c44e2a44231c`.  
**Source artifacts:** `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md`, `docs/architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md`, `docs/architecture/OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md`, and `schemas/command-query-registry.v1.json`.

## 1. Purpose and boundary

BR-001/BR-002 must be closed against the accepted first-release workflows, not by attempting to make every catalogued interface dispatchable. D-01 accepted PR-01…PR-20 and D-02 selected Option B on 2026-11-16. This document identifies the minimum command/query surface implied by that baseline, separates required interfaces from owner-dependent interfaces, and records the gaps between that surface and the current registry.

This document records the builder's technical analysis supporting D-04. The owner accepted the exact §12 classification on 2026-11-17. Acceptance is limited to first-release scope classification; it does not approve each handler contract, select the first Android action, authorize implementation, or make any registry entry dispatchable.

The governing architecture remains objective- and situation-centred. An objective is not a derived goal; a plan is not an objective; a proposal is not authorization; an affordance hypothesis is not a capability grant; a provider receipt is not an observed outcome.

## 2. Workflow-derived scope

| Product workflow | Required contract capability | Proposed first-release scope |
|---|---|---|
| 0 — Cloud runtime | Authenticated owner context, policy-bounded execution, durable experience/task/outcome state, cloud-side ownership | Required platform envelope; D-02 selects bounded selective synchronization of approved durable domains, with local execution authority retained per runtime |
| A — Offline conversation | Submit experience, assemble context, persist representation/experience, respond through inference abstraction | P0 |
| B — Recall | Search/retrieve persisted memory with provenance and inspect supporting records | P0 |
| C — Bounded objective | Create/revise/inspect an objective; derive and persist a distinct plan; checkpoint and control resumable task state | P0 |
| D — Permitted local action | Discover/assess relevant means, propose exact interaction, obtain independent authorization, dispatch/reconcile and verify outcome | Required product acceptance, but concrete first action is owner-reserved; contract design may proceed without selecting the action |
| E — Later outcome use | Persist observed outcome with evidence/lineage and retrieve it in a later related interaction | P0 |
| F — Permissions/resources | Inspect effective permissions and policy, deny unauthorized/ambiguous requests, inspect audit evidence and enforce budgets | P0 |

P0 means required to support the workflow contract in the proposed first release. It does not mean implementation-ready. P1 means conditional on the owner-reserved local-action choice or a later explicitly approved integration. Excluded means not part of the first-release dispatch surface.

## 3. Existing registry entries: proposed disposition

### 3.1 P0 command candidates already present

| Command | Workflow | Builder disposition |
|---|---|---|
| `experience.submit` | A | P0; define experience/evidence aggregate revision, owner scope, durable write and immutable event/outbox semantics |
| `representation.create` | A, B | P0; define source-experience lineage, representation revision and trust/provenance rules |
| `context.assemble` | A, B, C, E | P0; define read dependencies, context version/freshness and no-authority semantics |
| `context.invalidate` | A, B, C, E | P0 only if explicit invalidation is part of the owning context lifecycle; otherwise internal owner operation, not a public command |
| `memory.retrieve` | B, E | P0; this is a state-producing retrieval/audit operation only if the product requires durable retrieval records; otherwise it should be a query, not a command |
| `belief.propose`, `belief.revise` | B, E | P0; distinguish evidence-backed belief revision from direct mutation and retain contradictory evidence |
| `goal.create`, `goal.revise`, `goal.cancel` | C | P0 only for derived goal lifecycle; these do not satisfy objective lifecycle and must not be relabelled as objective commands |
| `plan.propose`, `plan.revise`, `plan.checkpoint` | C | P0; plan revisions must bind the objective revision, dependencies, constraints and evidence used |
| `task.start`, `task.pause`, `task.resume`, `task.cancel` | C | P0; existing command-specific contracts remain specified but per-entry conflict/replay/recovery execution evidence is still open |
| `outcome.evaluate` | E | P0; evaluation must distinguish observed evidence, attribution uncertainty and inferred lesson |

### 3.2 P0 query candidates already present

| Query | Workflow | Builder disposition |
|---|---|---|
| `memory.search` | B, E | P0; provenance-aware owner-scoped retrieval |
| `representation.inspect` | A, B | P0 |
| `context.get` | A, B, C, E | P0 |
| `belief.inspect` | B, E | P0 |
| `goal.get` | C | P0 for derived goals only |
| `plan.get` | C | P0 |
| `task.status` | C | P0 |
| `permission.inspect` | F | P0; return effective, current grants/policy only within authenticated owner scope |
| `audit.lookup` | F | P0; field-level redaction and non-disclosure of secret material are mandatory |

### 3.3 Conditional P1 command candidates already present

| Command family | Condition |
|---|---|
| `capability.discover`, `capability.verify`, `capability.invalidate` | Only where a selected means requires platform-specific capability discovery; these are not universal representations of possible means |
| `operation.propose`, `operation.cancel`, `operation.reconcile` | Required for the selected local-action path; exact action, risk and adapter contract remain owner-/platform-dependent |
| `approval.request`, `approval.revoke` | Required where the selected action's risk/authority policy requires explicit approval; approval remains separate from model proposal |
| `capability.knowledge.propose`, `capability.knowledge.revise` | Only if first-release acceptance requires persistent capability-use knowledge beyond the general world/means model |

### 3.4 Conditional P1 queries already present

| Query | Condition |
|---|---|
| `capability.search`, `capability.inspect`, `device.capabilities` | Only for a selected device-specific means; never use as the universal affordance query |
| `operation.status` | Required for the selected action lifecycle |
| `environment.inspect` | Only for a bounded observation contract needed by the selected workflow; must not imply always-on sensing |

### 3.5 Excluded from first-release dispatch

- `device.pair` and `device.revoke`: remain deferred multi-device operations.
- Unrestricted self-model/evolution activation and protected policy/value changes are excluded from first-release dispatch. The bounded training/evaluation path required by PR-19/PR-20 is in scope: `learning.experiment.submit` and `learning.candidate.evaluate` are P0 candidates for reproducible parameter-update experiments, held-out evaluation and candidate quarantine. `learning.update.propose` is a P0 candidate for evidence-linked experience-dependent adaptation. Candidate activation/rollback remains separately governed; exact lifecycle and approval linkage must be traced before D-04 is finalized. All remain design-only/non-dispatchable pending their implementation and verification gates.
- Any command or query whose owner, aggregate, data scope, semantics or per-entry acceptance evidence remains unresolved.

## 4. Foundational open-world command/query gaps

The initial registry omitted the minimum context-independent world/interaction operations implied by the product and foundational architecture. The eight world-interaction payload definitions and event families were not substitutes for command/query contracts. The builder has now added the proposed interface names below to the machine registry with versioned request/result schemas, aggregate/store bindings, semantic contracts, event bindings and acceptance IDs. They remain design proposals, not owner-approved release APIs or dispatchable entries.

| Proposed command | Owning domain | Minimum contract responsibility |
|---|---|---|
| `objective.create` / `objective.revise` | Objective subsystem | Persist owner intent, success/termination conditions, scope and revision; never collapse objective into a derived goal or plan |
| `world.entity.observe` | World-model subsystem | Record provisional entity/actor identity with evidence, provenance, scope and uncertainty |
| `world.relationship.revise` | World-model subsystem | Record contextual, time-scoped relationship evidence and retain contradictions |
| `situation.snapshot.create` | Context/world-understanding subsystem | Record partial observation, known unknowns, conflicts, time and validity; do not assert complete world state |
| `means.affordance.propose` | Means-reasoning subsystem | Store an evidence-backed, context-scoped affordance hypothesis; it grants no permission |
| `interaction.propose` | Interaction-control subsystem | Bind objective, situation, target, means, expected effects, risk and evidence; proposal is not authorization or dispatch |
| `interaction.outcome.record` | Outcome/evidence subsystem | Record independently observed outcome, source, uncertainty, causal links and reconciliation state |

Corresponding proposed query surface:

| Proposed query | Owning domain | Minimum contract responsibility |
|---|---|---|
| `objective.inspect` | Objective subsystem | Return objective revision, status, scope and success criteria |
| `world.entity.search` / `world.entity.inspect` | World model | Owner-scoped entity retrieval with provisional identity and provenance |
| `world.relationship.search` | World model | Context/time-bounded relationship retrieval |
| `situation.inspect` | Context/world understanding | Return snapshot age, evidence, unknowns and invalidation state |
| `means.affordance.search` | Means reasoning | Return context-scoped hypotheses with evidence/freshness, never implied authority |
| `interaction.inspect` | Interaction control | Return proposal/authorization/dispatch states as distinct fields |
| `interaction.outcome.inspect` | Outcome subsystem | Return observed evidence and evaluation separately |

The command/query names and bindings are now present in `command-query-registry.v1.json`, with the command transitions in `COMMAND-TRANSITION-AND-RECOVERY-CONTRACT-MATRIX.md` and query semantics in `QUERY-SEMANTICS-AND-SECURITY-CONTRACT-MATRIX.md`. They remain `design_only_not_dispatchable` pending handler-level implementation/tests and their individual security/verification gates; D-04 scope acceptance does not enable dispatch. Do not infer that every event should have a public command, or that a query should expose internal records wholesale.

## 5. Mandatory per-query contract baseline

Every P0 query must define all of the following before it can be considered dispatch-ready:

1. **Identity and scope:** derive `owner_id` and actor identity from the authenticated execution context; reject caller attempts to widen or substitute owner scope. Device/resource scope is explicit where applicable.
2. **Data classification:** classify every returned field, including identifiers, provenance, derived values and diagnostics. Default-deny fields not authorized for the caller and current purpose.
3. **Redaction/denial:** specify field-level redaction and whole-query denial. Avoid leaking whether another owner's record exists. Redaction must be deterministic and testable.
4. **Consistency:** define the exact guarantee for `snapshot`, `local_committed` and `eventual` per query. Never silently downgrade a requested guarantee. Authorization, permissions and operation dispatch state must not rely on stale eventual reads.
5. **Ordering/cursor:** define a total deterministic order with a stable unique tie-breaker. Cursors must bind owner, query/filter fingerprint, sort, consistency/snapshot watermark and expiry. Mutations during pagination must not silently duplicate/skip records; if the store cannot preserve the declared view, continuation must fail explicitly.
6. **Limits:** specify per-query deadline, maximum rows, maximum serialized bytes and any expensive-field budget. The envelope's generic 1..10000 bound is not an endpoint budget.
7. **Freshness/cache:** specify source revision, freshness window and invalidation. Do not cache authorization, permissions, mutable operation state or mutable task state across policy/revision changes. Cache immutable content only under a revision-bound key.
8. **Fixtures:** include allowed-owner, cross-owner denial, field redaction, malformed/expired cursor, deterministic pagination under mutation, consistency mismatch, deadline, row cap and byte cap cases as applicable.

No query is dispatch-ready until its own fields are populated and positive/negative fixtures execute against the actual handler.

## 6. Mandatory per-command contract baseline

Every P0 command must define:

- Owning aggregate, authoritative revision, legal source/target states and transition invariants.
- Authenticated owner/actor and exact resource/data/risk scope.
- Canonical request digest algorithm/version, idempotency key scope, same-digest replay and different-digest collision behaviour.
- Deadline semantics, safe cancellation points and races with commit/dispatch.
- Whether the command has external side effects; if so, exact dispatch state, receipt, uncertainty and reconciliation-before-retry rules.
- Exact error codes, recovery branches and immutable event payloads.
- Atomic local transaction/outbox boundary, optimistic concurrency failure and per-entry conflict/replay/recovery tests.

Command acceptance is not completion. A proposal is not authorization. An accepted local transaction is not proof that an external effect occurred. A dispatched or unknown side effect must be reconciled before retry.

## 7. Cross-cutting acceptance assertions

The first-release command/query subset must demonstrate, with executable fixtures and handler tests:

- Owner isolation for every read and write path.
- Objective/derived-goal/plan separation across create, revise, inspect and restart.
- Experience and evidence provenance survives representation, memory retrieval and later use.
- A partial or contradictory situation does not become a certain world fact.
- An affordance hypothesis does not grant authority or imply that a means is executable.
- Interaction proposal, approval, dispatch, provider receipt, observed outcome and evaluation remain distinct states.
- A task checkpoint resumes only against revalidated objective/plan/dependency revisions.
- Same idempotency digest replays the original result; a different digest under the same key is rejected.
- Before-commit and after-commit crash injection does not duplicate state transitions or external effects.
- Query pagination remains deterministic under concurrent insert/update/delete, or explicitly invalidates the cursor.
- Unauthorized, expired, revoked, ambiguous and cross-owner operations are denied without leaking protected fields.
- Cloud runtime cannot authorize mobile-local operations; no runtime silently assumes another runtime's local state.
- Non-device and human-mediated means remain representable; absence of a supported route is an explicit result, not a fabricated action.

## 8. Owner decisions and blockers — do not resolve by builder assumption

1. The product definition is proposed for owner review; its first-release workflow set must be accepted before this scope can become authoritative.
2. Cloud/mobile topology is resolved at option level: D-02 selects dual runtimes with bounded selective domain synchronization. Exact field-level allowlists, local-only classes, conflict/deletion/recovery semantics and executable SY acceptance cases remain open.
3. The first Android action remains an owner decision. No concrete capability, permission set or adapter is selected here.
4. Risk thresholds and approval policy for the selected action remain governed by the existing owner decision record.
5. Numerical query budgets and performance thresholds require measured baselines; the builder must propose values with evidence before they become acceptance thresholds.

## 9. Builder conclusion and next closure steps

**BR-001: OPEN. BR-002: OPEN. Overall planning status: NOT READY.**

The current registry is an incomplete design inventory, not a dispatch contract. The builder has identified a concrete scope gap: the registry's `goal.*` family cannot stand in for objective lifecycle, and the new open-world event/payload definitions are not yet represented by corresponding owner-scoped command/query interfaces. Closing this requires schema/registry and cross-document reconciliation, not merely filling generic strings on the existing 45/21 entries.

Next builder steps, in order:

1. Reconcile the proposed first-release scope with owner-approved product workflows and owner decisions.
2. Add or explicitly defer the missing objective/world/means/interaction command/query types, with exact schema and persistence bindings.
3. Define per-entry command aggregate transitions, owner/risk scope, idempotency, deadline/cancellation, side-effect/recovery, error/event/outbox semantics.
4. Define per-query owner scope, classification/redaction, consistency, ordering/cursor, limits and freshness/cache semantics.
5. Add entry-specific positive/negative fixtures and executable handler-level contract tests.
6. Keep all entries `design_only_not_dispatchable` until their own implementation and verification gates pass.

This analysis is a builder artifact only. It is not an independent review, tester result, product approval, implementation authorization or director acceptance.


## 10. Builder self-review and bounded structural verification (2026-11-12)

The builder re-fetched the current command/query registry, domain payload schema, world-interaction schema, event registry, error registry, and all six existing base/migration SQL files, then ran a bounded cross-artifact inspection against the exact branch revision.

**Checks executed and results:**

| Check | Result |
|---|---|
| Command/query registry parse | PASS — 45 commands and 21 queries parsed |
| Mapped command request/response schema references | PASS — all references resolve to declared definitions in the domain/world schema set |
| Query input/response/result schema references | PASS — all references resolve to declared definitions |
| Registry-to-proposed-DDL table references | PASS — every referenced table name was found in the six retrieved SQL files |
| Event registry structure | PASS — 84 event names present; every entry has a payload-schema reference and at least one fixture reference |
| Error registry structure | PASS — 35 entries; every entry has a handler-mapping reference and at least one fixture reference |
| First-release existing P0 command-name crosswalk | PASS — all referenced existing command names occur in the registry |

These are bounded source-level cross-reference checks executed against retrieved artifacts. They are not committed executable tests, do not parse or execute SQL, do not validate foreign-key/runtime behaviour, and do not prove that the referenced handlers, events or queries work.

**Self-review found the decisive closure gap remains:**

- 39 of 43 mapped commands still carry the eight unresolved semantic categories: aggregate transition/revision, exact owner/resource/risk scope, idempotency/replay/collision, deadline/cancellation, side-effect/reconciliation, error/recovery, emitted event/outbox and per-entry executable assertions.
- The four task-control commands carry the narrower remaining gap: per-entry conflict/replay/recovery execution evidence. Their generic twelve-case specification is not a substitute for command-specific executed tests.
- All 21 queries still carry all seven unresolved categories: owner/field scope, classification/redaction, consistency/snapshot, deterministic ordering/cursor, timeout/row/byte limits, freshness/cache, and positive/negative executable fixtures.
- The proposed objective/world/means/interaction interfaces are not yet canonical registry entries with request/response contracts, authoritative aggregate/persistence bindings, event mappings and executable acceptance tests.

**Builder verdict for this increment:** The scope analysis is internally cross-referenced at the structural level, but it does not close BR-001 or BR-002. Both remain OPEN and blocking. The registry remains design-only/non-dispatchable. Do not hand off for independent review or final testing until the remaining builder-owned technical contracts and self-review are complete. Owner-reserved product/topology/action decisions remain explicitly outside builder authority.


## 11. Owner-decision reconciliation — 2026-11-16

D-01 is accepted; D-02 Option B is selected; D-03 is staged; D-04's exact §12 classification was owner-accepted on 2026-11-17. The registry contains 54 command records and 29 query records; exact proposed identifiers must be derived from the registry at the final planning HEAD, not stale prose. No entry becomes dispatchable by inclusion in a proposal. The first-release subset must include the full bounded training path: reproducible experiment submission, worker budgets/cancellation, immutable artifact provenance, held-out evaluation, quarantine and separately governed activation/rollback. The registry includes `learning.experiment.submit`, `learning.candidate.evaluate` and `learning.update.propose`; their dependencies and PR-19/PR-20 lifecycle coverage remain to be proven. Option B's candidate domains are durable experience/provenance, representations, memory and evidence-backed beliefs, objectives/derived goals, and approved immutable model-version references. Sensitive raw observations, transient context, execution checkpoints, local capabilities, permissions, credentials, approvals and governance authority remain local by default. Field-level classification and executable SY tests remain open.


## 12. D-04 owner-accepted first-release subset — 2026-11-17

This section supersedes older unresolved owner-decision wording in §§8–9 where it conflicts with D-01/D-02. D-04 exact classification was owner-accepted on 2026-11-17. This is the accepted first-release interface classification, not dispatch authorization.

### Synchronization boundary

Under D-02 Option B, selected durable domain changes are synchronized internally through versioned change records, durable outboxes, idempotent relay/reconciliation and explicit conflict/deletion handling. This is runtime infrastructure, not a general-purpose user-dispatch command. No sync operation transfers device-local permissions, credentials, approvals, operation-dispatch state or governance authority. Exact field-level allowlists and executable SY acceptance evidence remain pre-implementation gates.

### P0 public/owner-facing command proposal

The minimum first-release command surface is:

- Experience and representation: `experience.submit`, `representation.create`, `context.assemble`.
- Evidence-backed knowledge: `belief.propose`, `belief.revise`.
- Objective and derived-goal lifecycle: `objective.create`, `objective.revise`, `goal.create`, `goal.revise`, `goal.cancel`.
- Planning and resumable work: `plan.propose`, `plan.revise`, `plan.checkpoint`, `task.start`, `task.pause`, `task.resume`, `task.cancel`.
- Open-world situation and interaction reasoning: `world.entity.observe`, `world.relationship.revise`, `situation.snapshot.create`, `means.affordance.propose`, `interaction.propose`, `interaction.outcome.record`.
- Experience-dependent adaptation and trainable model path: `outcome.evaluate`, `learning.update.propose`, `learning.experiment.submit`, `learning.candidate.evaluate`.

### P0 internal cognitive-cycle commands

These commands are required internal mechanisms for the first-release cognitive loop. They are not user-facing or model-selectable tools and must only be invoked by the owning runtime subsystem under its internal contract:

- Prediction: `prediction.create`, `prediction.evaluate`.
- Appraisal and attention: `appraisal.evaluate`, `attention.allocate`.
- Reasoning and decision recording: `reasoning.assess`, `decision.record`.

### P0 owner-governed self-model, evolution and approval lifecycle

These are internal/protected transitions needed for the WP-13 governed-evolution path and the first-release candidate lifecycle. They are not model-authorized operations or ordinary user-dispatch commands:

- Self-model and evolution proposals/evaluation: `self_model.update.propose`, `evolution.change.propose`, `evolution.candidate.evaluate`.
- Protected candidate lifecycle: `evolution.candidate.activate`, `evolution.candidate.rollback`.
- Owner-governed approval lifecycle: `approval.request`, `approval.decide`, `approval.revoke`.

`learning.candidate.evaluate` remains only in the public P0 group above; it is not repeated in this protected group. The distinct `evolution.candidate.evaluate` is protected internal.

`learning.candidate.evaluate` is classified once as a P0 public/owner-facing request for the held-out model-training evaluation required by PR-20. `evolution.candidate.evaluate` is a separate P0 internal/protected governed evolution-candidate evaluation in WP-13; the two are not interchangeable. The learning evaluation is deliberately not duplicated in the protected-command list. Activation and rollback require exact owner/governance authorization, immutable artifact identity, verified evaluation and rollback readiness. The machine-contract crosswalk now binds the learning update, experiment, attempt, learning evaluation and candidate artifact digest into the model-candidate proposal; the candidate ID is derived from the owner-scoped proposal and artifact digest. Host validation checks the canonical UUIDv5 identity, a schema-valid negative mismatch, and the canonical RFC 8785/SHA-256 activation and rollback digest vectors. These checks close the design/fixture crosswalk gap only; runtime recomputation, authenticated approval consumption and cross-store saga/recovery remain unimplemented and blocking before dispatch or activation. No model or worker may approve, activate or roll back its own candidate.

### P0 read-only query proposal

- Memory and evidence: `memory.search`, `knowledge.search`, `representation.inspect`, `context.get`, `belief.inspect`.
- Objectives and work: `objective.inspect`, `goal.get`, `plan.get`, `task.status`.
- World/situation/interaction: `world.entity.search`, `world.entity.inspect`, `world.relationship.search`, `situation.inspect`, `means.affordance.search`, `interaction.inspect`, `interaction.outcome.inspect`.
- Governance visibility: `permission.inspect`, `audit.lookup`.

### Conditional P1 commands and queries

These are conditional on the owner-selected first Android action, target-device validation and a demonstrated first-release workflow. They are not part of the default dispatch subset:

- Observation and discovery commands: `environment.observe`, `capability.discover`, `capability.verify`, `capability.invalidate`.
- Capability-use knowledge commands: `capability.knowledge.propose`, `capability.knowledge.revise`.
- Concrete operation commands: `operation.propose`, `operation.cancel`, `operation.reconcile`.
- Conditional read-only queries: `environment.inspect`, `capability.search`, `capability.inspect`, `capability.knowledge.inspect`, `device.capabilities`, `operation.status`.

The owner-governed `approval.*` commands above may also support a separately approved local-action lifecycle; their presence does not select an Android action or grant a permission. D-03 remains staged, so no concrete Android operation or platform-specific permission set is selected. The generic open-world reasoning contracts remain P0; concrete platform observation and execution remain conditional P1.

### Internal maintenance, diagnostics and deferred entries

- `context.invalidate` is internal context-lifecycle maintenance, not a public command.
- `memory.retrieve` is not a separate public command in this proposal; provenance-aware retrieval is represented by the P0 memory query unless an auditable state-changing retrieval workflow is proven necessary.
- `prediction.inspect`, `appraisal.inspect`, `attention.inspect`, `reasoning.inspect` and `decision.inspect` are owner-scoped internal diagnostic queries, not part of the first-release user-facing query surface.

`memory.search` is classified only as a P0 read-only query above; it is not an internal diagnostic entry.
- `device.pair` and `device.revoke` remain deferred; broad device handoff, voice, continuous sensing and broad external integrations remain outside first release.

### Registry-wide accounting

The following disjoint classification accounts for every registry identifier exactly once, without making entries dispatchable:

- **54 command records:** 27 P0 public/owner-facing; 14 P0 internal or owner-governed (6 cognitive-cycle + 8 protected lifecycle); 9 conditional P1; 2 internal maintenance/optional; 2 deferred. `learning.candidate.evaluate` is counted only in the public P0 group.
- **29 query records:** 18 P0 read-only; 6 conditional P1; 5 internal diagnostic. `memory.search` is counted only in the P0 read-only group.

All registry entries remain `design_only_not_dispatchable` until their own implementation and verification gates pass. Registry inclusion, P0 classification or owner approval of D-04 does not itself enable dispatch.

### Remaining technical gates before any classified entry can become dispatch-ready

1. Verify the complete 54-command/29-query classification against the registry at the final planning HEAD; preserve the counts and explicit disposition of every identifier.
2. Map every P0 entry to its aggregate, store, event, command/query semantics and acceptance scenario.
3. Complete the PR-19/PR-20 candidate lifecycle crosswalk: learning experiment artifact → candidate/evolution proposal identifiers → held-out evaluation → exact owner approval → activation → verified rollback. Do not assume the generic evolution IDs or approval digest bind correctly until proven by schemas and executable cases.
4. Complete per-entry positive/negative, owner-isolation, idempotency, concurrency, crash/recovery and resource-bound tests for all P0 commands.
5. Reconcile P0/P1 query privacy/redaction, cursor/snapshot semantics, limits and freshness against actual handlers; add executable positive/negative read-only tests.
6. Preserve `design_only_not_dispatchable` for every registry entry until its own implementation and verification gates pass; scope acceptance alone never enables dispatch.

**Builder recommendation and owner disposition (2026-11-17): ACCEPTED.** The owner accepted the exact classification and counts on the builder's recommendation. This final identifier-level reconciliation removes the two duplicate category placements without changing the accepted category counts: `learning.candidate.evaluate` is public P0 only; `memory.search` is P0 query only. The six technical gates above remain mandatory before affected entries can become dispatch-ready. Acceptance does not make any entry dispatchable or authorize implementation, Android action, training, candidate activation or governance operations.
