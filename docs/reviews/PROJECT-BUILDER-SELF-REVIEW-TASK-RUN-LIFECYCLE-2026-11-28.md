# Project Builder Self-Review Report — Task-Run Lifecycle

**Date:** 2026-11-28  
**Branch:** `impl/experience-continuity`  
**Review revision:** `fada5091c8044afa37ea52cbcc106a640989fcdb`  
**Review type:** Builder self-review, not an Independent Reviewer verdict  
**Scope:** Task-run persistence/state-transition implementation, schema initialization, regression tests, and exact-head CI.

## Governance
The Project Directorship and Team Operating Standard and Builder Operating Protocol were reviewed earlier in this builder run. The report remains a bounded review, not acceptance of WP-00–WP-09.

## Findings and corrections

### SR-01 — stale failure reference on non-failure states
**Finding:** Existing state could retain an old failure reference after transitioning into cancellation, completion, pause, running, queued, or lost state.
**Correction:** Clear the persisted and returned failure reference on non-failure states; retain/update it only for failed or blocked state transitions.
**Regression:** Blocked → cancelled asserts that both the transition return and persisted record have no stale failure reference.

### SR-02 — schema version not explicitly tracked
**Finding:** TaskRunStore created tables with `CREATE TABLE IF NOT EXISTS`, without a version marker or refusal to open a database from a newer schema.
**Correction:** Schema initialization is now in a SQLite transaction. `PRAGMA user_version` is checked; version > 1 is rejected; successful initialization sets version 1 atomically.
**Regression:** Tests assert fresh DB user_version=1 and reject a fixture at version 99.

### SR-03 — regression test could mask a late assertion failure
**Finding:** The test's success flag was set before the newly added failure-reference assertions. A later exception could be caught yet leave success true, allowing a false pass if cleanup succeeded.
**Correction:** Success is set only after every assertion in the full test completes. Transition-count assertion was also moved to an explicit failure check.
**Regression:** The test returns failure if any newly added assertion throws.

### SR-04 — migration test fixture directory was not created
**Finding:** The future-version fixture attempted SQLite open before the temporary root directory existed.
**Correction:** The test creates its temporary root before creating/opening fixture DBs.

## Re-review

- Read back the source and regression test after edits.
- Reviewed the GitHub compare patch from the prior review revision through the correction commits.
- Checked the transaction/rollback ordering: the schema-version statement is scoped/finalized before schema SQL; version marker update is committed with schema creation; a future version throws before schema mutation and unwinds the transaction.
- Checked test control flow: pass flag is assigned only after the new assertions; fixture root is created first; unsupported-version constructor must throw.
- CI was triggered at the latest code revision, but **not yet completed at the time of this report**. No compile/test pass is claimed for the latest correction set.

## Residual limitations (not falsely marked fixed)

1. Schema version 1 is a foundation marker; no future migration scripts exist yet because no later schema version is defined.
2. Journal tamper-evidence/cryptographic integrity, retention/compaction, backup/restore guarantees, and concurrent writer stress are not covered by this change.
3. Transition-state coverage is not exhaustive; only exercised cases are supported by the integration test.
4. TaskRunStore persists lifecycle records and transitions. It does not schedule/dispatch or execute tasks.
5. This review does not certify the full AURIONS codebase or WP-00–WP-09.

## Status
**In-scope findings SR-01 through SR-04 corrected in code/test.**  
**Latest exact-head CI verification: pending.**  
**Independent Reviewer and Project Director gates: remain separate.**
