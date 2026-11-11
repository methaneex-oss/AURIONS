# AURIONS — Cognitive and Capability Contract Matrix

- **Status:** Builder-authored contract reconciliation; IN PROGRESS.
- **Purpose:** Connect the cognitive and Android capability architectures to authoritative state ownership, persistence, APIs, events, work packages and verification.
- **Authority:** The owner decision register in `INITIAL-ENGINEERING-SPECIFICATION.md` remains authoritative. This matrix clarifies engineering ownership; it does not create owner decisions.
- **Governing invariant:** Engineer mechanisms; acquire behaviour and capability knowledge through evidence and experience. Do not replace discovery, reasoning, learning or adaptation with developer-authored task-to-action mappings.

## 1. Contract rules

1. Each durable state domain has one authoritative owner. Other mechanisms submit commands or consume queries/events; they do not write another domain's tables.
2. A persisted record, command or event is evidence of a state transition only to the extent its contract says so. A proposal is not an accepted update; provider success is not verified effect; discovery is not permission.
3. Cross-domain interactions use versioned contracts and stable identifiers. Cross-store references are validated by application services; there are no cross-file foreign keys or assumed distributed transactions.
4. Every acquired claim includes provenance, context/scope, uncertainty and lifecycle. Conflicting evidence is retained.
5. The mapping below is an ownership and traceability baseline. It does not imply that the SQL has been executed, C++ modules implemented, or tests passed.

## 2. Cognitive mechanism ownership matrix

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
| Decision | Decision subsystem; `decision_records` | `decision.record`; `decision.recorded.v1` | WP-10 | CM-008, owner-defer/clarification tests |
| Action / execution | Action gateway owns operation transitions; `operations`, `operation_steps`, `recovery_journal`, receipts/events in `aurion_events.db` | `operation.propose/cancel/reconcile`; operation lifecycle events | WP-11 / WP-03 / WP-04 | OP-001…OP-008, CM-009/010 |
| Outcome evaluation | Outcome subsystem; `outcome_evaluations`, `prediction_evaluations`, source evidence and operation receipt references | `outcome.evaluate`; `outcome.evaluated.v1`, `outcome.observed.v1` | WP-12 | CM-009…CM-014, LE-* |
| Learning | Learning/evaluation subsystem; `learning_updates`, experiment manifests and immutable artifacts | learning update/experiment/candidate commands and events | WP-12 / WP-14 | LE-001…LE-008, CM-011…CM-015 |
| Self-model | Self-model subsystem; `self_model_revisions` | self-model update proposal/query; `self_model.updated.v1` | WP-13 | CM-016 |
| Evolution | Evolution subsystem; `evolution_proposals`, candidate artifacts, governance approval and activation audit | evolution proposal/evaluate/approve/activate/rollback | WP-13 | CM-017, protected-change tests |

## 3. Android environment and capability ownership matrix

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

The common envelope in the implementation-ready contract remains mandatory. The following body fields are minimum semantic requirements. Canonical JSON Schema definitions now exist for the payloads listed here; they remain planning artifacts until full Draft 2020-12 validation, generated C++/Python type conformance and CI enforcement are established.

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
| CCM-04 | MEDIUM | The command/event catalogue did not provide machine-readable body schemas and shared fixtures for every domain. | **PARTIALLY SPECIFIED:** the common envelope, extensible capability descriptor and 52 domain/protocol/operational payload definitions now have generic positive fixtures; an explicit event-family-to-payload binding table covers the current 74 event types (with the operation lifecycle family bound to `operationLifecycleEvent`). 13 negative fixtures are included. A custom structural subset check passed all 52 positive payload fixtures plus the separate descriptor, envelope and decision fixtures, and rejected all 13 negative fixtures. This is not full JSON Schema Draft 2020-12 validation. Remaining: semantic review of each event binding; family-specific command request and query input/result schemas (the generic envelopes are wrappers only); final error-code/compatibility semantics; full validator/generator selection; C++/Python conformance and CI enforcement. |
| CCM-05 | MEDIUM | `learning_updates` alone did not express the evidence and candidate manifest needed for a learning claim. | **SPECIFIED:** proposed memory migration v3 adds `learning_update_details` with update kind, hypothesis, scope, evidence, baseline/candidate/protocol/metrics/regression artifact references, rollback and approval references. Machine-readable artifact-manifest and experiment-completion payloads/fixtures now exist; persistence lineage, migration execution and evaluation fixtures remain open. |
| CCM-06 | MEDIUM | The cognitive architecture defines plan interruption, stale context, revalidation and checkpoint semantics, but the original checkpoint record did not bind to exact plan/context/capability/dependency versions. | **SPECIFIED:** proposed event/recovery migration v2 adds `task_checkpoint_details` with plan/version, context reference, capability epoch digest, dependency-state digest, pending steps, resume conditions and invalidation reason. Executable stale-checkpoint/replan tests remain open. |
| CCM-07 | MEDIUM | Attention is intentionally runtime state, but its event durability and restart reconstruction policy were underspecified. | **SPECIFIED:** cognitive architecture §6.1 now defines when allocations are persisted, why old allocations are historical only, and how current attention is recomputed after restart. CM-021 and DB-017 cover the required behaviour; executable fixtures remain open. |
| CCM-08 | HIGH | `event_consumers.last_sequence` had no corresponding durable sequence column in `events`, so the consumer checkpoint could not be tied to a defined append order. | **SPECIFIED:** proposed event-store DDL now assigns a store-local `event_sequence INTEGER PRIMARY KEY AUTOINCREMENT` on durable append and makes `event_id` unique. Event/receipt/consumer checkpoint ordering is defined in the implementation contract; EV-001…EV-004 cover monotonic append, duplicate identity, atomic checkpointing and no global-order assumption. SQL execution and crash/fault validation remain open. |

## 7. Completion rule

This matrix is IN PROGRESS until:
1. Every row in Sections 2 and 3 maps to an authoritative implementation owner, schema, command/query/event and canonical test.
2. CCM-01, CCM-02, CCM-03, CCM-05, CCM-06, CCM-07 and CCM-08 have proposed design-level corrections in Section 26.5.2 of the source specification or the cognitive architecture. CCM-04 has an expanded schema/fixture and event-binding proposal, but semantic coverage and toolchain validation remain open. All eight require executable verification.
3. Domain payload schemas and shared fixtures are machine-readable and validated by the C++/Python contract toolchain. The envelope, capability descriptor, expanded domain/operational payload schemas and generic command/query wrappers exist under `schemas/`, but do not close CCM-04 until family-specific command/query payload coverage, full event/body semantic review and toolchain validation are complete.
4. Every schema change has a proposed migration and a tested migration path before implementation use.
5. The matrix is consistent with the owner decision register, no-hardcoding invariant, product definition and canonical roadmap.
6. The no-hardcoding regression family NHC-001…NHC-008 is mapped to implementation fixtures and code-review evidence.
7. The exact revised baseline receives independent re-review and owner planning-exit approval.

**Current disposition:** IN PROGRESS. This matrix makes cross-domain omissions explicit; it does not claim they are fixed, executed or validated.
