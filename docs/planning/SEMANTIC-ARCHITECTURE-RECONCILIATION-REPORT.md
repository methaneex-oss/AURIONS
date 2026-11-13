# AURIONS — Semantic Architecture Reconciliation Report

**Status:** Builder reconciliation proposal; not independently reviewed, owner-approved or implementation-authorized.  
**Scope:** BR-008 — reconcile foundational architecture, cognitive ownership, product workflows, command/query/event contracts, schemas, persistence ownership, work packages and acceptance evidence.  
**Core invariant:** Engineer mechanisms; let behaviour be acquired through experience.  
**Authority:** This report binds existing design proposals for traceability. It does not approve new product behaviour, select an Android action, select a cloud provider or authorize runtime dispatch.

## 1. Reconciliation result

The open-world architecture now has a machine-readable design contract surface for its foundational objective/world/means/interaction domains. The earlier gap where these concepts existed only as payload definitions and event names has been closed at the **specification and registry-binding level**.

Current branch inventory:
- 54 command entries: 52 mapped to typed request/response, owning aggregate/store, semantic transition, owner/actor authorization, idempotency, deadline/cancellation, side-effect/reconciliation, error and event bindings; two multi-device commands remain deferred.
- 29 read-only query entries: typed input/response/result schemas, owner scope, classification/redaction, consistency, ordering/cursor, freshness/cache and acceptance assertions.
- 89 event entries: each has a payload-schema and fixture reference; all remain design-only/non-dispatchable.
- 52 mapped commands have unique CC-001…CC-052 positive/negative acceptance assertions.
- 29 queries have unique QCC-001…QCC-029 positive/negative assertions and explicit read-only invariants.
- 89 reusable domain-payload schema definitions, 81 named positive domain fixtures and 29 negative controls are present in the current source corpus. Event, command and query schema/fixture reference checks are enforced in CI.

These are design and structural-integrity facts. They do not establish runtime handler/consumer correctness, executable cognitive scenarios, target-platform behaviour, security enforcement or production readiness.

## 2. Foundational concept separation

| Concept | Authoritative owner | Durable representation | Command / query surface | Event contract | Work package / evidence |
|---|---|---|---|---|---|
| Objective / desired state | Objective subsystem | `objective_records` | `objective.create`, `objective.revise`, `objective.inspect` | `objective.created.v1`, `objective.revised.v1` | WP-06/WP-10; objective/goal/plan distinction and owner-intent tests |
| Entity / actor | World-model subsystem | `world_entities` | `world.entity.observe`, `world.entity.search`, `world.entity.inspect` | `world.entity.observed.v1` | WP-06; provisional identity, evidence, owner isolation |
| Relationship | World-model subsystem | `world_relationships` | `world.relationship.revise`, `world.relationship.search` | `world.relationship.revised.v1` | WP-06; temporal validity, contradiction and revision |
| Situation | Context/world-understanding subsystem | `situation_snapshots` plus versioned `contexts` | `situation.snapshot.create`, `situation.inspect`, `context.assemble/get/invalidate` | `situation.snapshot.created.v1`, `context.assembled.v1`, `context.invalidated.v1` | WP-06/WP-07; partial observation, unknowns, stale context |
| Observation / evidence | Experience/evidence subsystem | `experiences`, `evidence_items`, `evidence_details`, artifact references | `experience.submit`, `environment.observe`; scoped evidence retrieval through domain queries | `experience.observed.v1`, `evidence.recorded.v1`, `environment.observed.v1` | WP-07/WP-08; provenance, authenticity, retention and untrusted-content tests |
| Belief / world model | Knowledge-belief subsystem | `knowledge_items`, `beliefs`, `belief_revisions`, evidence links | `belief.propose`, `belief.revise`, `belief.inspect`, `knowledge.search` | `belief.proposed.v1`, `belief.revised.v1` | WP-08; contradictory evidence and append-only revision |
| Possible means / affordance | Means-reasoning subsystem | `affordance_hypotheses` | `means.affordance.propose`, `means.affordance.search` | `means.affordance.proposed.v1` | WP-06/WP-09; non-device/human-mediated and context-dependent means |
| Capability descriptor / knowledge | Discovery and capability-knowledge subsystems | capability descriptors and `capability_knowledge_revisions` | `capability.discover/verify/invalidate`, `capability.knowledge.propose/revise`, corresponding inspect/search queries | discovery/verification/invalidation and knowledge proposed/revised events | WP-05/WP-09; discovery is not permission, stale descriptors invalidate dependent plans |
| Interaction proposal | Interaction-control subsystem | `interaction_proposals` | `interaction.propose`, `interaction.inspect` | `interaction.proposed.v1` | WP-04/WP-11; proposal is not authorization or dispatch |
| Operation / external effect | Action gateway and scheduler | `operations`, `operation_steps`, `recovery_journal`, receipts in `aurion_events.db` | `operation.propose/cancel/reconcile`, `operation.status` | operation lifecycle events | WP-03/WP-11; exact authorization, uncertain dispatch, reconciliation-before-retry |
| Interaction outcome | Outcome subsystem | `interaction_outcomes` plus evidence lineage | `interaction.outcome.record`, `interaction.outcome.inspect` | `interaction.outcome.observed.v1` | WP-11/WP-12; independent observation and attribution uncertainty |
| Prediction / evaluation | Prediction subsystem | `predictions`, `prediction_evaluations` | `prediction.create/evaluate`, `prediction.inspect` | `prediction.created.v1`, `prediction.evaluated.v1` | WP-09; prediction is not observation or outcome |
| Appraisal / attention | Appraisal and attention subsystems | `appraisal_records`; live attention allocation is runtime state | `appraisal.evaluate/inspect`, `attention.allocate/inspect` | `appraisal.updated.v1`, `attention.allocated.v1` | WP-03/WP-09; context-sensitive appraisal, resource-aware attention, restart reconstruction |
| Reasoning / decision | Reasoning and decision subsystems | `reasoning_assessments`, `decision_records` | `reasoning.assess/inspect`, `decision.record/inspect` | `reasoning.hypothesis.proposed.v1`, `decision.recorded.v1` | WP-09/WP-10; hypotheses and decisions do not grant authority |
| Derived goal / plan / task | Goal, planning and scheduler subsystems | `goals`, `goal_revisions`, `plans`, `plan_steps`, `task_runs`, `task_checkpoints` | goal/plan commands and queries; `task.start/pause/resume/cancel`, `task.status` | goal/plan/task events | WP-03/WP-10; objective is distinct from derived goal and plan; safe-point control |
| Outcome evaluation | Outcome subsystem | `outcome_evaluations`, `prediction_evaluations`, source evidence | `outcome.evaluate` and outcome evidence retrieval | `outcome.evaluated.v1`, `outcome.observed.v1` | WP-12; receipt, observed effect and causal attribution remain separate |
| Learning / experiment | Learning/evaluation subsystem and isolated worker supervisor | `learning_updates`, experiment manifests and immutable artifacts | `learning.update.propose`, `learning.experiment.submit`, `learning.candidate.evaluate` | learning and worker lifecycle events | WP-12/WP-14; experience-dependent change measured against frozen baselines and unseen controls |
| Self-model / evolution | Self-model and evolution subsystems with governance | `self_model_revisions`, `evolution_proposals`, candidate artifacts and activation audit | self-model/evolution proposal, evaluation, activation and rollback commands | proposed/updated self-model and evolution lifecycle events | WP-13; evidence-backed claims, candidate quarantine, owner-governed activation/rollback |

## 3. Cross-domain invariants reconciled

1. **Objective ≠ goal ≠ plan.** Owner intent and success criteria live in `objective_records`; derived goals reference an objective revision; plans bind exact objective/goal, situation, evidence, means and policy revisions. A goal command cannot create or rewrite owner intent.
2. **Entity ≠ resource ≠ capability.** World entities and actors can be people, objects, organizations, places, processes or systems. A resource reference and affordance hypothesis do not establish an executable provider interface.
3. **Observation ≠ evidence ≠ belief ≠ prediction.** Evidence retains source, scope, time and limitations. Beliefs are revisable claims. Predictions are prospective records. Outcome evaluation requires independently observed evidence.
4. **Affordance ≠ capability descriptor ≠ permission.** Affordances are context-dependent hypotheses; capability descriptors are versioned provider/interface evidence; permissions and governance approvals are independent authority decisions.
5. **Interaction proposal ≠ operation ≠ authorization.** A proposal records exact actors, targets, means and expected effects. A separate operation lifecycle and current governance decision are required before provider dispatch.
6. **Provider receipt ≠ observed outcome ≠ causal attribution.** Unknown or contradictory effects remain uncertain and are reconciled before retry. An outcome record must cite independent observation evidence.
7. **Learning proposal ≠ active behaviour change.** Updates, experiments and candidate evaluations are quarantined; activation is a separate governed transition. Persistent memory writes alone are not learning evidence.
8. **Runtime state ≠ historical event.** Attention allocation and other transient state are reconstructed from current conditions after restart; historical allocation events are not treated as current allocation.
9. **Local transaction ≠ distributed transaction.** Aggregate mutation and event/outbox commit atomically in each owning store. Cross-store work uses stable IDs, idempotent consumers and reconciliation; no cross-database ACID guarantee is assumed.
10. **Model output ≠ authority.** Model-generated identities, objectives, risk estimates, proposed effects, approvals and key references cannot self-authorize or widen authenticated scope.

## 4. Command/event reconciliation corrections

The following semantic mismatches identified during builder analysis have been resolved in schemas, fixtures, registry bindings and the command matrix:
- `memory.retrieve` is the auditable retrieval command and emits `memory.retrieved.v1`; `memory.search` remains read-only.
- `goal.cancel` appends a terminal `cancelled` goal revision and emits `goal.revised.v1` with that state.
- `approval.revoke` emits dedicated `approval.revoked.v1`.
- `capability.knowledge.propose` emits `capability.knowledge.proposed.v1`, distinct from revised/accepted knowledge.
- `learning.candidate.evaluate` emits `learning.candidate.evaluated.v1` with baseline, held-out dataset, metrics, regression and unseen-control lineage.
- `self_model.update.propose` emits `self_model.update.proposed.v1` with explicit proposed status.
- Objective revision has a dedicated `objective.revised.v1` event and a successor-revision fixture.

The event registry now contains 89 entries. All new events remain design-only/non-dispatchable until owning handlers and consumers are implemented and tested.

## 5. Explicitly unresolved scope and authority

These are not builder choices:
- First permitted Android action/capability remains owner-reserved.
- Cloud/offline-mobile cognitive-history continuity remains an owner decision; the architecture does not assume shared live state or separate histories.
- Target Android device selection and empirical Termux/SQLite/permission/lifecycle/resource evidence remain outstanding.
- Cloud key provider, recovery custodian and production recovery policy remain unselected.
- The first-release command/query subset remains a builder proposal pending owner acceptance.
- `device.pair` and `device.revoke` remain deferred to the later multi-device phase.

## 6. Evidence and remaining BR-008 work

Machine-enforced CI currently checks:
- 54 unique command types, 29 unique query types and 89 event types.
- All 52 mapped command entries have semantic fields, known error/event bindings and unique CC-001…CC-052 acceptance IDs; the two device commands are deferred.
- All 29 queries have owner scope, classification/redaction, consistency, ordering/cursor, limits/freshness and unique QCC-001…QCC-029 assertions; all remain read-only.
- Every event payload-schema and fixture reference resolves and each referenced fixture validates against its declared payload schema.
- Command and query request/response/result fixture references are validated against their declared schemas. The event producer/consumer matrix is checked bidirectionally against command producer bindings, payload schema definition names, intended consumer/owner-transition summaries and scenario coverage references.
- Governance integrity, host SQLite base/migration smoke checks and Android probe shell syntax.

The 89 event entries now carry producer-origin/trigger, owning-component, consumer-contract, owner-transition, ordering/idempotency, failure/recovery and scenario-reference specifications. This is a proposed contract, not evidence that runtime consumers exist. 51 events have command producer bindings; 38 have no command producer. Fifteen Action Gateway lifecycle events have exact internal state-transition triggers; the other 23 non-command events have exact trusted-ingress/internal producer triggers. All 38 events without command producers remain non-command origins; no public command was invented. The following remain unverified and keep BR-008 OPEN:
- Independent semantic review of all 89 proposed event consumer/owner-transition contracts, independent review and owner acceptance of the 38 non-command producer-trigger specifications, and cross-store saga/transaction ownership.
- Production handler implementation and executable command/query/event tests, including authorization, redaction, concurrency, idempotency, crash/restart, replay and no-blind-retry assertions.
- Execute all 39 INT/CM/AD scenario specifications with deterministic fakes, durable-state assertions, unseen controls and pre-registered learning acceptance metrics. The fixture corpus is specified and CI-validated, not executed.
- The learning-update acceptance event exists, but the canonical public acceptance/activation command and its relationship to the separate evolution activation path remain unresolved.
- Target SQLite/Termux behaviour, migration interruption/restore, device permissions/lifecycle/resources, C++ validator equivalence and C++/Python conformance.
- Independent review of the final planning revision and owner planning-exit acceptance.

**Disposition:** This report closes a builder-owned semantic traceability and registry-binding increment. It does not close BR-008 overall, establish implemented cognition or authorize runtime work. PR #2 remains draft/unmerged; no independent-review or tester handoff is implied.


## BR-004 builder increment — integrated scenario contract fixtures (2026-11-12)

Added `schemas/scenario-contracts.v1.schema.json` and `schemas/fixtures/scenario-contracts.fixture.json` with three integrated scenario specifications:
- INT-001: provenance, contradictory evidence, immutable prediction, independently observed outcome and quarantined learning-candidate evaluation.
- INT-002: owner objective, uncertain world state, unknown and changing means, human-mediated options, generic discovery and stale-plan invalidation.
- INT-003: exact-operation approval, independent OS permission, provider effect with lost receipt, crash/restart, reconciliation, revocation and no-blind-retry.

The fixture contains 28 ordered steps, nine negative controls, and explicit restart/replay, concurrency, fault, held-out and acceptance-threshold requirements. The validator now enforces scenario schema conformance, unique scenario/step/control IDs, known source scenario IDs, command/query/event references, and the non-executable/no-authority status.

Exact scenario-fixture code revision `a27260dfcd3ec7a7a77ca725b437f2565bd762ae` passed GitHub Actions run [43320550842](https://github.com/methaneex-oss/AURIONS/actions/runs/43320550842), including schema/fixture validation, governance integrity, host SQLite migration smoke tests and Android probe shell syntax.

**Evidence boundary:** This closes the initial machine-readable integrated scenario-specification subtask only. It does not provide a runtime scenario runner, production handlers, executed durable-state assertions or learning evidence. Full individual CM-001…CM-021 and AD-001…AD-015 instantiation remains outstanding; INT-001 explicitly records that the current registry lacks a canonical learning-update acceptance/activation transition. BR-004 remains OPEN.


## BR-004 builder increment — complete canonical scenario fixture inventory (2026-11-12)

Expanded the integrated scenario contract corpus from three INT scenarios to all 39 canonical probes: INT-001…INT-003, CM-001…CM-021 and AD-001…AD-015. The corpus now contains 172 ordered steps and 45 negative controls, with restart/replay, concurrency, fault, held-out and acceptance-threshold requirements on every scenario. The schema and validator require the exact 39-ID inventory, unique scenario/step/control IDs, known source scenario IDs and non-executable/no-authority status.

Exact revision `4e509a194f206c52d41fda1f6d3b3599bc5c0375` passed GitHub Actions run [43320967492](https://github.com/methaneex-oss/AURIONS/actions/runs/43320967492). All workflow steps passed: Draft 2020-12 schemas/fixtures (including all 39 scenario contracts and their registry references), governance integrity, host SQLite base/migration smoke tests and Android probe shell syntax.

**Evidence boundary:** This completes the builder's machine-readable scenario-specification coverage subtask. It does not create an AURIONS runtime scenario runner, production handlers or executed durable-state/learning tests. Runtime implementation remains unauthorized. INT-001 retains the explicit learning-update acceptance/activation gap; no command was invented. BR-004 remains OPEN overall until executable scenarios and behavioural evidence exist.


## BR-008 builder increment — exact event producer matrix parity (2026-11-12)

The schema validator now compares producer origin, exact trigger contract and owner-transition contract field-for-field between the event registry and both trigger matrices. Coverage is exact: 15 Action Gateway internal events plus 23 other non-command events. All 89 event entries now retain only the unresolved runtime-handler and event-specific-acceptance-execution gates.

Exact HEAD 2f4218c669ced79920af16ff122e5ab7080124b4 passed CI run [43323863934](https://github.com/methaneex-oss/AURIONS/actions/runs/43323863934). This closes specification parity only; owner acceptance, runtime handlers and executed event behaviour remain open.
