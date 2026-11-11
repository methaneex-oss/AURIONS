# AURIONS — First Usable Release Product Definition

**Status:** Proposed product definition for owner review. This document translates the existing owner-approved mission and first-milestone requirements into a bounded first-release proposal. It does not authorize implementation or silently settle unresolved product choices.

## 1. Product purpose

The first usable release is a persistent, adaptive personal intelligence system available through concurrent cloud operation and offline-capable mobile operation. Both deployment contexts use the same authoritative cognitive architecture and versioned contracts. The mobile runtime must complete its required local workflows without cloud connectivity. The system can converse, retain and retrieve relevant experiences, reason through bounded objectives, use discovered capabilities through owner-authorized boundaries, observe consequences and use evidence in later related interactions.

It is a first working system, not a finished general intelligence, unrestricted autonomous agent, multi-device ecosystem or proof of general learning.

The governing principle remains:

**Engineer the mechanisms; let behaviour be acquired through experience.**

The release must demonstrate interacting mechanisms and durable state changes. It must not simulate learning through hardcoded stimulus-response rules or describe ordinary chat-history retrieval as learning.

## 2. Target user and primary job

**Target user:** The owner operating AURIONS through the first CLI interface, with concurrent cloud and offline-capable mobile runtime targets. The initial mobile engineering baseline is the supported Termux environment on the target Android device; a native Android UI is not yet selected.

**Primary job:** Help the owner carry a bounded task across interactions and process restarts: understand the objective, retain relevant context, retrieve evidence, form and track a plan, perform an authorized low-risk action, record what happened and use that experience later.

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
| Local conversation | Required | Local model through replaceable inference interface |
| Experience persistence | Required | Durable committed records across restart |
| Memory retrieval | Required | Provenance-aware retrieval; vector DB not required |
| Context and representation | Required at a testable baseline | Must not collapse into untraceable prompt assembly |
| Knowledge/belief handling | Minimum explicit representation and evidence links needed for the first feedback workflow | No claim of mature general knowledge |
| Bounded reasoning and planning | Required | Objective distinct from versioned plan and task state |
| Outcome observation/evaluation | Required | Evidence linked to operation and expectation |
| Use of prior outcome | Required | Later related interaction must use retrieved outcome |
| Recovery | Required for committed persistence and operation reconciliation | Process survival is not guaranteed by Android/Termux |
| Governance | Required baseline | Execution-boundary enforcement, audit and owner authority |
| Resource limits | Required baseline | Measured values and platform limitations documented |
| Proactive autonomy | Architectural requirement; narrow first-release task execution only | No unrestricted background activity |
| Model training/fine-tuning | Not required to claim first release works | Training infrastructure and evaluation are separate work |
| General learning improvement | Not claimed by the feedback workflow | Requires held-out evaluation described in architecture |
| Offline-capable mobile runtime | Required concurrently with cloud operation; local environment/capability discovery, cognition, persistence and governed local operation must work without cloud availability | The CLI remains the first user-facing interface. A native Android UI is not selected; mobile UI technology and core boundary remain engineering decisions subject to platform validation |
| Cloud runtime | Required concurrently with offline-capable mobile operation; uses the same cognitive architecture/contracts and independently enforces owner, provider, disclosure and operation policy | Cloud availability does not authorize mobile-local operations or imply automatic cross-runtime state synchronization |
| Voice, camera and continuous sensing | Excluded from first release | Separate permissions, privacy and feasibility gates |
| Automatic cross-runtime state synchronization | Not assumed in first release | Cloud and mobile runtime state ownership/continuity must be explicitly specified; any synchronization is a separate governed capability and must not be inferred from shared contracts |
| Desktop/web clients | Excluded from first release | Later clients must use stable core contracts |
| Broad external integrations | Excluded from first release | Add one by one under capability and disclosure policy |

## 5. Explicit non-goals

The first usable release does not promise:

- Human-level or general intelligence.
- A fully trained or self-improving model.
- Autonomous modification of its own production code or protected governance.
- Unrestricted shell, device, account, network or filesystem access.
- Always-on microphone, camera, location or sensor monitoring.
- A mobile runtime that depends on cloud availability.
- Multi-device live synchronization or seamless handoff.
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

Passing PR-11 demonstrates experience-dependent feedback, not general learning improvement. Any stronger learning claim requires the held-out evaluation standard in the architecture document.

Numerical performance thresholds for latency, memory, storage and battery are intentionally deferred until baselines are measured on the target device. Acceptance must still report actual measurements and resource limitations; absence of a threshold does not permit omission of measurement.

## 7. Operational and safety constraints

- The offline-mobile runtime must remain locally useful and independent of cloud availability. The cloud runtime is a concurrent first-release deployment target, not merely an optional inference provider. Remote inference or external services receive only the minimum authorized context.
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
2. **Deployment: OWNER DECISION — cloud and offline mobile concurrently.** The first-release plan must deliver cloud operation and an offline-capable mobile runtime as concurrent first-class targets. Offline mobile operation must not depend on cloud availability. Both deployment contexts must use shared versioned application contracts and the same authoritative cognitive-core implementation/semantics; they must not become separate intelligence designs. **Builder topology proposal:** each runtime is authoritative for its own local state in the first release; automatic cross-runtime state synchronization and seamless handoff are excluded unless separately approved. A cloud plan cannot authorize a mobile-local action. The CLI deployment context(s) and exact process topology remain engineering details to validate.
3. **Android capability architecture:** The examples discussed by the owner (such as opening apps, adjusting volume and handling files) are illustrative scenarios only. They do not define, limit or preselect AURIONS' Android capabilities or its first permitted action. The architecture must investigate how AURIONS can perceive and represent its Android environment, discover available capabilities and their interfaces/constraints, learn their use through experience, reason and plan over them, and execute only through independent governance and platform permission boundaries. The capability model must not be a hardcoded catalogue of owner examples. The first end-to-end Android action-gateway acceptance scenario remains an owner decision.
4. **Target-device performance thresholds:** Establish after repeatable baseline measurements.
5. **Specific inference model/runtime configuration:** Preserve model independence and validate actual device feasibility; existing basic inference is not sufficient performance evidence.
6. **Any additional first-release capability:** Must be justified against the primary workflow and must not displace mandatory acceptance criteria.

The architecture/platform validation work must establish a general Android environment and capability-discovery strategy, including OS permission boundaries and empirical feasibility on the actual target device. Numerical performance thresholds remain measurement-dependent.

## 9. Dependencies and implementation gate

This product definition depends on the existing owner-approved engineering specification and architecture constraints. It must be reconciled with the API contracts, persistence/recovery design, platform strategy, security/operations design and evidence review.

No implementation work package is authorized by this proposal. Before implementation:
- The owner must approve this product definition. The first interface and concurrent cloud/offline-mobile direction are owner decisions; the first permitted local action remains unresolved. The independent runtime state boundary is a builder proposal and must be explicitly surfaced for owner acceptance if cross-context continuity is expected.
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
- Policy enforcement at the execution boundary and exact owner approval.
- Proactive bounded autonomy with explicit limits.
- Held-out learning evaluation and regression testing.
- Multi-device contracts designed early, with distributed implementation deferred.

Where this proposal is more specific than the source, it is a proposal for owner review, not an already-approved decision.
