# AURIONS — System Architecture and Technology Baseline

**Status:** Proposed architecture baseline for owner review. The foundational [Open-World Interaction and Means Architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md) governs how AURIONS understands objectives, changing situations and possible interactions. This document establishes system-wide implementation boundaries beneath that model; it is not a complete set of implementation-ready contracts or an implementation authorization. It expands the imported engineering specification, does not lock unmeasured framework choices, and does not claim any capability is implemented.

## 1. Architectural objective

AURIONS is intended to be one persistent, adaptive intelligence system accessible through multiple interfaces, able to observe and operate authorized resources, and capable of maintaining task continuity across supported devices. It is not a collection of independent chat clients, nor should its identity and memory depend on a single UI session or physical device.

Foundational principle: **Engineer the mechanisms; let behaviour be acquired through experience.**

The architecture must provide:
- One coherent system identity and explicit identities/authority for relevant actors, owners, organizations, runtimes and resources; device identities are one possible identity class.
- A durable cognitive/runtime core independent of UI sessions, devices and any one deployment context.
- Objective-led understanding of relevant situations, entities, relationships, evidence, uncertainty and possible means.
- Context-specific observation and interaction mechanisms that may involve digital, physical, social, institutional, human-mediated or mixed contexts.
- Multiple interfaces and integrations without making any platform, connector or capability registry the definition of intelligence.
- Local-first operation and policy-controlled remote resources where applicable.
- Explicit state ownership, authority, consent, effect verification, failure recovery and auditability.
- Multi-device contracts designed early, with distributed implementation deferred until the single-runtime core is reliable.
- A mechanism-based cognitive architecture; learned behaviour must not be replaced by hardcoded stimulus-response or task-to-action conclusions.

## 2. System layers and responsibility ownership

The foundational objective/world/means distinctions are defined in [Open-World Interaction and Means Architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md). The detailed mechanism interactions, state ownership, invariants, learning distinctions and cognitive-cycle verification scenarios are defined in [Cognitive Mechanism and Interaction Architecture](COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md). The layer map below expresses implementation responsibilities, not a device-first or fixed pipeline model.


| Responsibility | What it owns | Boundary / realization |
|---|---|---|
| Objective and intent understanding | Requested outcome, source/authority, scope, constraints, ambiguity and success evidence | Cognitive core; no task-to-action lookup table |
| Situation and world understanding | Relevant entities, actors, relationships, contexts, state claims, observations, time and uncertainty | Cognitive/world-model mechanisms; open-ended representation |
| Knowledge, memory and prediction | Experiences, evidence, beliefs, causal/predictive models, retrieval and revision lineage | Domain-owned persistence and cognitive mechanisms |
| Means and affordance reasoning | Context-dependent hypotheses about actors/resources/interactions, prerequisites, effects and confidence | Cognitive reasoning; may consume integrations but is not bounded by a registry |
| Deliberation and control | Attention, reasoning, goals, plans, decisions, interruption, budgets and recovery | C++ core mechanisms and runtime coordination |
| Authority and governance | Identity, consent, permissions, policy, privacy, risk, approval, revocation and audit | Independent enforcement boundaries closest to affected resource |
| Interaction realization | Context-specific observation, communication, protocol execution, effect enforcement and receipts | Trusted integrations/providers; includes but is not limited to device agents |
| Outcome evaluation and learning | Independent observation, attribution, memory revision, experiments and competence evaluation | C++ authority with isolated workers where justified |
| User experience | Text, voice, visual status, task views, notifications, settings and accessibility | UI clients; no direct domain DB writes |
| Persistence and synchronization | Durable state, artifacts, migrations, backup, recovery, conflict and deletion | Domain-owned stores and explicit replication contracts |
| Model and inference services | Model-independent inference, routing and optional local/remote compute | Replaceable provider boundary; no authority grant |

These are logical ownership boundaries, not a mandate for one process/service per row. Retain a modular monolith at the centre. Split components only when lifecycle, security, resource isolation, platform integration or distribution gives a concrete reason.

## 3. Deployment topology

The first engineering baseline is a single-device local runtime, initially exercised in Termux; this is a validation starting point, not the complete first-release deployment scope. The C++ cognitive core remains authoritative. The CLI is the owner-selected first user-facing interface. Cloud operation and offline-capable mobile operation are concurrent first-release targets, not sequential phases.

Deployment topology proposal:
- **Offline-capable mobile runtime:** a complete local runtime with the cognitive core, local stores, local inference where feasible, environment/capability discovery, local governance and local execution. It must continue required workflows without cloud connectivity.
- **Cloud runtime:** a separately deployable runtime using the same core implementation/semantics and versioned contracts. It owns only its declared cloud-side state and resources; it cannot authorize a mobile-local operation.
- **CLI:** the first user-facing interface. It communicates with the selected runtime through the same versioned application contracts and does not bypass policy.
- **Android platform adapter/UI:** Android-specific adapters are required for the offline-mobile target; a native UI remains a separate engineering choice and is not implied by the CLI decision.
- **Optional remote services:** inference providers, search, APIs or compute; enabled only through explicit provider and data policies.

Shared core contracts do not imply shared mutable databases or automatic state replication. Cloud/mobile state ownership and any first-release cross-context continuity must be explicitly specified before implementation. Until that contract is approved, each runtime is authoritative for its own local state and cross-runtime synchronization is not assumed.

AURIONS must remain useful when remote services are unavailable. A cloud backend is not mandatory merely to support multiple devices.

## 4. Interfaces and platform strategy

### Android
**Recommended candidate:** Kotlin + Jetpack Compose for native UI and Android platform integration. Keep cognitive logic out of the UI. Connect the C++ core through either a stable C ABI/JNI boundary or a versioned local IPC boundary.

The JNI/shared-library versus isolated-process choice is unresolved. Compare startup, memory, crash isolation, lifecycle, background execution and Termux integration on the actual phone before deciding.

### Desktop
**Leading candidate:** Qt 6/QML, given the C++ core and native desktop integration. A web-based desktop shell is an alternative if it materially improves cross-platform delivery or iteration. Compare both against representative workflows; do not adopt both without a product requirement.

### Web
**Deferred candidate:** TypeScript + React for a browser client when remote access and web-specific workflows justify it. It remains an authenticated client, not a separate intelligence implementation.

### CLI
The CLI is the first user-facing interface and must support the first-release workflows through stable application contracts. It may also expose diagnostics and controlled operations, but it is not allowed to bypass core policy.

### UI contract
UI clients communicate through versioned application commands/queries and event subscriptions. Every operation carries a durable operation ID and exposes explicit lifecycle status. The UI must display permissions, external data disclosures, progress, blocked states and recovery needs. No UI can bypass the action gateway or write cognitive state directly.

## 5. Context-specific interaction realizations and discovered means

AURIONS does not assume that all possible means are device capabilities or that every interaction is mediated by a device agent. Possible means may involve actors, resources, institutions, services, interfaces, physical objects, human-mediated processes or combinations not known at design time. Their representation and evaluation are governed by the [open-world interaction architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md).

A provider, connector, device agent or capability registry may expose evidence about one class of possible interaction. Such records are contextual, versioned and evidence-backed; they are not the complete action space or the definition of what AURIONS can reason about. Descriptors record source/provenance, interface semantics, preconditions, expected effects, authority requirements, risk, reversibility, resource constraints, availability, cancellation, idempotency and verification evidence where applicable.

Discovery, belief about a possible means, technical access, permission, consent, authorization and execution are distinct. Discovering an interface does not grant permission or authorize use. Unknown interfaces remain unknown; stale evidence is revalidated; revoked authority invalidates dependent proposals. AURIONS may instead ask, wait, delegate, observe, use another evidenced means, or conclude that no currently supportable route exists. The cognitive core must not contain hardcoded task-to-action branches.

### Android as one concrete context

The Android integration is one platform-specific realization. It must observe and represent only what is actually discoverable in its supported Android/Termux context; maintain provenance and limitations; and enforce Android OS permissions separately from AURIONS governance. It cannot assume root, unrestricted shell/filesystem access, arbitrary background execution or universal application control. Its capability descriptors do not generalize to desktop, iOS, cloud, physical or human-mediated contexts.

Examples such as launching an application, adjusting volume or manipulating files are illustrative test scenarios only. They are not an exhaustive capability catalogue, a fixed first-release scope or a preselected first action. The first end-to-end Android action scenario remains an owner decision.

## 6. Multi-device identity, communication and synchronization

Multi-device support is a distributed-systems concern, not simply a UI feature. Design contracts now; implement after the single-device core works.

### Identity and pairing
- Each installation/device has a distinct cryptographic identity.
- Pairing uses an authenticated owner-authorized flow with explicit device label and capability review.
- Device trust is revocable; lost or compromised devices can be revoked.
- Device identity is distinct from owner identity and grants no sensitive authority by itself.

### Communication
- Use authenticated encrypted transport (TLS) for network links.
- HTTPS handles durable requests; WebSockets or a suitable equivalent may carry live updates.
- Evaluate gRPC/Protocol Buffers only if typed streaming or throughput justifies added complexity.
- Keep transport behind versioned contracts. Local IPC and network transport preserve the same authorization and operation semantics.
- Never expose unauthenticated core-control endpoints to a LAN or public network.

### Synchronization
- Never replicate SQLite database files directly between devices.
- Replicate versioned domain changes/events and immutable artifact references through an explicit protocol.
- Define ownership and consistency per domain: device-local telemetry may remain local; selected user-approved memories may synchronize; governance and approval state require stronger authority and audit rules.
- Include stable IDs, causal/version metadata, idempotency, tombstones, acknowledgements, retry/backoff, bounded queues and reconciliation.
- Resolve conflicts with domain-specific rules. Do not assume last-write-wins or adopt CRDTs globally; use CRDTs only where their semantics are appropriate and tested.
- Deletion tombstones propagate to offline devices and prevent deleted data from reappearing. Preserve the existing 30-day historical-backup expiry policy.
- Design end-to-end encryption and key management before enabling sensitive cross-device synchronization.

### Task continuity
Tasks have durable IDs, ownership, checkpoints, deadlines and operation receipts. A task can move to another device only through an explicit handoff transferring required context, artifact references, capability needs and operation state. An offline device cannot be assumed available. Uncertain external side effects must be reconciled before retrying elsewhere.

## 7. Model, inference and compute routing

Keep a model-independent interface. Select a model/provider based on required capability, measured quality, latency, resource budget, privacy classification, availability and cost policy.

- Local inference is preferred where it meets task requirements.
- Remote inference is optional and task-scoped; only minimum authorized context may leave the device.
- Adapters normalize capability metadata, request/response schemas, cancellation, timeouts and errors.
- Model output is untrusted content/proposal, never authority to grant permissions or execute privileged actions.
- Heavy workloads may use an authorized desktop or remote compute provider subject to data-transfer and spending policies.
- Record model/provider selection and relevant evidence in task traces.
- Ensembles, agent-to-agent orchestration, embeddings and reranking are optional capabilities requiring measured value, not mandatory architecture decorations.

## 8. Voice and multimodal interaction

Voice is an interaction pipeline, not a cognitive subsystem:
1. Capture through an explicitly permissioned platform adapter.
2. Speech recognition through a replaceable local or authorized remote ASR provider.
3. Transcript, source and confidence enter the normal experience pipeline.
4. Cognitive processing and action authorization remain unchanged.
5. Responses route to text and/or speech synthesis.
6. Playback, interruption, cancellation and privacy controls remain with the interface.

Images, audio and other modalities follow the same capture → provenance → representation → cognition pattern. Raw-media, transcription and external-processing retention each require separate policy and deletion rules. Do not assume continuous recording or always-on sensing.

## 9. Integration and tool ecosystem

OS, application, web, hardware and provider integrations use adapters registered with the capability/tool gateway. Each declares identity/version, operation schemas, data access, side effects, permissions, network destinations, budgets, cancellation, idempotency and verification.

The gateway enforces authorization immediately before execution and records outcome evidence. Android integration must validate its platform-specific realization under the foundational open-world interaction architecture; it does not define the general means model. Any selected scenario is a test fixture for those mechanisms, not a predefined capability catalogue or fixed first action. External communications, purchases, account changes, destructive operations and protected governance changes retain existing approval requirements.

## 10. Technology stack and decision status

| Concern | Candidate | Status / decision rule |
|---|---|---|
| Core/runtime/cognition | C++ (C++20 provisional) | Accepted language direction; standard/toolchain awaits Termux and CI validation |
| ML/training/evaluation | Python + PyTorch | Accepted role; exact versions and worker isolation to validate |
| Android UI/platform | Kotlin + Jetpack Compose | Recommended; confirm with thin technical spike |
| Desktop UI | Qt 6/QML | Leading candidate, not owner-approved; compare with web shell |
| Web UI | TypeScript + React | Deferred until browser client is justified |
| Relational persistence | SQLite | Accepted initial choice; execute DDL and benchmark target device |
| Artifact storage | Filesystem + immutable artifact registry | Accepted architectural direction |
| Local inference | llama.cpp adapter | Basic inference evidence exists; sustained performance/integration unverified |
| Worker transport | Versioned JSON over local process boundary | Initial direction; strict schema/size/time validation |
| Internal events | Typed versioned envelopes | Accepted direction; schemas and fixtures remain to be implemented |
| Local app/core boundary | C ABI/JNI or versioned local IPC | Unresolved; measure before selection |
| Device/network transport | HTTPS/TLS; WebSocket for live updates if needed | Proposed; threat model and protocol review required |
| RPC/serialization | JSON initially; evaluate Protocol Buffers/gRPC later | Avoid complexity without demonstrated need |
| Sync backend | Optional relay; PostgreSQL candidate if server-side durable coordination is required | Deferred; single-device core first |
| Android secure key storage | Android Keystore adapter | Required for native Android sensitive operations; not implemented |
| CI/release | GitHub Actions, reproducible builds, signed artifacts | Candidate baseline; supply-chain/signing design required |
| Observability | Structured logs, metrics and traces with sensitive-data redaction | Required; implementation choice pending |

Do not introduce Kubernetes, microservices, a mandatory cloud backend, a message broker, a vector database or Rust merely because they are common in large systems. Each must solve a demonstrated requirement and justify operational cost.

## 11. Capability map inspired by J.A.R.V.I.S., F.R.I.D.A.Y. and E.D.I.T.H.

These are sources of capability inspiration, not templates to copy blindly and not promises of fictional unrestricted access.

| Capability family | AURIONS interpretation | Release placement |
|---|---|---|
| Conversation and contextual recall | Durable experiences, memory retrieval, provenance-aware context | First usable local release |
| Reasoning and task planning | Goals, bounded plans, progress and explicit task state | First usable local release, bounded scope |
| Tool/device operation | Environment/capability discovery, capability knowledge, governed action gateway, verification and receipts | First usable local release: prove the general mechanisms with an owner-approved narrow scenario |
| Proactive assistance | Persistent scheduler, triggers, budgets and notifications | Later, after reliable task lifecycle and permissions |
| Voice interaction | ASR/TTS adapters and interruption-aware interface | Later; text-first core remains usable |
| Cross-device access | Android/desktop clients and device identity | Android native UI after core contracts; the first user-facing interface remains CLI |
| Cross-device continuity | Task handoff, selected memory sync, conflict/deletion handling | Later, after single-device persistence and security |
| External resource use | Search, APIs, remote models and compute under policy | Incremental, provider-specific permissions |
| Sensor/multimodal awareness | Permissioned image/audio/device observations | Later, each modality independently validated |
| Self-monitoring and adaptation | Self-model, prediction evaluation, learning and evolution proposals | Incremental; learning requires held-out evidence |
| Large-scale infrastructure access | Explicit adapters to authorized services/datasets/devices | Optional future integrations; no assumed satellite or unrestricted access |

## 12. Proposed release progression

### Engineering foundation (not a user release)
Reproducible repository/build, stable contracts, dependency inventory, test harness and validated target toolchain.

### First usable release
A usable CLI as the first user-facing interface; a cloud runtime and an offline-capable mobile runtime delivered concurrently, using the same versioned contracts and authoritative cognitive architecture; model-independent inference; persistent conversation/experience; provenance-aware memory and retrieval; bounded task reasoning/planning; environment/capability discovery; one narrowly scoped owner-approved permitted action through the gateway; verified outcome persistence; restart recovery; offline operation; inspectable permissions and resource limits. Offline mobile operation does not by itself select a native Android UI technology; the CLI remains the first user-facing interface and the mobile interface/topology must be validated.

It must demonstrate that a recorded outcome changes later retrieval/reasoning in a repeatable test. Conversation history alone does not qualify as learning.

### Personal device interface expansion
A native Android UI may follow the first CLI interface, subject to platform validation. Android platform integration needed for the concurrent offline-mobile runtime is not deferred: its environment/capability discovery, permission, lifecycle and local execution mechanisms are first-release architecture requirements. Additional UI features, notifications and voice adapters can be added when separately validated.

### Multi-device release
Authenticated device pairing/revocation, versioned communication contracts, selected-domain synchronization, offline queues, conflict resolution, deletion propagation, task handoff, end-to-end encryption and recovery tests.

### Expanded ecosystem
Desktop/web clients, authorized external providers, multimodal sensors, additional device agents, remote compute and advanced proactive workflows. Each capability is independently permissioned and acceptance-tested.

These are dependency/evidence gates, not fixed developmental stages.

## 13. Required architecture decisions and validation spikes

1. **Android runtime integration:** compare C++ shared library via JNI with isolated local process/IPC. Measure startup, memory, crash isolation, lifecycle and background constraints on target phone.
2. **Android UI:** build a disposable Kotlin/Compose spike against mocked versioned core contracts; evaluate navigation, accessibility, state updates and permission UX. Do not embed cognition in the spike.
3. **Desktop UI:** compare Qt/QML with a web-based shell using a representative workflow and the same core API.
4. **Core API contract:** define command/query/event schemas, operation state machine, authentication context, compatibility and error semantics before UI implementation.
5. **Device identity/pairing:** threat-model key creation, backup/recovery, revocation and compromised-device handling.
6. **Sync semantics:** classify synchronized domains and specify authority, consistency, conflict and deletion behaviour before replication.
7. **Voice feasibility:** benchmark local ASR/TTS on target device; compare privacy, latency, language coverage, memory and battery.
8. **Dependency/license audit:** pin versions only after framework decisions; verify licenses, maintenance and Android/ARM64 compatibility.
9. **Device performance:** measure sustained inference, runtime memory, storage I/O, thermals, battery and background execution. Existing basic inference is insufficient evidence.
10. **Security review:** threat-model IPC/network/UI/device-agent boundaries, key lifecycle, external disclosure and update/signing process.

## 14. Revised planning and implementation sequence

The former P-01…P-08 and I-00/I-01 sequence is a historical planning outline. The active dependency-driven work-package proposal is [Canonical Implementation Roadmap](../planning/CANONICAL-IMPLEMENTATION-ROADMAP.md). It reconciles the original WP table, the later technical-contract table, the CLI first-interface decision and concurrent cloud/offline-mobile first-release direction.

The roadmap is still IN PROGRESS and requires architecture/contract owner mapping and consistency verification. It is not implementation authorization.

## 15. Architecture acceptance criteria

The architecture is ready for consistency review only when:
- Every capability-discovery, representation, knowledge, planning, authorization, execution, verification and learning responsibility has an owning component and explicit interface.
- Newly discovered capabilities can be represented and used through versioned descriptors without adding fixed task-to-action mappings to the cognitive core.
- Android capability discovery respects public platform interfaces, current grants and OS restrictions; discovery never implies permission or authorization.
- UI clients cannot bypass core policy or mutate cognitive state directly.
- Device agents expose narrow, revocable capabilities with execution-time checks.
- Local-first operation and remote-service failure behaviour are defined.
- Multi-device identity, synchronization, conflict, deletion and task handoff are specified without database-file replication.
- Model/provider selection cannot confer authority.
- Voice and sensor data have explicit capture, retention and disclosure controls.
- First usable release is testable and does not claim learning from conversation history alone.
- Technology choices are labelled accepted, recommended, deferred or unresolved.
- Dependencies, security implications, failure modes, recovery behaviour and test evidence are identified.
- Product scope, architecture and canonical roadmap are consistent with the existing owner decision register.
- The no-hardcoding invariant is traceable through architecture, capability contracts, cognitive mechanisms and acceptance tests.



## 16. Review-resolution addendum — 2026-11-11

This addendum resolves the author-review findings recorded before independent review. It does not represent independent validation or owner approval.

### 16.1 Learning evidence standard (F-01)

A changed retrieval result or later response after recording an outcome is necessary evidence of feedback, but is not by itself sufficient evidence of learning or improvement.

The following distinctions are mandatory:
- **Memory update:** an experience, outcome or state is durably recorded with provenance.
- **Knowledge/belief revision:** a belief changes in response to evidence under an explicit revision procedure; contradictory evidence and uncertainty remain representable.
- **Strategy/mechanism learning:** a mechanism or strategy is changed and evaluated on held-out tasks against a frozen baseline.
- **Model training:** a candidate model is produced by a reproducible training/fine-tuning process and evaluated separately.
- **Architecture evolution:** a proposed structural change is isolated, tested, compared and governed through the approved change lifecycle.

A claim of demonstrated learning improvement requires, at minimum:
1. A versioned, reproducible task/evaluation dataset with provenance and a held-out split not used to tune the candidate.
2. A frozen baseline and a candidate that differ in an identified learning mechanism, strategy or model artifact.
3. Predeclared task metrics, scoring rules and regression constraints appropriate to the capability being evaluated.
4. Repeatable improvement on held-out tasks, not only training or previously observed examples.
5. Evaluation on related unseen variations to test generalization.
6. Regression checks showing that protected capabilities and previously passing tasks have not materially degraded.
7. Recorded experiment configuration, artifact hashes, results, uncertainty/limitations and a reproducible decision.
8. Explicit acceptance of the candidate through the applicable release/governance process before activation.

The first usable release must prove the end-to-end experience/outcome feedback path and persistent retrieval. It must not be described as having demonstrated general learning merely because a stored outcome influences one later interaction. The stronger held-out standard above governs any claim of learning improvement. Numerical thresholds are established from measured baselines and task risk; they are not invented in this architecture document.

### 16.2 Product-definition dependency (F-02)

The first-release description in Section 12 is an architectural envelope, not a complete product specification. The companion `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md` defines the proposed user workflows, capability scope, exclusions, acceptance scenarios and unresolved owner choices. That proposal must be reconciled and explicitly approved before implementation.

### 16.3 Meaning of architectural completeness (F-03)

“System architecture” here means coverage of the major system responsibilities, boundaries, deployment topology, architectural constraints and known decision points. It does **not** mean that all engineering contracts are complete. The following remain required downstream deliverables:
- Versioned API, command, query, event and worker contracts, including compatibility and error semantics.
- Concrete operation state machine, failure catalogue, recovery and compensation rules.
- Per-domain synchronization authority, consistency, conflict and deletion semantics.
- Threat model, key lifecycle, residual-risk register and security validation.
- Executed schema/migration validation and measured platform/dependency evidence.

These are explicit planning dependencies, not implicit approval to invent them during implementation.

### 16.4 Governance and authorization constraints (F-04)

The source specification's governance decisions remain authoritative. Architecture and implementation must preserve:
- The defined R0–R5 risk classification and default-deny treatment of ambiguous or unavailable policy decisions.
- Policy enforcement independent of model reasoning and immediately at the execution boundary.
- Authenticated owner sessions for approvals, with approval bound to the exact operation, target, parameters, scope, effects and relevant data/recipient context.
- Approval expiry, revocation, one-time use, replay prevention and invalidation after material operation changes.
- Durable, append-only approval and governance audit evidence.
- No model, worker, integration or device agent may grant itself authority, expand its own capability or bypass the central policy boundary.
- Sensitive external disclosure requires explicit authorization; enabling a provider does not authorize unrestricted memory access.
- Protected governance changes require the owner's explicit approval and a recovery path.

The detailed risk definitions, approval envelope and security tests must be carried into the security and API-contract deliverables without weakening the source requirements.

### 16.5 Proactive bounded autonomy as a system-wide constraint (F-05)

Proactive bounded autonomy is an owner-approved system requirement, not merely a future UI feature. The runtime must ultimately support durable objectives, task decomposition, permitted task execution without repeated prompting, progress monitoring, bounded retries/recovery, resource budgets, checkpoints, cancellation/resumption and notification when completed, blocked or requiring owner intervention.

This does not authorize unrestricted action. The existing approval requirements for financial transactions, external communications unless specifically authorized, permanent destructive operations, significant security changes and protected governance changes remain in force. Sensitive external disclosure remains approval-gated. Early releases may expose only a narrow subset of autonomous workflows, but their architecture must not preclude the approved model.

### 16.6 First-interface decision superseded (F-06)

The earlier unresolved-interface disposition is superseded by the owner's explicit decision: CLI is the first user-facing interface. Cloud operation and offline-capable mobile operation are concurrent first-release targets. This decision does not settle the mobile UI technology, the exact deployment topology, or the JNI/shared-library versus IPC boundary; those remain subject to platform validation. Offline mobile operation must remain useful without cloud connectivity.

### 16.7 Planning exit conditions

The architecture proposal can be sent for independent review after the author-side findings are incorporated. It is not thereby accepted. Implementation remains blocked until product scope, contracts, platform decisions, data/synchronization design, security/operations, evidence review and explicit owner approval are complete.


## Change log — 2026-11-11

- Added complete system layers and deployment topology.
- Expanded Android, desktop, web, CLI and device-agent strategy.
- Added distributed identity, communication, synchronization, conflict, deletion and task-handoff design.
- Mapped J.A.R.V.I.S./F.R.I.D.A.Y./E.D.I.T.H.-inspired capability families to implementable responsibilities.
- Added voice/multimodal, integration gateway, model routing and compute strategy.
- Distinguished accepted decisions from recommendations and unresolved platform choices.
- Defined release progression, validation spikes, revised planning sequence and architecture acceptance criteria.
- No application code, database migrations, device configuration or production dependencies were changed by this planning document.

- Added author-review resolutions for learning evidence, product scope dependency, architecture completeness, governance, proactive bounded autonomy and the then-unresolved first-interface choice, subsequently resolved by the owner as CLI with concurrent cloud and offline-mobile targets.


## 17. Implementation-ready contract supplement

The companion [Implementation-Ready Planning Contracts](../planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md) now specifies the previously enumerated design-level gaps: component ownership and dependency rules; versioned command/query/event envelopes; C++/Python worker protocol; authorization and exact-operation approval; operation state machine and crash recovery; SQLite transaction/outbox patterns; synchronization, conflict and deletion semantics; test catalogue; threat model and key lifecycle; dependency/device validation procedures; and work-package dependencies.

The supplement is a proposed engineering baseline, not proof of implementation or validation. Its Section 15 separates specified design from empirical evidence gates and owner-reserved decisions. The architecture remains unapproved for implementation until those gates are satisfied or explicitly staged/accepted by the owner, the independent review is complete, and the owner authorizes transition.

- Added a dedicated Android environment/capability architecture, subsequently subordinated it as one context-specific realization, and introduced the foundational open-world interaction architecture; dependent contracts and validation remain in progress.
