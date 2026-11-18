# Independent Architecture Review — AURIONS

**Role:** Independent Reviewer  
**Exact revision reviewed:** `6f2cc12b6888b8a17291a8f6a44448d651a3582a`  
**PR:** #2 (`docs/complete-system-architecture`)  
**State at review:** open, draft, unmerged  
**Changed files (approx.):** 152  
**Review date:** 2026-11-18  

This report is an Independent Reviewer artifact. It was formed from primary repository sources (owner decision register, INITIAL-ENGINEERING-SPECIFICATION, architecture documents, planning contracts, schemas/fixtures, owner-decision matrix, planning-completion register, and GitHub PR/commit metadata). Project Builder summaries and prior author-side reviews were inspected only after independent assessment. No architecture, contract, schema, owner-decision, or policy files were modified by the Independent Reviewer.

---

## A. Project understanding

AURIONS is a trainable, adaptive intelligence system with a persistent cognitive core. Its governing principle is:

> **Engineer the mechanisms; let behaviour be acquired through experience.**

It is not a chatbot, thin LLM wrapper, or collection of fixed stimulus–response rules. Conversation is an interface capability, not the system identity. The intended system:

- Maintains durable experience, memory, knowledge/beliefs, prediction, appraisal, reasoning, goals/planning, decision, action, outcome evaluation, self-model and governed evolution.
- Operates local-first; remote resources are policy-controlled.
- Enforces owner authority through R0–R5 risk classes, exact-operation approval binding, execution-boundary policy, and fail-closed defaults.
- Supports bounded selective multi-device continuity (D-02 Option B) while keeping local effects, credentials, permissions and governance authoritative on each device.
- Owns and trains its primary model (randomly initialized decoder-only causal Transformer under AURIONS control); third-party pretrained weights are not the system brain.
- Demonstrates learning only through held-out evaluation against a frozen baseline, related unseen variations, and regression checks — not through conversation history or state mutation alone.

First usable release (D-01, owner-accepted PR-01…PR-20) requires a working cognitive runtime with experience/memory, reasoning, one narrowly scoped permitted local action (D-03 still staged), outcome feedback, and a bounded, reproducible model-training path (PR-19/PR-20). CLI is the engineering interface candidate; the product interface remains an owner decision.

No runtime implementation, training, dispatch, candidate activation or target-device validation has occurred. Host-side schema/DDL/CI evidence exists; it does not substitute for runtime or device evidence.

---

## B. Overall verdict

**ACCEPT WITH REQUIRED CORRECTIONS**

The architecture is broadly defensible, aligned with the owner decision register, and substantially more complete than earlier revisions. Machine-readable contracts, three-store DDL (21 files), D-02 selective-sync policy, command/query classification (D-04), event registry, scenario specifications, and candidate-lifecycle fixtures form a coherent planning baseline.

Material residual gaps remain in:

- Target-device / Termux feasibility evidence.
- Runtime enforcement of authorization, recovery, sync and training gates.
- Owner decisions still staged (D-03 first local action; export remains deny/disabled).
- Semantic closure of non-command event producers/consumers.
- Full C++/Python conformance and executable scenario evidence.

These do not invalidate the architectural direction. They block planning-exit and implementation authorization. The verdict applies only to SHA `6f2cc12b6888b8a17291a8f6a44448d651a3582a`.

---

## C. Findings register

| ID | Severity | Location / reference | Owner requirement / contract | Evidence & reasoning | Consequence if unresolved | Required correction / alternative | Blocks |
|----|----------|----------------------|------------------------------|----------------------|---------------------------|-----------------------------------|--------|
| IR-01 | High | Target-device / UQ-03, platform spikes | Measure before locking JNI vs IPC and performance thresholds | Host SQLite 3.46.1 and CI pass; no Termux/Android sustained-inference, memory, thermal, background or crash-isolation data on the ~6 GB target. | Risk of unviable process model or later expensive rework. | Execute documented device spike; record numbers before core–UI binding. | Implementation |
| IR-02 | High | D-03 | First permitted local action is owner decision | Explicitly staged; no action selected. | Cannot complete PR-07/PR-08 acceptance. | Obtain explicit owner selection of exact action, target and parameters. | First-release acceptance |
| IR-03 | High | D-02 runtime | Option B topology + Option A field policy accepted; export disabled | Policy registry and Memory v10 host-validated; peer enrollment, key lifecycle, projection/receiver handlers, executed SY scenarios and target evidence absent. | Sync cannot be claimed safe or complete. | Keep export deny/disabled; implement and pass SY-* + peer-trust gates before any export path. | Multi-device / WP-15 runtime |
| IR-04 | Medium | Event registry (94 events) | Typed events; explicit producers | 52 command-produced; 42 non-command triggers specified (15 Action Gateway + 27 trusted/internal). Owner acceptance of the 42 still open. | Ambiguous authority for non-command transitions. | Independent semantic review + owner acceptance of non-command producer/consumer matrix. | Semantic closure |
| IR-05 | Medium | Cross-store recovery | No distributed ACID; outbox + reconciliation | Host DDL/FK/integrity pass; crash, disk-full, concurrent, cross-store fault/replay and restore tests not executed on target. | Silent data loss or duplicate side-effects under real failure. | Require OP-*/DB-* fault suite on target before multi-store workflows are declared complete. | Persistence readiness |
| IR-06 | Medium | PR-19/PR-20 | Held-out learning + governed activation | Synthetic fixtures and digest vectors exist; no real training run, held-out improvement or runtime handlers. | Over-claim of learning readiness. | Keep fixtures as schema/transition tests only; runtime + measured improvement remain separate gates. | Learning claims |
| IR-07 | Medium | MD-16 dataset-rights | Fail-closed admission/revocation | Schemas and events present; authoritative enforcement at seal/admission not implemented. | Training on unauthorized data. | Implement fail-closed checks before any worker admission. | Training path |
| IR-08 | Low | Contract volume / checklist risk | Avoid premature complexity | Large corpus of schemas, scenarios and WPs. Risk of treating specification volume as progress. | False sense of readiness. | Prioritise first-release subset; keep later contracts phased. | None (hygiene) |
| IR-09 | Low | CI evidence scope | CI proves only executed checks | Multiple successful host runs cited; none prove Android/Termux, runtime sync, training or behavioural improvement. | Misreading CI as architecture validation. | Continue explicit evidence-boundary statements. | None |

No Critical finding that would require MAJOR REVISION or REJECT was identified. No owner decision is contradicted or silently weakened.

---

## D. Architecture assessment (Phase 3 areas)

1. **Architectural coherence** — Strong. Ownership matrix, dependency rules, modular-monolith centre and fail-closed defaults are consistent.  
2. **Cognitive architecture** — Sound. Interacting, iterative, interruptible mechanisms; open-world objective-led reasoning preserved.  
3. **No-hardcoding invariant** — Correctly enforced in contracts and NHC tests; safety invariants remain engineered.  
4. **Learning and adaptation** — Correct distinction between memory update, belief revision, strategy learning, model training and architecture evolution. Held-out standard intact.  
5. **First usable release** — Well-bounded by PR-01…PR-20. D-03 and device evidence still open.  
6. **Persistence and memory** — Three-store model, 21 ordered DDL files, outbox pattern, Memory v10 selective-sync schema host-validated. Target and fault evidence missing.  
7. **Runtime and technology** — C++ core + isolated Python workers + SQLite remains appropriate. Process boundary still measurement-gated.  
8. **Android / target-device** — Highest residual risk. Capability discovery, permission/authority separation and experience-driven capability learning are specified; measurements absent.  
9. **Multi-device** — D-02 Option B + Option A field policy correctly scoped; export disabled; runtime and peer-trust open.  
10. **Security and governance** — R0–R5, exact-operation binding, default-deny and audit preserved. Runtime enforcement and key lifecycle still required.  
11. **Autonomy** — Proactive bounded autonomy treated as system-wide constraint with narrow first-release exposure.  
12. **Failure handling** — Operation state machine, UNCERTAIN handling, reconciliation and recovery rules are among the strongest sections. Executable fault evidence still needed.  
13. **Implementation sequencing** — Work-package order and dependency edges are coherent; WP-00 remains unmerged pending gates.  
14. **Maintainability / complexity** — Conservative; no premature microservices, brokers or mandatory vector DB.  
15. **Evidence quality** — Explicit Specified / Validated / Implemented distinction maintained. CI and host DDL correctly scoped.

---

## E. First-release assessment

Must work end-to-end on the target environment:

- Reproducible local build and restart-safe durable state.  
- Local conversation via model-independent inference.  
- Provenance-linked experience persistence and retrieval.  
- Bounded objective + versioned plan with checkpoints.  
- One owner-selected, narrowly scoped, reversible local action through the authorized gateway (D-03).  
- Unauthorized / mismatched / expired actions denied.  
- Interrupted operations reconciled without unsafe duplicates.  
- Observed outcome recorded and used in a later related interaction.  
- No unauthorized external disclosure; resource limits and failures observable.  
- Bounded training path (PR-19/PR-20) with held-out evaluation, quarantine and governed activation/rollback — only after infrastructure exists.

The 14 PR-* conditions plus CM/CG/AU/OP/DB/SY scenario catalogues provide measurable assertions. Conversation-history “learning” or synthetic fixture passes alone are insufficient.

---

## F. Learning-proof assessment

Genuine learning requires:

- Versioned held-out dataset with provenance and leakage controls.  
- Frozen baseline vs candidate differing in an identified mechanism/artifact.  
- Predeclared metrics, related unseen variations, regression checks.  
- Experiment provenance (code, data, model hashes, seed, environment).  
- Quarantine until evaluation + owner/policy approval; reversible activation.

Memory update, belief revision, successful training execution or improved training loss do **not** satisfy the standard. Current PR-19/PR-20 fixtures are schema/transition tests only and correctly labelled as such.

---

## G. Planning and implementation readiness

**Design-level planning is substantially complete** for the first-release scope. Machine contracts, DDL, D-02 policy, D-04 classification, event registry and scenario specifications exist and are host-validated where claimed.

**Still required before planning-exit / implementation authorization:**

1. Explicit owner decision on D-03 (first local action).  
2. Target-device measurements (inference, memory, thermal, background, crash isolation).  
3. Runtime enforcement of authorization, recovery, dataset-rights and (when enabled) sync.  
4. Semantic acceptance of the 42 non-command event triggers/consumers.  
5. Executable fault, concurrency and restore evidence on target.  
6. C++/Python conformance for critical envelopes.  
7. Explicit owner planning-exit approval (separate from this review).

Implementation remains **blocked**. The Project Builder’s “NOT READY” disposition is correct.

---

## H. Recommended corrections (prioritized)

**Mandatory before planning exit / implementation**

1. Obtain D-03 owner selection of the exact first permitted local action.  
2. Execute and publish the target-device validation spike; use results to lock process boundary.  
3. Keep all commands/queries non-dispatchable until their individual gates pass.  
4. Preserve `default_action=deny` and `export_enabled=false` until peer trust, key lifecycle and SY runtime evidence exist.  
5. Close semantic review of the 42 non-command event producers/consumers.  
6. Require OP-*/DB-* fault and cross-store recovery evidence on target before multi-store claims.

**Mandatory before training path activation**

7. Implement fail-closed MD-16 dataset-rights checks at seal and admission.  
8. Keep PR-19/PR-20 fixtures as design tests only until real held-out improvement is demonstrated.

**Optional / hygiene**

9. Prioritise first-release subset of the large contract corpus.  
10. Continue explicit evidence-boundary language in all status reports.

---

## I. Final independent conclusion

The architecture at SHA `6f2cc12b6888b8a17291a8f6a44448d651a3582a` is technically sound in direction, aligned with the owner’s recorded decisions and foundational principle, and sufficiently complete as a **planning baseline** for the remaining evidence and owner gates.

It is **not** yet ready for planning exit, implementation authorization, command dispatch, training activation or merge. The residual blockers are empirical (device measurements, runtime enforcement, fault evidence) and decision (D-03, export enablement). Once those gates are closed and verified, the architecture can support a disciplined first usable release that demonstrates interacting mechanisms, durable experience feedback and a governed training path without over-claiming learning or autonomy.

**Verdict: ACCEPT WITH REQUIRED CORRECTIONS.**  

This report applies only to the exact reviewed SHA. Even ACCEPT does not authorize implementation, planning exit, or merge.

---

*Independent Reviewer artifact — 2026-11-18*
