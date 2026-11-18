-- Proposed additive migration v5 for aurion_memory.db.
-- A domain mutation and its publication intent must commit in this same database.
-- The event/recovery database is a central archive/dispatch ledger, not the sole durable outbox.

CREATE TABLE outbox (
  outbox_id BLOB PRIMARY KEY CHECK(length(outbox_id)=16),
  message_id BLOB NOT NULL UNIQUE CHECK(length(message_id)=16),
  destination TEXT NOT NULL,
  envelope_json TEXT NOT NULL CHECK(json_valid(envelope_json)),
  state TEXT NOT NULL CHECK(state IN ('pending','published','dead_letter')),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
  next_attempt_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  published_at_ms INTEGER,
  last_error_ref TEXT
) STRICT;
CREATE INDEX idx_memory_outbox_dispatch ON outbox(state,next_attempt_at_ms);
