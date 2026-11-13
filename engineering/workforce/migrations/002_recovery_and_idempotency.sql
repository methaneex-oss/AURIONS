-- Add durable lease generations, bounded retries and idempotent checkpoint writes.
ALTER TABLE wf_tasks
    ADD COLUMN IF NOT EXISTS lease_generation bigint NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS attempt_count integer NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS max_attempts integer NOT NULL DEFAULT 3,
    ADD COLUMN IF NOT EXISTS retry_after timestamptz;

ALTER TABLE wf_checkpoints
    ADD COLUMN IF NOT EXISTS idempotency_key text;

CREATE UNIQUE INDEX IF NOT EXISTS wf_checkpoints_task_idempotency_idx
    ON wf_checkpoints(task_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS wf_tasks_retry_after_idx
    ON wf_tasks(retry_after) WHERE state='RETRY_WAIT';
