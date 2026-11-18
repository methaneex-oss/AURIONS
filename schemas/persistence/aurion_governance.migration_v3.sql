-- Proposed additive migration v3 for aurion_governance.db.
-- Persist request owner/session lineage and make the explicit owner decision a
-- single-store, one-decision-per-request transition.

ALTER TABLE approval_requests ADD COLUMN owner_ref TEXT;
ALTER TABLE approval_requests ADD COLUMN owner_session_ref TEXT;

CREATE INDEX idx_approval_owner_state
  ON approval_requests(owner_ref,state,expires_at_ms);

CREATE TRIGGER trg_approval_request_requires_owner_session
BEFORE INSERT ON approval_requests
WHEN NEW.owner_ref IS NULL OR length(NEW.owner_ref)=0
  OR NEW.owner_session_ref IS NULL OR length(NEW.owner_session_ref)=0
BEGIN
  SELECT RAISE(ABORT,'approval_requests.owner_session_required');
END;

CREATE TRIGGER trg_approval_decision_requires_pending_exact_request
BEFORE INSERT ON approval_decisions
WHEN NOT EXISTS (
  SELECT 1 FROM approval_requests r
  WHERE r.request_id=NEW.request_id
    AND r.state='pending'
    AND r.owner_ref=NEW.authenticated_owner_ref
    AND r.operation_digest=NEW.approved_digest
    AND NEW.decided_at_ms>=r.requested_at_ms
    AND NEW.decided_at_ms<r.expires_at_ms
)
BEGIN
  SELECT RAISE(ABORT,'approval_decisions.request_owner_digest_state_or_expiry_mismatch');
END;

CREATE TRIGGER trg_approval_decision_advances_request_state
AFTER INSERT ON approval_decisions
BEGIN
  UPDATE approval_requests
  SET state=NEW.decision
  WHERE request_id=NEW.request_id AND state='pending';
END;

CREATE TRIGGER trg_approval_request_decision_state_requires_record
BEFORE UPDATE OF state ON approval_requests
WHEN NEW.state IN ('approved','denied')
  AND NOT EXISTS (
    SELECT 1 FROM approval_decisions d
    WHERE d.request_id=OLD.request_id AND d.decision=NEW.state
  )
BEGIN
  SELECT RAISE(ABORT,'approval_requests.decision_record_required');
END;
