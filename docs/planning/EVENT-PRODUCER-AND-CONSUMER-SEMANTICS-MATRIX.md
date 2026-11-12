# AURIONS — Event Producer and Consumer Semantics Matrix

**Status:** Builder reconciliation artifact; specified, not runtime-validated.  
**Authority:** The event registry and command registry remain design-only. This matrix makes command-to-event producer bindings explicit and records unresolved producer/consumer contracts without inventing them.

## 1. Binding rules

- `command_producers` is the exact set of command registry entries whose `emitted_event_bindings` names the event. The validator enforces this relationship in both directions.
- `command_producer_binding_status: bound` means at least one command producer is explicitly declared. It does **not** establish the complete event producer set; platform ingress, internal domain transitions, workers, sync and owner interactions are not assumed or excluded.
- `command_producer_binding_status: unresolved` means no command producer is currently bound. It does **not** mean the event is invalid or that no producer exists.
- All events remain `design_only_not_dispatchable`. A producer binding does not create a handler, consumer, authorization, owner transition, or dispatch permission.
- Every event still requires event-specific producer trigger/ownership, consumer semantics, owner transition, event-specific acceptance assertions, and executable replay/restart/fault evidence.

## 2. Inventory

| Event type | Command producer binding | Payload schema | Consumer / owner transition |
|---|---|---|---|
| `appraisal.updated.v1` | `appraisal.evaluate` | `appraisalUpdated` | UNRESOLVED |
| `approval.decided.v1` | UNRESOLVED — no command producer bound | `approvalDecision` | UNRESOLVED |
| `approval.requested.v1` | `approval.request` | `approvalRequested` | UNRESOLVED |
| `approval.revoked.v1` | `approval.revoke` | `approvalRevoked` | UNRESOLVED |
| `artifact.deleted.v1` | UNRESOLVED — no command producer bound | `artifactManifest` | UNRESOLVED |
| `artifact.quarantined.v1` | UNRESOLVED — no command producer bound | `artifactManifest` | UNRESOLVED |
| `artifact.registered.v1` | UNRESOLVED — no command producer bound | `artifactManifest` | UNRESOLVED |
| `attention.allocated.v1` | `attention.allocate` | `attentionAllocated` | UNRESOLVED |
| `belief.proposed.v1` | `belief.propose` | `beliefRevision` | UNRESOLVED |
| `belief.revised.v1` | `belief.revise` | `beliefRevision` | UNRESOLVED |
| `candidate.activated.v1` | `evolution.candidate.activate` | `evolutionCandidateLifecycle` | UNRESOLVED |
| `candidate.rolled_back.v1` | `evolution.candidate.rollback` | `evolutionCandidateLifecycle` | UNRESOLVED |
| `capability.discovered.v1` | `capability.discover` | `capabilityDescriptorRecord` | UNRESOLVED |
| `capability.invalidated.v1` | `capability.invalidate` | `capabilityDescriptorRecord` | UNRESOLVED |
| `capability.knowledge.proposed.v1` | `capability.knowledge.propose` | `capabilityKnowledgeRevision` | UNRESOLVED |
| `capability.knowledge.revised.v1` | `capability.knowledge.revise` | `capabilityKnowledgeRevision` | UNRESOLVED |
| `capability.revoked.v1` | UNRESOLVED — no command producer bound | `capabilityDescriptorRecord` | UNRESOLVED |
| `capability.verified.v1` | `capability.verify` | `capabilityDescriptorRecord` | UNRESOLVED |
| `context.assembled.v1` | `context.assemble` | `contextSnapshot` | UNRESOLVED |
| `context.invalidated.v1` | `context.invalidate` | `contextInvalidated` | UNRESOLVED |
| `decision.recorded.v1` | `decision.record` | `decisionRecorded` | UNRESOLVED |
| `disclosure.recorded.v1` | UNRESOLVED — no command producer bound | `externalDisclosureRecord` | UNRESOLVED |
| `environment.observed.v1` | `environment.observe` | `environmentObserved` | UNRESOLVED |
| `evidence.recorded.v1` | `experience.submit` | `evidenceItem` | UNRESOLVED |
| `evolution.candidate.evaluated.v1` | `evolution.candidate.evaluate` | `evolutionCandidateLifecycle` | UNRESOLVED |
| `evolution.proposed.v1` | `evolution.change.propose` | `evolutionProposed` | UNRESOLVED |
| `experience.observed.v1` | `experience.submit` | `experienceObserved` | UNRESOLVED |
| `goal.created.v1` | `goal.create` | `goalRevision` | UNRESOLVED |
| `goal.revised.v1` | `goal.cancel`, `goal.revise` | `goalRevision` | UNRESOLVED |
| `interaction.outcome.observed.v1` | `interaction.outcome.record` | `interactionOutcome` | UNRESOLVED |
| `interaction.proposed.v1` | `interaction.propose` | `interactionProposal` | UNRESOLVED |
| `learning.candidate.evaluated.v1` | `learning.candidate.evaluate` | `learningCandidateEvaluated` | UNRESOLVED |
| `learning.experiment.completed.v1` | UNRESOLVED — no command producer bound | `learningExperimentCompleted` | UNRESOLVED |
| `learning.update.accepted.v1` | UNRESOLVED — no command producer bound | `learningUpdate` | UNRESOLVED |
| `learning.update.proposed.v1` | `learning.update.propose` | `learningUpdate` | UNRESOLVED |
| `means.affordance.proposed.v1` | `means.affordance.propose` | `affordanceHypothesis` | UNRESOLVED |
| `memory.recorded.v1` | UNRESOLVED — no command producer bound | `memoryRecord` | UNRESOLVED |
| `memory.retrieved.v1` | `memory.retrieve` | `memoryRetrieval` | UNRESOLVED |
| `objective.created.v1` | `objective.create` | `objective` | UNRESOLVED |
| `objective.revised.v1` | `objective.revise` | `objectiveRevision` | UNRESOLVED |
| `operation.awaiting_approval.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.cancel_requested.v1` | `operation.cancel` | `operationLifecycleEvent` | UNRESOLVED |
| `operation.cancelled.v1` | `operation.cancel` | `operationLifecycleEvent` | UNRESOLVED |
| `operation.compensated.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.compensating.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.compensation_required.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.dispatched.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.expired.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.failed.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.manual_intervention.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.proposed.v1` | `operation.propose` | `operationLifecycleEvent` | UNRESOLVED |
| `operation.ready.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.reconciled.v1` | `operation.reconcile` | `operationLifecycleEvent` | UNRESOLVED |
| `operation.reconciling.v1` | `operation.reconcile` | `operationLifecycleEvent` | UNRESOLVED |
| `operation.rejected.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.revoked.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.running.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.succeeded.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.uncertain.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `operation.validating.v1` | UNRESOLVED — no command producer bound | `operationLifecycleEvent` | UNRESOLVED |
| `outcome.evaluated.v1` | `outcome.evaluate` | `outcomeEvaluation` | UNRESOLVED |
| `outcome.observed.v1` | UNRESOLVED — no command producer bound | `outcomeObserved` | UNRESOLVED |
| `permission.evaluated.v1` | UNRESOLVED — no command producer bound | `permissionEvaluated` | UNRESOLVED |
| `plan.checkpointed.v1` | `plan.checkpoint` | `taskCheckpointDetails` | UNRESOLVED |
| `plan.proposed.v1` | `plan.propose` | `planRevision` | UNRESOLVED |
| `plan.revised.v1` | `plan.revise` | `planRevision` | UNRESOLVED |
| `prediction.created.v1` | `prediction.create` | `predictionCreated` | UNRESOLVED |
| `prediction.evaluated.v1` | `prediction.evaluate` | `predictionEvaluation` | UNRESOLVED |
| `reasoning.hypothesis.proposed.v1` | `reasoning.assess` | `reasoningHypothesisProposed` | UNRESOLVED |
| `representation.created.v1` | `representation.create` | `representationCreated` | UNRESOLVED |
| `representation.revised.v1` | UNRESOLVED — no command producer bound | `representationRevised` | UNRESOLVED |
| `retention.deletion.completed.v1` | UNRESOLVED — no command producer bound | `retentionDeletionEvent` | UNRESOLVED |
| `retention.deletion.requested.v1` | UNRESOLVED — no command producer bound | `retentionDeletionEvent` | UNRESOLVED |
| `self_model.update.proposed.v1` | `self_model.update.propose` | `selfModelUpdateProposed` | UNRESOLVED |
| `self_model.updated.v1` | UNRESOLVED — no command producer bound | `selfModelUpdated` | UNRESOLVED |
| `situation.snapshot.created.v1` | `situation.snapshot.create` | `situation` | UNRESOLVED |
| `sync.change.applied.v1` | UNRESOLVED — no command producer bound | `syncChange` | UNRESOLVED |
| `sync.change.exported.v1` | UNRESOLVED — no command producer bound | `syncChange` | UNRESOLVED |
| `sync.conflict.detected.v1` | UNRESOLVED — no command producer bound | `syncConflictRecord` | UNRESOLVED |
| `sync.conflict.resolved.v1` | UNRESOLVED — no command producer bound | `syncConflictRecord` | UNRESOLVED |
| `sync.tombstone.applied.v1` | UNRESOLVED — no command producer bound | `syncChange` | UNRESOLVED |
| `task.control.requested.v1` | `task.start` | `taskControlRequest` | UNRESOLVED |
| `task.run.transitioned.v1` | `task.start` | `taskRunTransition` | UNRESOLVED |
| `worker.job.completed.v1` | UNRESOLVED — no command producer bound | `workerResult` | UNRESOLVED |
| `worker.job.failed.v1` | UNRESOLVED — no command producer bound | `workerFailure` | UNRESOLVED |
| `worker.job.progressed.v1` | UNRESOLVED — no command producer bound | `workerProgress` | UNRESOLVED |
| `worker.job.requested.v1` | `learning.experiment.submit` | `workerRequest` | UNRESOLVED |
| `world.entity.observed.v1` | `world.entity.observe` | `entity` | UNRESOLVED |
| `world.relationship.revised.v1` | `world.relationship.revise` | `relationshipRevision` | UNRESOLVED |

## 3. Required closure per event

Before an event can be considered implementation-ready, its owning component must define:

1. **Production trigger and owner:** exact state transition or trusted ingress that creates the event; command, platform, worker, sync or internal transition origin; authenticated owner/actor and scope.
2. **Aggregate and revision:** authoritative aggregate, expected/current revision rule, event sequence allocation, causation/correlation identifiers and ordering scope.
3. **Atomicity:** exact owning-store transaction that commits the state mutation with immutable event/outbox; cross-store work must use durable saga semantics, not a distributed-transaction claim.
4. **Consumer contract:** named consumer, accepted event/schema versions, idempotency key, duplicate/replay behaviour, ordering and gap recovery, poison-message/quarantine policy, and bounded retry/reconciliation.
5. **Authority and data handling:** whether the transition is merely observational, proposal-producing, governance-affecting or externally consequential; owner authorization, classification, redaction and retention requirements.
6. **Failure and recovery:** crash points before/after commit, duplicate delivery, stale revision, missing predecessor, unknown version, partial cross-store completion, cancellation and restart.
7. **Event-specific acceptance:** positive and negative assertions over durable state, emitted event/outbox count, consumer effects, no unauthorized transition and no false outcome claim.

## 4. Current measured gap

- Total registered events: **89**.
- Events with one or more explicit command producers: **51**.
- Events with no command producer binding: **38**.
- All events still carry the unresolved bindings `runtime_handler`, `consumer_semantics`, `owner_transition` and `event_specific_acceptance`.
- The command producer crosswalk is machine-enforced against `schemas/command-query-registry.v1.json`; it is not semantic or runtime validation.
- No event is dispatchable. No handler/consumer implementation, transaction execution, replay/restart test or independent review is claimed.

## 5. Decision and implementation boundary

This matrix does not choose a producer for an unbound event, invent consumer ownership, change event names or payloads, promote dispatch status, select a runtime topology, or authorize production implementation. Where an event requires an owner-reserved product, platform or authority decision, the dependency remains explicit for the owner.
