# AURIONS — System Architecture and Technology Baseline

**Status:** Proposed architecture baseline for owner review. This document establishes system-wide architectural coverage and boundaries; it is not a complete set of implementation-ready contracts or an implementation authorization. It expands the imported engineering specification, does not lock unmeasured framework choices, and does not claim any capability is implemented.

## 1. Architectural objective

AURIONS is intended to be one persistent, adaptive intelligence system accessible through multiple interfaces, able to observe and operate authorized resources, and capable of maintaining task continuity across supported devices. It is not a collection of independent chat clients, nor should its identity and memory depend on a single UI session or physical device.

Foundational principle: **Engineer the mechanisms; let behaviour be acquired through experience.**

The architecture must provide:
- One coherent system identity, with distinct authenticated device identities and scoped capabilities.
- A durable cognitive/runtime core independent of UI sessions.
- Multiple interchangeable interfaces and platform adapters.
- Local-first operation and policy-controlled remote resources.
- Explicit state ownership, capability boundaries, failure recovery and auditability.
- Multi-device contracts designed early, with distributed implementation deferred until the single-device core is reliable.
- A mechanism-based cognitive architecture; learned behaviour must not be replaced by hardcoded stimulus-response conclusions.

## 2. System layers and responsibility ownership

| Layer | Responsibilities | Primary owner/boundary |
|---|---|---|
| User experience | Text, voice, visual status, task views, notifications, settings, accessibility | Platform UI clients; no direct domain DB writes |
| Application/platform adapter | App lifecycle, OS APIs, permissions, local files, sensors, notifications, background constraints | Android/desktop/device adapters |
| Device agent | Device identity, capability discovery, local execution, resource reporting, operation receipts | Per-device runtime; least privilege |
| Core runtime | Orchestration, event dispatch, task scheduler, budgets, cancellation, recovery | C++ runtime |
| Cognitive mechanisms | Experience, representation, context, beliefs, prediction, attention/appraisal, reasoning, goals, planning, decision, self-model | C++ domain modules with explicit interfaces |
| Memory and knowledge | Experiences, retrieval, knowledge, evidence, beliefs, revision and retention | Domain-owned persistence interfaces |
| Learning and evolution | Dataset provenance, experiments, evaluation, candidate generation, controlled release and rollback | C++ authority + isolated Python workers |
| Model/inference services | Model routing, local/remote inference adapters, embeddings/reranking when justified | Model-independent inference interface |
| Tool/integration gateway | Capability registry, adapters, operation lifecycle, verification and side-effect handling | C++ action gateway + independent governance |
| Persistence/artifacts | SQLite stores, migrations, immutable artifacts, backups, encryption and deletion | Domain-owned stores/artifact registry |
| Connectivity/synchronization | Pairing, authenticated transport, replication, conflicts, offline queues and revocation | Sync subsystem/service when justified |
| Cross-cutting governance | Identity, authentication, authorization, privacy, audit, secrets, observability, updates and recovery | Independent enforcement interfaces |

These are logical ownership boundaries, not a mandate for one process/service per row. Retain a modular monolith at the centre. Split components only when lifecycle, security, resource isolation, platform integration or distribution gives a concrete reason.

## 3. Deployment topology

Initial deployment is a single-device local runtime, initially exercised in Termux. The C++ core remains authoritative. A CLI is an engineering/control interface, not the final product UI.

Future topology:
- **Android client:** native interface and Android-specific adapters.
- **Desktop client:** desktop interface and desktop-specific adapters; may host heavier local compute.
- **Additional device clients:** interfaces/agents with capability sets appropriate to their hardware.
- **Local runtime:** executes on a device and owns its local operations and state.
- **Optional remote services:** synchronization relay, external inference, search, APIs or compute; enabled only through explicit provider and data policies.

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
A small C++ CLI can provide immediate diagnostics, configuration, testing and controlled operation. It is not a substitute for the eventual user interface.

### UI contract
UI clients communicate through versioned application commands/queries and event subscriptions. Every operation carries a durable operation ID and exposes explicit lifecycle status. The UI must display permissions, external data disclosures, progress, blocked states and recovery needs. No UI can bypass the action gateway or write cognitive state directly.

## 5. Device agents and capability model

Each connected device exposes declared capabilities, not unrestricted OS access. A capability descriptor includes stable ID/version, device identity, operation schema, required permissions, data categories, side effects, resource requirements, availability, cancellation, idempotency and verification method.

Capability categories may include read-only diagnostics, user-selected files, notifications, voice I/O, camera/microphone/location, supported app integrations, local compute and narrowly scoped automation. Sensors require platform permission and purpose checks. A central plan does not imply that a device has granted a capability. Capabilities may be revoked or unavailable offline.

The device agent checks local platform permissions and policy at execution time. Model reasoning cannot grant permissions.

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

The gateway enforces authorization immediately before execution and records outcome evidence. Initial integrations should prove the lifecycle using local, low-risk capabilities: read-only diagnostics, user-selected files, local retrieval and one narrowly scoped reversible action. External communications, purchases, account changes, destructive operations and protected governance changes retain existing approval requirements.

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
| Tool/device operation | Capability registry, action gateway, verification and receipts | First usable local release: one narrow permitted action |
| Proactive assistance | Persistent scheduler, triggers, budgets and notifications | Later, after reliable task lifecycle and permissions |
| Voice interaction | ASR/TTS adapters and interruption-aware interface | Later; text-first core remains usable |
| Cross-device access | Android/desktop clients and device identity | Android client after core contracts; desktop thereafter |
| Cross-device continuity | Task handoff, selected memory sync, conflict/deletion handling | Later, after single-device persistence and security |
| External resource use | Search, APIs, remote models and compute under policy | Incremental, provider-specific permissions |
| Sensor/multimodal awareness | Permissioned image/audio/device observations | Later, each modality independently validated |
| Self-monitoring and adaptation | Self-model, prediction evaluation, learning and evolution proposals | Incremental; learning requires held-out evidence |
| Large-scale infrastructure access | Explicit adapters to authorized services/datasets/devices | Optional future integrations; no assumed satellite or unrestricted access |

## 12. Proposed release progression

### Engineering foundation (not a user release)
Reproducible repository/build, stable contracts, dependency inventory, test harness and validated target toolchain.

### First usable local release
One local persistent runtime; a usable text interface selected through the product-definition and platform-validation gates (CLI remains an engineering interface candidate, not an approved product-interface decision); model-independent inference; persistent conversation/experience; provenance-aware memory and retrieval; bounded task reasoning/planning; one narrowly scoped permitted action through the gateway; verified outcome persistence; restart recovery; offline operation; inspectable permissions and resource limits.

It must demonstrate that a recorded outcome changes later retrieval/reasoning in a repeatable test. Conversation history alone does not qualify as learning.

### Personal device release
Native Android UI, platform authentication/Keystore integration, notifications and voice adapters, lifecycle-safe local runtime integration, explicit capability permissions and operational diagnostics.

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

- **P-01 Product definition:** capability catalogue, user workflows, first usable release scope, non-goals and measurable acceptance criteria.
- **P-02 System architecture:** component boundaries, ownership, dependency direction, deployment topology and failure model.
- **P-03 Interface/API contracts:** commands, queries, events, operation lifecycle, UI/core and worker boundaries.
- **P-04 Platform strategy:** Android integration spike, desktop UI comparison, CLI engineering interface.
- **P-05 Data and synchronization design:** domain ownership, migrations, artifacts, device identity, replication and deletion semantics.
- **P-06 Security and operations:** threat model, authenticator, keys, permissions, updates, observability and recovery.
- **P-07 Evidence review:** dependency/license inventory, target-device measurements, schema execution and fault/security tests as applicable.
- **P-08 Consistency review and owner approval:** resolve contradictions, update work packages and obtain explicit approval.
- **I-00/I-01 only after approval:** foundation/build and shared contracts, revised to match accepted architecture.
- Subsequent implementation proceeds through persistence, runtime, inference, experience, memory, knowledge, cognition, goals, action, learning and platform/device capabilities in dependency order, each gated by executable tests.

The existing draft WP-00 PR is not approved for merge merely because it exists. Its scaffold must be reconciled with the approved product definition, target deployment model and revised roadmap first.

## 15. Architecture acceptance criteria

The architecture is ready for consistency review only when:
- Every capability has an owning component and explicit interface.
- UI clients cannot bypass core policy or mutate cognitive state directly.
- Device agents expose narrow, revocable capabilities with execution-time checks.
- Local-first operation and remote-service failure behaviour are defined.
- Multi-device identity, synchronization, conflict, deletion and task handoff are specified without database-file replication.
- Model/provider selection cannot confer authority.
- Voice and sensor data have explicit capture, retention and disclosure controls.
- First usable release is testable and does not claim learning from conversation history alone.
- Technology choices are labelled accepted, recommended, deferred or unresolved.
- Dependencies, security implications, failure modes, recovery behaviour and test evidence are identified.
- Product scope, architecture and roadmap are consistent with the existing owner decision register.



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

### 16.6 First interface remains unresolved (F-06)

CLI is an engineering/debugging interface candidate, not an owner-approved first-release product interface. The first usable release interface is deliberately unresolved pending the product-definition and platform-validation work. The product definition records this explicitly; the Android runtime/UI integration and interface choice must be decided using measured feasibility and owner approval, not silently fixed by the scaffold.

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

- Added author-review resolutions for learning evidence, product scope dependency, architecture completeness, governance, proactive bounded autonomy and unresolved first-interface choice.


## 17. Implementation-ready contract supplement

The companion [Implementation-Ready Planning Contracts](../planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md) now specifies the previously enumerated design-level gaps: component ownership and dependency rules; versioned command/query/event envelopes; C++/Python worker protocol; authorization and exact-operation approval; operation state machine and crash recovery; SQLite transaction/outbox patterns; synchronization, conflict and deletion semantics; test catalogue; threat model and key lifecycle; dependency/device validation procedures; and work-package dependencies.

The supplement is a proposed engineering baseline, not proof of implementation or validation. Its Section 15 separates specified design from empirical evidence gates and owner-reserved decisions. The architecture remains unapproved for implementation until those gates are satisfied or explicitly staged/accepted by the owner, the independent review is complete, and the owner authorizes transition.
