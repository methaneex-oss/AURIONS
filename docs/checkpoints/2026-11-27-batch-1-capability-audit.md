# AURIONS Batch 1 — Capability & Integration Audit

**Date:** 2026-11-27
**Branch:** `impl/experience-continuity`
**Verified HEAD:** `d99fbc3f91ae6f186963443b5e7bb6697bdfcbd9`
**Scope:** Five-objective audit: state/CI, inference boundary, integration contract, usable entry point, persistence reconciliation.
**Status:** AUDIT IN PROGRESS — this is not an acceptance report.

## 1. Live repository and CI

- Branch ref confirmed at `d99fbc3f91ae6f186963443b5e7bb6697bdfcbd9`.
- Model-baseline workflow `45993577645`: SUCCESS, but tested commit `ad683f8065fb9691125e26b2222b2f2d93ae15ac`, not current HEAD.
- C++ Core workflow `45993630763`: SUCCESS, but tested commit `d104aa1bd11495b49ea47a218cbb088f5ac3b3b6`, not current HEAD.
- Both intervening changes are documentation/checkpoint updates; this is not evidence of a source regression, but exact-head CI remains unverified.
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
- The CLI currently accepts prompt/query through argv in the C++ preview/model preview path; private prompt text can appear in process arguments. The Python provider CLI stdin mitigation does not automatically protect these C++ paths.
- Candidate output is explicitly quarantined and must not be described as active brain inference.
- Static source review is not a sandbox test: process isolation, filesystem/network access, resource exhaustion, malicious checkpoint behavior and Android/Termux behavior still need targeted execution tests.
- No live provider call or actual Android target validation is evidenced.

No concrete code defect is confirmed yet. Do not change the adapter until the remaining hostile tests and exact source paths are inspected.

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

The existing query-projection reconciliation is explicitly static: 29 query definitions/310 fields mapped to proposed sources; SQL/joins/owner filters/redaction/cursors and behavioral verification are not closed. Therefore:
- The prototype DB cannot be represented as canonical persistence closure.
- The candidate query-field inventory is not runtime evidence.
- A migration/integration plan must preserve the existing experience/belief/strategy data and provenance.
- Do not implement broad new tables before ownership and atomicity/recovery behavior are established.

## 6. External research comparison (initial)

Recent literature and architecture reports converge on the practical stack: model, planning/orchestration, working/episodic/semantic memory, tool/environment interaction, governance, and trajectory-level evaluation. A monolithic single-agent loop remains a reasonable starting point; multi-agent coordination is not a universal improvement and introduces coordination/failure overhead. Architecture choices should be benchmarked per task rather than copied as a brand-name framework.

References:
- Systematic review of agentic workflows, published 18 Nov 2026: https://link.springer.com/article/10.1007/s10791-026-10743-4
- Agentic AI systems survey (architecture, cognitive foundations, interaction, security and evaluation): https://www.sciencedirect.com/science/article/pii/S0925231226014475
- Survey on evaluation of LLM-based agents: https://aclanthology.org/2026.findings-acl.1330.pdf
- AgentArch benchmark comparing 18 enterprise configurations and reporting model/task-dependent architecture preferences: https://aclanthology.org/2026.aacl-long.44.pdf

Implication for AURIONS: use a small, integrated closed loop with explicit memory, evidence, planning, execution governance and postcondition observation; measure trajectory success, reliability, cost/latency, recoverability, context leakage and use of prior experience. Avoid adding multi-agent complexity before the integrated loop works.

## 7. Batch 1 test plan (not yet executed locally)

- Exact-head C++ and model-baseline CI.
- Hostile worker protocol cases: malformed/duplicate keys, wrong protocol/job/digest, missing fields, huge output, nonzero exit, hangs, stderr flood, request write/read errors.
- Prompt privacy tests for argv versus stdin.
- Context filtering tests: sensitivity, unverified belief, contradictory evidence, stale evidence and budget truncation.
- Candidate security: malformed checkpoint, unsafe serialization, wrong architecture/tokenizer, altered digest, resource-heavy candidate and activation/quarantine invariants.
- Conversation loop tests: first-turn response, memory recall, unrelated memory rejection, sensitive memory not leaked, restart persistence, contradiction handling and clear failure semantics.
- Persistence: execute all DDL/migrations against SQLite, migration from prototype store, transaction/failure/recovery, canonical ownership and query semantics.

## 8. Handoff priorities

1. Complete inference-boundary hostile testing and exact-head CI; fix only confirmed defects.
2. Write and validate a minimal versioned inference/cognition contract (request, response, context/evidence provenance, task scope, sensitivity, errors, cancellation, budgets).
3. Implement the bounded CLI conversation loop against that contract, with stdin privacy and tests.
4. Demonstrate a real response path using the currently owned candidate/runtime; report capability limitations honestly.
5. Persistence reconciliation and migration test plan; do not silently replace or discard current DB state.

**No merge, PR or main-branch changes. No owner acceptance implied.**
