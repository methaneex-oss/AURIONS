-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_memory.db
-- Source: docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md, Section 26.5.2
-- Proposed plan execution and learning evidence migration v3

CREATE TABLE plan_step_contracts (
  step_id BLOB PRIMARY KEY REFERENCES plan_steps(step_id),
  step_role TEXT NOT NULL,
  role_schema_version TEXT NOT NULL,
  capability_id TEXT,
  descriptor_version INTEGER,
  input_binding_json TEXT NOT NULL CHECK(json_valid(input_binding_json)),
  preconditions_json TEXT NOT NULL CHECK(json_valid(preconditions_json)),
  expected_effects_json TEXT NOT NULL CHECK(json_valid(expected_effects_json)),
  resource_budget_json TEXT NOT NULL CHECK(json_valid(resource_budget_json)),
  verification_contract_json TEXT NOT NULL CHECK(json_valid(verification_contract_json)),
  stop_conditions_json TEXT NOT NULL CHECK(json_valid(stop_conditions_json)),
  stale_input_digest TEXT NOT NULL,
  contract_version TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  CHECK((capability_id IS NULL)=(descriptor_version IS NULL)),
  FOREIGN KEY(capability_id,descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version)
) STRICT;
CREATE INDEX idx_plan_step_capability
  ON plan_step_contracts(capability_id,descriptor_version)
  WHERE capability_id IS NOT NULL;

CREATE TABLE learning_update_details (
  learning_update_id BLOB PRIMARY KEY
    REFERENCES learning_updates(learning_update_id),
  update_kind TEXT NOT NULL CHECK(update_kind IN
    ('episodic_acquisition','belief_revision','capability_knowledge',
     'strategy_mechanism','model_training','architecture_evolution')),
  hypothesis_json TEXT NOT NULL CHECK(json_valid(hypothesis_json)),
  scope_json TEXT NOT NULL CHECK(json_valid(scope_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  baseline_artifact_id BLOB REFERENCES artifacts(artifact_id),
  candidate_artifact_id BLOB REFERENCES artifacts(artifact_id),
  evaluation_protocol_artifact_id BLOB REFERENCES artifacts(artifact_id),
  metrics_artifact_id BLOB REFERENCES artifacts(artifact_id),
  regression_artifact_id BLOB REFERENCES artifacts(artifact_id),
  rollback_ref TEXT,
  approval_ref TEXT,
  created_at_ms INTEGER NOT NULL
) STRICT;
