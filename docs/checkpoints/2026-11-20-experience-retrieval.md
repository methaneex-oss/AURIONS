# AURIONS Builder Checkpoint — Experience Retrieval

**Checkpoint date:** 2026-11-20  
**Branch:** `impl/experience-continuity`  
**Code/documentation base before this checkpoint:** `c4326d8472d1e879ff7535c45e993053eca3c368`  
**Project direction:** [One-Brain Product Charter](../product/ONE-BRAIN-PRODUCT-CHARTER.md)

## Owner's governing direction

AURIONS is one persistent AI brain with local/offline and cloud/online access paths. It must learn from both local experience and online information, adapt from owner corrections and observed outcomes, and operate supported operating systems through objective-led interaction rather than a fixed command catalogue. Local and cloud access must share one coherent identity and reconciled cognitive state.

## Work completed in this milestone

- Added `ExperienceMatch` and a bounded `ExperienceStore::search(query, limit)` API.
- Implemented SQLite-backed lexical candidate retrieval over active experiences, searching content, source type and provenance using bound parameters.
- Added deterministic ranking: query-term coverage and content matches, then observed-time recency, then stable experience ID.
- Bounded search query size to 512 bytes, result limit to 1–100, and candidate scoring to 500 matching records.
- Preserved experience ID, content, source, provenance, timestamps and sensitivity in every returned match.
- Exposed `aurions experience search <database> <query> [limit]` through the CLI as JSON.
- Extended the process-restart integration test to check ranking, provenance, empty/invalid queries and no-match results.
- Updated README implementation status and preserved the one-brain product charter.

## Files changed in this milestone

- `core/cpp/include/aurions/experience_store.hpp`
- `core/cpp/src/experience_store.cpp`
- `core/cpp/src/main.cpp`
- `core/cpp/tests/experience_store_integration.py`
- `README.md`

## Evidence and limitations

- The exact SQLite `LIKE ... ESCAPE '\\'` query form was exercised separately against SQLite and returned the expected candidate row.
- **The C++ project build and CTest suite have not yet been executed in this session.** Do not mark the implementation test-passing until the branch's `C++ Core` workflow reports success.
- The repository workflow is configured to run on pushes to `impl/**`, but the available GitHub status lookup returned no status records at checkpoint time.
- This is lexical retrieval, not semantic/vector retrieval. Tokenization is currently ASCII-oriented and is not a multilingual tokenizer.
- The 500-result candidate cap bounds in-process scoring, **not SQLite scan cost**: the current leading-wildcard LIKE predicates can still scan the active experience corpus. This is acceptable only as an early small-corpus prototype. Add an indexed token/FTS strategy with measured target-device performance before treating retrieval as scalable.
- Search is a memory primitive only. No downstream cognitive consumer, belief revision, prediction feedback, adaptation or integrated learning loop has been implemented by this milestone.
- Existing persistence schema reconciliation, ownership/privacy enforcement, retention lifecycle and local/cloud synchronization remain separate open engineering work.

## Next builder actions

1. Obtain a real successful build and integration-test result for this exact branch revision; fix every failure before extending the system.
2. Add retrieval evaluation fixtures for partial matches, metadata-only matches, ties, sensitivity handling, larger stores and non-English text.
3. Connect retrieved experiences to the cognitive context/representation mechanism; do not stop at a search API.
4. Add evidence-backed knowledge/belief updates and prediction-versus-outcome feedback.
5. Demonstrate that a later decision changes because of a stored experience and remains changed after process restart.
6. Reconcile the experience store with the canonical three-store persistence architecture before expanding writes across stores.
7. Continue local/cloud inference and OS interaction behind the same brain identity/contracts; do not create two assistants.
8. Preserve the divergent branch history and review corrections. Do not merge the 1,321-commit-ahead / 14-commit-behind implementation branch into `main` blindly.

## Resume instructions

Start from `impl/experience-continuity`. Read this checkpoint and the One-Brain Product Charter first. Inspect the live branch head and working files before editing. The checkpoint's base SHA is a historical anchor, not a claim that it remains the current branch tip. Keep commits small enough to recover, and update this checkpoint after each substantial milestone.
