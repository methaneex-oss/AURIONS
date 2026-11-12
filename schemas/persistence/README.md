# AURIONS proposed SQLite DDL

**Status: proposed planning artifacts only. None of these scripts has been executed, applied to a user database, or validated against the target Termux/Android SQLite build.**

These files are the machine-readable DDL source for the three independent SQLite stores. Memory migration v4 proposes owner-scoped, versioned persistence for open-world entities, relationships, situation snapshots, context-dependent affordance hypotheses, interaction proposals and observed outcomes. The explanatory source specification in `docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md` Section 26 links to these files; do not maintain a second inline SQL copy there.

## Base schemas and migration order

| Store | Initial schema | Additive migrations |
|---|---|---|
| `aurion_memory.db` | [aurion_memory.base.sql](./aurion_memory.base.sql) | [migration v2](./aurion_memory.migration_v2.sql), [migration v3](./aurion_memory.migration_v3.sql), then [migration v4](./aurion_memory.migration_v4.sql) |
| `aurion_events.db` | [aurion_events.base.sql](./aurion_events.base.sql) | [migration v2](./aurion_events.migration_v2.sql) |
| `aurion_governance.db` | [aurion_governance.base.sql](./aurion_governance.base.sql) | No additive migration is specified yet |

Each database has its own migration ledger, transaction, backup and recovery. Do not combine these scripts into one cross-database transaction. Cross-store IDs are validated by application services; cross-file foreign keys are prohibited.

## Proposed SQLite minimum

Proposed minimum supported SQLite version: **3.38.0**, subject to target validation. The DDL uses `STRICT` tables (supported from 3.37.0) and `json_valid()`; JSON functions became built-in by default in 3.38.0. The target build must not compile with `SQLITE_OMIT_JSON`. Verify the actual Termux/Android runtime, compile options, foreign-key enforcement, WAL and backup API before accepting this baseline.

References:
- [SQLite STRICT tables](https://sqlite.org/stricttables.html)
- [SQLite 3.38.0 release notes](https://sqlite.org/releaselog/3_38_0.html)
- [SQLite JSON functions](https://sqlite.org/json1.html)

## Required validation before implementation approval

1. Execute each base schema on a clean database using the pinned minimum SQLite build.
2. Apply memory v2 then v3, and events v2, with independent migration ledgers and checksums.
3. Run `PRAGMA foreign_key_check`, `PRAGMA integrity_check`, JSON-function probes and migration-specific invariants after each step.
4. Test empty install, every supported upgrade, interrupted migration before/after commit, checksum mismatch, restore, disk-full, busy/locked, read-only/corrupt DB and process crash.
5. Verify all indexes, uniqueness/idempotency constraints, owner-scope query plans and target-device timings.
6. Confirm the 43 command and 21 query registry mappings against table ownership, read/write semantics, outbox boundaries and transaction scope.
7. Reconcile world-interaction schema references with memory v4 columns and event/operation references; prove that device-specific capability descriptors are not required for non-device means.\n8. Record exact SQLite source/version/compile options and Termux/Android device/build identity.

The static DDL table and foreign-key ownership crosswalk is not SQL execution. The v4 design is a first persistence mapping, not proof of complete semantic ownership: event bindings, canonical ID format, entity/evidence referential integrity, cross-store interaction-operation linkage, retention/deletion policy and query contracts still require closure. Until all tests pass, the DDL and migration set remain **IN PROGRESS**.
