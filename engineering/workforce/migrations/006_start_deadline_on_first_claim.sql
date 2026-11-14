-- Start max_duration_minutes at first claim, not task creation. Queued role tasks
-- may wait behind earlier sequential roles; the absolute contract deadline still applies.
ALTER TABLE wf_tasks
    ADD COLUMN IF NOT EXISTS started_at timestamptz;

DROP FUNCTION IF EXISTS wf_task_deadline(timestamptz, jsonb);
CREATE OR REPLACE FUNCTION wf_task_deadline(
    task_started_at timestamptz,
    task_contract jsonb
)
RETURNS timestamptz
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE
        WHEN task_started_at IS NULL THEN
            CASE
                WHEN COALESCE(task_contract->>'deadline', 'UNSET') = 'UNSET'
                    THEN 'infinity'::timestamptz
                ELSE (task_contract->>'deadline')::timestamptz
            END
        ELSE LEAST(
            task_started_at + make_interval(mins => (task_contract->>'max_duration_minutes')::int),
            CASE
                WHEN COALESCE(task_contract->>'deadline', 'UNSET') = 'UNSET'
                    THEN 'infinity'::timestamptz
                ELSE (task_contract->>'deadline')::timestamptz
            END
        )
    END;
$$;

CREATE OR REPLACE FUNCTION wf_task_absolute_deadline(task_contract jsonb)
RETURNS timestamptz
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT CASE
        WHEN COALESCE(task_contract->>'deadline', 'UNSET') = 'UNSET'
            THEN 'infinity'::timestamptz
        ELSE (task_contract->>'deadline')::timestamptz
    END;
$$;

COMMENT ON FUNCTION wf_task_deadline(timestamptz, jsonb) IS
    'Returns the absolute deadline while queued, then the earlier of the absolute deadline and max_duration_minutes from first claim.';
COMMENT ON FUNCTION wf_task_absolute_deadline(jsonb) IS
    'Returns the absolute contract deadline or infinity when no absolute deadline was configured.';
