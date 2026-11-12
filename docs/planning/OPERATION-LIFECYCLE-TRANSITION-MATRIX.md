# AURIONS — Operation Lifecycle Transition Matrix

**Status:** Proposed normative planning contract; not runtime-validated.  
**Authority:** This matrix refines the operation state enum and action-gateway event registry. It does not authorize provider dispatch or select a provider.

## 1. State transition rules

The operation lifecycle is an append-only, versioned state machine. A transition is committed only by the Action Gateway after checking the expected operation revision. Each emitted event is committed with the owning operation mutation and outbox record in one transaction. Provider invocation is a separate boundary. The state `succeeded` is a provider-reported result, not independently verified world outcome.

| Event | Allowed predecessor state(s) | Exact producer trigger | Owner transition contract |
|---|---|---|---|
| `operation.validating.v1` | proposed | Emitted when the Action Gateway accepts a persisted proposed operation revision and begins schema, target, descriptor, deadline and policy preflight. No provider invocation or external effect has occurred. | Record pre-dispatch validation in progress; no external effect is permitted. |
| `operation.awaiting_approval.v1` | validating | Emitted when preflight succeeds but the exact operation digest requires owner approval that is absent, expired or undecided. Dispatch remains blocked pending a separate governance decision. | Record pending exact-scope approval; dispatch remains blocked. |
| `operation.ready.v1` | validating, awaiting_approval | Emitted when all pre-dispatch checks are current, the operation digest is unchanged, required approval is valid and required platform permission is present. Readiness is not dispatch; the final authorization check still runs at the invocation boundary. | Record that pre-dispatch checks are complete; readiness is not proof of dispatch. |
| `operation.dispatched.v1` | ready | Emitted only after the Action Gateway persists a unique attempt/idempotency identity and crosses the provider invocation boundary for the exact request digest. A crash or missing receipt after this point is uncertain and must be reconciled before retry. | Persist dispatch attempt and exact request digest; external effect may have begun and must be reconciled before retry. |
| `operation.running.v1` | dispatched | Emitted when the provider returns an accepted asynchronous execution identity and explicitly reports that the exact attempt is running. This is not success or verified outcome. | Record provider execution state; do not infer success or observed outcome. |
| `operation.succeeded.v1` | dispatched, running | Emitted when the provider returns a final success receipt bound to the exact attempt and request digest. This is provider-reported success only; independent postcondition evidence remains required. | Record provider-reported success only; verified outcome requires independent postcondition evidence. |
| `operation.failed.v1` | dispatched, running | Emitted when the provider returns a definitive failure for the exact attempt. If evidence does not establish side-effect absence, the operation remains/enters uncertain and must be reconciled; failure is not permission to retry. | Record definitive provider failure for the exact attempt; side-effect absence must be established by reconciliation before retry. If effect state remains uncertain, retain/transition to uncertain rather than claiming no effect. |
| `operation.rejected.v1` | proposed, validating, awaiting_approval, ready | Emitted when schema, scope, policy, target, descriptor or final authority validation denies the operation before the provider invocation boundary. No provider call is permitted. | Record pre-dispatch denial; no provider effect is expected and no retry occurs without changed authorized input. |
| `operation.expired.v1` | proposed, validating, awaiting_approval, ready | Emitted when the operation deadline or required approval expires before provider invocation. If invocation may already have crossed the boundary, emit/retain uncertain and reconcile rather than assume no effect. | Record expiry and prevent late dispatch; if dispatch was already possible, reconcile rather than assume no effect. |
| `operation.revoked.v1` | proposed, validating, awaiting_approval, ready | Emitted when the gateway receives a governance approval, permission or capability revocation for the exact queued operation before provider invocation and invalidates that attempt. In-flight attempts remain separately reconciled; revocation is not rollback. | Record authority revocation against the operation; block future attempts and reconcile in-flight effects. |
| `operation.uncertain.v1` | dispatched, running, reconciling | Emitted when a dispatched/running/reconciling attempt has a timeout, lost receipt, contradictory provider evidence, crash boundary or unavailable reconciliation source that prevents a truthful terminal determination. Blind retry is prohibited. | Persist unknown external outcome and prohibit blind retry until provider/independent evidence reconciles it. |
| `operation.compensation_required.v1` | succeeded, uncertain | Emitted only after independent observation establishes an effect that violates the accepted postcondition or requires reversal under approved policy, and a technically available compensating operation is identified. Compensation requires separate authorization. | Record required compensation and its exact scope; compensation is not assumed safe or complete. |
| `operation.compensating.v1` | compensation_required | Emitted when a separately authorized compensation attempt is persisted and crosses its own provider invocation boundary. Compensation remains uncertain until independently verified. | Record compensation attempt; result remains uncertain until independently verified. |
| `operation.compensated.v1` | compensating | Emitted only after independent postcondition evidence confirms the compensating effect for the exact compensation attempt. Original action and compensation lineage remain immutable. | Record verified compensation evidence while preserving original action and compensation lineage. |
| `operation.manual_intervention.v1` | uncertain, failed, compensation_required, compensating | Emitted when bounded automated reconciliation/compensation is exhausted, evidence remains contradictory, or the effect is irreversible/unsafe to retry. Automated retry/compensation stops pending authorized owner resolution. | Escalate unresolved state and block automated retry/compensation until an authorized resolution. |

## 2. Global invariants

1. Every transition uses optimistic concurrency against the expected operation revision; stale writers receive a typed conflict.
2. The operation aggregate mutation, event sequence allocation and immutable outbox append are atomic within the owning store.
3. Each provider attempt has a unique attempt ID, canonical request digest, idempotency identity, deadline and provider/descriptor version.
4. The provider invocation boundary is recorded before any retry can be considered. After a possibly dispatched attempt, recovery reconciles; it does not infer no effect from a timeout.
5. Governance approval, OS/platform permission, capability verification and operation readiness are separate predicates. All required predicates are rechecked immediately before dispatch.
6. Provider receipt, independent world observation and outcome evaluation are distinct records. A provider success receipt cannot alone produce a verified outcome.
7. Compensation is a new operation with its own digest, authorization, attempt and independent verification. It does not delete or rewrite the original operation.
8. Unknown, contradictory, expired or revoked authority fails closed. Manual intervention is a durable terminal automation boundary, not a success result.

## 3. Closure boundary

The event registry now names these 15 internal Action Gateway event triggers. This closes the exact-trigger specification gap for these entries only. The remaining 23 events without command producers still require exact event-specific producer triggers. All 89 events remain design-only/non-dispatchable until runtime handlers and event-specific acceptance tests are implemented and executed. No provider adapter or implementation authorization is implied.

