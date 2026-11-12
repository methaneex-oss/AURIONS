# AURIONS — Cognitive, World and Interaction Contract Matrix

- **Status:** Builder-authored contract reconciliation; IN PROGRESS.
- **Purpose:** Connect the foundational open-world interaction architecture and cognitive mechanisms to authoritative state ownership, persistence, APIs, events, work packages and verification.
- **Authority:** The owner decision register in `INITIAL-ENGINEERING-SPECIFICATION.md` remains authoritative. This matrix clarifies engineering ownership; it does not create owner decisions.
- **Governing invariant:** The [Open-World Interaction and Means Architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md) is foundational. Engineer mechanisms; acquire behaviour, world knowledge and possible-means knowledge through evidence and experience. Do not replace objective-led reasoning with developer-authored task-to-action mappings or a closed platform/tool catalogue.

## 1. Contract rules

1. Each durable state domain has one authoritative owner. Other mechanisms submit commands or consume queries/events; they do not write another domain's tables.
2. A persisted record, command or event is evidence of a state transition only to the extent its contract says so. A proposal is not an accepted update; provider success is not verified effect; discovery is not permission.
3. Cross-domain interactions use versioned contracts and stable identifiers. Cross-store references are validated by application services; there are no cross-file foreign keys or assumed distributed transactions.
4. Every acquired claim includes provenance, context/scope, uncertainty and lifecycle. Conflicting evidence is retained.
5. The mapping below is an ownership and traceability baseline. It does not imply that the SQL has been executed, C++ modules implemented, or tests passed.

## 2. Cognitive mechanism ownership matrix

### 2.1 Foundational world and interaction ownership

| Domain | Authoritative owner / persistence | Contract family | Work package | Verification required |
|---|---|---|---|---|
| Objective interpretation | Objective subsystem; versioned `objective_records` distinct from derived `goals` | `objective.create`, `objective.revise`, `objective.inspect`; `objective.created.v1`, `objective.revised.v1` | WP-06 / WP-10 | Owner intent, objective/plan distinction, ambiguity, revision and success-evidence tests |
| Entities and actors | World-model subsystem; `world_entities` | `world.entity.observe`, `world.entity.search`, `world.entity.inspect`; `world.entity.observed.v1` | WP-06 | Novel entity, provisional identity, owner isolation and provenance tests |
| Relationships | World-model subsystem; `world_relationships` | `world.relationship.revise`, `world.relationship.search`; `world.relationship.revised.v1` | WP-06 | Contextual relation, contradiction, temporal validity and revision tests |
| Situation snapshots | Context/world-understanding subsystem; `situation_snapshots` plus existing versioned `contexts` | `situation.snapshot.create`, `situation.inspect`; `situation.snapshot.created.v1` | WP-06 / WP-07 | Partial observation, unknowns, conflicts, stale context and exogenous change tests |
| Evidence | Experience/evidence subsystem; existing `evidence_items`, proposed v4 `evidence_details` owner/scope extension and artifact lineage | `evidence.recorded.v1`; evidence query and provenance contract | WP-07 / WP-08 | Source-kind, authenticity, scope, retention and untrusted-content tests |
| Possible means / affordance hypotheses | Means-reasoning subsystem; `affordance_hypotheses` | `means.affordance.propose`, `means.affordance.search`; `means.affordance.proposed.v1` | WP-06 / WP-09 | Non-device, human-mediated, newly encountered, unsupported and context-change tests |
| Interaction proposals | Interaction-control subsystem; `interaction_proposals`; exact dispatched operation remains owned by events/recovery domain | `interaction.propose`, `interaction.inspect`; `interaction.proposed.v1`; authority and operation-link contract | WP-04 / WP-11 | Proposal is not authorization; exact-effect, cancellation, cross-store linkage and no-route tests |
| Interaction outcomes | Outcome subsystem; `interaction_outcomes` plus existing outcome/evidence lineage | `interaction.outcome.record`, `interaction.outcome.inspect`; `interaction.outcome.observed.v1`; attribution/reconciliation contract | WP-11 / WP-12 | Independent observation, uncertain effects, causal attribution and side-effect tests |

These contracts are a context-independent model. The Android-specific matrix below is a realization only. A domain may be represented without a device ID or platform capability descriptor.



| Mechanism / domain | Authoritative owner and durable state | Primary contract families | Work package | Verification |
|---|---|---|---|---|
| Experience / observation | Experience subsystem; `experiences`, linked `evidence_items`; large payloads via artifact references | `experience.submit`; `experience.observed.v1` | WP-07 | CM-001, CG-001, CM-020 |
| Representation | Representation subsystem; `representations` | representation creation/revision events; query by experience and representation type | WP-07 | CM-001, CG-002 |
| Context | Context subsystem; versioned `contexts` | context assemble/get/invalidate; `context.assembled.v1` | WP-07 | CM-002, CM-006 |
| Episodic / semantic memory | Memory subsystem; `memory_records`, `memory_links`; content/artifacts referenced, not trusted by filename | `memory.retrieve`, `memory.search`; `memory.recorded.v1`, `memory.retrieved.v1` | WP-08 | CG-003, CM-010, deletion tests |
| Knowledge / beliefs / evidence | Knowledge-belief subsystem; `knowledge_items`, `beliefs`, `belief_revisions`, `evidence_items`, `belief_revision_evidence` | belief propose/revise/inspect; `belief.proposed.v1`, `belief.revised.v1` | WP-08 | CM-003, CG-004 |
| Prediction | Prediction subsystem; `predictions`, `prediction_evaluations` | prediction create/inspect/evaluate; `prediction.created.v1`, `prediction.evaluated.v1` | WP-09 | CM-004, CG-005, CG-006 |
| Appraisal | Appraisal subsystem; `appraisal_records` | appraisal update/query; `appraisal.updated.v1` | WP-09 | CM-005, CG-007 |
| Attention | Attention subsystem; live allocation is runtime state; durable transitions may be recorded as typed events | attention allocate/query; `attention.allocated.v1` | WP-09 / WP-03 runtime | CM-005, CM-006, starvation/resource tests |
| Reasoning | Reasoning subsystem; `reasoning_assessments` and linked evidence/artifacts | reasoning assessment/proposal; `reasoning.hypothesis.proposed.v1` | WP-09 | CM-014, CM-019 |
| Goals | Goal subsystem; `goals`, `goal_revisions` | `goal.create`, `goal.cancel`, goal revision events | WP-10 | goal lifecycle, CM-006 |
| Planning | Planning subsystem; `plans`, `plan_steps`, `plan_step_dependencies`; durable run/checkpoint in events DB | `plan.propose`, `plan.checkpoint`; `plan.proposed.v1`, `plan.checkpointed.v1` | WP-10 / WP-03 | CM-006, CM-007, OP-008 |
| Task scheduling | Scheduler; `task_runs` with optimistic `revision`, `task_checkpoints` and task control/transition events in `aurion_events.db` | `task.start/pause/resume/cancel`; `task.control.requested.v1`, `task.run.transitioned.v1`, `task.status` | WP-03 | TS-001…TS-007, OP-008, CM-006/018/021 |
| Decision | Decision subsystem; `decision_records` | `decision.record`; `decision.recorded.v1` | WP-10 | CM-008, owner-defer/clarification tests |
| Action / execution | Action gateway owns operation transitions; `operations`, `operation_steps`, `recovery_journal`, receipts/events in `aurion_events.db` | `operation.propose/cancel/reconcile`; operation lifecycle events | WP-11 / WP-03 / WP-04 | OP-001…OP-008, CM-009/010 |
| Outcome evaluation | Outcome subsystem; `outcome_evaluations`, `prediction_evaluations`, source evidence and operation receipt references | `outcome.evaluate`; `outcome.evaluated.v1`, `outcome.observed.v1` | WP-12 | CM-009…CM-014, LE-* |
| Learning | Learning/evaluation subsystem; `learning_updates`, experiment manifests and immutable artifacts | learning update/experiment/candidate commands and events | WP-12 / WP-14 | LE-001…LE-008, CM-011…CM-015 |
| Self-model | Self-model subsystem; `self_model_revisions` | self-model update proposal/query; `self_model.updated.v1` | WP-13 | CM-016 |
| Evolution | Evolution subsystem; `evolution_proposals`, candidate artifacts, governance approval and activation audit | evolution proposal/evaluate/approve/activate/rollback | WP-13 | CM-017, protected-change tests |


> **Scope correction:** The following matrix is only the Android-specific realization. It does not define the complete ownership model for world understanding, entity/actor relationships, task semantics, non-device means, human-mediated interaction or other contexts. Initial context-independent contracts and proposed persistence mappings are now documented in §2.1 and `schemas/world-interaction.v1.schema.json`; their command/query/event implementation bindings, semantic integrity and executable tests remain open. An Android capability descriptor is not the universal representation of an affordance or possible means.

## 3. Android-specific interaction realization ownership matrix

| Mechanism | Owner | Durable state / authority | Contract family | Verification |
|---|---|---|---|---|
| Environment observation | Environment observer / platform adapter | Observation and experience records in memory domain; OS remains source of platform truth | `environment.observe`; `environment.observed.v1` | AD-001, AD-004, AD-011 |
| Discovery orchestration | Discovery broker | Discovery provenance and evidence; no permission is created | `capability.discover`; `capability.discovered.v1` | AD-002, AD-003, AD-015 |
| Capability description | Capability registry | `capability_descriptors` with version, provider/device scope, provenance, freshness and status | descriptor publish/update/invalidate/revoke | AD-004, AD-015, CAP-001 |
| Capability-use knowledge | Capability knowledge subsystem | `capability_knowledge_revisions`, `capability_knowledge_evidence`, `capability_relationships` | knowledge query/revision events | AD-008, AD-009, CAP-003 |
| Feasibility and planning | Cognitive planning subsystem | Versioned plans reference capability descriptor identity and version | feasibility query; plan proposal | AD-002, AD-009, CM-007 |
| AURIONS authorization | Governance subsystem | `permissions`, `policies`, approvals and revocations in governance DB | permission evaluation and approval protocol | AD-006, AD-010, AU-* |
| Android permission state | Android platform adapter | OS permission/grant state is authoritative; observed state is cached only as evidence | permission observation/revalidation | AD-005, AD-006 |
| Local execution | Action gateway + Android adapter | Operation state/receipt in events DB; exact policy decision in governance audit | operation dispatch/receipt/reconcile | AD-007, AD-011, AD-014, OP-* |
| Postcondition verification | Outcome evaluator + platform observer | Independent observation and outcome evaluation | outcome evaluate/verify | AD-007, CM-009 |
| Capability adaptation | Learning subsystem | Evidence-linked capability knowledge and evaluated strategy updates | learning proposal/evaluation/acceptance | AD-008, AD-009, CAP-003/004, LE-* |
| Lifecycle / rediscovery | Discovery broker + scheduler | Discovery epochs, descriptor status, revocation and operation events | invalidation/revocation/rediscovery events | AD-004, AD-005, AD-014 |

## 4. Minimum domain payload contracts

The common envelope in the implementation-ready contract remains mandatory. The following body fields are minimum semantic requirements. Canonical JSON Schema definitions now exist for the payloads listed here. The current corpus has passed Python-host Draft 2020-12 schema/fixture validation and is enforced in CI (8 schema meta-schema checks, 7 registry/fixture pairs, 78 positive domain payloads and 29 negative controls; workflow run [43288993781](https://github.com/methaneex-oss/AURIONS/actions/runs/43288993781) on PR head `0332792bc3f3c1793885d6fb5f8a0def9d392305`). These results establish schema/fixture conformance only; C++ validator equivalence, C++/Python serialization conformance, handler semantics, runtime dispatch and executable cognitive scenarios remain open. The schemas remain planning contracts, not production dispatch authorization.

### 4.1 Experience observation

Required: `experience_id`, `source_type`, `observed_at`, `recorded_at`, `content_ref`, `sensitivity`, `provenance`, `capture_method`, `capture_limitations`, `retention_class`.

Rules: source assertion, direct observation, provider receipt and model interpretation remain distinguishable. Raw source is immutable; corrections create new records or links. Sensitive payloads are referenced through governed artifacts, not copied into generic event logs.

### 4.2 Representation

Created payload required: `representation_id`, `experience_id`, `representation_type`, `method_id`, `method_version`, `content`, `uncertainty`, `source_refs[]`, `created_at`. Revised payload additionally requires `revision_number` and `supersedes_revision_id`.

Rules: one experience may yield multiple representations; a representation never overwrites the observation. Revisions are immutable and preserve supersession lineage. Model/algorithm provenance is retained.

### 4.3 Context snapshot

Required: `context_id`, `version`, `scope`, `valid_from`, optional `valid_until`, `attributes`, `provenance_refs`, `uncertainty`, `created_at`.

Rules: snapshots are immutable by version. New evidence produces a new version or invalidation event; consumers revalidate stale context.

### 4.4 Belief revision

Required: `belief_id`, `knowledge_id`, `revision_id`, `revision_number`, `epistemic_status`, optional `confidence`, `revision_reason`, `evidence_refs[]` with `stance` and `relevance`, `created_at`.

Rules: prior revisions remain queryable; contradictory evidence is not discarded; confidence semantics and calibration method are declared by the owning subsystem.

### 4.5 Prediction

Created payload required: `prediction_id`, `subject_ref`, `expected_outcome`, `evaluation_criteria`, `conditions`, `horizon`, `evidence_refs[]`, `created_at`; `confidence` is optional. Evaluation is a separate `predictionEvaluation` payload with `evaluation_id`, `prediction_id`, `observed_outcome_ref`, `result`, `evaluated_at` and `evidence_refs[]`.

Rules: the prospective prediction and criteria are immutable after creation. Evaluation appends observed outcome and evaluator evidence; it never edits the original expectation or smuggles mutable lifecycle status into the prediction record.

### 4.6 Capability descriptor

Required: `capability_id`, `descriptor_version`, `provider_id`, `device_scope`, `discovery_epoch`, `descriptor_schema_version`, `descriptor_sha256`, `source_ref`, `first_discovered_at`, `status`, and a versioned descriptor body. The body supports `interface` (including input/output schema references), `preconditions[]`, `effects[]`, `platform_requirements[]`, `constraints`, `risk_facts`, `execution` (timeout/cancellation/idempotency/retry/uncertain-outcome semantics), `verification`, `resource_profile`, `lifecycle` and `provenance`.

Rules: descriptor is data describing an observed interface, not code, permission or authorization. Invocation implementation remains in a trusted adapter. Descriptor contents are schema-validated, hashed and provenance-linked. Unknown fields cannot increase authority. Field-level semantics are specified in Section 4.4 of the Implementation-Ready Planning Contracts.

### 4.7 Plan step

Required: `step_id`, `plan_id`, `plan_version`, `sequence`, `step_role`, `role_schema_version`, `intent`, `input_binding`, `preconditions`, `expected_effects`, `resource_budget`, `dependencies[]`, `verification_contract`, `stop_conditions` and `status`. `capability_ref` is optional for steps that invoke a discovered capability and must bind the exact capability ID/descriptor version.

Rules: steps may represent reasoning, observation, waiting, clarification or action; not every step invokes a capability. A capability reference is never authorization. The plan must retain alternatives and uncertainty where material.

### 4.8 Operation proposal and receipt

Proposal required: `operation_id`, `owner_id`, `actor_identity`, `device_id`, `capability_id`, `descriptor_version`, `target_ref`, `canonical_parameters_artifact_id`, `parameter_digest`, `expected_effects_ref`, `sensitivity`, `data_categories`, `risk_class`, `policy_version_ref`, `deadline`, `resource_budget`, `idempotency_key`, `canonicalization_version`, `created_at`; goal/plan/step lineage and `approval_request_id` are optional references.

Attempt receipt required: `attempt_id`, `operation_id`, `attempt_number`, `state`, `idempotency_key`; dispatch/finish times, provider receipt, reported effects, verification evidence, error, uncertainty reason and reconciliation time are optional evidence fields.

Rules: the gateway revalidates descriptor version, parameters, current OS permission and AURIONS policy immediately before dispatch. A timeout after possible dispatch is uncertain, not failed. Provider receipt is not independent postcondition verification.

### 4.9 Outcome evaluation

Required: `outcome_evaluation_id`, `prediction_ref`, `plan_ref`, `operation_ref`, `expected_outcome_ref`, `observed_outcome_ref`, `verification_sources[]`, `result`, `attribution_hypotheses[]`, `uncertainty`, `created_at`.

Rules: preserve expected and observed evidence separately. Attribution remains a hypothesis unless the evaluation design supports causality.

### 4.10 Learning update

Required: `learning_update_id`, `target_mechanism`, `update_kind`, `hypothesis`, `scope`, `evidence_refs[]`, `state` and `created_at`. Optional evaluation/activation references are `baseline_artifact_ref`, `candidate_artifact_ref`, `evaluation_protocol_ref`, `metrics_ref`, `regression_results_ref`, `approval_ref` and `rollback_ref`.

Rules: distinguish episodic acquisition, belief revision, capability knowledge, strategy/mechanism learning, model training and architecture evolution. A proposal may omit candidate/evaluation references; an accepted update must satisfy the learning-evidence policy and required artifact lineage. Candidate updates remain isolated until acceptance criteria and approval are met.

## 5. State ownership and write protocol

- Experience, representation, context, memory, belief, prediction, appraisal, reasoning, goal, plan, decision, outcome, learning, self-model and capability-knowledge writes go through their owning domain command handlers.
- Operation lifecycle writes go through the action/runtime owner in the events DB. No cognitive mechanism directly edits operation state.
- Permission, approval, revocation and disclosure writes go through governance commands. No descriptor, plan or learned estimate can mutate a grant.
- Artifact bytes are written to a controlled artifact store; metadata/lineage changes go through the artifact registry. Content hashes are verified before registration.
- Events are immutable facts. A correction is a new event with causation, not mutation of history.
- Cross-store workflows use local transaction plus outbox/inbox and durable reconciliation; no distributed atomicity is assumed.

## 6. Identified contract/schema reconciliation gaps

These builder findings compare the cognitive/Android contracts against the proposed DDL. Proposed DDL corrections below are design specifications only; they are not executed or validated migrations.

| ID | Severity | Finding | Required builder resolution |
|---|---|---|---|
| CCM-01 | HIGH | The original `plan_steps` row lacked the typed execution contract required by the plan architecture. | **SPECIFIED:** proposed memory migration v3 adds `plan_step_contracts` with extensible step role/schema version, versioned capability reference, input binding, preconditions, expected effects, resource budget, verification, stop conditions and stale-input digest. DDL execution and application validation remain open. |
| CCM-02 | HIGH | The original operation-state CHECK constraint did not represent the full documented lifecycle. | **SPECIFIED:** proposed base DDL now enumerates the documented approval, dispatch, uncertainty, reconciliation, compensation and manual-intervention states. The application-enforced transition graph is now specified in Section 7.1 of the implementation contracts; OP-009/OP-010 and DB-012…DB-014 cover transition legality, terminal immutability and attempt separation. SQL CHECK constraints alone do not enforce legal transitions; execution/fault validation remains open. |
| CCM-03 | HIGH | The operation header did not persist the exact operation payload, principal/device lineage and per-attempt receipt/verification evidence required by the execution contract. | **SPECIFIED:** proposed events migration v2 adds owner/actor/device and originating-step binding in `operation_details`, plus `operation_attempts`; cross-store capability/approval validation and executable recovery tests remain open. |
| CCM-04 | MEDIUM | The command/event catalogue did not provide machine-readable body schemas and shared fixtures for every domain. | **PARTIALLY SPECIFIED:** the common envelope, extensible capability descriptor and 78 domain/protocol/operational payload definitions now have generic positive fixtures; an explicit event-family-to-payload binding table covers the current 84 event types (with the operation lifecycle family bound to `operationLifecycleEvent` and task control/transition events bound to their task schemas). The Python-host Draft 2020-12 CI validation now passes the current corpus: 8 schema meta-schema checks, 7 registry/fixture pairs, 78 positive domain payloads and 29 negative controls (run [43288993781](https://github.com/methaneex-oss/AURIONS/actions/runs/43288993781), exact PR head `0332792bc3f3c1793885d6fb5f8a0def9d392305`). This supersedes the earlier custom-subset-only evidence recorded above. Remaining: semantic review of each event and command/query binding; verify handler-specific state transitions, authorization, error mapping and redaction; complete error-registry handler mappings and compatibility semantics; C++ validator equivalence, C++/Python conformance and runtime execution. The initial registry now maps 43 of 45 declared command types to request schemas (device pairing/revocation are explicitly deferred) and all 21 query types to typed input/result schemas. Remaining: semantic review of each event and command/query binding; verify handler-specific state transitions, authorization, error mapping and redaction; complete error-registry handler mappings and compatibility semantics; full validator/generator selection; C++/Python conformance and CI enforcement. |
| CCM-05 | MEDIUM | `learning_updates` alone did not express the evidence and candidate manifest needed for a learning claim. | **SPECIFIED:** proposed memory migration v3 adds `learning_update_details` with update kind, hypothesis, scope, evidence, baseline/candidate/protocol/metrics/regression artifact references, rollback and approval references. Machine-readable artifact-manifest and experiment-completion payloads/fixtures now exist; persistence lineage, migration execution and evaluation fixtures remain open. |
| CCM-06 | MEDIUM | The cognitive architecture defines plan interruption, stale context, revalidation and checkpoint semantics, but the original checkpoint record did not bind to exact plan/context/capability/dependency versions. | **SPECIFIED:** proposed event/recovery migration v2 adds `task_checkpoint_details` with plan/version, context reference, capability epoch digest, dependency-state digest, pending steps, resume conditions and invalidation reason. Executable stale-checkpoint/replan tests remain open. |
| CCM-07 | MEDIUM | Attention is intentionally runtime state, but its event durability and restart reconstruction policy were underspecified. | **SPECIFIED:** cognitive architecture §6.1 now defines when allocations are persisted, why old allocations are historical only, and how current attention is recomputed after restart. CM-021 and DB-017 cover the required behaviour; executable fixtures remain open. |
| CCM-08 | HIGH | `event_consumers.last_sequence` had no corresponding durable sequence column in `events`, so the consumer checkpoint could not be tied to a defined append order. | **SPECIFIED:** proposed event-store DDL now assigns a store-local `event_sequence INTEGER PRIMARY KEY AUTOINCREMENT` on durable append and makes `event_id` unique. Event/receipt/consumer checkpoint ordering is defined in the implementation contract; EV-001…EV-004 cover monotonic append, duplicate identity, atomic checkpointing and no global-order assumption. SQL execution and crash/fault validation remain open. |
| CCM-09 | HIGH | `taskControlRequest.expected_version` had no corresponding persisted revision in `task_runs`; `taskRunStatus` omitted the version, and task control/state transitions had no event-body binding. | **SPECIFIED:** proposed event/recovery migration v2 adds `task_runs.revision`; `taskRunStatus` exposes it; `task.control.requested.v1` and `task.run.transitioned.v1` bind control requests and actual transitions to `taskControlRequest` and `taskRunTransition`. The scheduler state graph and TS-001…TS-007 are specified. Migration, atomicity, replay, transition and recovery tests remain open. |
| CCM-10 | HIGH | Provider failure semantics permitted a `dispatched` state to be paired with a retry posture that could blindly repeat a side effect; provider `enabled` state did not require explicit machine-readable governance and platform-permission evidence. | **SPECIFIED:** `providerFailure` now requires `reconcile_before_retry` for `dispatched` or `unknown` side-effect state and an explicit diagnostic-reference field. `providerLifecycle` requires validation/trust evidence for `validated`/`enabled` and separate governance-decision plus current platform-permission references for `enabled`; Android prose and neutral/enabled fixtures are aligned. Full schema, lifecycle, OS-permission and runtime validation remain open. |
| CCM-11 | MEDIUM | The normative error taxonomy was a prose seed only; no versioned machine-readable registry bound codes to category, default side-effect state, retry posture, recovery action and intervention policy. | **SPECIFIED:** added `error-registry.v1.schema.json` and `error-registry.v1.json` with 35 representative codes across 13 extensible categories. All entries remain `seed` with null handler mappings, so none is production-dispatchable. Added an incomplete-entry negative fixture. Code-to-handler mappings, code-specific fixture coverage and runtime recovery tests remain open. |

## 7. Completion rule

This matrix is IN PROGRESS until:
1. Every row in Sections 2 and 3 maps to an authoritative implementation owner, schema, command/query/event and canonical test.
2. CCM-01, CCM-02, CCM-03, CCM-05, CCM-06, CCM-07, CCM-08, CCM-09, CCM-10 and CCM-11 have proposed design-level corrections in Section 26.5.2 of the source specification, the implementation contracts, the Android architecture or the cognitive architecture. CCM-04 has an expanded schema/fixture and event-binding proposal, but semantic coverage and toolchain validation remain open. All eleven require executable verification.
3. Domain payload schemas and shared fixtures are machine-readable and pass the current Python-host Draft 2020-12 validator in CI. C++ validator equivalence and C++/Python serialization conformance remain open. This does not close CCM-04 until command/query handler semantics, full event/body semantic review, executable consumer tests and runtime bindings are complete.
4. Every schema change has a proposed migration and a tested migration path before implementation use.
5. The matrix is consistent with the owner decision register, no-hardcoding invariant, product definition and canonical roadmap.
6. The no-hardcoding regression family NHC-001…NHC-008 is mapped to implementation fixtures and code-review evidence.
7. The exact revised baseline receives independent re-review and owner planning-exit approval.

**Current disposition:** IN PROGRESS. This matrix makes cross-domain omissions explicit; it does not claim they are fixed, executed or validated.


## 8. Scenario-to-contract and test traceability

This section makes the architecture scenario IDs individually traceable to the existing contract-test catalogue and canonical payload definitions. The referenced payload fixtures prove payload shape only. They do **not** constitute an executable multi-step scenario fixture or a passing test. Every row below remains **SPECIFIED — scenario fixture and implementation execution outstanding** until a reproducible test records its inputs, state transitions, durable assertions, negative controls, build revision and result.

### 8.1 Cognitive mechanism scenarios

| Scenario | Required payload definitions | Related catalogue checks | Required scenario-level evidence |
|---|---|---|---|
| CM-001 | `experienceObserved`, `representationCreated` | CG-001, CG-002 | One immutable experience with multiple independently versioned representations; source record unchanged. |
| CM-002 | `contextSnapshot`, `contextInvalidated`, `reasoningAssessmentRequest` | CG-002, DB-016 | Context revision invalidates dependent reasoning inputs; stale input is rejected or recomputed. |
| CM-003 | `beliefRevision`, `evidenceItem` | CG-004 | Contradictory evidence creates a new revision; prior evidence and revisions remain retrievable. |
| CM-004 | `predictionCreated`, `predictionEvaluation` | CG-005, CG-006 | Prediction and criteria are committed before outcome; evaluation cannot mutate the original prediction. |
| CM-005 | `appraisalUpdated`, `attentionAllocated` | CG-007 | Allocation responds to changed evidence and resource state; no fixed stimulus mapping. |
| CM-006 | `taskRunStatus`, `taskRunTransition`, `taskCheckpointDetails`, `contextSnapshot` | CG-010, OP-008, TS-004 | Interrupt/replan at safe points; preserve committed state and reconcile dispatched work. |
| CM-007 | `planRevision`, `planStepContract`, `capabilityDescriptorRecord`, `capabilityKnowledgeRevision` | DB-011, CAP-002 | Plan binds exact descriptor version; stale/unavailable descriptor blocks dispatch and triggers revalidation. |
| CM-008 | `decisionRecorded`, `permissionEvaluated`, `approvalDecision` | AU-001…AU-012, OP-001 | Decision cannot grant authority; gateway independently enforces current authorization. |
| CM-009 | `operationLifecycleEvent`, `operationAttemptReceipt`, `outcomeObserved`, `outcomeEvaluation` | OP-003, OP-004 | Provider success without independent postcondition evidence remains unverified. |
| CM-010 | `operationLifecycleEvent`, `operationAttemptReceipt`, `contractError` | OP-003, OP-004, OP-005 | Unknown/dispatched side effect is reconciled before retry; no duplicate effect. |
| CM-011 | `learningUpdate`, `learningExperimentRequest`, `artifactManifest`, `learningExperimentCompleted` | LE-001…LE-008, DB-015 | Update links hypothesis, scope, evidence, frozen baseline, evaluation, regression and rollback artifacts. |
| CM-012 | `learningUpdate`, `artifactManifest`, `planRevision` | CG-008, CG-010, LE-005…LE-007 | Accepted update persists across restart and changes a later related task under the declared evaluation protocol. |
| CM-013 | `learningExperimentRequest`, `learningCandidateEvaluationRequest`, `artifactManifest` | CG-009, LE-002…LE-005 | Related unseen variations improve without unrelated regression; repeated seeded comparisons against frozen baseline. |
| CM-014 | `capabilityKnowledgeRevision`, `evidenceItem` | CAP-003, NHC-004 | One failure revises only evidence-supported scope; prior knowledge and contradictory evidence remain. |
| CM-015 | `capabilityKnowledgeRevision`, `permissionEvaluated`, `approvalDecision` | CAP-001, NHC-005 | Success cannot create universal competence, permission or owner authority. |
| CM-016 | `selfModelUpdated`, `operationAttemptReceipt`, `outcomeEvaluation` | LE-004, CG-008 | Confidence/calibration is compared with measured outcomes over a defined sample and scope. |
| CM-017 | `evolutionProposed`, `evolutionCandidateLifecycle`, `approvalDecision` | AU-001…AU-012, LE-007, LE-008 | Candidate cannot self-approve or mutate protected governance; activation and rollback are separately governed and audited. |
| CM-018 | `taskRunStatus`, `taskRunTransition`, `taskCheckpointDetails`, `operationLifecycleEvent` | OP-005, OP-008, TS-004, TS-007 | Cancellation/resource exhaustion preserves committed state and produces a recoverable, truthful terminal or uncertain status. |
| CM-019 | `capabilityDescriptorRecord`, `planStepContract` | CAP-004, NHC-001, NHC-007 | New compatible capability is represented and considered through generic mechanisms without a task-specific core branch. |
| CM-020 | `beliefRevision`, `representationRevised`, `evidenceItem` | CG-004 | Later evidence revises earlier interpretation without rewriting source observation or provenance. |
| CM-021 | `attentionAllocated`, `taskRunStatus`, `taskCheckpointDetails`, `contextSnapshot` | DB-017, TS-005 | Restart treats prior attention as history and reconstructs current allocation from current state and resources. |

### 8.2 Android environment and capability scenarios

| Scenario | Required payload definitions | Related catalogue checks | Required scenario-level evidence |
|---|---|---|---|
| AD-001 | `capabilityDescriptorRecord`, `permissionEvaluated`, `approvalDecision` | CAP-001, AU-001…AU-012 | Discovery is recorded while missing OS permission or AURIONS authorization independently blocks execution. |
| AD-002 | `capabilityDescriptorRecord`, `discoveryResult`, `contractError` | CT-002, CT-005 | Unknown interface/schema is reported as unknown; no fabricated invocation or side effect. |
| AD-003 | `discoveryRequest`, `discoveryResult`, `capabilityDescriptorRecord` | CAP-004, NHC-001, NHC-007 | New provider is represented through the generic discovery path without editing a task-to-action map. |
| AD-004 | `capabilityDescriptorRecord`, `providerLifecycle`, `environmentObserved` | CAP-002, CT-002 | Provider/OS/app version change invalidates stale descriptor and forces revalidation. |
| AD-005 | `permissionRecord`, `operationLifecycleEvent`, `providerLifecycle` | CAP-002, AU-001…AU-012, OP-005 | Revocation blocks queued/future work; in-flight side effects are safely cancelled or reconciled. |
| AD-006 | `operationProposal`, `approvalRequested`, `approvalDecision` | OP-006, DB-013, AU-001…AU-012 | Any change to target, parameters, effects, data scope or descriptor version invalidates exact-operation approval. |
| AD-007 | `operationAttemptReceipt`, `outcomeObserved`, `outcomeEvaluation` | OP-003, OP-004, CM-009 | Successful invocation with unverified postcondition is not reported as verified. |
| AD-008 | `capabilityKnowledgeRevision`, `evidenceItem` | CAP-003, NHC-004 | Failure updates context-specific knowledge without universal prohibition or history erasure. |
| AD-009 | `learningUpdate`, `planRevision`, `capabilityKnowledgeRevision` | CAP-004, NHC-008, LE-005 | Later related task adapts after evaluated feedback; unrelated controls remain within declared tolerance. |
| AD-010 | `permissionEvaluated`, `approvalDecision`, `auditRecord` | NHC-005, NHC-008, AU-001…AU-012 | Repeated success cannot remove policy checks, reduce risk or create approval. |
| AD-011 | `environmentObserved`, `capabilityDescriptorRecord`, `operationLifecycleEvent` | PR-17 | Network-isolated mobile workflow performs local discovery and a separately authorized operation. |
| AD-012 | `planRevision`, `operationProposal`, `approvalDecision` | PR-18, AU-001…AU-012 | Cloud-originated proposal cannot execute until the device independently revalidates and authorizes it. |
| AD-013 | `externalDisclosureRecord`, `environmentObserved` | AU-001…AU-012 | Sensitive observations remain local or are disclosed only through explicit scoped authorization and audit. |
| AD-014 | `operationAttemptReceipt`, `operationLifecycleEvent`, `contractError` | OP-003, OP-004, DB-012, DB-014 | Crash around dispatch produces reconciled or explicitly uncertain state; blind retry is impossible. |
| AD-015 | `capabilityDescriptorRecord`, `discoveryResult` | CAP-004, NHC-001, NHC-007 | New schema-compatible descriptor is accepted as data without adding a hardcoded behaviour branch. |

### 8.3 Evidence boundary

- The existing `schemas/fixtures/domain-payloads.fixture.json` provides payload-shape examples for the definitions referenced above. It does not prove the scenario sequences or durable-state assertions.
- The existing test catalogue names the scenario and related contract checks. No executable AURIONS test runner or scenario fixture suite exists in this planning branch.
- Scenario fixtures must be added with the owning implementation work package, using isolated test stores and deterministic provider fakes. They must include positive, negative, stale-version, replay, concurrency, cancellation and recovery controls as applicable.
- A scenario may be marked VALIDATED only from a recorded test run tied to the exact implementation commit, fixture corpus, toolchain and environment. This matrix is **SPECIFIED**, not validated.


## 9. Security, key and supply-chain traceability

| Test | Owning package / boundary | Required evidence | Status |
|---|---|---|---|
| SEC-001, SEC-002 | WP-04 identity/governance; WP-06 Android platform adapter | Key provenance, hardware-backing evidence, role separation and cross-domain denial | SPECIFIED — platform execution outstanding |
| SEC-003, SEC-005 | WP-02 persistence; WP-04 governance/security | Versioned envelope-encryption, crash-safe rotation, owner-controlled recovery and fail-closed key-loss traces | SPECIFIED — implementation and recovery policy evidence outstanding |
| SEC-004, SEC-006 | WP-02 persistence; WP-03 runtime; WP-04 security; WP-16 only where multi-device sync is in scope | Device revocation, backup/restore integrity, tombstone replay and no resurrection | SPECIFIED — device/backup execution outstanding |
| SEC-007 | WP-00 build/release foundation; WP-13 governed evolution | Signed update/artifact verification, key rotation and rejection of tampered/rollback artifacts | SPECIFIED — signing chain not implemented |
| SEC-008, SEC-011 | WP-04 governance/security; WP-05 provider routing; WP-15 integration | Field-level redaction, secret scans, data-egress policy and exact-operation disclosure approval | SPECIFIED — integration evidence outstanding |
| SEC-009 | WP-04 governance/security; WP-15 cloud/offline integration | KMS outage, unknown key version and revoked credential fail-closed traces; offline independence | SPECIFIED — cloud provider not selected |
| SEC-010 | WP-14 worker isolation; WP-04 security; WP-02 persistence | Worker sandbox/least privilege, no live DB/key access, quarantine and validated output | SPECIFIED — worker runtime not implemented |

These tests extend the security and key lifecycle plan in Sections 10.8 and 11.6 of the implementation-ready contracts. They are traceability and acceptance requirements only; no security control is marked implemented or validated by this matrix.
