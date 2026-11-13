-- Proposed additive migration v5 for aurion_events.db.
-- Add a durable, ordered, idempotent step ledger for the three cross-store
-- evolution sagas. operation_steps remain coordinator-owned; each target-store
-- mutation is independently committed with its local outbox.

ALTER TABLE operation_steps ADD COLUMN step_key TEXT
  CHECK(step_key IS NULL OR length(step_key)>0);
ALTER TABLE operation_steps ADD COLUMN target_store TEXT
  CHECK(target_store IS NULL OR target_store IN
    ('aurion_memory.db','aurion_governance.db','aurion_events.db'));
ALTER TABLE operation_steps ADD COLUMN idempotency_key TEXT
  CHECK(idempotency_key IS NULL OR length(idempotency_key)>0);
ALTER TABLE operation_steps ADD COLUMN request_digest TEXT
  CHECK(request_digest IS NULL OR
    (length(request_digest)=64 AND request_digest NOT GLOB '*[^0-9a-f]*'));
ALTER TABLE operation_steps ADD COLUMN expected_revision INTEGER
  CHECK(expected_revision IS NULL OR expected_revision>=0);
ALTER TABLE operation_steps ADD COLUMN result_digest TEXT
  CHECK(result_digest IS NULL OR
    (length(result_digest)=64 AND result_digest NOT GLOB '*[^0-9a-f]*'));
ALTER TABLE operation_steps ADD COLUMN started_at_ms INTEGER;
ALTER TABLE operation_steps ADD COLUMN completed_at_ms INTEGER
  CHECK(completed_at_ms IS NULL OR started_at_ms IS NULL OR completed_at_ms>=started_at_ms);
ALTER TABLE operation_steps ADD COLUMN compensation_for_step_number INTEGER
  CHECK(compensation_for_step_number IS NULL OR
    (compensation_for_step_number>=0 AND compensation_for_step_number<>step_number));

CREATE UNIQUE INDEX idx_operation_steps_saga_key
  ON operation_steps(operation_id,step_key)
  WHERE step_key IS NOT NULL;
CREATE UNIQUE INDEX idx_operation_steps_target_idempotency
  ON operation_steps(target_store,idempotency_key)
  WHERE target_store IS NOT NULL AND idempotency_key IS NOT NULL;

CREATE TRIGGER operation_steps_require_saga_contract
BEFORE INSERT ON operation_steps
WHEN (SELECT operation_type FROM operations WHERE operation_id=NEW.operation_id)
  IN ('evolution.candidate.evaluate','evolution.candidate.activate','evolution.candidate.rollback')
  AND (
    NEW.step_key IS NULL OR NEW.target_store IS NULL OR
    NEW.idempotency_key IS NULL OR NEW.request_digest IS NULL
  )
BEGIN
  SELECT RAISE(ABORT,'operation_steps.saga_step_contract_required');
END;

CREATE TRIGGER operation_steps_saga_identity_immutable
BEFORE UPDATE OF operation_id,step_number,action_id,step_key,target_store,
                 idempotency_key,request_digest,expected_revision,
                 compensation_for_step_number
ON operation_steps
WHEN (SELECT operation_type FROM operations WHERE operation_id=OLD.operation_id)
  IN ('evolution.candidate.evaluate','evolution.candidate.activate','evolution.candidate.rollback')
BEGIN
  SELECT RAISE(ABORT,'operation_steps.saga_step_identity_immutable');
END;

CREATE TRIGGER operation_steps_saga_terminal_time_required
BEFORE UPDATE OF state ON operation_steps
WHEN (SELECT operation_type FROM operations WHERE operation_id=OLD.operation_id)
  IN ('evolution.candidate.evaluate','evolution.candidate.activate','evolution.candidate.rollback')
  AND NEW.state IN ('succeeded','failed','rejected','expired','revoked','cancelled',
                    'compensated','manual_intervention')
  AND NEW.completed_at_ms IS NULL
BEGIN
  SELECT RAISE(ABORT,'operation_steps.saga_terminal_time_required');
END;

CREATE TRIGGER operation_steps_saga_no_delete
BEFORE DELETE ON operation_steps
WHEN (SELECT operation_type FROM operations WHERE operation_id=OLD.operation_id)
  IN ('evolution.candidate.evaluate','evolution.candidate.activate','evolution.candidate.rollback')
BEGIN
  SELECT RAISE(ABORT,'operation_steps.saga_history_immutable');
END;

ALTER TABLE recovery_journal ADD COLUMN operation_step_id BLOB
  REFERENCES operation_steps(operation_step_id);
CREATE UNIQUE INDEX idx_recovery_journal_step
  ON recovery_journal(operation_step_id)
  WHERE operation_step_id IS NOT NULL;

CREATE TRIGGER recovery_journal_requires_saga_step
BEFORE INSERT ON recovery_journal
WHEN (SELECT operation_type FROM operations WHERE operation_id=NEW.operation_id)
  IN ('evolution.candidate.evaluate','evolution.candidate.activate','evolution.candidate.rollback')
  AND (
    NEW.operation_step_id IS NULL OR
    (SELECT operation_id FROM operation_steps
      WHERE operation_step_id=NEW.operation_step_id)<>NEW.operation_id OR
    (SELECT target_store FROM operation_steps
      WHERE operation_step_id=NEW.operation_step_id)<>NEW.local_store
  )
BEGIN
  SELECT RAISE(ABORT,'recovery_journal.saga_step_binding_required');
END;
