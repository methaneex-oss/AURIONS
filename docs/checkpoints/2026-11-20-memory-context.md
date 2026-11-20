# AURIONS Builder Checkpoint — Memory Context Assembly

**Checkpoint date:** 2026-11-20  
**Branch:** `impl/experience-continuity`  
**Code/documentation base before this checkpoint update:** `dab0bf1766dde249fa096d8048e121469a2439d6`  
**Previous checkpoint:** [Experience retrieval](2026-11-20-experience-retrieval.md)  
**Product authority:** [One-Brain Product Charter](../product/ONE-BRAIN-PRODUCT-CHARTER.md)

## Owner's product direction

AURIONS is one persistent intelligence with local/offline and cloud/online access paths. Both paths share the same identity and evolving cognitive state. It learns from local experience and online information, adapts from owner corrections and observed outcomes, and should discover means to operate supported operating systems rather than being restricted to a fixed command catalogue.

## Work added since the previous checkpoint

The experience store now has a contextual retrieval API and CLI. This milestone adds a cognitive-context boundary on top of it:

- Added `MemoryContextBuilder`, which retrieves ranked experiences and assembles a bounded, provenance-preserving evidence packet.
- Context assembly is limited to 1–50 evidence items and 256 bytes–64 KiB.
- The serialized-payload estimate accounts for JSON escaping and reserves overhead for metadata/delimiters.
- Oversized or over-budget evidence is omitted rather than silently exceeding the configured budget; the packet reports omitted count.
- Each evidence item retains its experience ID, source type, content, provenance, observation and recording timestamps, sensitivity and relevance score.
- Added `aurions experience context <database> <query> [max-items]` JSON CLI output.
- Added `memory_context.cpp` to the CMake library and extended the integration test for context ordering, provenance, item cap, invalid item count and JSON escaping of quotes/newlines.
- Updated the repository README to distinguish the evidence-packet builder from actual reasoning or learning.

## Files added/changed

- Added `core/cpp/include/aurions/memory_context.hpp`
- Added `core/cpp/src/memory_context.cpp`
- Updated `core/cpp/src/main.cpp`
- Updated `CMakeLists.txt`
- Updated `core/cpp/tests/experience_store_integration.py`
- Updated `README.md`

## Verification state

- SQLite LIKE/ESCAPE query syntax was separately exercised with SQLite and returned the expected row.
- **No C++ build or CTest run has been completed in this environment.** The branch's C++ Core workflow is configured for pushes to `impl/**`, but the available status and workflow-run connectors do not expose push-triggered runs; the status lookup returned no status records. Do not call this test-passing until actual CI evidence is retrieved.
- A direct checkout/build attempt from this environment could not resolve GitHub's host, so no local build was possible.
- Tests have been authored but not executed. Their assertions are not evidence of passing behaviour.

## Known engineering limitations

- Retrieval is ASCII-oriented lexical matching, not semantic/vector retrieval and not multilingual tokenization.
- SQL uses leading-wildcard LIKE predicates. The 500-candidate cap bounds in-process scoring but **does not bound SQLite's scan cost**; this is suitable only for an early small corpus. Add indexed token/FTS retrieval and measure on target devices before scaling.
- The memory context builder is an evidence assembler, not a reasoning engine. It does not decide whether retrieved claims are true, update beliefs, infer skills, or change behaviour.
- Sensitivity is preserved as metadata but this store/context builder does not enforce authorization or redaction. A downstream cognitive consumer must not treat metadata as an access-control substitute.
- Canonical three-store persistence reconciliation, retention enforcement, encrypted sensitive storage, multi-device synchronization, local/cloud inference and OS autonomy remain open.
- The implementation branch remains substantially divergent from `main`; do not merge it blindly.

## Next actions — continue without waiting for routine approval

1. Obtain a successful build and CTest result for the exact branch head; repair all failures.
2. Add test coverage for context byte-budget edge cases and JSON escaping.
3. Replace scan-heavy lexical retrieval with indexed retrieval while preserving deterministic ranking and provenance.
4. Connect the evidence packet to the existing cognitive reasoning/context contracts; ensure it can affect subsequent reasoning, not merely be displayed.
5. Implement evidence-backed belief revision with provenance, uncertainty and contradiction handling.
6. Connect predictions to observed outcomes and show experience-dependent behavioural adaptation across process restart.
7. Reconcile storage with the canonical memory/events/governance databases before broadening persistence.
8. Continue local/cloud inference and OS interaction behind the same brain identity and state contracts.

## Resume instructions

Continue from `impl/experience-continuity`. Read this checkpoint and the previous experience-retrieval checkpoint. Inspect the live branch head and current source before editing. Preserve existing work and review corrections. Keep recoverable commit boundaries and update the checkpoint after each substantial milestone.


## Follow-up source-audit corrections (2026-11-20)

A subsequent source-level audit found and corrected defects in the CLI/retrieval path:

- Corrected SQLite LIKE escaping to use a one-character backslash escape expression. The prior generated SQL supplied a two-character ESCAPE expression, which SQLite rejects with `ESCAPE expression must be a single character`.
- Removed the duplicate `recorded_at_ms` key from search JSON.
- Added `recorded_at_ms` to each memory-context evidence item, matching the provenance/timestamp contract and the existing integration assertion.
- Strengthened the integration test JSON parser to reject duplicate object keys instead of silently accepting them.

The SQLite ESCAPE expression was checked directly against Python's SQLite binding: the one-character form succeeds and the two-character form fails as expected. This is a focused SQL syntax check, **not** a C++ build or execution of the integration suite. The full CMake build and CTest remain unverified.
