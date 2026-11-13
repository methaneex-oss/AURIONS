CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS wf_tasks (
    task_id text PRIMARY KEY,
    role text NOT NULL CHECK (role IN ('lead_builder','specialist_builder','architecture_reviewer','code_reviewer','negative_tester','integration_verifier')),
    state text NOT NULL CHECK (state IN ('QUEUED','CLAIMED','RUNNING','CHECKPOINTED','CANDIDATE_READY','TESTING','REVIEWING','INTEGRATION','AWAITING_DIRECTOR','ACCEPTED','BLOCKED','RETRY_WAIT','FAILED','REJECTED','CANCELLED')),
    contract_json jsonb NOT NULL,
    base_commit_sha char(40) NOT NULL,
    lease_worker text,
    lease_token_hash char(64),
    lease_expires_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS wf_tasks_state_created_idx ON wf_tasks(state, created_at);
CREATE INDEX IF NOT EXISTS wf_tasks_lease_expiry_idx ON wf_tasks(lease_expires_at) WHERE lease_expires_at IS NOT NULL;

CREATE TABLE IF NOT EXISTS wf_checkpoints (
    checkpoint_id bigserial PRIMARY KEY,
    task_id text NOT NULL REFERENCES wf_tasks(task_id),
    worker_id text NOT NULL,
    checkpoint_name text NOT NULL,
    payload_json jsonb NOT NULL,
    context_sha256 char(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS wf_checkpoints_task_created_idx ON wf_checkpoints(task_id, created_at DESC);

CREATE TABLE IF NOT EXISTS wf_audit_events (
    audit_id bigserial PRIMARY KEY,
    task_id text NOT NULL REFERENCES wf_tasks(task_id),
    event_type text NOT NULL,
    actor text NOT NULL,
    payload_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS wf_audit_task_created_idx ON wf_audit_events(task_id, created_at);

CREATE OR REPLACE FUNCTION wf_reject_audit_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'workforce audit events are append-only';
END;
$$;
DROP TRIGGER IF EXISTS wf_audit_no_update ON wf_audit_events;
CREATE TRIGGER wf_audit_no_update BEFORE UPDATE OR DELETE ON wf_audit_events
FOR EACH ROW EXECUTE FUNCTION wf_reject_audit_mutation();
