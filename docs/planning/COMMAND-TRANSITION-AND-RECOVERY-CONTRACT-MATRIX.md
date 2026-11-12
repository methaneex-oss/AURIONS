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
| `capability.knowledge.propose` | Create a quarantined, evidence-linked capability-knowledge candidate; no active knowledge head changes. | Dedicated proposed event binding remains unresolved; do not misuse `capability.knowledge.revised.v1` for a proposal. | Local candidate write only. Evaluation/acceptance is a separate governed transition. |
| `capability.knowledge.revise` | Append a new accepted knowledge revision only after required evidence/evaluation/authority; preserve contradictory evidence and prior revisions. | `capability.knowledge.revised.v1`. | Local write. Does not grant a platform permission or universal capability. |
| `memory.retrieve` | Existing entry writes retrieval records/links, while `memory.search` is already a read-only query. Its command-versus-query classification and retrieval-event write policy must be resolved before publication. | `memory.retrieved.v1` only if a durable retrieval event is explicitly required and its privacy/retention policy is defined. | **Classification conflict:** do not dispatch until the owner/domain decides whether this is a query or an auditable state-changing command. |
| `belief.propose` | Append a provisional belief revision linked to supporting/contradicting evidence; confidence and provenance remain explicit. | `belief.proposed.v1`. | Local write. Proposal does not replace accepted belief head unless a separate acceptance rule is met. |
| `belief.revise` | Append a new belief revision using current expected revision; preserve source history and contradictions. | `belief.revised.v1`. | Local write; stale revision conflicts; no evidence is silently deleted. |
| `prediction.create` | Append an immutable prediction with target, horizon, expected outcome, confidence and evidence/context revision. | `prediction.created.v1`. | Local write. It is not an observed outcome and cannot authorize action. |
| `prediction.evaluate` | Append evaluation linking one prediction to independently observed outcome evidence; never rewrite the prediction. | `prediction.evaluated.v1`. | Local write. Missing or uncertain outcome yields inconclusive evaluation, not fabricated success/failure. |
| `appraisal.evaluate` | Append appraisal output tied to the actual evidence/context/model revision; no fixed stimulus-to-emotion/action mapping. | `appraisal.updated.v1`. | Local computation/write. Re-run creates a new evaluation; no external side effect. |
| `attention.allocate` | Update runtime attention allocation under a scheduler/attention epoch; durable recording is selective and revisioned where persisted. | `attention.allocated.v1` when a durable allocation event is required. | Runtime-local allocation. Concurrent stale allocation must conflict/recompute; it cannot change authorization or policy priority. |
| `reasoning.assess` | Append reasoning assessment/hypotheses and evidence/artifact lineage; preserve alternatives and uncertainty. | `reasoning.hypothesis.proposed.v1`. | Local computation/write. A hypothesis is not a fact, plan, decision or action. |
| `goal.create` | Create a derived goal linked to its originating objective and constraints; never create or mutate the owner objective implicitly. | `goal.created.v1`. | Local write. Requires objective reference/revision and owner scope. |
| `goal.revise` | Append a goal revision under expected goal revision; revalidate objective and evidence links. | `goal.revised.v1`. | Local write. Does not rewrite the objective or silently alter a plan. |
| `goal.cancel` | Transition one non-terminal derived goal to cancelled under expected revision; retain prior history and dependent plan references. | No dedicated goal-cancel event exists; use of `goal.revised.v1` with a typed terminal status requires explicit payload/consumer confirmation. | Local write only. Event binding remains unresolved; do not dispatch until confirmed. |
| `plan.propose` | Create a proposed plan bound to exact objective/goal, situation, evidence, dependency and policy revisions; proposal is not authorization. | `plan.proposed.v1`. | Local write. No provider dispatch; unknown means remain explicit. |
| `plan.revise` | Append a new plan revision with expected plan revision; preserve prior plan and explain changed dependencies/evidence. | `plan.revised.v1`. | Local write. Stale objective/situation/means dependencies require revalidation. |
| `plan.checkpoint` | Persist a checkpoint bound to plan revision, task run, completed steps and dependency watermarks. | `plan.checkpointed.v1`. | Local write. Resume requires current checkpoint and dependency revalidation; no external action. |
| `decision.record` | Append a decision record containing considered options, evidence, selected option and decision authority. | `decision.recorded.v1`. | Local write. A recorded decision is not an approval or operation dispatch grant. |
| `operation.propose` | Create an immutable exact-operation proposal and durable lifecycle record with target, means, parameters, expected effects, risk and evidence. | `operation.proposed.v1`, then lifecycle events only as actual transitions occur. | Proposal only; MUST NOT call provider or dispatch. Governance evaluates exact digest separately. |
| `operation.cancel` | Request cancellation of one non-terminal operation; pre-dispatch may cancel, post-dispatch/unknown remains pending until reconciliation. | `operation.cancel_requested.v1`, then `operation.cancelled.v1` only after verified terminal result. | External side effect may already have occurred. Never claim reversal; reconcile before retry or terminal cancellation. |
| `operation.reconcile` | Reconcile one UNCERTAIN operation against its exact provider/target using operation-specific evidence; append reconciliation result. | `operation.reconciling.v1`, `operation.reconciled.v1` and resulting state event as applicable. | Provider query/reconciliation is not a new dispatch. No blind retry; provider identity/version and evidence are mandatory. |
| `approval.request` | Create a one-time owner approval request bound to operation ID, canonical digest, target, recipient, capability version, data classes, risk, policy and expiry. | `approval.requested.v1`. | No authorization is granted by request creation. Changed operation digest invalidates the request. |
| `approval.revoke` | Revoke one existing approval/nonce within governance authority; append revocation evidence and invalidate dependent pre-dispatch authorization. | Dedicated approval-revoked event binding is unresolved; `approval.decided.v1` may be used only if its schema explicitly models revocation. | Governance state change. Revocation after dispatch triggers operation reconciliation, not fictional rollback. |
| `outcome.evaluate` | Append evaluation of independently observed outcome evidence against prediction/objective criteria; retain attribution uncertainty. | `outcome.evaluated.v1`. | Local evaluation only. It cannot create the observation or claim causality without evidence. |
| `learning.update.propose` | Create a quarantined learning-update proposal with hypothesis, scope, source experiences, baseline and evaluation plan. | `learning.update.proposed.v1`. | No active memory/model change. Evaluation and owner/policy acceptance are separate. |
| `learning.experiment.submit` | Submit a bounded job to an isolated worker with immutable input/config/code/data references, seed, resource budget and deadline. | `worker.job.requested.v1`; completion event only after validated artifact/result. | Worker launch is a bounded external process side effect. Retry creates a new attempt; worker cannot access production keys, DB credentials or activation authority. |
| `learning.candidate.evaluate` | Evaluate a quarantined candidate against frozen baseline, held-out data, unseen controls and regression/safety thresholds. | No dedicated learning-candidate evaluation event is unambiguously registered; event binding remains unresolved pending payload/consumer contract. | Evaluation only; no activation. Incomplete evidence yields not-evaluated/rejected, not pass. |
| `self_model.update.propose` | Create a proposed self-model revision linked to evidence and confidence; active self-model remains unchanged. | Current `self_model.updated.v1` name implies an applied update; proposal/event mismatch must be resolved before binding. | Candidate only; do not mutate active self-model from model-generated claim. |
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

## 3. Per-entry unresolved blockers

The matrix intentionally identifies unresolved command/event mismatches rather than forcing every command into an existing event name. The following are explicit blockers:
1. `memory.retrieve` is currently a command while `memory.search` is a read-only query. Decide whether retrieval is an auditable state-changing operation or should be represented as a query with separate audit telemetry.
2. `goal.cancel` has no dedicated event name; confirm whether the existing goal revision payload supports a terminal cancellation state.
3. `approval.revoke` has no dedicated revocation event; confirm whether `approval.decided.v1` can represent revocation without conflating decision and revocation.
4. `capability.knowledge.propose` lacks a proposal event distinct from accepted/revised knowledge.
5. `learning.candidate.evaluate` lacks a clearly bound learning-candidate evaluation event.
6. `self_model.update.propose` currently points conceptually toward an event named `self_model.updated.v1`, which conflates proposal and accepted update.
7. The 39 non-task commands still need exact per-entry request digest fields, expected revision/dependency preconditions, exact error-code subsets, fixture IDs and executable before/after-commit/replay/recovery assertions. This matrix defines shared rules and intended domain effects; it does not claim those registry bindings or tests already exist.

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

This matrix completes a first-pass per-command semantic analysis for the existing 43 mapped entries and identifies concrete event/command mismatches. It does **not** close BR-001. The machine registry still needs per-entry expected-revision, authorization/risk, idempotency, deadline/cancellation, side-effect, error/event/outbox and fixture bindings; handler-level executable tests do not exist in this planning PR. The first-release command subset remains proposed pending owner acceptance. All commands remain `design_only_not_dispatchable`; device pairing/revocation remain deferred. No implementation authorization or owner decision is implied.
