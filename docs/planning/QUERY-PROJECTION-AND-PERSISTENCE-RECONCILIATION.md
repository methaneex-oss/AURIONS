# AURIONS — Query Projection and Persistence Reconciliation

- **Status:** Builder source-to-projection scan; unresolved fields explicitly recorded.
- **Scope:** All 29 query registry entries, their result-item schemas and currently proposed SQLite DDL.
- **Evidence:** Exact schema/DDL files at the current branch revision. This is a static column-name reconciliation, not executed SQL or semantic query verification.
- **Boundary:** A candidate column name is not proof of a correct SELECT, join, owner filter, redaction rule, or stable cursor. All queries remain design-only/non-dispatchable.

## 1. Findings

The semantic pass distinguishes a genuinely absent persisted field from a field that is derived from an existing event payload, relational join, stored timestamp, or authenticated read context. A read-only query may construct an ephemeral retrieval envelope; it must not write a retrieval receipt merely to satisfy the result schema. Every mapping below is a proposed source/transform, not executed SQL or a verified owner-scope/redaction implementation.

The query registry declares 29 result-item projections. A scan of the current DDL identified candidate source columns by exact field name, JSON-column suffix (`_json`) and timestamp suffix (`_ms`). It found fields with no direct/JSON/timestamp-named source in the query's bound tables.

This scan is deliberately conservative:
- A field listed as mapped has only a candidate storage column; the exact source table, join, JSON pointer, alias and conversion still require an explicit projection contract.
- A field listed as unmapped has no direct, `_json`, or `_ms` candidate in the query's declared tables. It must be backed by a specified join/artifact source, added to the DDL, or removed/changed in the result schema.
- No field is assumed to be derived from a different owner, an unbound table, an opaque artifact or an event payload without an explicit contract.

| Query | Result schema | Fields | Unmapped projection fields |
|---|---|---:|---|
| `environment.inspect` | `environmentObserved` | 14 | `observation_id`, `owner_id`, `device_id`, `environment_scope`, `source_id`, `collection_method`, `collector_version`, `platform_context`, `observed_facts`, `limitations`, `validity` |
| `capability.search` | `capabilityDescriptorRecord` | 13 | `descriptor_schema_version`, `descriptor_body` |
| `capability.inspect` | `capabilityDescriptorRecord` | 13 | `descriptor_schema_version`, `descriptor_body` |
| `capability.knowledge.inspect` | `capabilityKnowledgeRevision` | 10 | None by direct/JSON/timestamp name scan |
| `representation.inspect` | `representationCreated` | 9 | `method_id`, `method_version`, `source_refs` |
| `context.get` | `contextSnapshot` | 9 | `provenance_refs`, `uncertainty` |
| `memory.search` | `memoryRetrieval` | 6 | `retrieval_id`, `query_ref`, `scope`, `candidate_refs`, `access_decision_ref` |
| `knowledge.search` | `knowledgeItem` | 6 | None by direct/JSON/timestamp name scan |
| `belief.inspect` | `beliefRevision` | 9 | `evidence_refs` |
| `prediction.inspect` | `predictionCreated` | 9 | `conditions`, `horizon`, `confidence`, `evidence_refs` |
| `appraisal.inspect` | `appraisalUpdated` | 9 | None by direct/JSON/timestamp name scan |
| `attention.inspect` | `attentionAllocated` | 10 | `allocation_id`, `context_id`, `context_version`, `candidate_refs`, `selected_refs`, `deferred_refs`, `resource_budget`, `rationale_ref`, `created_at`, `valid_until` |
| `reasoning.inspect` | `reasoningHypothesisProposed` | 9 | None by direct/JSON/timestamp name scan |
| `goal.get` | `goalRevision` | 10 | None by direct/JSON/timestamp name scan |
| `plan.get` | `planRevision` | 9 | `step_refs`, `context_version_ref`, `capability_epoch_digest` |
| `decision.inspect` | `decisionRecorded` | 8 | None by direct/JSON/timestamp name scan |
| `task.status` | `taskRunStatus` | 10 | `checkpoint_refs`, `failure_ref`, `revision` |
| `operation.status` | `operationLifecycleEvent` | 11 | `occurred_at`, `policy_decision_ref`, `attempt_state` |
| `permission.inspect` | `permissionRecord` | 11 | `owner_id`, `capability_ref`, `target_scope`, `status`, `granted_by`, `approval_ref` |
| `audit.lookup` | `auditRecord` | 12 | `owner_id`, `actor_identity`, `action_type`, `approval_ref`, `evidence_refs`, `correlation_id` |
| `device.capabilities` | `capabilityDescriptorRecord` | 13 | `descriptor_schema_version`, `descriptor_body` |
| `objective.inspect` | `objective` | 11 | None by direct/JSON/timestamp name scan |
| `world.entity.search` | `entity` | 11 | None by direct/JSON/timestamp name scan |
| `world.entity.inspect` | `entity` | 11 | None by direct/JSON/timestamp name scan |
| `world.relationship.search` | `relationship` | 12 | None by direct/JSON/timestamp name scan |
| `situation.inspect` | `situation` | 12 | None by direct/JSON/timestamp name scan |
| `means.affordance.search` | `affordanceHypothesis` | 17 | None by direct/JSON/timestamp name scan |
| `interaction.inspect` | `interactionProposal` | 15 | `deadline`, `execution_binding_ref` |
| `interaction.outcome.inspect` | `interactionOutcome` | 11 | None by direct/JSON/timestamp name scan |

## 2. Field-level candidate inventory

### `environment.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/environmentObserved`
- Bound tables: `experiences`, `evidence_items`
- Unmapped by direct/JSON/timestamp column-name scan: `observation_id`, `owner_id`, `device_id`, `environment_scope`, `source_id`, `collection_method`, `collector_version`, `platform_context`, `observed_facts`, `limitations`, `validity`

- `observation_id` → **UNMAPPED in the bound DDL columns**
- `owner_id` → **UNMAPPED in the bound DDL columns**
- `device_id` → **UNMAPPED in the bound DDL columns**
- `environment_scope` → **UNMAPPED in the bound DDL columns**
- `observed_at` → experiences.observed_at_ms (timestamp conversion); evidence_items.observed_at_ms (timestamp conversion)
- `recorded_at` → experiences.recorded_at_ms (timestamp conversion); evidence_items.recorded_at_ms (timestamp conversion)
- `source_id` → **UNMAPPED in the bound DDL columns**
- `collection_method` → **UNMAPPED in the bound DDL columns**
- `collector_version` → **UNMAPPED in the bound DDL columns**
- `platform_context` → **UNMAPPED in the bound DDL columns**
- `observed_facts` → **UNMAPPED in the bound DDL columns**
- `sensitivity` → experiences.sensitivity
- `limitations` → **UNMAPPED in the bound DDL columns**
- `validity` → **UNMAPPED in the bound DDL columns**

### `capability.search`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/capabilityDescriptorRecord`
- Bound tables: `capability_descriptors`
- Unmapped by direct/JSON/timestamp column-name scan: `descriptor_schema_version`, `descriptor_body`

- `capability_id` → capability_descriptors.capability_id
- `descriptor_version` → capability_descriptors.descriptor_version
- `provider_id` → capability_descriptors.provider_id
- `device_scope` → capability_descriptors.device_scope
- `discovery_epoch` → capability_descriptors.discovery_epoch
- `descriptor_schema_version` → **UNMAPPED in the bound DDL columns**
- `descriptor_sha256` → capability_descriptors.descriptor_sha256
- `source_ref` → capability_descriptors.source_ref
- `first_discovered_at` → capability_descriptors.first_discovered_at_ms (timestamp conversion)
- `last_verified_at` → capability_descriptors.last_verified_at_ms (timestamp conversion)
- `expires_at` → capability_descriptors.expires_at_ms (timestamp conversion)
- `status` → capability_descriptors.status
- `descriptor_body` → capability_descriptors.descriptor_json (JSON decode; validate with the stored descriptor schema version)

### `capability.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/capabilityDescriptorRecord`
- Bound tables: `capability_descriptors`
- Unmapped by direct/JSON/timestamp column-name scan: `descriptor_schema_version`, `descriptor_body`

- `capability_id` → capability_descriptors.capability_id
- `descriptor_version` → capability_descriptors.descriptor_version
- `provider_id` → capability_descriptors.provider_id
- `device_scope` → capability_descriptors.device_scope
- `discovery_epoch` → capability_descriptors.discovery_epoch
- `descriptor_schema_version` → **UNMAPPED in the bound DDL columns**
- `descriptor_sha256` → capability_descriptors.descriptor_sha256
- `source_ref` → capability_descriptors.source_ref
- `first_discovered_at` → capability_descriptors.first_discovered_at_ms (timestamp conversion)
- `last_verified_at` → capability_descriptors.last_verified_at_ms (timestamp conversion)
- `expires_at` → capability_descriptors.expires_at_ms (timestamp conversion)
- `status` → capability_descriptors.status
- `descriptor_body` → capability_descriptors.descriptor_json (JSON decode; validate with the stored descriptor schema version)

### `capability.knowledge.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/capabilityKnowledgeRevision`
- Bound tables: `capability_knowledge_revisions`, `capability_knowledge_evidence`, `capability_relationships`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `knowledge_revision_id` → capability_knowledge_revisions.knowledge_revision_id; capability_knowledge_evidence.knowledge_revision_id
- `capability_id` → capability_knowledge_revisions.capability_id
- `descriptor_version` → capability_knowledge_revisions.descriptor_version
- `revision_number` → capability_knowledge_revisions.revision_number
- `context_scope` → capability_knowledge_revisions.context_scope_json (JSON decode)
- `claims` → capability_knowledge_revisions.claims_json (JSON decode)
- `confidence` → capability_knowledge_revisions.confidence_json (JSON decode)
- `status` → capability_knowledge_revisions.status
- `evidence_refs` → capability_relationships.evidence_refs_json (JSON decode)
- `created_at` → capability_knowledge_revisions.created_at_ms (timestamp conversion); capability_relationships.created_at_ms (timestamp conversion)

### `representation.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/representationCreated`
- Bound tables: `representations`
- Unmapped by direct/JSON/timestamp column-name scan: `method_id`, `method_version`, `source_refs`

- `representation_id` → representations.representation_id
- `experience_id` → representations.experience_id
- `representation_type` → representations.representation_type
- `method_id` → representations.method (legacy column projected as method_id; method-version and multi-source lineage remain unresolved)
- `method_version` → **UNMAPPED in the bound DDL columns**
- `content` → representations.content_json (JSON decode)
- `uncertainty` → representations.uncertainty_json (JSON decode)
- `source_refs` → **UNMAPPED in the bound DDL columns**
- `created_at` → representations.created_at_ms (timestamp conversion)

### `context.get`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/contextSnapshot`
- Bound tables: `contexts`
- Unmapped by direct/JSON/timestamp column-name scan: `provenance_refs`, `uncertainty`

- `context_id` → contexts.context_id
- `version` → contexts.version
- `scope` → contexts.scope
- `valid_from` → contexts.valid_from_ms (timestamp conversion)
- `valid_until` → contexts.valid_until_ms (timestamp conversion)
- `attributes` → contexts.attributes_json (JSON decode)
- `provenance_refs` → **UNMAPPED in the bound DDL columns**
- `uncertainty` → **UNMAPPED in the bound DDL columns**
- `created_at` → contexts.created_at_ms (timestamp conversion)

### `memory.search`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/memoryRetrieval`
- Bound tables: `memory_records`, `memory_links`
- Unmapped by direct/JSON/timestamp column-name scan: `retrieval_id`, `query_ref`, `scope`, `candidate_refs`, `access_decision_ref`

- `retrieval_id` → generated per query execution; ephemeral and not persisted by this read-only query
- `query_ref` → query-envelope/request reference supplied by the authenticated query execution
- `scope` → authenticated execution scope after policy evaluation; never copied from caller filters
- `candidate_refs` → **UNMAPPED in the bound DDL columns**
- `created_at` → memory_records.created_at_ms (timestamp conversion); memory_links.created_at_ms (timestamp conversion)
- `access_decision_ref` → authorization decision reference from the trusted query context when present; otherwise null, with no cross-store snapshot implied

### `knowledge.search`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/knowledgeItem`
- Bound tables: `knowledge_items`, `beliefs`, `belief_revisions`, `evidence_items`, `belief_revision_evidence`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `knowledge_id` → knowledge_items.knowledge_id; beliefs.knowledge_id
- `proposition` → knowledge_items.proposition
- `domain` → knowledge_items.domain
- `status` → knowledge_items.status
- `created_at` → knowledge_items.created_at_ms (timestamp conversion); beliefs.created_at_ms (timestamp conversion); belief_revisions.created_at_ms (timestamp conversion)
- `updated_at` → knowledge_items.updated_at_ms (timestamp conversion); beliefs.updated_at_ms (timestamp conversion)

### `belief.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/beliefRevision`
- Bound tables: `beliefs`, `belief_revisions`, `evidence_items`, `belief_revision_evidence`
- Unmapped by direct/JSON/timestamp column-name scan: `evidence_refs`

- `belief_id` → beliefs.belief_id; belief_revisions.belief_id
- `knowledge_id` → beliefs.knowledge_id
- `revision_id` → belief_revisions.revision_id; belief_revision_evidence.revision_id
- `revision_number` → belief_revisions.revision_number
- `epistemic_status` → belief_revisions.epistemic_status
- `confidence` → belief_revisions.confidence
- `revision_reason` → belief_revisions.revision_reason
- `evidence_refs` → belief_revision_evidence.evidence_id joined by revision_id; serialize as evidence references
- `created_at` → beliefs.created_at_ms (timestamp conversion); belief_revisions.created_at_ms (timestamp conversion)

### `prediction.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/predictionCreated`
- Bound tables: `predictions`, `prediction_evaluations`
- Unmapped by direct/JSON/timestamp column-name scan: `conditions`, `horizon`, `confidence`, `evidence_refs`

- `prediction_id` → predictions.prediction_id; prediction_evaluations.prediction_id
- `subject_ref` → predictions.subject_ref
- `expected_outcome` → predictions.expected_outcome_json (JSON decode)
- `evaluation_criteria` → predictions.evaluation_criteria_json (JSON decode)
- `conditions` → **UNMAPPED in the bound DDL columns**
- `horizon` → predictions.horizon_end_ms projected as the horizon deadline; no additional horizon fields are inferred
- `confidence` → **UNMAPPED in the bound DDL columns**
- `evidence_refs` → **UNMAPPED in the bound DDL columns**
- `created_at` → predictions.created_at_ms (timestamp conversion)

### `appraisal.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/appraisalUpdated`
- Bound tables: `appraisal_records`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `appraisal_id` → appraisal_records.appraisal_id
- `context_id` → appraisal_records.context_id
- `context_version` → appraisal_records.context_version
- `assessment` → appraisal_records.assessment_json (JSON decode)
- `uncertainty` → appraisal_records.uncertainty_json (JSON decode)
- `evidence_refs` → appraisal_records.evidence_refs_json (JSON decode)
- `sensitivity` → appraisal_records.sensitivity
- `created_at` → appraisal_records.created_at_ms (timestamp conversion)
- `valid_until` → appraisal_records.valid_until_ms (timestamp conversion)

### `attention.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/attentionAllocated`
- Bound tables: `events`
- Unmapped by direct/JSON/timestamp column-name scan: `allocation_id`, `context_id`, `context_version`, `candidate_refs`, `selected_refs`, `deferred_refs`, `resource_budget`, `rationale_ref`, `created_at`, `valid_until`

- `allocation_id` → events.payload_json $.allocation_id (attention.allocated.v1 body)
- `context_id` → events.payload_json $.context_id
- `context_version` → events.payload_json $.context_version
- `candidate_refs` → events.payload_json $.candidate_refs
- `selected_refs` → events.payload_json $.selected_refs
- `deferred_refs` → events.payload_json $.deferred_refs
- `resource_budget` → events.payload_json $.resource_budget
- `rationale_ref` → events.payload_json $.rationale_ref
- `created_at` → events.occurred_at_ms
- `valid_until` → events.payload_json $.valid_until

### `reasoning.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/reasoningHypothesisProposed`
- Bound tables: `reasoning_assessments`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `reasoning_id` → reasoning_assessments.reasoning_id
- `context_id` → reasoning_assessments.context_id
- `context_version` → reasoning_assessments.context_version
- `hypothesis_ref` → reasoning_assessments.hypothesis_ref
- `evidence_refs` → reasoning_assessments.evidence_refs_json (JSON decode)
- `conclusion_summary_ref` → reasoning_assessments.conclusion_summary_ref
- `uncertainty` → reasoning_assessments.uncertainty_json (JSON decode)
- `sensitivity` → reasoning_assessments.sensitivity
- `created_at` → reasoning_assessments.created_at_ms (timestamp conversion)

### `goal.get`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/goalRevision`
- Bound tables: `goals`, `goal_revisions`, `goal_revision_objective_bindings`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `goal_id` → goals.goal_id; goal_revisions.goal_id; goal_revision_objective_bindings.goal_id
- `revision` → goal_revisions.revision
- `description` → goal_revisions.description
- `state` → goal_revisions.state
- `priority` → goal_revisions.priority
- `constraints` → goal_revisions.constraints_json (JSON decode)
- `reason_ref` → goal_revisions.reason_ref
- `created_at` → goals.created_at_ms (timestamp conversion); goal_revisions.created_at_ms (timestamp conversion); goal_revision_objective_bindings.created_at_ms (timestamp conversion)
- `objective_id` → goal_revision_objective_bindings.objective_id
- `objective_version` → goal_revision_objective_bindings.objective_version

### `plan.get`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/planRevision`
- Bound tables: `plans`, `plan_steps`, `plan_step_dependencies`, `plan_step_contracts`
- Unmapped by direct/JSON/timestamp column-name scan: `step_refs`, `context_version_ref`, `capability_epoch_digest`

- `plan_id` → plans.plan_id; plan_steps.plan_id
- `goal_id` → plans.goal_id
- `goal_revision` → plans.goal_revision
- `plan_version` → plans.plan_version
- `status` → plans.status; plan_steps.status
- `created_at` → plans.created_at_ms (timestamp conversion); plan_steps.created_at_ms (timestamp conversion); plan_step_contracts.created_at_ms (timestamp conversion)
- `step_refs` → plan_steps.step_id joined by plan_id and ordered by sequence
- `context_version_ref` → **UNMAPPED in the bound DDL columns**
- `capability_epoch_digest` → **UNMAPPED in the bound DDL columns**

### `decision.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/decisionRecorded`
- Bound tables: `decision_records`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `decision_id` → decision_records.decision_id
- `goal_id` → decision_records.goal_id
- `plan_id` → decision_records.plan_id
- `decision_type` → decision_records.decision_type
- `selected_option_ref` → decision_records.selected_option_ref
- `rationale_ref` → decision_records.rationale_ref
- `uncertainty` → decision_records.uncertainty_json (JSON decode)
- `created_at` → decision_records.created_at_ms (timestamp conversion)

### `task.status`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/taskRunStatus`
- Bound tables: `task_runs`, `task_checkpoints`, `task_checkpoint_details`
- Unmapped by direct/JSON/timestamp column-name scan: `checkpoint_refs`, `failure_ref`, `revision`

- `task_run_id` → task_runs.task_run_id; task_checkpoints.task_run_id
- `task_definition_ref` → task_runs.task_definition_ref
- `state` → task_runs.state
- `priority` → task_runs.priority
- `budget` → task_runs.budget_json (JSON decode)
- `checkpoint_refs` → task_checkpoints.checkpoint_ref joined by task_run_id and ordered by sequence
- `created_at` → task_runs.created_at_ms (timestamp conversion); task_checkpoints.created_at_ms (timestamp conversion); task_checkpoint_details.created_at_ms (timestamp conversion)
- `updated_at` → task_runs.updated_at_ms (timestamp conversion)
- `failure_ref` → **UNMAPPED in the bound DDL columns**
- `revision` → task_runs.revision (added by aurion_events migration v2)

### `operation.status`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/operationLifecycleEvent`
- Bound tables: `operations`, `operation_steps`, `recovery_journal`, `operation_details`, `operation_attempts`
- Unmapped by direct/JSON/timestamp column-name scan: `occurred_at`, `policy_decision_ref`, `attempt_state`

- `operation_id` → operations.operation_id; operation_steps.operation_id; recovery_journal.operation_id; operation_details.operation_id; operation_attempts.operation_id
- `attempt_id` → operation_attempts.attempt_id
- `state` → operations.state; operation_steps.state; recovery_journal.state; operation_attempts.state
- `occurred_at` → events.occurred_at_ms for the matching operation lifecycle event (events added to this query's table bindings)
- `provider_receipt_ref` → operation_attempts.provider_receipt_ref
- `verification_evidence_ref` → operation_attempts.verification_evidence_ref
- `error_ref` → operation_attempts.error_ref
- `uncertainty_reason` → operation_attempts.uncertainty_reason
- `policy_decision_ref` → **UNMAPPED in the bound DDL columns**
- `attempt_state` → operation_attempts.state for the selected attempt
- `attempt_number` → operation_attempts.attempt_number

### `permission.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/permissionRecord`
- Bound tables: `permissions`, `policies`, `provider_permissions`, `approval_requests`, `approval_decisions`
- Unmapped by direct/JSON/timestamp column-name scan: `owner_id`, `capability_ref`, `target_scope`, `status`, `granted_by`, `approval_ref`

- `permission_id` → permissions.permission_id
- `owner_id` → **UNMAPPED in the bound DDL columns**
- `capability_ref` → permissions.capability_id
- `target_scope` → composed object from permissions.operation_scope_json, resource_scope_json, data_scope_json, side_effect_scope_json and environment_scope_json
- `status` → **UNMAPPED in the bound DDL columns**
- `policy_version_ref` → approval_requests.policy_version_ref
- `granted_by` → permissions.grant_source
- `approval_ref` → **UNMAPPED in the bound DDL columns**
- `created_at` → permissions.created_at_ms (timestamp conversion); policies.created_at_ms (timestamp conversion); provider_permissions.created_at_ms (timestamp conversion)
- `expires_at` → permissions.expires_at_ms (timestamp conversion); provider_permissions.expires_at_ms (timestamp conversion); approval_requests.expires_at_ms (timestamp conversion)
- `revoked_at` → permissions.revoked_at_ms (timestamp conversion); provider_permissions.revoked_at_ms (timestamp conversion)

### `audit.lookup`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/auditRecord`
- Bound tables: `governance_audit`, `data_disclosures`
- Unmapped by direct/JSON/timestamp column-name scan: `owner_id`, `actor_identity`, `action_type`, `approval_ref`, `evidence_refs`, `correlation_id`

- `audit_id` → governance_audit.audit_id
- `owner_id` → **UNMAPPED in the bound DDL columns**
- `actor_identity` → governance_audit.actor_id
- `action_type` → governance_audit.action
- `target_ref` → governance_audit.target_ref
- `decision` → governance_audit.decision
- `policy_version_ref` → governance_audit.policy_version_ref; data_disclosures.policy_version_ref
- `operation_id` → governance_audit.operation_id
- `approval_ref` → governance_audit.request_id joined to approval_requests.request_id when present
- `evidence_refs` → **UNMAPPED in the bound DDL columns**
- `occurred_at` → governance_audit.occurred_at_ms (timestamp conversion)
- `correlation_id` → **UNMAPPED in the bound DDL columns**

### `device.capabilities`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/capabilityDescriptorRecord`
- Bound tables: `capability_descriptors`
- Unmapped by direct/JSON/timestamp column-name scan: `descriptor_schema_version`, `descriptor_body`

- `capability_id` → capability_descriptors.capability_id
- `descriptor_version` → capability_descriptors.descriptor_version
- `provider_id` → capability_descriptors.provider_id
- `device_scope` → capability_descriptors.device_scope
- `discovery_epoch` → capability_descriptors.discovery_epoch
- `descriptor_schema_version` → **UNMAPPED in the bound DDL columns**
- `descriptor_sha256` → capability_descriptors.descriptor_sha256
- `source_ref` → capability_descriptors.source_ref
- `first_discovered_at` → capability_descriptors.first_discovered_at_ms (timestamp conversion)
- `last_verified_at` → capability_descriptors.last_verified_at_ms (timestamp conversion)
- `expires_at` → capability_descriptors.expires_at_ms (timestamp conversion)
- `status` → capability_descriptors.status
- `descriptor_body` → capability_descriptors.descriptor_json (JSON decode; validate with the stored descriptor schema version)

### `objective.inspect`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/objective`
- Bound tables: `objective_records`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `objective_id` → objective_records.objective_id
- `statement` → objective_records.statement
- `request_source_ref` → objective_records.request_source_ref
- `created_at` → objective_records.created_at_ms (timestamp conversion)
- `status` → objective_records.status
- `success_evidence` → objective_records.success_evidence_json (JSON decode)
- `constraints` → objective_records.constraints_json (JSON decode)
- `assumptions` → objective_records.assumptions_json (JSON decode)
- `uncertainty` → objective_records.uncertainty_json (JSON decode)
- `owner_ref` → objective_records.owner_ref
- `version` → objective_records.version

### `world.entity.search`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/entity`
- Bound tables: `world_entities`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `entity_id` → world_entities.entity_id
- `identity_status` → world_entities.identity_status
- `description` → world_entities.description
- `first_observed_at` → world_entities.first_observed_at_ms (timestamp conversion)
- `last_observed_at` → world_entities.last_observed_at_ms (timestamp conversion)
- `evidence_refs` → world_entities.evidence_refs_json (JSON decode)
- `scope` → world_entities.scope_json (JSON decode)
- `attributes` → world_entities.attributes_json (JSON decode)
- `sensitivity` → world_entities.sensitivity
- `owner_ref` → world_entities.owner_ref
- `version` → world_entities.version

### `world.entity.inspect`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/entity`
- Bound tables: `world_entities`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `entity_id` → world_entities.entity_id
- `identity_status` → world_entities.identity_status
- `description` → world_entities.description
- `first_observed_at` → world_entities.first_observed_at_ms (timestamp conversion)
- `last_observed_at` → world_entities.last_observed_at_ms (timestamp conversion)
- `evidence_refs` → world_entities.evidence_refs_json (JSON decode)
- `scope` → world_entities.scope_json (JSON decode)
- `attributes` → world_entities.attributes_json (JSON decode)
- `sensitivity` → world_entities.sensitivity
- `owner_ref` → world_entities.owner_ref
- `version` → world_entities.version

### `world.relationship.search`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/relationship`
- Bound tables: `world_relationships`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `relationship_id` → world_relationships.relationship_id
- `subject_ref` → world_relationships.subject_ref
- `predicate` → world_relationships.predicate
- `object_ref` → world_relationships.object_ref
- `epistemic_status` → world_relationships.epistemic_status
- `confidence` → world_relationships.confidence
- `evidence_refs` → world_relationships.evidence_refs_json (JSON decode)
- `valid_from` → world_relationships.valid_from_ms (timestamp conversion)
- `valid_until` → world_relationships.valid_until_ms (timestamp conversion)
- `context_ref` → world_relationships.context_ref
- `owner_ref` → world_relationships.owner_ref
- `version` → world_relationships.version

### `situation.inspect`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/situation`
- Bound tables: `situation_snapshots`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `situation_id` → situation_snapshots.situation_id
- `version` → situation_snapshots.version
- `objective_refs` → situation_snapshots.objective_refs_json (JSON decode)
- `entity_refs` → situation_snapshots.entity_refs_json (JSON decode)
- `observed_at` → situation_snapshots.observed_at_ms (timestamp conversion)
- `recorded_at` → situation_snapshots.recorded_at_ms (timestamp conversion)
- `state_claims` → situation_snapshots.state_claims_json (JSON decode)
- `unknowns` → situation_snapshots.unknowns_json (JSON decode)
- `conflicts` → situation_snapshots.conflicts_json (JSON decode)
- `evidence_refs` → situation_snapshots.evidence_refs_json (JSON decode)
- `context_ref` → situation_snapshots.context_ref
- `owner_ref` → situation_snapshots.owner_ref

### `means.affordance.search`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/affordanceHypothesis`
- Bound tables: `affordance_hypotheses`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `hypothesis_id` → affordance_hypotheses.hypothesis_id
- `objective_ref` → affordance_hypotheses.objective_ref
- `actor_refs` → affordance_hypotheses.actor_refs_json (JSON decode)
- `resource_refs` → affordance_hypotheses.resource_refs_json (JSON decode)
- `interaction_description` → affordance_hypotheses.interaction_description
- `preconditions` → affordance_hypotheses.preconditions_json (JSON decode)
- `expected_effects` → affordance_hypotheses.expected_effects_json (JSON decode)
- `authority_requirements` → affordance_hypotheses.authority_requirements_json (JSON decode)
- `evidence_refs` → affordance_hypotheses.evidence_refs_json (JSON decode)
- `confidence` → affordance_hypotheses.confidence
- `status` → affordance_hypotheses.status
- `scope` → affordance_hypotheses.scope_json (JSON decode)
- `limitations` → affordance_hypotheses.limitations_json (JSON decode)
- `composition_refs` → affordance_hypotheses.composition_refs_json (JSON decode)
- `owner_ref` → affordance_hypotheses.owner_ref
- `version` → affordance_hypotheses.version
- `created_at` → affordance_hypotheses.created_at_ms (timestamp conversion)

### `interaction.inspect`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/interactionProposal`
- Bound tables: `interaction_proposals`
- Unmapped by direct/JSON/timestamp column-name scan: `deadline`, `execution_binding_ref`

- `interaction_id` → interaction_proposals.interaction_id
- `objective_ref` → interaction_proposals.objective_ref
- `actor_ref` → interaction_proposals.actor_ref
- `target_refs` → interaction_proposals.target_refs_json (JSON decode)
- `means_hypothesis_refs` → interaction_proposals.means_hypothesis_refs_json (JSON decode)
- `proposed_effects` → interaction_proposals.proposed_effects_json (JSON decode)
- `authority_context_ref` → interaction_proposals.authority_context_ref
- `risk_assessment` → interaction_proposals.risk_assessment_json (JSON decode)
- `precondition_evidence_refs` → interaction_proposals.precondition_evidence_refs_json (JSON decode)
- `proposed_at` → interaction_proposals.proposed_at_ms (timestamp conversion)
- `deadline` → interaction_proposals.deadline_at_ms
- `status` → interaction_proposals.status
- `authorization_ref` → interaction_proposals.authorization_ref
- `execution_binding_ref` → interaction_proposals.execution_operation_ref
- `owner_ref` → interaction_proposals.owner_ref

### `interaction.outcome.inspect`

- Result schema: `schemas/world-interaction.v1.schema.json#/$defs/interactionOutcome`
- Bound tables: `interaction_outcomes`
- Unmapped by direct/JSON/timestamp column-name scan: none

- `outcome_id` → interaction_outcomes.outcome_id
- `interaction_ref` → interaction_outcomes.interaction_ref
- `observed_at` → interaction_outcomes.observed_at_ms (timestamp conversion)
- `recorded_at` → interaction_outcomes.recorded_at_ms (timestamp conversion)
- `result_status` → interaction_outcomes.result_status
- `observed_effects` → interaction_outcomes.observed_effects_json (JSON decode)
- `evidence_refs` → interaction_outcomes.evidence_refs_json (JSON decode)
- `unresolved_effects` → interaction_outcomes.unresolved_effects_json (JSON decode)
- `attribution` → interaction_outcomes.attribution_json (JSON decode)
- `side_effects` → interaction_outcomes.side_effects_json (JSON decode)
- `owner_ref` → interaction_outcomes.owner_ref

## 3. High-priority semantic gaps

1. **`environment.inspect`:** its result schema exposes observation identity, owner/device/scope, collector method/version, platform context, observed facts, limitations and validity. The bound `experiences`/`evidence_items` DDL does not provide direct/JSON/timestamp-named columns for most of those fields. The authoritative source payload and owner/device linkage must be specified; otherwise the query contract cannot be implemented faithfully.
2. **`memory.search`:** the result schema is a retrieval receipt (`retrieval_id`, `query_ref`, `candidate_refs`, `access_decision_ref`), while the query is bound to `memory_records`/`memory_links`. No retrieval-receipt table or explicit ephemeral-result contract is mapped. Clarify whether this query returns candidates, a persisted retrieval record, or a receipt from a separate retrieval operation.
3. **`attention.inspect`:** all result fields appear to be an event-derived allocation projection, but the query binds only `events`. The required event type filter, payload pointer mapping, sequence/ordering semantics and retention/freshness behaviour are not specified by the DDL column scan.
4. **`permission.inspect`:** result fields such as owner, capability reference, target scope, status, grantor and approval reference do not map directly to the current `permissions` table columns. The projection needs explicit aliases, derivation rules and joins across policy/approval/provider permission records; status must not be guessed.
5. **`audit.lookup`:** the result includes owner, actor identity, action type, approval reference, evidence references and correlation ID. The current governance audit row stores `actor_id`, `action`, `request_id` and a `details_digest`, but does not persist all those output values as direct columns. A digest cannot be expanded into evidence references. Either define a canonical details payload/source join or change the output schema.
6. **`representation.inspect`:** `method_id`, `method_version` and `source_refs` have no direct column candidate in `representations`; the current DDL stores `method` and experience linkage. Their decomposition/lineage rules need specification.
7. **`prediction.inspect`:** `conditions`, `horizon`, `confidence` and `evidence_refs` have no direct/JSON/timestamp candidate in the bound prediction tables. `horizon_end_ms` exists but does not alone define the full horizon contract.
8. **`interaction.inspect`:** `deadline` and `execution_binding_ref` lack direct/JSON/timestamp candidate columns in the bound interaction table; the DDL uses `deadline_at_ms` and `execution_operation_ref`, which require explicit alias and timestamp conversion rules.
9. **`context.get`:** `provenance_refs` is plural while DDL stores `provenance_ref`; `uncertainty` has no direct candidate. The cardinality and uncertainty source must be specified.
10. **`operation.status` and `task.status`:** these are projections across operation/task state, attempts, checkpoints and recovery. The exact event/current-state source, timestamps, failure references, policy decision lineage and checkpoint aggregation need explicit field-by-field definitions.
11. **`goal.get` objective lineage:** memory migration v6 now adds an owner-scoped, composite-FK binding from each new goal revision to an exact objective revision. The query table binding and result schema include `objective_id`/`objective_version`. Legacy unbound goal revisions remain excluded from valid derived-goal results pending explicit reconciliation. This corrects the missing durable lineage, but the actual SELECT and owner-scoped query remain unexecuted.

## 4. Required closure work

For every query:
1. Declare the exact result schema property inventory and an explicit field-to-source mapping.
2. For each field, identify source store/table/column, JSON pointer, join path, alias, conversion, nullability and whether it is current-state or event-history derived.
3. Define owner/actor scope before any existence-revealing lookup; prove cross-owner negative controls.
4. Define redaction by field and sensitivity; do not rely only on row-level filtering.
5. Define consistency/snapshot boundary across joined tables and stores.
6. Define deterministic ordering, stable cursor, freshness/cache and maximum rows/bytes/time.
7. Add positive, negative, redaction, stale-revision, pagination, consistency and query-plan fixtures.
8. Validate each query against a real deterministic store fixture and assert the exact projected field set and values. Schema shape validation alone is insufficient.

**Current disposition:** BR-002 remains OPEN. This report makes the storage/projection mismatch visible; it does not resolve it. Do not promote any query to dispatchable based on this scan.
