# Command Transition, Authority and Recovery Contract Matrix

**Status:** Builder contract proposal; no owner-approved first-release API scope and no runtime dispatch authorization.  
**Scope:** BR-001 — 43 mapped command entries. The two device pairing/revocation entries remain deferred.  
**Normative distinction:** A command requests a domain transition. Acceptance is not completion; a proposal is not authorization; a provider receipt is not an observed outcome.

## 1. Shared command execution contract

### 1.1 Authentication and authorization

The receiver derives `owner_id`, actor identity and device identity from the authenticated execution context. Payload values cannot substitute those identities or widen scope. The owning component loads the exact target aggregate under owner scope before exposing whether it exists. Missing, unbound or cross-owner records are denied without existence disclosure.

Authorization is evaluated at execution time, not at plan/proposal time. The enforcement decision independently checks owner/actor grant, resource/target scope, data categories, capability availability and version, policy version, expiry, budgets, approval binding, current OS permission and revocation. The model's risk estimate is advisory. Effective risk is derived by the enforcement boundary from the concrete target, data, recipient and effect; the highest applicable class governs. If risk, owner, capability, policy or approval is unknown, deny or require a new owner decision. A capability descriptor is not a grant.

### 1.2 Aggregate revision and transaction rules

- Immutable append-only records (experience observations, evidence, prediction evaluations, appraisal/reasoning assessments, decisions and outcome evaluations) append a new immutable record and retain source lineage. They do not overwrite prior evidence.
- Mutable aggregate heads (representations, contexts, capabilities, beliefs, goals, plans, operations, approvals, task runs and active artifact pointers) require an expected aggregate revision or dependency-version precondition. A committed mutation advances the authoritative aggregate revision exactly once.
- A create command must reject duplicate immutable IDs and bind the created record to the authenticated owner. A revise/control command must load the current owner-scoped aggregate and validate its allowed source state before mutation.
- Aggregate mutation and its immutable event/outbox record commit in one transaction in the owning database. No provider/worker I/O occurs while holding a SQLite write transaction. Cross-store work uses a durable operation/saga and reconciliation; there is no distributed ACID claim.
- Rejected, stale, unauthorized, expired or precondition-failed commands produce no domain mutation or success event. Any audit-denial record is a separately scoped governance audit action, not a partial domain transition.

### 1.3 Idempotency, deadline and cancellation

For every command, the receipt uniqueness scope is:
`(owner_id, actor_identity, command_type, command_version, idempotency_key)`.

The request digest is SHA-256 over RFC 8785 JSON Canonicalization Scheme bytes for the semantic command tuple: owner, actor, command type/version, operation ID, deadline, requested capability, data classification, approval reference and exact validated payload. Transport attempt fields `command_id`, `issued_at` and `idempotency_key` are excluded from the digest; the key is already part of the unique scope.

- Same scope + same digest returns the original stored response and MUST NOT repeat mutation, event, outbox insertion, worker launch or provider dispatch.
- Same scope + different digest returns `operation.conflict.IDEMPOTENCY_KEY_REUSE_MISMATCH`; it does not disclose or alter the original receipt.
- Expired deadline is rejected before any side effect. Deadline after local commit does not erase a committed result; retry replays the receipt.
- Pure local transitions may be cancelled only before commit. After commit, correction is a new linked transition, not rollback fiction.
- Worker cancellation is cooperative and must preserve job/attempt state. External operations use the operation lifecycle; after dispatch or uncertain dispatch, cancellation/retry requires reconciliation and cannot imply reversal.
- Receipt retention must outlive the supported retry/replay horizon. Deletion must preserve a key+digest tombstone or equivalent evidence for that horizon.

### 1.4 Shared typed errors

Every command validates schema/version before mutation. The common applicable error family is:
- `contract.schema.SCHEMA_MALFORMED`, `contract.schema.SCHEMA_MAJOR_UNSUPPORTED`, `contract.schema.SCHEMA_CONDITION_UNSUPPORTED`
- `governance.authorization.POLICY_DENIED`
- `operation.conflict.EXPECTED_REVISION_CONFLICT`, `operation.conflict.DEPENDENCY_VERSION_STALE`, `operation.conflict.IDEMPOTENCY_KEY_REUSE_MISMATCH`
- `operation.budget.DEADLINE_EXCEEDED`, `operation.budget.RESOURCE_BUDGET_EXCEEDED`, `operation.budget.CANCELLED_BEFORE_DISPATCH`
- `runtime.internal.STORAGE_COMMIT_UNCERTAIN`, `runtime.internal.INTERNAL_FAILURE`

Domain-specific provider, capability, evidence, platform-permission, approval and operation errors are added only where the command can encounter those conditions. The registry must bind the exact subset per command; this shared list is not a substitute for per-entry error mapping. Unknown commit outcome is not retried blindly: read the receipt/aggregate and reconcile.

## 2. Per-command transition contract

The following table defines the intended state effect and event boundary for each mapped command. Event names are the existing event-registry names; where the command/event relationship is not yet unambiguously supported by a dedicated payload or state contract, it is explicitly marked unresolved rather than guessed. Every event remains design-only/non-dispatchable until handler ownership, exact body schema, error mapping, fixture and transaction tests are complete.

| Command | Owning aggregate and transition | Event boundary | Side-effect / recovery classification |
|---|---|---|---|
| `experience.submit` | Append one owner-scoped experience observation and evidence links. Preserve source, capture time, provenance, uncertainty and immutable identity; never overwrite prior experience. | `experience.observed.v1`; `evidence.recorded.v1` only for separately validated evidence records. | Local append-only write. No external dispatch. Retry replays receipt; partial experience/evidence write is prohibited by one local transaction. |
| `representation.create` | Append a representation revision linked to one or more existing source experiences; retain prior revisions and provenance. Reject missing/cross-owner source references. | `representation.created.v1`. | Local write. No external dispatch. Source revision and representation identity are idempotently bound. |
| `context.assemble` | Create an immutable context snapshot from explicitly named, owner-scoped source revisions; record missing/unknown dependencies rather than inventing completeness. | `context.assembled.v1`. | Local derived-state write. No sensing or authorization side effect. Reassembly creates a new snapshot; it does not mutate source records. |
| `context.invalidate` | Mark the specified context revision stale and invalidate dependent derived views; never delete source experiences, memories or evidence. | `context.invalidated.v1`. | Local state change. Must be idempotent; stale revision conflicts; rebuild occurs separately. |
| `environment.observe` | Record one explicitly requested, bounded observation under exact device/resource/data scope and current OS permission. It is not continuous monitoring. | `environment.observed.v1`; experience linkage requires a separately defined causal binding. | Platform read can be externally observable/sensitive. Provider timeout/unknown result is not a successful observation; preserve provider identity/version and evidence. |
| `capability.discover` | Append discovery provenance and a provisional descriptor scoped to provider/device/context; no permission is created. | `capability.discovered.v1`. | Provider inquiry only under explicit discovery scope. Unavailable/unknown provider leaves capability unknown, not absent or granted. |
| `capability.verify` | Append verification evidence for an exact descriptor ID/version and verification method; stale descriptor version conflicts. | `capability.verified.v1`. | Verification does not grant authorization. Provider result uncertainty remains unverified; no fallback provider is silently substituted. |
| `capability.invalidate` | Mark exact descriptor revision stale/invalid and invalidate dependent plans/affordance estimates without erasing history. | `capability.invalidated.v1`; revocation event only when an authoritative revocation source exists. | Local invalidation; no automatic operation cancellation or policy mutation. Dependents revalidate separately. |
| `capability.knowledge.propose` | Create a quarantined, evidence-linked capability-knowledge candidate; no active knowledge head changes. | `capability.knowledge.proposed.v1` with provisional status; acceptance/revision remains a separate transition. | Local candidate write only. Evaluation/acceptance is a separate governed transition. |
| `capability.knowledge.revise` | Append a new accepted knowledge revision only after required evidence/evaluation/authority; preserve contradictory evidence and prior revisions. | `capability.knowledge.revised.v1`. | Local write. Does not grant a platform permission or universal capability. |
| `memory.retrieve` | Execute an owner-scoped retrieval and append a durable retrieval audit record/link; `memory.search` remains the read-only query that returns search results without a domain mutation. The command response references the retrieval record/result artifact, not raw unrestricted memory content. | `memory.retrieved.v1` in the same local transaction as the retrieval audit record and outbox. | Read/retrieval plus narrowly scoped audit write. Enforce query purpose, classification, retention and field redaction; no memory content mutation. |
| `belief.propose` | Append a provisional belief revision linked to supporting/contradicting evidence; confidence and provenance remain explicit. | `belief.proposed.v1`. | Local write. Proposal does not replace accepted belief head unless a separate acceptance rule is met. |
| `belief.revise` | Append a new belief revision using current expected revision; preserve source history and contradictions. | `belief.revised.v1`. | Local write; stale revision conflicts; no evidence is silently deleted. |
| `prediction.create` | Append an immutable prediction with target, horizon, expected outcome, confidence and evidence/context revision. | `prediction.created.v1`. | Local write. It is not an observed outcome and cannot authorize action. |
| `prediction.evaluate` | Append evaluation linking one prediction to independently observed outcome evidence; never rewrite the prediction. | `prediction.evaluated.v1`. | Local write. Missing or uncertain outcome yields inconclusive evaluation, not fabricated success/failure. |
| `appraisal.evaluate` | Append appraisal output tied to the actual evidence/context/model revision; no fixed stimulus-to-emotion/action mapping. | `appraisal.updated.v1`. | Local computation/write. Re-run creates a new evaluation; no external side effect. |
| `attention.allocate` | Update runtime attention allocation under a scheduler/attention epoch; durable recording is selective and revisioned where persisted. | `attention.allocated.v1` when a durable allocation event is required. | Runtime-local allocation. Concurrent stale allocation must conflict/recompute; it cannot change authorization or policy priority. |
| `reasoning.assess` | Append reasoning assessment/hypotheses and evidence/artifact lineage; preserve alternatives and uncertainty. | `reasoning.hypothesis.proposed.v1`. | Local computation/write. A hypothesis is not a fact, plan, decision or action. |
| `goal.create` | Create a derived goal linked to its originating objective and constraints; never create or mutate the owner objective implicitly. | `goal.created.v1`. | Local write. Requires objective reference/revision and owner scope. |
| `goal.revise` | Append a goal revision under expected goal revision; revalidate objective and evidence links. | `goal.revised.v1`. | Local write. Does not rewrite the objective or silently alter a plan. |
| `goal.cancel` | Transition one non-terminal derived goal to `cancelled` under expected revision; retain prior history and dependent plan references. `goalRevision.state` explicitly includes the terminal `cancelled` value. | `goal.revised.v1` carrying the new revision and `state=cancelled`; the event is a revision event, not a separate owner objective cancellation. | Local write only. Repeated cancellation replays; stale revision conflicts. |
| `plan.propose` | Create a proposed plan bound to exact objective/goal, situation, evidence, dependency and policy revisions; proposal is not authorization. | `plan.proposed.v1`. | Local write. No provider dispatch; unknown means remain explicit. |
| `plan.revise` | Append a new plan revision with expected plan revision; preserve prior plan and explain changed dependencies/evidence. | `plan.revised.v1`. | Local write. Stale objective/situation/means dependencies require revalidation. |
| `plan.checkpoint` | Persist a checkpoint bound to plan revision, task run, completed steps and dependency watermarks. | `plan.checkpointed.v1`. | Local write. Resume requires current checkpoint and dependency revalidation; no external action. |
| `decision.record` | Append a decision record containing considered options, evidence, selected option and decision authority. | `decision.recorded.v1`. | Local write. A recorded decision is not an approval or operation dispatch grant. |
| `operation.propose` | Create an immutable exact-operation proposal and durable lifecycle record with target, means, parameters, expected effects, risk and evidence. | `operation.proposed.v1`, then lifecycle events only as actual transitions occur. | Proposal only; MUST NOT call provider or dispatch. Governance evaluates exact digest separately. |
| `operation.cancel` | Request cancellation of one non-terminal operation; pre-dispatch may cancel, post-dispatch/unknown remains pending until reconciliation. | `operation.cancel_requested.v1`, then `operation.cancelled.v1` only after verified terminal result. | External side effect may already have occurred. Never claim reversal; reconcile before retry or terminal cancellation. |
| `operation.reconcile` | Reconcile one UNCERTAIN operation against its exact provider/target using operation-specific evidence; append reconciliation result. | `operation.reconciling.v1`, `operation.reconciled.v1` and resulting state event as applicable. | Provider query/reconciliation is not a new dispatch. No blind retry; provider identity/version and evidence are mandatory. |
| `approval.request` | Create a one-time owner approval request bound to operation ID, canonical digest, target, recipient, capability version, data classes, risk, policy and expiry. | `approval.requested.v1`. | No authorization is granted by request creation. Changed operation digest invalidates the request. |
| `approval.revoke` | Revoke one active approval/nonce within governance authority; append revocation evidence and invalidate dependent pre-dispatch authorization. | `approval.revoked.v1` with approval ID, revocation ID, owner session, reason, policy version and reconciliation-required flag. | Governance state change. Revocation after dispatch triggers operation reconciliation, not fictional rollback. |
| `outcome.evaluate` | Append evaluation of independently observed outcome evidence against prediction/objective criteria; retain attribution uncertainty. | `outcome.evaluated.v1`. | Local evaluation only. It cannot create the observation or claim causality without evidence. |
| `learning.update.propose` | Create a quarantined learning-update proposal with hypothesis, scope, source experiences, baseline and evaluation plan. | `learning.update.proposed.v1`. | No active memory/model change. Evaluation and owner/policy acceptance are separate. |
| `learning.experiment.submit` | Submit a bounded job to an isolated worker with immutable input/config/code/data references, seed, resource budget and deadline. | `worker.job.requested.v1`; completion event only after validated artifact/result. | Worker launch is a bounded external process side effect. Retry creates a new attempt; worker cannot access production keys, DB credentials or activation authority. |
| `learning.candidate.evaluate` | Evaluate a quarantined candidate against frozen baseline, held-out data, unseen controls and regression/safety thresholds. | `learning.candidate.evaluated.v1` records exact candidate/baseline/dataset/protocol/regression digests, metrics, results and passed/failed/inconclusive status. | Evaluation only; no activation. Incomplete evidence yields inconclusive, not pass. |
| `self_model.update.propose` | Create a proposed self-model revision linked to evidence and confidence; active self-model remains unchanged. | `self_model.update.proposed.v1` carries the revision with `status=proposed`; activation/acceptance is separate. | Candidate only; do not mutate active self-model from model-generated claim. |
| `evolution.change.propose` | Create a candidate artifact/proposal with source revision, change rationale, validation plan and rollback reference. | `evolution.proposed.v1`. | Quarantined artifact only; no active code/model/policy change. |
| `evolution.candidate.evaluate` | Record evaluation of exact immutable candidate artifact against baseline and acceptance gates. | `evolution.candidate.evaluated.v1`. | Evaluation only; candidate remains quarantined. |
| `evolution.candidate.activate` | Change active artifact pointer only after explicit owner/policy authorization, verified candidate evaluation, signature/provenance and rollback readiness. | `candidate.activated.v1`. | R5 protected transition. Never model-authorized; activation must be atomic/audited and reversible. |
| `evolution.candidate.rollback` | Restore exact prior approved artifact pointer after verified failure/rollback authorization; preserve failed candidate and audit lineage. | `candidate.rolled_back.v1`. | R5 protected transition. No deletion of failed artifact/evidence; verify restored artifact hash. |
| `task.start` | Queued → running only with current prerequisites, budget and dependency revisions. | `task.control.requested.v1`, `task.run.transitioned.v1`. | Local scheduler transition; task-control §4.2.3 governs revision, replay, safe point and recovery. |
| `task.pause` | Running → paused only at safe point; otherwise persist pending request. | Same task-control event pair. | Cooperative. Dispatched operations remain independent and must be reconciled. |
| `task.resume` | Paused → running only after checkpoint, plan, context, means and dependency revalidation. | Same task-control event pair. | Local scheduler transition; lost/terminal tasks cannot resume directly. |
| `task.cancel` | Non-terminal task cancellation request; terminal transition only after safe point and operation reconciliation. | Same task-control event pair. | Cooperative; cancellation is not proof of external reversal. |
| `device.pair` | Deferred future multi-device phase; no aggregate, request schema or owner authorization contract is approved. | None. | `deferred_by_scope`; no dispatch. |
| `device.revoke` | Deferred future multi-device phase; no aggregate, request schema or owner authorization contract is approved. | None. | `deferred_by_scope`; no dispatch. |

| `objective.create` | Create owner intent as objective_records version 1; success evidence, constraints and uncertainty remain explicit; never create a derived goal implicitly. | `objective.created.v1` | Local owner-intent write only; no action or authorization grant. |
| `objective.revise` | Require exact current objective and next version; append revision lineage and preserve original request source. | `objective.revised.v1` | Local objective revision only; material changes require downstream plan/dependency re-evaluation. |
| `world.entity.observe` | Append owner-scoped entity observation/evidence; new identity starts provisional at version 1; later versions preserve all evidence lineage. | `world.entity.observed.v1` | Records an already-obtained observation; does not trigger sensing or assert ground truth. |
| `world.relationship.revise` | Append exact relationship revision with temporal/context scope and evidence; subject/object must resolve under same owner. | `world.relationship.revised.v1` | Local world-model write; contradictory evidence remains visible and epistemically qualified. |
| `situation.snapshot.create` | Create immutable partial situation snapshot from exact objective/entity/evidence revisions; retain unknowns and conflicts. | `situation.snapshot.created.v1` | Local snapshot only; no sensing and no claim of complete world state. |
| `means.affordance.propose` | Create context-scoped possible-means hypothesis with actors, resources, preconditions, expected effects, authority requirements and evidence. | `means.affordance.proposed.v1` | Hypothesis only; not a capability grant, permission, guaranteed ability or executable API. |
| `interaction.propose` | Create immutable proposal bound to objective, actor, targets, means hypotheses, expected effects and precondition evidence. | `interaction.proposed.v1` | Proposal only; MUST NOT dispatch or contact target. Independent governance and operation path remain separate. |
| `interaction.outcome.record` | Append independently observed outcome, evidence, unresolved effects and attribution hypotheses for exact interaction. | `interaction.outcome.observed.v1` | Local evidence write; provider receipt alone is not observed outcome or causal proof. |

## 3. Resolved command/event bindings and remaining blockers

The six command/event or command/query mismatches identified in the initial matrix review are now resolved at the specification/schema/registry level:

1. `memory.retrieve` is the auditable retrieval command, with `memory.retrieved.v1`; `memory.search` remains the read-only query.
2. `goal.cancel` writes a terminal `cancelled` goal revision and emits `goal.revised.v1`; the goal revision schema now admits the explicit terminal state.
3. `approval.revoke` emits the new `approval.revoked.v1` event with a dedicated payload that records revocation authority context and whether an already-dispatched operation requires reconciliation.
4. `capability.knowledge.propose` emits `capability.knowledge.proposed.v1`, distinct from accepted/revised knowledge.
5. `learning.candidate.evaluate` emits `learning.candidate.evaluated.v1` with candidate/baseline/dataset/protocol lineage, metrics, regression results, unseen-control evidence and an explicit passed/failed/inconclusive status.
6. `self_model.update.propose` emits `self_model.update.proposed.v1` with an explicit proposed status, distinct from an applied self-model update.

The four newly introduced event payload definitions have positive fixture examples and remain design-only/non-dispatchable. The command registry binds these event names, and the event validator checks that each referenced schema and fixture resolves and validates.

Remaining BR-001 blockers are not naming gaps: no production handlers or executed command acceptance tests exist; the first-release command subset has not been accepted by the owner; target resource budgets remain unmeasured where applicable; and command/event consumers, persistence transactions, recovery and concurrency still require implementation evidence.

## 4. Required executable acceptance

For each command entry, the handler-level test suite must assert:
- Valid authenticated owner/actor and exact-scope grant; cross-owner, revoked, expired and unbound owner cases deny without existence disclosure.
- Exact schema/version validation occurs before mutation.
- Correct aggregate revision/state transition; stale revision and dependency versions produce no mutation.
- Same scoped key/digest replays exactly one durable response; different digest conflicts without overwriting the original receipt.
- Before-commit crash leaves no partial receipt/aggregate/event/outbox; after-commit/pre-publication crash replays receipt and publishes the outbox logically once.
- Deadline expiry and cancellation races obey the command-specific safe-point/dispatch state.
- Event body matches the actual committed transition and validates against the exact event payload schema.
- Error code and side-effect state are truthful; unknown provider outcome is UNCERTAIN and is reconciled before retry.
- No command crosses owner/store boundaries or invokes provider I/O inside a local database write transaction.

Task controls retain their existing TC-001…TC-012 cases plus per-command replay/crash assertions. Other commands require their own cases; a shared checklist does not prove handler behaviour.

## 5. Completion boundary

This matrix and the command registry now carry per-entry semantic bindings and 43 unique acceptance-case IDs for the 43 mapped commands. A machine-enforced validator checks those fields, known error/event references, exact command inventory and one-to-one acceptance-case presence. This closes the builder's first-pass specification/registry-binding subtask for BR-001, not BR-001 overall. Six command/event or command/query classification mismatches remain explicitly unresolved; all 43 acceptance cases remain design criteria, not executed handler tests. The first-release command subset remains proposed pending owner acceptance. All mapped commands remain `design_only_not_dispatchable`; device pairing/revocation remain deferred. No implementation authorization or owner decision is implied.


## 4. Per-command acceptance case catalogue

The following cases are builder-defined acceptance criteria, not executed handler tests. They give each mapped command an independently addressable positive and negative assertion. Task-control cases supplement the existing TC-001…TC-012 suite; they do not replace it.

| Acceptance ID | Command | Positive assertion | Negative / fault assertion |
|---|---|---|---|
| `CC-001` | `experience.submit` | One owner-scoped observation and its evidence links commit atomically with one receipt/event. | Duplicate experience ID, cross-owner source or invalid provenance leaves no partial record. |
| `CC-002` | `representation.create` | Representation revision 1 links only to exact owner-scoped source experience revisions. | Missing/cross-owner source or duplicate representation ID commits nothing. |
| `CC-003` | `context.assemble` | Snapshot records exact source revisions plus explicit unknown/missing dependencies. | Unbound source or stale required dependency cannot produce a falsely complete snapshot. |
| `CC-004` | `context.invalidate` | Current context revision becomes stale once and source records remain intact. | Stale revision conflicts; repeated request replays without duplicate invalidation. |
| `CC-005` | `environment.observe` | One explicitly requested observation is captured with current permission and source identity. | Missing/revoked OS permission causes no sensor/provider call and no observation record. |
| `CC-006` | `capability.discover` | Discovery appends provenance and a provisional descriptor without creating permission. | Unknown/unavailable provider leaves capability unknown and no trusted descriptor. |
| `CC-007` | `capability.verify` | Verification evidence binds exact descriptor and provider versions. | Stale descriptor or untrusted provider cannot become verified. |
| `CC-008` | `capability.invalidate` | Exact descriptor revision becomes invalid and dependent estimates are invalidated. | Stale descriptor revision conflicts; no history is deleted or operation falsely cancelled. |
| `CC-009` | `capability.knowledge.propose` | Evidence-backed candidate is quarantined and active knowledge head is unchanged. | Insufficient evidence or cross-owner lineage cannot alter active knowledge. |
| `CC-010` | `capability.knowledge.revise` | Accepted successor knowledge revision preserves prior and contradictory evidence. | Stale expected revision cannot replace current knowledge. |
| `CC-011` | `memory.retrieve` | If retained as a command, retrieval audit record is appended without changing memory contents. | Cross-owner retrieval is denied without record/existence disclosure; command/query classification remains a release blocker. |
| `CC-012` | `belief.propose` | Provisional belief is linked to supporting and contradicting evidence. | Unsupported/model-only claim is not promoted to accepted belief. |
| `CC-013` | `belief.revise` | Successor revision preserves prior belief and contradictory evidence. | Stale expected revision or missing evidence causes no update. |
| `CC-014` | `prediction.create` | Immutable prediction records exact context/belief revisions and horizon. | Prediction cannot be treated as observation, outcome or authorization. |
| `CC-015` | `prediction.evaluate` | Evaluation links exact prediction to independently observed outcome evidence. | Missing/uncertain outcome remains inconclusive and never fabricates a score. |
| `CC-016` | `appraisal.evaluate` | Appraisal is tied to context, evidence and model revisions; context changes can change appraisal. | Missing context/evidence is rejected; no fixed stimulus-to-emotion/action mapping is applied. |
| `CC-017` | `attention.allocate` | Current attention epoch is replaced once and advanced once. | Stale epoch cannot overwrite a newer allocation or alter governance priority. |
| `CC-018` | `reasoning.assess` | Assessment appends hypotheses, alternatives and evidence lineage. | Hypothesis is not promoted to fact or used as authorization. |
| `CC-019` | `goal.create` | Derived goal is created against an existing objective revision. | Missing/cross-owner objective cannot create a goal or mutate objective. |
| `CC-020` | `goal.revise` | Successor goal revision binds current objective revision and retains lineage. | Stale goal/objective revision conflicts without rewriting dependent plan. |
| `CC-021` | `goal.cancel` | Non-terminal goal receives one terminal cancelled revision and retained history. | Terminal goal cannot be cancelled again; event remains blocked until schema/consumer binding is resolved. |
| `CC-022` | `plan.propose` | Plan binds exact objective, situation, evidence, means and policy revisions. | Unknown means or stale dependencies cannot be represented as executable/authorized plan. |
| `CC-023` | `plan.revise` | New plan revision records changed dependencies and rationale. | Stale plan/objective/context/means revision conflicts. |
| `CC-024` | `plan.checkpoint` | Checkpoint records exact task/plan revisions, completed steps and dependency watermarks. | Stale task/plan or missing step evidence cannot be checkpointed. |
| `CC-025` | `decision.record` | Decision record preserves options, evidence and authority reference. | Decision record alone cannot satisfy approval or authorize dispatch. |
| `CC-026` | `operation.propose` | Exact operation proposal is persisted without invoking provider dispatch. | Missing target, stale means, missing permission or approval cannot reach dispatch. |
| `CC-027` | `operation.cancel` | Pre-dispatch operation can cancel; dispatched/unknown operation remains pending until reconciliation. | No terminal cancelled state or reversal claim while provider effect is unresolved. |
| `CC-028` | `operation.reconcile` | Fresh provider evidence advances an uncertain operation to a supported reconciled state without redispatch. | Missing/contradictory provider evidence leaves operation uncertain and retry prohibited. |
| `CC-029` | `approval.request` | One approval request is bound to exact operation digest, target, data, risk and expiry. | Changed operation digest, untrusted requester or missing scope cannot create usable approval. |
| `CC-030` | `approval.revoke` | Exact active approval is revoked and future pre-dispatch authorization is denied. | Revocation cannot imply reversal of an already dispatched operation; event binding remains unresolved. |
| `CC-031` | `outcome.evaluate` | Evaluation compares independently observed outcome with prediction/objective criteria and retains uncertainty. | Provider receipt alone cannot be treated as observed outcome or causal proof. |
| `CC-032` | `learning.update.propose` | Learning update candidate records experience lineage, frozen baseline and evaluation plan; active behaviour unchanged. | Missing provenance/baseline or model-generated unsupported claim cannot alter active mechanisms. |
| `CC-033` | `learning.experiment.submit` | Isolated worker receives immutable manifest, seed and bounded budget; output is quarantined. | Worker cannot access production keys/DB credentials or activate artifacts; timeout retains attempt uncertainty. |
| `CC-034` | `learning.candidate.evaluate` | Candidate evaluation uses frozen baseline, held-out data and unseen controls; no activation. | Incomplete/contaminated evaluation cannot pass or change active behaviour. |
| `CC-035` | `self_model.update.propose` | Proposed self-model revision is evidence-linked and active head remains unchanged. | Unmeasured/model-only capability claim cannot update active self-model; event semantics remain unresolved. |
| `CC-036` | `evolution.change.propose` | Candidate artifact and source revision are quarantined with validation and rollback lineage. | Proposal cannot change active runtime, policy or authority. |
| `CC-037` | `evolution.candidate.evaluate` | Exact artifact is evaluated against frozen baseline and safety/regression thresholds. | Missing evaluation evidence or artifact digest mismatch cannot pass. |
| `CC-038` | `evolution.candidate.activate` | Activation atomically advances active pointer only with owner/governance approval, valid signature and rollback readiness. | Missing/expired/revoked approval or stale active pointer blocks activation. |
| `CC-039` | `evolution.candidate.rollback` | Rollback restores exact prior approved artifact digest and records lineage. | Unknown prior digest or missing rollback authority cannot change active pointer. |
| `CC-040` | `task.start` | Queued run transitions to running exactly once after prerequisite, budget and revision checks. | Non-queued, stale, unowned or blocked run cannot start. |
| `CC-041` | `task.pause` | Running run pauses at safe point; otherwise durable pending request is recorded. | In-flight/unknown operation cannot be represented as paused or cancelled. |
| `CC-042` | `task.resume` | Paused run resumes only after checkpoint and all dependencies are revalidated. | Lost, terminal or stale-dependency run cannot resume. |
| `CC-043` | `task.cancel` | Non-terminal run cancellation completes only after safe point and operation reconciliation. | Dispatched/unknown operation keeps cancellation pending; no false external reversal claim. |

| `CC-044` | `objective.create` | Create version-1 objective with owner intent and success evidence. | Duplicate ID or owner_ref mismatch creates no objective or event. |
| `CC-045` | `objective.revise` | Append version+1 objective preserving source and prior criteria. | Stale/skip version conflicts; no goal or plan is silently rewritten. |
| `CC-046` | `world.entity.observe` | Append provisional entity observation with evidence and context scope. | Missing evidence or cross-owner reference creates no entity revision. |
| `CC-047` | `world.relationship.revise` | Append relation revision with valid_from/context and evidence lineage. | Unknown subject/object or stale version causes no relation change. |
| `CC-048` | `situation.snapshot.create` | Persist snapshot with exact source revisions, unknowns and conflicts. | Missing evidence lineage or cross-owner objective/entity rejects snapshot. |
| `CC-049` | `means.affordance.propose` | Persist hypothesis with explicit preconditions/effects/authority requirements. | Insufficient evidence remains unverified; no permission/capability is granted. |
| `CC-050` | `interaction.propose` | Persist proposal with exact target/means/effect digest and no dispatch. | Attempted provider call or missing authority evidence fails closed before any effect. |
| `CC-051` | `interaction.outcome.record` | Persist observed outcome with source evidence and unresolved attribution. | Provider receipt alone or absent independent evidence cannot record verified success. |
A passing implementation must execute these cases with deterministic stores/providers/workers, assert durable before/after state, event/outbox count, receipt replay and crash/restart behaviour, and preserve exact error/side-effect classification. Catalogue presence alone is not test evidence.
