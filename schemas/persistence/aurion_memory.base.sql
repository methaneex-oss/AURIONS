-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_memory.db
-- Source: docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md, Section 26.2
-- Initial memory database schema

PRAGMA foreign_keys = ON;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE experiences (
  experience_id BLOB PRIMARY KEY CHECK(length(experience_id)=16),
  source_type TEXT NOT NULL,
  observed_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  content_ref TEXT NOT NULL,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  provenance_ref TEXT NOT NULL,
  retention_state TEXT NOT NULL CHECK(retention_state IN
    ('active','archived','pending_deletion','deleted_active','backup_expiry_pending')),
  deleted_at_ms INTEGER
) STRICT;
CREATE INDEX idx_experiences_time ON experiences(observed_at_ms DESC);
CREATE INDEX idx_experiences_retention ON experiences(retention_state,recorded_at_ms);

CREATE TABLE representations (
  representation_id BLOB PRIMARY KEY CHECK(length(representation_id)=16),
  experience_id BLOB NOT NULL REFERENCES experiences(experience_id),
  representation_type TEXT NOT NULL,
  content_json TEXT NOT NULL CHECK(json_valid(content_json)),
  method TEXT NOT NULL,
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  created_at_ms INTEGER NOT NULL
) STRICT;
CREATE INDEX idx_representations_experience ON representations(experience_id);

CREATE TABLE contexts (
  context_id BLOB NOT NULL CHECK(length(context_id)=16),
  version INTEGER NOT NULL CHECK(version>0),
  scope TEXT NOT NULL,
  valid_from_ms INTEGER NOT NULL,
  valid_until_ms INTEGER,
  attributes_json TEXT NOT NULL CHECK(json_valid(attributes_json)),
  provenance_ref TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(context_id,version),
  CHECK(valid_until_ms IS NULL OR valid_until_ms>valid_from_ms)
) STRICT;

CREATE TABLE memory_records (
  memory_id BLOB PRIMARY KEY CHECK(length(memory_id)=16),
  memory_type TEXT NOT NULL,
  content_ref TEXT NOT NULL,
  summary TEXT,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  status TEXT NOT NULL CHECK(status IN ('active','archived','pending_deletion','deleted_active')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  last_accessed_at_ms INTEGER,
  retention_until_ms INTEGER,
  deleted_at_ms INTEGER
) STRICT;
CREATE INDEX idx_memory_status_type ON memory_records(status,memory_type);
CREATE INDEX idx_memory_retention ON memory_records(retention_until_ms)
  WHERE retention_until_ms IS NOT NULL;

CREATE TABLE memory_links (
  source_memory_id BLOB NOT NULL REFERENCES memory_records(memory_id),
  target_memory_id BLOB NOT NULL REFERENCES memory_records(memory_id),
  relation_type TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(source_memory_id,target_memory_id,relation_type),
  CHECK(source_memory_id<>target_memory_id)
) STRICT;

CREATE TABLE knowledge_items (
  knowledge_id BLOB PRIMARY KEY CHECK(length(knowledge_id)=16),
  proposition TEXT NOT NULL,
  domain TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('active','superseded','withdrawn')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE beliefs (
  belief_id BLOB PRIMARY KEY CHECK(length(belief_id)=16),
  knowledge_id BLOB NOT NULL REFERENCES knowledge_items(knowledge_id),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE belief_revisions (
  revision_id BLOB PRIMARY KEY CHECK(length(revision_id)=16),
  belief_id BLOB NOT NULL REFERENCES beliefs(belief_id),
  revision_number INTEGER NOT NULL CHECK(revision_number>0),
  previous_revision_id BLOB REFERENCES belief_revisions(revision_id),
  epistemic_status TEXT NOT NULL CHECK(epistemic_status IN
    ('provisional','supported','consolidated','disputed','withdrawn')),
  confidence REAL CHECK(confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
  revision_reason TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE(belief_id,revision_number),
  UNIQUE(belief_id,revision_id)
) STRICT;
CREATE INDEX idx_belief_revision_order ON belief_revisions(belief_id,revision_number DESC);

CREATE TABLE evidence_items (
  evidence_id BLOB PRIMARY KEY CHECK(length(evidence_id)=16),
  source_experience_id BLOB REFERENCES experiences(experience_id),
  source_ref TEXT NOT NULL,
  evidence_type TEXT NOT NULL,
  observed_at_ms INTEGER,
  recorded_at_ms INTEGER NOT NULL,
  reliability_json TEXT CHECK(reliability_json IS NULL OR json_valid(reliability_json))
) STRICT;

CREATE TABLE belief_revision_evidence (
  revision_id BLOB NOT NULL REFERENCES belief_revisions(revision_id),
  evidence_id BLOB NOT NULL REFERENCES evidence_items(evidence_id),
  stance TEXT NOT NULL CHECK(stance IN ('supports','contradicts','contextualizes')),
  relevance REAL CHECK(relevance IS NULL OR relevance BETWEEN 0.0 AND 1.0),
  PRIMARY KEY(revision_id,evidence_id,stance)
) STRICT;

CREATE TABLE predictions (
  prediction_id BLOB PRIMARY KEY CHECK(length(prediction_id)=16),
  subject_ref TEXT NOT NULL,
  expected_outcome_json TEXT NOT NULL CHECK(json_valid(expected_outcome_json)),
  evaluation_criteria_json TEXT NOT NULL CHECK(json_valid(evaluation_criteria_json)),
  horizon_end_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('open','partially_evaluated','evaluated','cancelled'))
) STRICT;

CREATE TABLE prediction_evaluations (
  evaluation_id BLOB PRIMARY KEY CHECK(length(evaluation_id)=16),
  prediction_id BLOB NOT NULL REFERENCES predictions(prediction_id),
  observed_outcome_ref TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN ('correct','partially_correct','incorrect','inconclusive')),
  evaluator TEXT NOT NULL,
  evaluated_at_ms INTEGER NOT NULL,
  details_json TEXT CHECK(details_json IS NULL OR json_valid(details_json))
) STRICT;

CREATE TABLE goals (
  goal_id BLOB PRIMARY KEY CHECK(length(goal_id)=16),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE goal_revisions (
  goal_id BLOB NOT NULL REFERENCES goals(goal_id),
  revision INTEGER NOT NULL CHECK(revision>0),
  description TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('proposed','active','paused','completed','abandoned','blocked')),
  priority REAL NOT NULL,
  constraints_json TEXT NOT NULL CHECK(json_valid(constraints_json)),
  reason_ref TEXT,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(goal_id,revision)
) STRICT;

CREATE TABLE plans (
  plan_id BLOB PRIMARY KEY CHECK(length(plan_id)=16),
  goal_id BLOB NOT NULL,
  goal_revision INTEGER NOT NULL,
  plan_version INTEGER NOT NULL CHECK(plan_version>0),
  status TEXT NOT NULL CHECK(status IN ('draft','ready','running','paused','completed','failed','superseded')),
  created_at_ms INTEGER NOT NULL,
  FOREIGN KEY(goal_id,goal_revision) REFERENCES goal_revisions(goal_id,revision),
  UNIQUE(goal_id,plan_version)
) STRICT;

CREATE TABLE plan_steps (
  step_id BLOB PRIMARY KEY CHECK(length(step_id)=16),
  plan_id BLOB NOT NULL REFERENCES plans(plan_id),
  sequence INTEGER NOT NULL CHECK(sequence>=0),
  description TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('pending','ready','running','completed','failed','skipped','blocked','awaiting_input','awaiting_permission','paused','cancelled','stale','superseded','uncertain','retry_wait')),
  action_id BLOB CHECK(action_id IS NULL OR length(action_id)=16),
  created_at_ms INTEGER NOT NULL,
  UNIQUE(plan_id,sequence)
) STRICT;

CREATE TABLE plan_step_dependencies (
  step_id BLOB NOT NULL REFERENCES plan_steps(step_id),
  depends_on_step_id BLOB NOT NULL REFERENCES plan_steps(step_id),
  PRIMARY KEY(step_id,depends_on_step_id),
  CHECK(step_id<>depends_on_step_id)
) STRICT;

CREATE TABLE learning_updates (
  learning_update_id BLOB PRIMARY KEY CHECK(length(learning_update_id)=16),
  mechanism TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN
    ('identified','proposed','evaluating','accepted','rejected','revised','deferred','rolled_back')),
  evidence_ref TEXT NOT NULL,
  baseline_ref TEXT,
  evaluation_ref TEXT,
  decision_reason TEXT,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  CHECK(updated_at_ms>=created_at_ms),
  CHECK(state NOT IN ('accepted','rolled_back') OR
        (baseline_ref IS NOT NULL AND evaluation_ref IS NOT NULL))
) STRICT;
CREATE INDEX idx_learning_state ON learning_updates(state,updated_at_ms);

CREATE TABLE retention_jobs (
  retention_job_id BLOB PRIMARY KEY CHECK(length(retention_job_id)=16),
  subject_type TEXT NOT NULL,
  subject_id BLOB NOT NULL,
  requested_at_ms INTEGER NOT NULL,
  active_deleted_at_ms INTEGER,
  index_cleanup_at_ms INTEGER,
  sync_cleanup_at_ms INTEGER,
  backup_expiry_at_ms INTEGER,
  status TEXT NOT NULL CHECK(status IN ('queued','processing','waiting_backup_expiry','completed','failed')),
  failure_ref TEXT
) STRICT;
