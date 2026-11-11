-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_memory.db
-- Source: docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md, Section 26.5.1
-- Proposed additive capability and cognitive-state migration v2

CREATE TABLE artifacts (
  artifact_id BLOB PRIMARY KEY CHECK(length(artifact_id)=16),
  artifact_kind TEXT NOT NULL,
  logical_name TEXT NOT NULL,
  semantic_version TEXT,
  sha256 TEXT NOT NULL CHECK(length(sha256)=64),
  byte_size INTEGER NOT NULL CHECK(byte_size>=0),
  media_type TEXT NOT NULL,
  storage_uri TEXT NOT NULL,
  producer_id TEXT NOT NULL,
  producer_version TEXT NOT NULL,
  source_operation_id TEXT,
  provenance_ref TEXT NOT NULL,
  license_ref TEXT,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  retention_class TEXT NOT NULL,
  encryption_key_ref TEXT,
  validation_state TEXT NOT NULL CHECK(validation_state IN
    ('unvalidated','validated','rejected','quarantined')),
  availability_state TEXT NOT NULL CHECK(availability_state IN
    ('available','missing','corrupt','quarantined')),
  deletion_state TEXT NOT NULL CHECK(deletion_state IN
    ('active','pending_deletion','deleted_active','backup_expiry_pending')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  deleted_at_ms INTEGER,
  CHECK(updated_at_ms>=created_at_ms),
  CHECK(deleted_at_ms IS NULL OR deleted_at_ms>=created_at_ms),
  CHECK(deletion_state NOT IN ('pending_deletion','deleted_active','backup_expiry_pending') OR deleted_at_ms IS NOT NULL)
) STRICT;
CREATE INDEX idx_artifacts_hash ON artifacts(sha256);
CREATE INDEX idx_artifacts_kind_status ON artifacts(artifact_kind,validation_state,availability_state);
CREATE INDEX idx_artifacts_retention ON artifacts(retention_class,deletion_state);

CREATE TABLE artifact_lineage (
  parent_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
  child_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
  transformation_id TEXT NOT NULL,
  configuration_digest TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(parent_artifact_id,child_artifact_id,transformation_id),
  CHECK(parent_artifact_id<>child_artifact_id)
) STRICT;
CREATE INDEX idx_artifact_lineage_child ON artifact_lineage(child_artifact_id);

CREATE TABLE capability_descriptors (
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL CHECK(descriptor_version>0),
  provider_id TEXT NOT NULL,
  device_scope TEXT NOT NULL,
  discovery_epoch TEXT NOT NULL,
  descriptor_json TEXT NOT NULL CHECK(json_valid(descriptor_json)),
  descriptor_sha256 TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN
    ('discovered','unverified','verified','unavailable','permission_required',
     'revoked','stale','retired')),
  source_ref TEXT NOT NULL,
  first_discovered_at_ms INTEGER NOT NULL,
  last_verified_at_ms INTEGER,
  expires_at_ms INTEGER,
  PRIMARY KEY(capability_id,descriptor_version),
  CHECK(expires_at_ms IS NULL OR expires_at_ms>first_discovered_at_ms),
  CHECK(status<>'verified' OR last_verified_at_ms IS NOT NULL)
) STRICT;
CREATE INDEX idx_capability_status_freshness
  ON capability_descriptors(device_scope,status,expires_at_ms);

CREATE TABLE capability_discovery_evidence (
  discovery_evidence_id BLOB PRIMARY KEY CHECK(length(discovery_evidence_id)=16),
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL,
  source_experience_id BLOB REFERENCES experiences(experience_id),
  evidence_id BLOB REFERENCES evidence_items(evidence_id),
  discovery_method TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN ('supports','contradicts','inconclusive')),
  confidence REAL CHECK(confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
  observed_at_ms INTEGER NOT NULL,
  details_json TEXT NOT NULL CHECK(json_valid(details_json)),
  CHECK(source_experience_id IS NOT NULL OR evidence_id IS NOT NULL),
  FOREIGN KEY(capability_id,descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version)
) STRICT;
CREATE INDEX idx_capability_discovery_time
  ON capability_discovery_evidence(capability_id,observed_at_ms DESC);

CREATE TABLE capability_knowledge_revisions (
  knowledge_revision_id BLOB PRIMARY KEY CHECK(length(knowledge_revision_id)=16),
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL,
  revision_number INTEGER NOT NULL CHECK(revision_number>0),
  context_scope_json TEXT NOT NULL CHECK(json_valid(context_scope_json)),
  claims_json TEXT NOT NULL CHECK(json_valid(claims_json)),
  confidence_json TEXT NOT NULL CHECK(json_valid(confidence_json)),
  status TEXT NOT NULL CHECK(status IN
    ('provisional','supported','disputed','superseded','withdrawn')),
  created_at_ms INTEGER NOT NULL,
  FOREIGN KEY(capability_id,descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version),
  UNIQUE(capability_id,descriptor_version,revision_number)
) STRICT;

CREATE TABLE capability_knowledge_evidence (
  knowledge_revision_id BLOB NOT NULL
    REFERENCES capability_knowledge_revisions(knowledge_revision_id),
  evidence_id BLOB NOT NULL REFERENCES evidence_items(evidence_id),
  stance TEXT NOT NULL CHECK(stance IN ('supports','contradicts','contextualizes')),
  relevance REAL CHECK(relevance IS NULL OR relevance BETWEEN 0.0 AND 1.0),
  PRIMARY KEY(knowledge_revision_id,evidence_id,stance)
) STRICT;

CREATE TABLE capability_relationships (
  source_capability_id TEXT NOT NULL,
  source_descriptor_version INTEGER NOT NULL,
  target_capability_id TEXT NOT NULL,
  target_descriptor_version INTEGER NOT NULL,
  relation_type TEXT NOT NULL,
  conditions_json TEXT NOT NULL CHECK(json_valid(conditions_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(source_capability_id,source_descriptor_version,
               target_capability_id,target_descriptor_version,relation_type),
  FOREIGN KEY(source_capability_id,source_descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version),
  FOREIGN KEY(target_capability_id,target_descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version),
  CHECK(source_capability_id<>target_capability_id OR
        source_descriptor_version<>target_descriptor_version)
) STRICT;

CREATE TABLE appraisal_records (
  appraisal_id BLOB PRIMARY KEY CHECK(length(appraisal_id)=16),
  context_id BLOB NOT NULL,
  context_version INTEGER NOT NULL,
  assessment_json TEXT NOT NULL CHECK(json_valid(assessment_json)),
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  created_at_ms INTEGER NOT NULL,
  valid_until_ms INTEGER,
  FOREIGN KEY(context_id,context_version) REFERENCES contexts(context_id,version),
  CHECK(valid_until_ms IS NULL OR valid_until_ms>created_at_ms)
) STRICT;

CREATE TABLE reasoning_assessments (
  reasoning_id BLOB PRIMARY KEY CHECK(length(reasoning_id)=16),
  context_id BLOB NOT NULL,
  context_version INTEGER NOT NULL,
  hypothesis_ref TEXT,
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  conclusion_summary_ref TEXT,
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  created_at_ms INTEGER NOT NULL,
  FOREIGN KEY(context_id,context_version) REFERENCES contexts(context_id,version)
) STRICT;

CREATE TABLE decision_records (
  decision_id BLOB PRIMARY KEY CHECK(length(decision_id)=16),
  goal_id BLOB REFERENCES goals(goal_id),
  plan_id BLOB REFERENCES plans(plan_id),
  decision_type TEXT NOT NULL CHECK(decision_type IN
    ('selected','deferred','rejected','clarification_required','cancelled')),
  selected_option_ref TEXT,
  rationale_ref TEXT NOT NULL,
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  created_at_ms INTEGER NOT NULL,
  CHECK(decision_type<>'selected' OR selected_option_ref IS NOT NULL)
) STRICT;

CREATE TABLE outcome_evaluations (
  outcome_evaluation_id BLOB PRIMARY KEY CHECK(length(outcome_evaluation_id)=16),
  prediction_id BLOB REFERENCES predictions(prediction_id),
  plan_id BLOB REFERENCES plans(plan_id),
  operation_id BLOB CHECK(operation_id IS NULL OR length(operation_id)=16),
  expected_outcome_ref TEXT,
  observed_outcome_ref TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN
    ('verified','partially_verified','not_verified','failed','inconclusive')),
  evaluation_json TEXT NOT NULL CHECK(json_valid(evaluation_json)),
  created_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE self_model_revisions (
  self_model_revision_id BLOB PRIMARY KEY CHECK(length(self_model_revision_id)=16),
  revision_number INTEGER NOT NULL UNIQUE CHECK(revision_number>0),
  claims_json TEXT NOT NULL CHECK(json_valid(claims_json)),
  confidence_json TEXT NOT NULL CHECK(json_valid(confidence_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  created_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE evolution_proposals (
  proposal_id BLOB PRIMARY KEY CHECK(length(proposal_id)=16),
  target_mechanism TEXT NOT NULL,
  description TEXT NOT NULL,
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  impact_risk_json TEXT NOT NULL CHECK(json_valid(impact_risk_json)),
  candidate_artifact_ref TEXT,
  evaluation_ref TEXT,
  state TEXT NOT NULL CHECK(state IN
    ('proposed','isolated','evaluating','awaiting_approval','approved',
     'rejected','activated','rolled_back','deferred')),
  approval_ref TEXT,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  CHECK(state NOT IN ('approved','activated') OR approval_ref IS NOT NULL)
) STRICT;
CREATE INDEX idx_evolution_state ON evolution_proposals(state,updated_at_ms);
