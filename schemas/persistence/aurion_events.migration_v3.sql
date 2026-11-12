-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_events.db
-- Migration: v3 — owner binding and idempotent task-control receipts.
-- Prerequisite: aurion_events.base.sql and aurion_events.migration_v2.sql.
--
-- Existing task_runs rows are intentionally left owner-unbound (NULL). Do not
-- infer or bulk-assign ownership. An authorized migration procedure must bind
-- each legacy task to its verified owner before that task can be controlled.
-- New task creation must always provide a non-empty owner_id.

ALTER TABLE task_runs ADD COLUMN owner_id TEXT
  CHECK(owner_id IS NULL OR length(owner_id)>0);

CREATE INDEX idx_task_runs_owner_state
  ON task_runs(owner_id,state,updated_at_ms DESC);

-- Enforce owner binding for newly inserted task runs while retaining legacy
-- rows until their owner can be established from authoritative provenance.
CREATE TRIGGER task_runs_require_owner_insert
BEFORE INSERT ON task_runs
WHEN NEW.owner_id IS NULL OR length(NEW.owner_id)=0
BEGIN
  SELECT RAISE(ABORT,'task_runs.owner_id_required');
END;

-- The task-control idempotency ledger is local to aurion_events.db so receipt,
-- task revision transition, event append and outbox enqueue can share one
-- SQLite transaction. Receipts intentionally have no FK to task_runs:
-- deletion/retention policy must not erase deduplication evidence prematurely.
CREATE TABLE task_command_receipts (
  receipt_id BLOB PRIMARY KEY CHECK(length(receipt_id)=16),
  owner_id TEXT NOT NULL CHECK(length(owner_id)>0),
  actor_identity TEXT NOT NULL CHECK(length(actor_identity)>0),
  command_type TEXT NOT NULL CHECK(command_type IN
    ('task.start','task.pause','task.resume','task.cancel')),
  command_version TEXT NOT NULL CHECK(length(command_version)>0), -- Version syntax is enforced by the versioned contract validator.
  idempotency_key TEXT NOT NULL CHECK(length(idempotency_key)>0),
  request_digest TEXT NOT NULL CHECK(length(request_digest)=64),
  task_run_id BLOB NOT NULL CHECK(length(task_run_id)=16),
  command_response_json TEXT NOT NULL CHECK(json_valid(command_response_json)),
  recorded_at_ms INTEGER NOT NULL,
  UNIQUE(owner_id,actor_identity,command_type,command_version,idempotency_key)
) STRICT;

CREATE INDEX idx_task_command_receipts_task
  ON task_command_receipts(task_run_id,recorded_at_ms);
