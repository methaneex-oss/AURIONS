-- Enforce the earlier of the task's absolute deadline and maximum lifetime.
CREATE OR REPLACE FUNCTION wf_task_deadline(task_created_at timestamptz, task_contract jsonb)
RETURNS timestamptz
LANGUAGE sql
IMMUTABLE
STRICT
AS $$
    SELECT LEAST(
        task_created_at + make_interval(mins => (task_contract->>'max_duration_minutes')::int),
        CASE
            WHEN COALESCE(task_contract->>'deadline', 'UNSET') = 'UNSET'
                THEN 'infinity'::timestamptz
            ELSE (task_contract->>'deadline')::timestamptz
        END
    );
$$;

COMMENT ON FUNCTION wf_task_deadline(timestamptz, jsonb) IS
    'Returns the earlier of the task absolute deadline and max_duration_minutes lifetime.';
