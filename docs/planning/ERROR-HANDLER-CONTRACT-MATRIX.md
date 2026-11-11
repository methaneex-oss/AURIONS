# AURIONS — Error Handler Contract Matrix

- **Status:** SPECIFIED — builder contract mapping; runtime handlers are NOT IMPLEMENTED.
- **Authority:** `docs/planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md` §4.5 and the owner decision register.
- **Machine-readable seed:** `schemas/error-registry.v1.json`.
- **Fixture set:** `schemas/fixtures/error-handler-cases.fixture.json`, validated structurally by `schemas/error-handler-fixtures.v1.schema.json`.
- **Purpose:** Give every current error code an explicit owning handler contract and recovery boundary without registering unimplemented handlers for production dispatch.

## Normative rules

1. The observed per-attempt `side_effect_state` is authoritative. Registry defaults are fallback metadata only.
2. Handler selection is by stable error category plus operation/domain context; code-specific recovery requirements refine the category contract. Do not encode error→behaviour shortcuts in cognitive reasoning.
3. `retryable` is advisory. A retry requires current state, policy, descriptor, idempotency, deadline and budget checks. `dispatched` or `unknown` requires reconciliation before retry.
4. Error handling must not grant permission, create owner approval, change provider trust, or transform uncertain outcomes into success.
5. Diagnostics are redacted and access-controlled. Error payloads never carry secrets or authority.
6. Every handler returns a durable disposition: rejected/no transition, deferred, quarantined, checkpointed, reconciled, or manual-intervention-required. The owning aggregate decides the actual legal state transition.
7. These are planning-level handler contracts. No production dispatch registration or runtime implementation is claimed.

## Category handler contracts

### EH-001

**Category:** `contract.schema`

- **Owner:** Contract validation and compatibility boundary.
- **Contract:** Validate envelope and registered payload against the negotiated version before accepting any command, query, event or worker message. Reject malformed input, unsupported required features and incompatible major versions before domain mutation.
- **Recovery:** Correct the payload or renegotiate a mutually supported contract. Never retry unchanged invalid input or silently drop security-relevant fields.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `contract.schema.SCHEMA_MALFORMED`, `contract.schema.SCHEMA_MAJOR_UNSUPPORTED`, `contract.schema.SCHEMA_CONDITION_UNSUPPORTED`.
- **Fixture cases:** `EHC-001`, `EHC-002`, `EHC-003`.

### EH-002

**Category:** `provider.identity`

- **Owner:** Environment and discovery subsystem.
- **Contract:** Quarantine the exact provider/version subject; verify identity, provenance, signature/digest, declared interface and validation evidence. Provider cannot validate or enable itself.
- **Recovery:** Acquire independent provenance/validation evidence or leave provider quarantined. Revalidate changed versions as new subjects.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `provider.identity.PROVIDER_UNKNOWN`, `provider.identity.PROVIDER_UNTRUSTED`, `provider.identity.PROVIDER_VERSION_UNVALIDATED`.
- **Fixture cases:** `EHC-004`, `EHC-005`, `EHC-006`.

### EH-003

**Category:** `provider.availability`

- **Owner:** Discovery broker or action gateway according to operation phase.
- **Contract:** Distinguish provider absence/unavailability from a dispatch whose effect is uncertain. Preserve the per-attempt dispatch state and provider/version evidence.
- **Recovery:** Use fresh availability evidence and bounded backoff only when non-dispatch is proven; otherwise reconcile before any retry.
- **Conservative default side-effect state:** `unknown`.
- **Mapped codes:** `provider.availability.PROVIDER_UNAVAILABLE`, `provider.availability.PROVIDER_RATE_LIMITED`.
- **Fixture cases:** `EHC-007`, `EHC-008`.

### EH-004

**Category:** `capability.validity`

- **Owner:** Capability registry and discovery broker.
- **Contract:** Invalidate the affected descriptor revision and dependent plans/checkpoints; preserve historical evidence and trigger rediscovery or revalidation.
- **Recovery:** Re-discover and validate the exact provider/device/version context. Never dispatch from stale, revoked or incompatible metadata.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `capability.validity.CAPABILITY_STALE`, `capability.validity.CAPABILITY_REVOKED`, `capability.validity.CAPABILITY_INCOMPATIBLE`.
- **Fixture cases:** `EHC-009`, `EHC-010`, `EHC-011`.

### EH-005

**Category:** `evidence.precondition`

- **Owner:** Owning cognitive mechanism or action gateway precondition evaluator.
- **Contract:** Retain evidence and uncertainty; distinguish false from unknown; prevent a command or operation transition whose required precondition is not established.
- **Recovery:** Acquire additional evidence, reevaluate, ask, defer or replan. Do not coerce unknown into false or success.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `evidence.precondition.EVIDENCE_INSUFFICIENT`, `evidence.precondition.PRECONDITION_FALSE`, `evidence.precondition.PRECONDITION_UNKNOWN`.
- **Fixture cases:** `EHC-012`, `EHC-013`, `EHC-014`.

### EH-006

**Category:** `platform.permission`

- **Owner:** Platform adapter reports; Android OS remains permission authority.
- **Contract:** Read current OS permission state at the execution boundary; report missing/revoked grant distinctly from AURIONS policy denial. No subsystem synthesizes a grant.
- **Recovery:** Use the platform's explicit permission flow where applicable, then re-observe current grant state. A denial remains a denial.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `platform.permission.PLATFORM_GRANT_MISSING`, `platform.permission.PLATFORM_GRANT_REVOKED`.
- **Fixture cases:** `EHC-015`, `EHC-016`.

### EH-007

**Category:** `governance.authorization`

- **Owner:** Governance subsystem.
- **Contract:** Evaluate exact owner, actor, device, target, parameters, effects, data categories, risk, policy version, approval digest and expiry. Persist denial/revocation evidence in governance ownership.
- **Recovery:** Require a new valid owner/governance decision for the exact operation. Never infer approval from model output, prior success or a stale grant.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `governance.authorization.POLICY_DENIED`, `governance.authorization.APPROVAL_EXPIRED`, `governance.authorization.APPROVAL_MISMATCH`, `governance.authorization.APPROVAL_REVOKED`.
- **Fixture cases:** `EHC-017`, `EHC-018`, `EHC-019`, `EHC-020`.

### EH-008

**Category:** `operation.conflict`

- **Owner:** Owning aggregate handler; action gateway for operation aggregates.
- **Contract:** Reload authoritative aggregate and dependency revisions; compare canonical idempotency digest; reject stale writes and mismatched key reuse without overwriting newer state.
- **Recovery:** Re-read current state and construct a newly validated request. An idempotency digest mismatch is an integrity error, not a retry.
- **Conservative default side-effect state:** `not_dispatched`.
- **Mapped codes:** `operation.conflict.EXPECTED_REVISION_CONFLICT`, `operation.conflict.DEPENDENCY_VERSION_STALE`, `operation.conflict.IDEMPOTENCY_KEY_REUSE_MISMATCH`.
- **Fixture cases:** `EHC-021`, `EHC-022`, `EHC-023`.

### EH-009

**Category:** `operation.budget`

- **Owner:** Scheduler and action gateway.
- **Contract:** Enforce deadline, resource budget and cancellation at defined safe points; preserve checkpoint and actual dispatch state. Cancellation request is not proof of cancellation after dispatch.
- **Recovery:** Checkpoint/replan within remaining budget. Prove dispatch absence or reconcile before a new attempt; reauthorize if operation scope/effects change.
- **Conservative default side-effect state:** `unknown`.
- **Mapped codes:** `operation.budget.DEADLINE_EXCEEDED`, `operation.budget.RESOURCE_BUDGET_EXCEEDED`, `operation.budget.CANCELLED_BEFORE_DISPATCH`.
- **Fixture cases:** `EHC-024`, `EHC-025`, `EHC-026`.

### EH-010

**Category:** `operation.dispatch`

- **Owner:** Action gateway and provider adapter boundary.
- **Contract:** Persist intent and attempt before dispatch; capture provider receipt and dispatch uncertainty; never infer non-dispatch from timeout, missing response or process death.
- **Recovery:** Reconcile the target/provider and operation attempt. Do not blindly retry.
- **Conservative default side-effect state:** `unknown`.
- **Mapped codes:** `operation.dispatch.ADAPTER_DISPATCH_FAILED`, `operation.dispatch.DISPATCH_RECEIPT_MISSING`.
- **Fixture cases:** `EHC-027`, `EHC-028`.

### EH-011

**Category:** `operation.outcome`

- **Owner:** Outcome evaluator with action gateway reconciliation.
- **Contract:** Keep expected outcome, provider-reported result and independently observed postcondition separate; preserve contradictory and incomplete evidence.
- **Recovery:** Perform independent observation/reconciliation or require manual intervention. Never report an unverified effect as success.
- **Conservative default side-effect state:** `unknown`.
- **Mapped codes:** `operation.outcome.OUTCOME_UNCERTAIN`, `operation.outcome.POSTCONDITION_UNVERIFIED`, `operation.outcome.PROVIDER_RESULT_CONTRADICTED`.
- **Fixture cases:** `EHC-029`, `EHC-030`, `EHC-031`.

### EH-012

**Category:** `provider.contract`

- **Owner:** Provider trust boundary and action gateway.
- **Contract:** Quarantine the affected provider version, retain receipts and diagnostics, validate output against its declared schema, and preserve whether dispatch may have occurred.
- **Recovery:** Reconcile possible effects before retry; revalidation or owner/platform intervention may be required before reuse.
- **Conservative default side-effect state:** `unknown`.
- **Mapped codes:** `provider.contract.PROVIDER_CONTRACT_VIOLATION`, `provider.contract.PROVIDER_INTEGRITY_FAILURE`.
- **Fixture cases:** `EHC-032`, `EHC-033`.

### EH-013

**Category:** `runtime.internal`

- **Owner:** Runtime, scheduler and authoritative persistence owner.
- **Contract:** Recover from durable journal, transaction outcome and idempotent receipts; distinguish proven rollback from uncertain commit. Never infer rollback from process failure.
- **Recovery:** Reconcile authoritative durable state and replay only idempotent work. Escalate unresolved commit/side-effect uncertainty.
- **Conservative default side-effect state:** `unknown`.
- **Mapped codes:** `runtime.internal.INTERNAL_FAILURE`, `runtime.internal.STORAGE_COMMIT_UNCERTAIN`.
- **Fixture cases:** `EHC-034`, `EHC-035`.


## Code-level mapping

| Error code | Handler contract | Default side-effect | Default retry posture | Fixture |
|---|---|---|---|---|
| `contract.schema.SCHEMA_MALFORMED` | [EH-001](#eh-001) | `not_dispatched` | `after_condition_change` | [EHC-001](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `contract.schema.SCHEMA_MAJOR_UNSUPPORTED` | [EH-001](#eh-001) | `not_dispatched` | `after_condition_change` | [EHC-002](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `contract.schema.SCHEMA_CONDITION_UNSUPPORTED` | [EH-001](#eh-001) | `not_dispatched` | `after_condition_change` | [EHC-003](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.identity.PROVIDER_UNKNOWN` | [EH-002](#eh-002) | `not_dispatched` | `after_condition_change` | [EHC-004](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.identity.PROVIDER_UNTRUSTED` | [EH-002](#eh-002) | `not_dispatched` | `after_condition_change` | [EHC-005](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.identity.PROVIDER_VERSION_UNVALIDATED` | [EH-002](#eh-002) | `not_dispatched` | `after_condition_change` | [EHC-006](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.availability.PROVIDER_UNAVAILABLE` | [EH-003](#eh-003) | `unknown` | `reconcile_before_retry` | [EHC-007](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.availability.PROVIDER_RATE_LIMITED` | [EH-003](#eh-003) | `unknown` | `reconcile_before_retry` | [EHC-008](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `capability.validity.CAPABILITY_STALE` | [EH-004](#eh-004) | `not_dispatched` | `after_condition_change` | [EHC-009](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `capability.validity.CAPABILITY_REVOKED` | [EH-004](#eh-004) | `not_dispatched` | `after_condition_change` | [EHC-010](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `capability.validity.CAPABILITY_INCOMPATIBLE` | [EH-004](#eh-004) | `not_dispatched` | `after_condition_change` | [EHC-011](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `evidence.precondition.EVIDENCE_INSUFFICIENT` | [EH-005](#eh-005) | `not_dispatched` | `after_condition_change` | [EHC-012](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `evidence.precondition.PRECONDITION_FALSE` | [EH-005](#eh-005) | `not_dispatched` | `after_condition_change` | [EHC-013](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `evidence.precondition.PRECONDITION_UNKNOWN` | [EH-005](#eh-005) | `not_dispatched` | `after_condition_change` | [EHC-014](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `platform.permission.PLATFORM_GRANT_MISSING` | [EH-006](#eh-006) | `not_dispatched` | `after_condition_change` | [EHC-015](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `platform.permission.PLATFORM_GRANT_REVOKED` | [EH-006](#eh-006) | `not_dispatched` | `after_condition_change` | [EHC-016](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `governance.authorization.POLICY_DENIED` | [EH-007](#eh-007) | `not_dispatched` | `after_condition_change` | [EHC-017](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `governance.authorization.APPROVAL_EXPIRED` | [EH-007](#eh-007) | `not_dispatched` | `after_condition_change` | [EHC-018](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `governance.authorization.APPROVAL_MISMATCH` | [EH-007](#eh-007) | `not_dispatched` | `after_condition_change` | [EHC-019](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `governance.authorization.APPROVAL_REVOKED` | [EH-007](#eh-007) | `not_dispatched` | `after_condition_change` | [EHC-020](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.conflict.EXPECTED_REVISION_CONFLICT` | [EH-008](#eh-008) | `not_dispatched` | `after_condition_change` | [EHC-021](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.conflict.DEPENDENCY_VERSION_STALE` | [EH-008](#eh-008) | `not_dispatched` | `after_condition_change` | [EHC-022](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.conflict.IDEMPOTENCY_KEY_REUSE_MISMATCH` | [EH-008](#eh-008) | `not_dispatched` | `after_condition_change` | [EHC-023](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.budget.DEADLINE_EXCEEDED` | [EH-009](#eh-009) | `unknown` | `reconcile_before_retry` | [EHC-024](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.budget.RESOURCE_BUDGET_EXCEEDED` | [EH-009](#eh-009) | `unknown` | `reconcile_before_retry` | [EHC-025](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.budget.CANCELLED_BEFORE_DISPATCH` | [EH-009](#eh-009) | `unknown` | `reconcile_before_retry` | [EHC-026](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.dispatch.ADAPTER_DISPATCH_FAILED` | [EH-010](#eh-010) | `unknown` | `reconcile_before_retry` | [EHC-027](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.dispatch.DISPATCH_RECEIPT_MISSING` | [EH-010](#eh-010) | `unknown` | `reconcile_before_retry` | [EHC-028](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.outcome.OUTCOME_UNCERTAIN` | [EH-011](#eh-011) | `unknown` | `reconcile_before_retry` | [EHC-029](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.outcome.POSTCONDITION_UNVERIFIED` | [EH-011](#eh-011) | `unknown` | `reconcile_before_retry` | [EHC-030](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `operation.outcome.PROVIDER_RESULT_CONTRADICTED` | [EH-011](#eh-011) | `unknown` | `reconcile_before_retry` | [EHC-031](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.contract.PROVIDER_CONTRACT_VIOLATION` | [EH-012](#eh-012) | `unknown` | `reconcile_before_retry` | [EHC-032](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `provider.contract.PROVIDER_INTEGRITY_FAILURE` | [EH-012](#eh-012) | `unknown` | `reconcile_before_retry` | [EHC-033](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `runtime.internal.INTERNAL_FAILURE` | [EH-013](#eh-013) | `unknown` | `reconcile_before_retry` | [EHC-034](../../schemas/fixtures/error-handler-cases.fixture.json) |
| `runtime.internal.STORAGE_COMMIT_UNCERTAIN` | [EH-013](#eh-013) | `unknown` | `reconcile_before_retry` | [EHC-035](../../schemas/fixtures/error-handler-cases.fixture.json) |

## Production registration gate

An entry remains `seed` until all of the following exist and pass:

- Concrete handler implementation owned by the named component.
- Explicit input/output contract and durable disposition for every applicable branch.
- Positive, negative, conflict, replay, cancellation and recovery tests appropriate to the error.
- Proof that actual per-attempt side-effect state overrides defaults and that no blind retry is possible.
- Cross-language conformance where the handler crosses C++/Python boundaries.
- Integration into the runtime registry with an explicit registration lifecycle and rollback path.

The current 35 entries are mapped to these design contracts and have one schema-shaped payload fixture each. This closes the **design mapping** gap only. It does not close runtime handler implementation, code-specific recovery coverage, full JSON Schema validation, or production registration.
