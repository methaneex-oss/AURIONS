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

### 2.1 Table-binding roles and write boundaries

The command registry distinguishes authoritative writes from read-only dependencies and asynchronous publication destinations. `persistence_stores` names only the stores whose state is mutated by the command; it does not include stores that are consulted or populated later by an outbox relay.

| Binding role | Meaning | Required invariant |
|---|---|---|
| `authoritative_write` | Store is listed in `persistence_stores`; command owns a state transition there. | The aggregate mutation and that store's local outbox commit in one transaction. |
| `read_dependency` | Store is consulted for policy, approval, descriptor or other evidence; no row is mutated by this command. | Binding must not include an outbox table; no write or receipt is implied. |
| `async_archive` | Central event archive receives the source store's outbox envelope asynchronously. | Used only for `aurion_events.db` with `events` and `outbox`; it is not part of a single-store source transaction. |
| `read_projection` | Query reads an authoritative store to produce a result. | Query is read-only; every bound table must exist in the declared store's DDL. |

This distinction is machine-enforced by the registry schema and validator. Every table binding carries a role; all bound table names must exist in the ordered DDL for that store; every authoritative write store must have a local outbox binding; read dependencies cannot claim an outbox; and query bindings must be read projections. The central event archive is not misrepresented as a synchronous write for single-store commands.

In particular, `evolution.change.propose` and `evolution.candidate.evaluate` read governance approval/policy evidence without writing the governance store. `evolution.candidate.evaluate` writes only memory state and its local outbox, with the event/recovery coordinator as its second authoritative saga store. Activation and rollback explicitly write all three stores and remain durable sagas.

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
| `evolution.candidate.evaluate` | aurion_memory.db, aurion_events.db | CROSS_STORE_SAGA | aurion_memory.db:outbox, aurion_events.db:outbox | coordinator: operations + operation_steps + recovery_journal; archive relay asynchronous |
| `evolution.candidate.activate` | aurion_memory.db, aurion_governance.db, aurion_events.db | CROSS_STORE_SAGA | aurion_memory.db:outbox, aurion_governance.db:outbox, aurion_events.db:outbox | coordinator: operations + operation_steps + recovery_journal; archive relay asynchronous |
| `evolution.candidate.rollback` | aurion_memory.db, aurion_governance.db, aurion_events.db | CROSS_STORE_SAGA | aurion_memory.db:outbox, aurion_governance.db:outbox, aurion_events.db:outbox | coordinator: operations + operation_steps + recovery_journal; archive relay asynchronous |
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
- **Coordinator intent:** create a durable operation plus ordered `operation_steps` row bound to candidate ID, artifact digest, frozen baseline, held-out dataset revision, target store, stable step key, per-target idempotency key, request digest and expected revision. The matching `recovery_journal.operation_step_id` links local commit evidence to that exact step.
- **Domain commit:** append the immutable candidate evaluation in memory and its memory-local outbox in one transaction. Candidate remains quarantined; evaluation cannot activate it.
- **Completion:** coordinator records the memory receipt and archive publication state. An interrupted evaluation remains pending/uncertain until the exact evaluation is reconciled; retry cannot create a second evaluation for the same idempotency scope.
- **Forbidden:** candidate activation, policy mutation or promotion based only on a worker result.

### 4.2 `evolution.candidate.activate`

- **Stores:** memory active-candidate state, governance approval/audit state, and event/recovery coordinator.
- **Preconditions:** exact candidate and active-pointer revisions; passing evaluation for the exact artifact digest; verified provenance/signature; rollback readiness; current explicit owner/governance grant.
- **Saga order:** (1) coordinator records activation intent and ordered step identities/expected revisions; (2) governance validates the exact approval and durably records its use/activation authorization with its local outbox; (3) memory validates the still-current candidate/pointer and commits the active-pointer transition with its local outbox; (4) each local commit is linked to its immutable coordinator step and recovery-journal record; (5) coordinator reconciles both local receipts and records completion.
- **Interruption:** no global atomicity is claimed. The coordinator blocks a competing activation while the saga is unresolved. Recovery repeats idempotent steps or performs an explicit compensating/rollback operation. A partial saga is never reported as fully activated.
- **Forbidden:** model self-approval, stale approval, silent pointer change, deletion of failed candidates or treating a provider/worker receipt as evaluation acceptance.

### 4.3 `evolution.candidate.rollback`

- **Stores:** memory active-candidate state, governance rollback-authorization/audit state, and event/recovery coordinator.
- **Preconditions:** exact current active-pointer revision, exact prior approved artifact digest, verified artifact integrity and explicit rollback authority.
- **Saga order:** (1) coordinator records rollback intent and ordered step identities/expected revisions; (2) governance validates rollback authority and commits the rollback authorization/audit record with its local outbox; (3) memory restores the exact prior artifact pointer and commits its local outbox; (4) each local commit is linked to its immutable coordinator step and recovery-journal record; (5) coordinator reconciles both local receipts and records completion.
- **Interruption:** no global atomicity is claimed. The saga remains unresolved until the pointer and governance audit agree. Recovery is idempotent; compensation is a separate explicit operation.
- **Forbidden:** deleting the failed candidate, restoring an unverified digest, or claiming rollback complete before reconciliation.

**Remaining limitation:** These saga sequences are builder contract proposals. They require semantic review, handler implementation, crash/replay/fault injection and independent verification before dispatchability. The registry's current multi-store entries remain blocked on those tests.

### 4.4 Dataset-source revocation impact

- **Stores:** governance authorization/revocation state, memory-owned dataset manifests and derived-artifact impact findings, and the existing events/recovery coordinator.
- **Coordinator intent:** create or resume one stable operation keyed to the exact authorization ID, authorization-record digest and revocation reference. Persist ordered steps, deterministic step identities, per-store idempotency keys, expected revisions and recovery-journal links in the existing `operations`, `operation_steps` and `recovery_journal` tables.
- **Revocation commit:** governance validates the authenticated owner/approval and exact authorization version, then appends the revocation record and governance-local outbox in one transaction. From this commit onward, admission checks consult authoritative governance state and fail closed even if event relay is delayed.
- **Impact scan:** memory resolves manifests and source-membership rows by authorization ID/digest, records immutable impact findings, identifies derived artifacts and worker attempts, and quarantines affected not-yet-used inputs/outputs according to policy. It commits findings and its memory-local outbox atomically.
- **Worker disposition:** the learning supervisor requests safe cancellation for active attempts. Unresponsive or uncertain attempts remain uncertain; partial outputs remain quarantined. A worker never decides whether rights are valid.
- **Completion:** the coordinator reconciles governance and memory receipts and emits `dataset.revocation.impact.assessed.v1` only after the impact assessment is durable. Unknown influence remains explicit. Retraining, unlearning assessment or candidate rollback requires a separate governed disposition.
- **Interruption:** replay uses the same operation/step/idempotency identities. A stale memory projection cannot override a committed governance revocation. No global transaction or automatic removal of training influence is claimed.
- **Migration decision:** the current events base schema already provides `operations`, `operation_steps`, `recovery_journal` and an events-local `outbox`; no events-store migration is justified unless a concrete missing field is identified during validator/DDL integration.

### 4.5 D-02 selective synchronization local persistence

- **Authoritative aggregate store:** `aurion_memory.db` owns the cognitive aggregates and the local outbox row committed with each eligible local aggregate revision. Its outbox publishes the domain event to the central event archive; it is not itself the peer-transport export ledger.
- **Builder-proposed local transport records:** the D-02 contract allocates immutable export records and export-transition history, destination inbox/idempotency receipts, quarantine evidence, peer acknowledgements bound to exact export/change/digest identity, append-only causal-gap events, immutable conflict records and owner resolutions, immutable tombstones and per-peer tombstone receipts, and append-only restore events carrying required/applied tombstone frontiers. These records are local to the memory store and are not synchronized.
- **Atomic receiver boundary:** destination aggregate mutation, its inbox receipt and the memory-local outbox publication intent must commit in one destination-memory transaction. A duplicate with the same change identity and digest returns the original receipt; a digest mismatch is quarantined without a second aggregate mutation.
- **Events store:** `aurion_events.db` remains the central event archive and generic saga/recovery coordinator. Its event-consumer receipts are not substitutes for domain-level sync inbox receipts. No additional events-store migration is justified by the current D-02 contract.
- **Governance store:** `aurion_governance.db` remains authoritative for owner authorization and any future accepted peer-trust decisions. The memory store holds only opaque references; key bytes, credentials and pairing secrets remain local-only. Peer bootstrap, trust and cryptographic lifecycle remain separate security/owner gates.
- **DDL status (superseding update — 2026-11-18):** Memory migration v10 is present in the ordered three-store chain. The chain contains 21 SQL files: three base schemas plus Memory v2…v10, Events v2…v6 and Governance v2…v5. Exact-current-head CI run [44319335286](https://github.com/methaneex-oss/AURIONS/actions/runs/44319335286) on `fb91e63314537f6b06630c45c700b6713b44b208` passed the SQLite DDL/migration smoke-test step on host SQLite 3.46.1. This supersedes the earlier twenty-file/v10-pending status in this section. No cross-file foreign keys or distributed ACID transaction are proposed. Runtime relay, receiver, peer-trust, key lifecycle and recovery handlers remain unimplemented.

## 5. Verification and evidence boundary

Current code-level guards:
- Each of the three SQLite DDL chains must define a local `outbox` table.
- Each command's authoritative `persistence_stores` must have an `outbox` table binding.
- One-store commands must declare `SINGLE_STORE_LOCAL_OUTBOX`.
- Multi-store commands must declare `CROSS_STORE_SAGA` and bind the event/recovery coordinator's `operations`, `operation_steps`, `recovery_journal` and `outbox`.
- The SQLite smoke validator executes all three base schemas and 18 ordered migrations: memory v2…v10, events v2…v6 and governance v2…v5 (21 SQL files total). It checks FK/integrity validity after each file; memory v4 interaction/objective, v8 model-lineage/pointer, v9 dataset-manifest/source-membership/split/seal/admission/revocation-impact and v10 selective-sync persistence invariants; event v3…v6 operation/step/recovery invariants; governance v3/v4 exact-approval and query-projection invariants; governance v5 immutable source-authorization/append-only revocation invariants; and local-outbox rollback. Exact-current-head workflow [44319335286](https://github.com/methaneex-oss/AURIONS/actions/runs/44319335286) on `fb91e63314537f6b06630c45c700b6713b44b208` passed all nine substantive workflow steps, including the 21-file host SQLite 3.46.1 DDL/migration smoke tests. This is host-side schema/DDL evidence only; it does not establish target Termux/Android behavior, crash/replay/fault recovery, runtime relay/consumer handlers or production workflows.

**Not established:** actual outbox relay code, central archive ingestion/deduplication under crash, consumer inbox behaviour, multi-store saga runtime, compensation execution, crash/replay fault injection, power-loss safety, target Android/Termux behaviour or production handlers. Host rollback probes establish only that the same SQLite transaction can roll back both rows in the same database.

All commands and events remain design-only/non-dispatchable. No implementation authorization or protected activation authority is created.
