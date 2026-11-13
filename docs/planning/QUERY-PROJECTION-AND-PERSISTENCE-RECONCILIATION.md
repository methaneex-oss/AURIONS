# AURIONS — Query Projection and Persistence Reconciliation

- **Status:** All 310 query result fields have a proposed source/derivation; no projection field remains unclassified. Runtime SQL and behavioural verification remain open.
- **Scope:** All 29 query registry entries, their result-item schemas and currently proposed SQLite DDL.
- **Evidence:** Exact schema/DDL files at the current branch revision. This is a static column-name reconciliation, not executed SQL or semantic query verification.
- **Boundary:** A candidate column name is not proof of a correct SELECT, join, owner filter, redaction rule, or stable cursor. All queries remain design-only/non-dispatchable.

## 1. Findings

The semantic pass distinguishes a genuinely absent persisted field from a field that is derived from an existing event payload, relational join, stored timestamp, or authenticated read context. A read-only query may construct an ephemeral retrieval envelope; it must not write a retrieval receipt merely to satisfy the result schema. Every mapping below is a proposed source/transform, not executed SQL or a verified owner-scope/redaction implementation.

The query registry declares 29 result-item projections containing 310 fields. The initial name scan exposed 65 fields across 16 queries without direct column-name candidates. The semantic pass and three additive migrations now provide a proposed persisted or query-derived source for all 310 fields: memory v7, events v4 and governance v4; governance v3 separately adds approval owner/session binding. No query SQL or handler is claimed implemented.

This reconciliation is deliberately conservative:
- A field with a proposed source/derivation below is not considered runtime-verified; exact SELECT expressions, joins, JSON pointers, aliases, nullability and owner filters still require implementation tests.
- A field listed as unresolved has no defensible source/derivation in the current proposed DDL and remains a blocker for the owning query contract. The current registry has zero such fields; this does not close runtime verification.
- No field is inferred from a different owner, an unbound table or an opaque artifact. Event-payload derivations name the exact event table and payload field.

| Query | Result schema | Fields | Unmapped projection fields |
|---|---|---:|---|
| `environment.inspect` | `environmentObserved` | 14 | None — all result fields have proposed sources/derivations |
| `capability.search` | `capabilityDescriptorRecord` | 13 | None — all result fields have proposed sources/derivations |
| `capability.inspect` | `capabilityDescriptorRecord` | 13 | None — all result fields have proposed sources/derivations |
| `capability.knowledge.inspect` | `capabilityKnowledgeRevision` | 10 | None — all result fields have proposed sources/derivations |
| `representation.inspect` | `representationCreated` | 9 | None — all result fields have proposed sources/derivations |
| `context.get` | `contextSnapshot` | 9 | None — all result fields have proposed sources/derivations |
| `memory.search` | `memoryRetrieval` | 6 | None — all result fields have proposed sources/derivations |
| `knowledge.search` | `knowledgeItem` | 6 | None — all result fields have proposed sources/derivations |
| `belief.inspect` | `beliefRevision` | 9 | None — all result fields have proposed sources/derivations |
| `prediction.inspect` | `predictionCreated` | 9 | None — all result fields have proposed sources/derivations |
| `appraisal.inspect` | `appraisalUpdated` | 9 | None — all result fields have proposed sources/derivations |
| `attention.inspect` | `attentionAllocated` | 10 | None — all result fields have proposed sources/derivations |
| `reasoning.inspect` | `reasoningHypothesisProposed` | 9 | None — all result fields have proposed sources/derivations |
| `goal.get` | `goalRevision` | 10 | None — all result fields have proposed sources/derivations |
| `plan.get` | `planRevision` | 9 | None — all result fields have proposed sources/derivations |
| `decision.inspect` | `decisionRecorded` | 8 | None — all result fields have proposed sources/derivations |
| `task.status` | `taskRunStatus` | 10 | None — all result fields have proposed sources/derivations |
| `operation.status` | `operationLifecycleEvent` | 11 | None — all result fields have proposed sources/derivations |
| `permission.inspect` | `permissionRecord` | 11 | None — all result fields have proposed sources/derivations |
| `audit.lookup` | `auditRecord` | 12 | None — all result fields have proposed sources/derivations |
| `device.capabilities` | `capabilityDescriptorRecord` | 13 | None — all result fields have proposed sources/derivations |
| `objective.inspect` | `objective` | 11 | None — all result fields have proposed sources/derivations |
| `world.entity.search` | `entity` | 11 | None — all result fields have proposed sources/derivations |
| `world.entity.inspect` | `entity` | 11 | None — all result fields have proposed sources/derivations |
| `world.relationship.search` | `relationship` | 12 | None — all result fields have proposed sources/derivations |
| `situation.inspect` | `situation` | 12 | None — all result fields have proposed sources/derivations |
| `means.affordance.search` | `affordanceHypothesis` | 17 | None — all result fields have proposed sources/derivations |
| `interaction.inspect` | `interactionProposal` | 15 | None — all result fields have proposed sources/derivations |
| `interaction.outcome.inspect` | `interactionOutcome` | 11 | None — all result fields have proposed sources/derivations |
## 2. Field-level candidate inventory

### `environment.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/environmentObserved`
- Bound tables: `environment_observations`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `observation_id` → environment_observations.observation_id
- `owner_id` → environment_observations.owner_ref (alias to owner_id)
- `device_id` → environment_observations.device_id
- `environment_scope` → environment_observations.environment_scope
- `observed_at` → environment_observations.observed_at_ms (timestamp conversion)
- `recorded_at` → environment_observations.recorded_at_ms (timestamp conversion)
- `source_id` → environment_observations.source_id
- `collection_method` → environment_observations.collection_method
- `collector_version` → environment_observations.collector_version
- `platform_context` → environment_observations.platform_context_json (JSON decode)
- `observed_facts` → environment_observations.observed_facts_json (JSON decode)
- `sensitivity` → environment_observations.sensitivity
- `limitations` → environment_observations.limitations_json (JSON decode)
- `validity` → environment_observations.validity_json (JSON decode; nullable)

### `capability.search`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/capabilityDescriptorRecord`
- Bound tables: `capability_descriptors`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `capability_id` → capability_descriptors.capability_id
- `descriptor_version` → capability_descriptors.descriptor_version
- `provider_id` → capability_descriptors.provider_id
- `device_scope` → capability_descriptors.device_scope
- `discovery_epoch` → capability_descriptors.discovery_epoch
- `descriptor_schema_version` → capability_descriptors.descriptor_schema_version (legacy NULL rows excluded)
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
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `capability_id` → capability_descriptors.capability_id
- `descriptor_version` → capability_descriptors.descriptor_version
- `provider_id` → capability_descriptors.provider_id
- `device_scope` → capability_descriptors.device_scope
- `discovery_epoch` → capability_descriptors.discovery_epoch
- `descriptor_schema_version` → capability_descriptors.descriptor_schema_version (legacy NULL rows excluded)
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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `representation_id` → representations.representation_id
- `experience_id` → representations.experience_id
- `representation_type` → representations.representation_type
- `method_id` → representations.method (legacy column projected as method_id; method-version and multi-source lineage are persisted separately by memory migration v7)
- `method_version` → representations.method_version (legacy NULL rows excluded)
- `content` → representations.content_json (JSON decode)
- `uncertainty` → representations.uncertainty_json (JSON decode)
- `source_refs` → representations.source_refs_json (JSON decode; legacy NULL rows excluded)
- `created_at` → representations.created_at_ms (timestamp conversion)

### `context.get`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/contextSnapshot`
- Bound tables: `contexts`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `context_id` → contexts.context_id
- `version` → contexts.version
- `scope` → contexts.scope
- `valid_from` → contexts.valid_from_ms (timestamp conversion)
- `valid_until` → contexts.valid_until_ms (timestamp conversion)
- `attributes` → contexts.attributes_json (JSON decode)
- `provenance_refs` → contexts.provenance_refs_json (JSON decode; legacy NULL rows excluded)
- `uncertainty` → contexts.uncertainty_json (JSON decode; legacy NULL rows excluded)
- `created_at` → contexts.created_at_ms (timestamp conversion)

### `memory.search`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/memoryRetrieval`
- Bound tables: `memory_records`, `memory_links`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `retrieval_id` → generated per query execution; ephemeral and not persisted by this read-only query
- `query_ref` → query-envelope/request reference supplied by the authenticated query execution
- `scope` → authenticated execution scope after policy evaluation; never copied from caller filters
- `candidate_refs` → memory_records.memory_id + provenance_refs_json + uncertainty_json; relevance is computed by the retrieval ranking function; legacy rows lacking provenance/uncertainty are excluded
- `created_at` → memory_records.created_at_ms (timestamp conversion); memory_links.created_at_ms (timestamp conversion)
- `access_decision_ref` → authorization decision reference from the trusted query context when present; otherwise null, with no cross-store snapshot implied

### `knowledge.search`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/knowledgeItem`
- Bound tables: `knowledge_items`, `beliefs`, `belief_revisions`, `evidence_items`, `belief_revision_evidence`
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

- `knowledge_id` → knowledge_items.knowledge_id; beliefs.knowledge_id
- `proposition` → knowledge_items.proposition
- `domain` → knowledge_items.domain
- `status` → knowledge_items.status
- `created_at` → knowledge_items.created_at_ms (timestamp conversion); beliefs.created_at_ms (timestamp conversion); belief_revisions.created_at_ms (timestamp conversion)
- `updated_at` → knowledge_items.updated_at_ms (timestamp conversion); beliefs.updated_at_ms (timestamp conversion)

### `belief.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/beliefRevision`
- Bound tables: `beliefs`, `belief_revisions`, `evidence_items`, `belief_revision_evidence`
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `prediction_id` → predictions.prediction_id; prediction_evaluations.prediction_id
- `subject_ref` → predictions.subject_ref
- `expected_outcome` → predictions.expected_outcome_json (JSON decode)
- `evaluation_criteria` → predictions.evaluation_criteria_json (JSON decode)
- `conditions` → predictions.conditions_json (JSON decode; legacy NULL rows excluded)
- `horizon` → predictions.horizon_end_ms projected as the horizon deadline; no additional horizon fields are inferred
- `confidence` → predictions.confidence (nullable)
- `evidence_refs` → predictions.evidence_refs_json (JSON decode; legacy NULL rows excluded)
- `created_at` → predictions.created_at_ms (timestamp conversion)

### `appraisal.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/appraisalUpdated`
- Bound tables: `appraisal_records`
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `plan_id` → plans.plan_id; plan_steps.plan_id
- `goal_id` → plans.goal_id
- `goal_revision` → plans.goal_revision
- `plan_version` → plans.plan_version
- `status` → plans.status; plan_steps.status
- `created_at` → plans.created_at_ms (timestamp conversion); plan_steps.created_at_ms (timestamp conversion); plan_step_contracts.created_at_ms (timestamp conversion)
- `step_refs` → plan_steps.step_id joined by plan_id and ordered by sequence
- `context_version_ref` → plans.context_version_ref (nullable)
- `capability_epoch_digest` → plans.capability_epoch_digest (nullable)

### `decision.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/decisionRecorded`
- Bound tables: `decision_records`
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `task_run_id` → task_runs.task_run_id; task_checkpoints.task_run_id
- `task_definition_ref` → task_runs.task_definition_ref
- `state` → task_runs.state
- `priority` → task_runs.priority
- `budget` → task_runs.budget_json (JSON decode)
- `checkpoint_refs` → task_checkpoints.checkpoint_ref joined by task_run_id and ordered by sequence
- `created_at` → task_runs.created_at_ms (timestamp conversion); task_checkpoints.created_at_ms (timestamp conversion); task_checkpoint_details.created_at_ms (timestamp conversion)
- `updated_at` → task_runs.updated_at_ms (timestamp conversion)
- `failure_ref` → task_runs.failure_ref (nullable; explicit failure reference only)
- `revision` → task_runs.revision (added by aurion_events migration v2)

### `operation.status`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/operationLifecycleEvent`
- Bound tables: `operations`, `operation_steps`, `recovery_journal`, `operation_details`, `operation_attempts`, `events`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `operation_id` → operations.operation_id; operation_steps.operation_id; recovery_journal.operation_id; operation_details.operation_id; operation_attempts.operation_id
- `attempt_id` → operation_attempts.attempt_id
- `state` → operations.state; operation_steps.state; recovery_journal.state; operation_attempts.state
- `occurred_at` → events.occurred_at_ms for the matching operation lifecycle event (events added to this query's table bindings)
- `provider_receipt_ref` → operation_attempts.provider_receipt_ref
- `verification_evidence_ref` → operation_attempts.verification_evidence_ref
- `error_ref` → operation_attempts.error_ref
- `uncertainty_reason` → operation_attempts.uncertainty_reason
- `policy_decision_ref` → operation_details.policy_decision_ref (nullable; explicit policy decision reference only)
- `attempt_state` → operation_attempts.state for the selected attempt
- `attempt_number` → operation_attempts.attempt_number

### `permission.inspect`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/permissionRecord`
- Bound tables: `permissions`, `policies`, `provider_permissions`, `approval_requests`, `approval_decisions`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `permission_id` → permissions.permission_id
- `owner_id` → permissions.owner_ref (alias to owner_id; legacy NULL rows excluded)
- `capability_ref` → permissions.capability_id
- `target_scope` → composed object from permissions.operation_scope_json, resource_scope_json, data_scope_json, side_effect_scope_json and environment_scope_json
- `status` → permissions.status (persisted active/revoked/expired/denied state; legacy NULL rows excluded)
- `policy_version_ref` → permissions.policy_version_ref (new canonical reference; legacy NULL rows excluded)
- `granted_by` → permissions.grant_source
- `approval_ref` → permissions.approval_ref (nullable)
- `created_at` → permissions.created_at_ms (timestamp conversion); policies.created_at_ms (timestamp conversion); provider_permissions.created_at_ms (timestamp conversion)
- `expires_at` → permissions.expires_at_ms (timestamp conversion); provider_permissions.expires_at_ms (timestamp conversion); approval_requests.expires_at_ms (timestamp conversion)
- `revoked_at` → permissions.revoked_at_ms (timestamp conversion); provider_permissions.revoked_at_ms (timestamp conversion)

### `audit.lookup`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/auditRecord`
- Bound tables: `governance_audit`, `data_disclosures`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `audit_id` → governance_audit.audit_id
- `owner_id` → governance_audit.owner_ref (alias to owner_id; legacy NULL rows excluded)
- `actor_identity` → governance_audit.actor_id
- `action_type` → governance_audit.action
- `target_ref` → governance_audit.target_ref
- `decision` → governance_audit.decision
- `policy_version_ref` → governance_audit.policy_version_ref; data_disclosures.policy_version_ref
- `operation_id` → governance_audit.operation_id
- `approval_ref` → governance_audit.request_id joined to approval_requests.request_id when present
- `evidence_refs` → governance_audit.evidence_refs_json (JSON decode; legacy NULL rows excluded)
- `occurred_at` → governance_audit.occurred_at_ms (timestamp conversion)
- `correlation_id` → governance_audit.correlation_id (legacy NULL rows excluded)

### `device.capabilities`

- Result schema: `schemas/domain-payloads.v1.schema.json#/$defs/capabilityDescriptorRecord`
- Bound tables: `capability_descriptors`
- Remaining unresolved source/derivation fields: None; proposed DDL/source mappings are recorded below. Legacy NULL rows are excluded where required fields are non-nullable in the result schema.

- `capability_id` → capability_descriptors.capability_id
- `descriptor_version` → capability_descriptors.descriptor_version
- `provider_id` → capability_descriptors.provider_id
- `device_scope` → capability_descriptors.device_scope
- `discovery_epoch` → capability_descriptors.discovery_epoch
- `descriptor_schema_version` → capability_descriptors.descriptor_schema_version (legacy NULL rows excluded)
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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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
- Remaining unresolved source/derivation fields: None; proposed mappings/derivations are listed below and remain unverified

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

## 3. Remaining verification gaps

The source-to-result inventory now has no unclassified fields, but the following are not yet executed or runtime-verified:

1. **Legacy rows:** memory v7 and governance v4 deliberately leave newly added columns NULL on legacy records. Queries whose result schemas require those values must exclude such rows until an authoritative backfill/reconciliation exists. No owner, source, confidence, evidence or policy state is inferred.
2. **memory.search:** candidate provenance and uncertainty are persisted; relevance remains a query-time ranking result. The ranker, deterministic tie-break, evidence filtering and resource budget have not been executed.
3. **attention.inspect:** event payload JSON is the source. The actual event-type predicate, sequence watermark, retention boundary and snapshot query remain unimplemented.
4. **permission.inspect / audit.lookup:** owner/status/evidence/correlation sources are now represented in governance v4. The SQL joins, cross-owner negative controls, denial semantics and field-level redaction remain unimplemented.
5. **All 29 queries:** no executable SELECT suite currently proves exact aliases, JSON decoding, timestamp conversion, joins, owner predicates, snapshot consistency, stable cursors, pagination, maximum rows/bytes/time or query-plan/index use.
6. **Target resource budgets:** numerical endpoint budgets remain blocked on measured target-runtime evidence; no invented limits are substituted.


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
