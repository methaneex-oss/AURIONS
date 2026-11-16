-- PR-19/PR-20 model-candidate lifecycle persistence. Additive only.
ALTER TABLE learning_updates ADD COLUMN owner_ref TEXT;
ALTER TABLE artifacts ADD COLUMN owner_ref TEXT;
ALTER TABLE evolution_proposals ADD COLUMN owner_ref TEXT;

CREATE TRIGGER learning_updates_owner_required
BEFORE INSERT ON learning_updates
WHEN NEW.owner_ref IS NULL OR length(trim(NEW.owner_ref))=0
BEGIN SELECT RAISE(ABORT,'learning_updates.owner_ref_required'); END;

CREATE TRIGGER evolution_proposals_owner_required
BEFORE INSERT ON evolution_proposals
WHEN NEW.owner_ref IS NULL OR length(trim(NEW.owner_ref))=0
BEGIN SELECT RAISE(ABORT,'evolution_proposals.owner_ref_required'); END;

CREATE TABLE learning_experiments (
 experiment_id BLOB PRIMARY KEY CHECK(length(experiment_id)=16),
 learning_update_id BLOB NOT NULL REFERENCES learning_updates(learning_update_id),
 owner_ref TEXT NOT NULL,
 baseline_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 dataset_manifest_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 protocol_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 training_manifest_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 initialization_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 architecture_config_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 tokenizer_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 initialization_method TEXT NOT NULL CHECK(initialization_method IN ('random_initialization','prior_aurions_checkpoint')),
 dataset_split_ref TEXT NOT NULL,
 code_revision TEXT NOT NULL,
 configuration_digest TEXT NOT NULL CHECK(length(configuration_digest)=64 AND configuration_digest NOT GLOB '*[^0-9a-f]*'),
 random_seed TEXT NOT NULL,
 resource_budget_json TEXT NOT NULL CHECK(json_valid(resource_budget_json)),
 deadline_at_ms INTEGER NOT NULL,
 created_at_ms INTEGER NOT NULL,
 UNIQUE(experiment_id,learning_update_id,owner_ref)
) STRICT;
CREATE INDEX idx_learning_experiments_update ON learning_experiments(learning_update_id,created_at_ms);

CREATE TRIGGER learning_experiments_owner_scope
BEFORE INSERT ON learning_experiments
WHEN (SELECT owner_ref FROM learning_updates WHERE learning_update_id=NEW.learning_update_id) IS NOT NEW.owner_ref
 OR EXISTS (SELECT 1 FROM artifacts WHERE artifact_id IN
   (NEW.baseline_artifact_id,NEW.dataset_manifest_artifact_id,NEW.protocol_artifact_id,
    NEW.training_manifest_artifact_id,NEW.initialization_artifact_id,
    NEW.architecture_config_artifact_id,NEW.tokenizer_artifact_id)
   AND owner_ref IS NOT NEW.owner_ref)
BEGIN SELECT RAISE(ABORT,'learning_experiments.owner_scope_mismatch'); END;

CREATE TABLE learning_experiment_attempts (
 attempt_id BLOB PRIMARY KEY CHECK(length(attempt_id)=16),
 experiment_id BLOB NOT NULL,
 learning_update_id BLOB NOT NULL,
 owner_ref TEXT NOT NULL,
 job_id BLOB NOT NULL UNIQUE CHECK(length(job_id)=16),
 attempt_number INTEGER NOT NULL CHECK(attempt_number>0),
 configuration_digest TEXT NOT NULL CHECK(length(configuration_digest)=64 AND configuration_digest NOT GLOB '*[^0-9a-f]*'),
 state TEXT NOT NULL CHECK(state IN ('queued','running','completed','failed','cancelled','uncertain')),
 started_at_ms INTEGER,
 finished_at_ms INTEGER,
 candidate_artifact_id BLOB REFERENCES artifacts(artifact_id),
 failure_ref TEXT,
 UNIQUE(experiment_id,attempt_number),
 UNIQUE(attempt_id,experiment_id,learning_update_id,owner_ref),
 FOREIGN KEY(experiment_id,learning_update_id,owner_ref)
   REFERENCES learning_experiments(experiment_id,learning_update_id,owner_ref),
 CHECK(finished_at_ms IS NULL OR (started_at_ms IS NOT NULL AND finished_at_ms>=started_at_ms))
) STRICT;

CREATE TABLE learning_candidate_evaluations (
 evaluation_id BLOB PRIMARY KEY CHECK(length(evaluation_id)=16),
 learning_update_id BLOB NOT NULL,
 experiment_id BLOB NOT NULL,
 attempt_id BLOB NOT NULL,
 owner_ref TEXT NOT NULL,
 candidate_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 candidate_artifact_sha256 TEXT NOT NULL CHECK(length(candidate_artifact_sha256)=64 AND candidate_artifact_sha256 NOT GLOB '*[^0-9a-f]*'),
 baseline_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 baseline_artifact_sha256 TEXT NOT NULL CHECK(length(baseline_artifact_sha256)=64 AND baseline_artifact_sha256 NOT GLOB '*[^0-9a-f]*'),
 dataset_manifest_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 dataset_manifest_sha256 TEXT NOT NULL CHECK(length(dataset_manifest_sha256)=64 AND dataset_manifest_sha256 NOT GLOB '*[^0-9a-f]*'),
 evaluation_protocol_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 evaluation_protocol_sha256 TEXT NOT NULL CHECK(length(evaluation_protocol_sha256)=64 AND evaluation_protocol_sha256 NOT GLOB '*[^0-9a-f]*'),
 regression_suite_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 metrics_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 regression_results_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 unseen_controls_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 report_digest TEXT NOT NULL CHECK(length(report_digest)=64 AND report_digest NOT GLOB '*[^0-9a-f]*'),
 status TEXT NOT NULL CHECK(status IN ('passed','failed','inconclusive')),
 evaluated_at_ms INTEGER NOT NULL,
 UNIQUE(evaluation_id,learning_update_id,experiment_id,attempt_id,owner_ref),
 FOREIGN KEY(experiment_id,learning_update_id,owner_ref)
   REFERENCES learning_experiments(experiment_id,learning_update_id,owner_ref),
 FOREIGN KEY(attempt_id,experiment_id,learning_update_id,owner_ref)
   REFERENCES learning_experiment_attempts(attempt_id,experiment_id,learning_update_id,owner_ref)
) STRICT;
CREATE INDEX idx_learning_candidate_evaluations_lineage
 ON learning_candidate_evaluations(learning_update_id,experiment_id,attempt_id,evaluated_at_ms);

CREATE TRIGGER learning_candidate_evaluations_owner_scope
BEFORE INSERT ON learning_candidate_evaluations
WHEN EXISTS (SELECT 1 FROM artifacts WHERE artifact_id IN
 (NEW.candidate_artifact_id,NEW.baseline_artifact_id,NEW.dataset_manifest_artifact_id,
  NEW.evaluation_protocol_artifact_id,NEW.regression_suite_artifact_id,NEW.metrics_artifact_id,
  NEW.regression_results_artifact_id,NEW.unseen_controls_artifact_id)
 AND owner_ref IS NOT NEW.owner_ref)
BEGIN SELECT RAISE(ABORT,'learning_candidate_evaluations.owner_scope_mismatch'); END;

ALTER TABLE learning_update_details ADD COLUMN experiment_id BLOB REFERENCES learning_experiments(experiment_id);
ALTER TABLE learning_update_details ADD COLUMN attempt_id BLOB REFERENCES learning_experiment_attempts(attempt_id);
ALTER TABLE learning_update_details ADD COLUMN evaluation_id BLOB REFERENCES learning_candidate_evaluations(evaluation_id);

CREATE TRIGGER learning_update_details_lineage_match
BEFORE UPDATE OF experiment_id,attempt_id,evaluation_id ON learning_update_details
WHEN (NEW.experiment_id IS NOT NULL OR NEW.attempt_id IS NOT NULL OR NEW.evaluation_id IS NOT NULL)
 AND (NEW.experiment_id IS NULL OR NEW.attempt_id IS NULL OR NEW.evaluation_id IS NULL
 OR NOT EXISTS (SELECT 1 FROM learning_experiments e WHERE e.experiment_id=NEW.experiment_id AND e.learning_update_id=NEW.learning_update_id)
 OR NOT EXISTS (SELECT 1 FROM learning_experiment_attempts a WHERE a.attempt_id=NEW.attempt_id AND a.experiment_id=NEW.experiment_id AND a.learning_update_id=NEW.learning_update_id)
 OR NOT EXISTS (SELECT 1 FROM learning_candidate_evaluations v WHERE v.evaluation_id=NEW.evaluation_id AND v.experiment_id=NEW.experiment_id AND v.attempt_id=NEW.attempt_id AND v.learning_update_id=NEW.learning_update_id))
BEGIN SELECT RAISE(ABORT,'learning_update_details.lineage_mismatch'); END;

ALTER TABLE evolution_proposals ADD COLUMN candidate_id BLOB CHECK(candidate_id IS NULL OR length(candidate_id)=16);
ALTER TABLE evolution_proposals ADD COLUMN source_learning_update_id BLOB REFERENCES learning_updates(learning_update_id);
ALTER TABLE evolution_proposals ADD COLUMN source_experiment_id BLOB REFERENCES learning_experiments(experiment_id);
ALTER TABLE evolution_proposals ADD COLUMN source_attempt_id BLOB REFERENCES learning_experiment_attempts(attempt_id);
ALTER TABLE evolution_proposals ADD COLUMN learning_evaluation_id BLOB REFERENCES learning_candidate_evaluations(evaluation_id);
ALTER TABLE evolution_proposals ADD COLUMN candidate_artifact_id BLOB REFERENCES artifacts(artifact_id);
ALTER TABLE evolution_proposals ADD COLUMN candidate_artifact_sha256 TEXT CHECK(candidate_artifact_sha256 IS NULL OR (length(candidate_artifact_sha256)=64 AND candidate_artifact_sha256 NOT GLOB '*[^0-9a-f]*'));
CREATE UNIQUE INDEX idx_evolution_candidate_id ON evolution_proposals(candidate_id);

CREATE TRIGGER evolution_proposals_model_lineage_match
BEFORE INSERT ON evolution_proposals
WHEN NEW.candidate_artifact_id IS NOT NULL AND
 (NEW.owner_ref IS NULL OR NEW.candidate_id IS NULL OR NEW.candidate_artifact_sha256 IS NULL
 OR NEW.source_learning_update_id IS NULL OR NEW.source_experiment_id IS NULL
 OR NEW.source_attempt_id IS NULL OR NEW.learning_evaluation_id IS NULL
 OR NOT EXISTS (SELECT 1 FROM artifacts a WHERE a.artifact_id=NEW.candidate_artifact_id AND a.sha256=NEW.candidate_artifact_sha256 AND a.owner_ref=NEW.owner_ref)
 OR NOT EXISTS (SELECT 1 FROM learning_candidate_evaluations e WHERE e.evaluation_id=NEW.learning_evaluation_id
   AND e.learning_update_id=NEW.source_learning_update_id AND e.experiment_id=NEW.source_experiment_id
   AND e.attempt_id=NEW.source_attempt_id AND e.owner_ref=NEW.owner_ref
   AND e.candidate_artifact_id=NEW.candidate_artifact_id AND e.candidate_artifact_sha256=NEW.candidate_artifact_sha256))
BEGIN SELECT RAISE(ABORT,'evolution_proposals.model_lineage_mismatch'); END;

CREATE TABLE evolution_candidate_evaluations (
 evaluation_id BLOB PRIMARY KEY CHECK(length(evaluation_id)=16),
 proposal_id BLOB NOT NULL REFERENCES evolution_proposals(proposal_id),
 candidate_id BLOB NOT NULL REFERENCES evolution_proposals(candidate_id),
 owner_ref TEXT NOT NULL,
 artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 artifact_sha256 TEXT NOT NULL CHECK(length(artifact_sha256)=64 AND artifact_sha256 NOT GLOB '*[^0-9a-f]*'),
 baseline_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 baseline_artifact_sha256 TEXT NOT NULL CHECK(length(baseline_artifact_sha256)=64 AND baseline_artifact_sha256 NOT GLOB '*[^0-9a-f]*'),
 evaluation_protocol_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 evaluation_protocol_sha256 TEXT NOT NULL CHECK(length(evaluation_protocol_sha256)=64 AND evaluation_protocol_sha256 NOT GLOB '*[^0-9a-f]*'),
 report_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 report_digest TEXT NOT NULL CHECK(length(report_digest)=64 AND report_digest NOT GLOB '*[^0-9a-f]*'),
 status TEXT NOT NULL CHECK(status IN ('passed','failed','inconclusive')),
 evaluated_at_ms INTEGER NOT NULL,
 UNIQUE(evaluation_id,candidate_id,proposal_id,owner_ref)
) STRICT;

CREATE TRIGGER evolution_candidate_evaluations_owner_scope
BEFORE INSERT ON evolution_candidate_evaluations
WHEN NOT EXISTS (SELECT 1 FROM evolution_proposals p
 JOIN artifacts a ON a.artifact_id=NEW.artifact_id
 JOIN artifacts b ON b.artifact_id=NEW.baseline_artifact_id
 JOIN artifacts protocol ON protocol.artifact_id=NEW.evaluation_protocol_artifact_id
 JOIN artifacts report ON report.artifact_id=NEW.report_artifact_id
 WHERE p.proposal_id=NEW.proposal_id AND p.candidate_id=NEW.candidate_id
 AND p.owner_ref=NEW.owner_ref AND p.candidate_artifact_id=NEW.artifact_id
 AND p.candidate_artifact_sha256=NEW.artifact_sha256
 AND a.sha256=NEW.artifact_sha256 AND a.owner_ref=NEW.owner_ref
 AND b.owner_ref=NEW.owner_ref AND protocol.owner_ref=NEW.owner_ref AND report.owner_ref=NEW.owner_ref)
BEGIN SELECT RAISE(ABORT,'evolution_candidate_evaluations.owner_or_artifact_mismatch'); END;

ALTER TABLE evolution_proposals ADD COLUMN evolution_evaluation_id BLOB REFERENCES evolution_candidate_evaluations(evaluation_id);

CREATE TABLE active_candidate_pointers (
 owner_ref TEXT NOT NULL,
 target_mechanism TEXT NOT NULL,
 revision INTEGER NOT NULL CHECK(revision>0),
 candidate_id BLOB NOT NULL REFERENCES evolution_proposals(candidate_id),
 proposal_id BLOB NOT NULL REFERENCES evolution_proposals(proposal_id),
 artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 artifact_sha256 TEXT NOT NULL CHECK(length(artifact_sha256)=64 AND artifact_sha256 NOT GLOB '*[^0-9a-f]*'),
 updated_at_ms INTEGER NOT NULL,
 PRIMARY KEY(owner_ref,target_mechanism)
) STRICT;

CREATE TABLE candidate_pointer_history (
 transition_id BLOB PRIMARY KEY CHECK(length(transition_id)=16),
 owner_ref TEXT NOT NULL,
 target_mechanism TEXT NOT NULL,
 revision INTEGER NOT NULL CHECK(revision>0),
 previous_revision INTEGER NOT NULL CHECK(previous_revision>=0),
 operation_type TEXT NOT NULL CHECK(operation_type IN ('activate','rollback')),
 proposal_id BLOB NOT NULL REFERENCES evolution_proposals(proposal_id),
 previous_candidate_id BLOB REFERENCES evolution_proposals(candidate_id),
 new_candidate_id BLOB NOT NULL REFERENCES evolution_proposals(candidate_id),
 previous_artifact_id BLOB REFERENCES artifacts(artifact_id),
 new_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
 artifact_sha256 TEXT NOT NULL CHECK(length(artifact_sha256)=64 AND artifact_sha256 NOT GLOB '*[^0-9a-f]*'),
 approval_ref TEXT NOT NULL CHECK(length(approval_ref)>0),
 operation_id BLOB NOT NULL CHECK(length(operation_id)=16),
 operation_digest TEXT NOT NULL CHECK(length(operation_digest)=64 AND operation_digest NOT GLOB '*[^0-9a-f]*'),
 learning_evaluation_id BLOB REFERENCES learning_candidate_evaluations(evaluation_id),
 evolution_evaluation_id BLOB REFERENCES evolution_candidate_evaluations(evaluation_id),
 rollback_ref TEXT,
 occurred_at_ms INTEGER NOT NULL,
 UNIQUE(owner_ref,target_mechanism,revision),
 CHECK(operation_type<>'activate' OR (learning_evaluation_id IS NOT NULL AND evolution_evaluation_id IS NOT NULL)),
 CHECK(operation_type<>'rollback' OR (rollback_ref IS NOT NULL AND length(rollback_ref)>0))
) STRICT;

CREATE TRIGGER candidate_pointer_history_validate
BEFORE INSERT ON candidate_pointer_history
WHEN NOT EXISTS (SELECT 1 FROM evolution_proposals p JOIN artifacts a ON a.artifact_id=NEW.new_artifact_id
 WHERE p.proposal_id=NEW.proposal_id AND p.candidate_id=NEW.new_candidate_id
 AND p.owner_ref=NEW.owner_ref AND p.target_mechanism=NEW.target_mechanism
 AND p.candidate_artifact_id=NEW.new_artifact_id AND p.candidate_artifact_sha256=NEW.artifact_sha256
 AND a.sha256=NEW.artifact_sha256 AND a.owner_ref=NEW.owner_ref)
 OR (NEW.operation_type='activate' AND NOT EXISTS (
 SELECT 1 FROM learning_candidate_evaluations le JOIN evolution_candidate_evaluations ee
 ON ee.evaluation_id=NEW.evolution_evaluation_id
 WHERE le.evaluation_id=NEW.learning_evaluation_id AND le.status='passed' AND ee.status='passed'
 AND le.owner_ref=NEW.owner_ref AND ee.owner_ref=NEW.owner_ref
 AND le.candidate_artifact_id=NEW.new_artifact_id AND le.candidate_artifact_sha256=NEW.artifact_sha256
 AND ee.candidate_id=NEW.new_candidate_id AND ee.artifact_id=NEW.new_artifact_id AND ee.artifact_sha256=NEW.artifact_sha256))
BEGIN SELECT RAISE(ABORT,'candidate_pointer_history.candidate_or_evaluation_mismatch'); END;

CREATE TRIGGER candidate_pointer_history_no_update
BEFORE UPDATE ON candidate_pointer_history
BEGIN SELECT RAISE(ABORT,'candidate_pointer_history.append_only'); END;
CREATE TRIGGER candidate_pointer_history_no_delete
BEFORE DELETE ON candidate_pointer_history
BEGIN SELECT RAISE(ABORT,'candidate_pointer_history.append_only'); END;

CREATE TRIGGER active_candidate_pointer_insert_requires_history
BEFORE INSERT ON active_candidate_pointers
WHEN NOT EXISTS (SELECT 1 FROM candidate_pointer_history h
 WHERE h.owner_ref=NEW.owner_ref AND h.target_mechanism=NEW.target_mechanism
 AND h.revision=NEW.revision AND h.previous_revision=0 AND h.previous_candidate_id IS NULL
 AND h.new_candidate_id=NEW.candidate_id AND h.proposal_id=NEW.proposal_id
 AND h.new_artifact_id=NEW.artifact_id AND h.artifact_sha256=NEW.artifact_sha256)
BEGIN SELECT RAISE(ABORT,'active_candidate_pointers.history_required'); END;

CREATE TRIGGER active_candidate_pointer_update_requires_history
BEFORE UPDATE ON active_candidate_pointers
WHEN NEW.owner_ref IS NOT OLD.owner_ref OR NEW.target_mechanism IS NOT OLD.target_mechanism
 OR NEW.revision<>OLD.revision+1
 OR NOT EXISTS (SELECT 1 FROM candidate_pointer_history h
  WHERE h.owner_ref=NEW.owner_ref AND h.target_mechanism=NEW.target_mechanism
  AND h.revision=NEW.revision AND h.previous_revision=OLD.revision
  AND h.previous_candidate_id=OLD.candidate_id AND h.new_candidate_id=NEW.candidate_id
  AND h.proposal_id=NEW.proposal_id AND h.new_artifact_id=NEW.artifact_id
  AND h.artifact_sha256=NEW.artifact_sha256)
BEGIN SELECT RAISE(ABORT,'active_candidate_pointers.compare_and_swap_or_history_required'); END;

CREATE TRIGGER active_candidate_pointer_no_delete
BEFORE DELETE ON active_candidate_pointers
BEGIN SELECT RAISE(ABORT,'active_candidate_pointers.delete_prohibited'); END;
