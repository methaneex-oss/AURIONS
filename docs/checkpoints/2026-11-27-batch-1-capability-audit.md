# AURIONS Batch 1 — Capability & Integration Audit

**Date:** 2026-11-27
**Branch:** `impl/experience-continuity`
**Latest inspected HEAD:** `8039c26a9f2202564e038a15cce7818ac9ea795b`
**Scope:** Five-objective audit: state/CI, inference boundary, integration contract, usable entry point, persistence reconciliation.
**Status:** AUDIT IN PROGRESS — this is not an acceptance report.

## 1. Live repository and CI

- Branch ref confirmed at `8039c26a9f2202564e038a15cce7818ac9ea795b`.
- Previous baseline C++ Core workflow `45993909208` passed at `d99fbc3`.
- New C++ Core run `45995771731` and model-baseline run `45995771649` were queued/in progress at the latest check on `8039c26`; exact conclusions must be checked before acceptance.
- C++ Core run `45995535753` passed at `3932e313fae081b0cd5a38444f641055a83da358`, which contains the bounded stdin source implementation; the subsequent hostile protocol test additions and worker sandbox documentation were not yet covered by a completed exact-head run.
- No local build/test run in this environment.

## 2. Inference boundary audit (source review)

Inspected:
- `core/cpp/include/aurions/inference_adapter.hpp`
- `core/cpp/src/inference_adapter.cpp`
- `core/cpp/src/main.cpp`
- `ml/python/aurions_ml/inference_worker.py`
- `ml/python/aurions_ml/inference.py`
- `core/cpp/tests/inference_adapter_integration.py`
- `core/cpp/tests/cognition_preview_integration.py`
- `ml/python/tests/cpp_model_preview_e2e.py`

### Positive evidence
- Worker is spawned using argv, not shell interpolation.
- Environment is allowlisted (PATH, PYTHONPATH, PYTHONHOME, HOME, TMPDIR, LANG, LC_ALL, LD_LIBRARY_PATH); common cloud credentials are excluded.
- IPC uses bounded request/output channels; response-size limits, timeout/kill, exit-status checks, job-ID binding, protocol-version checks, candidate digest matching, token-limit matching and quarantined status validation exist.
- Candidate checkpoint is loaded with `weights_only=True`, strict state-dict loading, format/tokenizer/architecture checks and quarantine/non-activation checks.
- Preview context filters sensitive observations and beliefs and omits unverified beliefs.
- Tests use fake workers for boundary/error tests and a candidate smoke E2E path.

### Limitations / risks to verify
- This is **candidate-preview inference**, not the user conversation runtime. The provider runtime remains a separate standalone primitive and is not integrated into the cognitive runtime/router.
- Preview prompt is assembled as a bounded evidence packet and uses the literal header “Evidence only; no actions.” It is not a complete conversational agent/task loop.
- **Corrected:** C++ model-preview and cognition-preview commands now accept `--stdin`; bounded readers cap model prompt at 8192 bytes and cognition query at 4096 bytes. Regression cases cover private prompt delivery via stdin and oversized stdin rejection. The provider runtime already supported stdin; this closes the separate C++ CLI argv exposure for these preview commands. It does not yet implement a normal conversation command.
- Hostile adapter regression cases were added for wrong job ID, wrong artifact digest, wrong protocol version, duplicate response keys, malformed JSON, worker rejection and oversized response. Existing Python worker tests already cover duplicate/unknown request fields, activation-eligible candidate rejection and oversized requests.
- Candidate output is explicitly quarantined and must not be described as active brain inference.
- **Security correction:** the Python worker is not an OS sandbox. It runs with the launching user's filesystem and network permissions unless deployment-specific isolation is applied. The worker docstring now states this explicitly. Environment allowlisting and protocol bounds are defense-in-depth, not sandboxing.
- Still unverified: filesystem/network isolation, resource exhaustion, malicious checkpoint stress, stderr flood, process cancellation races, and Android/Termux execution.
- No live provider call or actual Android target validation is evidenced.

A confirmed prompt privacy weakness was corrected. The full hostile test suite is added but awaits the current CI result.

## 3. Integration-contract gap

The existing code can retrieve context, assemble a prompt and request quarantined candidate output. It does not yet demonstrate a supported user interaction path where:
1. user objective/message is accepted through a product interface;
2. runtime establishes task/context/sensitivity scope;
3. relevant experience/belief evidence is retrieved and provenance preserved;
4. inference produces a response/decision proposal;
5. response is validated and presented;
6. interaction and outcome are recorded as experiences;
7. later retrieval uses those experiences to change a subsequent response.

The contract must separate *model-generated text*, *reasoning/decision proposal*, *authorized operation*, *observed outcome*, and *accepted learning*. Model text is untrusted and cannot self-authorize.

## 4. Entry point

The implemented CLI is a store/diagnostic interface: experience record/search/context/show, belief create/evidence/show, cognition context/preview, strategy choose/outcome and model preview. There is no complete supported conversation entry point evidenced in the source inspected. Preview commands are not the release CLI workflow.

The most useful near-term deliverable should be a bounded CLI conversation slice (not a UI redesign): message input; safe stdin; runtime/context selection; context retrieval; inference adapter contract; response output; durable record; restart/recall test. It must use the AURIONS-owned model path and must not silently promote a third-party hosted model to the product brain.

## 5. Persistence reconciliation

The current implemented stores (experience, belief and strategy) are SQLite-backed and accessed through the prototype CLI. README describes them as a bounded primitive. The canonical planning baseline specifies separate memory, event/recovery and governance stores plus ownership, migrations, outboxes/inboxes, artifacts, deletion/retention and cross-store recovery.

Correction after inspecting `scripts/validate_sqlite_ddl.py`: the repository already has substantive host-side persistence validation. It executes all three base SQLite stores plus 21 ordered migration files; checks foreign keys and integrity after each DDL step; validates key table/column/trigger presence; tests rollback atomicity for aggregate/outbox pairs; tests sync ledger, inbox idempotency, acknowledgements, checkpoints, causal gaps, conflicts, tombstones, restore lifecycle, owner scope, append-only constraints and source-column references for the documented projection inventory. This is materially stronger than a static schema-only check.
However, the query-projection reconciliation still explicitly does not implement/execute the 29 query handlers or prove their joins, owner filters, redaction, stable cursors and runtime behavior. The DDL script itself states that host smoke validation does not prove Android/Termux compatibility, crash/restore correctness, concurrency or cross-store runtime recovery. Therefore:
- The prototype DB cannot be represented as canonical persistence closure.
- The 21-file DDL chain has executable host-side smoke/invariant coverage; this must be retained and extended, not rewritten.
- The candidate query-field inventory is not proof that the 29 query handlers exist or behave correctly.
- A migration/integration plan must preserve the existing experience/belief/strategy data and provenance.
- Android/Termux, crash/restore, concurrency and cross-store runtime recovery remain unverified.
- Do not implement broad new tables before ownership and atomicity/recovery behavior are established.

## 6. External research comparison (initial)

Recent literature and architecture reports converge on the practical stack: model, planning/orchestration, working/episodic/semantic memory, tool/environment interaction, governance, and trajectory-level evaluation. A monolithic single-agent loop remains a reasonable starting point; multi-agent coordination is not a universal improvement and introduces coordination/failure overhead. Architecture choices should be benchmarked per task rather than copied as a brand-name framework.

References:
- Systematic review of agentic workflows, published 18 Nov 2026: https://link.springer.com/article/10.1007/s10791-026-10743-4
- Agentic AI systems survey (architecture, cognitive foundations, interaction, security and evaluation): https://www.sciencedirect.com/science/article/pii/S0925231226014475
- Survey on evaluation of LLM-based agents: https://aclanthology.org/2026.findings-acl.1330.pdf
- AgentArch benchmark comparing 18 enterprise configurations and reporting model/task-dependent architecture preferences: https://aclanthology.org/2026.aacl-long.44.pdf

Implication for AURIONS: use a small, integrated closed loop with explicit memory, evidence, planning, execution governance and postcondition observation; measure trajectory success, reliability, cost/latency, recoverability, context leakage and use of prior experience. Avoid adding multi-agent complexity before the integrated loop works.

## 7. Integration contract and brain-first correction

Added `docs/architecture/BRAIN-INFERENCE-LOCAL-CLOUD-CONTRACT-V1.md` and linked it from README. It specifies one C++ cognitive runtime with local/offline and cloud/online inference adapters; backend output is untrusted candidate text; local device authority remains local; cloud egress is policy-gated; online research becomes source-attributed experience; and cognitive learning is distinct from memory storage and model-weight training. It is a builder proposal, not implementation or owner acceptance.

This explicitly avoids treating UI work as the next priority. The first usable interaction path must be a thin CLI/runtime path into the brain, not a UI-first redesign.

## 8. Batch 1 test plan

- Exact-head C++ and model-baseline CI.
- Hostile worker protocol cases: malformed/duplicate keys, wrong protocol/job/digest, missing fields, huge output, nonzero exit, hangs, stderr flood, request write/read errors.
- Prompt privacy tests for argv versus stdin.
- Context filtering tests: sensitivity, unverified belief, contradictory evidence, stale evidence and budget truncation.
- Candidate security: malformed checkpoint, unsafe serialization, wrong architecture/tokenizer, altered digest, resource-heavy candidate and activation/quarantine invariants.
- Conversation loop tests: first-turn response, memory recall, unrelated memory rejection, sensitive memory not leaked, restart persistence, contradiction handling and clear failure semantics.
- Persistence: execute all DDL/migrations against SQLite, migration from prototype store, transaction/failure/recovery, canonical ownership and query semantics.

## 9. Handoff priorities

1. Finish current exact-head CI and close the added hostile worker tests; add platform isolation/resource/cancellation tests where feasible.
2. Validate the proposed inference/cognition contract against actual schemas and implement a shared C++ adapter interface used by both local and cloud backends.
3. Implement a brain-first C++ CLI conversation/task loop (not a UI), with bounded stdin, context retrieval, model route selection, validated output and durable interaction records.
4. Demonstrate real responses through the local route with network disabled, then the cloud route with explicit egress policy; prove both use the same cognitive context and persistence semantics. Do not present quarantined candidate preview as production inference.
5. Preserve and extend the existing SQLite DDL tests; implement/test query handlers and migration from the prototype stores, then validate crash/restart and Android/Termux behavior.

**No merge, PR or main-branch changes. No owner acceptance implied.**
