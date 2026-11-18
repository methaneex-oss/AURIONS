-- Proposed additive migration v4 for aurion_governance.db.
-- Add exact owner, permission-state, approval and evidence fields required by
-- permission.inspect and audit.lookup. Legacy rows remain NULL and are not
-- assigned an owner or evidence by inference.

ALTER TABLE permissions ADD COLUMN owner_ref TEXT
  CHECK(owner_ref IS NULL OR length(owner_ref)>0);
ALTER TABLE permissions ADD COLUMN status TEXT
  CHECK(status IS NULL OR status IN ('active','revoked','expired','denied'));
ALTER TABLE permissions ADD COLUMN approval_ref TEXT;
ALTER TABLE permissions ADD COLUMN policy_version_ref TEXT;

CREATE INDEX idx_permissions_owner_status
  ON permissions(owner_ref,status,created_at_ms DESC);

CREATE TRIGGER permissions_require_projection_scope
BEFORE INSERT ON permissions
WHEN NEW.owner_ref IS NULL OR length(NEW.owner_ref)=0
  OR NEW.status IS NULL OR NEW.policy_version_ref IS NULL
  OR length(NEW.policy_version_ref)=0
BEGIN
  SELECT RAISE(ABORT,'permissions.owner_status_policy_required');
END;

ALTER TABLE governance_audit ADD COLUMN owner_ref TEXT
  CHECK(owner_ref IS NULL OR length(owner_ref)>0);
ALTER TABLE governance_audit ADD COLUMN evidence_refs_json TEXT
  CHECK(evidence_refs_json IS NULL OR json_valid(evidence_refs_json));
ALTER TABLE governance_audit ADD COLUMN correlation_id TEXT;

CREATE INDEX idx_governance_audit_owner_time
  ON governance_audit(owner_ref,occurred_at_ms DESC);

CREATE TRIGGER governance_audit_require_projection_evidence
BEFORE INSERT ON governance_audit
WHEN NEW.owner_ref IS NULL OR length(NEW.owner_ref)=0
  OR NEW.evidence_refs_json IS NULL OR NEW.correlation_id IS NULL
BEGIN
  SELECT RAISE(ABORT,'governance_audit.owner_evidence_correlation_required');
END;

ALTER TABLE data_disclosures ADD COLUMN owner_ref TEXT
  CHECK(owner_ref IS NULL OR length(owner_ref)>0);
ALTER TABLE data_disclosures ADD COLUMN evidence_refs_json TEXT
  CHECK(evidence_refs_json IS NULL OR json_valid(evidence_refs_json));
ALTER TABLE data_disclosures ADD COLUMN correlation_id TEXT;

CREATE INDEX idx_data_disclosures_owner_time
  ON data_disclosures(owner_ref,disclosed_at_ms DESC);

CREATE TRIGGER data_disclosures_require_projection_evidence
BEFORE INSERT ON data_disclosures
WHEN NEW.owner_ref IS NULL OR length(NEW.owner_ref)=0
  OR NEW.evidence_refs_json IS NULL OR NEW.correlation_id IS NULL
BEGIN
  SELECT RAISE(ABORT,'data_disclosures.owner_evidence_correlation_required');
END;
