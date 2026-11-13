-- Proposed additive migration v4 for aurion_events.db.
-- Preserve the exact failure and policy-decision references needed by read-only status projections.
-- Existing records remain NULL; no failure or policy decision is inferred retroactively.

ALTER TABLE task_runs ADD COLUMN failure_ref TEXT;
ALTER TABLE operation_details ADD COLUMN policy_decision_ref TEXT;
