# AURIONS proposed SQLite DDL

**Status: proposed planning artifacts. All three base schemas and eight additive migrations have executed in host-side CI smoke tests; they have not been applied to a user database or validated against the target Termux/Android SQLite build.**

These files are the machine-readable DDL source for the three independent SQLite stores. Memory migration v5 adds the memory-store transactional outbox required by the cross-store protocol. Memory migration v6 adds an owner-scoped binding from every new derived goal revision to an exact objective revision. Memory migration v7 adds explicit environment-observation, descriptor-schema, representation-lineage, context-uncertainty, memory-provenance, prediction-evidence and plan-context projection sources. Events migration v4 adds task failure and operation policy-decision references. Governance migration v2 adds the corresponding governance-store outbox; governance migration v3 binds approval requests to owner/session and enforces one exact decision per request; governance migration v4 adds owner-scoped permission and audit/disclosure projection fields. Memory migration v4 proposes owner-scoped, versioned persistence for objective records (distinct from derived goals), owner/scope details for existing evidence records, open-world entities, relationships, situation snapshots, context-dependent affordance hypotheses, interaction proposals and observed outcomes. The explanatory source specification in `docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md` Section 26 links to these files; do not maintain a second inline SQL copy there.

## Base schemas and migration order

| Store | Initial schema | Additive migrations |
|---|---|---|
| `aurion_memory.db` | [aurion_memory.base.sql](./aurion_memory.base.sql) | [migration v2](./aurion_memory.migration_v2.sql), [migration v3](./aurion_memory.migration_v3.sql), then [migration v4](./aurion_memory.migration_v4.sql), then [migration v5](./aurion_memory.migration_v5.sql), then [migration v6](./aurion_memory.migration_v6.sql), then [migration v7](./aurion_memory.migration_v7.sql) |
| `aurion_events.db` | [aurion_events.base.sql](./aurion_events.base.sql) | [migration v2](./aurion_events.migration_v2.sql), then [migration v3](./aurion_events.migration_v3.sql), then [migration v4](./aurion_events.migration_v4.sql) |
| `aurion_governance.db` | [aurion_governance.base.sql](./aurion_governance.base.sql) | [migration v2](./aurion_governance.migration_v2.sql), then [migration v3](./aurion_governance.migration_v3.sql), then [migration v4](./aurion_governance.migration_v4.sql) |

Each database has its own migration ledger, transaction, backup and recovery. Do not combine these scripts into one cross-database transaction. Cross-store IDs are validated by application services; cross-file foreign keys are prohibited.

## Proposed SQLite minimum

Proposed minimum supported SQLite version: **3.38.0**, subject to target validation. The DDL uses `STRICT` tables (supported from 3.37.0) and `json_valid()`; JSON functions became built-in by default in 3.38.0. The target build must not compile with `SQLITE_OMIT_JSON`. Verify the actual Termux/Android runtime, compile options, foreign-key enforcement, WAL and backup API before accepting this baseline.

References:
- [SQLite STRICT tables](https://sqlite.org/stricttables.html)
- [SQLite 3.38.0 release notes](https://sqlite.org/releaselog/3_38_0.html)
- [SQLite JSON functions](https://sqlite.org/json1.html)

## Host-side DDL execution evidence (2026-11-12)

The workflow runs `scripts/validate_sqlite_ddl.py` after schema and governance validation. Historical exact-head run [43383148511](https://github.com/methaneex-oss/AURIONS/actions/runs/43383148511) executed the then-current eleven SQL files. The current proposed chain contains fifteen files: three base schemas plus memory v2…v7, events v2…v4 and governance v2…v4. The new migrations add explicit query-projection sources and approval owner/session invariants; the updated runner now includes positive and negative smoke assertions for those additions. Exact-head run [43386377963](https://github.com/methaneex-oss/AURIONS/actions/runs/43386377963) on PR head `2a32dd13253ba501288d9b248a3048f8b0a3a31e` passed all nine workflow steps and executed all fifteen SQL files in order on host SQLite 3.46.1. It verified FK/integrity checks and the memory v7, events v4 and governance v3/v4 projection/approval invariants. This remains host-side smoke evidence only. It checked foreign-key enforcement, foreign-key integrity and database integrity after each file; objective insert; event sequence allocation; task-owner trigger; memory/governance local-outbox rollback; same-owner interaction-outcome linkage; exact goal-to-objective revision binding; rejection of unbound goal revisions; and rejection of cross-owner objective bindings.

This result establishes host-side DDL execution for that exact revision only. It does not establish target Termux/Android SQLite compatibility, crash/rollback/restore safety, concurrency behaviour, complete application-level invariants, cross-store recovery or runtime handler correctness. The automated check must remain enabled on future SQL and validator changes.

## Required validation before implementation approval

1. Execute each base schema on a clean database using the pinned minimum SQLite build.
2. Apply memory v2…v7, events v2…v4 and governance v2…v4 in order, with independent migration ledgers and checksums. Events v3 leaves legacy task owners NULL pending authoritative owner backfill; verify this gate and the new-task owner trigger.
3. Run `PRAGMA foreign_key_check`, `PRAGMA integrity_check`, JSON-function probes and migration-specific invariants after each step.
4. Test empty install, every supported upgrade, interrupted migration before/after commit, checksum mismatch, restore, disk-full, busy/locked, read-only/corrupt DB and process crash.
5. Verify all indexes, uniqueness/idempotency constraints, owner-scope query plans and target-device timings.
6. Confirm the 52 mapped command types (plus two deferred device commands) and all 29 query result-field mappings against table ownership, read/write semantics, store-local outbox boundaries and transaction scope.
7. Reconcile world-interaction schema references with memory v4 columns and event/operation references; prove that device-specific capability descriptors are not required for non-device means.
8. Record exact SQLite source/version/compile options and Termux/Android device/build identity.

The static DDL table and foreign-key ownership crosswalk is not SQL execution. The memory v4 and events v3 designs are first persistence mappings, not proof of complete semantic ownership: event bindings, canonical ID format, entity/evidence referential integrity (including evidence-details linkage to existing evidence IDs), cross-store interaction-operation linkage, retention/deletion policy and query contracts and task-control lifecycle/receipt tests still require closure. Events v3 introduces a durable task-control receipt ledger, but its retry-horizon and retention/tombstone procedure must be proven before deletion is enabled. Until all tests pass, the DDL and migration set remain **IN PROGRESS**.


## Store-local transactional outbox correction

See [Store-local Outbox and Cross-Store Saga Ownership Matrix](../../docs/planning/STORE-LOCAL-OUTBOX-AND-CROSS-STORE-SAGA-MATRIX.md) for the command-by-command transaction boundary and recovery protocol.

The cross-store protocol requires the authoritative store to commit its aggregate mutation and publication intent in one local transaction. The earlier DDL set violated that requirement: only `aurion_events.db` had an `outbox` table, while memory and governance mutations were mapped to that separate database. A separate event database cannot make those domain commits atomic.

Memory migration v5 and governance migration v2 add an identically shaped local `outbox` table to their respective stores. The existing event-store outbox remains for event-store-owned mutations and downstream dispatch. A relay copies committed local outbox envelopes into the central event archive using stable message IDs and payload digests; delivery is at least once and consumers deduplicate. A relay failure leaves the source outbox pending and does not roll back or misreport the already-committed domain mutation.

CI now executes the new migrations and verifies the common outbox columns. It also performs rollback probes proving that a memory aggregate insert and its local outbox row, and a governance policy insert and its local outbox row, roll back together. This is host-side SQLite evidence only; relay crash/replay, multi-store saga, target Android/Termux and power-loss tests remain open.


## Owner-bound objective-to-goal lineage

Memory migration v6 adds `goal_revision_objective_bindings`. Every new `goal_revisions` row must be paired in the same transaction with a binding to an exact `objective_records(objective_id, version, owner_ref)` row. The composite foreign key prevents a goal from referencing a missing objective revision or crossing owner scope. A trigger rejects new goal revisions without a binding. Insert the binding row first and the goal revision second in one transaction; deferred foreign keys validate both parent rows at commit.

Legacy goal revisions without a binding are not assigned an objective by inference. They must be quarantined from valid derived-goal queries and explicitly reconciled before they can be revised or treated as current owner-derived goals. Host CI tests valid linkage, missing-binding rejection and cross-owner rejection. This does not prove the goal handlers or legacy-data reconciliation runtime.
