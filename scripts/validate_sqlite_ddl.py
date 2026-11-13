#!/usr/bin/env python3
"""Execute every proposed SQLite base schema and additive migration on host SQLite.

This is a host-side DDL/migration smoke gate. It does not establish Android/
Termux compatibility, crash safety, restore correctness, concurrency safety,
or application-level transaction/outbox behaviour.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DDL = ROOT / "schemas" / "persistence"


def check_database(name: str, connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    if enabled != 1:
        raise AssertionError(f"{name}: foreign-key enforcement is disabled")
    fk_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    if fk_errors:
        raise AssertionError(f"{name}: foreign_key_check failed: {fk_errors[:5]}")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise AssertionError(f"{name}: integrity_check failed: {integrity}")


def execute_chain(name: str, files: list[str]) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    for filename in files:
        path = DDL / filename
        sql = path.read_text(encoding="utf-8")
        try:
            connection.executescript(sql)
        except sqlite3.Error as exc:
            raise AssertionError(f"{name}: {filename} failed: {exc}") from exc
        check_database(f"{name} after {filename}", connection)
    return connection


def require_columns(connection: sqlite3.Connection, table: str, expected: set[str]) -> None:
    actual = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    missing = expected - actual
    if missing:
        raise AssertionError(f"{table}: missing columns {sorted(missing)}")


def expect_integrity_error(
    connection: sqlite3.Connection, label: str, statement: str, values: tuple = ()
) -> None:
    try:
        connection.execute(statement, values)
    except sqlite3.IntegrityError:
        return
    raise AssertionError(f"{label}: invalid row was accepted")


def test_memory() -> None:
    db = execute_chain("memory", [
        "aurion_memory.base.sql",
        "aurion_memory.migration_v2.sql",
        "aurion_memory.migration_v3.sql",
        "aurion_memory.migration_v4.sql",
        "aurion_memory.migration_v5.sql",
        "aurion_memory.migration_v6.sql",
        "aurion_memory.migration_v7.sql",
    ])
    require_columns(db, "objective_records", {
        "objective_id", "owner_ref", "version", "success_evidence_json"
    })
    require_columns(db, "evidence_details", {
        "evidence_id", "owner_ref", "epistemic_status", "sensitivity"
    })
    require_columns(db, "goal_revision_objective_bindings", {
        "goal_id", "goal_revision", "owner_ref", "objective_id", "objective_version", "created_at_ms"
    })
    require_columns(db, "outbox", {
        "outbox_id", "message_id", "destination", "envelope_json", "state",
        "attempt_count", "next_attempt_at_ms", "created_at_ms", "published_at_ms",
        "last_error_ref",
    })
    require_columns(db, "environment_observations", {
        "observation_id", "owner_ref", "device_id", "environment_scope",
        "observed_at_ms", "recorded_at_ms", "source_id", "collection_method",
        "collector_version", "platform_context_json", "observed_facts_json",
        "sensitivity", "limitations_json", "validity_json",
    })
    require_columns(db, "capability_descriptors", {"descriptor_schema_version"})
    require_columns(db, "representations", {"method_version", "source_refs_json"})
    require_columns(db, "contexts", {"provenance_refs_json", "uncertainty_json"})
    require_columns(db, "memory_records", {"provenance_refs_json", "uncertainty_json"})
    require_columns(db, "predictions", {"conditions_json", "confidence", "evidence_refs_json"})
    require_columns(db, "plans", {"context_version_ref", "capability_epoch_digest"})
    for table in (
        "world_entities", "world_relationships", "situation_snapshots",
        "affordance_hypotheses", "interaction_proposals", "interaction_outcomes",
    ):
        if not db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone():
            raise AssertionError(f"memory: missing v4 table {table}")
    db.execute(
        """INSERT INTO objective_records
        (objective_id,owner_ref,version,statement,request_source_ref,status,
         success_evidence_json,constraints_json,assumptions_json,uncertainty_json,
         created_at_ms)
        VALUES ('obj-1','owner-1',1,'test objective','source-1','proposed',
                '[]','[]','[]','[]',1)"""
    )
    db.commit()
    # Aggregate and publication intent share one owning-store transaction.
    db.execute("BEGIN")
    db.execute(
        """INSERT INTO objective_records
        (objective_id,owner_ref,version,statement,request_source_ref,status,
         success_evidence_json,constraints_json,assumptions_json,uncertainty_json,
         created_at_ms)
        VALUES ('obj-rollback','owner-1',1,'rollback probe','source-1','proposed',
                '[]','[]','[]','[]',2)"""
    )
    db.execute(
        """INSERT INTO outbox
        (outbox_id,message_id,destination,envelope_json,state,created_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (bytes([6]) * 16, bytes([7]) * 16, "event-archive", "{}", "pending", 2),
    )
    db.rollback()
    if db.execute("SELECT 1 FROM objective_records WHERE objective_id='obj-rollback'").fetchone():
        raise AssertionError("memory: aggregate survived rollback without its outbox")
    if db.execute("SELECT 1 FROM outbox WHERE message_id=?", (bytes([7]) * 16,)).fetchone():
        raise AssertionError("memory: outbox survived aggregate rollback")
    # Interaction outcomes must reference a proposal owned by the same owner.
    db.execute(
        """INSERT INTO interaction_proposals
        (interaction_id,owner_ref,objective_ref,actor_ref,target_refs_json,
         means_hypothesis_refs_json,proposed_effects_json,risk_assessment_json,
         precondition_evidence_refs_json,status,proposed_at_ms)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        ("interaction-1", "owner-1", "objective-1", "actor-1", "[]",
         "[]", "[]", "{}", "[]", "proposed", 4),
    )
    db.execute(
        """INSERT INTO interaction_outcomes
        (outcome_id,interaction_ref,owner_ref,result_status,observed_effects_json,
         evidence_refs_json,unresolved_effects_json,attribution_json,side_effects_json,
         observed_at_ms,recorded_at_ms)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        ("outcome-1", "interaction-1", "owner-1", "observed", "[]",
         "[]", "[]", "{}", "[]", 5, 5),
    )
    for interaction_ref, owner_ref, outcome_id in (
        ("missing-interaction", "owner-1", "outcome-missing"),
        ("interaction-1", "owner-2", "outcome-cross-owner"),
    ):
        try:
            db.execute(
                """INSERT INTO interaction_outcomes
                (outcome_id,interaction_ref,owner_ref,result_status,observed_effects_json,
                 evidence_refs_json,unresolved_effects_json,attribution_json,side_effects_json,
                 observed_at_ms,recorded_at_ms)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (outcome_id, interaction_ref, owner_ref, "observed", "[]",
                 "[]", "[]", "{}", "[]", 6, 6),
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError(
                f"memory: invalid interaction outcome reference was accepted: {outcome_id}"
            )
    db.commit()
    # A new goal revision must bind to an exact objective revision owned by the same owner.
    goal_id = bytes([11]) * 16
    db.execute("BEGIN")
    db.execute(
        "INSERT INTO goals (goal_id,created_at_ms,updated_at_ms) VALUES (?,?,?)",
        (goal_id, 7, 7),
    )
    db.execute(
        """INSERT INTO goal_revision_objective_bindings
        (goal_id,goal_revision,owner_ref,objective_id,objective_version,created_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (goal_id, 1, "owner-1", "obj-1", 1, 7),
    )
    db.execute(
        """INSERT INTO goal_revisions
        (goal_id,revision,description,state,priority,constraints_json,reason_ref,created_at_ms)
        VALUES (?,?,?,?,?,?,?,?)""",
        (goal_id, 1, "derived goal", "proposed", 0.5, "{}", "source-1", 7),
    )
    db.commit()
    if not db.execute(
        "SELECT 1 FROM goal_revision_objective_bindings WHERE goal_id=? AND objective_id='obj-1' AND objective_version=1",
        (goal_id,),
    ).fetchone():
        raise AssertionError("memory: exact objective binding was not persisted")

    # A new goal revision without a binding is rejected at insert time.
    unbound_goal_id = bytes([12]) * 16
    db.execute(
        "INSERT INTO goals (goal_id,created_at_ms,updated_at_ms) VALUES (?,?,?)",
        (unbound_goal_id, 8, 8),
    )
    try:
        db.execute(
            """INSERT INTO goal_revisions
            (goal_id,revision,description,state,priority,constraints_json,reason_ref,created_at_ms)
            VALUES (?,?,?,?,?,?,?,?)""",
            (unbound_goal_id, 1, "unbound goal", "proposed", 0.5, "{}", "source-1", 8),
        )
    except sqlite3.IntegrityError as exc:
        if "goal_revisions.objective_binding_required" not in str(exc):
            raise
    else:
        raise AssertionError("memory: new goal revision without objective binding was accepted")
    db.rollback()

    # A binding that crosses owner scope fails its deferred composite FK at commit.
    cross_owner_goal_id = bytes([13]) * 16
    db.execute("BEGIN")
    db.execute(
        "INSERT INTO goals (goal_id,created_at_ms,updated_at_ms) VALUES (?,?,?)",
        (cross_owner_goal_id, 9, 9),
    )
    db.execute(
        """INSERT INTO goal_revision_objective_bindings
        (goal_id,goal_revision,owner_ref,objective_id,objective_version,created_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (cross_owner_goal_id, 1, "owner-2", "obj-1", 1, 9),
    )
    db.execute(
        """INSERT INTO goal_revisions
        (goal_id,revision,description,state,priority,constraints_json,reason_ref,created_at_ms)
        VALUES (?,?,?,?,?,?,?,?)""",
        (cross_owner_goal_id, 1, "cross-owner goal", "proposed", 0.5, "{}", "source-1", 9),
    )
    try:
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
    else:
        raise AssertionError("memory: cross-owner objective binding was accepted")
    # Query projection source columns are additive; legacy rows remain NULL and are
    # never assigned invented provenance, uncertainty or confidence.
    db.execute(
        """INSERT INTO environment_observations
        (observation_id,owner_ref,device_id,environment_scope,observed_at_ms,
         recorded_at_ms,source_id,collection_method,collector_version,
         platform_context_json,observed_facts_json,sensitivity,limitations_json,
         validity_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("obs-1","owner-1","00000000-0000-4000-8000-000000000001","device",
         10,11,"source:1","platform_probe","probe-v1","{}","[]",1,"[]",None),
    )
    if db.execute(
        "SELECT owner_ref,observed_facts_json FROM environment_observations WHERE observation_id='obs-1'"
    ).fetchone() != ("owner-1","[]"):
        raise AssertionError("memory: environment observation projection source did not round-trip")

    expect_integrity_error(
        db, "capability descriptor without schema version",
        """INSERT INTO capability_descriptors
        (capability_id,descriptor_version,provider_id,device_scope,discovery_epoch,
         descriptor_json,descriptor_sha256,status,source_ref,first_discovered_at_ms)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        ("cap-test",1,"provider","device","epoch","{}","a"*64,"discovered","source",1),
    )
    db.execute(
        """INSERT INTO capability_descriptors
        (capability_id,descriptor_version,provider_id,device_scope,discovery_epoch,
         descriptor_json,descriptor_sha256,status,source_ref,first_discovered_at_ms,
         descriptor_schema_version)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        ("cap-test",1,"provider","device","epoch","{}","a"*64,"discovered","source",1,"1.0"),
    )

    experience_id = bytes([14]) * 16
    db.execute(
        """INSERT INTO experiences
        (experience_id,source_type,observed_at_ms,recorded_at_ms,content_ref,
         sensitivity,provenance_ref,retention_state)
        VALUES (?,?,?,?,?,?,?,?)""",
        (experience_id,"test",1,1,"artifact:test",0,"source:test","active"),
    )
    expect_integrity_error(
        db, "representation without method/source lineage",
        """INSERT INTO representations
        (representation_id,experience_id,representation_type,content_json,method,
         uncertainty_json,created_at_ms)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([15])*16,experience_id,"test","{}","method:test","{}",2),
    )
    db.execute(
        """INSERT INTO representations
        (representation_id,experience_id,representation_type,content_json,method,
         uncertainty_json,created_at_ms,method_version,source_refs_json)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (bytes([15])*16,experience_id,"test","{}","method:test","{}",2,"1.0",'["experience:test"]'),
    )

    expect_integrity_error(
        db, "context without provenance/uncertainty",
        """INSERT INTO contexts
        (context_id,version,scope,valid_from_ms,attributes_json,provenance_ref,created_at_ms)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([16])*16,1,"owner",1,"{}","source:test",2),
    )
    db.execute(
        """INSERT INTO contexts
        (context_id,version,scope,valid_from_ms,attributes_json,provenance_ref,
         created_at_ms,provenance_refs_json,uncertainty_json)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (bytes([16])*16,1,"owner",1,"{}","source:test",2,'["source:test"]',"{}"),
    )

    expect_integrity_error(
        db, "memory record without provenance/uncertainty",
        """INSERT INTO memory_records
        (memory_id,memory_type,content_ref,summary,sensitivity,status,created_at_ms,updated_at_ms)
        VALUES (?,?,?,?,?,?,?,?)""",
        (bytes([17])*16,"semantic","artifact:test","test",0,"active",2,2),
    )
    db.execute(
        """INSERT INTO memory_records
        (memory_id,memory_type,content_ref,summary,sensitivity,status,created_at_ms,
         updated_at_ms,provenance_refs_json,uncertainty_json)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (bytes([17])*16,"semantic","artifact:test","test",0,"active",2,2,'["source:test"]',"{}"),
    )

    expect_integrity_error(
        db, "prediction without conditions/evidence",
        """INSERT INTO predictions
        (prediction_id,subject_ref,expected_outcome_json,evaluation_criteria_json,
         created_at_ms,status)
        VALUES (?,?,?,?,?,?)""",
        (bytes([18])*16,"subject:test","{}","{}",2,"open"),
    )
    db.execute(
        """INSERT INTO predictions
        (prediction_id,subject_ref,expected_outcome_json,evaluation_criteria_json,
         horizon_end_ms,created_at_ms,status,conditions_json,confidence,evidence_refs_json)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (bytes([18])*16,"subject:test","{}","{}",10,2,"open","{}",0.6,'["evidence:test"]'),
    )

    check_database("memory smoke insert", db)
    db.close()


def test_events() -> None:
    db = execute_chain("events", [
        "aurion_events.base.sql",
        "aurion_events.migration_v2.sql",
        "aurion_events.migration_v3.sql",
        "aurion_events.migration_v4.sql",
        "aurion_events.migration_v5.sql", "aurion_events.migration_v6.sql",
    ])
    require_columns(db, "task_runs", {"revision", "owner_id", "failure_ref"})
    require_columns(db, "operation_details", {"policy_decision_ref"})
    require_columns(db, "operation_steps", {
        "step_key", "target_store", "idempotency_key", "request_digest",
        "expected_revision", "result_digest", "started_at_ms", "completed_at_ms",
        "compensation_for_step_number",
    })
    require_columns(db, "recovery_journal", {"operation_step_id"})
    required = (
        "task_run_id", "task_definition_ref", "state", "priority",
        "budget_json", "created_at_ms", "updated_at_ms",
    )
    values = (bytes([1]) * 16, "task-definition", "queued", 1.0, "{}", 1, 1)
    placeholders = ",".join("?" for _ in required)
    try:
        db.execute(
            f"INSERT INTO task_runs ({','.join(required)}) VALUES ({placeholders})",
            values,
        )
    except sqlite3.IntegrityError as exc:
        if "task_runs.owner_id_required" not in str(exc):
            raise
    else:
        raise AssertionError("events: ownerless new task row was accepted")
    db.execute(
        f"INSERT INTO task_runs ({','.join(required)},owner_id) "
        f"VALUES ({placeholders},?)",
        (*values, "owner-1"),
    )
    try:
        db.execute(
            "UPDATE task_runs SET owner_id='owner-2' WHERE task_run_id=?",
            (bytes([1]) * 16,),
        )
    except sqlite3.IntegrityError as exc:
        if "task_runs.owner_id_immutable" not in str(exc):
            raise
    else:
        raise AssertionError("events: bound task owner was reassigned")
    # The store assigns the append sequence; callers do not supply it.
    db.execute(
        """INSERT INTO events
        (event_id,message_id,message_type,contract_version,producer_component,
         producer_instance_id,correlation_id,occurred_at_ms,recorded_at_ms,
         payload_json,payload_digest,sensitivity,retention_class)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([2]) * 16, bytes([3]) * 16, "test.event.v1", "1.0",
         "ddl-smoke", bytes([4]) * 16, bytes([5]) * 16, 1, 1, "{}", "a" * 64,
         0, "operational"),
    )
    sequence = db.execute("SELECT event_sequence FROM events").fetchone()[0]
    if sequence != 1:
        raise AssertionError(f"events: expected first store-assigned sequence 1, got {sequence}")

    # Cross-store evolution sagas require ordered, immutable, idempotent steps.
    operation_id = bytes([40]) * 16
    expect_integrity_error(
        db, "saga operation missing idempotency key",
        """INSERT INTO operations
        (operation_id,operation_type,state,created_at_ms,updated_at_ms)
        VALUES (?,?,?,?,?)""",
        (bytes([39])*16,"evolution.candidate.activate","proposed",9,9),
    )
    expect_integrity_error(
        db, "saga operation empty idempotency key",
        """INSERT INTO operations
        (operation_id,operation_type,state,idempotency_key,created_at_ms,updated_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (bytes([38])*16,"evolution.candidate.activate","proposed","",9,9),
    )
    db.execute(
        """INSERT INTO operations
        (operation_id,operation_type,state,idempotency_key,created_at_ms,updated_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (operation_id,"evolution.candidate.activate","proposed","saga-idem-1",10,10),
    )
    expect_integrity_error(
        db, "duplicate saga operation idempotency key",
        """INSERT INTO operations
        (operation_id,operation_type,state,idempotency_key,created_at_ms,updated_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (bytes([37])*16,"evolution.candidate.activate","proposed","saga-idem-1",10,10),
    )
    step_columns = (
        "operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,"
        "step_key,target_store,idempotency_key,request_digest,expected_revision,started_at_ms"
    )
    step_values = (
        bytes([41])*16,operation_id,0,bytes([42])*16,"pending",11,
        "governance.authorize","aurion_governance.db",
        "saga-idem-1:governance.authorize","a"*64,3,11
    )
    step_placeholders = ",".join("?" for _ in step_values)
    expect_integrity_error(
        db, "saga step without stable identity/idempotency",
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (bytes([43])*16,operation_id,1,bytes([44])*16,"pending",11),
    )
    db.execute(
        f"INSERT INTO operation_steps ({step_columns}) VALUES ({step_placeholders})",
        step_values,
    )
    expect_integrity_error(
        db, "duplicate saga step key",
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (bytes([45])*16,operation_id,1,bytes([46])*16,"pending",12,
         "governance.authorize","aurion_governance.db",
         "saga-idem-1:governance.authorize:retry","b"*64),
    )
    expect_integrity_error(
        db, "duplicate target-store saga idempotency key",
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (bytes([47])*16,operation_id,1,bytes([48])*16,"pending",12,
         "governance.audit","aurion_governance.db",
         "saga-idem-1:governance.authorize","b"*64),
    )
    expect_integrity_error(
        db, "saga step identity mutation",
        "UPDATE operation_steps SET step_key='rewritten' WHERE operation_step_id=?",
        (bytes([41])*16,),
    )
    expect_integrity_error(
        db, "saga step history deletion",
        "DELETE FROM operation_steps WHERE operation_step_id=?",
        (bytes([41])*16,),
    )
    expect_integrity_error(
        db, "saga terminal state without completion timestamp",
        "UPDATE operation_steps SET state='succeeded',started_at_ms=NULL,completed_at_ms=12 WHERE operation_step_id=?",
        (bytes([41])*16,),
    )
    db.execute(
        """UPDATE operation_steps
        SET state='succeeded',started_at_ms=11,completed_at_ms=12,result_ref='approval:receipt',
            result_digest=?
        WHERE operation_step_id=?""",
        ("c"*64,bytes([41])*16),
    )
    expect_integrity_error(
        db, "saga recovery journal without step binding",
        """INSERT INTO recovery_journal
        (journal_id,operation_id,phase,local_store,intended_transition,state,
         created_at_ms,updated_at_ms)
        VALUES (?,?,?,?,?,?,?,?)""",
        (bytes([49])*16,operation_id,"governance","aurion_governance.db",
         "approval_committed","applied",12,12),
    )
    expect_integrity_error(
        db, "recovery journal local store differs from saga step target",
        """INSERT INTO recovery_journal
        (journal_id,operation_id,phase,local_store,intended_transition,state,
         created_at_ms,updated_at_ms,operation_step_id)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (bytes([50])*16,operation_id,"memory","aurion_memory.db",
         "memory_commit","applied",12,12,bytes([41])*16),
    )
    db.execute(
        """INSERT INTO recovery_journal
        (journal_id,operation_id,phase,local_store,intended_transition,state,
         created_at_ms,updated_at_ms,operation_step_id)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (bytes([49])*16,operation_id,"governance","aurion_governance.db",
         "approval_committed","applied",12,12,bytes([41])*16),
    )

    # Saga identity and recovery linkage must not be mutable after creation.
    expect_integrity_error(
        db, "saga operation type downgrade bypass",
        "UPDATE operations SET operation_type='ordinary.operation' WHERE operation_id=?",
        (operation_id,),
    )
    expect_integrity_error(
        db, "saga idempotency key rewrite",
        "UPDATE operations SET idempotency_key='rewritten' WHERE operation_id=?",
        (operation_id,),
    )
    expect_integrity_error(
        db, "saga operation history deletion",
        "DELETE FROM operations WHERE operation_id=?",
        (operation_id,),
    )
    expect_integrity_error(
        db, "recovery journal store reassignment",
        "UPDATE recovery_journal SET local_store='aurion_memory.db' WHERE journal_id=?",
        (bytes([49])*16,),
    )
    expect_integrity_error(
        db, "recovery journal step unlink",
        "UPDATE recovery_journal SET operation_step_id=NULL WHERE journal_id=?",
        (bytes([49])*16,),
    )
    expect_integrity_error(
        db, "recovery journal saga history deletion",
        "DELETE FROM recovery_journal WHERE journal_id=?",
        (bytes([49])*16,),
    )
    expect_integrity_error(
        db, "terminal saga step inserted without timestamps",
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (bytes([51])*16,operation_id,2,bytes([52])*16,"succeeded",13,
         "memory.activate","aurion_memory.db","saga-idem-1:memory.activate","d"*64),
    )
    expect_integrity_error(
        db, "compensation step references nonexistent prior step",
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest,compensation_for_step_number)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([53])*16,operation_id,2,bytes([54])*16,"pending",13,
         "governance.compensate","aurion_governance.db",
         "saga-idem-1:governance.compensate","e"*64,99),
    )
    expect_integrity_error(
        db, "compensation step cannot cross target stores",
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest,compensation_for_step_number)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([55])*16,operation_id,2,bytes([56])*16,"pending",13,
         "memory.compensate","aurion_memory.db",
         "saga-idem-1:memory.compensate","f"*64,0),
    )
    db.execute(
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest,compensation_for_step_number)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([57])*16,operation_id,1,bytes([58])*16,"pending",13,
         "governance.compensate","aurion_governance.db",
         "saga-idem-1:governance.compensate","1"*64,0),
    )
    db.execute(
        """INSERT INTO operation_steps
        (operation_step_id,operation_id,step_number,action_id,state,updated_at_ms,
         step_key,target_store,idempotency_key,request_digest,started_at_ms,completed_at_ms)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([59])*16,operation_id,2,bytes([60])*16,"succeeded",14,
         "memory.evaluate","aurion_memory.db","saga-idem-1:memory.evaluate","2"*64,13,14),
    )
    db.commit()
    check_database("events smoke insert", db)
    db.close()


def test_governance() -> None:
    db = execute_chain("governance", [
        "aurion_governance.base.sql", "aurion_governance.migration_v2.sql",
        "aurion_governance.migration_v3.sql", "aurion_governance.migration_v4.sql",
    ])
    require_columns(db, "outbox", {
        "outbox_id", "message_id", "destination", "envelope_json", "state",
        "attempt_count", "next_attempt_at_ms", "created_at_ms", "published_at_ms",
        "last_error_ref",
    })
    require_columns(db, "permissions", {
        "owner_ref", "status", "approval_ref", "policy_version_ref"
    })
    require_columns(db, "governance_audit", {
        "owner_ref", "evidence_refs_json", "correlation_id"
    })
    require_columns(db, "data_disclosures", {
        "owner_ref", "evidence_refs_json", "correlation_id"
    })
    for table in ("policies", "permissions", "approval_requests",
                  "approval_decisions", "governance_audit", "data_disclosures"):
        if not db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone():
            raise AssertionError(f"governance: missing expected table {table}")
    db.execute("BEGIN")
    db.execute(
        """INSERT INTO policies
        (policy_id,policy_name,policy_version,policy_document_json,protected,active,created_at_ms)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([8]) * 16, "rollback-probe", 1, "{}", 0, 1, 3),
    )
    db.execute(
        """INSERT INTO outbox
        (outbox_id,message_id,destination,envelope_json,state,created_at_ms)
        VALUES (?,?,?,?,?,?)""",
        (bytes([9]) * 16, bytes([10]) * 16, "event-archive", "{}", "pending", 3),
    )
    db.rollback()
    if db.execute("SELECT 1 FROM policies WHERE policy_name='rollback-probe'").fetchone():
        raise AssertionError("governance: policy survived rollback without its outbox")
    if db.execute("SELECT 1 FROM outbox WHERE message_id=?", (bytes([10]) * 16,)).fetchone():
        raise AssertionError("governance: outbox survived policy rollback")
    # Owner-scoped permission/audit projections reject new records without their
    # required owner and evidence/correlation lineage.
    policy_id = bytes([30]) * 16
    db.execute(
        """INSERT INTO policies
        (policy_id,policy_name,policy_version,policy_document_json,protected,active,created_at_ms)
        VALUES (?,?,?,?,?,?,?)""",
        (policy_id,"projection-test",1,"{}",0,1,1),
    )
    # Approval requests must be owner/session bound; a decision must match the
    # exact pending request, owner, digest and expiry, and may occur only once.
    request_id = bytes([34]) * 16
    request_fields = (
        "request_id,operation_id,requester_id,operation_digest,operation_summary,"
        "risk_class,data_categories_json,recipient_summary,policy_version_ref,"
        "requested_at_ms,expires_at_ms,state"
    )
    request_values = (
        request_id,bytes([35])*16,"owner-1","a"*64,"test approval","R1",
        "[]","test recipient","policy:projection-test:1",10,20,"pending"
    )
    expect_integrity_error(
        db, "approval request without owner/session",
        f"INSERT INTO approval_requests ({request_fields}) VALUES ({','.join('?' for _ in request_values)})",
        request_values,
    )
    db.execute(
        f"INSERT INTO approval_requests ({request_fields},owner_ref,owner_session_ref) "
        f"VALUES ({','.join('?' for _ in request_values)},?,?)",
        (*request_values,"owner-1","session-1"),
    )
    expect_integrity_error(
        db, "approval decision with mismatched digest",
        """INSERT INTO approval_decisions
        (decision_id,request_id,authenticated_owner_ref,decision,approved_digest,
         decided_at_ms,authentication_context_ref)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([36])*16,request_id,"owner-1","approved","b"*64,15,"session-1"),
    )
    db.execute(
        """INSERT INTO approval_decisions
        (decision_id,request_id,authenticated_owner_ref,decision,approved_digest,
         decided_at_ms,authentication_context_ref)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([36])*16,request_id,"owner-1","approved","a"*64,15,"session-1"),
    )
    request_state = db.execute(
        "SELECT state FROM approval_requests WHERE request_id=?", (request_id,)
    ).fetchone()[0]
    if request_state != "approved":
        raise AssertionError("governance: exact approval decision did not advance request state")
    expect_integrity_error(
        db, "second decision for one approval request",
        """INSERT INTO approval_decisions
        (decision_id,request_id,authenticated_owner_ref,decision,approved_digest,
         decided_at_ms,authentication_context_ref)
        VALUES (?,?,?,?,?,?,?)""",
        (bytes([37])*16,request_id,"owner-1","denied","a"*64,16,"session-1"),
    )
    expect_integrity_error(
        db, "permission without owner/status/policy version",
        """INSERT INTO permissions
        (permission_id,subject_id,capability_id,operation_scope_json,resource_scope_json,
         data_scope_json,side_effect_scope_json,environment_scope_json,valid_from_ms,
         grant_source,policy_id,created_at_ms,status,policy_version_ref)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([31])*16,"subject","capability","{}","{}","{}","{}","{}",1,
         "owner_grant",policy_id,2,"active","policy:projection-test:1"),
    )
    db.execute(
        """INSERT INTO permissions
        (permission_id,subject_id,capability_id,operation_scope_json,resource_scope_json,
         data_scope_json,side_effect_scope_json,environment_scope_json,valid_from_ms,
         grant_source,policy_id,created_at_ms,owner_ref,status,approval_ref,policy_version_ref)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([31])*16,"subject","capability","{}","{}","{}","{}","{}",1,
         "owner_grant",policy_id,2,"owner-1","active",None,"policy:projection-test:1"),
    )
    expect_integrity_error(
        db, "governance audit without owner/evidence/correlation",
        """INSERT INTO governance_audit
        (audit_id,actor_id,action,details_digest,occurred_at_ms,record_digest)
        VALUES (?,?,?,?,?,?)""",
        (bytes([32])*16,"owner-1","permission.grant","d"*64,3,"e"*64),
    )
    db.execute(
        """INSERT INTO governance_audit
        (audit_id,actor_id,action,details_digest,occurred_at_ms,record_digest,
         owner_ref,evidence_refs_json,correlation_id)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (bytes([32])*16,"owner-1","permission.grant","d"*64,3,"e"*64,
         "owner-1",'["evidence:grant"]',"00000000-0000-4000-8000-000000000001"),
    )
    expect_integrity_error(
        db, "data disclosure without owner/evidence/correlation",
        """INSERT INTO data_disclosures
        (disclosure_id,provider_id,purpose,data_categories_json,payload_digest,
         policy_version_ref,disclosed_at_ms,outcome)
        VALUES (?,?,?,?,?,?,?,?)""",
        (bytes([33])*16,"provider","purpose","[]","f"*64,"policy:1",4,"sent"),
    )
    db.execute(
        """INSERT INTO data_disclosures
        (disclosure_id,provider_id,purpose,data_categories_json,payload_digest,
         policy_version_ref,disclosed_at_ms,outcome,owner_ref,evidence_refs_json,correlation_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (bytes([33])*16,"provider","purpose","[]","f"*64,"policy:1",4,"sent",
         "owner-1",'["evidence:disclosure"]',"00000000-0000-4000-8000-000000000002"),
    )
    db.commit()
    check_database("governance projection smoke", db)
    db.close()


def main() -> int:
    if sqlite3.sqlite_version_info < (3, 38, 0):
        raise AssertionError(
            f"SQLite {sqlite3.sqlite_version} is below proposed minimum 3.38.0"
        )
    test_memory()
    test_events()
    test_governance()
    print(
        f"PASS: all three SQLite stores and seventeen ordered DDL files executed; "
        f"SQLite {sqlite3.sqlite_version}; FK/integrity checks passed; "
        "memory v4/v5/v6/v7, event v3/v4/v5/v6 and governance v2/v3/v4 outbox/objective/approval/query-projection/saga-ledger smoke invariants passed."
    )
    print(
        "LIMIT: host smoke validation only; Android/Termux baseline, crash/restore, "
        "concurrency, cross-store recovery and runtime handlers remain unverified."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
