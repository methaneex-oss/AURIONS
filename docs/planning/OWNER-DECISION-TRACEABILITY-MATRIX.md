# AURIONS — Owner Decision Traceability Matrix

- **Status:** Builder traceability baseline; IN PROGRESS pending complete repository audit and owner review.
- **Authority:** Section 3 and operational-authority sections of [Initial Engineering Specification](INITIAL-ENGINEERING-SPECIFICATION.md). That source remains authoritative.
- **Purpose:** Prove that owner decisions are reflected in architecture, contracts, roadmap and acceptance criteria without converting engineering proposals into owner decisions.
- **Evidence rule:** A reference to a document is not proof of implementation or validation. All rows below are currently **SPECIFIED** unless a separate test/review result is explicitly cited.

## 1. Foundational principle decisions

| Owner decision | Architectural disposition | Contract / test trace | Roadmap | Status / remaining gap |
|---|---|---|---|---|
| MP-01 — Evolve everything, including foundational values/objectives, subject to protected authority and safeguards | Cognitive mechanism architecture §4.17 defines isolated evolution proposals, evaluation, approval, activation and rollback; governance retains protected authority. | `evolution.change.propose`; `evolution.candidate.evaluate/activate/rollback`; CM-017; R5/AU tests | WP-13 | SPECIFIED. Verify protected-value change lifecycle and recovery end-to-end before activation work. |
| MP-02 — Continuous development; no fixed developmental stages | System architecture §12 describes dependency/evidence gates rather than fixed developmental stages; roadmap WPs are dependency constraints, not intelligence stages. | Evolution proposal lifecycle; roadmap status discipline | WP-13, continuous across WPs | SPECIFIED. Ensure all older stage language is clearly historical/superseded. |
| MP-03 — Identify limitations, propose changes, test in isolation, seek approval to integrate | Cognitive architecture §§4.16–4.17; candidate quarantine, evaluation and approval path. | `self_model.update.propose`, `evolution.change.propose`; CM-016/017; LE-007/008 | WP-12, WP-13 | SPECIFIED. Isolated candidate sandbox and activation proof remain implementation/validation work. |
| MP-04 — Self-model of capabilities, limitations, confidence, resources, performance and goals | Cognitive architecture §4.16; `self_model_revisions` stores evidence-backed revisions. | `self_model.update.propose`; `self_model.updated.v1`; CM-016 | WP-13 | SPECIFIED. Calibration dataset/schema and measurable calibration acceptance remain to be finalized. |
| MP-05 — Core principles and user authority protected; other elements may adapt within constraints | Cognitive architecture §4.17 and governance architecture; learned state cannot grant authority or mutate protected policy. | R5; exact-operation approval; CM-017; NHC-008 | WP-04, WP-13 | SPECIFIED. Complete trace to every protected setting and policy mutation path. |
| MP-06 — Improve local model primarily through training | Python worker and model-training architecture; isolated training/evaluation artifacts and governed activation. | Worker protocol; LE-001…LE-008; candidate quarantine/rollback | WP-05, WP-12, WP-14 | SPECIFIED. Local training feasibility and model lifecycle are not device-validated; external hardware pipeline remains planned. |

## 2. Architecture decisions

| Owner decision | Architectural disposition | Contract / test trace | Roadmap | Status / remaining gap |
|---|---|---|---|---|
| IP-01 — Modular monolith with selected independent services where justified | System architecture §2; logical mechanisms do not require one process/service each. | CT-007 dependency-cycle test; component ownership matrix | WP-00…WP-15 | SPECIFIED. Service splits require measured justification, not assumption. |
| IP-02 — C++ core; other languages where better suited | System architecture technology baseline; Python is limited to isolated training/experiments/evaluation workers. | C++/Python worker protocol §5; worker failure tests | WP-00, WP-01, WP-14 | SPECIFIED. Final compiler/runtime versions and target ABI remain validation gates. |
| IP-03 — Model-independent interfaces from the beginning | Inference abstraction in system architecture §7; provider-specific adapters behind stable contracts. | Inference command/query/provider metadata and compatibility tests | WP-01, WP-05 | SPECIFIED. Exact schema and provider conformance fixtures remain open. |
| IP-04 — SQLite initially, defined schemas and migrations | Three-store DDL and migration protocol in source spec §26; migration proposals include v2/v3 additions. | DB-001…DB-015; migration integrity/fault acceptance | WP-02 | SPECIFIED. No DDL/migration has been executed on the target SQLite baseline. |
| IP-05 — Typed internal events and explicit interfaces | Versioned common envelope, command/query/event contracts, immutable event semantics. | CT-001…CT-007; shared schema fixtures required | WP-01 | SPECIFIED. Exact machine-readable body schemas and generated type/fixture pipeline remain open. |
| IP-06 — Design multi-device contracts early; implement distribution after single-device core works | System architecture §6 and contracts §9 define authenticated domain changes, conflicts, tombstones and recovery; implementation deferred. | SY-001…SY-008; device pairing/revocation tests | WP-16 after core; contracts prepared earlier | SPECIFIED. No direct SQLite file replication; cross-runtime state ownership must be explicit. |
| IP-07 — Training pipeline supports capable external hardware and lightweight local experiments where feasible | Python worker isolation and artifact/evaluation pipeline. | Worker process contract; LE-001…LE-008; artifact tests | WP-14 | SPECIFIED. External hardware orchestration and local feasibility are not implemented/validated. |
| IP-08 — Test mechanisms individually, then validate complete cognitive cycles | Dedicated cognitive architecture defines individual responsibilities and integrated CM scenarios. | CM-001…CM-020; CG-001…CG-010 | WP-07…WP-12 | SPECIFIED. Test fixtures and executable integration tests do not yet exist. |
| IP-09 — Use external libraries when they reduce development time without compromising design | Dependency audit procedure and explicit technology decision criteria. | SBOM/license/security audit; clean reproducible build | WP-00, WP-05, WP-14 | SPECIFIED. Actual dependency selection and audit remain open. |
| IP-10 — First milestone: persistent local assistant that converses, remembers, retrieves, reasons through task and retains outcomes | First usable release product definition; cloud and offline-mobile targets were later owner-decided concurrently. | PR-01…PR-18; CM/CG/LE tests | WP-15 | SPECIFIED. Product approval, target-device validation and exact first permitted local action remain open. |

## 3. Detailed engineering baselines

| Baseline | Architectural disposition | Contract / test trace | Roadmap | Status / remaining gap |
|---|---|---|---|---|
| UQ-01 — Separate storage systems for memory domains | Three SQLite files: memory/domain, events/recovery and governance. | Store ownership and transaction rules; DB tests | WP-02 | SPECIFIED. DDL execution/fault validation outstanding. |
| UQ-02 — Separate Python workers for training/experiments; typed process messages | Isolated worker supervisor, bounded JSON protocol, artifact intake; no live authority. | Worker request/progress/result/failure schema; crash/timeout tests | WP-14 | SPECIFIED. Machine schemas, sandbox limits and executable tests remain open. |
| UQ-03 — In-process and separate-process inference remain possible; benchmark phone before choosing | JNI/shared library versus IPC remains unresolved until actual-device spike. | Platform validation procedure | WP-05, WP-11, WP-15 | BLOCKED on target-device measurements. |
| UQ-04 — Persist durable experiences, state changes, actions and outcomes; sample transient diagnostics | Durable experience, memory, belief, prediction, goal, plan, operation, outcome and learning state; attention/diagnostics are selectively transient. | Persistence, event and retention tests | WP-02, WP-03, WP-07…WP-13 | SPECIFIED. Verify each domain's retention and durability classification. |
| UQ-05 — Evaluation/dataset infrastructure before choosing fine-tuning targets | Frozen baselines, data manifests, held-out evaluation and artifact provenance precede model target selection. | LE-001…LE-008 | WP-12, WP-14 | SPECIFIED. No fine-tuning target is silently selected. |
| UQ-06 — Hybrid knowledge trust/revision; provisional beliefs then consolidation after evidence | Belief revisions preserve evidence, contradiction and epistemic status. | CM-003, CM-020, CG-004 | WP-08 | SPECIFIED. Confidence calibration and consolidation criteria need executable fixtures. |
| UQ-07 — Broad tool access with policy checks at execution boundary | Dynamic capability discovery and extensible adapters; policy independently enforced at execution. | AD-001…AD-015, CAP-001…CAP-004, AU-001…AU-012 | WP-06, WP-11 | SPECIFIED. Broad access is limited to discoverable, supported, authorized interfaces; it does not imply privilege bypass. |
| UQ-08 — Protected rules may be proposed for change, but require approval and recovery | Evolution candidates isolated; R5 approval, audit, rollback and recovery. | CM-017; protected-change/AU tests | WP-04, WP-13 | SPECIFIED. Implementation and recovery validation outstanding. |
| UQ-09 — Separate logical stores and SQLite files for durable events and protected governance | Memory, events/recovery and governance DB ownership; no cross-file foreign keys. | DB-001…DB-015; OP and AU suites | WP-02, WP-03, WP-04 | SPECIFIED. Migration and cross-store fault tests outstanding. |
| UQ-10 — Vector search optional; replaceable retrieval; benchmark conventional retrieval first | Retrieval abstraction; conventional indexes first; vector retrieval only if benchmark justifies it. | Retrieval relevance/provenance benchmarks | WP-08 | SPECIFIED. Benchmark evidence not yet available. |
| UQ-11 — Durable operation IDs, local transactions, idempotency, explicit commit states, recovery journal and reconciliation | Operation projection, details, attempts, event log, outbox/inbox and recovery journal. | OP-001…OP-008; DB-012…DB-014 | WP-02, WP-03, WP-11 | SPECIFIED. Proposed schema changes unexecuted; crash/fault tests outstanding. |
| UQ-12 — Policy enforcement independent of model reasoning and at execution boundary | Governance and local gateway are separate from reasoning/planning; default deny on ambiguity. | AU-001…AU-012; AD-010; NHC-008 | WP-04, WP-11 | SPECIFIED. Security enforcement is not implemented or pen-tested. |
| UQ-13 — Approval bound to exact operation and authenticated owner session, durable audit | Approval digest binds operation, parameters, target, capability version, policy, data and recipient. | AU tests; OP-006; exact-operation approval tests | WP-04, WP-11 | SPECIFIED. Authentication/key implementation and replay tests outstanding. |
| UQ-14 — Persistent background scheduler with budgets, checkpoints, cancellation and resumption | Task runs, checkpoints, deadlines, budgets and recovery coordinator. | OP-008; CM-006/018; task restart tests | WP-03, WP-10 | SPECIFIED. Android background execution remains platform-dependent and unvalidated. |
| UQ-15 — Encrypt sensitive persistent data/backups; key management separate | Key separation, rotation, backup/recovery and device key lifecycle defined. | Security/key lifecycle review; backup/restore tests | WP-04, WP-02 | SPECIFIED. Actual key custody and cryptographic implementation remain open. |
| UQ-16 — Explicit retention/deletion across indexes, references, backups and synchronized copies | Retention jobs, artifact lineage, tombstones, offline-device protection and 30-day backup expiry. | ART-001…ART-004; SY-004…SY-006; deletion fault tests | WP-02, WP-16 | SPECIFIED. Actual deletion/restore execution and sync propagation remain unvalidated. |
| UQ-17 — Repeatable held-out improvement against baseline and regression testing | Frozen baseline, held-out data, unseen variations, repeated runs, regression checks, quarantined candidates and rollback. | LE-001…LE-008; CM-011…CM-013 | WP-12, WP-14 | SPECIFIED. No learning improvement is claimed before executable evidence exists. |

## 4. Operational authority and online-resource decisions

| Owner decision | Architectural disposition | Contract / test trace | Status / remaining gap |
|---|---|---|---|
| Proactive bounded autonomy | Persistent objectives, decomposition, budgets, checkpoints, cancellation, bounded retries, recovery and notification; consequential actions retain approval gates. | Scheduler/task contracts; OP-008; AU suite | SPECIFIED. First-release autonomy subset must remain bounded and owner-approved. |
| Policy-controlled autonomous resource utilization | Provider/capability metadata, local/remote routing, cost/reliability/privacy policy and fallback. | Provider permissions, data disclosure records, inference adapter contracts | SPECIFIED. Provider selection and actual provider security are not validated. |
| Contextual sharing/private information | Data minimization, explicit approval for sensitive external disclosure, provider scope and durable disclosure audit. | R3/R4 policy; AU tests; disclosure audit | SPECIFIED. Actual egress enforcement and penetration tests outstanding. |
| 30-day historical-backup expiry | Immediate active deletion, index/reference cleanup, tombstones, exclusion from future backups and historical expiry within 30 days. | ART and SY deletion tests; retention job schema | SPECIFIED. Execution and restore tests outstanding. |

## 5. Traceability limitations and completion rule

- This matrix maps the current documented owner decisions; it does not authorize changes to them.
- Engineering details in architecture/contracts remain proposals until owner approval where they materially affect product behaviour, privacy, authority or release scope.
- A test ID is a planned test until executable fixtures and results exist.
- A DDL definition is proposed until executed against the pinned target SQLite baseline and fault-tested.
- Historical wording in source records remains for provenance; superseded proposals must not be treated as current authority.
- If a decision changes, update the source decision register first, then reconcile this matrix, product definition, architecture, contracts, roadmap and tests.

**Current disposition:** IN PROGRESS. The decision-to-document trace is specified, but full repository-wide consistency, executable validation, independent review of the exact final revision and owner planning-exit approval remain open.
