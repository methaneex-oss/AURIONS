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

## Verification state (updated 2026-11-21)

- Exact branch-head CI run [44844452501](https://github.com/methaneex-oss/AURIONS/actions/runs/44844452501) on commit `518a6e535b359da34d2bd960c9d6ca89e0d51f73`: **passed**.
- CMake configure: passed.
- C++ compilation and linking: passed.
- CTest: passed (1/1 integration test).
- The integration test verifies process-restart persistence, JSON round-tripping, provenance retention, lexical ranking, bounded context assembly, omission accounting, and both explicit and default search/context argument forms.
- This is host CI evidence only. It does not validate Termux/Android, local/cloud inference, belief revision, reasoning, behavioural adaptation, synchronization or OS interaction.


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


## Follow-up source-audit corrections (2026-11-20 to 2026-11-21)

Source audit and successive CI runs exposed and corrected the following:

- Search/context JSON now has no duplicate `recorded_at_ms` key and every context evidence item includes that timestamp.
- Integration JSON parsing rejects duplicate object keys.
- SQLite LIKE predicates now use the valid one-character `!` escape expression. An earlier checkpoint note incorrectly described the intended escape as a backslash; the actual committed SQL uses `ESCAPE '!'`.
- The CLI had an off-by-one argument bug: search and context treated the optional limit/max-items argument as the query. This was the cause of empty retrieval results. The CLI now reads the query from `argv[4]` and the optional bound from `argv[5]`, with correct argument counts for both default and explicit limits.
- Test diagnostics preserve subprocess stdout/stderr and report returned candidates when ranking assertions fail.
- Integration coverage now exercises both explicit and default search/context argument forms.



## CI runner-policy repair

The first available push-triggered workflow run was inspected rather than treated as a code failure. It failed before checkout/build because repository Actions policy requires every action to be pinned to a full commit SHA; the workflow used the floating tag `actions/checkout@v4`. The workflow now pins checkout to the immutable v4.2.2 commit `11bd71901bbe5b1630ceea73d27597364c9af683`.

- Workflow file: `.github/workflows/cpp-core.yml`
- Repair commit: `430a760917fb3cd720c597bf48286db50aa337a8`
- The failed run's only executed step was runner setup; CMake configure, compilation and CTest did not run.
- No workflow run/status for the pinning commit was visible at checkpoint time. The repaired workflow is therefore **not yet validated**.


## First complete CI execution and test failure (2026-11-20)

The pinned workflow did execute on commit `c3278176f9b8bea5ace7d59a2bc8b0dc5d2fe793`:

- CMake configure: passed.
- C++ compilation/link: passed.
- CTest: failed; 0/1 tests passed.
- Failure location: `core/cpp/tests/experience_store_integration.py:67`, during the contextual search command `experience search ... "AURIONS local brain" 10`.
- The first test helper discarded subprocess stderr, hiding the underlying SQLite/runtime diagnostic. The helper now raises an assertion containing command, stdout and stderr so the next CI run exposes the root cause.
- Diagnostic-instrumentation commit: `c84b55090bdd026cca5dbd32084b90cd2136fede`.

This is the first actual compiler/test evidence for the implementation: the C++ code compiles, but the integration test is failing. Do not describe this milestone as passing. Next action is to obtain the instrumented run's stderr, fix the underlying defect, rerun CTest, and only then connect the memory context to reasoning.

## Branch integration warning

GitHub's compare endpoint currently reports `impl/experience-continuity` as diverged from `main` (merge base `7327938183157ba54d932745612dfd4720981f30`, branch 14 commits behind main and a reported 1342 commits ahead). This branch must not be merged or rebased blindly. Before integration, inspect the actual commit graph and reconcile its implementation with the canonical mainline persistence and cognitive contracts. Preserve this isolated branch until a safe integration plan is established.


## Verified implementation milestone — 2026-11-21

The previous test failures were resolved at their causes, not by weakening assertions:

1. Run `44842625000` on `dbf21f48` confirmed that the first SQL-escape correction was incomplete; SQLite still rejected the generated ESCAPE expression.
2. Commit `b3aec61d153134f2f14ee2d3d7c65d1ada4bb4b3` corrected the emitted SQL to use `ESCAPE '!'`. Its run confirmed the SQL error was gone but exposed an empty search result.
3. Commit `d16cd603c94e602033b1283cb04ba7d6e677af92` fixed the root cause: the CLI read the optional limit instead of the query. CI run [44844335370](https://github.com/methaneex-oss/AURIONS/actions/runs/44844335370) passed configure, build and CTest.
4. Commit `518a6e535b359da34d2bd960c9d6ca89e0d51f73` added explicit regression coverage for default search and context arguments. CI run [44844452501](https://github.com/methaneex-oss/AURIONS/actions/runs/44844452501) passed configure, build and CTest (1/1).

The currently verified code head is `518a6e535b359da34d2bd960c9d6ca89e0d51f73`.

## Next capability milestone

Do not expand subsystem count for its own sake. The next implementation must make a real, testable capability change:

- Introduce an evidence-backed belief update that consumes persisted experience references, records support/contradiction and provenance, and preserves immutable revision history.
- Prove that new evidence changes the stored belief state in a principled, inspectable way, that contradictory evidence can revise it, and that the result survives process restart.
- Then provide a cognitive consumer boundary that can use retrieved evidence and revised beliefs in a later response/decision. Do not label evidence assembly alone as understanding or learning.
- Keep the algorithm general and evidence-driven; do not encode fixed stimulus-to-response rules or predetermined beliefs.
- Inspect and reconcile with the existing canonical persistence contracts before adding parallel tables or an unrelated second memory database.

The current implementation still provides persistence and lexical recall only. It does not yet understand natural language, revise beliefs, reason, learn strategies, adapt behaviour, or invoke a model. Those capabilities remain unimplemented and must be demonstrated by end-to-end tests.


## Capability milestone — persistent evidence-based belief revision (2026-11-21)

**Implementation:** Added `BeliefStore` using the existing canonical memory table names and shapes for `knowledge_items`, `beliefs`, `belief_revisions`, `evidence_items` and `belief_revision_evidence`. The implementation stores these records in the same SQLite database as experiences; it does not create a separate belief database.

The new CLI supports:
- `belief create`: create a proposition/domain with a prior confidence and immutable initial revision.
- `belief evidence`: attach an active experience as supporting, contradicting or contextual evidence.
- `belief show`: inspect the proposition, complete revision chain, confidence, epistemic status and per-revision evidence provenance.

Confidence is updated through log-odds evidence accumulation. Evidence reliability (0.5 to less than 1.0) and relevance (0 to 1) determine update magnitude. Supporting evidence increases confidence; contradictory evidence decreases it; contextualizing evidence is retained without changing confidence. The same experience cannot be counted twice for the same belief. Each update is committed transactionally and appends a revision linked to its predecessor.

**Behavioural test evidence:** The integration test creates a 0.5 prior, applies supporting evidence with reliability 0.8 and obtains 0.8 confidence, applies equally reliable contradictory evidence and returns to 0.5, then adds contextual evidence without shifting confidence. It verifies provenance, stance, duplicate rejection, revision sequence and recovery of the complete revision history through a fresh CLI process.

- CI run [44844792537](https://github.com/methaneex-oss/AURIONS/actions/runs/44844792537) on code commit `e33278914d419e0579e0081cad41999f89f19d00`: **passed**.
- CMake configure: passed.
- C++ build/link: passed.
- CTest: passed (1/1 integration test).
- README updated with the verified capabilities and current CLI contract in commit `0091e177bff2997e4f923e51067f497bd1159fc3`.

**Limits that remain explicit:** Evidence stance, reliability and relevance are currently caller-supplied. AURIONS does not yet infer whether raw language or observations support a proposition. The evidence updater assumes conditional independence and does not model correlated sources. It is an evidence-revision primitive, not autonomous natural-language understanding, a reasoning model, skill acquisition or behavioural adaptation.

## Next capability work

Connect contextual memory retrieval and belief revision to a cognitive consumer that can use evidence in a later response or decision. The consumer must distinguish retrieved observations from beliefs, expose uncertainty and provenance, and avoid turning unverified text into truth. Then add prediction/outcome records and test whether observed consequences revise future predictions or strategies across process restart. Do not claim general learning until the later behaviour measurably changes.
