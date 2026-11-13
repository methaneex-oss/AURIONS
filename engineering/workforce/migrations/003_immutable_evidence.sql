-- Bind every lifecycle gate to one append-only evidence digest and artifact reference.
CREATE TABLE IF NOT EXISTS wf_task_evidence (
    evidence_id bigserial PRIMARY KEY,
    task_id text NOT NULL REFERENCES wf_tasks(task_id),
    stage text NOT NULL CHECK (stage IN ('WORKER_OUTPUT','CANDIDATE','TEST','REVIEW_BUNDLE','INTEGRATED')),
    sha256 char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-fA-F]{64}$'),
    evidence_ref text NOT NULL CHECK (length(evidence_ref) BETWEEN 1 AND 512),
    actor text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(task_id, stage)
);
CREATE INDEX IF NOT EXISTS wf_task_evidence_task_created_idx
    ON wf_task_evidence(task_id, created_at DESC);

CREATE OR REPLACE FUNCTION wf_reject_evidence_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'workforce evidence records are append-only';
END;
$$;
DROP TRIGGER IF EXISTS wf_evidence_no_update ON wf_task_evidence;
CREATE TRIGGER wf_evidence_no_update BEFORE UPDATE OR DELETE ON wf_task_evidence
FOR EACH ROW EXECUTE FUNCTION wf_reject_evidence_mutation();
