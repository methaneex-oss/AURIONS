-- Proposed additive migration v6 for aurion_events.db.
-- Close integrity gaps in the durable cross-store saga coordinator ledger.

-- An operation's saga classification is part of its durable identity. Changing
-- it after creation must not disable saga-specific constraints.
CREATE TRIGGER operations_saga_type_immutable
BEFORE UPDATE OF operation_type ON operations
WHEN NEW.operation_type <> OLD.operation_type
  AND (
    OLD.operation_type IN ('evolution.candidate.evaluate',
                           'evolution.candidate.activate',
                           'evolution.candidate.rollback')
    OR NEW.operation_type IN ('evolution.candidate.evaluate',
                               'evolution.candidate.activate',
                               'evolution.candidate.rollback')
  )
BEGIN
  SELECT RAISE(ABORT,'operations.saga_type_immutable');
END;

-- A compensation step must identify an earlier step in the same operation and
-- target the same authoritative store. A numeric reference alone is not proof.
CREATE TRIGGER operation_steps_compensation_reference_required
BEFORE INSERT ON operation_steps
WHEN NEW.compensation_for_step_number IS NOT NULL
  AND (SELECT operation_type FROM operations WHERE operation_id=NEW.operation_id)
    IN ('evolution.candidate.evaluate',
        'evolution.candidate.activate',
        'evolution.candidate.rollback')
  AND NOT EXISTS (
    SELECT 1 FROM operation_steps AS original
    WHERE original.operation_id=NEW.operation_id
      AND original.step_number=NEW.compensation_for_step_number
      AND original.step_number<NEW.step_number
      AND original.target_store=NEW.target_store
  )
BEGIN
  SELECT RAISE(ABORT,'operation_steps.compensation_reference_invalid');
END;

-- Terminal steps need both ends of their execution interval, whether they are
-- inserted terminal or transition to terminal later.
CREATE TRIGGER operation_steps_saga_terminal_timestamps_insert
BEFORE INSERT ON operation_steps
WHEN (SELECT operation_type FROM operations WHERE operation_id=NEW.operation_id)
  IN ('evolution.candidate.evaluate',
      'evolution.candidate.activate',
      'evolution.candidate.rollback')
  AND NEW.state IN ('succeeded','failed','rejected','expired','revoked','cancelled',
                    'compensated','manual_intervention')
  AND (NEW.started_at_ms IS NULL OR NEW.completed_at_ms IS NULL)
BEGIN
  SELECT RAISE(ABORT,'operation_steps.saga_terminal_timestamps_required');
END;

CREATE TRIGGER operation_steps_saga_terminal_timestamps_update
BEFORE UPDATE OF state,started_at_ms,completed_at_ms ON operation_steps
WHEN (SELECT operation_type FROM operations WHERE operation_id=NEW.operation_id)
  IN ('evolution.candidate.evaluate',
      'evolution.candidate.activate',
      'evolution.candidate.rollback')
  AND NEW.state IN ('succeeded','failed','rejected','expired','revoked','cancelled',
                    'compensated','manual_intervention')
  AND (NEW.started_at_ms IS NULL OR NEW.completed_at_ms IS NULL)
BEGIN
  SELECT RAISE(ABORT,'operation_steps.saga_terminal_timestamps_required');
END;

-- The journal's operation/step/store/transition identity is immutable; only
-- its state, timestamps and diagnostic evidence may advance.
CREATE TRIGGER recovery_journal_saga_identity_immutable
BEFORE UPDATE OF operation_id,operation_step_id,local_store,phase,intended_transition
ON recovery_journal
WHEN (SELECT operation_type FROM operations WHERE operation_id=OLD.operation_id)
  IN ('evolution.candidate.evaluate',
      'evolution.candidate.activate',
      'evolution.candidate.rollback')
  AND (
    NEW.operation_id IS NOT OLD.operation_id
    OR NEW.operation_step_id IS NOT OLD.operation_step_id
    OR NEW.local_store IS NOT OLD.local_store
    OR NEW.phase IS NOT OLD.phase
    OR NEW.intended_transition IS NOT OLD.intended_transition
  )
BEGIN
  SELECT RAISE(ABORT,'recovery_journal.saga_identity_immutable');
END;

-- Recovery journal rows are append-only evidence for saga reconciliation.
CREATE TRIGGER recovery_journal_saga_no_delete
BEFORE DELETE ON recovery_journal
WHEN (SELECT operation_type FROM operations WHERE operation_id=OLD.operation_id)
  IN ('evolution.candidate.evaluate',
      'evolution.candidate.activate',
      'evolution.candidate.rollback')
BEGIN
  SELECT RAISE(ABORT,'recovery_journal.saga_history_immutable');
END;


CREATE TRIGGER operations_saga_idempotency_required
BEFORE INSERT ON operations
WHEN NEW.operation_type IN ('evolution.candidate.evaluate',
                            'evolution.candidate.activate',
                            'evolution.candidate.rollback')
  AND (NEW.idempotency_key IS NULL OR length(NEW.idempotency_key)=0)
BEGIN
  SELECT RAISE(ABORT,'operations.saga_idempotency_required');
END;

-- Saga identity and deduplication keys are durable; they cannot be rewritten
-- or erased even before the first step has been appended.
CREATE TRIGGER operations_saga_identity_immutable
BEFORE UPDATE OF operation_id,idempotency_key,created_at_ms ON operations
WHEN OLD.operation_type IN ('evolution.candidate.evaluate',
                            'evolution.candidate.activate',
                            'evolution.candidate.rollback')
  AND (
    NEW.operation_id IS NOT OLD.operation_id
    OR NEW.idempotency_key IS NOT OLD.idempotency_key
    OR NEW.created_at_ms IS NOT OLD.created_at_ms
  )
BEGIN
  SELECT RAISE(ABORT,'operations.saga_identity_immutable');
END;

CREATE TRIGGER operations_saga_no_delete
BEFORE DELETE ON operations
WHEN OLD.operation_type IN ('evolution.candidate.evaluate',
                            'evolution.candidate.activate',
                            'evolution.candidate.rollback')
BEGIN
  SELECT RAISE(ABORT,'operations.saga_history_immutable');
END;
