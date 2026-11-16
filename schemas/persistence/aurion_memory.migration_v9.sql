-- AURIONS proposed additive migration v9 for aurion_memory.db.
-- Immutable dataset manifests, source membership, split/seal evidence, admission
-- decisions and revocation-impact lineage. Governance authorization IDs are opaque
-- cross-store references and deliberately have no cross-database foreign keys.
-- All domain mutations publish through the memory-local outbox added in v5.

CREATE TABLE dataset_manifests (
  manifest_id BLOB PRIMARY KEY CHECK(length(manifest_id)=16),
  schema_version TEXT NOT NULL CHECK(length(schema_version)>0),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  model_family_ref TEXT NOT NULL CHECK(length(model_family_ref)>0),
  training_purpose TEXT NOT NULL CHECK(training_purpose IN
    ('foundation_pretraining','instruction_sft','preference_training','outcome_training','evaluation')),
  model_generation_ref TEXT NOT NULL CHECK(length(model_generation_ref)>0),
  tokenizer_artifact_ref TEXT NOT NULL CHECK(length(tokenizer_artifact_ref)>0),
  manifest_artifact_ref TEXT NOT NULL CHECK(length(manifest_artifact_ref)>0),
  preprocessing_pipeline_ref TEXT NOT NULL CHECK(length(preprocessing_pipeline_ref)>0),
  preprocessing_config_digest TEXT NOT NULL CHECK(length(preprocessing_config_digest)=64 AND preprocessing_config_digest NOT GLOB '*[^0-9a-f]*'),
  deduplication_report_ref TEXT NOT NULL CHECK(length(deduplication_report_ref)>0),
  quality_report_ref TEXT NOT NULL CHECK(length(quality_report_ref)>0),
  language_domain_classification_ref TEXT NOT NULL CHECK(length(language_domain_classification_ref)>0),
  curriculum_config_ref TEXT NOT NULL CHECK(length(curriculum_config_ref)>0),
  curriculum_config_digest TEXT NOT NULL CHECK(length(curriculum_config_digest)=64 AND curriculum_config_digest NOT GLOB '*[^0-9a-f]*'),
  manifest_digest TEXT NOT NULL CHECK(length(manifest_digest)=64 AND manifest_digest NOT GLOB '*[^0-9a-f]*'),
  rights_policy_snapshot_ref TEXT NOT NULL CHECK(length(rights_policy_snapshot_ref)>0),
  rights_policy_snapshot_digest TEXT NOT NULL CHECK(length(rights_policy_snapshot_digest)=64 AND rights_policy_snapshot_digest NOT GLOB '*[^0-9a-f]*'),
  lifecycle TEXT NOT NULL CHECK(lifecycle IN ('sealed','superseded','quarantined','revoked_impact_pending')),
  derived_artifact_refs_json TEXT NOT NULL CHECK(json_valid(derived_artifact_refs_json) AND json_type(derived_artifact_refs_json)='array'),
  authorization_evaluated_at_ms INTEGER NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE(manifest_id,manifest_digest)
) STRICT;
CREATE INDEX idx_dataset_manifests_owner_purpose
  ON dataset_manifests(owner_ref,model_family_ref,training_purpose,created_at_ms DESC);

CREATE TABLE dataset_manifest_sources (
  manifest_id BLOB NOT NULL REFERENCES dataset_manifests(manifest_id),
  source_ref TEXT NOT NULL CHECK(length(source_ref)>0),
  source_content_sha256 TEXT NOT NULL CHECK(length(source_content_sha256)=64 AND source_content_sha256 NOT GLOB '*[^0-9a-f]*'),
  authorization_id BLOB NOT NULL CHECK(length(authorization_id)=16),
  authorization_record_digest TEXT NOT NULL CHECK(length(authorization_record_digest)=64 AND authorization_record_digest NOT GLOB '*[^0-9a-f]*'),
  license_or_terms_digest TEXT NOT NULL CHECK(length(license_or_terms_digest)=64 AND license_or_terms_digest NOT GLOB '*[^0-9a-f]*'),
  source_artifact_ref TEXT NOT NULL CHECK(length(source_artifact_ref)>0),
  transformation_lineage_refs_json TEXT NOT NULL CHECK(json_valid(transformation_lineage_json) AND json_type(transformation_lineage_json)='array'),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  model_family_ref TEXT NOT NULL CHECK(length(model_family_ref)>0),
  PRIMARY KEY(manifest_id,source_ref)
) STRICT;
CREATE INDEX idx_dataset_manifest_sources_authorization
  ON dataset_manifest_sources(authorization_id,authorization_record_digest,manifest_id);

CREATE TABLE dataset_manifest_exclusions (
  manifest_id BLOB NOT NULL REFERENCES dataset_manifests(manifest_id),
  source_ref TEXT NOT NULL CHECK(length(source_ref)>0),
  reason TEXT NOT NULL CHECK(reason IN
    ('unknown_rights','denied','expired','revoked','incompatible_license','private_without_authorization',
     'duplicate','low_quality','evaluation_contamination','scope_mismatch','content_digest_mismatch')),
  evidence_ref TEXT,
  PRIMARY KEY(manifest_id,source_ref)
) STRICT;

CREATE TABLE dataset_manifest_splits (
  manifest_id BLOB NOT NULL REFERENCES dataset_manifests(manifest_id),
  split_type TEXT NOT NULL CHECK(split_type IN ('train','validation','held_out')),
  split_ref TEXT NOT NULL CHECK(length(split_ref)>0),
  split_digest TEXT NOT NULL CHECK(length(split_digest)=64 AND split_digest NOT GLOB '*[^0-9a-f]*'),
  PRIMARY KEY(manifest_id,split_type)
) STRICT;

CREATE TABLE dataset_manifest_seals (
  manifest_id BLOB PRIMARY KEY REFERENCES dataset_manifests(manifest_id),
  manifest_digest TEXT NOT NULL CHECK(length(manifest_digest)=64 AND manifest_digest NOT GLOB '*[^0-9a-f]*'),
  authorization_check_digest TEXT NOT NULL CHECK(length(authorization_check_digest)=64 AND authorization_check_digest NOT GLOB '*[^0-9a-f]*'),
  sealed_at_ms INTEGER NOT NULL,
  supervisor_ref TEXT NOT NULL CHECK(length(supervisor_ref)>0)
) STRICT;

CREATE TRIGGER dataset_manifest_sources_owner_scope
BEFORE INSERT ON dataset_manifest_sources
WHEN NOT EXISTS (
  SELECT 1 FROM dataset_manifests m
  WHERE m.manifest_id=NEW.manifest_id
    AND m.owner_ref=NEW.owner_ref
    AND m.model_family_ref=NEW.model_family_ref
)
BEGIN SELECT RAISE(ABORT,'dataset_manifest_sources.owner_model_scope_mismatch'); END;

CREATE TRIGGER dataset_manifest_seal_requires_complete_membership
BEFORE INSERT ON dataset_manifest_seals
WHEN NOT EXISTS (
  SELECT 1 FROM dataset_manifests m
  WHERE m.manifest_id=NEW.manifest_id AND m.manifest_digest=NEW.manifest_digest
)
 OR NOT EXISTS (SELECT 1 FROM dataset_manifest_sources s WHERE s.manifest_id=NEW.manifest_id)
 OR (SELECT count(*) FROM dataset_manifest_splits s WHERE s.manifest_id=NEW.manifest_id)<>3
 OR NOT EXISTS (SELECT 1 FROM dataset_manifest_splits s WHERE s.manifest_id=NEW.manifest_id AND s.split_type='train')
 OR NOT EXISTS (SELECT 1 FROM dataset_manifest_splits s WHERE s.manifest_id=NEW.manifest_id AND s.split_type='validation')
 OR NOT EXISTS (SELECT 1 FROM dataset_manifest_splits s WHERE s.manifest_id=NEW.manifest_id AND s.split_type='held_out')
BEGIN SELECT RAISE(ABORT,'dataset_manifest_seals.incomplete_manifest'); END;

CREATE TABLE dataset_manifest_lifecycle_events (
  lifecycle_event_id BLOB PRIMARY KEY CHECK(length(lifecycle_event_id)=16),
  manifest_id BLOB NOT NULL REFERENCES dataset_manifests(manifest_id),
  lifecycle_state TEXT NOT NULL CHECK(lifecycle_state IN ('superseded','quarantined','revoked_impact_pending')),
  evidence_ref TEXT NOT NULL CHECK(length(evidence_ref)>0),
  occurred_at_ms INTEGER NOT NULL
) STRICT;
CREATE INDEX idx_dataset_manifest_lifecycle
  ON dataset_manifest_lifecycle_events(manifest_id,occurred_at_ms DESC);

CREATE TABLE dataset_admission_decisions (
  admission_id BLOB PRIMARY KEY CHECK(length(admission_id)=16),
  manifest_id BLOB REFERENCES dataset_manifests(manifest_id),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  model_family_ref TEXT NOT NULL CHECK(length(model_family_ref)>0),
  training_purpose TEXT NOT NULL CHECK(training_purpose IN
    ('foundation_pretraining','instruction_sft','preference_training','outcome_training','evaluation')),
  outcome TEXT NOT NULL CHECK(outcome IN ('admitted','blocked')),
  denial_reason TEXT,
  authorization_id BLOB CHECK(authorization_id IS NULL OR length(authorization_id)=16),
  policy_version_ref TEXT NOT NULL CHECK(length(policy_version_ref)>0),
  worker_job_ref TEXT,
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json) AND json_type(evidence_refs_json)='array'),
  checked_at_ms INTEGER NOT NULL,
  CHECK(outcome<>'blocked' OR (denial_reason IS NOT NULL AND length(denial_reason)>0))
) STRICT;
CREATE INDEX idx_dataset_admission_owner_time
  ON dataset_admission_decisions(owner_ref,checked_at_ms DESC);

CREATE TRIGGER dataset_admission_scope_and_seal
BEFORE INSERT ON dataset_admission_decisions
WHEN NEW.manifest_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM dataset_manifests m
  WHERE m.manifest_id=NEW.manifest_id
    AND m.owner_ref=NEW.owner_ref
    AND m.model_family_ref=NEW.model_family_ref
    AND m.training_purpose=NEW.training_purpose
)
 OR (NEW.outcome='admitted' AND (
   NEW.manifest_id IS NULL OR NOT EXISTS (
     SELECT 1 FROM dataset_manifest_seals s WHERE s.manifest_id=NEW.manifest_id
   )
 ))
BEGIN SELECT RAISE(ABORT,'dataset_admission_decisions.scope_or_seal_required'); END;

CREATE TABLE dataset_revocation_impacts (
  impact_id BLOB PRIMARY KEY CHECK(length(impact_id)=16),
  revocation_ref TEXT NOT NULL CHECK(length(revocation_ref)>0),
  authorization_id BLOB NOT NULL CHECK(length(authorization_id)=16),
  authorization_record_digest TEXT NOT NULL CHECK(length(authorization_record_digest)=64 AND authorization_record_digest NOT GLOB '*[^0-9a-f]*'),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  operation_ref TEXT NOT NULL CHECK(length(operation_ref)>0),
  manifest_refs_json TEXT NOT NULL CHECK(json_valid(manifest_refs_json) AND json_type(manifest_refs_json)='array'),
  derived_artifact_refs_json TEXT NOT NULL CHECK(json_valid(derived_artifact_refs_json) AND json_type(derived_artifact_refs_json)='array'),
  active_attempt_refs_json TEXT NOT NULL CHECK(json_valid(active_attempt_refs_json) AND json_type(active_attempt_refs_json)='array'),
  influence_state TEXT NOT NULL CHECK(influence_state IN ('not_consumed','staged','consumed','unknown')),
  disposition TEXT NOT NULL CHECK(disposition IN
    ('no_affected_artifacts','quarantine','compliant_retraining','unlearning_assessment','rollback_assessment','manual_review')),
  findings_digest TEXT NOT NULL CHECK(length(findings_digest)=64 AND findings_digest NOT GLOB '*[^0-9a-f]*'),
  assessed_at_ms INTEGER NOT NULL,
  UNIQUE(revocation_ref,operation_ref)
) STRICT;
CREATE INDEX idx_dataset_revocation_impacts_authorization
  ON dataset_revocation_impacts(authorization_id,authorization_record_digest,assessed_at_ms DESC);

CREATE TRIGGER dataset_manifests_no_update
BEFORE UPDATE ON dataset_manifests
BEGIN SELECT RAISE(ABORT,'dataset_manifests.immutable_manifest'); END;
CREATE TRIGGER dataset_manifests_no_delete
BEFORE DELETE ON dataset_manifests
BEGIN SELECT RAISE(ABORT,'dataset_manifests.immutable_manifest'); END;
CREATE TRIGGER dataset_manifest_sources_no_update
BEFORE UPDATE ON dataset_manifest_sources
BEGIN SELECT RAISE(ABORT,'dataset_manifest_sources.immutable_membership'); END;
CREATE TRIGGER dataset_manifest_sources_no_delete
BEFORE DELETE ON dataset_manifest_sources
BEGIN SELECT RAISE(ABORT,'dataset_manifest_sources.immutable_membership'); END;
CREATE TRIGGER dataset_manifest_exclusions_no_update
BEFORE UPDATE ON dataset_manifest_exclusions
BEGIN SELECT RAISE(ABORT,'dataset_manifest_exclusions.immutable_exclusion'); END;
CREATE TRIGGER dataset_manifest_exclusions_no_delete
BEFORE DELETE ON dataset_manifest_exclusions
BEGIN SELECT RAISE(ABORT,'dataset_manifest_exclusions.immutable_exclusion'); END;
CREATE TRIGGER dataset_manifest_splits_no_update
BEFORE UPDATE ON dataset_manifest_splits
BEGIN SELECT RAISE(ABORT,'dataset_manifest_splits.immutable_split'); END;
CREATE TRIGGER dataset_manifest_splits_no_delete
BEFORE DELETE ON dataset_manifest_splits
BEGIN SELECT RAISE(ABORT,'dataset_manifest_splits.immutable_split'); END;
CREATE TRIGGER dataset_manifest_seals_no_update
BEFORE UPDATE ON dataset_manifest_seals
BEGIN SELECT RAISE(ABORT,'dataset_manifest_seals.immutable_seal'); END;
CREATE TRIGGER dataset_manifest_seals_no_delete
BEFORE DELETE ON dataset_manifest_seals
BEGIN SELECT RAISE(ABORT,'dataset_manifest_seals.immutable_seal'); END;
CREATE TRIGGER dataset_manifest_lifecycle_events_no_update
BEFORE UPDATE ON dataset_manifest_lifecycle_events
BEGIN SELECT RAISE(ABORT,'dataset_manifest_lifecycle_events.append_only'); END;
CREATE TRIGGER dataset_manifest_lifecycle_events_no_delete
BEFORE DELETE ON dataset_manifest_lifecycle_events
BEGIN SELECT RAISE(ABORT,'dataset_manifest_lifecycle_events.append_only'); END;
CREATE TRIGGER dataset_admission_decisions_no_update
BEFORE UPDATE ON dataset_admission_decisions
BEGIN SELECT RAISE(ABORT,'dataset_admission_decisions.append_only'); END;
CREATE TRIGGER dataset_admission_decisions_no_delete
BEFORE DELETE ON dataset_admission_decisions
BEGIN SELECT RAISE(ABORT,'dataset_admission_decisions.append_only'); END;
CREATE TRIGGER dataset_revocation_impacts_no_update
BEFORE UPDATE ON dataset_revocation_impacts
BEGIN SELECT RAISE(ABORT,'dataset_revocation_impacts.append_only'); END;
CREATE TRIGGER dataset_revocation_impacts_no_delete
BEFORE DELETE ON dataset_revocation_impacts
BEGIN SELECT RAISE(ABORT,'dataset_revocation_impacts.append_only'); END;
