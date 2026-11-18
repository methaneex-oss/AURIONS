-- Proposed additive migration v7 for aurion_memory.db.
-- Add explicit persisted sources required by the query result contracts.
-- Legacy rows remain nullable/unresolved; do not infer missing provenance or confidence.
-- New writes must populate the fields enforced by the insert guards below.

ALTER TABLE capability_descriptors ADD COLUMN descriptor_schema_version TEXT;
CREATE INDEX idx_capability_descriptor_schema
  ON capability_descriptors(descriptor_schema_version);

CREATE TRIGGER capability_descriptors_require_schema_version
BEFORE INSERT ON capability_descriptors
WHEN NEW.descriptor_schema_version IS NULL OR length(NEW.descriptor_schema_version)=0
BEGIN
  SELECT RAISE(ABORT,'capability_descriptors.schema_version_required');
END;

ALTER TABLE representations ADD COLUMN method_version TEXT;
ALTER TABLE representations ADD COLUMN source_refs_json TEXT
  CHECK(source_refs_json IS NULL OR json_valid(source_refs_json));

CREATE TRIGGER representations_require_projection_lineage
BEFORE INSERT ON representations
WHEN NEW.method_version IS NULL OR length(NEW.method_version)=0
  OR NEW.source_refs_json IS NULL
BEGIN
  SELECT RAISE(ABORT,'representations.projection_lineage_required');
END;

ALTER TABLE contexts ADD COLUMN provenance_refs_json TEXT
  CHECK(provenance_refs_json IS NULL OR json_valid(provenance_refs_json));
ALTER TABLE contexts ADD COLUMN uncertainty_json TEXT
  CHECK(uncertainty_json IS NULL OR json_valid(uncertainty_json));

CREATE TRIGGER contexts_require_projection_lineage
BEFORE INSERT ON contexts
WHEN NEW.provenance_refs_json IS NULL OR NEW.uncertainty_json IS NULL
BEGIN
  SELECT RAISE(ABORT,'contexts.projection_lineage_required');
END;

ALTER TABLE memory_records ADD COLUMN provenance_refs_json TEXT
  CHECK(provenance_refs_json IS NULL OR json_valid(provenance_refs_json));
ALTER TABLE memory_records ADD COLUMN uncertainty_json TEXT
  CHECK(uncertainty_json IS NULL OR json_valid(uncertainty_json));

CREATE TRIGGER memory_records_require_projection_lineage
BEFORE INSERT ON memory_records
WHEN NEW.provenance_refs_json IS NULL OR NEW.uncertainty_json IS NULL
BEGIN
  SELECT RAISE(ABORT,'memory_records.projection_lineage_required');
END;

ALTER TABLE predictions ADD COLUMN conditions_json TEXT
  CHECK(conditions_json IS NULL OR json_valid(conditions_json));
ALTER TABLE predictions ADD COLUMN confidence REAL
  CHECK(confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0);
ALTER TABLE predictions ADD COLUMN evidence_refs_json TEXT
  CHECK(evidence_refs_json IS NULL OR json_valid(evidence_refs_json));

CREATE TRIGGER predictions_require_projection_evidence
BEFORE INSERT ON predictions
WHEN NEW.conditions_json IS NULL OR NEW.evidence_refs_json IS NULL
BEGIN
  SELECT RAISE(ABORT,'predictions.projection_evidence_required');
END;

ALTER TABLE plans ADD COLUMN context_version_ref TEXT;
ALTER TABLE plans ADD COLUMN capability_epoch_digest TEXT;

CREATE TABLE environment_observations (
  observation_id TEXT PRIMARY KEY,
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  device_id TEXT NOT NULL CHECK(length(device_id)>0),
  environment_scope TEXT NOT NULL CHECK(length(environment_scope)>0),
  observed_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  source_id TEXT NOT NULL CHECK(length(source_id)>0),
  collection_method TEXT NOT NULL CHECK(length(collection_method)>0),
  collector_version TEXT NOT NULL CHECK(length(collector_version)>0),
  platform_context_json TEXT NOT NULL CHECK(json_valid(platform_context_json)),
  observed_facts_json TEXT NOT NULL CHECK(json_valid(observed_facts_json)),
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  limitations_json TEXT NOT NULL CHECK(json_valid(limitations_json)),
  validity_json TEXT CHECK(validity_json IS NULL OR json_valid(validity_json))
) STRICT;

CREATE INDEX idx_environment_observations_owner_time
  ON environment_observations(owner_ref,observed_at_ms DESC,observation_id);
CREATE INDEX idx_environment_observations_device_scope
  ON environment_observations(owner_ref,device_id,environment_scope,observed_at_ms DESC);
