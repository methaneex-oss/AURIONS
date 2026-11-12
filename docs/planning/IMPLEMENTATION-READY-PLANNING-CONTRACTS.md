# AURIONS — Implementation-Ready Planning Contracts and Validation Plan

**Status:** Author-prepared planning supplement; proposed until owner approval. This document closes the design gaps listed in the author-side review where they can be resolved without fabricating test evidence or making owner-reserved product decisions. It does not claim SQL execution, device measurements, dependency audit, penetration testing, or implementation.

**Authority:** The imported owner decision register remains authoritative. Where this supplement adds detail, it is an engineering proposal. A proposal must not silently become an owner decision. The [Open-World Interaction and Means Architecture](../architecture/OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md) is the foundational objective-led model. The [Cognitive and Capability Contract Matrix](../architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md) is the canonical crosswalk for world, interaction, cognitive and platform-specific state ownership, persistence, work-package and test mapping. The initial language-neutral JSON Schema source is `schemas/domain-payloads.v1.schema.json`; it currently contains 86 reusable schema definitions, while `schemas/fixtures/domain-payloads.fixture.json` contains 78 named positive payload examples across experience, representation, context, evidence, belief, prediction, appraisal, attention, reasoning, memory, knowledge, goals, plans, decisions, capability discovery/knowledge, operation lifecycle, outcome evaluation, learning, self-model, evolution, governance, checkpoints, worker protocol, task control and sync. The definition count and fixture-example count are different measures; neither implies complete handler semantics or scenario-level validation. The common envelope and extensible capability descriptor body are defined separately in `schemas/message-envelope.v1.schema.json` and `schemas/capability-descriptor-body.v1.schema.json`. It is an initial schema set, not yet the complete command/event contract corpus or a selected runtime validator.

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

This document can move items to Specified only. It cannot move empirical or implementation gates to Validated/Implemented. Command/query/response/error/compatibility payload definitions are planning contracts; they do not establish runtime conformance.

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
| Device/provider-specific environment discovery | Scoped observations, discovery provenance, versioned provider/interface descriptors and lifecycle | Platform adapters, provider contracts, governance queries | Treat discovery as permission, invent unavailable interfaces or claim this is the universal means model |
| Context | Context assembly and relevance metadata | Representation, memory query interfaces | Persist foreign-domain records directly |
| Memory | Episodic/semantic/working-memory persistence contracts and retrieval | Storage abstraction, provenance | Authorize actions or silently rewrite evidence |
| Artifact registry | Immutable artifact metadata, content hashes, storage references, lineage and deletion state | Filesystem/object storage, memory DB, retention/deletion services | Treat filenames as trusted paths, merge authorization semantics during deduplication or expose unvalidated artifacts |
| Knowledge/beliefs | Claims, evidence links, confidence, revision history | Memory, evidence evaluation | Treat model output as verified fact |
| Prediction | Prediction records, horizons, expected outcomes and uncertainty | Beliefs, context | Execute actions |
| Outcome evaluation | Prediction/plan comparison, observed postconditions, attribution hypotheses and evaluation evidence | Prediction, action receipts, experience, context | Rewrite original predictions or equate provider success with verified effects |
| Appraisal/attention | Contextual appraisal estimates, salience and adaptive resource allocation | Context, goals, prediction, learning evidence | Hardcode stimulus-to-emotion/action conclusions or suppress governance checks |
| Reasoning | Inference traces and candidate explanations | Context, knowledge, inference interface | Grant permissions or write protected state |
| Goals/planning | Goal state, plan graph, dependencies, budgets and checkpoints | Reasoning, scheduler, capability descriptions | Assume tool capability implies permission |
| Decision | Candidate selection and rationale | Goals, plans, risk estimates | Bypass policy enforcement |
| Governance | Identity, policies, permissions, approvals, audit | Secure key/identity provider, governance DB | Trust model-provided identity or self-grant |
| Programmatic execution gateway | Exact operation validation, dispatch, receipts, independent verification and reconciliation for integrations that invoke programmatic interfaces | Governance, applicable provider adapters, event store | Execute without a fresh policy decision or imply all means require this gateway |
| Scheduler | Durable task runs, triggers, deadlines, budgets and cancellation | Goals/plans, operation store | Expand authority beyond task grant |
| Learning/evaluation | Experience-dependent mechanism/capability updates, experiment provenance, datasets, metrics and candidate results | Outcome evaluation, memory/knowledge interfaces, isolated workers | Treat storage as learning, activate candidate or modify protected runtime state |
| Self-model | Evidence-backed capability, limitation, confidence, resource and performance estimates | Discovery, outcomes, benchmarks, learning | Self-authorize or claim unverified capability |
| Evolution | Isolated change proposals, impact analysis, candidate comparison, approval and rollback records | Self-model, learning, governance | Self-approve or mutate protected authority |
| Inference adapter | Model/provider request/response normalization | Local/remote provider clients | Treat generated content as trusted instruction |
| Python worker supervisor | Process lifecycle, schema validation, quotas and artifact intake | Worker protocol, artifact registry | Import worker state into live cognition without validation |
| Sync | Authenticated change exchange, cursors, tombstones and receipts | Domain export/import APIs, device identity | Replicate SQLite files or bypass local policy |
| UI/platform adapter | Presentation, OS permission prompts and user input | Application command/query API | Directly mutate domain DBs or make authorization decisions |

### 3.1 Dependency rules
- Dependencies point toward stable domain interfaces; no component may import another component's private persistence schema.
- Governance and the programmatic execution gateway are dependencies of consequential provider-backed execution, not of objective/world understanding, means reasoning, human-mediated interaction or all forms of deliberation.
- Cognitive modules may exchange typed events and queries; no global mutable singleton state.
- Event handlers MUST be idempotent and MUST NOT recursively create unbounded event cycles.
- Cycles between module dependencies are prohibited. Feedback loops are represented as asynchronous events/state transitions, not cyclic compile-time dependencies.
- Cross-domain writes use owning-domain commands. A transaction spanning SQLite files is not assumed atomic.
- A dependency exception requires a recorded rationale, owner, failure impact and removal/validation plan.

## 4. Application API: commands, queries and events

### 4.1 Command contract
A command requests a state transition; it is not proof that the transition occurred.

Canonical body schema: `commandEnvelope`. Required fields: `command_id`, open namespaced `command_type`, `command_version`, `owner_id`, `actor_identity`, `issued_at`, `deadline`, `idempotency_key`, `payload`, and `data_classification`. `operation_id`, `requested_capability` and `approval_reference` are optional nullable references because many commands do not create an external operation or request a platform capability. The receiver resolves `command_type + command_version` through its versioned command registry and validates the payload against that registered schema; it must not trust a producer-supplied arbitrary schema path.

Initial command families:
- `experience.submit`, `representation.create`, `context.assemble`, `context.invalidate`
- `environment.observe`, `capability.discover`, `capability.verify`, `capability.invalidate`, `capability.knowledge.propose`, `capability.knowledge.revise`
- `memory.retrieve`, `belief.propose`, `belief.revise`, `prediction.create`, `prediction.evaluate`
- `appraisal.evaluate`, `attention.allocate`, `reasoning.assess`
- `goal.create`, `goal.revise`, `goal.cancel`, `plan.propose`, `plan.revise`, `plan.checkpoint`, `decision.record`
- `operation.propose`, `operation.cancel`, `operation.reconcile`
- `approval.request`, `approval.revoke`, `outcome.evaluate`
- `learning.update.propose`, `learning.experiment.submit`, `learning.candidate.evaluate`
- `self_model.update.propose`, `evolution.change.propose`, `evolution.candidate.evaluate`, `evolution.candidate.activate`, `evolution.candidate.rollback`
- `task.start`, `task.pause`, `task.resume`, `task.cancel`
- `device.pair`, `device.revoke` (future multi-device phase)

A command response uses `commandResponse`, echoes `command_type` and `command_version`, and is one of: `accepted`, `rejected`, `pending`, `conflict`, `unsupported_version`. Accepted means durably accepted for processing, not completed. Failures use `contractError`, which records retryability and whether a side effect was not dispatched, dispatched, unknown or not applicable; this distinction is mandatory for safe retry/reconciliation.

The command envelope is a wrapper, not a complete command contract. The initial first-release command families are bound to request payload schemas in Section 4.2.1. Each handler still requires a verified owning state transition, authorization requirements, idempotency behaviour, cancellation/deadline rules, response semantics and error mapping. New command types must add a schema and registry entry before publication. Unknown command types or unsupported major versions are rejected before side effects.

### 4.2 Query contract
Canonical body schema: `queryEnvelope`. Each query carries an open namespaced `query_type` and `query_version`, resolved through a versioned query registry rather than a closed enum. Queries are read-only, scoped to an authenticated owner/device context, bounded by timeout and result size, and carry a consistency indicator (`snapshot`, `eventual`, or `local_committed`). Queries MUST NOT trigger hidden side effects.

Initial query families: `environment.inspect`, `capability.search`, `capability.inspect`, `capability.knowledge.inspect`, `representation.inspect`, `context.get`, `memory.search`, `knowledge.search`, `belief.inspect`, `prediction.inspect`, `appraisal.inspect`, `attention.inspect`, `reasoning.inspect`, `goal.get`, `plan.get`, `decision.inspect`, `task.status`, `operation.status`, `permission.inspect`, `audit.lookup`, `device.capabilities`. Query families are versioned interface namespaces, not a closed list of system behaviours or capabilities. The initial query families are bound to the generic `domainQuery` or `memoryRetrievalQuery` input and a typed result-item schema in Section 4.2.2; responses use `queryResponse`. Each handler still requires verified authorization/data-scope rules, consistency semantics, resource bounds and redaction behaviour. New query types must add explicit input/result bindings before publication.

### 4.2.1 Initial command payload registry

The machine-readable [command/query registry](../../schemas/command-query-registry.v1.json), governed by `schemas/command-query-registry.v1.schema.json`, is the canonical versioned inventory. It records 45 command-envelope references (43 with request-payload mappings and two device commands deferred to the later multi-device phase) and 21 query-envelope, input and result mappings. Every entry is explicitly non-dispatchable while any required handler binding is unresolved. The tables below remain the human-readable payload crosswalk; they do not authorize runtime registration.

The following table binds the initial command families to request-body schemas. The registry is extensible; it is not a closed list of behaviours or Android capabilities. Command handlers MUST validate the body against the registered schema version before state mutation. The event emitted after a successful command remains a separate immutable event and must use the event-body mapping in Section 4.3.

| Command type | Request payload schema |
|---|---|
| `experience.submit` | `experienceObserved` |
| `representation.create` | `representationCreated` |
| `context.assemble` | `contextAssemblyRequest` |
| `context.invalidate` | `contextInvalidationRequest` |
| `environment.observe` | `environmentObservationRequest` |
| `capability.discover` | `capabilityDiscoveryRequest` |
| `capability.verify` | `capabilityVerificationRequest` |
| `capability.invalidate` | `capabilityInvalidationRequest` |
| `capability.knowledge.propose` / `capability.knowledge.revise` | `capabilityKnowledgeRevision` |
| `memory.retrieve` | `memoryRetrievalQuery` |
| `belief.propose` / `belief.revise` | `beliefRevision` |
| `prediction.create` | `predictionCreated` |
| `prediction.evaluate` | `predictionEvaluationRequest` |
| `appraisal.evaluate` | `appraisalEvaluationRequest` |
| `attention.allocate` | `attentionAllocationRequest` |
| `reasoning.assess` | `reasoningAssessmentRequest` |
| `goal.create` / `goal.revise` | `goalRevision` |
| `goal.cancel` | `goalControlRequest` |
| `plan.propose` / `plan.revise` | `planRevision` |
| `plan.checkpoint` | `planCheckpointRequest` |
| `decision.record` | `decisionRecorded` |
| `operation.propose` | `operationProposal` |
| `operation.cancel` / `operation.reconcile` | `operationControlRequest` |
| `approval.request` | `approvalRequested` |
| `approval.revoke` | `approvalRevocationRequest` |
| `outcome.evaluate` | `outcomeEvaluationRequest` |
| `learning.update.propose` | `learningUpdate` |
| `learning.experiment.submit` | `learningExperimentRequest` |
| `learning.candidate.evaluate` | `learningCandidateEvaluationRequest` |
| `self_model.update.propose` | `selfModelUpdated` |
| `evolution.change.propose` | `evolutionProposed` |
| `evolution.candidate.evaluate` / `evolution.candidate.activate` / `evolution.candidate.rollback` | `evolutionCandidateActionRequest` |
| `task.start` / `task.pause` / `task.resume` / `task.cancel` | `taskControlRequest` |
| `device.pair` / `device.revoke` | **DEFERRED:** future multi-device phase; no first-release request schema or executable command is authorized. |

The schema bindings above define payload shape only. Each handler still requires an owning component, allowed state transition, expected-version/concurrency check, authorization/data-scope rule, idempotency rule, cancellation/deadline behaviour, response and failure mapping. Where a request reuses a domain payload schema, the handler must not persist the request as an event without applying the owning domain's validation and transition rules.

### 4.2.2 Initial query input and result registry

The same machine-readable registry is authoritative for query type/version, common query envelope, input schema, result-item schema, owner, persistence mapping and generic payload-shape fixture references. All entries remain non-dispatchable until authorization, redaction, consistency, ordering, limits, freshness and read-only evidence are bound and tested. All query types use the generic `domainQuery` input schema except memory retrieval, which uses `memoryRetrievalQuery`. Results are wrapped in `queryResponse`; `query_type + query_version` resolves the domain-specific result schema. Query handlers remain read-only and must enforce the owner/device scope and sensitivity policy before returning records.

| Query type | Input schema | Result item schema |
|---|---|---|
| `environment.inspect` | `domainQuery` | `environmentObserved` |
| `capability.search` | `domainQuery` | `capabilityDescriptorRecord` |
| `capability.inspect` | `domainQuery` | `capabilityDescriptorRecord` |
| `capability.knowledge.inspect` | `domainQuery` | `capabilityKnowledgeRevision` |
| `representation.inspect` | `domainQuery` | `representationCreated` |
| `context.get` | `domainQuery` | `contextSnapshot` |
| `memory.search` | `memoryRetrievalQuery` | `memoryRetrieval` |
| `knowledge.search` | `domainQuery` | `knowledgeItem` |
| `belief.inspect` | `domainQuery` | `beliefRevision` |
| `prediction.inspect` | `domainQuery` | `predictionCreated` |
| `appraisal.inspect` | `domainQuery` | `appraisalUpdated` |
| `attention.inspect` | `domainQuery` | `attentionAllocated` |
| `reasoning.inspect` | `domainQuery` | `reasoningHypothesisProposed` |
| `goal.get` | `domainQuery` | `goalRevision` |
| `plan.get` | `domainQuery` | `planRevision` |
| `decision.inspect` | `domainQuery` | `decisionRecorded` |
| `task.status` | `domainQuery` | `taskRunStatus` |
| `operation.status` | `domainQuery` | `operationLifecycleEvent` |
| `permission.inspect` | `domainQuery` | `permissionRecord` |
| `audit.lookup` | `domainQuery` | `auditRecord` |
| `device.capabilities` | `domainQuery` | `capabilityDescriptorRecord` |

The result schema specifies each result item; `queryResponse.results` is a collection of those validated items with pagination and consistency metadata. This table does not grant access to a record: every result is filtered through the owning domain's authorization and disclosure rules. New query types require an explicit input/result binding and fixtures before publication.

### 4.3 Event catalogue
Every event includes the common envelope and an immutable event body. Initial event names:
- `experience.observed.v1`, `evidence.recorded.v1`
- `objective.created.v1`
- `world.entity.observed.v1`, `world.relationship.revised.v1`, `situation.snapshot.created.v1`
- `means.affordance.proposed.v1`, `interaction.proposed.v1`, `interaction.outcome.observed.v1`
- `representation.created.v1`, `representation.revised.v1`
- `context.assembled.v1`, `context.invalidated.v1`
- `environment.observed.v1`, `capability.discovered.v1`, `capability.verified.v1`, `capability.invalidated.v1`, `capability.revoked.v1`, `capability.knowledge.revised.v1`
- `memory.recorded.v1`, `memory.retrieved.v1`
- `belief.proposed.v1`, `belief.revised.v1`
- `prediction.created.v1`, `prediction.evaluated.v1`
- `appraisal.updated.v1`, `attention.allocated.v1`, `reasoning.hypothesis.proposed.v1`, `decision.recorded.v1`, `outcome.evaluated.v1`
- `goal.created.v1`, `goal.revised.v1`, `plan.proposed.v1`, `plan.revised.v1`, `plan.checkpointed.v1`
- `permission.evaluated.v1`, `approval.requested.v1`, `approval.decided.v1`
- `operation.proposed.v1`, `operation.validating.v1`, `operation.awaiting_approval.v1`, `operation.ready.v1`, `operation.dispatched.v1`, `operation.running.v1`, `operation.succeeded.v1`, `operation.failed.v1`, `operation.rejected.v1`, `operation.expired.v1`, `operation.revoked.v1`, `operation.cancel_requested.v1`, `operation.cancelled.v1`, `operation.uncertain.v1`, `operation.reconciling.v1`, `operation.reconciled.v1`, `operation.compensation_required.v1`, `operation.compensating.v1`, `operation.compensated.v1`, `operation.manual_intervention.v1`
- `outcome.observed.v1`, `learning.update.proposed.v1`, `learning.update.accepted.v1`, `learning.experiment.completed.v1`
- `self_model.updated.v1`, `evolution.proposed.v1`, `evolution.candidate.evaluated.v1`, `candidate.activated.v1`, `candidate.rolled_back.v1`
- `sync.change.exported.v1`, `sync.change.applied.v1`, `sync.tombstone.applied.v1`, `sync.conflict.detected.v1`, `sync.conflict.resolved.v1`
- `artifact.registered.v1`, `artifact.quarantined.v1`, `artifact.deleted.v1`, `disclosure.recorded.v1`, `retention.deletion.requested.v1`, `retention.deletion.completed.v1`
- `worker.job.requested.v1`, `worker.job.progressed.v1`, `worker.job.completed.v1`, `worker.job.failed.v1`
- `task.control.requested.v1`, `task.run.transitioned.v1`

#### Event-body schema binding

Every event body MUST validate against exactly one versioned payload schema before persistence or publication. The common envelope's `message_type` selects the event contract; the payload schema does not grant authority. The following table is the human-readable event-to-body mapping. The machine-readable companion `schemas/event-registry.v1.json`, validated by `schemas/event-registry.v1.schema.json`, records all 84 event names, payload schema references and body-fixture references. The registry is a design baseline only: every entry remains non-dispatchable with unresolved runtime handler, consumer semantics, owner transition and event-specific acceptance bindings.

| Event family | Payload definition |
|---|---|
| `experience.observed.v1` | `experienceObserved` |
| `evidence.recorded.v1` | `evidenceItem` |
| `objective.created.v1` | `objective` in `world-interaction.v1.schema.json` |
| `world.entity.observed.v1` | `entity` in `world-interaction.v1.schema.json` |
| `world.relationship.revised.v1` | `relationship` in `world-interaction.v1.schema.json` |
| `situation.snapshot.created.v1` | `situation` in `world-interaction.v1.schema.json` |
| `means.affordance.proposed.v1` | `affordanceHypothesis` in `world-interaction.v1.schema.json` |
| `interaction.proposed.v1` | `interactionProposal` in `world-interaction.v1.schema.json` |
| `interaction.outcome.observed.v1` | `interactionOutcome` in `world-interaction.v1.schema.json` |
| `representation.created.v1` / `representation.revised.v1` | `representationCreated` / `representationRevised` |
| `context.assembled.v1` / `context.invalidated.v1` | `contextSnapshot` / `contextInvalidated` |
| `environment.observed.v1` | `environmentObserved` |
| `capability.discovered.v1` / `capability.verified.v1` / `capability.invalidated.v1` / `capability.revoked.v1` | `capabilityDescriptorRecord` |
| `capability.knowledge.revised.v1` | `capabilityKnowledgeRevision` |
| `memory.recorded.v1` / `memory.retrieved.v1` | `memoryRecord` / `memoryRetrieval` |
| `belief.proposed.v1` / `belief.revised.v1` | `beliefRevision` |
| `prediction.created.v1` / `prediction.evaluated.v1` | `predictionCreated` / `predictionEvaluation` |
| `appraisal.updated.v1` / `attention.allocated.v1` / `reasoning.hypothesis.proposed.v1` | `appraisalUpdated` / `attentionAllocated` / `reasoningHypothesisProposed` |
| `decision.recorded.v1` | `decisionRecorded` |
| `goal.created.v1` / `goal.revised.v1` | `goalRevision` |
| `plan.proposed.v1` / `plan.revised.v1` / `plan.checkpointed.v1` | `planRevision` / `planRevision` / `taskCheckpointDetails` |
| `permission.evaluated.v1` / `approval.requested.v1` / `approval.decided.v1` | `permissionEvaluated` / `approvalRequested` / `approvalDecision` |
| All `operation.*.v1` lifecycle events | `operationLifecycleEvent` |
| `outcome.observed.v1` / `outcome.evaluated.v1` | `outcomeObserved` / `outcomeEvaluation` |
| `learning.update.proposed.v1` / `learning.update.accepted.v1` / `learning.experiment.completed.v1` | `learningUpdate` / `learningUpdate` / `learningExperimentCompleted` |
| `self_model.updated.v1` | `selfModelUpdated` |
| `evolution.proposed.v1` / `evolution.candidate.evaluated.v1` | `evolutionProposed` / `evolutionCandidateLifecycle` |
| `candidate.activated.v1` / `candidate.rolled_back.v1` | `evolutionCandidateLifecycle` |
| `sync.change.exported.v1` / `sync.change.applied.v1` / `sync.tombstone.applied.v1` | `syncChange` |
| `artifact.registered.v1` / `artifact.quarantined.v1` / `artifact.deleted.v1` | `artifactManifest` |
| `disclosure.recorded.v1` | `externalDisclosureRecord` |
| `retention.deletion.requested.v1` / `retention.deletion.completed.v1` | `retentionDeletionEvent` |
| `sync.conflict.detected.v1` / `sync.conflict.resolved.v1` | `syncConflictRecord` |
| `task.control.requested.v1` | `taskControlRequest` |
| `task.run.transitioned.v1` | `taskRunTransition` |
| `worker.job.requested.v1` / `worker.job.progressed.v1` / `worker.job.completed.v1` / `worker.job.failed.v1` | `workerRequest` / `workerProgress` / `workerResult` / `workerFailure` |

Payload definitions are in `schemas/domain-payloads.v1.schema.json` and `schemas/world-interaction.v1.schema.json`; exact event-to-payload and body-fixture references are also recorded in `schemas/event-registry.v1.json`. The common envelope is in `schemas/message-envelope.v1.schema.json`; provider/interface-specific capability descriptor bodies use `schemas/capability-descriptor-body.v1.schema.json`. The latter are not the universal model of possible means. Event-to-payload binding MUST be enforced by the event validator, not by a model-authored type claim. Any new event requires a new explicit mapping and compatible schema/fixture before it can be published.

Events are append-only facts. Each durable append receives an `event_sequence` from the receiving event store inside the same local transaction as the event record; producers never supply or predict it. The sequence is monotonically increasing and unique within that one event store, not a global cross-device order. Consumers persist `last_sequence` only after the corresponding state change and event receipt are committed. Duplicate `message_id` with identical content is acknowledged without a second append; the same ID with a different payload digest is a protocol-integrity error. Corrections are new compensating events with causation links; do not rewrite history to conceal a prior outcome.

Event-stream acceptance checks:
- **EV-001:** concurrent appends receive unique, monotonically increasing local sequences; a crash cannot expose a committed consumer cursor beyond committed event/receipt state.
- **EV-002:** duplicate message ID with identical digest does not create a second event or apply twice; same ID with a different digest is rejected and audited.
- **EV-003:** consumer checkpoint advances only after its owning state change and receipt commit; restart resumes after the last committed sequence without skipping or replaying side effects.
- **EV-004:** timestamps are not used as the sole ordering mechanism; causation/correlation and domain revisions are retained, and no global order is inferred across independent event stores.
- **EV-005:** every event-registry entry resolves to exactly one payload schema and at least one body fixture; event names are unique; an unknown or mismatched body is rejected before append, and a registry entry alone never enables dispatch.
- **EV-006:** world-entity, relationship, situation, affordance, interaction-proposal and outcome events preserve owner scope, provenance, revision/temporal validity and cross-record reference checks; replay cannot silently convert provisional claims or proposals into verified facts or authorization.
- **TS-001:** every accepted task control request is durably recorded as `task.control.requested.v1`; rejected/stale requests do not mutate task state.
- **TS-002:** every committed task state transition emits `task.run.transitioned.v1` in the same event-store transaction as the `task_runs` projection update.
- **TS-003:** `taskControlRequest.expected_version` must equal `task_runs.revision`; stale requests return conflict and preserve the current revision.
- **TS-004:** pause/cancel requests remain pending until a documented safe point; dispatched operations are reconciled before a task is reported cancelled.
- **TS-005:** resume requires a current checkpoint and revalidation of plan, context, capability and dependency versions; a `lost` run cannot resume before reconciliation.
- **TS-006:** `completed`, `failed` and `cancelled` are terminal task states; no transition can mutate a terminal run.
- **TS-007:** crash/replay around control acceptance or transition commit does not duplicate a state change or advance revision twice.

## 4.4 Platform-specific environment and capability payload contracts

These payload contracts describe one provider/device-specific class of observations and discovered interfaces. They do not define the general world model or enumerate the behaviours AURIONS may learn to perform. Every payload is carried inside the common envelope and remains subject to its actual owner/context scope, schema validation, sensitivity controls and authorization. Device scope is required only for device-specific records; non-device entities, actors, resources and interactions use the context-independent world-interaction contracts.

### Device/platform environment observation

Required fields:
- `observation_id`: stable UUID.
- `owner_id`, `device_id`: authenticated scope for this device-specific observation.
- `environment_scope`: declared observation boundary.
- `observed_at`, `recorded_at`: UTC timestamps.
- `source_id`, `collection_method`, `collector_version`: provenance.
- `platform_context`: versioned context containing only known device/OS/build/runtime facts relevant to the observation.
- `observed_facts[]`: typed fact references or bounded structured values; each fact carries its own source and confidence/limitations.
- `sensitivity`, `limitations[]`, `validity`: disclosure and staleness metadata.

An observation is not a capability, permission, or authorization. Missing facts remain unknown. The observer must record collection limitations and must not claim a complete view of Android.

### Discovery request and result

A discovery request carries:
- `discovery_id`, `owner_id`, `device_id`, `requested_scope`, `requested_at`.
- `source_refs[]`: references to installed/approved discovery adapters; this is an extensible provider registry, not a closed behaviour catalogue.
- `observation_refs[]`: relevant environment evidence.
- `mode`: passive metadata discovery or separately authorized active verification.
- `resource_budget`, `deadline`, `cancellation_token`.

A discovery result carries:
- `discovery_id`, `status`, `completed_at`.
- `descriptor_refs[]`, `evidence_refs[]`, `unknowns[]`, `limitations[]`.
- `provider_errors[]` with stable error category, retryability and diagnostic reference.
- `next_validity_check` or expiry guidance where supported.

Passive discovery must not trigger an unapproved side effect. Active verification is a distinct operation with its own exact-operation authorization when it can affect state.

### Capability descriptor

A descriptor is immutable for a given `capability_id + descriptor_version`. Updates create a new version; revocation, staleness and retirement are lifecycle facts, not silent edits.

Required envelope fields:
- `capability_id`: stable opaque identifier, not a hardcoded operation enum.
- `descriptor_version`: positive integer.
- `provider_id`, `device_scope`, `discovery_epoch`.
- `descriptor_schema_version`: independently versioned descriptor schema.
- `descriptor_sha256`: digest of canonical descriptor content.
- `source_ref`, `first_discovered_at`, `status`.

The descriptor body must support these extensible groups:
- `interface`: invocation contract reference, input/output schema references, transport/provider version and compatibility constraints.
- `preconditions[]`: predicates, evidence, validity scope and unknown/known state.
- `effects[]`: expected state changes, affected resources, data read/write/disclosure and possible side effects.
- `platform_requirements[]`: required Android permission/API/user-grant conditions. These are requirements, not evidence that a grant exists.
- `constraints`: availability, OS/provider version, target scope, rate/size limits, connectivity and environmental conditions.
- `risk_facts`: effect-based facts supplied to the independent risk/policy evaluator. A provider cannot assign itself a lower policy risk or choose its approval class.
- `execution`: timeout, cancellation, idempotency, retry and uncertain-outcome semantics.
- `verification`: observable postconditions, evidence sources and verification limitations.
- `resource_profile`: estimated CPU, memory, storage, network, battery and execution-time needs, each with provenance/uncertainty.
- `lifecycle`: discovery/verification state, observed validity and invalidation reason.
- `provenance`: discovery source, evidence references, timestamps, device/OS/provider context and collector version.

Unknown optional fields remain unknown, not default-true. Unsupported major descriptor schema versions are rejected safely; compatible minor extensions are preserved or explicitly reported as unsupported without inventing semantics. Descriptor content is never an authority grant.

### Capability knowledge revision

Required fields:
- `knowledge_revision_id`, `capability_id`, `descriptor_version`, `revision_number`.
- `context_scope`: device/provider/OS/app version and other evidenced conditions under which the claim applies.
- `claims[]`: typed claims about preconditions, effects, reliability, resource use, failure modes or safe composition.
- `evidence_refs[]`: each evidence reference records support/contradiction/contextualization.
- `confidence`: calibrated estimate with method and sample basis; null/unknown is permitted.
- `status`: provisional, supported, disputed, superseded or withdrawn.
- `created_at`, `supersedes_revision_id`.

A revision cannot broaden permissions, lower governance risk or create authority. A single success/failure cannot create a universal competence/prohibition. Revisions retain history and evidence lineage.

### Plan step capability reference

A plan step that proposes use of a discovered capability must reference:
- `capability_id` and exact `descriptor_version`.
- `provider_id`, target scope and input schema version.
- Parameter reference/digest, precondition references and expected effect references.
- Expected postcondition/verification criteria.
- Resource/deadline/cancellation budget.
- Relevant capability-knowledge revision references and uncertainty.

A plan reference is not a dispatch instruction or authorization. The runtime must revalidate descriptor freshness and preconditions before requesting governance evaluation.

### Exact operation proposal and execution receipt

The operation proposal must bind the exact capability ID/version, provider, target, canonical parameters/digest, expected effects, data categories/recipients, risk facts, resource/deadline limits, idempotency key and plan/goal lineage. Governance evaluates the exact proposal independently and returns an immutable decision reference; the model or provider cannot fill in or alter that decision.

The execution receipt records operation/attempt IDs, dispatch state/time, adapter/provider receipt reference, observed result, verification state/evidence, error category, cancellation/timeout state and uncertainty. A provider success response is not a verified postcondition. Dispatched-without-confirmation becomes UNCERTAIN and must be reconciled before retry.

### Error and compatibility semantics

Use the `contractError` payload. At minimum, distinguish: unsupported schema major version; malformed descriptor; unknown provider; unavailable provider; stale descriptor; missing observation evidence; missing platform grant; denied AURIONS policy; expired/mismatched approval; failed precondition; resource/deadline exhaustion; cancelled-before-dispatch; dispatch failure; dispatched outcome unknown; postcondition not verified; and provider contract violation.

`error_code` is a stable, namespaced identifier resolved through a versioned error registry, not a closed list embedded in the cognitive core. `category` identifies the failure domain; `retryable` is advisory and cannot override `side_effect_state`. `side_effect_state=unknown` or `dispatched` forbids blind retry; the operation must reconcile or enter manual intervention unless a provider-specific idempotency/reconciliation contract proves safety. Unknown error codes default to non-retryable with unknown side-effect state. Diagnostic references must point to redacted, access-controlled artifacts; `details` cannot carry secrets or grant authority.

### 4.5 Normative error taxonomy and compatibility negotiation

The error registry is extensible, but each registered code MUST declare one stable category, default retry posture, side-effect default, required reconciliation action, and whether owner/platform intervention is required. Codes are identifiers, not behavioural rules; handlers use the category and operation state to select a safe recovery path.

| Category | Representative namespaced codes | Default side-effect state | Retry/recovery rule |
|---|---|---|---|
| `contract.schema` | `SCHEMA_MALFORMED`, `SCHEMA_MAJOR_UNSUPPORTED`, `SCHEMA_CONDITION_UNSUPPORTED` | `not_dispatched` | Do not retry unchanged input; negotiate or correct the contract first |
| `provider.identity` | `PROVIDER_UNKNOWN`, `PROVIDER_UNTRUSTED`, `PROVIDER_VERSION_UNVALIDATED` | `not_dispatched` | Quarantine/revalidate provider; provider cannot self-promote trust |
| `provider.availability` | `PROVIDER_UNAVAILABLE`, `PROVIDER_RATE_LIMITED` | `not_dispatched` only when dispatch is proven absent; otherwise `unknown` | Retry only after backoff and fresh availability evidence; reconcile if dispatch may have occurred |
| `capability.validity` | `CAPABILITY_STALE`, `CAPABILITY_REVOKED`, `CAPABILITY_INCOMPATIBLE` | `not_dispatched` | Invalidate dependent plans and rediscover/revalidate; never dispatch from stale descriptor |
| `evidence.precondition` | `EVIDENCE_INSUFFICIENT`, `PRECONDITION_FALSE`, `PRECONDITION_UNKNOWN` | `not_dispatched` | Acquire evidence, re-evaluate or defer; unknown is not false |
| `platform.permission` | `PLATFORM_GRANT_MISSING`, `PLATFORM_GRANT_REVOKED` | `not_dispatched` | Require platform grant through OS flow; do not infer or synthesize it |
| `governance.authorization` | `POLICY_DENIED`, `APPROVAL_EXPIRED`, `APPROVAL_MISMATCH`, `APPROVAL_REVOKED` | `not_dispatched` | Do not retry until a new valid authorization decision exists |
| `operation.conflict` | `EXPECTED_REVISION_CONFLICT`, `DEPENDENCY_VERSION_STALE`, `IDEMPOTENCY_KEY_REUSE_MISMATCH` | `not_dispatched` unless existing operation is found | Reload authoritative revisions; same idempotency key with different canonical digest is an integrity failure |
| `operation.budget` | `DEADLINE_EXCEEDED`, `RESOURCE_BUDGET_EXCEEDED`, `CANCELLED_BEFORE_DISPATCH` | `not_dispatched` only when dispatch absence is durable | Checkpoint or replan; a new attempt requires a new explicit operation decision where scope/effects change |
| `operation.dispatch` | `ADAPTER_DISPATCH_FAILED`, `DISPATCH_RECEIPT_MISSING` | `dispatched` or `unknown` unless proven otherwise | Reconcile the target/provider; no blind retry |
| `operation.outcome` | `OUTCOME_UNCERTAIN`, `POSTCONDITION_UNVERIFIED`, `PROVIDER_RESULT_CONTRADICTED` | `dispatched` or `unknown` | Preserve evidence, perform independent observation/reconciliation, or enter manual intervention |
| `provider.contract` | `PROVIDER_CONTRACT_VIOLATION`, `PROVIDER_INTEGRITY_FAILURE` | `unknown` after dispatch; otherwise `not_dispatched` | Quarantine affected provider version; preserve receipts and reconcile possible effects |
| `runtime.internal` | `INTERNAL_FAILURE`, `STORAGE_COMMIT_UNCERTAIN` | `unknown` unless transaction rollback is proven | Recover from durable state; never infer rollback from process failure |

The machine-readable seed is `schemas/error-registry.v1.json`, governed by `schemas/error-registry.v1.schema.json`. It contains 35 representative codes across 13 extensible categories. Each entry now points to a category-owned design contract in [Error Handler Contract Matrix](ERROR-HANDLER-CONTRACT-MATRIX.md) and to one schema-shaped payload fixture in `schemas/fixtures/error-handler-cases.fixture.json`. The registry entries deliberately remain `seed`, so no handler is registered for production dispatch: the mapping is specified, but runtime handlers and code-specific recovery execution are not implemented. The fixture-set shape is governed by `schemas/error-handler-fixtures.v1.schema.json`. These defaults are advisory; the actual per-attempt state remains authoritative.

The table is the minimum registry seed, not a closed error enum. An implementation MUST retain the actual side-effect state observed for the individual attempt; it MUST NOT overwrite it with the category default. `retryable=true` is never sufficient authority to retry. Retry requires all of: dispatch state proven safe, current descriptor and policy revalidation, unchanged canonical operation digest or a newly authorized operation, valid deadline/budget, and idempotency/reconciliation contract.

#### Compatibility negotiation state machine

A producer and consumer negotiate before accepting a versioned command, query, event stream or worker job:
1. Exchange producer/consumer identity, supported envelope major/minor ranges, message-family versions and required feature identifiers.
2. Select the highest mutually supported major and a mutually supported minor under that major; required features must all be supported.
3. Reject if no common major exists, a required feature is missing, a security-relevant extension is unknown, or the peer identity/trust check fails.
4. Record the negotiated tuple, peer identities, feature set, decision, reason and timestamp as an auditable compatibility result.
5. Bind the negotiated tuple to the session/job/stream. Re-negotiate on peer restart, version change, trust/lifecycle change or schema incompatibility.

Compatibility negotiation MUST NOT silently downgrade security, authorization, integrity, encryption or side-effect guarantees. Optional extension loss may be tolerated only when the owning schema declares the extension optional and the consumer reports the loss. A successful negotiation establishes protocol compatibility only; it grants no capability, permission or authorization.

#### Command/query registry completeness gate

For every `command_type + command_version`, the registry MUST bind: request schema ID/version; response schema ID/version; owning component and aggregate; expected-revision/dependency-version requirements; state transition(s); authorization/data classification; idempotency scope and digest rules; deadline/cancellation semantics; possible side-effect state; error-code mapping; emitted event(s); persistence owner; and positive, negative, conflict, replay and recovery fixtures.

For every `query_type + query_version`, the registry MUST bind: filter/input schema; result schema; owner/device scope; data classification and field-level redaction; authorization rule; consistency mode; deterministic ordering/cursor semantics; timeout/result/byte limits; cache/freshness rules; and proof that execution is read-only.

A registry entry missing any applicable binding is **not registered for production dispatch**. The current registry now records the individual family names, payload-schema references, owner/persistence mappings and unresolved semantic bindings. It is a design inventory only; every command/query remains non-dispatchable until all applicable fields and fixtures are completed and verified. This gate prevents a generic envelope or open namespace from being mistaken for a complete application API.

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
- `PROPOSED/VALIDATING/READY → REJECTED | EXPIRED`
- `AWAITING_APPROVAL → REJECTED | EXPIRED | REVOKED | CANCELLED`
- `READY/DISPATCHED/RUNNING → CANCEL_REQUESTED`; a pre-dispatch permission revocation transitions to `REVOKED`, while a post-dispatch revocation requires outcome reconciliation.
- `RUNNING → FAILED | UNCERTAIN`
- `CANCEL_REQUESTED → CANCELLED | SUCCEEDED | UNCERTAIN`
- `UNCERTAIN → RECONCILING → SUCCEEDED | FAILED | COMPENSATION_REQUIRED | MANUAL_INTERVENTION`
- `COMPENSATION_REQUIRED → COMPENSATING → COMPENSATED | MANUAL_INTERVENTION`

Terminal states are immutable: `SUCCEEDED`, `FAILED`, `REJECTED`, `EXPIRED`, `REVOKED`, `CANCELLED`, `COMPENSATED` and `MANUAL_INTERVENTION`. Corrections are new linked operations/events. Never transition `UNCERTAIN` directly to retry.

The durable operation projection and operation-event payload use the exact 19 values in the proposed `operations.state` CHECK constraint. For state-specific events (`operation.proposed.v1`, `operation.validating.v1`, `operation.awaiting_approval.v1`, `operation.ready.v1`, `operation.dispatched.v1`, `operation.running.v1`, `operation.succeeded.v1`, `operation.failed.v1`, `operation.rejected.v1`, `operation.expired.v1`, `operation.revoked.v1`, `operation.cancel_requested.v1`, `operation.cancelled.v1`, `operation.uncertain.v1`, `operation.reconciling.v1`, `operation.compensation_required.v1`, `operation.compensating.v1`, `operation.compensated.v1`, `operation.manual_intervention.v1`), the payload `state` MUST equal the event suffix. `operation.reconciled.v1` is a reconciliation-result event; its payload `state` is the actual resulting operation state and must include reconciliation evidence. The attempt lifecycle is separate: when `attempt_state` is present, `attempt_id` and `attempt_number` are required and the state must match the `operation_attempts.state` contract. `accepted` is a command response, not an operation state; `started` is not a durable state (use `running`).

### 7.2 Operation record
The authoritative operation projection is stored in `operations`; exact immutable operation parameters and authorization context are stored in `operation_details`; each dispatch/retry is recorded in `operation_attempts`; step-level execution is tracked in `operation_steps`; cross-store recovery is tracked in `recovery_journal`. Together they persist operation ID, task/goal/plan/step lineage, owner/actor/device, capability and descriptor version, canonical parameters and digest, target, expected effects, data categories, risk class, policy version, approval reference, idempotency key, deadline, resource budget, current state, attempt number, dispatch receipt, observed result, verification evidence, timestamps and causation/correlation IDs. See proposed event/recovery migration v2 in Section 26.5.2 of the source specification.

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

## 7.5 Task-run lifecycle and scheduler control

Task-run state is a durable scheduler projection in `aurion_events.db`. Its states are `queued`, `running`, `paused`, `completed`, `failed`, `cancelled`, `blocked` and `lost`. The `revision` field is the optimistic-concurrency version for that task run. Proposed event/recovery migration v2 adds `task_runs.revision` with an initial value of 1; every committed state transition increments it exactly once.

A `taskControlRequest.expected_version` MUST equal the current `task_runs.revision`. A mismatch returns a typed conflict with the current revision and produces no state mutation. The `taskRunStatus` query projection exposes the revision. Every accepted control request emits `task.control.requested.v1` using `taskControlRequest`; every actual state transition emits `task.run.transitioned.v1` using `taskRunTransition`. The task-run projection update and its transition event are committed in one local event-store transaction. The request event may be committed before the resulting transition when the scheduler must wait for a safe point.

Allowed task-run transitions:

| Current state | Allowed next state | Constraint |
|---|---|---|
| Initial | `queued` | New run starts at revision 1. |
| `queued` | `running`, `blocked`, `cancelled`, `failed` | `task.start` may move a queued run to running only after current prerequisites and budgets are checked. |
| `running` | `paused`, `completed`, `failed`, `blocked`, `cancelled`, `lost` | Pause/cancel is cooperative. A dispatched operation must be reconciled before the task is marked cancelled or completed. |
| `paused` | `running`, `cancelled`, `blocked` | Resume revalidates checkpoint and all bound dependency versions. |
| `blocked` | `queued`, `cancelled`, `failed` | A blocker must be resolved and current dependencies revalidated before returning to the queue. |
| `lost` | `queued`, `failed`, `cancelled` | Reconcile worker/process and checkpoint state first; never resume directly from an unresolved lost state. |
| `completed`, `failed`, `cancelled` | None | Terminal states are immutable. |

`task.start` is valid only for a queued run; `task.pause` only for a running run; `task.resume` only for a paused run; and `task.cancel` for a non-terminal run. A control request can be durably accepted while its effect remains pending. In particular, cancellation does not imply that a dispatched operation stopped or was reversed. The task remains non-terminal until safe-point handling and any required operation reconciliation are complete. A blocked run returns to `queued` through scheduler readiness evaluation; a lost run requires reconciliation before it can be queued again.

The event body records the previous/current state and revision, cause, actor, time and applicable control-request, checkpoint, failure or reconciliation references. JSON Schema validates payload shape; the owning scheduler enforces legal transitions, revision increment, state-dependent evidence and the atomic projection/event commit.

## 8. Persistence, schema and transaction boundaries

### 8.1 Store ownership
- `aurion_memory.db`: experience/representation/context, memories, knowledge, evidence, beliefs, predictions, goals, plans, immutable artifact metadata/lineage, versioned discovered capability descriptors and learned capability knowledge, durable appraisal/decision/outcome summaries, self-model revisions, evolution proposals and learning metadata.
- `aurion_events.db`: event log, capability discovery/execution events, operations, operation steps, task runs/checkpoints, outbox/inbox and recovery journal.
- `aurion_governance.db`: owner/device identities and trust, policies, permission grants, approval requests/decisions, revocations, disclosure records and security audit. A capability descriptor is not a permission grant; the OS and governance authorities are rechecked independently at execution.

Each DB has its own migration ledger, backup/restore procedure, integrity check and schema version. Cross-file foreign keys are prohibited. Cross-store references use UUIDs validated by application services.

### 8.2 Transaction pattern
- A domain command writes its aggregate and an outbox record in one transaction within the owning DB.
- Outbox publisher retries until acknowledged; event ID deduplicates consumers.
- Consumer records inbox receipt and state change in one local transaction.
- Cross-store workflows use durable operation/saga state and compensating actions; never imply a distributed ACID commit.
- A write spanning governance and operation stores first obtains a signed/immutable decision reference, then writes the operation record; if either step fails, reconcile from durable audit and fail closed.
- SQLite connections use explicit transaction scopes, foreign keys within each DB, busy timeout and WAL only after target-device validation. Durability/synchronous settings must be documented and tested against power-loss expectations.

### 8.3 DDL and migration acceptance
The canonical proposed SQL is under [`schemas/persistence/`](../../schemas/persistence/README.md): three base schemas plus memory migrations v2/v3 and event/recovery migration v2. The source specification Section 26 links to these machine-readable files. Proposed minimum SQLite version is 3.38.0 (STRICT tables plus built-in JSON functions); target Termux/Android compile options remain unverified. All scripts remain unexecuted proposals. Before implementation approval:
- Parse/execute all three base schemas and all three additive migrations against the pinned minimum SQLite version.
- Enable foreign keys and verify every declared FK.
- Run schema lint for missing indexes on foreign keys, owner scope, status, timestamps, retrieval predicates and idempotency keys.
- Validate uniqueness for IDs, idempotency keys and active approval nonces.
- Test each store from empty DB and each supported prior schema version; apply memory migrations v2 then v3 and event migration v2 in order.
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
- CT-008: canonical JSON Schema files parse and validate all positive/negative shared fixtures; C++ and Python consumers use the same versioned fixture corpus.
- EV-001 through EV-006: verify store-local monotonic event sequence, duplicate message identity/digest handling, atomic consumer checkpoint advancement, causal ordering, and exact body binding/semantic lineage for the open-world event families without relying on timestamps or inventing global cross-context order.

### 10.1.1 No-hardcoding regression tests
These tests protect the governing architecture rule: mechanisms are engineered; behaviour and capability knowledge are acquired through experience. They do not prohibit explicit safety, schema, protocol or permission invariants.
- NHC-001: introduce a new schema-compatible capability provider; the discovery/representation path accepts it without adding a task-to-action branch to the cognitive core.
- NHC-002: present the same objective under different observed environments; candidate means are derived from current discovered descriptors and evidence, not a fixed objective-to-operation mapping.
- NHC-003: with incomplete discovery evidence, the system represents the capability as unknown and asks, defers or explains the limitation instead of inventing an interface.
- NHC-004: a capability failure updates evidence within its observed context and does not automatically create a universal prohibition.
- NHC-005: a successful operation does not establish universal competence, persistent permission or authority to repeat it in a different scope.
- NHC-006: removing or adding one illustrative phone-operation example does not require changing the architecture's capability model or define its capability boundary.
- NHC-007: an accepted evidence-backed strategy/capability update changes a later related task after restart and is traceable to the experience and evaluation that justified it.
- NHC-008: repeated successful actions cannot weaken permission checks, risk classification, approval requirements or owner authority.
- NHC-009: an entity/relationship based on indirect evidence remains provisional and is revised on contradiction, expiry or new evidence without rewriting source history.
- NHC-010: a human-mediated or non-device route can be considered without a device capability descriptor, provider adapter or platform-specific branch.
- NHC-011: a multi-context task preserves identity, provenance, state ownership and authority independently at each boundary.
- NHC-012: a proposed interaction cannot dispatch until the independent authority boundary approves the exact actor, targets, effects, parameters and scope.
- NHC-013: when no evidenced/authorized means is available, the system can ask, observe, wait, delegate or stop; it must not synthesize an executable route from task labels.
- NHC-014: changed world state or stale evidence invalidates dependent affordance estimates and triggers reassessment without silently changing the objective.
- NHC-015: provider receipt, independently observed effect and causal attribution are distinct; uncertain effects are reconciled before any success/learning claim.
- NHC-016: objective success criteria persist independently from derived goals/plans; replanning or execution failure cannot rewrite the requested outcome.

### 10.2 Cognitive-cycle integration tests
- CM-001 through CM-029: execute the cognitive mechanism and interaction scenarios defined in [Cognitive Mechanism and Interaction Architecture](../architecture/COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md). Preserve the exact scenario IDs, fixtures and negative controls.
- AD-001 through AD-015: execute the Android-specific observation/discovery/permission scenarios defined in [Android Platform Interaction Realization](../architecture/ANDROID-ENVIRONMENT-AND-CAPABILITY-ARCHITECTURE.md). These are platform validation tests, not tests of the general open-world means model.
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
- OP-009: every operation-state transition is accepted only if it appears in the documented transition graph; terminal states cannot be reopened.
- OP-010: operation aggregate state and attempt state remain distinct, and every attempt transition is bound to operation ID, attempt ID/number and idempotency key.

### 10.5 Persistence, sync and deletion tests
- DB-001 through DB-010: DDL, migration, constraint, disk-full, corruption, crash, restore and transaction fault tests from Section 8.3.
- DB-011: plan-step contract accepts a current versioned capability descriptor and rejects missing/stale/mismatched descriptor references; non-capability steps remain representable.
- DB-012: operation projection rejects illegal lifecycle transitions and preserves terminal-state immutability.
- DB-013: canonical operation parameter digest and capability/policy/approval references remain bound to the exact operation.
- DB-014: duplicate attempt delivery is idempotent; dispatch without receipt becomes uncertain and cannot be blindly retried.
- DB-015: learning-update details require evidence and baseline/evaluation references before acceptance; artifact lineage and rollback references remain resolvable.
- DB-016: task checkpoint detail binds the checkpoint to a plan/version, context version, capability epoch and dependency-state digest; stale or mismatched checkpoints cannot resume silently.
- DB-017: after restart, historical attention-allocation events are not restored as current truth; allocation is recomputed from current goals, tasks, context, permissions and resources.
- TS-001…TS-007: verify durable task-control requests, versioned task-run transitions, safe-point pause/cancel, stale-checkpoint rejection, lost-run reconciliation, terminal immutability and crash/replay.
- ART-001: artifact checksum and byte size are verified before metadata becomes available.
- ART-002: artifact lineage rejects self-reference and application validation rejects cycles.
- ART-003: deleting a source artifact processes derived lineage, indexes and backup/sync state.
- ART-004: byte deduplication never merges sensitivity, authorization, retention or deletion semantics.
- CAP-001: descriptor discovery does not create a permission grant or authorization.
- CAP-002: revoked/stale descriptor or platform grant blocks queued execution and triggers safe revalidation.
- CAP-003: contradictory capability-use evidence creates a scoped knowledge revision without erasing history.
- CAP-004: a new schema-compatible capability descriptor is represented without a hardcoded task-to-action branch.
- NHC-001 through NHC-016: execute the no-hardcoding and capability-extensibility regression checks defined in Section 10.7.
- SY-001: duplicate sync envelope applies once.
- SY-002: out-of-order causal change is buffered/rejected safely.
- SY-003: conflict retains both versions and provenance.
- SY-004: tombstone reaches online device and removes active retrieval.
- SY-005: offline stale device cannot resurrect deleted content.
- SY-006: restore replays tombstones before exposing content.
- SY-007: revoked device cannot sync or execute.
- SY-008: direct SQLite file replication is absent.

### 10.6 Local cognitive/action acceptance subset (not the full dual-context release)
This local cognitive/action acceptance subset is necessary but is not, by itself, acceptance of the complete first release. The complete first release must also pass the cloud/offline-mobile integration acceptance protocol PR-15 through PR-18 in the product definition and canonical roadmap. The local subset is accepted only when:
1. Fresh install and restart preserve the same local owner/system identity under the documented recovery model.
2. A conversation creates durable, provenance-linked experience records.
3. A later session retrieves relevant memory and cites its source internally.
4. A bounded objective can be represented as a plan with dependencies, budget and cancellation.
5. At least one narrowly scoped owner-approved local interaction is executed through the applicable programmatic boundary after policy evaluation; the exact first action remains an owner decision.
6. The system records dispatch receipt, observed outcome and verification evidence.
7. A restart at each operation transition recovers or reconciles without duplicate side effects.
8. An explicit denial is enforced even if the model recommends execution.
9. Offline core workflows remain available without external services.
10. A paired evaluation demonstrates outcome-sensitive later behaviour; separate held-out learning tests are required for claims of general learning improvement.
11. Data export/deletion and backup restore behave according to documented policy.
12. Test suite, build revision, environment and evidence artifacts are reproducible.

### 10.7 No-hardcoding and capability extensibility tests

These tests protect the foundational rule that mechanisms are engineered while behaviours and capability knowledge are discovered or acquired from evidence. They do not prohibit deterministic safety constraints, schemas, protocols, type checks, resource limits or governance enforcement.

- **NHC-001 — New provider without planner patch:** introduce a schema-compatible provider and capability descriptor fixture; the generic discovery/registry/planning path can represent and consider it without adding a task-specific branch or changing the cognitive core.
- **NHC-002 — Environment-dependent candidate generation:** hold the objective constant while changing the discovered environment/capability evidence; candidate means and feasibility must respond to the evidence rather than a fixed objective-to-operation mapping.
- **NHC-003 — Unknown remains unknown:** remove required descriptor evidence or provide an unsupported major schema version; the system must not infer an interface, permission, precondition or successful outcome.
- **NHC-004 — Scoped evidence update:** capability success/failure updates only the supported device/provider/version/context scope; it must not become universal competence or prohibition without evaluation.
- **NHC-005 — Learned update cannot alter authority:** apply a candidate capability/strategy update and verify that permission, risk, approval, owner authority and execution-gateway checks remain unchanged.
- **NHC-006 — No fixed stimulus-response substitute:** review fixtures and implementation paths for developer-authored stimulus-to-emotion/action, success/failure-to-reward, or task-to-action mappings presented as learned cognition; reject any such path unless it is an explicitly approved deterministic safety invariant.
- **NHC-007 — New capability regression:** add a compatible capability descriptor after the planner and core are built; the system must process it through generic contracts without recompiling a task catalogue or adding a task-specific dispatch branch.
- **NHC-008 — Evidence-based strategy adaptation:** after a scoped strategy update passes its evaluation gate, a later related task must show the expected change; related unseen variations and unrelated regression controls must be included.

NHC-006 requires architecture/code review plus targeted static searches and behavioural fixtures; a text search alone is not proof of absence. Record inspected paths, exceptions, reviewer, revision and evidence. NHC-001…NHC-016 are required planning acceptance tests and remain unvalidated until executed against implementation.


### 10.8 Security, key lifecycle and supply-chain tests

These tests are infrastructure/security acceptance checks, not behavioural rules. They must use isolated test keys, fake platform/KMS adapters and non-production data until platform validation is authorized.

- **SEC-001 — Key provenance and platform backing:** keys are generated from the platform cryptographic RNG; Android Keystore hardware-backed/StrongBox capability is queried and recorded as evidence, never assumed. A software-backed fallback is explicitly identified and cannot be reported as hardware-backed.
- **SEC-002 — Key separation:** owner identity, per-device identity, data-encryption, transport/session and code-signing key domains are distinct. A key or grant from one domain cannot decrypt or authorize another.
- **SEC-003 — Envelope encryption and rotation:** domain/artifact data-encryption keys are wrapped by versioned platform/cloud key-encryption keys. Rotation/re-wrapping is crash-safe, idempotent and auditable; old key versions remain available only for the documented transition/recovery window.
- **SEC-004 — Device revocation:** revoking a device invalidates future authentication, sync and operation authorization. A disconnected device cannot resurrect deleted data or resume privileged work when it reconnects.
- **SEC-005 — Key loss and recovery:** missing, corrupt, revoked or unsupported keys fail closed. Recovery is available only through a separately configured owner-controlled recovery path; no hidden export, universal recovery key or model-authorized bypass exists.
- **SEC-006 — Backup/restore:** backups contain ciphertext and required non-secret metadata, not plaintext key material. Restore verifies integrity and key availability, replays deletion tombstones before exposing data, and records any unrecoverable domain explicitly.
- **SEC-007 — Update and artifact signing:** release/update manifests and protected model/runtime artifacts are verified against versioned trust roots; tampered, unsigned, revoked-key or unauthorized rollback packages are rejected and audited.
- **SEC-008 — Log and telemetry minimization:** secrets, raw private observations, authentication material and unapproved sensitive payloads do not appear in logs, crash reports or telemetry; field-level redaction and secret scanning are tested.
- **SEC-009 — Cloud key-service failure:** unknown key versions, KMS outage, revoked cloud credentials or failed unwrap operations deny protected cloud access; local offline operations remain limited to locally available keys and local authorization.
- **SEC-010 — Worker isolation:** a compromised Python worker cannot read production keys, write live cognitive/governance databases, change policy or activate artifacts; output is bounded, schema-validated and quarantined before an authorized integration path.
- **SEC-011 — Data-egress boundary:** prompts, provider requests, sync payloads and diagnostics contain only authorized data categories/recipients; sensitive external disclosure requires the exact-operation approval and durable audit path.

These checks are **SPECIFIED**, not executed. Platform-specific cryptographic provider selection, hardware-backing claims, recovery semantics and KMS integration remain subject to the actual Android/Termux and cloud deployment evidence.

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


### 11.6 Key hierarchy, data protection and validation boundaries

The following is the proposed mechanism boundary; it does not select a cloud vendor or claim a target device supports every feature.

- Keep owner identity keys, per-device identity keys, data-encryption keys (DEKs), key-encryption keys (KEKs), transport/session keys and update/artifact signing keys in separate roles and trust domains.
- Use envelope encryption for durable data and artifacts. Separate DEK scopes for memory, events, governance and artifact content; store only ciphertext, key-version identifiers and non-secret metadata in SQLite. Never derive encryption keys from device IDs, account IDs or other public identifiers.
- Device KEKs/private identity keys are held through an Android Keystore-backed native boundary when available. Query and record hardware-backed/StrongBox status. Termux is not assumed to have direct Keystore access; a native bridge/companion boundary and actual API/ABI tests are required. A software-backed fallback, if later approved, must be explicitly labelled and must not claim hardware protection.
- Cloud KEK operations use a provider-independent interface. No cloud KMS provider, account, region or key hierarchy is selected in this planning phase. Cloud key access must be tenant/owner scoped and independently authenticated.
- Rotation is versioned and event-audited. Rotation may be triggered by compromise, revocation, key age/algorithm policy or owner action; no arbitrary fixed interval is imposed here. Re-wrapping must be crash-safe and preserve recovery for still-authorized data.
- Backups contain encrypted data and key-version metadata only. Recovery material, if offered, must be configured and controlled by the owner, stored separately from the backup and tested without creating a universal bypass. Without a valid recovery path, key loss may make encrypted data permanently unavailable; the system must fail closed and disclose this.
- Revocation blocks new sessions and remote operations, and key rotation/re-wrapping removes access for revoked devices where the storage model permits. Offline revocation cannot be enforced until the device reconnects; this residual risk remains explicit.
- Update-signing trust roots are distinct from model-generated artifacts and ordinary device identity keys. A model/worker cannot create or replace a production trust root or authorize its own candidate.

**Validation boundary:** SEC-001…SEC-011 require host fakes plus actual platform/cloud integration tests. Android Keystore hardware backing, Termux bridge feasibility, secure backup/restore, KMS outage/revocation, signing-key rotation and device-loss recovery are not validated by schema or documentation checks.


### 11.7 Provider-independent key-service boundary and trust/data-flow contract

This section makes the provider-independent boundary explicit. It is a design contract only: it selects no cloud KMS, Android bridge, recovery provider, cryptographic library or production key policy.

#### Key-service interface responsibilities

The runtime depends on a narrow key-service abstraction. Domain code MUST NOT call a vendor SDK or platform keystore API directly.

| Operation | Input authority and scope | Required result | Failure rule |
|---|---|---|---|
| `describe_key` | Authenticated internal caller; opaque key reference | Key ID/version, purpose, algorithm identifier, provider class, backing evidence and lifecycle state; never key bytes | Unknown/unavailable metadata is an error, not an inferred default |
| `generate_data_key` | Authorized domain + data-classification scope + algorithm policy | Fresh DEK material for immediate in-memory use plus wrapped DEK and opaque KEK reference/version | No plaintext DEK persistence; fail closed if wrapping cannot complete |
| `unwrap_data_key` | Authenticated workload, exact owner/domain and ciphertext key-version reference | DEK only for the authorized operation and bounded lifetime | Deny on owner/domain mismatch, revoked/unknown key, provider outage or policy failure |
| `rewrap_data_key` | Authorized rotation/recovery job with source and destination key versions | New wrapped DEK plus durable old/new version lineage | Idempotent and resumable; do not delete old wrapping until verified completion and retention gate |
| `sign` / `verify` | Purpose-bound signing key and canonical manifest/message digest | Signature or verified identity/key-version evidence | Signing keys cannot be used for data decryption or owner authentication |
| `revoke_key` | Governance-authorized revocation command with reason and scope | Durable revocation receipt and effective-state evidence | Revocation cannot be inferred from timeout; uncertain provider result requires reconciliation |
| `create_recovery_package` / `restore_recovery_package` | Explicit owner-configured recovery policy and separately authenticated recovery actor | Encrypted recovery metadata and verifiable restore result | No implicit recovery, hidden escrow, universal bypass or model-initiated recovery |

All methods use opaque references, typed errors, bounded deadlines and audit correlation IDs. Provider-specific metadata is retained as evidence, not treated as authority. The interface MUST expose whether a key is hardware-backed, software-backed, remote, unknown or unsupported; it MUST NOT collapse these states into a boolean "secure" flag.

#### Trust-boundary and data-flow map

| Boundary | Data crossing it | Mandatory control | Owner / enforcement point |
|---|---|---|---|
| Model/inference output → cognitive core | Generated text, tool suggestions, candidate plans | Treat as untrusted content; validate typed structure; no identity, policy, key or approval authority | Cognitive ingress + governance |
| UI/CLI → application API | User requests, session identity, query/command payloads | Authenticate session; derive owner/actor from trusted session; reject caller-supplied scope escalation | Auth/session boundary |
| Cognitive core → governance | Exact proposed operation, target, effects, risk, evidence | Governance independently evaluates current policy, grants, expiry and approval; core cannot self-authorize | Governance service |
| Runtime → local key provider | Opaque key references, bounded cryptographic requests | Narrow IPC/API; caller identity and purpose binding; no raw key export; platform backing reported from observed evidence | Local key adapter |
| Runtime → cloud key provider | Owner-scoped key operation, authenticated workload identity | Mutual/service authentication, tenant isolation, least privilege, bounded request and audit; no device authority transfer | Cloud key adapter |
| Domain store ↔ encryption layer | Plaintext only inside authorized process boundary; ciphertext + key metadata at rest | Separate DEK scopes for memory/events/governance/artifacts; authenticated encryption; integrity checked before use | Storage/encryption boundary |
| Python worker ↔ supervisor | Job-scoped inputs and candidate artifacts | No production key handles or live DB credentials; bounded IPC; schema validation; quarantine before integration | Worker supervisor |
| Runtime → backup/export | Ciphertext, non-secret metadata, tombstones and version references | Owner policy, integrity manifest, backup epoch; recovery material stored separately | Backup/retention service |
| Build/release pipeline → runtime | Signed binaries, manifests and protected artifacts | Pinned source provenance, separate update-signing trust root, signature and rollback verification | Release verifier |
| Runtime ↔ external provider/sync peer | Explicitly classified payloads and authenticated change records | Recipient allowlist/policy, minimum disclosure, replay protection, durable receipt and deletion semantics | Egress/sync boundary |

No trust boundary may be bypassed by a model-generated instruction, provider response, worker artifact, cached permission or technical possession of a key reference. A key reference is not a grant. A successful cryptographic operation is not proof that the underlying business operation was authorized.

#### Host-fake contract test procedure

Before platform integration, a deterministic host test harness MUST supply fake local-key, cloud-key, identity, clock, audit, backup and signing adapters. The fakes MUST expose controllable states (available, unavailable, revoked, unknown version, wrong owner, wrong purpose, delayed response, duplicate response, corrupt ciphertext, partial rotation and uncertain commit) and record every call. Test keys and payloads MUST be synthetic and isolated from production credentials.

| Test group | Injected condition | Required assertion | Linked acceptance |
|---|---|---|---|
| Key provenance | Hardware status unknown; software fallback selected | Report exact backing class; never claim hardware backing without provider evidence | SEC-001 |
| Separation | Attempt to use identity/signing/transport key as data DEK or across owners/domains | Deny; no cross-purpose or cross-owner decryption/authorization | SEC-002 |
| Envelope and rotation | Duplicate rotation request; crash before/after rewrap commit | One effective version transition; resumable lineage; old key retained until verified completion | SEC-003 |
| Revocation | Revoke while disconnected; reconnect with stale session/queued operation | Reject future privileged work after revocation is observed; preserve offline enforcement limitation | SEC-004 |
| Recovery | Missing, corrupt, revoked key; unconfigured recovery actor | Fail closed; no hidden export or fallback key; report unrecoverable scope | SEC-005 |
| Backup/restore | Corrupt manifest, unavailable KEK, stale backup with tombstone | Verify before exposure; replay tombstones first; expose no plaintext key material | SEC-006 |
| Signing | Unsigned, tampered, revoked signer or rollback manifest | Reject and audit; model/worker cannot add trust root | SEC-007 |
| Logging | Inject secret-like values and private payload markers | Assert absence from logs, diagnostics, crash metadata and telemetry | SEC-008 |
| Cloud key failure | Timeout, denied credential, unknown version, failed unwrap | Deny protected cloud access; do not fall back to a different owner/key; local path remains independently scoped | SEC-009 |
| Worker compromise | Worker attempts key access, DB mutation, policy update or candidate activation | Access denied; output quarantined and bounded | SEC-010 |
| Data egress | Unapproved recipient/category, stale approval, digest mismatch | Deny transmission; durable audit of decision; no sensitive bytes emitted | SEC-011 |

Each test report records source revision, fake-adapter configuration, synthetic key IDs (never key material), request digest, injected fault, observed calls, durable state before/after, expected/actual result and log-redaction result. A passing fake test establishes interface behaviour only; it does not establish Android Keystore, cloud KMS, secure hardware, OS isolation or production cryptographic correctness.

#### Explicit implementation and owner gates

- The cloud key provider, account/tenant mapping, region, recovery custodian and production recovery policy remain unselected. Selecting them requires the applicable owner/security approval.
- Android Keystore access from the Termux runtime requires an evidenced native bridge/companion boundary and target-device testing. No software fallback is silently enabled by this specification.
- Algorithm suites, nonce strategy, KDF parameters, key lifetimes and cryptographic library versions must be selected by a qualified security implementation review against supported providers; this document intentionally does not invent those parameters.
- Production key generation, encryption, signing, revocation, backup/restore and recovery controls remain NOT IMPLEMENTED until real adapters and independent security tests exist.

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


### 12.1 Current dependency inventory and JSON Schema validator evaluation

**Observed WP-00 scaffold inventory (PR #1, inspected on 2026-11-12):**
- The scaffold has no third-party C++ runtime library dependency. It uses the C++ standard library, CMake/CTest and a single version smoke test.
- Its CI workflow uses `actions/checkout@v4` by major tag and `ubuntu-latest`; neither the action commit nor runner image is immutable. This is a reproducibility/supply-chain gap to address when WP-00 is reconciled after planning approval.
- No SQLite library/version, JSON Schema validator, C++/Python contract generator, Python runtime package or model runtime is currently selected/pinned by the scaffold.
- C++20 is explicitly provisional; target Termux/Android compiler and build evidence remain outstanding.

**Validator status — split by execution boundary:**

- **Adopted for Python-host CI:** pinned `jsonschema[format]==4.26.0`, installed from `requirements-validation.txt`, executed by `scripts/validate_schemas.py` in `.github/workflows/schema-validation.yml`. On final planning PR revision `0332792bc3f3c1793885d6fb5f8a0def9d392305`, workflow run [43288993781](https://github.com/methaneex-oss/AURIONS/actions/runs/43288993781) passed the Draft 2020-12 schema/fixture validation and governance integrity steps. The corpus result recorded in [Schema Validation Results](../reviews/SCHEMA-VALIDATION-RESULTS-2026-11-12.md) is 8 schema meta-schema checks, 7 registry/fixture pairs, 78 positive domain payloads and 29 negative controls.
- This adoption is limited to Python-host schema/fixture validation. It does not establish C++ validator equivalence, Android/Termux feasibility, C++/Python serialization conformance, runtime command/query semantics or production handler readiness.

**C++/shared-evaluator candidate — proposed, not adopted:**
- C++ boundary: Corvus JSON Schema C ABI release `capi-v0.1.7`, tag commit `150e755760a0b318e7f0aa5c57d7522e79af612c`, using its header-only C++ wrapper.
- Shared evaluator: Corvus Rust crate `corvus-json-schema` version `0.2.2`; the C API crate is version `0.1.7`, edition 2024, and declares Rust 1.89 as its minimum.
- Python worker/test binding: `corvus-json-schema-rs` version `0.2.2`, backed by the same Rust evaluator. The pure-Python `corvus-json-schema` package is a separate implementation and is not the proposed pairing.
- Project license: Apache-2.0. The published C API release contains Linux aarch64 GNU and musl packages, but no Android/Bionic target package. The Python binding's published wheel matrix likewise does not list Android. A source build/cross-compile for the actual Android/Termux target is therefore a mandatory feasibility gate, not an assumed capability.
- The C API release includes a third-party notice for Unicode-derived tables under Unicode License 3.0. The complete transitive crate/license/SBOM inventory and exact package hashes must be captured before adoption.
- The evaluator advertises JSON Schema Draft 2020-12 support and reports conformance against the official JSON-Schema-Test-Suite/Bowtie. These upstream claims are candidate-selection evidence, not AURIONS integration or target-device test results.

**Decision on schema-to-code generation for the initial contract baseline:**
- No generator is selected for the first implementation baseline. C++ interfaces and Python worker message types will be explicit, reviewed boundary types; the versioned JSON Schemas remain the wire-format validation authority.
- Rationale: capability descriptors and provider-defined extensions are intentionally open-world. Generating closed enums or assuming all extension properties are statically known would create pressure to encode the current fixture set as the capability boundary. Explicit adapters must preserve unknown compatible extension data while keeping authority-sensitive fields closed and validated.
- C++/Python conformance will be enforced by running the same positive/negative fixture corpus through both bindings. If hand-maintained adapters produce measurable drift, evaluate a generator against the actual schemas and require unknown-field preservation and Draft 2020-12 compatibility before adoption.

**Remaining C++ candidate adoption gates (not passed):**
1. Build the Corvus C API and Python binding from pinned sources for host and target Android/Termux; record compiler, Rust, NDK/ABI and package hashes.
2. Verify external `$ref` resolution, format assertion, regex/resource limits, error reporting and recursion/resource limits against the AURIONS schemas.
3. Run the required official JSON-Schema-Test-Suite subset and the complete AURIONS positive/negative corpus through both C++ and Python bindings; compare normalized results.
4. Produce Cargo/Python dependency inventories, license notices, SBOM, vulnerability scan and reproducible offline rebuild.
5. Decide whether the C++ candidate is suitable only after target and licensing evidence is available. The existing Python-host CI remains in place and does not depend on adoption of this candidate.

The Python-host validator is adopted and CI-enforced for its stated scope. The Corvus evaluation remains a reasoned C++ candidate recommendation, not a final dependency approval or completed license/security audit. Sources inspected: `https://github.com/corvus-dotnet/Corvus.JsonSchema`, release `https://github.com/corvus-dotnet/Corvus.JsonSchema/releases/tag/capi-v0.1.7`, and `https://json-schema.org/specification`.

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

The former WP table in this section is superseded because it did not align with the original engineering specification and deferred Android device integration despite the owner's concurrent offline-mobile first-release direction.

The single current work-package baseline is [Canonical Implementation Roadmap](CANONICAL-IMPLEMENTATION-ROADMAP.md). It defines WP-00 through WP-16, dependency relationships, first-release integration targets, deliverables and exit criteria. The roadmap remains a proposal and does not authorize implementation.


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
3. **Android platform realization:** the examples (app launch, volume adjustment and file handling) are illustrative only, not an exhaustive capability list, fixed scope or selected first action. Planning must define the general objective/world/means reasoning independently of platforms, then specify Android observation, Android-specific discovery, platform permission integration and empirical feasibility under that model. No fixed operation catalogue may be inferred from the examples.
4. Numeric performance/latency/resource thresholds after device baselines.
5. Any change to protected authority, privacy, external disclosure or risk tolerance.

The first-interface and deployment directions are owner-decided. The foundational open-world interaction architecture and its first schema/persistence mapping remain IN PROGRESS; Android is one separate platform-specific realization. Implementation authorization and the planning exit remain separate owner gates. See PLANNING-COMPLETION-REGISTER.md for authoritative status.

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


### 4.2.3 Task-control command contract (builder closure candidate)

This section narrows the four scheduler controls to their actual target: one owner-scoped task run in `aurion_events.db`. These commands do not select a device, provider, external capability or arbitrary task-owned action. They change scheduler state only. Any operation already dispatched by the task retains its own operation/attempt state and authorization; task control cannot erase, reverse or declare that external effect cancelled.

#### Target and authority

- The payload `task_run_id` is the sole target selector. The handler MUST load that exact row and require `task_runs.owner_id = commandEnvelope.owner_id`. A missing, NULL-owner or mismatched row is denied without disclosing whether another owner's row exists.
- `actor_identity` MUST be authenticated. The governance decision MUST establish that this actor is the owner principal or has an active owner-authorized grant for the exact scheduler-control operation and task-run scope. An authenticated identity string alone is not authority.
- These commands have no device target and no requested external capability. They MUST NOT inherit device permissions or capability grants merely because the task may later invoke provider-backed operations.
- The task-control authorization decision is evaluated at execution time, after envelope validation and before the task-run mutation. Expired approval, revoked grant, owner mismatch or policy denial prevents the transition.
- The control request's reason is audit context, not authority and not a substitute for a policy decision.

#### Revision and transition invariants

- `expected_version` MUST equal the current `task_runs.revision`; otherwise return a conflict and do not append a transition event or mutate the projection.
- A committed transition increments revision by exactly one. The transition event's `previous_revision` and `revision` MUST match the before/after row values.
- The scheduler MUST apply the legal transition table defined by the task-run lifecycle contract; this command family does not permit arbitrary state assignment. Terminal states remain terminal.
- Pause and cancel are requests, not proof that an in-flight operation stopped. If the task is at a safe point, the scheduler may commit the transition. Otherwise it records a pending control request and continues to expose the actual task and operation states. A dispatched or unknown operation is reconciled independently before any claim that its effects are cancelled.
- Resume requires a valid checkpoint and revalidation of plan, context, discovered means and dependency revisions. A lost run requires reconciliation before resume.
- A rejected, stale, unauthorized or expired request does not mutate the task projection. An accepted-but-pending request is not a committed task transition.

#### Idempotency and replay

For `task.start`, `task.pause`, `task.resume` and `task.cancel`, the deduplication key is unique within:
`(owner_id, actor_identity, command_type, command_version, idempotency_key)`.

The request digest is SHA-256 over RFC 8785 JSON Canonicalization Scheme bytes for the semantic command tuple:
`owner_id`, `actor_identity`, `command_type`, `command_version`, `operation_id`, `deadline`, `requested_capability`, `data_classification`, `approval_reference`, and the exact validated command payload. Exclude transport-attempt fields `command_id`, `issued_at` and `idempotency_key`; the key is already part of the unique scope. Do not normalize, reorder or reinterpret payload strings beyond RFC 8785 canonicalization.

- First use reserves and commits the receipt in the same local SQLite transaction as the durable control-request event and outbox record. If the request can transition immediately, the task projection update and immutable transition event are included in that same transaction. If it must wait for a safe point, the pending request remains durable and the later task projection update plus transition event commit together in a separate transaction.
- Same scoped key and same digest returns the stored original command response and does not reapply the transition or emit another event.
- Same scoped key and different digest is rejected as `operation.conflict.IDEMPOTENCY_KEY_REUSE_MISMATCH`; it must not reveal or overwrite the original response.
- A crash before transaction commit leaves neither the receipt nor the transition committed. A crash after commit replays the stored response on retry. There is no cross-database atomicity claim.
- Receipts remain available for the task's deduplication lifetime. Deletion/retention must preserve a tombstone or equivalent key+digest evidence for at least the maximum supported retry/replay horizon; that horizon and deletion procedure remain an explicit persistence acceptance gate.

#### Persistence and transaction boundary

Migration `aurion_events.migration_v3.sql` adds nullable owner binding for legacy task rows, an insert trigger requiring ownership for new rows, and `task_command_receipts`. Existing rows remain unbound; ownership MUST be populated only from authoritative provenance. A NULL owner row cannot be controlled. The receipt ledger intentionally has no task-row foreign key so task deletion cannot silently erase replay evidence.

For a task-control request whose effects are wholly local to the event store, the receipt, `task.control.requested.v1` event and outbox insertion MUST commit in one transaction. When the control can be applied immediately, that transaction also includes the task-run revision update and `task.run.transitioned.v1` event. When it must wait for a safe point, the request/receipt are committed as pending; the later task-run revision update and transition event commit atomically in a separate transaction. Event publication is asynchronous from the committed outbox. A task-control transaction MUST NOT perform provider I/O while holding the SQLite write transaction.

#### Acceptance cases to implement and execute

| Case | Given / action | Required assertion |
|---|---|---|
| TC-001 | Authenticated owner controls an owned queued task with matching revision | Exactly one legal transition; revision +1; one transition event; one receipt; outbox row committed atomically. |
| TC-002 | Owner A targets owner B's task | Denied without state mutation, event append or existence disclosure. |
| TC-003 | Actor has no active exact-scope grant | Denied; an identity string or task payload cannot self-authorize. |
| TC-004 | Expected revision is stale | Conflict; no revision increment, transition event or side effect. |
| TC-005 | Same idempotency scope and digest is replayed | Original response returned; no second transition/event/outbox effect. |
| TC-006 | Same idempotency scope but different digest | Collision rejected; original receipt unchanged; no transition. |
| TC-007 | Crash injected before local transaction commit | No receipt, projection transition, transition event or outbox row survives. |
| TC-008 | Crash injected after local transaction commit but before publication | Retry returns stored response; outbox publishes once logically; projection revision does not increment again. |
| TC-009 | Pause/cancel arrives while a provider operation is dispatched or unknown | Task control remains pending at safe point; operation is reconciled independently; no false cancelled-success claim. |
| TC-010 | Resume uses stale checkpoint/plan/context/means/dependency revision | Resume rejected or deferred; no running transition until revalidation succeeds. |
| TC-011 | Legacy task row has NULL owner_id | Control denied; no inferred owner assignment. |
| TC-012 | Task is terminal | No further state transition; replay of a prior accepted request returns its stored response only. |

#### Per-command acceptance assertions

The shared TC cases above cover owner/actor authorization, optimistic concurrency, idempotency receipts, digest collisions, transaction crash boundaries and terminal immutability. The following assertions make the legal effect of each command explicit; they are design acceptance criteria, not evidence of an implemented handler.

| Command | Valid source state and required positive assertion | Command-specific negative/pending assertion |
|---|---|---|
| task.start | Only a queued task run may start. With current prerequisites, current dependency revisions and sufficient remaining budget, commit queued → running exactly once; increment revision by one and persist the transition event with the projection. | Running, paused, blocked, lost or terminal runs cannot be started by this command. Unresolved prerequisites or exhausted budget cannot produce running; preserve the projection and return a typed blocked/precondition result. |
| task.pause | Only a running task run may be paused. At a scheduler safe point, commit running → paused exactly once with revision +1 and the matching transition event. | If an operation is in flight or the scheduler is not at a safe point, durably accept the control request as pending without claiming paused or changing the operation's state. A stale revision or non-running source state cannot mutate the projection. |
| task.resume | Only a paused task run may resume. Require a valid current checkpoint and revalidate plan, context, discovered-means and dependency revisions before committing paused → running exactly once. | A lost run cannot resume directly. Missing/stale checkpoint or changed dependency revisions reject/defer the request without a running transition. Resume cannot recreate a completed, failed or cancelled run. |
| task.cancel | Any non-terminal task run may receive a cancellation request. At a safe point with no unresolved dispatched/unknown operation, commit the legal cancellation transition exactly once. | A dispatched/unknown operation keeps cancellation pending until independently reconciled; do not report cancelled, erase the operation, or imply reversal before evidence. Terminal runs remain immutable; cancellation cannot rewrite completed/failed/cancelled history. |

Per-command replay assertions: for each of the four commands, repeat the same scoped key and canonical digest and assert the original response is returned without another request/transition event or revision increment; reuse that key with a different digest and assert collision rejection without disclosing or altering the original receipt. Inject failure before local transaction commit and after commit/before outbox publication for each command path; assert atomic rollback in the first case and receipt/outbox replay without duplicate transition in the second. These are required test cases, not a blanket assumption that one command's test proves another command's state-dependent branch.

**Evidence boundary:** These are specified acceptance cases, not executed runtime tests. The proposed migration is not executed. Task controls remain `design_only_not_dispatchable` until migration execution, lifecycle table reconciliation, executable tests, and builder review pass.
