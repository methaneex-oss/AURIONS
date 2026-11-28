# Project Builder Self-Review — Code Audit and Defect Disposition

**Date:** 2026-11-28  
**Repository:** `methaneex-oss/AURIONS`  
**Branch:** `impl/experience-continuity`  
**Audit revision:** `31b252cce567d4de603d74568f259629293d1021`  
**Role:** Project Builder self-review. This is not an Independent Reviewer report or Director acceptance.

## 1. Scope and honesty boundary

This is a code-focused self-audit of the implemented runtime, persistence, inference/provider, candidate-training/admission, test and build paths. I compared implementation behavior and test coverage against the One-Brain Product Charter, the MCU/human-cognition engineering research reference, the architecture/review residuals, the README's capability statements, and current checkpoint/traceability notes.

Reviewed code areas include:
- C++ CLI/runtime and JSON/prompt/process boundaries.
- Experience, memory context, belief revision, representation, strategy and task-run stores.
- C++ inference-worker adapter, CMake/build/test registration.
- Python provider runtime, candidate inference/worker, tokenizer/model, synthetic and admitted-data training, artifact store, dataset admission and training worker.
- Integration and unit tests covering persistence, CLI, privacy/route checks, worker protocol, training, inference, admission, checkpoint lineage and recovery.

**Not claimed:** every schema, planning document, historical commit, external research source, Android behavior, or every possible input/failure has been exhaustively line-audited. CI is not a proof of absence of defects. No local build/test environment was available; test execution evidence is from GitHub Actions.

## 2. Defects found and corrected before handoff

### SR-01 — stale task-run failure reference
**Impact:** current state could retain an obsolete failure reference after recovery or cancellation.  
**Correction:** clear failure references on non-failure states; align the returned object and persisted row.  
**Regression:** blocked-to-cancelled checks both returned and persisted state.

### SR-02 — chat result referenced removed variables after atomic-turn API change
**Impact:** C++ compilation failed after the persistence method changed to return a `ConversationTurn`.  
**Correction:** output IDs from `turn.user.id` and `turn.assistant.id`.  
**Evidence:** CI failure at revision `82b3c5f`; correction committed.

### SR-03 — conversation persistence omitted `source_type` bind
**Impact:** conversation experience insertion failed against the NOT NULL column; turns could not persist.  
**Correction:** bind the insert's source-type parameter for both user and assistant rows.  
**Regression:** conversation persistence test now verifies source types, content, provenance and reads both rows back.

### SR-04 — C++ conversation test used `assert` in Release configuration
**Impact:** `NDEBUG` removed the assertions, so the test did not actually verify persistence.  
**Correction:** replace assertions with runtime `require` checks that throw on failure.

### SR-05 — rollback test's search assertion was a false positive
**Impact:** searching `second user` could return old conversation records because lexical retrieval matches `source_type` metadata; the test was not isolating partial persistence.  
**Correction:** search the unique term `second`; add SQLite trigger fault injection to abort the assistant insert after the user-side insert has begun. Verify no user experience remains after transaction rollback.

### SR-06 — admitted-model evaluation only measured the first window
**Impact:** validation and held-out losses could be dominated by one window and give misleading improvement evidence.  
**Correction:** deterministically evaluate up to eight evenly spaced windows across each split, aggregating token-weighted loss.

### SR-07 — deterministic training sampler could visit only a subset of windows
**Impact:** a fixed stride of 7 could cycle a fraction of samples when the window count shared a factor with 7.  
**Correction:** select a deterministic stride coprime with the number of start positions, ensuring the schedule can traverse every window.

### SR-08 — cognition accepted up to 4096-byte queries but retrieval rejected queries over 512 bytes
**Impact:** valid input within the CLI limit failed in experience/belief retrieval; context budget was also too small for the declared input range.  
**Correction:** align retrieval query bounds to 4096 bytes and increase cognition context assembly budget to 8192 bytes while the prompt builder still enforces its independent 8192-byte final prompt limit.  
**Regression:** a 660-byte chat query must succeed; 4097-byte stdin must still be rejected.

### SR-09 — context-budget edit introduced a C++ syntax error
**Impact:** build failed.  
**Correction:** restore the missing closing parenthesis. The exact-head matrix was rerun.

### SR-10 — admission evidence could be recorded with a policy version different from the one checked
**Impact:** the persisted admission ledger and candidate lineage could misstate which policy version authorized admission.  
**Correction:** `AdmissionResult` now carries the checked `policy_version_ref`; admission recording rejects a mismatch; candidate lineage stores it; candidate loader requires the policy and training-purpose fields.  
**Regression:** mismatch rejection and missing-policy-lineage rejection added.

These findings were not hidden or deferred into the Independent Review. They were corrected in the Builder pass.

## 3. CI and simulated failure evidence

### Previous failures that led to corrections
- `82b3c5f003`: C++ compilation failed because chat output referenced undeclared experience variables after the atomic persistence API changed.
- `6b26ff0e8a`: build succeeded, but conversation persistence integration failed (1 of 12 tests). The active test caught the missing source-type bind.
- `9562341403`: C++ compilation failed on a missing parenthesis in the context-budget call. Corrected.

### Current exact-head verification
- Current C++ Core run: **46138857523**, revision `31b252cce567d4de603d74568f259629293d1021`. All four matrix configurations completed successfully: GCC Ubuntu 22.04, GCC Ubuntu 24.04, Clang Ubuntu 24.04, GCC ASan+UBSan Ubuntu 24.04. All 12 CTest tests passed on the Ubuntu 22.04 job.
- Current AURIONS owned-model baseline run: **46138857482**, revision `31b252cce567d4de603d74568f259629293d1021`, completed **success**. The workflow exercised provider runtime tests, model/causal masking/training/inference/resume tests, C++ cognition and inference-adapter build, C++ preview of an admitted candidate, synthetic checkpoint creation, local checkpoint inference, and quarantined artifact publication.
- Schema-contract validation run **46121343495** passed on revision `341cdc7fdb`; schema sources were not changed during this self-review.

No local test run is claimed.

## 4. Architecture and research comparison

The implementation direction is consistent with the engineering principle **“engineer mechanisms; let behavior be acquired through experience”** at a primitive level:
- persistent experience and provenance;
- lexical retrieval/context assembly;
- evidence-linked belief revisions;
- representations linked to experiences;
- outcome-driven strategy selection with stored predictions/evaluations;
- durable task-run lifecycle/recovery records;
- a provider-backed chat slice that retrieves public context and atomically stores a successful conversation turn;
- an AURIONS-owned randomly initialized trainable model and a rights-gated candidate training path that remains quarantined.

The implementation does **not** yet constitute the integrated cognitive loop described by the charter/research:
- no objective/goal manager or autonomous planner;
- no OS observation/interface discovery/action gateway or real action dispatch;
- no independent postcondition observer;
- no online research acquisition pipeline;
- no integrated prediction/appraisal/attention/reasoning consumer that learns from independently observed outcomes;
- no cross-device synchronization/reconciliation runtime;
- no verified local/offline inference on Android/Termux;
- no live cloud endpoint validation;
- no model candidate activation or rollback workflow.

The current chat path is a bounded provider-inference loop, not AURIONS' complete brain or its owned model. The owned-model path is a small trainable baseline/candidate pipeline, not evidence of broad intelligence or generalized learning.

## 5. Residual risks and gaps (not represented as fixed)

1. **Dataset admission integrity:** the gate checks persisted authorization, scope, approval, expiry, revocation and manifest-seal records. It does not recompute the full manifest/authorization-check digest from canonical bytes or verify the policy-snapshot artifact itself. Training verifies source/split artifact bytes, but does not independently reconstruct the entire authorization proof. No training dispatcher or candidate activation exists; this remains a blocker before any real training authority.
2. **Data leakage:** split digests must differ and lineage must be bound, but content-level overlap/leakage between train, validation and held-out sets is not detected.
3. **Evaluation strength:** admitted training currently evaluates eight deterministic windows per split, not every token/window. This is a bounded smoke/initial evaluation and cannot substantiate generalization by itself.
4. **Retrieval:** lexical search can match source/provenance metadata and only scores a bounded recent candidate set. False positives and missed old memories remain possible; semantic retrieval is not implemented.
5. **Inference isolation:** the worker is a process/protocol boundary, not an OS sandbox. Filesystem/network isolation, malicious checkpoint stress, resource caps, cancellation-race testing and target-device isolation are unverified.
6. **Persistence:** the prototype stores are SQLite-backed but are not yet fully reconciled with the canonical three-store migration, query, outbox, retention/deletion and recovery contracts. Task-run schema migrations, journal tamper-evidence and concurrency/fault stress are incomplete.
7. **Privacy classification:** chat sensitivity is caller-supplied; automatic classification is not implemented. Cloud route requires explicit opt-in and public sensitivity, but the caller can mislabel private input.
8. **Platform/live evidence:** no Android/Termux, offline-device, live-provider, synchronization, OS-action, backup/restore or device crash evidence exists.

## 6. Self-review disposition

**Defects identified in the bounded implementation slice: corrected.**  
**C++ host matrix: passed at exact revision.**  
**Python/model/provider/admission workflow: passed at exact code revision.**  
**Full product/codebase readiness: NOT established.**  
**Independent Reviewer and Project Director gates: remain separate.**

I will not state “there should be no errors” or guarantee the user's testing will be error-free. The corrected regression suite materially reduces the risk, but live-device, integration, adversarial and untested behavior can still expose defects. The bounded self-review is ready for Independent Reviewer scrutiny with the residuals above—not as a claim that the whole AURIONS project is complete.
