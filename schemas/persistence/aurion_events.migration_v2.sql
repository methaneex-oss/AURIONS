-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_events.db
-- Source: docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md, Section 26.5.2
-- Proposed operation evidence and task checkpoint migration v2

CREATE TABLE operation_details (
  operation_id BLOB PRIMARY KEY REFERENCES operations(operation_id),
  owner_id TEXT NOT NULL,
  actor_identity TEXT NOT NULL,
  device_id BLOB NOT NULL CHECK(length(device_id)=16),
  origin_step_id BLOB CHECK(origin_step_id IS NULL OR length(origin_step_id)=16),
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL CHECK(descriptor_version>0),
  target_ref TEXT NOT NULL,
  canonical_parameters_artifact_id BLOB NOT NULL CHECK(length(canonical_parameters_artifact_id)=16),
  parameter_digest TEXT NOT NULL CHECK(length(parameter_digest)=64),
  expected_effects_ref TEXT NOT NULL,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  risk_class TEXT NOT NULL CHECK(risk_class IN ('R0','R1','R2','R3','R4','R5')),
  policy_version_ref TEXT NOT NULL,
  approval_request_id BLOB CHECK(approval_request_id IS NULL OR length(approval_request_id)=16),
  deadline_at_ms INTEGER,
  resource_budget_json TEXT NOT NULL CHECK(json_valid(resource_budget_json)),
  canonicalization_version TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE operation_attempts (
  attempt_id BLOB PRIMARY KEY CHECK(length(attempt_id)=16),
  operation_id BLOB NOT NULL REFERENCES operations(operation_id),
  attempt_number INTEGER NOT NULL CHECK(attempt_number>0),
  state TEXT NOT NULL CHECK(state IN
    ('prepared','dispatched','running','succeeded','failed','uncertain',
     'reconciling','compensation_required','compensating','compensated',
     'manual_intervention','cancelled')),
  idempotency_key TEXT NOT NULL,
  dispatched_at_ms INTEGER,
  finished_at_ms INTEGER,
  provider_receipt_ref TEXT,
  reported_effects_ref TEXT,
  verification_evidence_ref TEXT,
  error_ref TEXT,
  uncertainty_reason TEXT,
  reconciled_at_ms INTEGER,
  UNIQUE(operation_id,attempt_number),
  UNIQUE(operation_id,idempotency_key)
) STRICT;
CREATE INDEX idx_operation_attempt_state
  ON operation_attempts(state,dispatched_at_ms);

CREATE TABLE task_checkpoint_details (
  checkpoint_id BLOB PRIMARY KEY REFERENCES task_checkpoints(checkpoint_id),
  plan_id BLOB NOT NULL CHECK(length(plan_id)=16),
  plan_version INTEGER NOT NULL CHECK(plan_version>0),
  context_version_ref TEXT NOT NULL,
  capability_epoch_digest TEXT NOT NULL,
  dependency_state_digest TEXT NOT NULL,
  pending_steps_json TEXT NOT NULL CHECK(json_valid(pending_steps_json)),
  resume_conditions_json TEXT NOT NULL CHECK(json_valid(resume_conditions_json)),
  invalidation_reason TEXT,
  created_at_ms INTEGER NOT NULL
) STRICT;

ALTER TABLE task_runs
  ADD COLUMN revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>0);
