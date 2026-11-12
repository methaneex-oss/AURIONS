# AURIONS — Operation Lifecycle Transition Matrix

**Status:** Proposed normative planning contract; not runtime-validated.  
**Authority:** This matrix refines the operation state enum and action-gateway event registry. It does not authorize provider dispatch or select a provider.

## 1. State transition rules

The operation lifecycle is an append-only, versioned state machine. A transition is committed only by the Action Gateway after checking the expected operation revision. Each emitted event is committed with the owning operation mutation and outbox record in one transaction. Provider invocation is a separate boundary. The state `succeeded` is a provider-reported result, not independently verified world outcome.

| Event | Allowed predecessor state(s) | Exact producer trigger | Effect / authority boundary |
|---|---|---|---|
| `operation.validating.v1` | proposed | The Action Gateway accepts a persisted proposal revision and begins schema, target, descriptor, deadline and policy preflight. | Pre-dispatch only. No provider invocation or external effect. |
| `operation.awaiting_approval.v1` | validating | Preflight succeeds but the exact operation digest requires owner approval that is absent, expired or not yet decided. | Remains blocked. Approval request/decision is a separate governance transition. |
| `operation.ready.v1` | validating, awaiting_approval | All pre-dispatch checks are current, the exact operation digest is unchanged, required approval is valid, and platform permission is present where required. | Ready is not dispatched. A final authorization check is still required at the dispatch boundary. |
| `operation.dispatched.v1` | ready | The Action Gateway persists a unique attempt and idempotency identity, then crosses the provider invocation boundary for that exact request digest. | The provider may have acted. A crash or missing receipt makes the attempt uncertain; never blindly retry. |
| `operation.running.v1` | dispatched | The provider returns an accepted asynchronous execution identity and reports that the operation is running. | Provider execution state only; not success or verified outcome. |
| `operation.succeeded.v1` | dispatched, running | The provider returns a final success receipt bound to the exact attempt and request digest. | Provider-reported success only. Independent postcondition evidence is still required. |
| `operation.failed.v1` | dispatched, running | The provider returns a definitive failure for the exact attempt. If side-effect absence is not established, the operation must remain/transition to uncertain pending reconciliation. | Failure receipt is not proof of no side effect. No retry until reconciliation establishes effect state and retry safety. |
| `operation.rejected.v1` | proposed, validating, awaiting_approval, ready | Schema, scope, policy, target, descriptor or final authority validation denies the operation before the provider invocation boundary. | No provider call is permitted. A changed request requires a new digest and fresh evaluation. |
| `operation.expired.v1` | proposed, validating, awaiting_approval, ready | The operation deadline or required approval expires before provider invocation. If invocation may already have crossed the boundary, emit/retain uncertain and reconcile instead. | Prevents late dispatch; does not imply reversal or absence of an already-started effect. |
| `operation.revoked.v1` | proposed, validating, awaiting_approval, ready | The exact approval, permission or capability authority is revoked before provider invocation and the gateway invalidates the queued operation. | Blocks future attempts. If an attempt is already in flight, preserve its state and reconcile; revocation is not rollback. |
| `operation.uncertain.v1` | dispatched, running, reconciling | A timeout, lost receipt, contradictory provider evidence, crash boundary or unavailable reconciliation source prevents a truthful terminal determination. | Blocks blind retry and automatic success/failure claims until evidence resolves the attempt. |
| `operation.compensation_required.v1` | succeeded, uncertain | Independent observation establishes an effect that violates the accepted postcondition or requires reversal under the approved policy, and a compensating action is technically available. | Compensation is a new exact operation and requires separate authorization; do not infer it from failure. |
| `operation.compensating.v1` | compensation_required | A separately authorized compensation attempt is persisted and crosses its own provider invocation boundary. | Compensation result remains uncertain until independently verified. |
| `operation.compensated.v1` | compensating | Independent postcondition evidence confirms the compensating effect for the exact compensation attempt. | Preserve original action, compensation attempt and evidence lineage; never erase the original effect. |
| `operation.manual_intervention.v1` | uncertain, failed, compensation_required, compensating | Bounded automated reconciliation/compensation is exhausted, evidence remains contradictory, or the effect is irreversible/unsafe to retry. | Stop automated retry/compensation and require an authorized owner resolution. |

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
