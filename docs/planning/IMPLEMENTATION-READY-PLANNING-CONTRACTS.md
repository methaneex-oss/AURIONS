# AURIONS — Implementation-Ready Planning Contracts and Validation Plan

**Status:** Author-prepared planning supplement; proposed until owner approval. This document closes the design gaps listed in the author-side review where they can be resolved without fabricating test evidence or making owner-reserved product decisions. It does not claim SQL execution, device measurements, dependency audit, penetration testing, or implementation.

**Authority:** The imported owner decision register remains authoritative. Where this supplement adds detail, it is an engineering proposal. A proposal must not silently become an owner decision.

## 1. Scope and completion semantics

This supplement defines:
- Component ownership and dependency rules.
- Versioned command, query, event and Python-worker contracts.
- Authorization policy and approval semantics.
- Durable operation lifecycle, recovery and uncertain-side-effect handling.
- Persistence transaction boundaries and synchronization/deletion protocol.
- Test catalogue and measurable acceptance rules.
- Dependency, platform, device, security and schema validation procedures.
- Implementation work-package order, dependencies and exit criteria.
- Explicit unresolved owner decisions and evidence gates.

Three kinds of completion must not be conflated:

1. **Specified:** the contract/design exists and is internally reviewable.
2. **Validated:** the design or artifact has passed the named reproducible test or review.
3. **Implemented:** production code/configuration exists and passes its acceptance tests.

This document can move items to Specified only. It cannot move empirical or implementation gates to Validated/Implemented.

## 2. Normative language and compatibility

The terms MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are normative.

### 2.1 Versioning
- Every public command, query, event, worker message, persisted schema and sync envelope has an explicit major/minor version.
- Major changes are incompatible; minor changes add optional fields or values with defined fallback behaviour.
- Unknown major versions are rejected before side effects.
- Unknown optional fields are ignored only where the schema explicitly permits it; security-relevant unknown fields cause rejection.
- Producers declare supported versions; consumers advertise accepted ranges.
- Persisted records retain the schema version used to encode them.
- Migrations are ordered, deterministic, restartable and accompanied by rollback/restore instructions. Destructive migrations require a verified backup and a recovery rehearsal.

### 2.2 Common envelope
All cross-module and cross-process messages use a validated envelope:

| Field | Type / rule |
|---|---|
| `envelope_version` | Required supported major/minor |
| `message_id` | Globally unique UUID; duplicate delivery is expected |
| `message_type` | Namespaced stable identifier |
| `schema_version` | Version for message body |
| `created_at` | UTC timestamp; producer clock is advisory |
| `producer_id` | Authenticated component/device identity |
| `correlation_id` | Required trace/task correlation |
| `causation_id` | Optional parent message/operation |
| `tenant_or_owner_id` | Required owner scope; never inferred from model text |
| `payload` | Type-validated body; bounded size |
| `classification` | Data sensitivity label |
| `integrity` | Transport/storage integrity metadata; not a substitute for authentication |

The receiver validates identity, version, size, schema, ownership, classification and authorization before accepting the payload. A valid schema does not imply authorization.

## 3. Component ownership and dependency matrix

| Component | Owns | May depend on | Must not do |
|---|---|---|---|
| Experience | Raw observation metadata, source/provenance, capture lifecycle | Platform adapters, representation | Directly execute tools or set beliefs |
| Representation | Typed modality-neutral representations and confidence/provenance | Experience, modality adapters | Decide authority or mutate governance |
| Context | Context assembly and relevance metadata | Representation, memory query interfaces | Persist foreign-domain records directly |
| Memory | Episodic/semantic/working-memory persistence contracts and retrieval | Storage abstraction, provenance | Authorize actions or silently rewrite evidence |
| Knowledge/beliefs | Claims, evidence links, confidence, revision history | Memory, evidence evaluation | Treat model output as verified fact |
| Prediction | Prediction records, horizons, expected outcomes and uncertainty | Beliefs, context | Execute actions |
| Appraisal/attention | Salience, resource allocation and prioritization outputs | Context, goals, prediction | Hardcode stimulus-to-emotion/action conclusions |
| Reasoning | Inference traces and candidate explanations | Context, knowledge, inference interface | Grant permissions or write protected state |
| Goals/planning | Goal state, plan graph, dependencies, budgets and checkpoints | Reasoning, scheduler, capability descriptions | Assume tool capability implies permission |
| Decision | Candidate selection and rationale | Goals, plans, risk estimates | Bypass policy enforcement |
| Governance | Identity, policies, permissions, approvals, audit | Secure key/identity provider, governance DB | Trust model-provided identity or self-grant |
| Action gateway | Operation validation, dispatch, receipts and verification | Governance, capability adapters, event store | Execute without a fresh policy decision |
| Scheduler | Durable task runs, triggers, deadlines, budgets and cancellation | Goals/plans, operation store | Expand authority beyond task grant |
| Learning/evaluation | Experiment provenance, datasets, metrics, candidate results | Memory export interfaces, isolated workers | Activate candidate or modify protected runtime state |
| Inference adapter | Model/provider request/response normalization | Local/remote provider clients | Treat generated content as trusted instruction |
| Python worker supervisor | Process lifecycle, schema validation, quotas and artifact intake | Worker protocol, artifact registry | Import worker state into live cognition without validation |
| Sync | Authenticated change exchange, cursors, tombstones and receipts | Domain export/import APIs, device identity | Replicate SQLite files or bypass local policy |
| UI/platform adapter | Presentation, OS permission prompts and user input | Application command/query API | Directly mutate domain DBs or make authorization decisions |

### 3.1 Dependency rules
- Dependencies point toward stable domain interfaces; no component may import another component's private persistence schema.
- Governance and action gateway are dependencies of execution, not of model reasoning.
- Cognitive modules may exchange typed events and queries; no global mutable singleton state.
- Event handlers MUST be idempotent and MUST NOT recursively create unbounded event cycles.
- Cycles between module dependencies are prohibited. Feedback loops are represented as asynchronous events/state transitions, not cyclic compile-time dependencies.
- Cross-domain writes use owning-domain commands. A transaction spanning SQLite files is not assumed atomic.
- A dependency exception requires a recorded rationale, owner, failure impact and removal/validation plan.

## 4. Application API: commands, queries and events

### 4.1 Command contract
A command requests a state transition; it is not proof that the transition occurred.

Required fields: `command_id`, `command_version`, `owner_id`, `actor_identity`, `operation_id`, `issued_at`, `deadline`, `idempotency_key`, `requested_capability`, `payload`, `data_classification`, `approval_reference` (nullable only when policy says no approval is required).

Initial command families:
- `experience.submit`
- `memory.retrieve`
- `goal.create`, `goal.cancel`
- `plan.propose`, `plan.checkpoint`
- `operation.propose`, `operation.cancel`, `operation.reconcile`
- `approval.request`, `approval.revoke`
- `learning.experiment.submit`, `learning.candidate.evaluate`
- `device.pair`, `device.revoke` (future multi-device phase)

A command response is one of: `accepted`, `rejected`, `pending`, `conflict`, `unsupported_version`. Accepted means durably accepted for processing, not completed.

### 4.2 Query contract
Queries are read-only, scoped to an authenticated owner/device context, bounded by timeout and result size, and carry a consistency indicator (`snapshot`, `eventual`, or `local_committed`). Queries MUST NOT trigger hidden side effects.

Initial query families: `memory.search`, `goal.get`, `task.status`, `operation.status`, `permission.inspect`, `audit.lookup`, `device.capabilities`.

### 4.3 Event catalogue
Every event includes the common envelope and an immutable event body. Initial event names:
- `experience.observed.v1`
- `representation.created.v1`
- `context.assembled.v1`
- `memory.recorded.v1`, `memory.retrieved.v1`
- `belief.proposed.v1`, `belief.revised.v1`
- `prediction.created.v1`, `prediction.evaluated.v1`
- `goal.created.v1`, `plan.proposed.v1`, `plan.checkpointed.v1`
- `permission.evaluated.v1`, `approval.requested.v1`, `approval.decided.v1`
- `operation.accepted.v1`, `operation.started.v1`, `operation.succeeded.v1`, `operation.failed.v1`, `operation.uncertain.v1`, `operation.reconciled.v1`
- `outcome.observed.v1`, `learning.experiment.completed.v1`, `candidate.activated.v1`, `candidate.rolled_back.v1`
- `sync.change.exported.v1`, `sync.change.applied.v1`, `sync.tombstone.applied.v1`

Events are append-only facts. Corrections are new compensating events with causation links; do not rewrite history to conceal a prior outcome.

## 5. C++ / Python worker protocol

Python is an untrusted, isolated experiment worker. It is not an authority boundary for production state.

### 5.1 Process contract
- Parent starts a worker with an explicit executable, pinned environment, working directory, resource limits and generated job ID.
- Input/output use newline-delimited UTF-8 JSON messages with a strict maximum message size and schema version.
- Standard output is protocol-only; diagnostics go to standard error.
- Parent enforces wall-clock deadline, CPU/memory limits where supported, cancellation and process termination.
- No ambient production DB credentials, governance keys, tool credentials or unrestricted network access are provided.
- Worker reads only job-scoped input artifacts and writes only to a job-scoped output directory.
- Parent validates every output and computes artifact hashes before registering it.
- Worker cannot activate models, alter policies, mutate live memory, grant permissions or execute tools.

### 5.2 Message types
Request: `job_id`, `protocol_version`, `job_type`, `input_artifact_refs[]`, `config`, `seed`, `resource_budget`, `deadline`.

Progress: `job_id`, `sequence`, `phase`, `progress_fraction` (optional), `metrics` (bounded, non-sensitive).

Result: `job_id`, `status`, `output_artifact_refs[]`, `metrics`, `environment_manifest`, `dataset_manifest`, `code_revision`, `random_seed`, `started_at`, `finished_at`.

Failure: `job_id`, `error_code`, `retryable`, `diagnostic_ref`; never include secrets in diagnostics.

### 5.3 Worker failure semantics
Malformed message, unsupported version, oversized output, timeout, resource exhaustion, nonzero exit, missing artifact, hash mismatch or undeclared output fails the job. A failed worker result is not partially applied. Retrying creates a new attempt under the same logical experiment ID and a distinct attempt ID.

## 6. Authorization policy and approval protocol

### 6.1 Risk classes
Risk classes are cumulative; the highest applicable class governs.

| Class | Meaning | Default treatment |
|---|---|---|
| R0 | Public, non-sensitive read or local computation | Allow only if capability and scope are explicitly available |
| R1 | Owner-local, reversible, low-impact state change | Allow only within explicit standing grant and resource budget |
| R2 | Sensitive local data access or reversible consequential local change | Narrow grant; log; approval when policy/data sensitivity requires |
| R3 | External disclosure, external communication, account-affecting or materially consequential action | Explicit owner approval unless a narrowly defined standing authorization exists; sensitive data disclosure always explicit |
| R4 | Financial transaction, purchase, permanent destructive operation, significant security change | Explicit per-operation approval |
| R5 | Protected governance/core authority change | Explicit owner approval, independent validation, rollback/recovery; never model-authorized |

If classification is ambiguous, policy unavailable, identity invalid or policy version unknown: deny. A model's risk estimate is advisory only; the enforcement layer independently classifies from the registered capability and concrete parameters.

### 6.2 Authorization decision
Evaluate at execution time:
1. Authenticated owner session and actor/device identity.
2. Capability registered, enabled and locally available.
3. Resource and target are within explicit scope.
4. Data categories and recipients are permitted.
5. Risk class and policy version.
6. Budget, rate, time and expiry constraints.
7. Required approval exists and matches exact operation digest.
8. Device OS permission is still granted.
9. Operation is not cancelled, revoked, expired or replayed.

Decision is `allow`, `deny`, or `require_approval`, with stable reason codes. A previous allow is not a reusable approval token.

### 6.3 Exact-operation approval
Approval record binds:
- one-time request ID and nonce;
- authenticated owner identity/session;
- operation ID and canonical parameter digest;
- capability ID/version, target and destination;
- data categories and disclosure recipients;
- risk class and policy version;
- resource/cost limits;
- expiry and revocation state.

Any material change to parameters, recipient, target, data category, capability version or policy version invalidates approval and requires a new request. Approval is single-use and replay-protected. Approval UI presents a human-readable summary derived from the canonical operation, not model-authored prose alone. Durable audit records request, display payload hash, owner decision, execution decision and final receipt.

### 6.4 Baseline policy tests
- Invalid/expired/revoked session → deny.
- Unknown capability or target outside scope → deny.
- Missing policy store or corrupt policy → deny.
- Model asks itself for permission → no effect.
- Changed amount/recipient/target after approval → approval invalid.
- Replayed approval ID/nonce → deny.
- Approval from another owner/device session → deny.
- External disclosure with sensitive data and no explicit approval → deny.
- OS permission revoked after planning → execution denied.
- R4/R5 operation without matching approval → deny.
- Harmless authorized read within scope → no repeated approval prompt.
- Policy version changes between approval and execution → re-evaluate; stale approval rejected.

## 7. Durable operation lifecycle and recovery

### 7.1 State machine
Allowed transitions:

`PROPOSED → VALIDATING → AWAITING_APPROVAL → READY → DISPATCHED → RUNNING → SUCCEEDED`

Alternative terminal/exception transitions:
- `PROPOSED/VALIDATING/READY → REJECTED`
- `AWAITING_APPROVAL → EXPIRED | REVOKED | CANCELLED`
- `READY/DISPATCHED/RUNNING → CANCEL_REQUESTED`
- `RUNNING → FAILED | UNCERTAIN`
- `CANCEL_REQUESTED → CANCELLED | SUCCEEDED | UNCERTAIN`
- `UNCERTAIN → RECONCILING → SUCCEEDED | FAILED | COMPENSATION_REQUIRED | MANUAL_INTERVENTION`
- `COMPENSATION_REQUIRED → COMPENSATING → COMPENSATED | MANUAL_INTERVENTION`

Terminal states are immutable; corrections are new linked operations/events. Never transition UNCERTAIN directly to retry.

### 7.2 Operation record
Persist: operation ID, task/goal ID, owner/actor/device, capability and version, canonical parameter hash, target, risk class, policy version, approval reference, idempotency key, deadlines, resource budget, current state, attempt number, dispatch receipt, external reference, observed result, verification evidence, timestamps and causation/correlation IDs.

### 7.3 Side-effect rules
- Prefer idempotent operations with stable idempotency keys.
- Before dispatch, durably record intent and authorization decision.
- After dispatch, persist provider/device receipt before declaring success.
- A timeout after dispatch is UNCERTAIN, not FAILED.
- Reconcile against the target/provider using an operation-specific query before retrying.
- If no reliable reconciliation is possible, stop and request manual intervention; do not risk duplicate side effects.
- Compensation is a new explicit operation, not rollback fiction. It must be separately authorized if consequential.
- Cancellation is cooperative; a dispatched external operation may already have happened. Report that uncertainty.

### 7.4 Crash recovery
On restart:
1. Load non-terminal operations from event store.
2. Validate schema versions and integrity.
3. Recheck session, permission, approval expiry/revocation and policy version.
4. Resume only operations proven not dispatched or whose adapter supports safe idempotent resume.
5. Mark dispatched-without-receipt operations UNCERTAIN and reconcile.
6. Restore scheduler checkpoints and budgets; expired tasks do not execute.
7. Emit recovery events and preserve an audit trail.

No cross-database atomic transaction is assumed. Use local transaction + outbox in each owning store, stable IDs, idempotent consumers and reconciliation.

## 8. Persistence, schema and transaction boundaries

### 8.1 Store ownership
- `aurion_memory.db`: experience/representation/context, memories, knowledge, evidence, beliefs, predictions, goals, plans, learning metadata.
- `aurion_events.db`: event log, operations, operation steps, task runs/checkpoints, outbox/inbox, recovery journal.
- `aurion_governance.db`: identities, device trust, policies, capabilities/grants, approvals, revocations, disclosure records and security audit.

Each DB has its own migration ledger, backup/restore procedure, integrity check and schema version. Cross-file foreign keys are prohibited. Cross-store references use UUIDs validated by application services.

### 8.2 Transaction pattern
- A domain command writes its aggregate and an outbox record in one transaction within the owning DB.
- Outbox publisher retries until acknowledged; event ID deduplicates consumers.
- Consumer records inbox receipt and state change in one local transaction.
- Cross-store workflows use durable operation/saga state and compensating actions; never imply a distributed ACID commit.
- A write spanning governance and operation stores first obtains a signed/immutable decision reference, then writes the operation record; if either step fails, reconcile from durable audit and fail closed.
- SQLite connections use explicit transaction scopes, foreign keys within each DB, busy timeout and WAL only after target-device validation. Durability/synchronous settings must be documented and tested against power-loss expectations.

### 8.3 DDL and migration acceptance
Before implementation approval:
- Parse/execute all three DDLs against the pinned minimum SQLite version.
- Enable foreign keys and verify every declared FK.
- Run schema lint for missing indexes on foreign keys, owner scope, status, timestamps, retrieval predicates and idempotency keys.
- Validate uniqueness for IDs, idempotency keys and active approval nonces.
- Test migration from empty DB and each supported prior schema version.
- Test interrupted migration and recovery from verified backup.
- Test constraint violations, busy/locked behaviour, WAL checkpoint, disk full, read-only/corrupt DB and process crash during commit.
- Verify no cross-file FK or direct database-file replication exists.
- Record query plans and target-device timings for representative retrieval and writes.
- DDL is not approved merely because it parses; semantic invariants and failure tests must pass.

## 9. Multi-device synchronization and deletion protocol

### 9.1 Domain classification
Each record type declares: authoritative device/store, whether sync is allowed, sensitivity, encryption requirement, conflict policy, retention, deletion policy and whether it may be exported to a remote relay. Default is local-only.

Governance approvals and secrets are not blindly synchronized. Device trust is managed by owner-authorized pairing and revocation. A device cannot create owner approval on behalf of another device.

### 9.2 Change envelope
A sync change contains change ID, domain/type/schema version, owner ID, source device ID, aggregate ID, aggregate version, causal parents/vector metadata where required, creation time, payload hash, encrypted payload reference, tombstone flag, retention class and idempotency key. Transport authenticates both devices and verifies authorization at destination.

### 9.3 Conflict handling
- Single-writer domains reject concurrent writes from non-authoritative devices.
- Multi-writer domains require explicit domain merge functions and deterministic tests.
- Last-write-wins is prohibited for beliefs, approvals, permissions, deletion and consequential task state.
- Conflicts are retained as conflict records with both versions and provenance; no evidence is silently discarded.
- Task handoff uses lease/ownership epoch and operation receipts. A stale device cannot resume after lease revocation.
- Duplicate changes are acknowledged idempotently; out-of-order changes are buffered or rejected pending causal predecessors.

### 9.4 Offline devices and deletion
- Deletion creates a signed tombstone with owner, object/domain ID, deletion epoch, causal/version metadata and timestamp.
- Active indexes and retrieval visibility are removed locally immediately.
- Tombstones are retained until all authorized devices acknowledge or are revoked, plus the defined safety retention interval.
- Offline devices receive tombstones on reconnect before accepting new writes for affected objects.
- A device behind a deletion epoch cannot reintroduce the deleted record; its conflicting payload is quarantined and audited.
- Future backups exclude deleted records. Historical backups expire within 30 days of deletion.
- Restore must replay tombstones before exposing restored content.
- If an offline device cannot be reached, UI must disclose pending deletion propagation and allow owner revocation.
- Deletion audit retains only minimal metadata and must not preserve deleted content.

## 10. Test catalogue and release acceptance

Every test has stable ID, requirement link, fixture/version, preconditions, exact steps, expected result, cleanup, determinism notes and evidence artifact. No test passes on a log message alone; assert durable state and observable behaviour.

### 10.1 Foundation and contract tests
- CT-001: supported envelope round-trip preserves IDs, version and classification.
- CT-002: unknown major version rejected without side effect.
- CT-003: duplicate message delivery produces one domain transition.
- CT-004: invalid schema, oversized payload and missing owner scope rejected.
- CT-005: unsupported command returns stable error; no hidden side effect.
- CT-006: query API performs no writes.
- CT-007: dependency graph contains no forbidden cycles.

### 10.2 Cognitive-cycle integration tests
- CG-001: observation is stored with provenance and source.
- CG-002: representation/context link to source experience.
- CG-003: retrieval returns provenance and respects owner/data scope.
- CG-004: new contradictory evidence creates a belief revision record; prior evidence remains auditable.
- CG-005: prediction stores expected outcome, horizon and confidence.
- CG-006: observed consequence evaluates prediction without rewriting the prediction.
- CG-007: appraisal/attention changes allocation through learned/state mechanisms, not fixed stimulus→emotion/action tables.
- CG-008: outcome influences a later relevant decision in a repeatable paired test.
- CG-009: unrelated control tasks do not regress beyond declared tolerance.
- CG-010: restart preserves durable experience, belief and task continuity.

### 10.3 Learning proof
- LE-001: freeze baseline version, dataset, task set, prompts/configuration and scoring procedure.
- LE-002: separate training/development/held-out test data; prevent leakage by IDs and content similarity checks.
- LE-003: include related unseen variations and distribution-shift probes.
- LE-004: compare candidate against frozen baseline across repeated seeded runs; report confidence intervals and sample size.
- LE-005: require predefined minimum improvement and no critical safety/regression failures.
- LE-006: record experiment code revision, data hashes, model/artifact hash, environment, seed and metrics.
- LE-007: candidate remains quarantined until evaluation and owner/policy approval; activation is versioned and reversible.
- LE-008: rollback restores prior artifact/configuration and emits audit event.
- Memory update, belief revision, successful training execution or improved training loss alone do not satisfy learning acceptance.

### 10.4 Governance and operation tests
- AU-001 through AU-012: execute every baseline policy test in Section 6.4.
- OP-001: operation cannot dispatch before durable intent and authorization.
- OP-002: crash before dispatch resumes safely.
- OP-003: crash after dispatch without receipt becomes UNCERTAIN.
- OP-004: timeout reconciliation prevents duplicate side effect.
- OP-005: cancellation race reports succeeded/cancelled/uncertain accurately.
- OP-006: expired approval and stale policy are rejected.
- OP-007: compensation is a separate authorized operation.
- OP-008: resource/deadline budget exhaustion stops work and checkpoints state.

### 10.5 Persistence, sync and deletion tests
- DB-001 through DB-010: DDL, migration, constraint, disk-full, corruption, crash, restore and transaction fault tests from Section 8.3.
- SY-001: duplicate sync envelope applies once.
- SY-002: out-of-order causal change is buffered/rejected safely.
- SY-003: conflict retains both versions and provenance.
- SY-004: tombstone reaches online device and removes active retrieval.
- SY-005: offline stale device cannot resurrect deleted content.
- SY-006: restore replays tombstones before exposing content.
- SY-007: revoked device cannot sync or execute.
- SY-008: direct SQLite file replication is absent.

### 10.6 First usable release exit criteria
The first usable local release is accepted only when:
1. Fresh install and restart preserve the same local owner/system identity under the documented recovery model.
2. A conversation creates durable, provenance-linked experience records.
3. A later session retrieves relevant memory and cites its source internally.
4. A bounded objective can be represented as a plan with dependencies, budget and cancellation.
5. At least one narrowly scoped local capability is executed through the action gateway after policy evaluation.
6. The system records dispatch receipt, observed outcome and verification evidence.
7. A restart at each operation transition recovers or reconciles without duplicate side effects.
8. An explicit denial is enforced even if the model recommends execution.
9. Offline core workflows remain available without external services.
10. A paired evaluation demonstrates outcome-sensitive later behaviour; separate held-out learning tests are required for claims of general learning improvement.
11. Data export/deletion and backup restore behave according to documented policy.
12. Test suite, build revision, environment and evidence artifacts are reproducible.

## 11. Threat model and security validation

### 11.1 Assets
Owner identity/session, governance DB, memory and private context, operation authority, approval records, provider credentials, device keys, model/training artifacts, audit integrity and update-signing keys.

### 11.2 Trust boundaries
Untrusted model output; external web/provider content; Python workers; UI clients; device agents; local IPC; network sync; filesystem/artifact imports; backup/restore; build and release pipeline.

### 11.3 Threat scenarios and controls
- Prompt injection or hostile retrieved content → content provenance/taint, no authority from content, tool policy independent of model.
- Compromised worker → sandbox/least privilege, no production secrets/DB write access, artifact validation and quarantine.
- Forged/replayed command → authenticated channel, nonce/idempotency, owner scope and replay cache.
- Approval tampering → canonical operation digest, one-time nonce, expiry, policy binding and durable audit.
- Compromised/lost device → per-device keys, scoped grants, revocation and tombstone enforcement.
- Local database theft → encryption at rest where platform/key model supports it, key separation, no plaintext secret storage.
- Malicious update/dependency → pinned dependencies, provenance/SBOM, signature verification and controlled update channel.
- Log leakage → structured redaction, data classification and secret scanning.
- Resource exhaustion → bounded payloads, quotas, timeouts, queue limits and circuit breakers.
- Backup rollback/resurrection → backup epochs, tombstone replay and integrity verification.

### 11.4 Key lifecycle
Separate owner identity keys, per-device keys, data-encryption keys, transport keys and signing keys. Generate using platform cryptographic RNG; store device secrets in Android Keystore when native Android is available. Define backup/recovery separately from key export. Support rotation with key version IDs and re-encryption/re-wrapping. Revocation invalidates future sessions and sync. Key loss must fail closed and expose a documented recovery path; do not invent recovery access that bypasses owner authority.

### 11.5 Residual risks
Termux is not a strong hostile-app sandbox; a rooted/compromised OS can access process memory and local files. Software-only controls cannot fully protect data on a compromised device. Remote providers see data intentionally transmitted to them. Offline-device deletion is delayed until reconnect or revocation. These limitations must be disclosed, not described as eliminated.

## 12. Dependency and licensing audit procedure

Before pinning a dependency:
- Record direct/transitive package, exact version, source, license and license obligations.
- Verify active maintenance, security advisories, supported compilers/ABIs, Android/ARM64 support and offline build availability.
- Check static/dynamic linking obligations, redistribution notices, model weights/data licenses and commercial-use constraints.
- Record provenance, hashes, SBOM and update policy.
- Reject abandoned, unmaintained or incompatible dependencies unless a documented exception is approved.
- Build from a clean environment with network disabled after dependency acquisition.
- Scan for known vulnerabilities and verify checksums/signatures.
- Re-run compatibility and regression tests on upgrades.

No dependency/license audit is claimed complete by this checklist. It becomes complete only when the actual selected dependency inventory and evidence are attached.

## 13. Platform and target-device validation plan

Target baseline recorded in the source spec is historical and must be remeasured. On the actual device, capture:
- Exact model/build, Android version, ABI, kernel, physical RAM, available storage and thermal state.
- Compiler/CMake/Ninja/SQLite versions and clean build logs.
- Core startup latency, idle/peak RSS, working-set growth and memory under pressure.
- Inference latency (cold/warm), tokens/sec, peak memory and sustained run duration.
- Storage read/write latency, DB contention, WAL/checkpoint behaviour and recovery.
- Battery drain and thermal throttling over a representative sustained workload.
- Background execution, process death, reboot recovery and OS battery-management behaviour.
- JNI/shared-library vs IPC prototype measurements.
- Voice ASR/TTS only if selected for a target release.

Run at least three repetitions per benchmark after a documented warm-up; report median, p95, max, variance, device temperature and test conditions. Set product thresholds only after baseline measurements and owner review. Basic inference success is not a performance qualification.

## 14. Implementation work packages and dependencies

Implementation remains blocked pending owner approval and the evidence gates in Section 15. Proposed order:

| WP | Deliverable | Depends on | Exit criteria |
|---|---|---|---|
| WP-00 | Repository/build/toolchain foundation | Planning approval | Clean reproducible host and target builds; CI green; no hidden network dependency |
| WP-01 | Contract/schema foundation | WP-00; Sections 2–5 | Versioned envelopes, command/query/event schemas, compatibility and fixtures |
| WP-02 | Persistence foundation | WP-01; Section 8 | Three DBs, migrations, integrity and crash/fault tests |
| WP-03 | Identity/governance | WP-01/02; Section 6/11 | Authenticated owner session, capability registry, default-deny enforcement, approval and audit tests |
| WP-04 | Operation runtime/scheduler | WP-01/02/03; Section 7 | Durable operation state machine, recovery, reconciliation, budgets and cancellation |
| WP-05 | Experience/representation/context | WP-01/02 | Provenance-preserving ingestion and restart-safe records |
| WP-06 | Memory/knowledge/belief | WP-02/05 | Retrieval, evidence-linked revision and conflict history |
| WP-07 | Prediction/appraisal/reasoning/goals/planning | WP-03/04/05/06 | Integrated bounded cognitive cycle; no hardcoded behavioural conclusions |
| WP-08 | Inference and narrow action adapter | WP-03/04/07 | Model-independent inference and one owner-approved local capability |
| WP-09 | Outcome and learning evaluation | WP-05–08 | Paired outcome tests, held-out evaluation harness, provenance and rollback |
| WP-10 | First user-facing interface | Product/UI owner decision; WP-01/03/04/07/08 | End-to-end first-release workflows; interface cannot bypass policy |
| WP-11 | Device integration | Platform spike; WP-10 | Android lifecycle, permission, key and background tests |
| WP-12 | Multi-device synchronization | WP-02/03/04/11; Sections 9/11 | Pairing, revocation, domain sync, conflict, deletion and handoff tests |
| WP-13 | External providers/voice/multimodal | Provider/platform decisions; WP-03/09/11 | Per-provider policy, disclosure, budgets, privacy and failure tests |

WP-00 PR #1 is a scaffold proposal and must be reconciled against this sequence; it is not authorization to implement cognition or prematurely freeze a UI/runtime choice.

## 15. Planning exit gates and outstanding evidence

### 15.1 Design deliverables addressed by this supplement
- [x] Component ownership/dependency rules specified.
- [x] Versioned envelope and command/query/event families specified.
- [x] C++/Python worker trust boundary and protocol specified.
- [x] Risk classes, authorization checks and exact-operation approval specified.
- [x] Operation lifecycle, uncertain side effects, recovery and compensation specified.
- [x] Store ownership, outbox/inbox transaction pattern and migration acceptance specified.
- [x] Multi-device change, conflict, offline and deletion semantics specified.
- [x] Test catalogue and first-release acceptance criteria specified.
- [x] Threat model, key lifecycle and residual-risk categories specified.
- [x] Dependency audit procedure specified.
- [x] Device/platform measurement protocol specified.
- [x] Work-package dependency and exit criteria proposed.

These are specified proposals, not independently validated or owner-approved implementation contracts.

### 15.2 Evidence gates not honestly closable by documentation alone
- [ ] Execute and fault-test all three actual SQLite DDLs and migrations on the selected SQLite baseline.
- [ ] Complete actual dependency/license/SBOM audit after framework/version selection.
- [ ] Run clean host and Termux/ARM64 builds; reconcile WP-00 PR #1 and obtain green CI.
- [ ] Run target-device performance, thermal, battery, memory, storage and background-lifecycle benchmarks.
- [ ] Prototype and measure Android C++ JNI/shared-library versus IPC boundary.
- [ ] Complete security review of actual implementation, keys, IPC, update chain and data flows.
- [ ] Produce reproducible test fixtures and execute the contract, governance, operation, cognitive, learning and recovery suites as code is implemented.
- [ ] Validate backup/restore and deletion expiry behaviour with actual artifacts.
- [ ] Independent review of the final revised planning baseline.
- [ ] Explicit owner approval of planning exit and implementation start.

### 15.3 Owner-reserved product decisions
The following must not be guessed by the technical lead:
1. ~~First user-facing interface (CLI, Android-native or another client).~~ **RESOLVED: CLI is the first user-facing interface.**
2. **RESOLVED: cloud operation and offline-capable mobile operation are concurrent first-release targets.** Offline mobile must not require cloud connectivity; both contexts use shared versioned contracts and the authoritative cognitive core. Mobile UI technology and exact deployment topology remain subject to validation.
3. **Android capability architecture remains to be corrected and validated.** App launch, volume adjustment and file handling were examples supplied to illustrate the breadth of possible Android interaction, not an exhaustive capability list, fixed scope or selected first action. Planning must define environment perception/representation, capability discovery, capability learning, reasoning/planning over discovered capabilities, platform adapters and independent governance. No fixed operation catalogue should be inferred from the examples.
3. Numeric performance/latency/resource thresholds after device baselines.
4. Any change to protected authority, privacy, external disclosure or risk tolerance.

The first-interface and deployment directions are owner-decided. The Android capability architecture requires correction and validation; implementation authorization and the planning exit remain separate owner gates.

## 16. Planning exit rule

Initial planning is complete only when:
- The original specification, architecture, product definition and this supplement agree.
- All design deliverables are specified and traceable to owner decisions.
- All evidence gates that are prerequisites to the chosen implementation path have passed or are explicitly accepted as staged validation gates by the owner.
- Unresolved owner decisions are answered without substituting engineering preference.
- PR #1 is reconciled with the approved work-package sequence.
- The independent reviewer has reviewed the final revision, not an earlier draft.
- Required corrections from that review are resolved or explicitly accepted by the owner.
- The owner explicitly authorizes the transition.

Until then, PR #2 stays draft/unmerged and no implementation begins.

## 17. Change log
- 2026-11-11: Added implementation-ready planning contracts, recovery/sync/security/test specifications, validation procedures, work-package dependencies and explicit evidence/owner gates to prevent known planning omissions from being delegated to the independent reviewer.
