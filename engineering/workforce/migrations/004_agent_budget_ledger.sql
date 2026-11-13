-- Persistent per-work-package/per-role inference budgets and crash-safe reservations.
CREATE TABLE IF NOT EXISTS wf_agent_budgets (
    work_package_id text NOT NULL,
    role text NOT NULL CHECK (role IN ('lead_builder','specialist_builder','architecture_reviewer','code_reviewer','negative_tester','integration_verifier')),
    max_model_calls integer NOT NULL CHECK (max_model_calls BETWEEN 1 AND 100),
    max_tokens bigint NOT NULL CHECK (max_tokens BETWEEN 1 AND 200000),
    used_model_calls integer NOT NULL DEFAULT 0 CHECK (used_model_calls >= 0),
    used_tokens bigint NOT NULL DEFAULT 0 CHECK (used_tokens >= 0),
    reserved_calls integer NOT NULL DEFAULT 0 CHECK (reserved_calls >= 0),
    reserved_tokens bigint NOT NULL DEFAULT 0 CHECK (reserved_tokens >= 0),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY(work_package_id, role)
);

CREATE TABLE IF NOT EXISTS wf_budget_reservations (
    reservation_id uuid PRIMARY KEY,
    task_id text NOT NULL REFERENCES wf_tasks(task_id),
    work_package_id text NOT NULL,
    role text NOT NULL,
    worker_id text NOT NULL,
    lease_generation bigint NOT NULL,
    lease_token_hash char(64) NOT NULL,
    reserved_tokens bigint NOT NULL CHECK (reserved_tokens > 0),
    actual_tokens bigint,
    state text NOT NULL CHECK (state IN ('RESERVED','SETTLED','RELEASED','ABANDONED','OVERRUN')),
    created_at timestamptz NOT NULL DEFAULT now(),
    settled_at timestamptz,
    FOREIGN KEY(work_package_id, role) REFERENCES wf_agent_budgets(work_package_id, role)
);
CREATE INDEX IF NOT EXISTS wf_budget_reservations_task_state_idx
    ON wf_budget_reservations(task_id, state, created_at);
