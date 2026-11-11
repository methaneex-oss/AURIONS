<!--
Source: AURION — Project Control Center & Initial Engineering Specification
Notion page: https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204
Retrieved: 2026-11-11
Purpose: faithful repository mirror of the planning record. Owner decisions, proposals,
unresolved items, validation gates and historical change notes must remain distinguishable.
This document is not evidence that implementation or validation has occurred.
-->

# AURIONS — Initial Engineering Specification (Planning Record)

> Repository/system identifier: **AURIONS** (owner naming clarification: the final “S” denotes “System”). The source planning record uses **AURION** as its working name and expansion. Preserve that historical wording; treat AURIONS as the repository/system identifier going forward.

> This file is a repository mirror of the canonical planning record. Update this file and the Notion control center together when a material decision changes. Do not silently overwrite owner decisions or historical rationale.

> Canonical source of truth for planning. Future work must update this record rather than regenerate disconnected chat summaries. Keep owner decisions, accepted baselines, proposals, validation evidence, unresolved issues and implementation status separate.

## 1. Project control

**Phase:** Initial planning / pre-implementation specification.
**Implementation status:** Not started by this planning work. No source code, repository changes, device configuration changes or database migrations have been made.
**Next milestone:** Complete the implementation-ready specification, run a consistency review, then obtain explicit owner approval before implementation.

### Working rules

1. This page is the canonical project record. Read relevant sections before continuing.
2. Never ask the owner to repeat a recorded decision.
3. Do not reopen settled decisions without concrete contradictory evidence or a material risk.
4. The technical lead makes routine engineering choices and explains them; ask the owner only about authority, privacy, risk tolerance, personal preference or genuinely unresolved product direction.
5. Every proposal must cover purpose, rationale, dependencies, failure modes, security/privacy implications and acceptance criteria.
6. Label items as Owner decision, Accepted baseline, Proposed, Unresolved, Validated or Implemented. Never present a proposal as tested or implemented.
7. Update this record in place, maintain a change log and avoid disconnected planning documents.
8. No implementation until the entire initial specification and roadmap pass consistency review and the owner approves the transition.

A section is complete only when requirements, interfaces, ownership, failure behaviour, safeguards, tests and dependencies are precise enough that implementation does not require guessing.

## 2. Product identity and mission

**Working name:** AURION — Adaptive Unified Reasoning, Intelligence, Observation and Navigation.
**Working tagline:** Intelligence that evolves through experience.
**Branding status:** Proposed, not recorded as final owner-approved branding.

**Mission:** Develop an intelligent, adaptive and persistent system that acquires knowledge, learns from experience, develops capabilities, reasons about its environment, pursues objectives and continuously improves its ability to operate effectively.

AURION is intended to be an advanced personal assistant, not merely a chatbot or thin LLM wrapper; offline-first but able to use online resources under policy; capable of reasoning, planning, knowledge acquisition, memory, tool use, objective execution and adaptation; proactively autonomous within explicit boundaries; designed for multiple devices; initially developed/tested in Termux; and continuously evolving rather than following fixed developmental stages.

AURION is a separate project, not a copy of the whole JARVIS project/repository. Selected JARVIS mechanisms and principles may be reused where appropriate.

**Foundational principle:** “Engineer the mechanisms; let behaviour be acquired through experience.”

Do not hardcode behavioural conclusions (for example, stimulus-to-emotion, failure-to-trauma, success-to-reward or input-to-response) and present them as learning. Engineering mechanisms, protocols, constraints and safeguards is necessary; hardcoding the behaviour those mechanisms should acquire is not.

## 3. Owner decisions — authoritative register

Do not ask these again unless the owner changes them.

### Foundational principles

| ID | Owner decision |
| --- | --- |
| MP-01 | Evolve everything, including foundational values and objectives, subject to protected authority and safeguards. |
| MP-02 | Continuous development; no fixed developmental stages. |
| MP-03 | Identify limitations, propose changes, test in isolation and seek approval to integrate. |
| MP-04 | Maintain a self-model of capabilities, limitations, confidence, resources, performance and goals. |
| MP-05 | Core principles and user authority are protected; other elements may adapt within constraints. |
| MP-06 | Improve the local model primarily through training. |

Protected rules may be proposed for revision, but changes require explicit approval and a recovery mechanism.

### Architecture decisions

| ID | Decision |
| --- | --- |
| IP-01 | Modular monolith at the centre, with selected independent services where justified. |
| IP-02 | C++ core; use other languages for responsibilities they serve better. |
| IP-03 | Model-independent interfaces from the beginning. |
| IP-04 | SQLite initially, with defined schemas and migration support. |
| IP-05 | Typed internal events and explicit interfaces. |
| IP-06 | Design multi-device contracts early; implement distribution after the single-device core works. |
| IP-07 | Training pipeline supports capable external hardware and lightweight local experiments where feasible. |
| IP-08 | Build/test mechanisms individually, then validate their interaction in complete cognitive cycles. |
| IP-09 | Use external libraries when they reduce development time without compromising the design. |
| IP-10 | First milestone: persistent local assistant that converses, remembers, retrieves, reasons through a task and retains outcomes. |

### Detailed engineering baselines

| ID | Accepted baseline |
| --- | --- |
| UQ-01 | Separate storage systems for different memory domains. |
| UQ-02 | Separate Python workers for training/experiments; typed messages across process boundaries. |
| UQ-03 | Keep in-process and separate-process inference possible; benchmark on the actual phone before choosing. |
| UQ-04 | Persist durable experiences, state changes, actions and outcomes; sample transient diagnostics. |
| UQ-05 | Build evaluation and dataset infrastructure before selecting fine-tuning targets. |
| UQ-06 | Hybrid knowledge trust/revision: provisional beliefs first, consolidation after evidence. |
| UQ-07 | Broad tool access with policy checks at the execution boundary. |
| UQ-08 | Protected rules may be proposed for change, but require approval and recovery. |
| UQ-09 | Separate logical stores and initially use SQLite; separate DB files for durable events and protected governance records. |
| UQ-10 | Vector search is not mandatory initially; use a replaceable retrieval interface and benchmark conventional retrieval first. |
| UQ-11 | Durable operation IDs, transactions within stores, idempotent event processing, explicit commit states, recovery journal and reconciliation. |
| UQ-12 | Policy enforcement independent of model reasoning and enforced at the execution boundary. |
| UQ-13 | Approval bound to exact operation and authenticated owner session, with durable audit. |
| UQ-14 | Persistent background scheduler with budgets, checkpoints, cancellation and resumption. |
| UQ-15 | Encrypt sensitive persistent data and backups; key management separate from ordinary application data. |
| UQ-16 | Explicit retention/deletion lifecycle, including indexes, references, backups and synchronized copies. |
| UQ-17 | Verify learning through repeatable held-out task improvement against baseline and regression testing. |

### Operational authority

**Owner choice: Proactive bounded autonomy.**

AURION should understand objectives, decompose them into tasks, identify resources/tools, execute permitted tasks without repeated prompting, monitor progress, recover from recoverable failures, make reasonable decisions, preserve progress across sessions and notify the owner when completed, blocked or requiring intervention. It should identify relevant problems/opportunities and undertake authorized work proactively.

Approval is required for purchases/financial transactions, external communications unless specifically authorized, permanent destructive operations, significant security changes and protected governance-rule changes. Permissions must be explicit, inspectable, adjustable and auditable. Harmless authorized reads, diagnostics and tests should not require repeated approval.

### Online services and private information

**Owner choice: Policy-controlled autonomous resource utilization.**

AURION may select among configured online services/resources—search, external AI models, APIs, cloud compute and research/development tools—based on task requirements, capability, reliability, cost, availability and privacy. It should use local alternatives when appropriate, fall back when providers fail and record external transfers.

**Private-information sharing: Contextual sharing.**

- Send only the private context necessary for an authorized task.
- Apply data minimization and policy enforcement.
- Sensitive information requires explicit approval before external disclosure.
- Do not unnecessarily expose credentials/secrets.
- Record external disclosures.
- Prefer local processing when appropriate.
- Enabling an external provider does not grant unrestricted access to all AURION memory.

### Deletion and backup retention

**Owner choice: 30-day backup expiry.**

- Remove from active memory immediately.
- Remove retrieval-index entries.
- Propagate deletion to synchronized devices.
- Exclude deleted information from future backups.
- Historical backups containing deleted information expire within 30 days.
- Keep minimal deletion records and expose limitations.

Offline devices cannot be erased immediately; their deletion instruction must remain pending, and they must not reintroduce deleted information during later synchronization.

## 4. Language and runtime strategy

Initial language set:

- **C++:** authoritative core/runtime, cognition, memory, reasoning, goals, planning, learning/evolution coordination and tool policy.
- **Python:** ML training, fine-tuning, dataset preparation, experiments and evaluation.
- **SQL:** relational schemas, queries and migrations.
- **Kotlin:** likely later for native Android integration/UI.
- **TypeScript:** optional future web interface.
- **Rust:** not currently justified.

Start with C++, Python and SQL. Add languages only for concrete requirements. C++/Python boundary uses typed process/message contracts, not tight coupling or Python embedding by default.

## 5. Device and existing model groundwork

Previously established:

- Device: itel C671L (itel City 100), Android 14, ARM64 (aarch64), 8 CPU cores.
- Physical RAM approximately 6 GB. Reported 6+12 GB expansion uses storage and is not equivalent to physical RAM.
- Prior observation: MemTotal approximately 5.6 GiB; MemAvailable approximately 2.0 GiB; swap approximately 4.2 GiB.
- Termux tools: clang 21.1.8, CMake 4.4.5, Git 2.56.0.
- llama.cpp cloned at ~/llama.cpp; CMake build succeeded.
- CLI: 0.8.0-dev (build 12102, commit bbb02c93e).
- Model: ~/llama.cpp/models/Qwen3-4B-Q4_K_M.gguf, approximately 2.50 GB.
- Reported SHA-256: 7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5.
- Basic inference with Qwen3-4B Q4_K_M through llama.cpp succeeded.

**Evidence boundary:** this establishes successful build and basic inference only. It does not establish sustained stability, latency suitability, background reliability, thermal behaviour, battery impact or concurrent workload performance. Measure those before runtime decisions.

## 6. Target architecture

### Conceptual layers

1. Interfaces: CLI, Android, voice, web and other devices.
2. C++ cognitive core.
3. Runtime services: inference, storage, scheduling, resources, model management and events.
4. Supporting systems: Python training/evaluation workers; later synchronization service.
5. Data and model assets.
6. Platform infrastructure.

Security and governance cut across all layers. Architecture style: modular monolith at the centre, with independent services only where lifecycle, resource or security boundaries justify them.

### Logical cognitive responsibilities

Orchestration; experience; representation; context; cognition; reasoning; prediction; appraisal; attention; goals; planning; decision; action; memory; knowledge; learning; self-model; evolution; governance; evaluation.

These are logical ownership boundaries, not a requirement to create a separate process/library/executable for every module.

### Cognitive cycle

Experience/observation → representation → context → memory/knowledge → belief state → prediction → attention/appraisal → reasoning → goal evaluation/planning → decision/permission → action → observed consequence → prediction/outcome evaluation → learning/memory update → self-model/strategy update.

Not a rigid pipeline: conditional, iterative, concurrent and interrupt paths are expected.

### Typed events

Events describe what happened; interfaces define operations. Candidate events include experience observed, representation/context updated, memory retrieved, belief revised, prediction generated/evaluated, goal created/changed, plan generated, action proposed/completed/failed, permission granted/denied, learning update committed and improvement proposal created.

Every event contract must define schema version, source, timestamps, correlation/causation IDs, ordering expectations, duplicate handling, durability, validation, error propagation, traceability and protection against arbitrary state mutation.

## 7. Persistence and memory architecture

Initial proposal: three SQLite databases:

1. aurion_memory.db: experiences, representations, contexts, memory, knowledge, beliefs, evidence, predictions, goals, plans, discovered capability descriptors/knowledge, durable appraisal/decision/outcome summaries, self-model revisions, evolution proposals and learning metadata.
2. aurion_events.db: durable events, operations, operation steps, recovery journal, task runs and checkpoints.
3. aurion_governance.db: policies, permissions, approval requests/decisions, protected changes, audit, provider permissions and data disclosures.

Working memory remains in RAM. Large content/model/dataset artifacts live in filesystem storage with metadata references. Vector retrieval is deferred until evaluation demonstrates a need.

Ownership:

- Memory owns episodic/semantic memory records and retrieval metadata.
- Knowledge owns consolidated knowledge; belief subsystem owns provisional/revised beliefs and evidence lineage.
- Capability discovery owns versioned capability descriptors, discovery evidence, capability knowledge revisions and evidence-supported capability relationships in the memory domain; it does not own permission grants.
- Event infrastructure owns durable event history.
- Model manager owns model metadata/deployment.
- Appraisal/reasoning/decision/outcome subsystems own bounded durable assessment/decision/evaluation records; transient attention allocation remains in working runtime state unless a durable event is required.
- Self-model owns evidence-backed self-model revisions; evolution owns change proposals and candidate/evaluation references.
- Governance owns protected policies, owner identity, permission grants, approvals and authorization.

Cross-store consistency uses shared durable operation IDs, transactions within each DB, idempotent event processing, explicit commit states, recovery journal/reconciliation, periodic consistency checks and coordinated backup/restore. Do not assume a global transaction across database files.

## 8. Database schema design baseline

A proposed SQL schema was drafted in the planning conversation. It is a proposal, not executed or validated. The complete DDL must be retained in a linked technical appendix before implementation; this control page records the canonical entity model and rules.

### Memory DB entities

experiences; representations; contexts; memory_records; memory_links; knowledge_items; beliefs; evidence_items; belief_revisions; belief_evidence; predictions; prediction_evaluations; goals; plans; plan_steps; plan_step_dependencies; capability_descriptors; capability_discovery_evidence; capability_knowledge_revisions; capability_knowledge_evidence; capability_relationships; appraisal_records; reasoning_assessments; decision_records; outcome_evaluations; self_model_revisions; evolution_proposals; learning_updates.

Rules:

- Experience is an observation, not automatically a fact.
- Representation is an interpretation; multiple representations may exist for one experience.
- Beliefs are propositions with evidence, context, epistemic status and revision history.
- Evidence can support, contradict or qualify a belief.
- Predictions are stored before outcomes are known; evaluation cannot rewrite original predictions.
- Goal is distinct from its versioned plans.
- Plan dependency cycles require application-level validation.
- Learning updates reference evidence, mechanism, hypothesis, baseline, evaluation and decision.

### Events/recovery DB entities

events; event_consumers; operations; operation_steps; recovery_journal; task_runs; task_checkpoints; audit_references.

Rules:

- Uncertain external outcomes must be reconciled before retrying.
- Operation IDs and idempotency keys prevent duplicate side effects.
- Events are not the authoritative owner of cognitive conclusions.
- Checkpoints support resumption but do not guarantee Android/Termux keeps a process alive.

### Governance DB entities

policies; permissions; approval_requests; approval_decisions; protected_changes; provider_permissions; data_disclosures; governance_audit.

Rules:

- Model cannot grant itself permissions.
- Approval binds exact operation, target, scope, effects and authenticated owner session.
- Approval records are immutable; later changes are new records/events.
- External disclosure is recorded and minimized.
- Audit integrity requires a verifiable mechanism; a hash column alone is insufficient.

### Shared conventions — proposed

UUID IDs stored as 16-byte BLOBs; UTC Unix timestamps in integer milliseconds; booleans as constrained integers; enumerations as constrained text; PRAGMA user_version per DB plus migration history; explicit retention/deletion lifecycle. Enable foreign keys on every connection. Cross-database references use stable UUIDs and application-level validation because SQLite cannot enforce cross-file foreign keys.

### Migration strategy — proposed

1. Stop writes to the DB being migrated.
2. Verify database integrity and available storage.
3. Create and verify a consistent backup.
4. Apply deterministic versioned migration.
5. Run structural and data-integrity validation.
6. Update schema version and migration history.
7. Commit and reopen through the application.
8. Resume writes only after validation.
9. On failure, roll back or restore verified backup, then reconcile cross-store operations.

WAL, synchronous mode, busy timeout, checkpointing and backup behaviour must be benchmarked on actual Termux storage. WAL is not automatically superior.

### Known schema corrections

1. Cross-database references require application-level consistency checks.
2. Provider permission history must support versioned grants/revocations; one unique provider row is too restrictive.
3. Approval lifecycle must reject expired, revoked or mismatched approvals.
4. Deletion must cover content files, indexes, caches, backups and synchronized devices.
5. Original prediction content and criteria must be immutable.
6. Dependency cycles and invalid graph relationships require application validation.
7. Audit integrity needs a verifiable mechanism, not just an integrity_hash field.
8. Every SQL table, index, constraint and transaction boundary must be reviewed as a coherent schema before implementation.

## 9. Model and inference architecture

Model-independent inference interface. Initial local model candidate: Qwen3-4B Q4_K_M via llama.cpp, basic inference tested. Future options: local GGUF models, alternative engines, remote models, embeddings and reranking.

Capability discovery includes text, structured output, tool-call format, context size, embeddings and multimodal capabilities where relevant. Preserve in-process and separate-process inference options until benchmarked.

Measure on device: peak resident memory, model load time, time to first token, generation throughput, CPU utilization, thermal throttling, battery impact, concurrent workload interference, failure and restart recovery.

Do not select runtime topology from model size or RAM estimates alone.

## 10. Learning, training and evolution

Python worker pipeline:
approved experience/data → dataset preparation → training/fine-tuning → candidate artifact → evaluation/regression → release validation → versioned release → controlled deployment → monitoring/rollback.

C++ remains authoritative for objectives, data authorization, evaluation criteria and release eligibility. Python workers do not directly mutate live cognitive state or approve production artifacts.

Worker contracts include job IDs, immutable dataset/model references, configuration, resource budgets, evaluation requirements, artifact references, metrics, status/errors and reproducibility metadata.

Keep memory updates, knowledge/belief revision, strategy learning, model fine-tuning and architecture evolution distinct.

Learning is demonstrated through repeatable held-out task improvement against baseline, related unseen variations and regression checks. Data accumulation or successful training alone is not proof.

Evolution lifecycle:
limitation/opportunity → evidence → proposal → impact/risk analysis → isolated candidate → tests → baseline comparison → reject/revise/seek approval → integrate approved change → monitor → rollback regressions.

## 11. Knowledge and belief management

Use provisional beliefs followed by evidence-supported consolidation, with disputed and withdrawn states as needed. Retain provenance, context, supporting/contradicting evidence, revision history, status and rationale.

Do not use simplistic rules such as “N observations = truth”. Confidence must be calibrated before being interpreted probabilistically.

## 12. Tool and action security

Execution lifecycle:
reasoning/planning → tool discovery → capability validation → action proposal → policy enforcement → authorization → execution → result verification → outcome record.

Tool declarations include stable identity/version, operations and input/output schemas, required permissions and data access, side-effect classification, resource requirements, offline support, cancellation, idempotency and verification method.

Model cannot grant permissions; tools cannot self-escalate; shell cannot bypass policy; untrusted external content is not privileged instruction; destructive operations require authorization; important actions are audited. Risk classification depends on actual effects, not tool names. Authorization is checked at execution, not merely during planning.

## 13. Governance and approval

Protected change lifecycle:
proposal → rationale/evidence → impact/risk → isolated candidate → validation/adversarial tests → exact owner approval → versioned activation → monitoring → rollback.

Approval is bound to the exact proposal/operation and is not reusable as generic authorization. AURION cannot redefine what constitutes owner approval.

## 14. Background scheduling and autonomy

Persistent task state, checkpoints, priorities, budgets, cancellation, safe resumption, dependencies and progress reporting are required.

Android/Termux can interrupt background processes. Persistent task state does not guarantee process survival or notification delivery. Native Android integration may improve scheduling/notifications later but still respects OS constraints.

## 15. Multi-device architecture

Design contracts early; defer actual distribution until the single-device core works. Later requirements: logical AURION identity, device identity/runtime instance identity, shared versus local state, device authentication, encrypted transport, selective permission-aware sync, conflict resolution, offline sync, model distribution, workload routing and deletion propagation.

## 16. Testing and evidence requirements

Test categories: unit, integration, persistence, cognitive-cycle, learning, model evaluation, evolution, security, recovery, performance/resource and multi-device.

Acceptance principles:

- Reproducible clean build.
- Invalid messages rejected.
- Persistence survives restart.
- Interrupted operations reconcile.
- Memory retrieved with provenance.
- Contradictory evidence can revise beliefs.
- Predictions evaluated independently.
- Held-out improvement demonstrated.
- Unauthorized operations blocked.
- Permitted autonomous tasks proceed without unnecessary prompts.
- Unnecessary private context excluded from external disclosure.
- Regressions detected and candidates can be rolled back.
- Resource use measured on actual phone.
- Deployment and recovery reproducible.

Numerical performance thresholds are set after baseline measurements, not invented prematurely.

## 17. First milestone

A persistent local AURION that converses, records/retrieves experiences, reasons through a bounded objective, executes at least one explicitly permitted action, observes/evaluates the outcome and uses that outcome in a later related interaction.

Acceptance:

1. Runs locally in Termux.
2. Uses local model through inference abstraction.
3. Conversations/experiences persist across restart.
4. Relevant retrieval preserves provenance.
5. Represents bounded objective and plan.
6. Executes at least one explicitly permitted action through action interface.
7. Records outcome and evaluates expectations.
8. Outcome demonstrably influences later retrieval/reasoning/strategy.
9. Significant operations are traceable.
10. Handles errors/resource limits without corrupting state.

Chat history alone is not sufficient evidence of memory or learning.

## 18. Implementation work packages — planning baseline

**Historical planning table:** This original WP-00…WP-16 breakdown is retained for decision history. It is superseded by `docs/planning/CANONICAL-IMPLEMENTATION-ROADMAP.md`, which reconciles the later detailed contracts and the owner's concurrent cloud/offline-mobile first-release decision. Do not use the historical numbering as the current implementation sequence.


| Work package | Scope |
| --- | --- |
| WP-00 | Foundation and build system |
| WP-01 | Shared contracts |
| WP-02 | Persistence |
| WP-03 | Runtime |
| WP-04 | Inference |
| WP-05 | Experience |
| WP-06 | Memory |
| WP-07 | Knowledge |
| WP-08 | Cognition |
| WP-09 | Goals |
| WP-10 | Action |
| WP-11 | Learning |
| WP-12 | Self-model |
| WP-13 | Evolution |
| WP-14 | Python workers |
| WP-15 | Hardening |
| WP-16 | Expansion |

Critical dependency path:
WP-00 → WP-01 → WP-02/WP-03 → WP-04/WP-05 → WP-06/WP-07 → WP-08 → WP-09/WP-10 → WP-11 → WP-12/WP-13 → WP-15.

Worker infrastructure follows shared contracts and artifact-management foundations. This is a dependency baseline, not a promise that all work is strictly sequential.

## 19. Remaining specification checklist — historical snapshot

This checklist records the outstanding items at the time of the original specification. Later sections and the [Planning Completion Register](PLANNING-COMPLETION-REGISTER.md) supersede its status. Do not use this historical checklist alone to determine current completion.

- [ ] Exact versioned event schemas and C++/Python worker message contracts.
- [ ] Component dependency matrix: ownership, allowed/forbidden dependencies, cycle prevention and interfaces.
- [ ] Full authorization policy: scopes, risk classes, approval expiry, revocation, exact-operation binding and audit.
- [ ] Crash-recovery catalogue: concrete failure scenarios, expected state transitions, reconciliation and compensation.
- [ ] Complete deletion/synchronization specification: offline devices, derived data, backups and restore behaviour.
- [ ] Test catalogue: test IDs, fixtures, preconditions, steps, expected outcomes and measurable criteria.
- [ ] Dependency/licensing review: ARM64, Termux, offline operation, Android roadmap and license compatibility.
- [ ] Complete SQL review: DDL correctness, constraints, indexes, transactions, migrations and cross-store consistency.
- [ ] Architecture-wide consistency review against all owner decisions.
- [ ] Risk register and explicit residual-risk acceptance.
- [ ] Implementation roadmap with dependencies, deliverables and exit criteria.
- [ ] Final pre-implementation review and owner approval.

## 20. Required format for remaining specification sections

Each section must define purpose/scope; requirements/invariants; component ownership; exact interfaces/contracts; data model/lifecycle; normal operation; failure modes/recovery; security/privacy/authority; dependencies/alternatives; test cases/acceptance criteria; status and unresolved issues.

## 21. Change log

- Initial capture: consolidated AURION mission, owner decisions, architecture baselines, device/model groundwork, cognitive architecture, storage design, SQL entity model, operational/security requirements, first milestone and remaining planning work from the planning conversation.
- Status: SQL schema and architecture are proposals/baselines, not verified implementation. No implementation is authorized by this document alone.

## 22. Immediate next action — historical snapshot

This was the next action when the initial specification was first consolidated. It is superseded by the later planning supplements and the current builder-owned work ledger in [Planning Completion Register](PLANNING-COMPLETION-REGISTER.md).

Continue the remaining specification checklist in this same controlled project record. Do not restart from the mission or re-summarize settled decisions. Complete exact event/message contracts, component dependencies, authorization, recovery, deletion/sync, tests, dependency/licensing and consistency review. Update this record as each section is completed and preserve the change log. Only after the entire initial planning stage is complete should the owner be asked to approve implementation.

---

# Part II — Detailed engineering contracts

## 23. Versioned event and worker-message contracts

**Status:** Proposed specification baseline; not implemented or schema-validated.
**Purpose:** Establish one unambiguous contract between the C++ core, runtime services, persistence and Python workers. Components must not depend on another component's private structures or directly mutate another component's owned state.

### 23.1 Contract families and transport

Use two related but distinct contract families:

1. **Internal domain events:** describe facts about something that has happened in AURION, such as an experience being recorded or an action completing.
2. **Worker/control messages:** request work from a process/service and report its result, such as preparing a dataset or evaluating a model candidate.

A request is not an event. A request can fail before work happens; an event reports an occurrence that has happened.

Initial transport:

- In-process C++ modules use typed C++ interfaces and typed event values. Do not serialize every internal call merely for architectural appearance.
- C++ ↔ Python workers use JSON Lines (one complete JSON object per line) over a controlled process pipe initially. A later local IPC transport may reuse the same envelope and payload schemas.
- Persist durable events in the event store. Transient diagnostics may be sampled and need not become durable domain events.
- stdout is the worker protocol channel; diagnostics go to stderr.

JSON is the initial interchange encoding, not the internal C++ data model. Validate at process boundaries and convert to typed internal structures.

### 23.2 Canonical envelope

Every event and worker message uses this envelope:

```json
{
  "contract_version": "1.0",
  "message_id": "UUID",
  "message_type": "experience.recorded",
  "occurred_at": "2026-11-11T14:30:00.000Z",
  "producer": {
    "component": "experience",
    "instance_id": "UUID",
    "version": "0.1.0"
  },
  "correlation_id": "UUID",
  "causation_id": "UUID",
  "payload": {}
}
```

Field rules:

| Field | Rule |
| --- | --- |
| contract_version | Required major.minor contract version. Major incompatibility requires a new major version. |
| message_id | Required UUID; globally unique for this message. |
| message_type | Required stable, namespaced identifier; never infer type from payload shape. |
| occurred_at | Required UTC RFC 3339 timestamp with explicit Z or offset; normalize to UTC at ingestion. |
| producer.component | Required registered component identifier. |
| producer.instance_id | Required runtime/process instance UUID. |
| producer.version | Required software component version. |
| correlation_id | Required UUID linking the request/task/cognitive operation. |
| causation_id | Optional UUID of the immediate message/event that caused this one; absent for a root occurrence. |
| payload | Required object validated against the schema registered for message_type and contract_version. |

A receiver adds its own received_at_ms and processing metadata in its receiving store; the producer must not claim to know when another component received the message.

**Timestamp convention:** wire format uses UTC RFC 3339; SQLite stores UTC Unix epoch milliseconds as previously proposed. Reject timestamps without timezone information. Clock skew is possible; causal ordering uses causation/correlation IDs, the receiving event store's monotonically assigned `event_sequence`, aggregate/domain revisions and operation state, not wall-clock timestamps alone. `event_sequence` is local to one event store and does not imply global ordering across independent devices or producers.

**Identifier convention:** UUID text on the wire; 16-byte UUID BLOB in SQLite. IDs must not be reused.

### 23.3 Message type namespaces

Stable namespaced types:

- Domain events: experience.recorded, representation.created, context.updated, belief.revised, prediction.created, prediction.evaluated, goal.changed, plan.created, action.proposed, action.started, action.completed, action.failed, permission.decision_recorded, learning.update_committed, evolution.proposal_created.
- Worker commands: worker.dataset.prepare, [worker.experiment.run](http://worker.experiment.run), worker.model.evaluate, worker.candidate.validate, worker.artifact.inspect.
- Worker responses: worker.accepted, worker.progress, worker.completed, worker.failed, worker.cancelled.
- Runtime control: [runtime.health](http://runtime.health).request, [runtime.health](http://runtime.health).response, runtime.cancel.request, runtime.shutdown.request.

Do not create a new event type for every minor field variation. Use a stable event type with a versioned payload schema. Do not overload a generic state.changed event for domain facts that need specific semantics.

### 23.4 Domain-event payload contracts

All payloads below are minimum required fields. Additional fields require schema evolution and compatibility review.

| Type | Required payload | Invariants |
| --- | --- | --- |
| experience.recorded | experience_id, source_type, observed_at, content_ref, sensitivity, provenance_ref | Observation is not automatically a fact. Content reference must resolve under access policy. |
| representation.created | representation_id, experience_id, representation_type, content, method, uncertainty | Preserve source experience and interpretation method; never overwrite the source observation. |
| context.updated | context_id, context_version, scope, valid_from, attributes_ref | Context has scope and temporal validity; temporary context does not silently become durable fact. |
| belief.revised | belief_id, revision_id, previous_revision_id, proposition_ref, epistemic_status, evidence_refs, revision_reason | Append-only revision; evidence references resolve; status is not objective truth. |
| prediction.created | prediction_id, subject_ref, expected_outcome, evaluation_criteria, horizon, created_before_outcome | Prediction content and criteria become immutable once committed. |
| prediction.evaluated | prediction_id, evaluation_id, observed_outcome_ref, result, evaluated_at, evaluator | Evaluation is separate; never mutate original prediction. |
| goal.changed | goal_id, goal_revision, change_kind, state, reason_ref | Goal revision is distinct from plan version; preserve prior revisions. |
| plan.created | plan_id, goal_id, goal_revision, plan_version, step_refs, dependency_refs | Plan references a specific goal revision; dependency graph must be acyclic unless a separately specified iterative-plan construct is used. |
| action.proposed | action_id, operation_id, tool_id, operation_name, target_ref, effects, authorization_request_id | Proposal is not permission or execution. |
| action.started | action_id, operation_id, attempt_id, started_at, executor_id | Execution starts only after a valid authorization decision at the execution boundary. |
| action.completed | action_id, operation_id, attempt_id, result_ref, verification | Completion requires result capture; do not infer success from process exit alone where effect verification is available. |
| action.failed | action_id, operation_id, attempt_id, failure_class, retryability, diagnostic_ref | Failure is not permission to retry; uncertain side effects require reconciliation. |
| permission.decision_recorded | decision_id, request_id, decision, policy_version, scope_digest, decided_at | Immutable and bound to exact requested operation/scope; cannot grant broader authority. |
| learning.update_committed | learning_update_id, mechanism, evidence_refs, baseline_ref, evaluation_ref, decision | Committed update requires evaluation evidence; proposals/running updates use different states. |
| evolution.proposal_created | proposal_id, target, rationale_ref, risk_assessment_ref, candidate_ref | Proposal does not activate itself; protected changes still require exact owner approval. |

References such as content_ref, provenance_ref, attributes_ref, reason_ref and result_ref must be typed references, not arbitrary filesystem paths or unrestricted URLs. Access is resolved by the owning subsystem and checked against policy.

### 23.5 Worker command and response contracts

Worker messages use the same envelope, with correlation_id linking command, progress and terminal response. Every command payload includes job_id and immutable input references.

**Dataset preparation request**

```json
{
  "job_id": "UUID",
  "dataset_source_refs": ["dataset-source:UUID:version"],
  "preparation_spec_ref": "artifact:UUID:version",
  "output_artifact_uri": "worker-output://job/UUID",
  "resource_budget": {
    "max_memory_bytes": 1073741824,
    "max_cpu_threads": 2,
    "max_duration_seconds": 1800
  },
  "reproducibility": {
    "seed": 12345,
    "deterministic_required": true
  }
}
```

**Experiment/model-evaluation request**

```json
{
  "job_id": "UUID",
  "base_model_ref": "model:UUID:version",
  "dataset_ref": "dataset:UUID:version",
  "objective_ref": "evaluation-objective:UUID:version",
  "experiment_config_ref": "artifact:UUID:version",
  "evaluation_suite_ref": "evaluation-suite:UUID:version",
  "resource_budget": {
    "max_memory_bytes": 2147483648,
    "max_cpu_threads": 4,
    "max_duration_seconds": 3600
  },
  "output_artifact_uri": "worker-output://job/UUID"
}
```

These are examples of field shape, not fixed device budgets. The scheduler assigns real budgets from measured device capacity and task policy.

**Worker response payloads**

- worker.accepted: job_id, worker_id, accepted_at, effective_budget.
- worker.progress: job_id, sequence, stage, progress_fraction (nullable if unknowable), metrics_ref, updated_at.
- worker.completed: job_id, artifact_ref, artifact_checksum, evaluation_report_ref, resource_usage_ref, reproducibility_ref.
- worker.failed: job_id, failure_code, retryable, diagnostic_ref, partial_artifact_refs.
- worker.cancelled: job_id, cancelled_at, last_safe_checkpoint_ref, partial_artifact_refs.

A worker must not claim completion without a durable artifact reference and checksum when the job is expected to produce an artifact. A worker cannot approve or deploy its own candidate.

### 23.6 Validation and compatibility

At every process boundary:

1. Enforce maximum message size before parsing.
2. Parse exactly one complete JSON object per line.
3. Validate envelope fields and primitive types.
4. Validate message_type against an allowlisted registry.
5. Validate payload against the exact schema version.
6. Reject unknown required fields or incompatible major versions.
7. Permit forward-compatible optional fields only under explicit schema rules.
8. Validate referenced IDs/artifacts and access rights before use.
9. Record rejection reason without copying sensitive payload content into logs.

Do not silently coerce wrong types, missing identifiers or invalid enum values. Unknown optional fields may be ignored only when the schema explicitly permits it. Unknown message types are rejected.

Versioning:

- Patch-level implementation fixes do not alter the wire schema.
- Minor contract versions may add optional fields while preserving existing semantics.
- Major versions may change required fields or semantics and require explicit compatibility handling.
- Producer and consumer declare supported contract versions before starting a worker session.
- Never reinterpret an old field with a new meaning.

### 23.7 Delivery, ordering, idempotency and failure semantics

**Delivery guarantee:** at-least-once for durable events and worker messages. Exactly-once delivery is not promised. Effective exactly-once state transitions are approximated through durable message IDs, idempotent handlers, unique constraints and operation reconciliation.

Consumer requirements:

- Persist message ID and processing outcome.
- Duplicate message_id with identical content is acknowledged as duplicate and not applied again.
- Duplicate message_id with different content is a protocol-integrity error.
- Maintain consumer checkpoint/sequence for ordered streams where ordering is required.
- Do not assume global ordering across independent producers.
- Use causation_id and correlation_id to reconstruct causal relationships.
- Acknowledge durable messages only after receiving state is committed or safely journaled.

For cross-database writes, no global SQLite transaction exists. Use an explicit operation state machine and recovery journal. The source database commits its local state and an outbox/recovery record together; a dispatcher publishes the message; the consumer commits idempotently and records its receipt. Reconciliation resolves interrupted states. Do not claim atomicity across the three files.

**Worker lifecycle:** created → dispatched → accepted → running → completed \| failed \| cancelled \| timed_out. A worker may also become lost when its process disappears and status cannot be obtained. Terminal states are immutable. A retry creates a new attempt under the same logical job or a new job according to job policy; it is never an unrecorded replay.

**Cancellation:** cooperative first; hard process termination only after timeout and with partial-output quarantine. A cancellation request does not prove the worker stopped. Confirm process termination and persist terminal status.

**Retry:** bounded by policy, backoff and resource budget. Retry only operations declared safe/idempotent or after reconciliation establishes that no duplicate side effect occurred.

### 23.8 Security and privacy requirements

- Worker receives only the minimum input data required for its job.
- Dataset references must already be authorized; a worker cannot broaden dataset access.
- No credentials or governance signing keys in worker payloads or environment unless a narrowly scoped secret is essential and explicitly provisioned.
- Worker output is untrusted until validated, scanned and checked against declared artifact limits.
- Worker process gets a restricted working directory and explicit read/write paths.
- Network access is disabled by default for training/evaluation workers; any exception is separately authorized.
- Resource limits, timeouts and cancellation are enforced by the parent runtime where platform permits.
- Termux is not a strong security sandbox. File/process restrictions reduce accidental exposure but do not provide equivalent isolation to a dedicated OS sandbox or container runtime.
- Logs must not contain raw sensitive prompts, private training examples, tokens or secrets by default.

### 23.9 Acceptance tests

| ID | Test | Expected result |
| --- | --- | --- |
| EVT-001 | Missing required envelope field | Reject before dispatch |
| EVT-002 | Invalid UUID or timestamp without timezone | Reject |
| EVT-003 | Unknown message type | Reject and record safe diagnostic |
| EVT-004 | Unsupported major contract version | Reject with compatibility error |
| EVT-005 | Oversized JSONL line | Reject without unbounded allocation |
| EVT-006 | Duplicate message ID, identical body | Idempotent acknowledgement; no duplicate state change |
| EVT-007 | Duplicate message ID, altered body | Integrity/protocol error |
| EVT-008 | Consumer crashes after commit but before acknowledgement | Redelivery produces no duplicate state transition |
| EVT-009 | Producer crashes between local commit and publish | Outbox/recovery dispatcher eventually publishes |
| EVT-010 | Worker exits without terminal response | Mark lost/uncertain; reconcile before retry |
| EVT-011 | Worker reports artifact with wrong checksum | Reject artifact |
| EVT-012 | Worker attempts undeclared network access | Deny where enforceable; record policy violation |
| EVT-013 | Cancellation during dataset preparation | Safe checkpoint or quarantined partial artifact; terminal state recorded |
| EVT-014 | Out-of-order event from independent producers | Preserve causal references; do not invent total order |
| EVT-015 | Sensitive payload rejected | Diagnostic does not leak payload contents |

### 23.10 Unresolved engineering items

- Select exact JSON Schema dialect and validator library after dependency/licensing review.
- Decide whether worker transport remains stdin/stdout JSONL or moves to local sockets after device benchmark; contract remains transport-independent.
- Define canonical typed-reference syntax and artifact URI registry.
- Define event retention/compaction while preserving audit and recovery requirements.
- Implement schema compatibility tests in CI once repository/build pipeline is selected.

**Section exit criterion:** C++ and Python independently validate the same contract fixtures; duplicate delivery, interruption and version mismatch tests pass; no worker can mutate authoritative state outside its contract.

## Change log update

- Added Part II, Section 23: versioned event and worker-message contracts, delivery semantics, worker lifecycle, validation, privacy controls and acceptance tests.
- This section is a proposed specification baseline, not implemented or validated against code.

## 26. Initial SQLite schema and migration baseline

**Status:** Proposed DDL baseline; not executed or validated against the target SQLite build. Three separate files remain: memory/domain, events/recovery and governance. Cross-file relationships use UUID references validated by application reconciliation; SQLite foreign keys do not cross database-file ownership boundaries.

### 26.1 Conventions

- UUIDs: 16-byte BLOB primary keys; canonical UUID strings on wire.
- Timestamps: UTC Unix epoch milliseconds in INTEGER columns; RFC 3339 at interfaces.
- JSON TEXT only for bounded, validated flexible documents. Query-critical fields remain typed columns.
- Enable foreign keys on every connection. Use short write transactions; never hold DB transactions during inference or external actions.
- Use STRICT tables only if the shipped SQLite version supports them; otherwise add explicit type checks. Verify JSON functions, WAL and backup API on the actual Termux SQLite build.
- Keep large models/datasets outside SQLite as immutable artifacts with metadata and checksums.
- Back up live DBs through SQLite backup facilities or a coordinated checkpointed procedure, not by blindly copying a live WAL database.

### 26.2 Memory database — aurion_memory.db

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE experiences (
  experience_id BLOB PRIMARY KEY CHECK(length(experience_id)=16),
  source_type TEXT NOT NULL,
  observed_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  content_ref TEXT NOT NULL,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  provenance_ref TEXT NOT NULL,
  retention_state TEXT NOT NULL CHECK(retention_state IN
    ('active','archived','pending_deletion','deleted_active','backup_expiry_pending')),
  deleted_at_ms INTEGER
) STRICT;
CREATE INDEX idx_experiences_time ON experiences(observed_at_ms DESC);
CREATE INDEX idx_experiences_retention ON experiences(retention_state,recorded_at_ms);

CREATE TABLE representations (
  representation_id BLOB PRIMARY KEY CHECK(length(representation_id)=16),
  experience_id BLOB NOT NULL REFERENCES experiences(experience_id),
  representation_type TEXT NOT NULL,
  content_json TEXT NOT NULL CHECK(json_valid(content_json)),
  method TEXT NOT NULL,
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  created_at_ms INTEGER NOT NULL
) STRICT;
CREATE INDEX idx_representations_experience ON representations(experience_id);

CREATE TABLE contexts (
  context_id BLOB NOT NULL CHECK(length(context_id)=16),
  version INTEGER NOT NULL CHECK(version>0),
  scope TEXT NOT NULL,
  valid_from_ms INTEGER NOT NULL,
  valid_until_ms INTEGER,
  attributes_json TEXT NOT NULL CHECK(json_valid(attributes_json)),
  provenance_ref TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(context_id,version),
  CHECK(valid_until_ms IS NULL OR valid_until_ms>valid_from_ms)
) STRICT;

CREATE TABLE memory_records (
  memory_id BLOB PRIMARY KEY CHECK(length(memory_id)=16),
  memory_type TEXT NOT NULL,
  content_ref TEXT NOT NULL,
  summary TEXT,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  status TEXT NOT NULL CHECK(status IN ('active','archived','pending_deletion','deleted_active')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  last_accessed_at_ms INTEGER,
  retention_until_ms INTEGER,
  deleted_at_ms INTEGER
) STRICT;
CREATE INDEX idx_memory_status_type ON memory_records(status,memory_type);
CREATE INDEX idx_memory_retention ON memory_records(retention_until_ms)
  WHERE retention_until_ms IS NOT NULL;

CREATE TABLE memory_links (
  source_memory_id BLOB NOT NULL REFERENCES memory_records(memory_id),
  target_memory_id BLOB NOT NULL REFERENCES memory_records(memory_id),
  relation_type TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(source_memory_id,target_memory_id,relation_type),
  CHECK(source_memory_id<>target_memory_id)
) STRICT;

CREATE TABLE knowledge_items (
  knowledge_id BLOB PRIMARY KEY CHECK(length(knowledge_id)=16),
  proposition TEXT NOT NULL,
  domain TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('active','superseded','withdrawn')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE beliefs (
  belief_id BLOB PRIMARY KEY CHECK(length(belief_id)=16),
  knowledge_id BLOB NOT NULL REFERENCES knowledge_items(knowledge_id),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE belief_revisions (
  revision_id BLOB PRIMARY KEY CHECK(length(revision_id)=16),
  belief_id BLOB NOT NULL REFERENCES beliefs(belief_id),
  revision_number INTEGER NOT NULL CHECK(revision_number>0),
  previous_revision_id BLOB REFERENCES belief_revisions(revision_id),
  epistemic_status TEXT NOT NULL CHECK(epistemic_status IN
    ('provisional','supported','consolidated','disputed','withdrawn')),
  confidence REAL CHECK(confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
  revision_reason TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE(belief_id,revision_number),
  UNIQUE(belief_id,revision_id)
) STRICT;
CREATE INDEX idx_belief_revision_order ON belief_revisions(belief_id,revision_number DESC);

CREATE TABLE evidence_items (
  evidence_id BLOB PRIMARY KEY CHECK(length(evidence_id)=16),
  source_experience_id BLOB REFERENCES experiences(experience_id),
  source_ref TEXT NOT NULL,
  evidence_type TEXT NOT NULL,
  observed_at_ms INTEGER,
  recorded_at_ms INTEGER NOT NULL,
  reliability_json TEXT CHECK(reliability_json IS NULL OR json_valid(reliability_json))
) STRICT;

CREATE TABLE belief_revision_evidence (
  revision_id BLOB NOT NULL REFERENCES belief_revisions(revision_id),
  evidence_id BLOB NOT NULL REFERENCES evidence_items(evidence_id),
  stance TEXT NOT NULL CHECK(stance IN ('supports','contradicts','contextualizes')),
  relevance REAL CHECK(relevance IS NULL OR relevance BETWEEN 0.0 AND 1.0),
  PRIMARY KEY(revision_id,evidence_id,stance)
) STRICT;

CREATE TABLE predictions (
  prediction_id BLOB PRIMARY KEY CHECK(length(prediction_id)=16),
  subject_ref TEXT NOT NULL,
  expected_outcome_json TEXT NOT NULL CHECK(json_valid(expected_outcome_json)),
  evaluation_criteria_json TEXT NOT NULL CHECK(json_valid(evaluation_criteria_json)),
  horizon_end_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('open','partially_evaluated','evaluated','cancelled'))
) STRICT;

CREATE TABLE prediction_evaluations (
  evaluation_id BLOB PRIMARY KEY CHECK(length(evaluation_id)=16),
  prediction_id BLOB NOT NULL REFERENCES predictions(prediction_id),
  observed_outcome_ref TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN ('correct','partially_correct','incorrect','inconclusive')),
  evaluator TEXT NOT NULL,
  evaluated_at_ms INTEGER NOT NULL,
  details_json TEXT CHECK(details_json IS NULL OR json_valid(details_json))
) STRICT;

CREATE TABLE goals (
  goal_id BLOB PRIMARY KEY CHECK(length(goal_id)=16),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE goal_revisions (
  goal_id BLOB NOT NULL REFERENCES goals(goal_id),
  revision INTEGER NOT NULL CHECK(revision>0),
  description TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('proposed','active','paused','completed','abandoned','blocked')),
  priority REAL NOT NULL,
  constraints_json TEXT NOT NULL CHECK(json_valid(constraints_json)),
  reason_ref TEXT,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(goal_id,revision)
) STRICT;

CREATE TABLE plans (
  plan_id BLOB PRIMARY KEY CHECK(length(plan_id)=16),
  goal_id BLOB NOT NULL,
  goal_revision INTEGER NOT NULL,
  plan_version INTEGER NOT NULL CHECK(plan_version>0),
  status TEXT NOT NULL CHECK(status IN ('draft','ready','running','paused','completed','failed','superseded')),
  created_at_ms INTEGER NOT NULL,
  FOREIGN KEY(goal_id,goal_revision) REFERENCES goal_revisions(goal_id,revision),
  UNIQUE(goal_id,plan_version)
) STRICT;

CREATE TABLE plan_steps (
  step_id BLOB PRIMARY KEY CHECK(length(step_id)=16),
  plan_id BLOB NOT NULL REFERENCES plans(plan_id),
  sequence INTEGER NOT NULL CHECK(sequence>=0),
  description TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('pending','ready','running','completed','failed','skipped','blocked','awaiting_input','awaiting_permission','paused','cancelled','stale','superseded','uncertain','retry_wait')),
  action_id BLOB CHECK(action_id IS NULL OR length(action_id)=16),
  created_at_ms INTEGER NOT NULL,
  UNIQUE(plan_id,sequence)
) STRICT;

CREATE TABLE plan_step_dependencies (
  step_id BLOB NOT NULL REFERENCES plan_steps(step_id),
  depends_on_step_id BLOB NOT NULL REFERENCES plan_steps(step_id),
  PRIMARY KEY(step_id,depends_on_step_id),
  CHECK(step_id<>depends_on_step_id)
) STRICT;

CREATE TABLE learning_updates (
  learning_update_id BLOB PRIMARY KEY CHECK(length(learning_update_id)=16),
  mechanism TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN
    ('identified','proposed','evaluating','accepted','rejected','revised','deferred','rolled_back')),
  evidence_ref TEXT NOT NULL,
  baseline_ref TEXT,
  evaluation_ref TEXT,
  decision_reason TEXT,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  CHECK(updated_at_ms>=created_at_ms),
  CHECK(state NOT IN ('accepted','rolled_back') OR
        (baseline_ref IS NOT NULL AND evaluation_ref IS NOT NULL))
) STRICT;
CREATE INDEX idx_learning_state ON learning_updates(state,updated_at_ms);

CREATE TABLE retention_jobs (
  retention_job_id BLOB PRIMARY KEY CHECK(length(retention_job_id)=16),
  subject_type TEXT NOT NULL,
  subject_id BLOB NOT NULL,
  requested_at_ms INTEGER NOT NULL,
  active_deleted_at_ms INTEGER,
  index_cleanup_at_ms INTEGER,
  sync_cleanup_at_ms INTEGER,
  backup_expiry_at_ms INTEGER,
  status TEXT NOT NULL CHECK(status IN ('queued','processing','waiting_backup_expiry','completed','failed')),
  failure_ref TEXT
) STRICT;
```

### 26.3 Event/recovery database — aurion_events.db

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE events (
  -- Assigned by this event store at durable append; never supplied by the producer.
  event_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id BLOB NOT NULL UNIQUE CHECK(length(event_id)=16),
  message_id BLOB NOT NULL UNIQUE CHECK(length(message_id)=16),
  message_type TEXT NOT NULL,
  contract_version TEXT NOT NULL,
  producer_component TEXT NOT NULL,
  producer_instance_id BLOB NOT NULL CHECK(length(producer_instance_id)=16),
  correlation_id BLOB NOT NULL CHECK(length(correlation_id)=16),
  causation_id BLOB CHECK(causation_id IS NULL OR length(causation_id)=16),
  occurred_at_ms INTEGER NOT NULL,
  recorded_at_ms INTEGER NOT NULL,
  payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
  payload_digest TEXT NOT NULL,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  retention_class TEXT NOT NULL CHECK(retention_class IN ('operational','durable','audit','recovery'))
) STRICT;
CREATE INDEX idx_events_type_time ON events(message_type,occurred_at_ms DESC);
CREATE INDEX idx_events_correlation ON events(correlation_id,occurred_at_ms);

CREATE TABLE event_consumers (
  consumer_id TEXT PRIMARY KEY,
  -- Last committed local events.event_sequence consumed by this consumer.
  last_sequence INTEGER NOT NULL DEFAULT 0 CHECK(last_sequence>=0),
  updated_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE event_receipts (
  consumer_id TEXT NOT NULL REFERENCES event_consumers(consumer_id),
  message_id BLOB NOT NULL CHECK(length(message_id)=16),
  payload_digest TEXT NOT NULL,
  processed_at_ms INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('applied','duplicate','rejected','deferred')),
  diagnostic_ref TEXT,
  PRIMARY KEY(consumer_id,message_id)
) STRICT;

CREATE TABLE operations (
  operation_id BLOB PRIMARY KEY CHECK(length(operation_id)=16),
  operation_type TEXT NOT NULL,
  origin_goal_id BLOB CHECK(origin_goal_id IS NULL OR length(origin_goal_id)=16),
  origin_plan_id BLOB CHECK(origin_plan_id IS NULL OR length(origin_plan_id)=16),
  state TEXT NOT NULL CHECK(state IN
    ('proposed','validating','awaiting_approval','ready','dispatched','running','succeeded','failed','rejected','expired','revoked','cancel_requested','cancelled','uncertain','reconciling','compensation_required','compensating','compensated','manual_intervention')),
  idempotency_key TEXT,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  terminal_at_ms INTEGER
) STRICT;
CREATE UNIQUE INDEX idx_operation_idempotency ON operations(operation_type,idempotency_key)
  WHERE idempotency_key IS NOT NULL;
CREATE INDEX idx_operations_state ON operations(state,updated_at_ms);

CREATE TABLE operation_steps (
  operation_step_id BLOB PRIMARY KEY CHECK(length(operation_step_id)=16),
  operation_id BLOB NOT NULL REFERENCES operations(operation_id),
  step_number INTEGER NOT NULL CHECK(step_number>=0),
  action_id BLOB NOT NULL CHECK(length(action_id)=16),
  state TEXT NOT NULL CHECK(state IN
    ('pending','validating','awaiting_approval','ready','dispatched','running','succeeded','failed','rejected','expired','revoked','cancel_requested','cancelled','uncertain','reconciling','compensation_required','compensating','compensated','manual_intervention')),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
  result_ref TEXT,
  updated_at_ms INTEGER NOT NULL,
  UNIQUE(operation_id,step_number)
) STRICT;

CREATE TABLE recovery_journal (
  journal_id BLOB PRIMARY KEY CHECK(length(journal_id)=16),
  operation_id BLOB NOT NULL REFERENCES operations(operation_id),
  phase TEXT NOT NULL,
  local_store TEXT NOT NULL,
  local_record_ref TEXT,
  intended_transition TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','applied','compensated','manual_intervention')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  diagnostic_ref TEXT
) STRICT;
CREATE INDEX idx_recovery_pending ON recovery_journal(state,updated_at_ms)
  WHERE state IN ('pending','manual_intervention');

CREATE TABLE outbox (
  outbox_id BLOB PRIMARY KEY CHECK(length(outbox_id)=16),
  message_id BLOB NOT NULL UNIQUE CHECK(length(message_id)=16),
  destination TEXT NOT NULL,
  envelope_json TEXT NOT NULL CHECK(json_valid(envelope_json)),
  state TEXT NOT NULL CHECK(state IN ('pending','published','dead_letter')),
  attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count>=0),
  next_attempt_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  published_at_ms INTEGER,
  last_error_ref TEXT
) STRICT;
CREATE INDEX idx_outbox_dispatch ON outbox(state,next_attempt_at_ms);

CREATE TABLE task_runs (
  task_run_id BLOB PRIMARY KEY CHECK(length(task_run_id)=16),
  task_definition_ref TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN
    ('queued','running','paused','completed','failed','cancelled','blocked','lost')),
  priority REAL NOT NULL,
  budget_json TEXT NOT NULL CHECK(json_valid(budget_json)),
  created_at_ms INTEGER NOT NULL,
  started_at_ms INTEGER,
  updated_at_ms INTEGER NOT NULL,
  completed_at_ms INTEGER
) STRICT;

CREATE TABLE task_checkpoints (
  checkpoint_id BLOB PRIMARY KEY CHECK(length(checkpoint_id)=16),
  task_run_id BLOB NOT NULL REFERENCES task_runs(task_run_id),
  sequence INTEGER NOT NULL CHECK(sequence>=0),
  checkpoint_ref TEXT NOT NULL,
  state_digest TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE(task_run_id,sequence)
) STRICT;
```

### 26.4 Governance database — aurion_governance.db

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE schema_migrations (
  version INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE policies (
  policy_id BLOB PRIMARY KEY CHECK(length(policy_id)=16),
  policy_name TEXT NOT NULL,
  policy_version INTEGER NOT NULL CHECK(policy_version>0),
  policy_document_json TEXT NOT NULL CHECK(json_valid(policy_document_json)),
  protected INTEGER NOT NULL CHECK(protected IN (0,1)),
  active INTEGER NOT NULL CHECK(active IN (0,1)),
  created_at_ms INTEGER NOT NULL,
  UNIQUE(policy_name,policy_version)
) STRICT;
CREATE UNIQUE INDEX idx_policy_active ON policies(policy_name) WHERE active=1;

CREATE TABLE permissions (
  permission_id BLOB PRIMARY KEY CHECK(length(permission_id)=16),
  subject_id TEXT NOT NULL,
  capability_id TEXT NOT NULL,
  operation_scope_json TEXT NOT NULL CHECK(json_valid(operation_scope_json)),
  resource_scope_json TEXT NOT NULL CHECK(json_valid(resource_scope_json)),
  data_scope_json TEXT NOT NULL CHECK(json_valid(data_scope_json)),
  side_effect_scope_json TEXT NOT NULL CHECK(json_valid(side_effect_scope_json)),
  environment_scope_json TEXT NOT NULL CHECK(json_valid(environment_scope_json)),
  budget_json TEXT CHECK(budget_json IS NULL OR json_valid(budget_json)),
  valid_from_ms INTEGER NOT NULL,
  expires_at_ms INTEGER,
  grant_source TEXT NOT NULL,
  policy_id BLOB NOT NULL REFERENCES policies(policy_id),
  revoked_at_ms INTEGER,
  revocation_reason TEXT,
  created_at_ms INTEGER NOT NULL,
  CHECK(expires_at_ms IS NULL OR expires_at_ms>valid_from_ms)
) STRICT;
CREATE INDEX idx_permissions_lookup ON permissions(subject_id,capability_id,valid_from_ms,expires_at_ms);

CREATE TABLE approval_requests (
  request_id BLOB PRIMARY KEY CHECK(length(request_id)=16),
  operation_id BLOB NOT NULL CHECK(length(operation_id)=16),
  requester_id TEXT NOT NULL,
  operation_digest TEXT NOT NULL,
  operation_summary TEXT NOT NULL,
  risk_class TEXT NOT NULL CHECK(risk_class IN ('R0','R1','R2','R3','R4','R5')),
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  recipient_summary TEXT,
  policy_version_ref TEXT NOT NULL,
  requested_at_ms INTEGER NOT NULL,
  expires_at_ms INTEGER NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('pending','approved','denied','expired','invalidated','revoked')),
  CHECK(expires_at_ms>requested_at_ms)
) STRICT;
CREATE INDEX idx_approval_expiry ON approval_requests(state,expires_at_ms);

CREATE TABLE approval_decisions (
  decision_id BLOB PRIMARY KEY CHECK(length(decision_id)=16),
  request_id BLOB NOT NULL UNIQUE REFERENCES approval_requests(request_id),
  authenticated_owner_ref TEXT NOT NULL,
  decision TEXT NOT NULL CHECK(decision IN ('approved','denied')),
  approved_digest TEXT NOT NULL,
  decided_at_ms INTEGER NOT NULL,
  authentication_context_ref TEXT NOT NULL
) STRICT;

CREATE TABLE protected_changes (
  change_id BLOB PRIMARY KEY CHECK(length(change_id)=16),
  target_ref TEXT NOT NULL,
  old_version_ref TEXT NOT NULL,
  candidate_version_ref TEXT NOT NULL,
  approval_request_id BLOB NOT NULL REFERENCES approval_requests(request_id),
  validation_report_ref TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('proposed','validated','approved','activated','rolled_back','rejected')),
  created_at_ms INTEGER NOT NULL,
  activated_at_ms INTEGER,
  rolled_back_at_ms INTEGER
) STRICT;

CREATE TABLE governance_audit (
  audit_id BLOB PRIMARY KEY CHECK(length(audit_id)=16),
  actor_id TEXT NOT NULL,
  action TEXT NOT NULL,
  target_ref TEXT,
  decision TEXT,
  policy_version_ref TEXT,
  operation_id BLOB,
  request_id BLOB,
  details_digest TEXT NOT NULL,
  occurred_at_ms INTEGER NOT NULL,
  previous_record_digest TEXT,
  record_digest TEXT NOT NULL
) STRICT;
CREATE INDEX idx_governance_audit_time ON governance_audit(occurred_at_ms DESC);

CREATE TABLE provider_permissions (
  provider_permission_id BLOB PRIMARY KEY CHECK(length(provider_permission_id)=16),
  provider_id TEXT NOT NULL,
  capability_scope_json TEXT NOT NULL CHECK(json_valid(capability_scope_json)),
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  purpose_scope_json TEXT NOT NULL CHECK(json_valid(purpose_scope_json)),
  policy_id BLOB NOT NULL REFERENCES policies(policy_id),
  valid_from_ms INTEGER NOT NULL,
  expires_at_ms INTEGER,
  revoked_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  CHECK(expires_at_ms IS NULL OR expires_at_ms>valid_from_ms)
) STRICT;

CREATE TABLE data_disclosures (
  disclosure_id BLOB PRIMARY KEY CHECK(length(disclosure_id)=16),
  provider_id TEXT NOT NULL,
  purpose TEXT NOT NULL,
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  payload_digest TEXT NOT NULL,
  payload_ref TEXT,
  approval_request_id BLOB REFERENCES approval_requests(request_id),
  policy_version_ref TEXT NOT NULL,
  disclosed_at_ms INTEGER NOT NULL,
  outcome TEXT NOT NULL CHECK(outcome IN ('sent','blocked','failed','uncertain'))
) STRICT;
CREATE INDEX idx_disclosures_provider_time ON data_disclosures(provider_id,disclosed_at_ms DESC);
```

### 26.5 DDL review issues that must be resolved before implementation

- Belief current revision is deliberately query-derived: select the latest committed revision by revision number. This avoids a mutable pointer that can reference another belief's revision.
- Plan dependency acyclicity must be enforced by planner validation and transactional tests; SQLite CHECK constraints cannot express arbitrary graph-cycle detection.
- Cross-file action/goal/plan references require reconciliation because they are not foreign keys.
- JSON validity is not schema validation, authorization or encryption. Validate each JSON document against its contract before storage.
- The proposed additive memory-schema migration in Section 26.5.1 now defines artifact metadata and lineage tables; execution, hash/lineage invariants and deletion/restore fault tests remain outstanding.
- Define sensitive event-payload encryption/redaction before durable event storage.
- Audit-chain hashes need an external signed checkpoint if tamper evidence against whole-database rewrite is required.
- Use non-null idempotency keys for operations that claim idempotency; enforce this at operation creation.
- Verify STRICT, JSON functions, WAL and foreign-key behaviour on the actual SQLite runtime before adopting this DDL unchanged.

### 26.5.1 Capability and cognitive-state schema extension — proposed migration v2

The initial memory DDL did not include durable storage for the artifact registry, dynamic capability registry and several durable cognitive state domains introduced by the Android and cognitive mechanism architectures. That is a schema completeness gap; the registry must not be hidden inside an untyped blob or confused with governance permissions.

The following is a proposed additive migration for `aurion_memory.db`. It is not executed or validated. It deliberately stores capability descriptions and evidence-backed knowledge separately from authority grants. Current Android permission state remains authoritative in the OS and is rechecked at execution; AURIONS grants/approvals remain in `aurion_governance.db`.

```sql
CREATE TABLE artifacts (
  artifact_id BLOB PRIMARY KEY CHECK(length(artifact_id)=16),
  artifact_kind TEXT NOT NULL,
  logical_name TEXT NOT NULL,
  semantic_version TEXT,
  sha256 TEXT NOT NULL CHECK(length(sha256)=64),
  byte_size INTEGER NOT NULL CHECK(byte_size>=0),
  media_type TEXT NOT NULL,
  storage_uri TEXT NOT NULL,
  producer_id TEXT NOT NULL,
  producer_version TEXT NOT NULL,
  source_operation_id TEXT,
  provenance_ref TEXT NOT NULL,
  license_ref TEXT,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  retention_class TEXT NOT NULL,
  encryption_key_ref TEXT,
  validation_state TEXT NOT NULL CHECK(validation_state IN
    ('unvalidated','validated','rejected','quarantined')),
  availability_state TEXT NOT NULL CHECK(availability_state IN
    ('available','missing','corrupt','quarantined')),
  deletion_state TEXT NOT NULL CHECK(deletion_state IN
    ('active','pending_deletion','deleted_active','backup_expiry_pending')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  deleted_at_ms INTEGER,
  CHECK(updated_at_ms>=created_at_ms),
  CHECK(deleted_at_ms IS NULL OR deleted_at_ms>=created_at_ms),
  CHECK(deletion_state NOT IN ('pending_deletion','deleted_active','backup_expiry_pending') OR deleted_at_ms IS NOT NULL)
) STRICT;
CREATE INDEX idx_artifacts_hash ON artifacts(sha256);
CREATE INDEX idx_artifacts_kind_status ON artifacts(artifact_kind,validation_state,availability_state);
CREATE INDEX idx_artifacts_retention ON artifacts(retention_class,deletion_state);

CREATE TABLE artifact_lineage (
  parent_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
  child_artifact_id BLOB NOT NULL REFERENCES artifacts(artifact_id),
  transformation_id TEXT NOT NULL,
  configuration_digest TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(parent_artifact_id,child_artifact_id,transformation_id),
  CHECK(parent_artifact_id<>child_artifact_id)
) STRICT;
CREATE INDEX idx_artifact_lineage_child ON artifact_lineage(child_artifact_id);

CREATE TABLE capability_descriptors (
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL CHECK(descriptor_version>0),
  provider_id TEXT NOT NULL,
  device_scope TEXT NOT NULL,
  discovery_epoch TEXT NOT NULL,
  descriptor_json TEXT NOT NULL CHECK(json_valid(descriptor_json)),
  descriptor_sha256 TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN
    ('discovered','unverified','verified','unavailable','permission_required',
     'revoked','stale','retired')),
  source_ref TEXT NOT NULL,
  first_discovered_at_ms INTEGER NOT NULL,
  last_verified_at_ms INTEGER,
  expires_at_ms INTEGER,
  PRIMARY KEY(capability_id,descriptor_version),
  CHECK(expires_at_ms IS NULL OR expires_at_ms>first_discovered_at_ms),
  CHECK(status<>'verified' OR last_verified_at_ms IS NOT NULL)
) STRICT;
CREATE INDEX idx_capability_status_freshness
  ON capability_descriptors(device_scope,status,expires_at_ms);

CREATE TABLE capability_discovery_evidence (
  discovery_evidence_id BLOB PRIMARY KEY CHECK(length(discovery_evidence_id)=16),
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL,
  source_experience_id BLOB REFERENCES experiences(experience_id),
  evidence_id BLOB REFERENCES evidence_items(evidence_id),
  discovery_method TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN ('supports','contradicts','inconclusive')),
  confidence REAL CHECK(confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
  observed_at_ms INTEGER NOT NULL,
  details_json TEXT NOT NULL CHECK(json_valid(details_json)),
  CHECK(source_experience_id IS NOT NULL OR evidence_id IS NOT NULL),
  FOREIGN KEY(capability_id,descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version)
) STRICT;
CREATE INDEX idx_capability_discovery_time
  ON capability_discovery_evidence(capability_id,observed_at_ms DESC);

CREATE TABLE capability_knowledge_revisions (
  knowledge_revision_id BLOB PRIMARY KEY CHECK(length(knowledge_revision_id)=16),
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL,
  revision_number INTEGER NOT NULL CHECK(revision_number>0),
  context_scope_json TEXT NOT NULL CHECK(json_valid(context_scope_json)),
  claims_json TEXT NOT NULL CHECK(json_valid(claims_json)),
  confidence_json TEXT NOT NULL CHECK(json_valid(confidence_json)),
  status TEXT NOT NULL CHECK(status IN
    ('provisional','supported','disputed','superseded','withdrawn')),
  created_at_ms INTEGER NOT NULL,
  FOREIGN KEY(capability_id,descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version),
  UNIQUE(capability_id,descriptor_version,revision_number)
) STRICT;

CREATE TABLE capability_knowledge_evidence (
  knowledge_revision_id BLOB NOT NULL
    REFERENCES capability_knowledge_revisions(knowledge_revision_id),
  evidence_id BLOB NOT NULL REFERENCES evidence_items(evidence_id),
  stance TEXT NOT NULL CHECK(stance IN ('supports','contradicts','contextualizes')),
  relevance REAL CHECK(relevance IS NULL OR relevance BETWEEN 0.0 AND 1.0),
  PRIMARY KEY(knowledge_revision_id,evidence_id,stance)
) STRICT;

CREATE TABLE capability_relationships (
  source_capability_id TEXT NOT NULL,
  source_descriptor_version INTEGER NOT NULL,
  target_capability_id TEXT NOT NULL,
  target_descriptor_version INTEGER NOT NULL,
  relation_type TEXT NOT NULL,
  conditions_json TEXT NOT NULL CHECK(json_valid(conditions_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  created_at_ms INTEGER NOT NULL,
  PRIMARY KEY(source_capability_id,source_descriptor_version,
               target_capability_id,target_descriptor_version,relation_type),
  FOREIGN KEY(source_capability_id,source_descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version),
  FOREIGN KEY(target_capability_id,target_descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version),
  CHECK(source_capability_id<>target_capability_id OR
        source_descriptor_version<>target_descriptor_version)
) STRICT;

CREATE TABLE appraisal_records (
  appraisal_id BLOB PRIMARY KEY CHECK(length(appraisal_id)=16),
  context_id BLOB NOT NULL,
  context_version INTEGER NOT NULL,
  assessment_json TEXT NOT NULL CHECK(json_valid(assessment_json)),
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  created_at_ms INTEGER NOT NULL,
  valid_until_ms INTEGER,
  FOREIGN KEY(context_id,context_version) REFERENCES contexts(context_id,version),
  CHECK(valid_until_ms IS NULL OR valid_until_ms>created_at_ms)
) STRICT;

CREATE TABLE reasoning_assessments (
  reasoning_id BLOB PRIMARY KEY CHECK(length(reasoning_id)=16),
  context_id BLOB NOT NULL,
  context_version INTEGER NOT NULL,
  hypothesis_ref TEXT,
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  conclusion_summary_ref TEXT,
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  created_at_ms INTEGER NOT NULL,
  FOREIGN KEY(context_id,context_version) REFERENCES contexts(context_id,version)
) STRICT;

CREATE TABLE decision_records (
  decision_id BLOB PRIMARY KEY CHECK(length(decision_id)=16),
  goal_id BLOB REFERENCES goals(goal_id),
  plan_id BLOB REFERENCES plans(plan_id),
  decision_type TEXT NOT NULL CHECK(decision_type IN
    ('selected','deferred','rejected','clarification_required','cancelled')),
  selected_option_ref TEXT,
  rationale_ref TEXT NOT NULL,
  uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
  created_at_ms INTEGER NOT NULL,
  CHECK(decision_type<>'selected' OR selected_option_ref IS NOT NULL)
) STRICT;

CREATE TABLE outcome_evaluations (
  outcome_evaluation_id BLOB PRIMARY KEY CHECK(length(outcome_evaluation_id)=16),
  prediction_id BLOB REFERENCES predictions(prediction_id),
  plan_id BLOB REFERENCES plans(plan_id),
  operation_id BLOB CHECK(operation_id IS NULL OR length(operation_id)=16),
  expected_outcome_ref TEXT,
  observed_outcome_ref TEXT NOT NULL,
  result TEXT NOT NULL CHECK(result IN
    ('verified','partially_verified','not_verified','failed','inconclusive')),
  evaluation_json TEXT NOT NULL CHECK(json_valid(evaluation_json)),
  created_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE self_model_revisions (
  self_model_revision_id BLOB PRIMARY KEY CHECK(length(self_model_revision_id)=16),
  revision_number INTEGER NOT NULL UNIQUE CHECK(revision_number>0),
  claims_json TEXT NOT NULL CHECK(json_valid(claims_json)),
  confidence_json TEXT NOT NULL CHECK(json_valid(confidence_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  created_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE evolution_proposals (
  proposal_id BLOB PRIMARY KEY CHECK(length(proposal_id)=16),
  target_mechanism TEXT NOT NULL,
  description TEXT NOT NULL,
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  impact_risk_json TEXT NOT NULL CHECK(json_valid(impact_risk_json)),
  candidate_artifact_ref TEXT,
  evaluation_ref TEXT,
  state TEXT NOT NULL CHECK(state IN
    ('proposed','isolated','evaluating','awaiting_approval','approved',
     'rejected','activated','rolled_back','deferred')),
  approval_ref TEXT,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  CHECK(state NOT IN ('approved','activated') OR approval_ref IS NOT NULL)
) STRICT;
CREATE INDEX idx_evolution_state ON evolution_proposals(state,updated_at_ms);
```

**Storage semantics:**
- Artifact metadata is authoritative for immutable content references; blobs remain in filesystem/object storage. Lineage is required for derived-data deletion and model/dataset provenance. Content hashes identify bytes but do not merge authorization, retention or sensitivity semantics.
- Capability descriptors are versioned discovered interface descriptions, not permissions. The descriptor JSON is schema-validated by the application and hash-checked; unknown fields do not grant authority.
- Discovery evidence and capability knowledge revisions retain provenance and contradictory evidence. A failed attempt is contextual evidence, not a universal prohibition.
- Capability relationships describe evidence-supported composition/constraints; they are not fixed task recipes.
- Appraisal and reasoning records store bounded evidence-linked assessments and concise rationale references, not unbounded internal reasoning transcripts. Attention allocations are transient runtime state; durable attention decisions may be represented by typed events when needed.
- Decision and outcome records summarize durable decisions and observed effects. Operation lifecycle remains authoritative in `aurion_events.db`; policy grants and approvals remain authoritative in `aurion_governance.db`.
- Self-model revisions and evolution proposals preserve evidence and version history. They cannot grant permissions or activate protected changes.
- Cross-store operation IDs and approval references are validated by application services; no cross-file foreign keys are introduced.

This migration must be reconciled with the final component contracts and tested for index coverage, JSON schema validation, retention/deletion, migrations and crash recovery before implementation. Application-level invariants still include descriptor JSON schema validation, exact evidence ownership, decision-to-plan/goal consistency, capability relationship validity, and the rule that no descriptor status or learned knowledge grants authority. The migration's CHECK constraints are necessary but not sufficient.


### 26.5.2 Plan execution and operation-evidence contract extension — proposed migration

The cross-document contract audit identified that the cognitive plan contract and operation lifecycle require more structured durable state than the initial DDL currently provides. The following additions are proposed before any migration is executed. They are additive and keep capability descriptions separate from authority.

**Memory database — proposed migration v3**

```sql
CREATE TABLE plan_step_contracts (
  step_id BLOB PRIMARY KEY REFERENCES plan_steps(step_id),
  step_role TEXT NOT NULL,
  role_schema_version TEXT NOT NULL,
  capability_id TEXT,
  descriptor_version INTEGER,
  input_binding_json TEXT NOT NULL CHECK(json_valid(input_binding_json)),
  preconditions_json TEXT NOT NULL CHECK(json_valid(preconditions_json)),
  expected_effects_json TEXT NOT NULL CHECK(json_valid(expected_effects_json)),
  resource_budget_json TEXT NOT NULL CHECK(json_valid(resource_budget_json)),
  verification_contract_json TEXT NOT NULL CHECK(json_valid(verification_contract_json)),
  stop_conditions_json TEXT NOT NULL CHECK(json_valid(stop_conditions_json)),
  stale_input_digest TEXT NOT NULL,
  contract_version TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL,
  CHECK((capability_id IS NULL)=(descriptor_version IS NULL)),
  FOREIGN KEY(capability_id,descriptor_version)
    REFERENCES capability_descriptors(capability_id,descriptor_version)
) STRICT;
CREATE INDEX idx_plan_step_capability
  ON plan_step_contracts(capability_id,descriptor_version)
  WHERE capability_id IS NOT NULL;

CREATE TABLE learning_update_details (
  learning_update_id BLOB PRIMARY KEY
    REFERENCES learning_updates(learning_update_id),
  update_kind TEXT NOT NULL CHECK(update_kind IN
    ('episodic_acquisition','belief_revision','capability_knowledge',
     'strategy_mechanism','model_training','architecture_evolution')),
  hypothesis_json TEXT NOT NULL CHECK(json_valid(hypothesis_json)),
  scope_json TEXT NOT NULL CHECK(json_valid(scope_json)),
  evidence_refs_json TEXT NOT NULL CHECK(json_valid(evidence_refs_json)),
  baseline_artifact_id BLOB REFERENCES artifacts(artifact_id),
  candidate_artifact_id BLOB REFERENCES artifacts(artifact_id),
  evaluation_protocol_artifact_id BLOB REFERENCES artifacts(artifact_id),
  metrics_artifact_id BLOB REFERENCES artifacts(artifact_id),
  regression_artifact_id BLOB REFERENCES artifacts(artifact_id),
  rollback_ref TEXT,
  approval_ref TEXT,
  created_at_ms INTEGER NOT NULL
) STRICT;
```

A plan step that does not invoke an environment capability may leave `capability_id` and `descriptor_version` NULL; it still declares typed inputs, preconditions, expected effects, budgets, verification and stop conditions. The legacy `plan_steps.action_id` is not a capability identity and must not be used as a substitute for the versioned capability reference. Capability reference is not permission or approval.

**Event/recovery database — proposed migration v2**

```sql
CREATE TABLE operation_details (
  operation_id BLOB PRIMARY KEY REFERENCES operations(operation_id),
  owner_id TEXT NOT NULL,
  actor_identity TEXT NOT NULL,
  device_id BLOB NOT NULL CHECK(length(device_id)=16),
  origin_step_id BLOB CHECK(origin_step_id IS NULL OR length(origin_step_id)=16),
  capability_id TEXT NOT NULL,
  descriptor_version INTEGER NOT NULL CHECK(descriptor_version>0),
  target_ref TEXT NOT NULL,
  canonical_parameters_artifact_id BLOB NOT NULL CHECK(length(canonical_parameters_artifact_id)=16),
  parameter_digest TEXT NOT NULL CHECK(length(parameter_digest)=64),
  expected_effects_ref TEXT NOT NULL,
  sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
  data_categories_json TEXT NOT NULL CHECK(json_valid(data_categories_json)),
  risk_class TEXT NOT NULL CHECK(risk_class IN ('R0','R1','R2','R3','R4','R5')),
  policy_version_ref TEXT NOT NULL,
  approval_request_id BLOB CHECK(approval_request_id IS NULL OR length(approval_request_id)=16),
  deadline_at_ms INTEGER,
  resource_budget_json TEXT NOT NULL CHECK(json_valid(resource_budget_json)),
  canonicalization_version TEXT NOT NULL,
  created_at_ms INTEGER NOT NULL
) STRICT;

CREATE TABLE operation_attempts (
  attempt_id BLOB PRIMARY KEY CHECK(length(attempt_id)=16),
  operation_id BLOB NOT NULL REFERENCES operations(operation_id),
  attempt_number INTEGER NOT NULL CHECK(attempt_number>0),
  state TEXT NOT NULL CHECK(state IN
    ('prepared','dispatched','running','succeeded','failed','uncertain',
     'reconciling','compensation_required','compensating','compensated',
     'manual_intervention','cancelled')),
  idempotency_key TEXT NOT NULL,
  dispatched_at_ms INTEGER,
  finished_at_ms INTEGER,
  provider_receipt_ref TEXT,
  reported_effects_ref TEXT,
  verification_evidence_ref TEXT,
  error_ref TEXT,
  uncertainty_reason TEXT,
  reconciled_at_ms INTEGER,
  UNIQUE(operation_id,attempt_number),
  UNIQUE(operation_id,idempotency_key)
) STRICT;
CREATE INDEX idx_operation_attempt_state
  ON operation_attempts(state,dispatched_at_ms);

CREATE TABLE task_checkpoint_details (
  checkpoint_id BLOB PRIMARY KEY REFERENCES task_checkpoints(checkpoint_id),
  plan_id BLOB NOT NULL CHECK(length(plan_id)=16),
  plan_version INTEGER NOT NULL CHECK(plan_version>0),
  context_version_ref TEXT NOT NULL,
  capability_epoch_digest TEXT NOT NULL,
  dependency_state_digest TEXT NOT NULL,
  pending_steps_json TEXT NOT NULL CHECK(json_valid(pending_steps_json)),
  resume_conditions_json TEXT NOT NULL CHECK(json_valid(resume_conditions_json)),
  invalidation_reason TEXT,
  created_at_ms INTEGER NOT NULL
) STRICT;

```

The expanded `operations.state` and `operation_steps.state` values in the proposed base DDL are the canonical durable lifecycle projection. The operation-attempt table records each dispatch attempt and its receipt/verification evidence. Operation details bind owner, actor, device, originating plan step, exact capability version and the canonical parameter artifact ID/digest. Parameter payloads and sensitive effect details are stored as governed artifacts with sensitivity and encryption metadata, not copied as plaintext into the event database. Task checkpoint details bind a resumable checkpoint to the exact plan version, context/capability epoch and dependency-state digest. State transitions remain governed by Section 7.1; SQL CHECK constraints restrict values but do not enforce the transition graph. The command handler must atomically append the lifecycle event and update the owning projection in one `aurion_events.db` transaction.

Cross-store capability descriptor and approval references are validated by application services against the current memory and governance stores immediately before dispatch. No cross-file foreign keys are introduced.

These additions close specification mismatches only. They have not been executed, benchmarked or validated against the target SQLite build. They require migration fixtures for fresh install, upgrade, interruption, invalid references, duplicate attempts, uncertain dispatch, stale checkpoint invalidation, recovery and rollback.

### 26.6 Migration protocol

Each DB has its own monotonic migration version and checksum. There is no cross-file atomic migration.

1. Acquire exclusive per-file migration lock.
2. Read schema version and verify application compatibility.
3. Verify migration checksum.
4. Create a verified backup using SQLite backup API.
5. Apply one migration in a transaction where supported.
6. Run foreign-key check, integrity check and migration-specific invariants.
7. Update migration registry and PRAGMA user_version in the same transaction.
8. Commit, reopen and perform health checks.
9. Record cross-store migration status; reconcile if that record fails after local commit.
10. Retain pre-migration backup until new version passes acceptance tests.

Before-commit failure rolls back. After-commit/report failure is reconciled as committed. Integrity failure blocks writes and enters recovery mode. Restore coordinated DBs and artifact manifest from a consistent snapshot; never fake migration history to bypass a failure.

Migration tests: fresh install; every supported upgrade path; interruption before/after commit; checksum mismatch; integrity/foreign-key checks; coordinated restore; refusal of unsupported schema versions.

## 27. Crash recovery and operational runbook

**Status:** Proposed operational specification.

A startup recovery coordinator inspects unfinished operations, pending outbox messages, unacknowledged receipts, missing workers, checkpoints, cross-store references and incomplete backups/migrations.

| Failure point | Required response |
| --- | --- |
| Before operation record | No accepted operation; caller may submit a new request |
| After record, before dispatch | Resume only if authorization remains valid; otherwise reauthorize |
| After authorization, before execution | Recheck expiry and revocation |
| During read-only action | Retry within budget if safe |
| During local write | Inspect transaction/journal; commit or compensate idempotently |
| During external side effect | Mark uncertain; inspect provider/target before retry |
| Effect completed, result not persisted | Reconcile actual effect and persist recovered result |
| Result committed, event not published | Outbox republishes; consumer deduplicates |
| Worker disappears | Mark lost/uncertain; quarantine partial artifacts |
| Cancellation during non-interruptible action | Track cancellation request; inspect effect and notify owner if unresolved |
| One DB restored without others | Block cross-store writes until reconciliation |
| Storage exhausted | Stop nonessential work; preserve recovery metadata; report blockage |
| Provider unavailable | Use authorized compatible fallback or pause safely |

Startup order:

1. Acquire single-instance runtime lock.
2. Validate config, schema versions, DB integrity and artifact roots.
3. Verify protected governance state before enabling actions.
4. Reconcile migrations and backup manifests.
5. Reconcile operations, outbox and receipts.
6. Detect lost workers and quarantine partial artifacts.
7. Validate checkpoints and artifact checksums.
8. Rebuild disposable indexes from authoritative records if required.
9. Enable scheduler and new work only after safe recovery.

If governance cannot be trusted, permit read-only diagnostics only; disable protected actions.

Fault-injection tests must kill the process at every operation transition, duplicate outbox delivery, simulate uncertain external effects, corrupt artifacts, restore mismatched backups, exhaust storage, revoke permissions during pause and kill workers mid-output.

## 28. Retention, deletion, backup and synchronization

**Owner decision: historical backups containing deleted information expire within 30 days.**

Deletion workflow:

1. Write durable deletion job and tombstone.
2. Immediately exclude the subject from ordinary retrieval.
3. Remove/invalidate active records and retrieval-index entries.
4. Remove attributable caches and pending derived artifacts.
5. Propagate tombstone to every registered device.
6. Exclude content from all future backups.
7. Expire historical backups containing it no later than 30 days after deletion.
8. Verify completion across registered stores/devices.
9. Retain only minimal deletion/audit evidence, not the deleted content.

Backups are encrypted and have manifests for DB versions, artifact versions, snapshot time, runtime/device version and checksums. Restores replay tombstones newer than the snapshot before enabling retrieval or disclosure. Backup keys are stored separately. Restore tests are mandatory.

Deletion scope includes embeddings, indexes, summaries derived solely from deleted records, cached prompts/results, worker temp files, datasets, device replicas and exported reports. If content influenced model weights, track lineage and assess unlearning/retraining; do not claim exact removal unless validated.

Retention classes:

- Ephemeral context/diagnostics: short configurable TTL.
- Active memory: user-controlled; deletion immediately removes retrieval access.
- Operational task/checkpoint data: retain for recovery, then compact.
- Governance/audit: restricted, integrity-protected, with retention period to be finalized after jurisdictional review.
- Backups: maximum 30-day expiry for deleted content.
- Model/dataset lineage: minimum records needed for reproducibility and deletion impact assessment.

Sync rules: tombstones beat stale replicas; important belief/goal conflicts create versions, not silent last-write-wins; governance is not merged as ordinary data; sync is authenticated, encrypted, replay-protected and idempotent. A device offline beyond tombstone retention must fully reconcile before contributing data.

Tests: immediate retrieval exclusion, index rebuild, offline-device tombstone, future-backup exclusion, restore+tombstone replay, 30-day expiry, derived-artifact lineage and audit redaction.

## 29. Test catalogue and evidence standard

| Test layer | Required proof |
| --- | --- |
| Unit | Deterministic invariants and fixtures |
| Contract | Same C++/Python valid and invalid fixture corpus |
| Integration | Reproducible interface and persistence tests |
| Cognitive cycle | Trace from experience through outcome and later use |
| Learning | Held-out improvement and regression report |
| Evolution | Isolated candidate, approval, rollout and rollback evidence |
| Security | Adversarial boundary and denial tests |
| Recovery | Fault-injection and restored DB integrity |
| Performance | RSS, latency, throughput, thermal and battery measurements |
| Compatibility | ARM64/Termux build matrix |
| Multi-device | Authenticated sync, replay, conflict and deletion tests |

Required end-to-end scenarios:

1. Experience survives restart and is retrieved with provenance.
2. Contradictory evidence creates a traceable belief revision.
3. Prediction is committed before its observation window and evaluated later.
4. Goal revision does not rewrite plans based on the prior revision.
5. Denied action never reaches tool execution.
6. Altered target invalidates exact approval.
7. Permitted action outcome influences a later related task.
8. Uncertain side effect is reconciled before retry.
9. Candidate learning update is compared against held-out baseline.
10. Regression causes rejection or rollback.
11. Deletion propagates to index, sync and backup lifecycle.
12. Cross-store interruptions reconcile.
13. Core local operation works without network.
14. Memory/storage pressure causes safe degradation.
15. Inference provider can be replaced without changing cognitive contracts.

Learning is demonstrated only with a frozen baseline, predefined held-out tasks/metrics, reproducible candidate/config, multiple relevant tasks, regression checks, persistence evidence and a recorded accept/reject/rollback decision. Data accumulation or a single improved answer is not proof.

Benchmark the actual phone under cold/warm load, several context sizes, thread counts, memory pressure, foreground/background contention, sustained thermal load and controlled battery intervals. Record OS, device, model checksum and runtime config. Set numerical gates after measurements. One successful Qwen3-4B CLI inference does not prove continuous background suitability or local fine-tuning feasibility.

## 30. Dependency, licensing and platform review

This is a review checklist, not a completed legal audit.

Every dependency needs exact version/source, license, ARM64 and Termux compatibility, maintenance/security review, transitive dependency inventory, reproducible build/checksum, fallback/removal plan and a concrete reason for adoption.

Initial categories:

- Clang/CMake: pin supported versions and reproduce builds.
- llama.cpp: pin commit/build flags; review code license separately from model license.
- SQLite: confirm runtime version, compile options, WAL and backup behaviour.
- JSON/schema validation: license and C++/Python fixture parity.
- Python ML: select only after task-specific experiments; validate ARM64 availability, build cost, RAM and disk.
- Cryptography: use maintained established libraries; no custom cryptographic primitives.
- Test frameworks: verify license, ARM64 and CI support.
- Android bridge: Kotlin/native integration later; verify API and background execution limits.

Track model, tokenizer, dataset, code and resulting artifact licenses separately. Record source, version, checksum, use restrictions, provenance, redistribution terms and fine-tuning lineage. Downloadability does not imply unrestricted use.

Termux is a development/runtime environment, not a guarantee of always-on background execution. Android can stop processes, reclaim memory and restrict notifications. The phone has about 6 GB physical RAM; storage-backed RAM expansion is not equivalent. Existing local inference proves basic inference only, not training, sustained operation or multi-service concurrency.

Exit criteria: dependency bill of materials, model/dataset license register, ARM64 build verification, unnecessary dependency removal and documented unsupported platform assumptions.

## 31. Architecture consistency review and planning exit gate — historical baseline

The gate principles remain relevant, but the work-package and status snapshot in this section is superseded by [Canonical Implementation Roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md) and [Planning Completion Register](PLANNING-COMPLETION-REGISTER.md).

Mandatory pre-implementation resolutions:

1. Event outbox ownership and per-workflow cross-store write order must be explicit. A separate event DB cannot make a memory DB commit atomic.
2. Artifact registry must define immutable IDs, versions, checksums, filesystem layout, access and deletion.
3. Sensitive event payload encryption/redaction must be defined before durable logging.
4. Owner authentication for Termux approval must be specified; an approval digest or UUID is not authentication.
5. Key storage, recovery and backup separation must be defined before encrypted persistence is enabled.
6. SQLite runtime capabilities must be verified.
7. Local inference and local fine-tuning feasibility must be assessed separately; heavy training may require approved external compute.
8. Memory update, belief revision, strategy learning, retrieval adaptation and model-weight updates need separate evidence/rollback rules.
9. Goal provenance and conflict resolution must prevent autonomy from expanding its own authority.
10. Background tasks need deadlines, memory/CPU/network/cost budgets and preemption rules.

Initial planning is complete only when mission/non-goals, owner decisions, architecture, schemas/migrations, contracts, authorization/privacy, recovery/deletion, test catalogue, dependency/license review, device limitations, work-package dependencies and acceptance evidence are all consolidated and reviewed. No implementation starts until the user approves the consolidated specification and roadmap.

Implementation roadmap:

- **A — Foundation:** repository/build baseline, dependency inventory, contracts, IDs/time/errors, CI and architecture checks.
- **B — Persistence/recovery:** DBs, migrations, artifact registry, outbox/inbox, operation journal, backup/restore and tombstones.
- **C — Runtime/inference:** process lifecycle, model adapter, resource telemetry, scheduler and offline operation.
- **D — Experience/memory:** observation, provenance, representation, context, memory and retrieval.
- **E — Knowledge/cognition:** evidence, belief revision, prediction/evaluation, reasoning and appraisal interfaces.
- **F — Goals/action:** goal revisions, planning, tool registry, execution gateway and permissions.
- **G — Demonstrable learning:** outcome feedback, held-out evaluation, learning updates and strategy adaptation.
- **H — Self-model/evolution:** capability/performance model, candidate evaluation, approval, rollout and rollback.
- **I — Hardening:** fault injection, security, performance, resource limits and recovery exercises.
- **J — Expansion:** voice/native Android, broader tools, external compute and multi-device sync after earlier gates pass.

Every work package must specify inputs/dependencies, owned outputs, interface references, tests, acceptance evidence, resource/security constraints and rollback/recovery. Prose alone does not make a package implementation-ready.

## Change log update

- Added Section 26: initial three-file SQLite DDL, integrity caveats and migration protocol.
- Added Section 27: startup recovery and crash/failure procedures.
- Added Section 28: deletion, 30-day backup expiry, derived data and sync.
- Added Section 29: test catalogue, learning evidence and device benchmark protocol.
- Added Section 30: dependency, licensing, model/data and platform review.
- Added Section 31: consistency blockers, planning exit gate and roadmap.
- These are planning specifications. No SQL was executed and no repository code was changed.

## 32. Canonical interface and event contracts

**Status:** Normative design baseline. Exact C++ type names are selected during WP-01; wire semantics are fixed here.

### 41.1 Common message envelope

Every inter-module event and worker message carries:

```json
{
  "message_id": "uuid",
  "message_type": "experience.observed",
  "contract_version": "1.0",
  "producer": {"component": "experience", "instance_id": "uuid", "runtime_version": "semver"},
  "occurred_at": "RFC3339 UTC",
  "recorded_at": "RFC3339 UTC",
  "correlation_id": "uuid",
  "causation_id": "uuid-or-null",
  "operation_id": "uuid-or-null",
  "sensitivity": "public|internal|private|restricted",
  "payload": {},
  "payload_digest": "sha256"
}
```

Rules:

- IDs are generated before durable dispatch and remain stable across retries.
- Reuse of a message ID with a different digest is a contract/security violation; quarantine it.
- Correlation groups a workflow; causation identifies the immediate triggering message.
- Occurred time is producer time; recorded time is receiver persistence time.
- Reject unknown major versions. Ignore unknown optional minor-version fields only where the schema explicitly allows it.
- Enforce payload size limits and typed schemas. JSON validity alone is insufficient.
- Encrypt or redact sensitive payloads before durable storage; never copy secrets into diagnostic logs.
- Events are immutable facts. Commands are explicit requests; never disguise a command as an event.

### 41.2 Core event families

| Event | Required semantics |
| --- | --- |
| experience.observed | source, content/artifact reference, observation time, provenance, sensitivity |
| representation.created | source experience IDs, type, method/version, content reference, uncertainty |
| context.revised | context identity/version, scope, validity interval, provenance |
| memory.recorded | memory identity/type, source references, retention class, sensitivity |
| belief.revised | belief identity, prior/new revision, epistemic status, evidence and reason |
| prediction.issued | prediction identity, expected outcome, criteria, evaluation horizon |
| prediction.evaluated | original prediction ID, observed outcome, evaluator and result |
| goal.revised | goal ID, prior/new revision, reason/provenance |
| plan.created | plan ID/version, goal revision, ordered steps and dependencies |
| action.proposed | operation/action ID, capability, exact target/effects, data scope, risk and budget |
| authorization.decided | operation digest, policy version, decision and approval reference |
| action.completed / action.failed | operation/step IDs, actual effects, result reference and verification |
| learning.update_proposed | mechanism, evidence, hypothesis, baseline and evaluation plan |
| learning.update_decided | candidate, evaluation report, decision and rollback reference |
| evolution.proposed | limitation evidence, candidate scope, impact and validation plan |

Semantic changes require a new major contract version. Event payloads must not contain credentials or unbounded raw conversation dumps by default.

### 41.3 C++ interface rules

- Public module interfaces use explicit value types, typed results/errors and stable IDs; no shared mutable global state.
- Asynchronous work uses cancellation tokens, deadlines and explicit lifecycle states.
- Every mutating operation accepts an operation context: operation ID, correlation ID, deadline, budget and authorization reference.
- Modules access owned persistence through APIs; no direct writes into another module's tables.
- Inject clock, ID generator, storage, inference, event transport and tools for deterministic tests.
- Error categories: invalid input, contract/version mismatch, unauthorized, unavailable, timeout, resource exhausted, conflict, persistence failure, uncertain side effect, cancelled and internal fault.
- Diagnostics are structured and must not expose secrets.

### 41.4 Python worker contract

Workers are replaceable, separately supervised processes. They do not own live cognition, user authority, production deployment or protected policy.

Requests carry job ID/type, contract version, attempt, creation/deadline times, immutable input artifact IDs/checksums, dataset/model versions, configuration, resource budget, network mode, output schema, evaluation protocol and cancellation/checkpoint instructions.

Responses carry the same job ID/version; state (accepted, running, checkpointed, succeeded, failed, cancelled, timed out or resource exhausted); output artifact references/checksums; metrics; reproducibility metadata; diagnostics; and worker version.

Workers do not write application databases, change permissions or activate production artifacts. The C++ coordinator validates worker identity, schema, checksum, budget and output. Duplicate delivery is idempotent; partial outputs are quarantined.

### 41.5 Contract compatibility

Maintain versioned JSON Schema or equivalent typed definitions and one shared fixture corpus consumed by C++ and Python. CI tests valid/invalid payloads, missing fields, unknown versions, size limits, duplicate IDs, digest mismatch, cancellation, deadline expiry and compatibility. Breaking changes require migration notes and a compatibility window for persisted messages.

## 33. Artifact registry and content-addressed storage

**Status:** Accepted design requirement; implementation belongs to WP-02.

Every durable file/model/dataset/checkpoint/report has an immutable artifact record containing:

- UUID, kind, logical name and semantic version.
- SHA-256, byte size, media type and storage URI.
- Creation time, producer version and source operation/job.
- Parent/input artifact IDs and transformation/configuration digest.
- License/provenance, sensitivity, retention class and encryption-key reference.
- Validation, availability and deletion/tombstone states.

Store content-addressed blobs; expose opaque artifact IDs to cognitive modules. Never use user filenames as paths. Write to a temporary path, flush, verify checksum, atomically promote on the same filesystem, then commit metadata. Failed DB commits leave collectible orphans; missing/corrupt blobs are quarantined and dependent operations blocked.

Deduplication must not merge access or retention semantics. Shared bytes cannot be removed while another authorized live artifact references them. Deletion lineage traverses derived artifacts. If data influenced a model checkpoint, removing the source row is not proof that the model is clean.

## 34. Cross-store commit protocol and transactional outbox

**Status:** Normative requirement.

Separate SQLite files cannot provide one atomic transaction. Every state mutation that must emit a durable event therefore writes an outbox record in the same transaction and database as the authoritative state change.

1. Validate command and authorization.
2. Begin transaction in the owning database.
3. Apply state mutation and insert outbox record in that transaction.
4. Commit; this is the local durable acceptance point.
5. Dispatcher publishes to event DB/consumer.
6. Consumer atomically persists message and receipt.
7. Consumer applies its local state change and local outbox in one transaction.
8. Acknowledge source outbox only after durable receipt.
9. Retry at least once; deduplicate by message ID and verify digest.
10. Reconcile missing receipts, stuck dispatches and cross-store references.

Do not claim global exactly-once delivery. The guarantee is at-least-once transport, idempotent effects and reconciliation. Consumer receipt must not precede its local effect/outbox commit. External side effects remain uncertain until verified against the target. If execution may have happened but its result is missing, mark uncertain, inspect the target/provider and reconcile; never blindly retry.

## 35. Authorization, risk and privacy enforcement

**Status:** Owner policy decisions are accepted; this specifies execution semantics.

### 35.1 Authorization inputs

Evaluate authenticated principal/session assurance; capability/tool identity/version; exact operation, target and effects; data categories/sensitivity; destination/recipient/provider and purpose; scope/environment/deadline/frequency/resource budget; current permission/policy versions; reversibility/blast radius; and matching approval validity.

Decision: allow, deny, require owner approval, or defer for reconciliation. Default to deny if governance cannot be evaluated.

### 35.2 Risk classes

| Class | Examples | Default |
| --- | --- | --- |
| R0 | Local read-only retrieval, harmless diagnostics | Allow within granted scope |
| R1 | Reversible local writes, bounded local computation | Allow within explicit scope/budget |
| R2 | Material local state changes, approved dependency installation, candidate evaluation | Pre-authorized scope or owner approval |
| R3 | Non-sensitive external disclosure, approved remote compute | Provider permission and minimization; sensitive data still needs explicit approval |
| R4 | External communications, purchases, financial commitments, broad security changes | Explicit owner approval unless exact standing authorization exists |
| R5 | Permanent destructive action, protected-governance change, broad credential/key revocation | Exact owner approval, strong authentication, recovery plan and audit; some may remain prohibited |

Risk follows actual effects and data, not tool name. Shell is not inherently low-risk; a read-only API may still disclose private information.

### 35.3 Approval binding

Approval binds a canonical digest over principal, operation, exact target/parameters/effects, data categories, recipient, scope, policy version, expiry and budget. Any material change invalidates it. Approval is single-use unless the owner explicitly grants bounded reuse. A UUID/digest/model assertion is not authentication; owner identity requires a trusted authentication mechanism.

Recheck revocation immediately before execution and at safe checkpoints. Long-running actions revalidate before consequential steps. A model or governed tool cannot create, expand or renew its own permission.

### 35.4 Data egress

Identify exact fields and sensitivity; establish necessity; minimize; check provider capability and permission; redact/transform locally where feasible; obtain explicit approval for sensitive disclosure; record destination, purpose, categories, digest and result. Never put raw secrets or sensitive payloads in audit logs. A connected provider is not authorized to access all memory.

## 36. Security, keys and threat model

Threats: prompt/content injection, compromised tools, stolen device, local compromise, malicious dependencies/models, replay, forged approval, database tampering, unauthorized sync peer, provider leakage, resource exhaustion and accidental destruction.

Controls:

- Treat web pages, documents, model outputs and tool results as untrusted data, never privileged policy instructions.
- Enforce authorization independently of model reasoning at the final execution boundary.
- Least privilege for tools, workers, filesystem and network.
- Authenticate sync peers; encrypt transport; use replay-resistant identities/nonces.
- Verify provenance/checksums/signatures for dependencies, models and datasets where available.
- Separate governance and keys from ordinary memory and model-accessible content.
- Budget/rate-limit untrusted input, tools, inference and worker jobs.
- Keep secrets out of prompts, logs, crash dumps and event payloads.
- Support device lock, key rotation, revocation and recovery.
- Use established cryptographic libraries; no custom cryptography.

Key hierarchy proposal: device root secret in Android Keystore after native integration; until then use strongest practical Termux-compatible protected storage and document weaker protection. Derive separate data, backup and authentication keys with a standard KDF. Use authenticated encryption with unique nonces. Store key identifiers, never raw keys, beside ciphertext. Keep recovery material separate from backup payload and owner-controlled. Lost keys may make data unrecoverable; resolve this trade-off before production.

Security acceptance requires threat-model review, authorization bypass and replay tests, malicious tool-output tests, secret scanning, backup/key recovery exercise, device-loss/revocation scenario and independent cryptographic integration review.

## 37. Risk register

| ID | Risk | Impact | Mitigation / gate |
| --- | --- | --- | --- |
| RSK-01 | Phone limits/Android process termination | Instability/lost work | Benchmark, budgets, checkpoints, safe pause/resume; no always-on promise |
| RSK-02 | Local model quality/context limits | Poor task results | Model-independent adapter, evaluation set, approved fallback |
| RSK-03 | Local fine-tuning infeasible | Misaligned training plan | Separate inference/training; evaluate external compute |
| RSK-04 | Cross-store partial commits | Inconsistent state | Local outboxes, idempotency, journal, reconciliation, fault injection |
| RSK-05 | Prompt/tool injection | Unsafe action | Untrusted-data boundary and independent policy |
| RSK-06 | Approval spoof/scope drift | Unauthorized action | Authenticated session, exact digest, expiry, single-use approval |
| RSK-07 | Sensitive disclosure | Privacy breach | Minimize, classify, encrypt, approve and audit |
| RSK-08 | Deletion misses derived data/replicas | Retained information | Artifact lineage, tombstones, restore replay, 30-day expiry |
| RSK-09 | False learning claims | No real adaptation | Held-out baseline, regression gates, reproducible evidence |
| RSK-10 | License incompatibility | Legal/redistribution restrictions | SBOM and model/dataset license register |
| RSK-11 | Key loss/device compromise | Exposure or irrecoverable data | Key separation, recovery, rotation, revocation |
| RSK-12 | Scope expansion | Delayed milestone | Critical path; defer multi-device/voice |
| RSK-13 | Schema/contract drift | Integration failure | Versioned contracts, shared fixtures, migration CI |
| RSK-14 | Unbounded autonomy/resource use | Cost, battery, privacy, safety | Budgets, scheduler, stop conditions, audit |

Residual risks: Termux cannot guarantee background execution; no local model is guaranteed accurate; removing training influence may require retraining/unlearning; external providers add availability/data risks; an unlocked compromised device may expose data despite encryption.

## 38. Work-package deliverables and exit gates — superseded

The table previously in this section is retained in repository history and is no longer the active work-package baseline. It deferred Android integration to expansion, which conflicts with the owner's later decision that offline-capable mobile and cloud operation are concurrent first-release targets.

Use [Canonical Implementation Roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md) for the current proposed WP-00…WP-16 sequence, dependencies, first-release platform work and exit criteria. This roadmap remains subject to planning review and owner approval; it does not authorize implementation.


## 39. First milestone acceptance protocol

Milestone: persistent local assistant that converses, remembers, retrieves, reasons through a bounded objective, executes one explicitly permitted action, observes its consequence and uses the outcome later.

Pass only when one reproducible test run demonstrates:

1. Build/run in Termux on target device.
2. Local inference through model-independent interface.
3. Experience stored and retrieved after process restart.
4. Retrieval includes provenance and context/uncertainty.
5. Bounded goal and versioned plan created.
6. Action proposal passes independent policy enforcement.
7. One allowed and one denied action; denied action has no side effect.
8. Actual allowed-action outcome verified and persisted.
9. Outcome changes later retrieval/reasoning/strategy in a predefined test.
10. Operation IDs, events, decisions and persistence transitions are traceable.
11. Interrupted task recovers without duplicate side effects or corruption.
12. Local path works without network.
13. Resource use and device limitations are measured.

A scripted demo, hardcoded response, transcript alone or one successful inference is insufficient. The learned outcome must survive restart.

## 40. Earlier planning status — superseded by current completion register

This section's former status table and WP-00/WP-01 planning-exit statement were an earlier planning snapshot. They are superseded by Section 33 of this specification and by [Planning Completion Register](PLANNING-COMPLETION-REGISTER.md) and [Canonical Implementation Roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md).

In particular:
- The earlier checked/drafted status did not establish COMPLETE — VERIFIED.
- The former recommendation to begin WP-00/WP-01 is not current implementation authorization.
- Android capability discovery, cognitive mechanism contracts, cross-document consistency and canonical work-package reconciliation remain builder-owned planning work.
- External validation, independent review of the exact final revision and explicit owner approval remain separate gates.

**Current status:** Planning is IN PROGRESS. Implementation is not authorized.

## 41. Final engineering resolutions for implementation readiness

**Status:** Engineering baseline selected to close routine design gaps. These are proposed implementation constraints, not validated code. The owner retains approval over the complete specification and transition to implementation.

### 32.1 Cross-store consistency and event publication

Do not attempt distributed ACID transactions across the three SQLite files. Use a durable operation coordinator and a transactional outbox in the same database as the state mutation that must publish an event.

- The authoritative store for a domain owns its state change and its outbox row in one SQLite transaction.
- Each store has a local outbox table. The event/recovery database is the central event archive and dispatch ledger, not the only place where an event can be made durable.
- A relay copies outbox envelopes into the central event archive using stable message IDs and payload digests. Repeated delivery is expected and deduplicated by consumer ID plus message ID.
- A consumer applies its local state mutation and records its receipt in the same local transaction whenever both are in the same store. If state and receipt live in different stores, use a durable operation step and reconciliation; never claim atomicity.
- Cross-store workflows are sagas: each step records intent, performs one local transaction or external effect, records the result, and advances. Compensation is a new explicit operation, not deletion of history.
- A timeout after an external side effect yields an uncertain state, not failed; inspect the target before retrying.
- Event IDs, message IDs, operation IDs and idempotency keys are generated before dispatch and remain stable across retries.

Required envelope fields: message ID, event ID, message type, contract version, producer component, producer instance ID, occurred and recorded timestamps, correlation ID, optional causation ID, operation ID where applicable, payload, payload digest, sensitivity, retention class and trace context. Reject unknown major versions, malformed IDs, invalid timestamps, schema violations, oversized payloads and unauthorized data categories. Unknown additive fields may be ignored only when the contract explicitly permits forward-compatible extensions.

### 32.2 Artifact registry and filesystem

Add an artifact registry owned by the runtime/artifact service before production workflows depend on filesystem references.

Minimum metadata: immutable artifact ID; artifact type; semantic or content version; SHA-256 digest; byte size; media type; storage URI; creation time; producer/job; parent artifact IDs; sensitivity; retention class; license/provenance; encryption-key reference; lifecycle state; and deletion lineage.

Rules:

- Write to a temporary path, fsync where supported, verify size and digest, then atomically rename within the same filesystem.
- Publish registry metadata only after the artifact is complete and verified. A crash between file creation and metadata commit leaves an orphan for reconciliation, never a valid artifact.
- Never overwrite an artifact ID or content-addressed object. New content creates a new artifact ID/version.
- Verify expected digests where integrity matters; quarantine mismatches.
- Registry references are opaque IDs, not arbitrary user-controlled paths. Resolve paths under a fixed application root and reject traversal/symlink escapes.
- Deletion tombstones the registry record, then removes replicas and content according to retention policy. Shared artifacts require reference/lineage analysis before removal.
- Temporary files and incomplete worker outputs have bounded quotas and startup garbage collection.

### 32.3 Encryption and key management

Use a maintained cryptographic library and authenticated encryption; do not implement primitives. Encrypt sensitive content and backups at rest, and use authenticated encrypted transport for sync/provider connections.

- Separate data-encryption keys from encrypted data and backups. Use envelope encryption: a random data key encrypts content; a key-encryption key protects the data key.
- Keep key material outside ordinary SQLite rows and ordinary backups. On Android, prefer platform-backed Keystore integration when native integration exists. During Termux-only development, use a user-controlled secret or supported OS-backed facility where available; document that filesystem-only secrets are weaker if the device is compromised.
- Never log keys, plaintext sensitive payloads, authorization tokens or full private prompts by default.
- Key rotation creates a new key version and controlled re-encryption job; old keys remain available only until verified migration/backup expiry permits retirement.
- Recovery must not silently bypass encryption. Loss of required keys can make data unrecoverable; communicate this explicitly and test recovery before relying on encrypted backups.
- Cryptographic metadata records algorithm suite, key version, nonce, authentication tag and associated-data version. Nonces must be unique per key as required by the selected algorithm.
- Backups use an independently managed backup key hierarchy.

### 32.4 Owner authentication and exact approval

A UUID, approval digest or possession of a local process is not proof of owner identity.

- Define an OwnerAuthenticator interface with platform-specific implementations. The Termux bootstrap implementation requires an explicit owner-held secret/passphrase, stored only as a salted, memory-hard verifier; never store the raw secret.
- Unlock creates a short-lived authenticated owner session with expiry, session nonce and authentication strength. Lock on expiry, runtime restart where required, or explicit lock.
- High-impact approvals require fresh re-authentication. Bind approval to the exact operation digest, target, parameters, data categories, recipient, policy version, expiry and one-time request ID.
- Any material change invalidates approval. Approval is consumed once and cannot be replayed for a different operation.
- Model-generated text, local caller identity, a command-line flag or an untrusted device is not owner approval.
- If secure local secret storage cannot be established on the current Termux setup, restrict runtime to read-only and low-risk operations until a safer authenticator is available. Native Android Keystore/biometric integration is a later platform adapter, not an assumption about Termux.

### 32.5 Risk classes and authorization

Risk is determined by actual effects, scope, reversibility, data sensitivity and external impact, not by tool name.

| Class | Effect | Default policy |
| --- | --- | --- |
| R0 | Read-only local, non-sensitive diagnostics | Allowed within resource limits |
| R1 | Reversible local changes to non-sensitive state | Allowed only under explicit capability scope |
| R2 | Sensitive-data access, meaningful local side effects or bounded external data transfer | Explicit narrow permission; fresh approval when policy requires sensitive disclosure or elevated risk |
| R3 | External communication, publication, account changes or actions affecting other people | Exact owner approval unless a narrowly defined standing authorization exists |
| R4 | Financial commitment, purchase, irreversible/destructive action or security-critical change | Fresh exact owner approval and pre-execution verification |
| R5 | Protected principles, owner authority, governance root, key trust root or approval mechanism changes | Explicit owner approval through a separate protected procedure; candidate isolation and recovery path mandatory |

Standing permissions specify subject, capability, operation, target/resource, data categories, side effects, environment, budget, validity period and revocation. Deny by default when policy evaluation is unavailable or ambiguous. A model may propose but cannot grant, widen or self-renew permissions.

### 41.6 C++/Python contracts and dependency boundaries

- C++ owns authoritative runtime state, policy enforcement, operation lifecycle, goal/plan state, memory/knowledge writes, evaluation acceptance and deployment decisions.
- Python workers receive immutable job envelopes and write only to assigned staging/artifact areas. They cannot directly update live domain state, grant permissions, publish accepted knowledge or activate a model.
- Worker envelope: contract version, job ID, attempt, worker ID, job type, immutable input artifact references/digests, config artifact reference/digest, resource budget, deadline, cancellation token, required output schema, and trace/correlation IDs.
- Worker result: matching job ID and attempt, terminal state, output artifact references/digests, metrics, environment/version manifest, reproducibility metadata, warnings/errors and completion time.
- Transport: versioned JSON initially over a local process boundary (stdin/stdout or local socket), with strict size/time limits and schema validation. Keep transport behind an interface so a more efficient encoding can be benchmarked later.
- Standard error carries diagnostics; standard output carries protocol envelopes only. No shell interpolation of untrusted fields. Worker processes run with least filesystem/network privileges feasible.
- C++ validates every result, checks artifact digest and provenance, runs required evaluation, and makes the accept/reject decision.

### 41.7 Component ownership and dependency direction

| Component | Owns | May depend on | Must not own |
| --- | --- | --- | --- |
| Core orchestration | Lifecycle and workflow coordination | Contracts, runtime interfaces | Domain truth or policy bypass |
| Experience | Observations and source provenance | Event and artifact interfaces | Consolidated truth |
| Representation/context | Interpretations and scoped context versions | Experience, schemas | Authority decisions |
| Memory | Memory records, links and retrieval lifecycle | Persistence, artifact, retention | Permission grants |
| Knowledge/beliefs | Propositions, evidence and revision history | Memory, evaluation | Rewriting source evidence |
| Prediction/evaluation | Forecasts and immutable outcome evaluations | Knowledge, experience | Retrospective mutation of forecasts |
| Cognition/reasoning | Inference and synthesis | Model, knowledge, context | Direct privileged execution |
| Goals/planning | Goal revisions, plan versions and dependencies | Cognition, policy query | Expanding permissions |
| Action gateway | Tool contracts, execution and verification | Governance, operations, runtime | Policy definition or owner identity |
| Governance | Policy, permission, approval and audit | Authenticator, persistence | Model-generated authorization |
| Learning | Update hypotheses and evaluation decisions | Evidence, evaluation, workers | Direct live model activation |
| Self-model | Capability/resource/performance estimates | Telemetry, evaluation | Self-certification of authority |
| Evolution | Isolated candidates, rollout/rollback proposals | Learning, governance, artifact registry | Bypassing protected approval |
| Runtime | Process, scheduler, resource and model lifecycle | Platform adapters | Cognitive policy decisions |
| Artifact service | Immutable artifact lifecycle | Filesystem, crypto, metadata DB | Semantic interpretation |

Dependency direction is inward toward stable contracts. Domain modules call interfaces, not concrete UI/platform implementations. Governance enforcement is injected at the action boundary and cannot be bypassed by internal module calls.

### 41.8 Operational budgets and preemption

Every autonomous task receives a budget envelope: wall-clock deadline, CPU time/priority, memory ceiling, storage quota, network allowance, external spend ceiling (default zero unless explicitly authorized), retry count, concurrency class and cancellation policy. The scheduler reserves resources before starting work, checkpoints at safe boundaries, and preempts lower-priority work under memory/thermal pressure. On the phone, background execution is best-effort; missed deadlines are surfaced as delayed/blocked, not silently treated as completed.

### 41.9 Security and privacy defaults

- Local-first processing; external transfer is purpose-bound and data-minimized.
- Sensitive categories are classified before storage, indexing, prompt construction or provider transfer.
- External content is untrusted input, never policy or system authority.
- Secrets are redacted from logs, traces, crash reports and worker diagnostics.
- Tool execution uses structured arguments and fixed executable allowlists; no model-authored shell command is executed as a privileged action.
- Network egress is denied unless a task capability explicitly allows a destination and data category.
- Policy evaluation failure, corrupted governance state or unavailable authenticator fails closed for consequential actions.
- Security events and data disclosures are auditable without retaining unnecessary plaintext.

## 42. Planning status and owner gate — corrected status record

This specification contains a substantial proposed engineering baseline. The presence of the sections below does not mean the corresponding planning layers are complete or verified. The later builder audit identified remaining design work, particularly the Android environment/capability architecture, cognitive mechanism contracts, architecture-wide consistency, and reconciliation of competing work-package roadmaps.

**Status vocabulary:** SPECIFIED means documented; REVIEWED means consistency-checked; VALIDATED means tested against executable schemas, tools or measured environments; IMPLEMENTED means present in code; VERIFIED means acceptance evidence demonstrates the requirement. These states must not be conflated.

| Area | Current honest status |
| --- | --- |
| Mission, non-goals and owner decisions | SPECIFIED; consistency audit in progress |
| Architecture and module responsibilities | SPECIFIED at logical level; mechanism/interface completeness in progress |
| Android environment/capability architecture | IN PROGRESS; general discovery and learning architecture not yet complete |
| Database entities and initial DDL | Drafted; execution and target-runtime validation outstanding |
| Event/worker contracts | Semantics specified; complete executable schemas/fixtures and component traceability outstanding |
| Cross-store transaction/recovery | Protocol specified; fault-injection validation outstanding |
| Artifact registry | Design specified; implementation outstanding |
| Authorization/risk/privacy | Policy model specified; platform authenticator and enforcement validation outstanding |
| Key management/threat model | Requirements specified; platform-specific design and review outstanding |
| Deletion/backup/sync | Lifecycle specified; restore/offline-device tests outstanding |
| Test catalogue/milestone acceptance | Catalogue specified; executable fixtures/tests outstanding |
| Dependencies/licenses | Review criteria specified; actual SBOM/license audit outstanding |
| Device performance | Basic inference only; benchmark outstanding |
| Work packages/roadmap | Multiple proposals exist; canonical dependency-driven roadmap reconciliation outstanding |
| Architecture-wide consistency | IN PROGRESS |
| Implementation | Not started; not authorized |

The previous checklist's checked boxes represented that text had been drafted, not that planning layers were complete or verified. They are intentionally replaced by explicit evidence statuses.

**Planning exit is not declared.** The builder must finish the remaining design and consistency work recorded in the planning completion register. External validation, independent review of the exact final revision and explicit owner approval remain separate gates. Implementation remains blocked until the owner authorizes the transition.

## Change log — final planning consolidation

- Resolved cross-store delivery with per-store transactional outboxes, idempotent consumers and saga recovery.
- Defined immutable artifact registry and safe filesystem publication/deletion.
- Defined envelope encryption, key separation, rotation and recovery constraints.
- Defined owner authentication and one-time exact-operation approval.
- Defined R0–R5 risk classes and default-deny authorization.
- Defined C++/Python job/result contracts and worker isolation.
- Defined module ownership and dependency direction.
- Defined per-task resource budgets, cancellation and preemption.
- Consolidated privacy/security defaults and explicit fail-closed behaviour.
- Recorded an earlier draft-level planning baseline; this was later superseded by the evidence-based completion register. Drafted sections are not proof of verified planning completion.
- No implementation code, database migration, device configuration or repository changes were performed by this planning update.

- 2026-11-11: Corrected the former planning checklist: checked boxes had indicated documented sections, not verified completion. Replaced the implied completion claim with explicit specified/reviewed/validated/implemented/verified status and linked the builder-owned planning completion register.
