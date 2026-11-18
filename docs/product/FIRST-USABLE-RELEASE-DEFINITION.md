# AURIONS — First Usable Release Product Definition

**Status:** ACCEPTED BY OWNER on 2026-11-16. This document translates the existing owner-approved mission and first-milestone requirements into a bounded first-release proposal under the foundational [Open-World Interaction and Means Architecture](../architecture/OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md). It does not authorize implementation or silently settle unresolved product choices.

## 1. Product purpose

AURIONS is a trainable AI system with an evolving cognitive architecture, not a personal-assistant product, chatbot or thin LLM wrapper. Conversation is one possible interface, not the system's identity. The first usable release is a persistent, adaptive system available through concurrent cloud operation and offline-capable mobile operation. Both deployment contexts use the same authoritative cognitive architecture and versioned contracts. The mobile runtime must complete its required local workflows without cloud connectivity. AURIONS must acquire and use experience, retain and retrieve evidence, understand bounded objectives in relevant situations, reason about evidence-supported possible means, interact only through applicable authority boundaries, observe consequences, and improve through both experience-dependent adaptation and controlled model training. Means are not limited to device capabilities, registered tools or platform adapters.

It is an early trainable system, not finished general intelligence, an unrestricted autonomous agent, a multi-device ecosystem or proof of general intelligence. Learning and training claims must be bounded by reproducible evidence.

The governing principle remains:

**Engineer the mechanisms; let behaviour be acquired through experience.**

The release must demonstrate interacting mechanisms and durable state changes. It must not simulate learning through hardcoded stimulus-response rules or describe ordinary chat-history retrieval as learning.

## 2. Target user and primary job

**Target user:** The owner operating AURIONS through the first CLI interface, with concurrent cloud and offline-capable mobile runtime targets. The initial mobile engineering baseline is the supported Termux environment on the target Android device; a native Android UI is not yet selected.

**Primary job:** Acquire, represent and retain experience; build and revise evidence-backed knowledge; predict and evaluate outcomes; improve reusable processing and model parameters through controlled learning; and apply those improvements to later objectives. The CLI is the first interface for inspecting and interacting with this evolving system.

The system must remain useful when remote services are unavailable. Remote model/provider use is optional and governed by data disclosure and spending policy.

## 3. First-release user workflows

### Workflow 0 — Operate through the cloud runtime

1. The owner authenticates to the cloud deployment through the supported CLI/application contract.
2. The cloud runtime initializes its own authorized runtime context and uses the same cognitive-core contracts and semantics as the offline-mobile runtime.
3. AURIONS performs cloud-hosted work within the owner's configured permissions, data-disclosure policy and resource budgets.
4. Remote inference, external providers and cloud-hosted execution remain separately governed; cloud availability does not create authority over a mobile device.
5. The runtime records durable experiences, task state, operation receipts and outcomes within its declared state-ownership boundary.

**Expected result:** Cloud operation is a real first-release deployment target, not merely an optional inference provider. It cannot bypass local Android authorization or silently assume access to mobile-local state.


### Workflow A — Start and converse in offline mobile mode

1. The owner starts the mobile-local runtime through the selected supported interface.
2. AURIONS initializes the mobile runtime's local stores, cognitive core and model-independent inference adapter.
3. The owner submits a message.
4. AURIONS produces a response using the local model path.
5. The interaction is durably recorded as an experience with timestamps, source/provenance and relevant references.
6. The owner can restart the runtime and continue without losing committed state.

**Expected result:** Offline-mobile conversation works without requiring a cloud service, and committed experience survives process restart.

### Workflow B — Recall a relevant prior experience

1. The owner asks a question that depends on a prior interaction or recorded experience.
2. AURIONS retrieves relevant records using the available retrieval mechanism.
3. Retrieved material retains provenance and is distinguishable from inference or unverified claims.
4. AURIONS uses relevant retrieved context in its response.
5. The owner can inspect the supporting source/reference.

**Expected result:** Recall is based on persisted records, not merely the current process context. Irrelevant or unsupported memories must not be presented as certain facts.

### Workflow C — Work through a bounded objective

1. The owner provides a bounded objective.
2. AURIONS represents the objective separately from its plan.
3. It produces a plan with steps, dependencies, status and relevant resource/time limits.
4. It tracks progress and records changes.
5. It can resume the task after interruption using durable task state.
6. It reports completion, blockage or the need for owner intervention.

**Expected result:** The system manages a durable task rather than returning only a one-off answer. Planning and task state remain inspectable.

### Workflow D — Execute one permitted local action

1. AURIONS proposes an action through the action interface.
2. The action declares its target, parameters, expected effects, required capability and risk.
3. The policy boundary evaluates the exact operation.
4. The system executes only if the applicable capability and authorization are valid.
5. It records an operation ID, execution state and outcome evidence.
6. It verifies the result where the action permits verification.
7. An interrupted or uncertain operation is reconciled before retrying.

**Expected result:** At least one owner-selected, explicitly permitted, narrowly scoped and reversible local action completes through the real authorization and action lifecycle. The particular action is an owner decision and must not be guessed by implementers.

### Workflow E — Use an outcome in a later interaction

1. AURIONS records the action's observed consequence and evaluates it against the expected outcome.
2. The record retains provenance and links to the originating objective, plan and operation.
3. In a later related interaction, AURIONS retrieves and uses that outcome.
4. It distinguishes the observed fact from any inferred lesson or revised belief.
5. Contradictory evidence can be retained and can trigger belief revision rather than being silently discarded.

**Expected result:** The complete feedback path is demonstrated: experience → representation/context → persistence → retrieval → later reasoning. This proves persistent feedback and use of experience, not by itself general learning improvement.

### Workflow G — Train and evaluate an AURIONS-owned model candidate

**Model-ownership invariant:** The primary model is owned and trained under AURIONS control; AURIONS is not a thin wrapper around a hosted commercial model. The initial model baseline uses an AURIONS-controlled architecture/configuration with randomly initialized parameters. Pretrained third-party weights or a hosted third-party LLM are not silently substituted as the system's brain. The full owner-selected model direction is consolidated in [Model Architecture and Training Owner Decisions MD-01…MD-16](../planning/MODEL-ARCHITECTURE-AND-TRAINING-OWNER-DECISIONS.md) and [Initial Engineering Specification §27](../planning/INITIAL-ENGINEERING-SPECIFICATION.md). Architecture size, tokenizer algorithm, dataset composition, optimizer/training schedule and compute budgets remain engineering choices subject to feasibility evidence. MD-16 source-rights, dataset-manifest and revocation requirements are specified in [the dataset authorization contract](../planning/DATASET-SOURCE-RIGHTS-AND-TRAINING-AUTHORIZATION-CONTRACT.md), but the machine schemas, fixtures, persistence and enforcement remain a blocker before nontrivial corpus ingestion/training. Any proposal to import pretrained weights or make external model inference a core dependency requires a separate explicit owner decision.

Online research is source acquisition, not automatic model training. Retrieved material retains source, time, provenance, trust, sensitivity and licensing/data-use metadata. It may enter a training dataset only after curation and data-use approval; retrieval alone never changes model weights.

1. AURIONS selects an explicitly approved training dataset with provenance, version and declared data-use scope.
2. The training pipeline creates non-overlapping training, validation and held-out evaluation partitions and checks for leakage.
3. A bounded worker trains the AURIONS-owned model from its declared initialization or a prior AURIONS-owned checkpoint. The initial baseline is randomly initialized, with architecture, tokenizer, configuration and initialization provenance versioned.
4. The worker returns a versioned candidate artifact, metrics, configuration and provenance; it cannot modify the active model or authoritative cognitive state.
5. The evaluation path compares the candidate with the frozen baseline on held-out tasks and relevant regression controls.
6. Candidate activation requires the applicable approval and compatibility checks; failed or regressive candidates remain quarantined and can be discarded.
7. An activated candidate has a recorded rollback target and a tested rollback procedure.

**Expected result:** A real parameter update is produced and evaluated with reproducible evidence. The system distinguishes model-weight training from memory, belief and strategy adaptation. Training may use local resources where feasible or explicitly approved capable hardware; local inference and local operation remain independent of remote training.

### Workflow F — Respect permissions and resource limits

1. The owner can inspect the capabilities and permissions available to AURIONS.
2. Harmless authorized reads and diagnostics do not trigger unnecessary repeated prompts.
3. Unauthorized or ambiguous actions are denied.
4. Sensitive external disclosure is blocked unless explicitly authorized.
5. The runtime enforces configured CPU, memory, storage, network, deadline and retry budgets where supported.
6. The system records denials, failures and relevant resource-limit events without leaking secrets.

**Expected result:** The model cannot authorize itself, and failure or policy denial does not corrupt committed state.

## 4. First-release capability scope

| Capability | First-release scope | Boundary |
|---|---|---|
| Local conversation | Required | AURIONS-owned model through a replaceable local inference runtime; no hosted third-party model is a required dependency |
| Experience persistence | Required | Durable committed records across restart |
| Memory retrieval | Required | Provenance-aware retrieval; vector DB not required |
| Context and representation | Required at a testable baseline | Must not collapse into untraceable prompt assembly |
| Knowledge/belief handling | Minimum explicit representation and evidence links needed for the first feedback workflow | No claim of mature general knowledge |
| Bounded reasoning and planning | Required | Objective distinct from versioned plan and task state; route is derived from task-relevant evidence and constraints, not a fixed task-to-action mapping |
| Outcome observation/evaluation | Required | Evidence linked to the proposed interaction, expected effects and independently observed outcome; provider receipts alone are insufficient |
| Use of prior outcome | Required | Later related interaction must use retrieved outcome |
| Recovery | Required for committed persistence and operation reconciliation | Process survival is not guaranteed by Android/Termux |
| Governance | Required baseline | Execution-boundary enforcement, audit and owner authority |
| Resource limits | Required baseline | Measured values and platform limitations documented |
| Proactive autonomy | Architectural requirement; narrow first-release task execution only | No unrestricted background activity |
| AURIONS-owned model training | Required at a bounded, reproducible baseline | Initial model uses randomly initialized parameters and AURIONS-controlled architecture/configuration; at least one real parameter-update experiment, versioned candidate artifact, frozen baseline and leakage-controlled held-out evaluation. Training may use local resources or explicitly approved cloud/remote compute with approved data access; local inference and offline operation must not depend on remote training |
| General learning improvement | No broad/general improvement claim from one experiment | Report measured results only for evaluated tasks and held-out distributions; separate experience-dependent adaptation from model-weight changes |
| Offline-capable mobile runtime | Required concurrently with cloud operation; local cognition, persistence, situation understanding and governed interactions available in the validated local context must work without cloud availability | The CLI remains the first user-facing interface. A native Android UI is not selected; mobile UI technology and core boundary remain engineering decisions subject to platform validation |
| Cloud runtime | Required concurrently with offline-capable mobile operation; uses the same cognitive architecture/contracts and independently enforces owner, provider, disclosure and operation policy | Cloud availability does not authorize mobile-local operations. D-02 selects bounded synchronization of explicitly approved durable domains; no unrestricted replication or authority transfer |
| Voice, camera and continuous sensing | Excluded from first release | Separate permissions, privacy and feasibility gates |
| Cross-runtime state synchronization | Bounded selective domain synchronization is included in the first-release architecture under owner decision D-02 (Option B); general multi-device synchronization/handoff remains excluded | Only explicitly allowlisted durable domain changes may synchronize through versioned changes/outboxes and reconciliation; local execution state, permissions, credentials, approvals and governance authority never synchronize |
| Desktop/web user-facing clients | Excluded from first release | This is a client/deployment scope decision only; it does not exclude desktop, web, iOS, human-mediated or other contexts from the general world model or from later task-relevant interaction reasoning |
| Broad external integrations | Excluded from first release | Add one by one under capability and disclosure policy |

## 5. Explicit non-goals

The first usable release does not promise:

- Human-level or general intelligence.
- A finished, generally intelligent or unbounded self-improving model; bounded training and evaluation are required, but automatic production activation is not.
- Autonomous modification of its own production code or protected governance.
- Unrestricted shell, device, account, network or filesystem access.
- Always-on microphone, camera, location or sensor monitoring.
- A mobile runtime that depends on cloud availability.
- General-purpose multi-device live synchronization or seamless handoff beyond the bounded cloud/mobile selective-sync subset approved under D-02.
- A complete Android application experience.
- Arbitrary execution of external communications, purchases, financial transactions or destructive operations.
- A large-scale multi-agent/LLM ensemble.
- A vector database, message broker, microservice fleet or orchestration platform without demonstrated need.

## 6. First-release acceptance protocol

The release is accepted only when the following scenarios pass in both required deployment contexts (cloud runtime and offline-capable mobile runtime), with reproducible evidence. Each result must identify its runtime, build, configuration and state-ownership boundary.

| ID | Acceptance condition | Evidence required |
|---|---|---|
| PR-01 | Clean local build and reproducible startup | Build logs, toolchain/dependency versions and repeatable startup |
| PR-02 | Local conversation works through inference abstraction | Recorded request/response test and provider configuration |
| PR-03 | Committed experiences survive process restart | Before/after restart persistence test |
| PR-04 | Relevant prior experience is retrieved with provenance | Fixture, retrieved record IDs, source references and relevance assertions |
| PR-05 | Unsupported or contradictory evidence is not silently treated as certain | Belief/evidence fixtures and revision assertions |
| PR-06 | Bounded objective and plan persist independently | Goal/plan records, revisions, dependencies and restart test |
| PR-07 | One owner-approved local action executes through the gateway | Exact operation envelope, authorization decision, execution receipt and verification |
| PR-08 | Unauthorized and ambiguous actions are denied | Negative tests covering missing, expired, revoked and mismatched authorization |
| PR-09 | Interrupted operations reconcile without unsafe duplicate execution | Fault injection, state transitions, idempotency and recovery evidence |
| PR-10 | Action outcome is durably recorded and evaluated | Linked operation, expected outcome, observed evidence and evaluation |
| PR-11 | Later related interaction retrieves and uses that outcome | Repeatable test with retrieved references and observable reasoning-context effect |
| PR-12 | Sensitive data is not sent to an external provider without authorization | Egress/policy tests and disclosure audit |
| PR-13 | Resource limits and failure paths are observable | Measurements, bounded-failure tests and redacted diagnostics |
| PR-14 | Runtime can recover without corrupting committed state | Restart/crash tests and database integrity checks |
| PR-15 | Cloud runtime operates as a real deployment target using the shared cognitive-core contracts | Authenticated cloud startup/conversation/task trace, durable cloud-side state and policy audit |
| PR-16 | Cloud and mobile builds implement compatible versioned cognitive/application contracts without becoming separate intelligence designs | Shared contract fixtures and compatibility tests against both runtime builds |
| PR-17 | Offline-mobile workflows complete with network disabled; cloud unavailability does not block local cognition, persistence, discovery or authorized local execution | Network-isolation test, local persistence/restart test and authorized/denied local operation traces |
| PR-18 | Cloud runtime cannot authorize or execute a mobile-local operation, and neither runtime silently assumes the other's local state | Negative cross-boundary authorization tests and state-ownership assertions |
| PR-19 | A bounded training run produces a new, versioned candidate for the AURIONS-owned model, starting from its declared random initialization or a prior AURIONS-owned checkpoint; imported pretrained third-party weights are not the default baseline | Model/architecture and tokenizer versions, initialization provenance, dataset manifest, split/leakage checks, training configuration, baseline/candidate hashes and checkpoint provenance |
| PR-20 | Candidate evaluation uses a frozen baseline and leakage-controlled held-out data; activation is separately authorized and rollback is verified | Held-out metrics, task-specific regression results, candidate quarantine, approval record, activation/rollback trace and proof that training loss alone cannot activate a model |

Passing PR-11 demonstrates experience-dependent feedback, not model training. PR-19 and PR-20 separately verify a real model-parameter update and its held-out evaluation/activation boundary. Neither one experiment nor a lower training loss establishes general learning improvement.

Numerical performance thresholds for latency, memory, storage and battery are intentionally deferred until baselines are measured on the target device. Acceptance must still report actual measurements and resource limitations; absence of a threshold does not permit omission of measurement.

## 7. Operational and safety constraints

- The offline-mobile runtime must remain locally useful and independent of cloud availability. The cloud runtime is a concurrent first-release deployment target and supports approved online research/data acquisition and capable training compute where needed. Remote inference is not a required dependency or the primary model; any external inference provider remains optional, task-scoped and subject to explicit owner approval and data-disclosure policy.
- The owner remains the authority for permissions and protected changes.
- The R0–R5 risk model, exact-operation approval binding, authenticated owner session, expiry, revocation, replay protection and durable audit remain mandatory.
- The model, Python workers and integrations cannot grant permissions or directly mutate authoritative live cognitive state.
- Termux is not a strong security sandbox. Do not represent process separation or filesystem conventions as equivalent to OS-enforced isolation.
- Android/Termux may terminate or defer background work. Persisted checkpoints support recovery but do not guarantee continuous execution or notification delivery.
- Uncertain external side effects must be reconciled before retry.
- Deletion applies to active records, derived indexes/references, synchronized copies and backup lifecycle according to the owner's existing 30-day historical-backup expiry decision.
- Secret material must not appear in logs, prompts, worker output or ordinary artifacts.

## 8. Decisions intentionally left open

These items cannot be silently decided by the architecture author or implementation team:

1. **First interface: OWNER DECISION — CLI.** The CLI is the first user-facing interface, not merely an engineering/debugging tool.
2. **Deployment: OWNER DECISION — cloud and offline mobile concurrently.** The first-release plan must deliver both as first-class targets; offline mobile must not depend on cloud availability. Both use shared versioned contracts and the same authoritative cognitive-core implementation/semantics. **D-02 OWNER DECISION — OPTION B SELECTED (2026-11-16):** both contexts are full runtimes with bounded selective synchronization of explicitly approved durable domain changes. This supersedes the earlier no-sync proposal. The exact field-level allowlists, local-only classes, conflict/deletion/recovery semantics and executable SY acceptance cases remain builder-owned design gates before implementation. A cloud plan cannot authorize a mobile-local action. CLI deployment context(s) and exact process topology remain engineering details to validate. See [Cloud and Offline-Mobile Runtime Topology Decision](../architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md).
3. **Foundational interaction model and Android realization:** The examples discussed by the owner (such as opening apps, adjusting volume and handling files) are illustrative scenarios only. They do not define or limit the general model of possible means, nor preselect the first permitted action. The foundational architecture must define objective-led understanding of relevant situations, entities, actors, resources, evidence and context-dependent means. Android observation, discovery and OS permission integration are one realization beneath that model. The capability model must not be a hardcoded catalogue of owner examples. The first end-to-end Android action-gateway acceptance scenario remains an owner decision.
4. **Target-device performance thresholds:** Establish after repeatable baseline measurements.
5. **AURIONS-owned model implementation details:** Preserve the owner-selected direction to build/train AURIONS' own model from randomly initialized parameters. Model architecture/size, tokenizer, training objective, local inference engine and resource profile remain engineering choices requiring measured feasibility evidence. No pretrained third-party model is selected as the primary model.
6. **Any additional first-release capability:** Must be justified against the primary workflow and must not displace mandatory acceptance criteria.
7. **Cloud/mobile state continuity:** Resolved at topology level by D-02 (Option B). The first release includes bounded selective synchronization for explicitly allowlisted durable domains. The initial candidate domains are experiences/provenance, representations, memory, evidence-backed knowledge/belief revisions, objectives/derived goals and approved immutable model-version references. Raw/sensitive observations, transient context, plans/task checkpoints, device capabilities, permissions, credentials, approval secrets, operation dispatch state and governance authority remain local by default. Field-level classification, per-aggregate conflict/deletion/recovery rules and executable SY tests remain open before implementation.

The architecture/validation work must establish the general objective-led world/situation and means-reasoning contracts independently of any platform, then validate each selected context-specific realization separately. Android OS permission boundaries and empirical feasibility on the actual target device remain a distinct platform gate. Numerical performance thresholds remain measurement-dependent.

## 9. Dependencies and implementation gate

This product definition depends on the existing owner-approved engineering specification and architecture constraints. It must be reconciled with the API contracts, persistence/recovery design, platform strategy, security/operations design and evidence review.

No implementation work package is authorized by this proposal. Before implementation:
- The owner accepted this product definition on 2026-11-16 (D-01) and selected Option B for dual-runtime selective domain synchronization (D-02). The first permitted local action remains unresolved and staged (D-03), pending target-device/runtime validation; no action is selected or authorized. D-04 command/query subset remains pending owner acceptance.
- The architecture and contracts must be reconciled with it.
- Required security, persistence, recovery and learning-evaluation criteria must be testable.
- The owner must explicitly approve the planning exit.

## 10. Traceability to existing owner decisions

This proposal operationalizes, without replacing, the existing decisions concerning:
- Persistent local first milestone and experience/outcome retention.
- C++ authoritative core and model-independent inference.
- SQLite initial persistence with separate memory, events/recovery and governance stores.
- Typed contracts and separate Python workers.
- Provenance-aware memory, provisional beliefs and evidence-based revision.
- Objective-led open-world understanding, context-dependent possible means, and separation of proposal, authority, execution and verified outcome.
- Policy enforcement at the execution boundary and exact owner approval.
- Proactive bounded autonomy with explicit limits.
- Held-out learning evaluation and regression testing.
- Bounded cloud/mobile selective synchronization in WP-15 under D-02; broad multi-device synchronization and seamless handoff remain deferred to later expansion.

Where this proposal is more specific than the source, it is a proposal for owner review, not an already-approved decision.
