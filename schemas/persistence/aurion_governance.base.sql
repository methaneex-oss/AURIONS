-- AURIONS proposed SQLite DDL. NOT EXECUTED OR VALIDATED.
-- Store: aurion_governance.db
-- Source: docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md, Section 26.4
-- Initial governance database schema

PRAGMA foreign_keys = ON;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE policies (
  policy_id BLOB PRIMARY KEY CHECK(length(policy_id)=16),
  policy_name TEXT NOT NULL,
  policy_version INTEGER NOT NULL CHECK(policy_version>0),
  policy_document_json TEXT NOT NULL CHECK(json_valid(policy_document_json)),
  protected INTEGER NOT NULL CHECK(protected IN (0,1)),
  active INTEGER NOT NULL CHECK(active IN (0,1)),
  created_at_ms INTEGER NOT NULL,
  UNIQUE(policy_name,policy_version)
) STRICT;
CREATE UNIQUE INDEX idx_policy_active ON policies(policy_name) WHERE active=1;

CREATE TABLE permissions (
  permission_id BLOB PRIMARY KEY CHECK(length(permission_id)=16),
  subject_id TEXT NOT NULL,
  capability_id TEXT NOT NULL,
  operation_scope_json TEXT NOT NULL CHECK(json_valid(operation_scope_json)),
  resource_scope_json TEXT NOT NULL CHECK(json_valid(resource_scope_json)),
  data_scope_json TEXT NOT NULL CHECK(json_valid(data_scope_json)),
  side_effect_scope_json TEXT NOT NULL CHECK(json_valid(side_effect_scope_json)),
  environment_scope_json TEXT NOT NULL CHECK(json_valid(environment_scope_json)),
  budget_json TEXT CHECK(budget_json IS NULL OR json_valid(budget_json)),
  valid_from_ms INTEGER NOT NULL,
  expires_at_ms INTEGER,
  grant_source TEXT NOT NULL,
  policy_id BLOB NOT NULL REFERENCES policies(policy_id),
  revoked_at_ms INTEGER,
  revocation_reason TEXT,
  created_at_ms INTEGER NOT NULL,
  CHECK(expires_at_ms IS NULL OR expires_at_ms>valid_from_ms)
) STRICT;
CREATE INDEX idx_permissions_lookup ON permissions(subject_id,capability_id,valid_from_ms,expires_at_ms);

CREATE TABLE approval_requests (
  request_id BLOB PRIMARY KEY CHECK(length(request_id)=16),
  operation_id BLOB NOT NULL CHECK(length(operation_id)=16),
  requester_id TEXT NOT NULL,
  operation_digest TEXT NOT NULL,
  operation_summary TEXT NOT NULL,
  risk_class TEXT NOT NULL CHECK(risk_class IN ('R0','R1','R2','R3','R4','R5')),
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  recipient_summary TEXT,
  policy_version_ref TEXT NOT NULL,
  requested_at_ms INTEGER NOT NULL,
  expires_at_ms INTEGER NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','approved','denied','expired','invalidated','revoked')),
  CHECK(expires_at_ms>requested_at_ms)
) STRICT;
CREATE INDEX idx_approval_expiry ON approval_requests(state,expires_at_ms);

CREATE TABLE approval_decisions (
  decision_id BLOB PRIMARY KEY CHECK(length(decision_id)=16),
  request_id BLOB NOT NULL UNIQUE REFERENCES approval_requests(request_id),
  authenticated_owner_ref TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('approved','denied')),
  approved_digest TEXT NOT NULL,
  decided_at_ms INTEGER NOT NULL,
  authentication_context_ref TEXT NOT NULL
) STRICT;

CREATE TABLE protected_changes (
  change_id BLOB PRIMARY KEY CHECK(length(change_id)=16),
  target_ref TEXT NOT NULL,
  old_version_ref TEXT NOT NULL,
  candidate_version_ref TEXT NOT NULL,
  approval_request_id BLOB NOT NULL REFERENCES approval_requests(request_id),
  validation_report_ref TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('proposed','validated','approved','activated','rolled_back','rejected')),
  created_at_ms INTEGER NOT NULL,
  activated_at_ms INTEGER,
  rolled_back_at_ms INTEGER
) STRICT;

CREATE TABLE governance_audit (
  audit_id BLOB PRIMARY KEY CHECK(length(audit_id)=16),
  actor_id TEXT NOT NULL,
  action TEXT NOT NULL,
  target_ref TEXT,
  decision TEXT,
  policy_version_ref TEXT,
  operation_id BLOB,
  request_id BLOB,
  details_digest TEXT NOT NULL,
  occurred_at_ms INTEGER NOT NULL,
  previous_record_digest TEXT,
  record_digest TEXT NOT NULL
) STRICT;
CREATE INDEX idx_governance_audit_time ON governance_audit(occurred_at_ms DESC);

CREATE TABLE provider_permissions (
  provider_permission_id BLOB PRIMARY KEY CHECK(length(provider_permission_id)=16),
  provider_id TEXT NOT NULL,
  capability_scope_json TEXT NOT NULL CHECK(json_valid(capability_scope_json)),
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  purpose_scope_json TEXT NOT NULL CHECK(json_valid(purpose_scope_json)),
  policy_id BLOB NOT NULL REFERENCES policies(policy_id),
  valid_from_ms INTEGER NOT NULL,
  expires_at_ms INTEGER,
  revoked_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  CHECK(expires_at_ms IS NULL OR expires_at_ms>valid_from_ms)
) STRICT;

CREATE TABLE data_disclosures (
  disclosure_id BLOB PRIMARY KEY CHECK(length(disclosure_id)=16),
  provider_id TEXT NOT NULL,
  purpose TEXT NOT NULL,
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  payload_digest TEXT NOT NULL,
  payload_ref TEXT,
  approval_request_id BLOB REFERENCES approval_requests(request_id),
  policy_version_ref TEXT NOT NULL,
  disclosed_at_ms INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('sent','blocked','failed','uncertain'))
) STRICT;
CREATE INDEX idx_disclosures_provider_time ON data_disclosures(provider_id,disclosed_at_ms DESC);
