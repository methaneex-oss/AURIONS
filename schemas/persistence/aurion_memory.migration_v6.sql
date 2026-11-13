-- Proposed additive migration v6 for aurion_memory.db.
-- Bind every new derived goal revision to an exact owner-scoped objective revision.
-- Legacy goal revisions remain unbound; never infer their objective from description or plan text.

CREATE UNIQUE INDEX idx_objective_revision_owner
  ON objective_records(objective_id,version,owner_ref);

CREATE TABLE goal_revision_objective_bindings (
  goal_id BLOB NOT NULL,
  goal_revision INTEGER NOT NULL CHECK(goal_revision>0),
  owner_ref TEXT NOT NULL,
  objective_id TEXT NOT NULL,
  objective_version INTEGER NOT NULL CHECK(objective_version>0),
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(goal_id,goal_revision),
  FOREIGN KEY(goal_id,goal_revision)
    REFERENCES goal_revisions(goal_id,revision)
    DEFERRABLE INITIALLY DEFERRED,
  FOREIGN KEY(objective_id,objective_version,owner_ref)
    REFERENCES objective_records(objective_id,version,owner_ref)
    DEFERRABLE INITIALLY DEFERRED
) STRICT;

CREATE INDEX idx_goal_objective_owner
  ON goal_revision_objective_bindings(owner_ref,objective_id,objective_version);

-- Insert the binding row first in the same transaction, then insert goal_revisions.
-- Deferred FKs validate both parent records at commit.
CREATE TRIGGER trg_goal_revision_requires_objective_binding
BEFORE INSERT ON goal_revisions
WHEN NOT EXISTS (
  SELECT 1 FROM goal_revision_objective_bindings
  WHERE goal_id=NEW.goal_id AND goal_revision=NEW.revision
)
BEGIN
  SELECT RAISE(ABORT,'goal_revisions.objective_binding_required');
END;
