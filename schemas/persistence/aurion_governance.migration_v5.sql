-- AURIONS proposed additive migration v5 for aurion_governance.db.
-- Immutable dataset-source authorization versions and append-only revocation evidence.
-- Each governance mutation publishes through the governance-local outbox added in v2.

CREATE TABLE dataset_source_authorizations (
  authorization_id BLOB PRIMARY KEY CHECK(length(authorization_id)=16),
  authorization_revision INTEGER NOT NULL CHECK(authorization_revision>0),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  source_ref TEXT NOT NULL CHECK(length(source_ref)>0),
  source_content_sha256 TEXT NOT NULL CHECK(length(source_content_sha256)=64 AND source_content_sha256 NOT GLOB '*[^0-9a-f]*'),
  source_origin_json TEXT NOT NULL CHECK(json_valid(source_origin_json) AND json_type(source_origin_json)='object'),
  rights_holder_ref TEXT,
  authorization_basis TEXT NOT NULL CHECK(authorization_basis IN
    ('license','contract','public_domain_determination','explicit_owner_authorization','statutory_exception')),
  license_or_terms_ref TEXT NOT NULL CHECK(length(license_or_terms_ref)>0),
  license_or_terms_digest TEXT NOT NULL CHECK(length(license_or_terms_digest)=64 AND license_or_terms_digest NOT GLOB '*[^0-9a-f]*'),
  permitted_purposes_json TEXT NOT NULL CHECK(json_valid(permitted_purposes_json) AND json_type(permitted_purposes_json)='array'),
  training_permission TEXT NOT NULL CHECK(training_permission IN ('allow','deny')),
  memory_retention_permission TEXT NOT NULL CHECK(memory_retention_permission IN ('allow','deny')),
  private_data_classification TEXT NOT NULL CHECK(private_data_classification IN ('public','private','personal','sensitive','confidential')),
  private_data_authorization_ref TEXT,
  project_ref TEXT NOT NULL CHECK(length(project_ref)>0),
  model_family_ref TEXT NOT NULL CHECK(length(model_family_ref)>0),
  dataset_scope_ref TEXT NOT NULL CHECK(length(dataset_scope_ref)>0),
  policy_version_ref TEXT NOT NULL CHECK(length(policy_version_ref)>0),
  valid_from_ms INTEGER NOT NULL,
  expires_at_ms INTEGER,
  decision_state TEXT NOT NULL CHECK(decision_state IN ('active','denied')),
  approval_request_id BLOB NOT NULL REFERENCES approval_requests(request_id),
  decision_ref TEXT NOT NULL CHECK(length(decision_ref)>0),
  supersedes_authorization_id BLOB CHECK(supersedes_authorization_id IS NULL OR length(supersedes_authorization_id)=16),
  created_at_ms INTEGER NOT NULL,
  record_digest TEXT NOT NULL CHECK(length(record_digest)=64 AND record_digest NOT GLOB '*[^0-9a-f]*'),
  UNIQUE(authorization_id,record_digest),
  UNIQUE(owner_ref,source_ref,source_content_sha256,authorization_revision),
  CHECK(expires_at_ms IS NULL OR expires_at_ms>valid_from_ms),
  CHECK(private_data_classification='public' OR
        (private_data_authorization_ref IS NOT NULL AND length(private_data_authorization_ref)>0)),
  CHECK(training_permission<>'allow' OR json_array_length(permitted_purposes_json)>0)
) STRICT;
CREATE INDEX idx_dataset_authorizations_source
  ON dataset_source_authorizations(owner_ref,source_ref,source_content_sha256,created_at_ms DESC);
CREATE INDEX idx_dataset_authorizations_scope
  ON dataset_source_authorizations(owner_ref,model_family_ref,dataset_scope_ref,decision_state,valid_from_ms,expires_at_ms);

CREATE TRIGGER dataset_source_authorizations_no_update
BEFORE UPDATE ON dataset_source_authorizations
BEGIN SELECT RAISE(ABORT,'dataset_source_authorizations.immutable_version'); END;
CREATE TRIGGER dataset_source_authorizations_no_delete
BEFORE DELETE ON dataset_source_authorizations
BEGIN SELECT RAISE(ABORT,'dataset_source_authorizations.immutable_version'); END;

CREATE TABLE dataset_source_authorization_revocations (
  revocation_id BLOB PRIMARY KEY CHECK(length(revocation_id)=16),
  authorization_id BLOB NOT NULL,
  authorization_record_digest TEXT NOT NULL CHECK(length(authorization_record_digest)=64 AND authorization_record_digest NOT GLOB '*[^0-9a-f]*'),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  actor_identity TEXT NOT NULL CHECK(length(actor_identity)>0),
  approval_request_id BLOB NOT NULL REFERENCES approval_requests(request_id),
  operation_id BLOB NOT NULL CHECK(length(operation_id)=16),
  reason_ref TEXT NOT NULL CHECK(length(reason_ref)>0),
  policy_version_ref TEXT NOT NULL CHECK(length(policy_version_ref)>0),
  revoked_at_ms INTEGER NOT NULL,
  revocation_digest TEXT NOT NULL CHECK(length(revocation_digest)=64 AND revocation_digest NOT GLOB '*[^0-9a-f]*'),
  UNIQUE(authorization_id,operation_id),
  FOREIGN KEY(authorization_id,authorization_record_digest)
    REFERENCES dataset_source_authorizations(authorization_id,record_digest)
) STRICT;
CREATE INDEX idx_dataset_authorization_revocations_lookup
  ON dataset_source_authorization_revocations(authorization_id,revoked_at_ms DESC);

CREATE TRIGGER dataset_source_revocations_owner_scope
BEFORE INSERT ON dataset_source_authorization_revocations
WHEN NOT EXISTS (
  SELECT 1 FROM dataset_source_authorizations a
  WHERE a.authorization_id=NEW.authorization_id
    AND a.record_digest=NEW.authorization_record_digest
    AND a.owner_ref=NEW.owner_ref
)
BEGIN SELECT RAISE(ABORT,'dataset_source_revocations.authorization_scope_mismatch'); END;
CREATE TRIGGER dataset_source_authorization_revocations_no_update
BEFORE UPDATE ON dataset_source_authorization_revocations
BEGIN SELECT RAISE(ABORT,'dataset_source_authorization_revocations.append_only'); END;
CREATE TRIGGER dataset_source_authorization_revocations_no_delete
BEFORE DELETE ON dataset_source_authorization_revocations
BEGIN SELECT RAISE(ABORT,'dataset_source_authorization_revocations.append_only'); END;
