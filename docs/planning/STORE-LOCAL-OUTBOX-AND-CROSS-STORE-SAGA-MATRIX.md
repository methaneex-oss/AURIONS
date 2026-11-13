# AURIONS — Store-Local Outbox and Cross-Store Saga Ownership

- **Status:** Builder transaction-boundary reconciliation; specified and structurally CI-checked, not runtime-validated.
- **Authority:** The owner-approved three-store architecture and cross-store commit protocol in `INITIAL-ENGINEERING-SPECIFICATION.md` §§26 and 32.1.
- **Purpose:** Ensure every authoritative store commits its own mutation and publication intent atomically, while cross-store workflows use durable sagas rather than impossible cross-file atomicity.
- **Boundary:** This document does not authorize dispatch, implementation or protected evolution activation.

## 1. Corrected architectural defect

The prior DDL had an `outbox` table only in `aurion_events.db`, while memory and governance commands were specified to mutate aggregates in their own databases. That contradicted the normative rule that the authoritative store must commit its state mutation and outbox row in the same SQLite transaction. A separate event database cannot provide that atomicity.

The correction is:
- `aurion_memory.db` owns a local `outbox`, added by migration v5.
- `aurion_governance.db` owns a local `outbox`, added by migration v2.
- `aurion_events.db` retains its local `outbox` for event-store-owned state and downstream dispatch.
- Each active command declares an explicit `transaction_contract`. Single-store commands use one local transaction; multi-store commands use a durable saga.
- The command registry binds every active command's authoritative `persistence_stores` to its local `outbox`. CI rejects a missing DDL table, missing binding or transaction-contract mismatch.

## 2. Store ownership and relay protocol

| Store | Authoritative state examples | Local outbox | Central archive role |
|---|---|---|---|
| `aurion_memory.db` | Experiences, representations, memory, beliefs, objectives, world/situation/means records, plans, outcomes, learning and evolution candidate state | `outbox` in memory migration v5 | Domain events are relayed after the local commit |
| `aurion_governance.db` | Policies, permissions, approvals, protected-change and disclosure audit | `outbox` in governance migration v2 | Governance events are relayed after the local commit |
| `aurion_events.db` | Event archive/receipts, operations, task runs/checkpoints and recovery journal | Existing `outbox` in event base schema | Central append-only archive and dispatch/recovery coordinator |

The publication protocol is:

1. The authoritative store validates owner scope, expected revision and command semantics.
2. It commits the aggregate mutation and immutable outbox envelope in one local transaction. If the transaction fails, neither survives.
3. A relay reads pending local outbox rows and appends the envelope to the central event archive using stable message/event IDs and payload digest.
4. Archive ingestion is idempotent. Duplicate message ID plus identical digest is acknowledged; the same ID with a different digest is a protocol-integrity error.
5. The source outbox is marked published only after the central archive has durably acknowledged the message.
6. Consumers apply their own state mutation and inbox receipt in one local transaction when both are in one store. Cross-store consumer effects use a saga and reconciliation.
7. Delivery is at least once. Exactly-once transport is not claimed; idempotent effects and durable reconciliation are required.

A relay failure leaves the source outbox pending. It does not roll back a committed domain mutation, report that mutation as uncommitted, or trigger a duplicate domain write. The central event-store outbox is not a substitute for the source store's local outbox.

## 3. Command-level transaction classification

`persistence_stores` identifies authoritative stores whose durable state is changed or coordinated by the command. Every listed store must have a local outbox binding. `table_bindings` may additionally name read dependencies and central archive tables; it does not imply that every listed table is written in the same transaction. The `transaction_contract` field is the authoritative statement of the transaction boundary.

| Command | Authoritative stores / coordinator | Boundary | Required local outbox | Archive / event role |
|---|---|---|---|---|
| `experience.submit` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `representation.create` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `context.assemble` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `context.invalidate` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `environment.observe` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `capability.discover` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `capability.verify` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `capability.invalidate` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `capability.knowledge.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `capability.knowledge.revise` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `memory.retrieve` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `belief.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `belief.revise` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `prediction.create` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `prediction.evaluate` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `appraisal.evaluate` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `attention.allocate` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `reasoning.assess` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `goal.create` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `goal.revise` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `goal.cancel` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `plan.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `plan.revise` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `plan.checkpoint` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `decision.record` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `operation.propose` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `operation.cancel` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `operation.reconcile` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `approval.request` | aurion_governance.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_governance.db:outbox | event-store-owned event/operation state |
| `approval.decide` | aurion_governance.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_governance.db:outbox | event-store-owned event/operation state |
| `approval.revoke` | aurion_governance.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_governance.db:outbox | event-store-owned event/operation state |
| `outcome.evaluate` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `learning.update.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `learning.experiment.submit` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `learning.candidate.evaluate` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `self_model.update.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `evolution.change.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | central event archive referenced; relay is asynchronous |
| `evolution.candidate.evaluate` | aurion_memory.db, aurion_events.db | CROSS_STORE_SAGA | aurion_memory.db:outbox, aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `evolution.candidate.activate` | aurion_memory.db, aurion_governance.db, aurion_events.db | CROSS_STORE_SAGA | aurion_memory.db:outbox, aurion_governance.db:outbox, aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `evolution.candidate.rollback` | aurion_memory.db, aurion_governance.db, aurion_events.db | CROSS_STORE_SAGA | aurion_memory.db:outbox, aurion_governance.db:outbox, aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `task.start` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `task.pause` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `task.resume` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `task.cancel` | aurion_events.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_events.db:outbox | central event archive referenced; relay is asynchronous |
| `device.pair` | — | DEFERRED | none — deferred | event-store-owned event/operation state |
| `device.revoke` | — | DEFERRED | none — deferred | event-store-owned event/operation state |
| `objective.create` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `objective.revise` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `world.entity.observe` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `world.relationship.revise` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `situation.snapshot.create` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `means.affordance.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `interaction.propose` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |
| `interaction.outcome.record` | aurion_memory.db | SINGLE_STORE_LOCAL_OUTBOX | aurion_memory.db:outbox | event-store-owned event/operation state |

## 4. Cross-store saga contracts

Only three currently mapped command types declare more than one authoritative store. They remain design-only/non-dispatchable.

### 4.1 `evolution.candidate.evaluate`

- **Stores:** memory state plus event/recovery coordinator. Governance policy/approval tables are read dependencies, not writes.
- **Coordinator intent:** create a durable operation/recovery-journal record bound to candidate ID, artifact digest, frozen baseline, held-out dataset revision and evaluation request digest.
- **Domain commit:** append the immutable candidate evaluation in memory and its memory-local outbox in one transaction. Candidate remains quarantined; evaluation cannot activate it.
- **Completion:** coordinator records the memory receipt and archive publication state. An interrupted evaluation remains pending/uncertain until the exact evaluation is reconciled; retry cannot create a second evaluation for the same idempotency scope.
- **Forbidden:** candidate activation, policy mutation or promotion based only on a worker result.

### 4.2 `evolution.candidate.activate`

- **Stores:** memory active-candidate state, governance approval/audit state, and event/recovery coordinator.
- **Preconditions:** exact candidate and active-pointer revisions; passing evaluation for the exact artifact digest; verified provenance/signature; rollback readiness; current explicit owner/governance grant.
- **Saga order:** (1) coordinator records activation intent and expected revisions; (2) governance validates the exact approval and durably records its use/activation authorization with its local outbox; (3) memory validates the still-current candidate/pointer and commits the active-pointer transition with its local outbox; (4) coordinator reconciles both local receipts and records completion.
- **Interruption:** no global atomicity is claimed. The coordinator blocks a competing activation while the saga is unresolved. Recovery repeats idempotent steps or performs an explicit compensating/rollback operation. A partial saga is never reported as fully activated.
- **Forbidden:** model self-approval, stale approval, silent pointer change, deletion of failed candidates or treating a provider/worker receipt as evaluation acceptance.

### 4.3 `evolution.candidate.rollback`

- **Stores:** memory active-candidate state, governance rollback-authorization/audit state, and event/recovery coordinator.
- **Preconditions:** exact current active-pointer revision, exact prior approved artifact digest, verified artifact integrity and explicit rollback authority.
- **Saga order:** (1) coordinator records rollback intent; (2) governance validates rollback authority and commits the rollback authorization/audit record with its local outbox; (3) memory restores the exact prior artifact pointer and commits its local outbox; (4) coordinator reconciles both local receipts and records completion.
- **Interruption:** no global atomicity is claimed. The saga remains unresolved until the pointer and governance audit agree. Recovery is idempotent; compensation is a separate explicit operation.
- **Forbidden:** deleting the failed candidate, restoring an unverified digest, or claiming rollback complete before reconciliation.

**Remaining limitation:** These saga sequences are builder contract proposals. They require semantic review, handler implementation, crash/replay/fault injection and independent verification before dispatchability. The registry's current multi-store entries remain blocked on those tests.

## 5. Verification and evidence boundary

Current code-level guards:
- Each of the three SQLite DDL chains must define a local `outbox` table.
- Each command's authoritative `persistence_stores` must have an `outbox` table binding.
- One-store commands must declare `SINGLE_STORE_LOCAL_OUTBOX`.
- Multi-store commands must declare `CROSS_STORE_SAGA` and bind the event/recovery coordinator's `operations`, `recovery_journal` and `outbox`.
- The SQLite smoke validator executes memory v5 and governance v2 and performs rollback probes showing a memory aggregate + outbox and governance policy + outbox roll back together.

**Not established:** actual outbox relay code, central archive ingestion/deduplication under crash, consumer inbox behaviour, multi-store saga runtime, compensation, power-loss safety, target Android/Termux behaviour or production handlers. Host rollback probes establish only that the same SQLite transaction can roll back both rows in the same database.

All commands and events remain design-only/non-dispatchable. No implementation authorization or protected activation authority is created.
