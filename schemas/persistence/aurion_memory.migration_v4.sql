-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_memory.db
-- Proposed migration v4: open-world entity, situation, means and interaction lineage.
-- Cross-store references are stable textual references; no cross-database foreign keys.
-- JSON arrays/objects are validated structurally here; semantic reference resolution belongs to application validation.

CREATE TABLE world_entities (
  entity_id TEXT NOT NULL,
  owner_ref TEXT NOT NULL,
  version INTEGER NOT NULL CHECK(version>0),
  identity_status TEXT NOT NULL,
  description TEXT NOT NULL,
  attributes_json TEXT NOT NULL CHECK(json_valid(attributes_json)),
  scope_json TEXT NOT NULL CHECK(json_valid(scope_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  observed_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  PRIMARY KEY(entity_id,version)
) STRICT;
CREATE INDEX idx_world_entities_owner_time
  ON world_entities(owner_ref,recorded_at_ms DESC);
CREATE INDEX idx_world_entities_identity
  ON world_entities(owner_ref,identity_status,entity_id);

CREATE TABLE world_relationships (
  relationship_id TEXT NOT NULL,
  owner_ref TEXT NOT NULL,
  version INTEGER NOT NULL CHECK(version>0),
  subject_ref TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_ref TEXT NOT NULL,
  epistemic_status TEXT NOT NULL,
  confidence REAL CHECK(confidence IS NULL OR (confidence>=0.0 AND confidence<=1.0)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  context_ref TEXT,
  valid_from_ms INTEGER NOT NULL,
  valid_until_ms INTEGER,
  recorded_at_ms INTEGER NOT NULL,
  PRIMARY KEY(relationship_id,version),
  CHECK(valid_until_ms IS NULL OR valid_until_ms>valid_from_ms)
) STRICT;
CREATE INDEX idx_world_relationship_subject
  ON world_relationships(owner_ref,subject_ref,predicate,valid_from_ms DESC);
CREATE INDEX idx_world_relationship_object
  ON world_relationships(owner_ref,object_ref,predicate,valid_from_ms DESC);

CREATE TABLE situation_snapshots (
  situation_id TEXT NOT NULL,
  owner_ref TEXT NOT NULL,
  version INTEGER NOT NULL CHECK(version>0),
  objective_refs_json TEXT NOT NULL CHECK(json_valid(objective_refs_json)),
  entity_refs_json TEXT NOT NULL CHECK(json_valid(entity_refs_json)),
  state_claims_json TEXT NOT NULL CHECK(json_valid(state_claims_json)),
  unknowns_json TEXT NOT NULL CHECK(json_valid(unknowns_json)),
  conflicts_json TEXT NOT NULL CHECK(json_valid(conflicts_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  context_ref TEXT,
  observed_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  PRIMARY KEY(situation_id,version)
) STRICT;
CREATE INDEX idx_situation_owner_recorded
  ON situation_snapshots(owner_ref,recorded_at_ms DESC);

CREATE TABLE affordance_hypotheses (
  hypothesis_id TEXT NOT NULL,
  owner_ref TEXT NOT NULL,
  version INTEGER NOT NULL CHECK(version>0),
  objective_ref TEXT NOT NULL,
  actor_refs_json TEXT NOT NULL CHECK(json_valid(actor_refs_json)),
  resource_refs_json TEXT NOT NULL CHECK(json_valid(resource_refs_json)),
  interaction_description TEXT NOT NULL,
  preconditions_json TEXT NOT NULL CHECK(json_valid(preconditions_json)),
  expected_effects_json TEXT NOT NULL CHECK(json_valid(expected_effects_json)),
  authority_requirements_json TEXT NOT NULL CHECK(json_valid(authority_requirements_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  confidence REAL NOT NULL CHECK(confidence>=0.0 AND confidence<=1.0),
  status TEXT NOT NULL,
  scope_json TEXT NOT NULL CHECK(json_valid(scope_json)),
  limitations_json TEXT NOT NULL CHECK(json_valid(limitations_json)),
  composition_refs_json TEXT NOT NULL CHECK(json_valid(composition_refs_json)),
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(hypothesis_id,version)
) STRICT;
CREATE INDEX idx_affordance_owner_objective
  ON affordance_hypotheses(owner_ref,objective_ref,status);

CREATE TABLE interaction_proposals (
  interaction_id TEXT PRIMARY KEY,
  owner_ref TEXT NOT NULL,
  objective_ref TEXT NOT NULL,
  actor_ref TEXT NOT NULL,
  target_refs_json TEXT NOT NULL CHECK(json_valid(target_refs_json)),
  means_hypothesis_refs_json TEXT NOT NULL CHECK(json_valid(means_hypothesis_refs_json)),
  proposed_effects_json TEXT NOT NULL CHECK(json_valid(proposed_effects_json)),
  authority_context_ref TEXT,
  risk_assessment_json TEXT NOT NULL CHECK(json_valid(risk_assessment_json)),
  precondition_evidence_refs_json TEXT NOT NULL CHECK(json_valid(precondition_evidence_refs_json)),
  status TEXT NOT NULL,
  authorization_ref TEXT,
  execution_operation_ref TEXT,
  proposed_at_ms INTEGER NOT NULL,
  deadline_at_ms INTEGER
) STRICT;
CREATE INDEX idx_interaction_proposals_owner_status
  ON interaction_proposals(owner_ref,status,proposed_at_ms DESC);

CREATE TABLE interaction_outcomes (
  outcome_id TEXT PRIMARY KEY,
  interaction_ref TEXT NOT NULL,
  owner_ref TEXT NOT NULL,
  result_status TEXT NOT NULL,
  observed_effects_json TEXT NOT NULL CHECK(json_valid(observed_effects_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  unresolved_effects_json TEXT NOT NULL CHECK(json_valid(unresolved_effects_json)),
  attribution_json TEXT NOT NULL CHECK(json_valid(attribution_json)),
  side_effects_json TEXT NOT NULL CHECK(json_valid(side_effects_json)),
  observed_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL
) STRICT;
CREATE INDEX idx_interaction_outcomes_owner_time
  ON interaction_outcomes(owner_ref,recorded_at_ms DESC);
CREATE INDEX idx_interaction_outcomes_interaction
  ON interaction_outcomes(interaction_ref,recorded_at_ms DESC);
