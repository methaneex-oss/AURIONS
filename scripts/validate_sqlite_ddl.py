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


def test_memory() -> None:
    db = execute_chain("memory", [
        "aurion_memory.base.sql",
        "aurion_memory.migration_v2.sql",
        "aurion_memory.migration_v3.sql",
        "aurion_memory.migration_v4.sql",
    ])
    require_columns(db, "objective_records", {
        "objective_id", "owner_ref", "version", "success_evidence_json"
    })
    require_columns(db, "evidence_details", {
        "evidence_id", "owner_ref", "epistemic_status", "sensitivity"
    })
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
    check_database("memory smoke insert", db)
    db.close()


def test_events() -> None:
    db = execute_chain("events", [
        "aurion_events.base.sql",
        "aurion_events.migration_v2.sql",
        "aurion_events.migration_v3.sql",
    ])
    require_columns(db, "task_runs", {"revision", "owner_id"})
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
    db.commit()
    check_database("events smoke insert", db)
    db.close()


def test_governance() -> None:
    db = execute_chain("governance", ["aurion_governance.base.sql"])
    for table in ("policies", "permissions", "approval_requests",
                  "approval_decisions", "governance_audit", "data_disclosures"):
        if not db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone():
            raise AssertionError(f"governance: missing expected table {table}")
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
        f"PASS: all three SQLite stores and eight ordered DDL files executed; "
        f"SQLite {sqlite3.sqlite_version}; FK/integrity checks passed; "
        "memory v4 and event v3 smoke invariants passed."
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
