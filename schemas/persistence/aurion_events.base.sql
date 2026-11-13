-- AURIONS proposed SQLite DDL. Host-side CI smoke execution verified; target Termux/Android validation pending.
-- Store: aurion_events.db
-- Source: docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md, Section 26.3
-- Initial event/recovery database schema

PRAGMA foreign_keys = ON;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE events (
  -- Assigned by this event store at durable append; never supplied by the producer.
  event_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id BLOB NOT NULL UNIQUE CHECK(length(event_id)=16),
  message_id BLOB NOT NULL UNIQUE CHECK(length(message_id)=16),
  message_type TEXT NOT NULL,
  contract_version TEXT NOT NULL,
  producer_component TEXT NOT NULL,
  producer_instance_id BLOB NOT NULL CHECK(length(producer_instance_id)=16),
  correlation_id BLOB NOT NULL CHECK(length(correlation_id)=16),
  causation_id BLOB CHECK(causation_id IS NULL OR length(causation_id)=16),
  occurred_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
  payload_digest TEXT NOT NULL,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  retention_class TEXT NOT NULL CHECK(retention_class IN ('operational','durable','audit','recovery'))
) STRICT;
CREATE INDEX idx_events_type_time ON events(message_type,occurred_at_ms DESC);
CREATE INDEX idx_events_correlation ON events(correlation_id,occurred_at_ms);

CREATE TABLE event_consumers (
  consumer_id TEXT PRIMARY KEY,
  -- Last committed local events.event_sequence consumed by this consumer.
  last_sequence INTEGER NOT NULL DEFAULT 0 CHECK(last_sequence>=0),
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE event_receipts (
  consumer_id TEXT NOT NULL REFERENCES event_consumers(consumer_id),
  message_id BLOB NOT NULL CHECK(length(message_id)=16),
  payload_digest TEXT NOT NULL,
  processed_at_ms INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('applied','duplicate','rejected','deferred')),
  diagnostic_ref TEXT,
  PRIMARY KEY(consumer_id,message_id)
) STRICT;

CREATE TABLE operations (
  operation_id BLOB PRIMARY KEY CHECK(length(operation_id)=16),
  operation_type TEXT NOT NULL,
  origin_goal_id BLOB CHECK(origin_goal_id IS NULL OR length(origin_goal_id)=16),
  origin_plan_id BLOB CHECK(origin_plan_id IS NULL OR length(origin_plan_id)=16),
  state TEXT NOT NULL CHECK(state IN
    ('proposed','validating','awaiting_approval','ready','dispatched','running','succeeded','failed','rejected','expired','revoked','cancel_requested','cancelled','uncertain','reconciling','compensation_required','compensating','compensated','manual_intervention')),
  idempotency_key TEXT,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  terminal_at_ms INTEGER
) STRICT;
CREATE UNIQUE INDEX idx_operation_idempotency ON operations(operation_type,idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE INDEX idx_operations_state ON operations(state,updated_at_ms);

CREATE TABLE operation_steps (
  operation_step_id BLOB PRIMARY KEY CHECK(length(operation_step_id)=16),
  operation_id BLOB NOT NULL REFERENCES operations(operation_id),
  step_number INTEGER NOT NULL CHECK(step_number>=0),
  action_id BLOB NOT NULL CHECK(length(action_id)=16),
  state TEXT NOT NULL CHECK(state IN
    ('pending','validating','awaiting_approval','ready','dispatched','running','succeeded','failed','rejected','expired','revoked','cancel_requested','cancelled','uncertain','reconciling','compensation_required','compensating','compensated','manual_intervention')),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
  result_ref TEXT,
  updated_at_ms INTEGER NOT NULL,
  UNIQUE(operation_id,step_number)
) STRICT;

CREATE TABLE recovery_journal (
  journal_id BLOB PRIMARY KEY CHECK(length(journal_id)=16),
  operation_id BLOB NOT NULL REFERENCES operations(operation_id),
  phase TEXT NOT NULL,
  local_store TEXT NOT NULL,
  local_record_ref TEXT,
  intended_transition TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','applied','compensated','manual_intervention')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  diagnostic_ref TEXT
) STRICT;
CREATE INDEX idx_recovery_pending ON recovery_journal(state,updated_at_ms)
  WHERE state IN ('pending','manual_intervention');

CREATE TABLE outbox (
  outbox_id BLOB PRIMARY KEY CHECK(length(outbox_id)=16),
  message_id BLOB NOT NULL UNIQUE CHECK(length(message_id)=16),
  destination TEXT NOT NULL,
  envelope_json TEXT NOT NULL CHECK(json_valid(envelope_json)),
  state TEXT NOT NULL CHECK(state IN ('pending','published','dead_letter')),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
  next_attempt_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  published_at_ms INTEGER,
  last_error_ref TEXT
) STRICT;
CREATE INDEX idx_outbox_dispatch ON outbox(state,next_attempt_at_ms);

CREATE TABLE task_runs (
  task_run_id BLOB PRIMARY KEY CHECK(length(task_run_id)=16),
  task_definition_ref TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN
    ('queued','running','paused','completed','failed','cancelled','blocked','lost')),
  priority REAL NOT NULL,
  budget_json TEXT NOT NULL CHECK(json_valid(budget_json)),
  created_at_ms INTEGER NOT NULL,
  started_at_ms INTEGER,
  updated_at_ms INTEGER NOT NULL,
  completed_at_ms INTEGER
) STRICT;

CREATE TABLE task_checkpoints (
  checkpoint_id BLOB PRIMARY KEY CHECK(length(checkpoint_id)=16),
  task_run_id BLOB NOT NULL REFERENCES task_runs(task_run_id),
  sequence INTEGER NOT NULL CHECK(sequence>=0),
  checkpoint_ref TEXT NOT NULL,
  state_digest TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE(task_run_id,sequence)
) STRICT;
