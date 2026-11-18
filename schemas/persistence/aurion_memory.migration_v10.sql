-- AURIONS additive migration v10 for aurion_memory.db.
-- Durable local-only transport, idempotency, causality, conflict, deletion and restore state.
-- These records are never exported as domain payloads; no peer key material is stored here.
-- Domain mutation, inbox receipt and memory-local outbox publication intent share one transaction.

CREATE TABLE sync_export_ledger (
  export_id BLOB PRIMARY KEY CHECK(length(export_id)=16),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  source_runtime_id BLOB NOT NULL CHECK(length(source_runtime_id)=16),
  target_runtime_id BLOB NOT NULL CHECK(length(target_runtime_id)=16),
  change_id BLOB NOT NULL CHECK(length(change_id)=16),
  aggregate_type TEXT NOT NULL CHECK(length(aggregate_type)>0),
  aggregate_id TEXT NOT NULL CHECK(length(aggregate_id)>0),
  base_revision INTEGER NOT NULL CHECK(base_revision>=0),
  aggregate_revision INTEGER NOT NULL CHECK(aggregate_revision>base_revision),
  source_sequence INTEGER NOT NULL CHECK(source_sequence>0),
  schema_version TEXT NOT NULL CHECK(length(schema_version)>0),
  allowlist_version TEXT NOT NULL CHECK(length(allowlist_version)>0),
  payload_digest TEXT NOT NULL CHECK(length(payload_digest)=64 AND payload_digest NOT GLOB '*[^0-9a-f]*'),
  envelope_digest TEXT NOT NULL CHECK(length(envelope_digest)=64 AND envelope_digest NOT GLOB '*[^0-9a-f]*'),
  outbox_id BLOB NOT NULL REFERENCES outbox(outbox_id),
  created_at_ms INTEGER NOT NULL,
  UNIQUE(source_runtime_id,target_runtime_id,change_id),
  UNIQUE(source_runtime_id,target_runtime_id,source_sequence)
) STRICT;
CREATE INDEX idx_sync_export_target ON sync_export_ledger(target_runtime_id,source_sequence);
CREATE INDEX idx_sync_export_aggregate ON sync_export_ledger(owner_ref,aggregate_type,aggregate_id,aggregate_revision);

CREATE TABLE sync_export_events (
  export_event_id BLOB PRIMARY KEY CHECK(length(export_event_id)=16),
  export_id BLOB NOT NULL REFERENCES sync_export_ledger(export_id),
  event_sequence INTEGER NOT NULL CHECK(event_sequence>0),
  state TEXT NOT NULL CHECK(state IN ('queued','exported','acknowledged','quarantined','superseded')),
  transition_digest TEXT NOT NULL CHECK(length(transition_digest)=64 AND transition_digest NOT GLOB '*[^0-9a-f]*'),
  occurred_at_ms INTEGER NOT NULL,
  UNIQUE(export_id,event_sequence)
) STRICT;
CREATE TRIGGER sync_export_events_transition
BEFORE INSERT ON sync_export_events
WHEN NOT (
  (NEW.event_sequence=1 AND NEW.state='queued')
  OR EXISTS (
    SELECT 1 FROM sync_export_events p
    WHERE p.export_id=NEW.export_id
      AND p.event_sequence=(SELECT max(x.event_sequence) FROM sync_export_events x WHERE x.export_id=NEW.export_id)
      AND NEW.event_sequence=p.event_sequence+1
      AND ((p.state='queued' AND NEW.state IN ('exported','quarantined','superseded'))
        OR (p.state='exported' AND NEW.state IN ('acknowledged','quarantined')))
  )
)
BEGIN SELECT RAISE(ABORT,'sync_export_events.invalid_transition'); END;

CREATE TABLE sync_inbox_receipts (
  receipt_id BLOB PRIMARY KEY CHECK(length(receipt_id)=16),
  source_runtime_id BLOB NOT NULL CHECK(length(source_runtime_id)=16),
  target_runtime_id BLOB NOT NULL CHECK(length(target_runtime_id)=16),
  change_id BLOB NOT NULL CHECK(length(change_id)=16),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  aggregate_type TEXT NOT NULL CHECK(length(aggregate_type)>0),
  aggregate_id TEXT NOT NULL CHECK(length(aggregate_id)>0),
  base_revision INTEGER NOT NULL CHECK(base_revision>=0),
  aggregate_revision INTEGER NOT NULL CHECK(aggregate_revision>base_revision),
  payload_digest TEXT NOT NULL CHECK(length(payload_digest)=64 AND payload_digest NOT GLOB '*[^0-9a-f]*'),
  outcome TEXT NOT NULL CHECK(outcome IN ('applied','deferred','conflict','tombstone_applied')),
  receipt_digest TEXT NOT NULL CHECK(length(receipt_digest)=64 AND receipt_digest NOT GLOB '*[^0-9a-f]*'),
  received_at_ms INTEGER NOT NULL,
  committed_at_ms INTEGER NOT NULL,
  UNIQUE(source_runtime_id,change_id)
) STRICT;
CREATE INDEX idx_sync_inbox_aggregate ON sync_inbox_receipts(owner_ref,aggregate_type,aggregate_id,aggregate_revision);

CREATE TABLE sync_quarantined_envelopes (
  quarantine_id BLOB PRIMARY KEY CHECK(length(quarantine_id)=16),
  source_runtime_id BLOB CHECK(source_runtime_id IS NULL OR length(source_runtime_id)=16),
  claimed_change_id BLOB CHECK(claimed_change_id IS NULL OR length(claimed_change_id)=16),
  observed_payload_digest TEXT NOT NULL CHECK(length(observed_payload_digest)=64 AND observed_payload_digest NOT GLOB '*[^0-9a-f]*'),
  reason_code TEXT NOT NULL CHECK(reason_code IN ('identity_digest_mismatch','owner_scope_mismatch','untrusted_peer','unknown_schema','unknown_allowlist','unknown_policy','invalid_signature','invalid_projection','invalid_causality','invalid_tombstone','retention_blocked')),
  quarantine_ref TEXT NOT NULL CHECK(length(quarantine_ref)>0),
  observed_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE sync_peer_acknowledgements (
  acknowledgement_id BLOB PRIMARY KEY CHECK(length(acknowledgement_id)=16),
  export_id BLOB NOT NULL REFERENCES sync_export_ledger(export_id),
  peer_runtime_id BLOB NOT NULL CHECK(length(peer_runtime_id)=16),
  change_id BLOB NOT NULL CHECK(length(change_id)=16),
  payload_digest TEXT NOT NULL CHECK(length(payload_digest)=64 AND payload_digest NOT GLOB '*[^0-9a-f]*'),
  receipt_digest TEXT NOT NULL CHECK(length(receipt_digest)=64 AND receipt_digest NOT GLOB '*[^0-9a-f]*'),
  acknowledged_at_ms INTEGER NOT NULL,
  UNIQUE(export_id,peer_runtime_id)
) STRICT;
CREATE TRIGGER sync_peer_acknowledgements_match_export
BEFORE INSERT ON sync_peer_acknowledgements
WHEN NOT EXISTS (
  SELECT 1 FROM sync_export_ledger e
  WHERE e.export_id=NEW.export_id AND e.target_runtime_id=NEW.peer_runtime_id
    AND e.change_id=NEW.change_id AND e.payload_digest=NEW.payload_digest
)
BEGIN SELECT RAISE(ABORT,'sync_peer_acknowledgements.export_mismatch'); END;

CREATE TRIGGER sync_export_events_ack_requires_receipt
BEFORE INSERT ON sync_export_events
WHEN NEW.state='acknowledged' AND NOT EXISTS (
  SELECT 1 FROM sync_peer_acknowledgements a WHERE a.export_id=NEW.export_id
)
BEGIN SELECT RAISE(ABORT,'sync_export_events.acknowledgement_required'); END;

CREATE TABLE sync_peer_checkpoints (
  checkpoint_id BLOB PRIMARY KEY CHECK(length(checkpoint_id)=16),
  peer_runtime_id BLOB NOT NULL CHECK(length(peer_runtime_id)=16),
  stream_ref TEXT NOT NULL CHECK(length(stream_ref)>0),
  source_sequence INTEGER NOT NULL CHECK(source_sequence>=0),
  change_id BLOB CHECK(change_id IS NULL OR length(change_id)=16),
  cursor_digest TEXT NOT NULL CHECK(length(cursor_digest)=64 AND cursor_digest NOT GLOB '*[^0-9a-f]*'),
  recorded_at_ms INTEGER NOT NULL,
  UNIQUE(peer_runtime_id,stream_ref,source_sequence)
) STRICT;
CREATE TRIGGER sync_peer_checkpoints_monotonic
BEFORE INSERT ON sync_peer_checkpoints
WHEN EXISTS (
  SELECT 1 FROM sync_peer_checkpoints p
  WHERE p.peer_runtime_id=NEW.peer_runtime_id AND p.stream_ref=NEW.stream_ref
    AND p.source_sequence>NEW.source_sequence
)
BEGIN SELECT RAISE(ABORT,'sync_peer_checkpoints.non_monotonic'); END;

CREATE TABLE sync_causal_gap_events (
  gap_event_id BLOB PRIMARY KEY CHECK(length(gap_event_id)=16),
  gap_id BLOB NOT NULL CHECK(length(gap_id)=16),
  event_sequence INTEGER NOT NULL CHECK(event_sequence>0),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  aggregate_type TEXT NOT NULL CHECK(length(aggregate_type)>0),
  aggregate_id TEXT NOT NULL CHECK(length(aggregate_id)>0),
  source_runtime_id BLOB NOT NULL CHECK(length(source_runtime_id)=16),
  blocked_change_id BLOB NOT NULL CHECK(length(blocked_change_id)=16),
  missing_parent_change_id BLOB NOT NULL CHECK(length(missing_parent_change_id)=16),
  state TEXT NOT NULL CHECK(state IN ('opened','resolved')),
  resolution_ref TEXT,
  occurred_at_ms INTEGER NOT NULL,
  UNIQUE(gap_id,event_sequence),
  CHECK(state<>'resolved' OR (resolution_ref IS NOT NULL AND length(resolution_ref)>0))
) STRICT;
CREATE TRIGGER sync_causal_gap_events_transition
BEFORE INSERT ON sync_causal_gap_events
WHEN NOT (
  (NEW.event_sequence=1 AND NEW.state='opened')
  OR EXISTS (
    SELECT 1 FROM sync_causal_gap_events p
    WHERE p.gap_id=NEW.gap_id
      AND p.event_sequence=(SELECT max(x.event_sequence) FROM sync_causal_gap_events x WHERE x.gap_id=NEW.gap_id)
      AND NEW.event_sequence=p.event_sequence+1 AND p.state='opened' AND NEW.state='resolved'
      AND p.blocked_change_id=NEW.blocked_change_id
      AND p.missing_parent_change_id=NEW.missing_parent_change_id
  )
)
BEGIN SELECT RAISE(ABORT,'sync_causal_gap_events.invalid_transition'); END;

CREATE TABLE sync_conflict_records (
  conflict_id BLOB PRIMARY KEY CHECK(length(conflict_id)=16),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  aggregate_type TEXT NOT NULL CHECK(length(aggregate_type)>0),
  aggregate_id TEXT NOT NULL CHECK(length(aggregate_id)>0),
  local_runtime_id BLOB NOT NULL CHECK(length(local_runtime_id)=16),
  remote_runtime_id BLOB NOT NULL CHECK(length(remote_runtime_id)=16),
  local_change_id BLOB NOT NULL CHECK(length(local_change_id)=16),
  remote_change_id BLOB NOT NULL CHECK(length(remote_change_id)=16),
  common_base_revision INTEGER NOT NULL CHECK(common_base_revision>=0),
  local_revision INTEGER NOT NULL CHECK(local_revision>common_base_revision),
  remote_revision INTEGER NOT NULL CHECK(remote_revision>common_base_revision),
  conflict_revision INTEGER NOT NULL CHECK(conflict_revision>0),
  allowlist_version TEXT NOT NULL CHECK(length(allowlist_version)>0),
  classification_policy_version TEXT NOT NULL CHECK(length(classification_policy_version)>0),
  detected_at_ms INTEGER NOT NULL,
  UNIQUE(owner_ref,aggregate_type,aggregate_id,conflict_revision),
  CHECK(local_change_id<>remote_change_id),
  CHECK(local_runtime_id<>remote_runtime_id)
) STRICT;
CREATE TABLE sync_conflict_resolutions (
  resolution_id BLOB PRIMARY KEY CHECK(length(resolution_id)=16),
  conflict_id BLOB NOT NULL UNIQUE REFERENCES sync_conflict_records(conflict_id),
  expected_conflict_revision INTEGER NOT NULL CHECK(expected_conflict_revision>0),
  actor_ref TEXT NOT NULL CHECK(length(actor_ref)>0),
  approval_ref TEXT NOT NULL CHECK(length(approval_ref)>0),
  resolution_digest TEXT NOT NULL CHECK(length(resolution_digest)=64 AND resolution_digest NOT GLOB '*[^0-9a-f]*'),
  successor_revision INTEGER NOT NULL CHECK(successor_revision>0),
  resolved_at_ms INTEGER NOT NULL
) STRICT;
CREATE TRIGGER sync_conflict_resolutions_revision
BEFORE INSERT ON sync_conflict_resolutions
WHEN NOT EXISTS (
  SELECT 1 FROM sync_conflict_records c
  WHERE c.conflict_id=NEW.conflict_id AND c.conflict_revision=NEW.expected_conflict_revision
    AND NEW.successor_revision>max(c.local_revision,c.remote_revision)
)
BEGIN SELECT RAISE(ABORT,'sync_conflict_resolutions.revision_mismatch'); END;

CREATE TABLE sync_tombstone_records (
  tombstone_id BLOB PRIMARY KEY CHECK(length(tombstone_id)=16),
  deletion_id BLOB NOT NULL UNIQUE CHECK(length(deletion_id)=16),
  owner_ref TEXT NOT NULL CHECK(length(owner_ref)>0),
  aggregate_type TEXT NOT NULL CHECK(length(aggregate_type)>0),
  aggregate_id TEXT NOT NULL CHECK(length(aggregate_id)>0),
  deletion_revision INTEGER NOT NULL CHECK(deletion_revision>0),
  source_runtime_id BLOB NOT NULL CHECK(length(source_runtime_id)=16),
  change_id BLOB NOT NULL CHECK(length(change_id)=16),
  retention_policy_version TEXT NOT NULL CHECK(length(retention_policy_version)>0),
  replay_horizon_until_ms INTEGER NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE(owner_ref,aggregate_type,aggregate_id,deletion_revision)
) STRICT;
CREATE TABLE sync_tombstone_peer_receipts (
  tombstone_receipt_id BLOB PRIMARY KEY CHECK(length(tombstone_receipt_id)=16),
  tombstone_id BLOB NOT NULL REFERENCES sync_tombstone_records(tombstone_id),
  peer_runtime_id BLOB NOT NULL CHECK(length(peer_runtime_id)=16),
  receipt_digest TEXT NOT NULL CHECK(length(receipt_digest)=64 AND receipt_digest NOT GLOB '*[^0-9a-f]*'),
  acknowledged_at_ms INTEGER NOT NULL,
  UNIQUE(tombstone_id,peer_runtime_id)
) STRICT;

CREATE TABLE sync_restore_events (
  restore_event_id BLOB PRIMARY KEY CHECK(length(restore_event_id)=16),
  restore_id BLOB NOT NULL CHECK(length(restore_id)=16),
  event_sequence INTEGER NOT NULL CHECK(event_sequence>0),
  runtime_id BLOB NOT NULL CHECK(length(runtime_id)=16),
  backup_ref TEXT NOT NULL CHECK(length(backup_ref)>0),
  state TEXT NOT NULL CHECK(state IN ('started','replaying','blocked','reconciled')),
  required_tombstone_frontier INTEGER NOT NULL CHECK(required_tombstone_frontier>=0),
  applied_tombstone_frontier INTEGER NOT NULL CHECK(applied_tombstone_frontier>=0),
  occurred_at_ms INTEGER NOT NULL,
  UNIQUE(restore_id,event_sequence),
  CHECK(applied_tombstone_frontier<=required_tombstone_frontier),
  CHECK(state<>'reconciled' OR applied_tombstone_frontier=required_tombstone_frontier)
) STRICT;
CREATE TRIGGER sync_restore_events_transition
BEFORE INSERT ON sync_restore_events
WHEN NOT (
  (NEW.event_sequence=1 AND NEW.state='started' AND NEW.applied_tombstone_frontier=0)
  OR EXISTS (
    SELECT 1 FROM sync_restore_events p
    WHERE p.restore_id=NEW.restore_id
      AND p.event_sequence=(SELECT max(x.event_sequence) FROM sync_restore_events x WHERE x.restore_id=NEW.restore_id)
      AND NEW.event_sequence=p.event_sequence+1 AND p.runtime_id=NEW.runtime_id AND p.backup_ref=NEW.backup_ref
      AND p.required_tombstone_frontier=NEW.required_tombstone_frontier
      AND NEW.applied_tombstone_frontier>=p.applied_tombstone_frontier
      AND ((p.state='started' AND NEW.state IN ('replaying','blocked'))
        OR (p.state='replaying' AND NEW.state IN ('replaying','blocked','reconciled'))
        OR (p.state='blocked' AND NEW.state IN ('replaying','blocked')))
  )
)
BEGIN SELECT RAISE(ABORT,'sync_restore_events.invalid_transition'); END;

CREATE TRIGGER sync_export_ledger_no_update BEFORE UPDATE ON sync_export_ledger BEGIN SELECT RAISE(ABORT,'sync_export_ledger.immutable'); END;
CREATE TRIGGER sync_export_ledger_no_delete BEFORE DELETE ON sync_export_ledger BEGIN SELECT RAISE(ABORT,'sync_export_ledger.immutable'); END;
CREATE TRIGGER sync_export_events_no_update BEFORE UPDATE ON sync_export_events BEGIN SELECT RAISE(ABORT,'sync_export_events.append_only'); END;
CREATE TRIGGER sync_export_events_no_delete BEFORE DELETE ON sync_export_events BEGIN SELECT RAISE(ABORT,'sync_export_events.append_only'); END;
CREATE TRIGGER sync_inbox_receipts_no_update BEFORE UPDATE ON sync_inbox_receipts BEGIN SELECT RAISE(ABORT,'sync_inbox_receipts.append_only'); END;
CREATE TRIGGER sync_inbox_receipts_no_delete BEFORE DELETE ON sync_inbox_receipts BEGIN SELECT RAISE(ABORT,'sync_inbox_receipts.append_only'); END;
CREATE TRIGGER sync_quarantined_envelopes_no_update BEFORE UPDATE ON sync_quarantined_envelopes BEGIN SELECT RAISE(ABORT,'sync_quarantined_envelopes.append_only'); END;
CREATE TRIGGER sync_quarantined_envelopes_no_delete BEFORE DELETE ON sync_quarantined_envelopes BEGIN SELECT RAISE(ABORT,'sync_quarantined_envelopes.append_only'); END;
CREATE TRIGGER sync_peer_acknowledgements_no_update BEFORE UPDATE ON sync_peer_acknowledgements BEGIN SELECT RAISE(ABORT,'sync_peer_acknowledgements.append_only'); END;
CREATE TRIGGER sync_peer_acknowledgements_no_delete BEFORE DELETE ON sync_peer_acknowledgements BEGIN SELECT RAISE(ABORT,'sync_peer_acknowledgements.append_only'); END;
CREATE TRIGGER sync_peer_checkpoints_no_update BEFORE UPDATE ON sync_peer_checkpoints BEGIN SELECT RAISE(ABORT,'sync_peer_checkpoints.append_only'); END;
CREATE TRIGGER sync_peer_checkpoints_no_delete BEFORE DELETE ON sync_peer_checkpoints BEGIN SELECT RAISE(ABORT,'sync_peer_checkpoints.append_only'); END;
CREATE TRIGGER sync_causal_gap_events_no_update BEFORE UPDATE ON sync_causal_gap_events BEGIN SELECT RAISE(ABORT,'sync_causal_gap_events.append_only'); END;
CREATE TRIGGER sync_causal_gap_events_no_delete BEFORE DELETE ON sync_causal_gap_events BEGIN SELECT RAISE(ABORT,'sync_causal_gap_events.append_only'); END;
CREATE TRIGGER sync_conflict_records_no_update BEFORE UPDATE ON sync_conflict_records BEGIN SELECT RAISE(ABORT,'sync_conflict_records.immutable'); END;
CREATE TRIGGER sync_conflict_records_no_delete BEFORE DELETE ON sync_conflict_records BEGIN SELECT RAISE(ABORT,'sync_conflict_records.immutable'); END;
CREATE TRIGGER sync_conflict_resolutions_no_update BEFORE UPDATE ON sync_conflict_resolutions BEGIN SELECT RAISE(ABORT,'sync_conflict_resolutions.append_only'); END;
CREATE TRIGGER sync_conflict_resolutions_no_delete BEFORE DELETE ON sync_conflict_resolutions BEGIN SELECT RAISE(ABORT,'sync_conflict_resolutions.append_only'); END;
CREATE TRIGGER sync_tombstone_records_no_update BEFORE UPDATE ON sync_tombstone_records BEGIN SELECT RAISE(ABORT,'sync_tombstone_records.immutable'); END;
CREATE TRIGGER sync_tombstone_records_no_delete BEFORE DELETE ON sync_tombstone_records BEGIN SELECT RAISE(ABORT,'sync_tombstone_records.immutable'); END;
CREATE TRIGGER sync_tombstone_peer_receipts_no_update BEFORE UPDATE ON sync_tombstone_peer_receipts BEGIN SELECT RAISE(ABORT,'sync_tombstone_peer_receipts.append_only'); END;
CREATE TRIGGER sync_tombstone_peer_receipts_no_delete BEFORE DELETE ON sync_tombstone_peer_receipts BEGIN SELECT RAISE(ABORT,'sync_tombstone_peer_receipts.append_only'); END;
CREATE TRIGGER sync_restore_events_no_update BEFORE UPDATE ON sync_restore_events BEGIN SELECT RAISE(ABORT,'sync_restore_events.append_only'); END;
CREATE TRIGGER sync_restore_events_no_delete BEFORE DELETE ON sync_restore_events BEGIN SELECT RAISE(ABORT,'sync_restore_events.append_only'); END;
