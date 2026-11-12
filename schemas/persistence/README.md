# AURIONS proposed SQLite DDL

**Status: proposed planning artifacts. All three base schemas and five additive migrations have executed in host-side CI smoke tests; they have not been applied to a user database or validated against the target Termux/Android SQLite build.**

These files are the machine-readable DDL source for the three independent SQLite stores. Memory migration v4 proposes owner-scoped, versioned persistence for objective records (distinct from derived goals), owner/scope details for existing evidence records, open-world entities, relationships, situation snapshots, context-dependent affordance hypotheses, interaction proposals and observed outcomes. The explanatory source specification in `docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md` Section 26 links to these files; do not maintain a second inline SQL copy there.

## Base schemas and migration order

| Store | Initial schema | Additive migrations |
|---|---|---|
| `aurion_memory.db` | [aurion_memory.base.sql](./aurion_memory.base.sql) | [migration v2](./aurion_memory.migration_v2.sql), [migration v3](./aurion_memory.migration_v3.sql), then [migration v4](./aurion_memory.migration_v4.sql) |
| `aurion_events.db` | [aurion_events.base.sql](./aurion_events.base.sql) | [migration v2](./aurion_events.migration_v2.sql), then [migration v3](./aurion_events.migration_v3.sql) |
| `aurion_governance.db` | [aurion_governance.base.sql](./aurion_governance.base.sql) | No additive migration is specified yet |

Each database has its own migration ledger, transaction, backup and recovery. Do not combine these scripts into one cross-database transaction. Cross-store IDs are validated by application services; cross-file foreign keys are prohibited.

## Proposed SQLite minimum

Proposed minimum supported SQLite version: **3.38.0**, subject to target validation. The DDL uses `STRICT` tables (supported from 3.37.0) and `json_valid()`; JSON functions became built-in by default in 3.38.0. The target build must not compile with `SQLITE_OMIT_JSON`. Verify the actual Termux/Android runtime, compile options, foreign-key enforcement, WAL and backup API before accepting this baseline.

References:
- [SQLite STRICT tables](https://sqlite.org/stricttables.html)
- [SQLite 3.38.0 release notes](https://sqlite.org/releaselog/3_38_0.html)
- [SQLite JSON functions](https://sqlite.org/json1.html)

## Host-side DDL execution evidence (2026-11-12)

The workflow runs `scripts/validate_sqlite_ddl.py` after schema and governance validation. Latest exact-head run [43324236645](https://github.com/methaneex-oss/AURIONS/actions/runs/43324236645) on PR head `7c81d2629cfe40701f3319f33c19c0ec2ebf2ee0` executed all eight SQL files in the order above on host SQLite. It checked foreign-key enforcement, foreign-key integrity and database integrity after each file, then exercised selected objective insert, event sequence allocation and task-owner trigger invariants. Earlier run 43288000757 is retained as historical evidence.

This result establishes host-side DDL execution for that exact revision only. It does not establish target Termux/Android SQLite compatibility, crash/rollback/restore safety, concurrency behaviour, complete application-level invariants, cross-store recovery or runtime handler correctness. The automated check must remain enabled on future SQL and validator changes.

## Required validation before implementation approval

1. Execute each base schema on a clean database using the pinned minimum SQLite build.
2. Apply memory v2, v3, v4 and events v2, v3 in order, with independent migration ledgers and checksums. Events v3 leaves legacy task owners NULL pending authoritative owner backfill; verify this gate and the new-task owner trigger.
3. Run `PRAGMA foreign_key_check`, `PRAGMA integrity_check`, JSON-function probes and migration-specific invariants after each step.
4. Test empty install, every supported upgrade, interrupted migration before/after commit, checksum mismatch, restore, disk-full, busy/locked, read-only/corrupt DB and process crash.
5. Verify all indexes, uniqueness/idempotency constraints, owner-scope query plans and target-device timings.
6. Confirm the 51 mapped command types (plus two deferred device commands) and 29 query mappings against table ownership, read/write semantics, outbox boundaries and transaction scope.
7. Reconcile world-interaction schema references with memory v4 columns and event/operation references; prove that device-specific capability descriptors are not required for non-device means.
8. Record exact SQLite source/version/compile options and Termux/Android device/build identity.

The static DDL table and foreign-key ownership crosswalk is not SQL execution. The memory v4 and events v3 designs are first persistence mappings, not proof of complete semantic ownership: event bindings, canonical ID format, entity/evidence referential integrity (including evidence-details linkage to existing evidence IDs), cross-store interaction-operation linkage, retention/deletion policy and query contracts and task-control lifecycle/receipt tests still require closure. Events v3 introduces a durable task-control receipt ledger, but its retry-horizon and retention/tombstone procedure must be proven before deletion is enabled. Until all tests pass, the DDL and migration set remain **IN PROGRESS**.
