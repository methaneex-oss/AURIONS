# AURIONS — Cognitive Mechanism and Interaction Architecture

- **Status:** Builder design proposal; IN PROGRESS until reconciled with the complete contract set and independently reviewed.
- **Purpose:** Specify how cognitive mechanisms interact to produce persistent, experience-dependent change under the foundational [Open-World Interaction and Means Architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md).
- **Governing principle:** Engineer the mechanisms; let behaviour be acquired through experience.
- **Non-goal:** This is not a hardcoded behavioural script, a fixed stimulus-to-response table, or a rigid linear pipeline.

## 1. Architectural requirement

AURIONS must not consist of a collection of isolated subsystems that merely expose names such as memory, prediction, reasoning or learning. The mechanisms must exchange evidence and state through explicit contracts and interact in a continuing, conditional, interruptible process.

The central requirement is **persistent experience-dependent adaptation**: observations and consequences must be capable of changing the system's future representations, beliefs, predictions, attention allocation, strategies, plans and context-dependent means/affordance reasoning. Changes must be traceable to evidence, evaluated in context and retained across restart when they are durable.

The system must not claim that it has learned merely because it stored a conversation, changed a memory record, revised a belief, executed a training job or lowered training loss. Those are distinct events and need distinct evidence.

## 2. Operating model: recurrent, event-driven cognition

The cognitive system is a recurrent set of interacting mechanisms coordinated by an orchestration/runtime layer. Its task and interaction model is objective-led and world/context grounded; it must not assume that a device, platform adapter, connector or registered capability is the universal source or route for action.

A useful conceptual view is:

**Experience and observation ↔ representation and context ↔ memory, knowledge and beliefs ↔ prediction, appraisal and attention ↔ reasoning ↔ goals, planning and decision ↔ governed action ↔ observed consequences ↔ evaluation and learning ↔ revised future processing.**

The arrows are not a prescribed execution sequence. Mechanisms can:
- Run concurrently when their inputs are available.
- Revisit earlier interpretations when new evidence arrives.
- Interrupt or suspend work when urgency, risk, resources or new evidence changes.
- Trigger rediscovery, retrieval, replanning or owner clarification.
- Produce partial results with uncertainty rather than blocking the entire cognitive cycle.
- Resume from durable checkpoints after process death.

The orchestrator coordinates work and resource budgets; it does not encode the system's desired conclusions or hardcode task-specific behaviour.

## 3. Shared state and ownership

Every state domain has one authoritative owner. Other mechanisms consume it through contracts and publish proposals/events rather than writing directly into another subsystem's records.

| State domain | Authoritative owner | Key content |
|---|---|---|
| Raw observations and experiences | Experience subsystem | Source, time, context, raw/normalized observation references, sensitivity and provenance |
| Representations | Representation subsystem | One or more interpretations, features, relations, uncertainty and source links |
| Active context and situation model | Context/world-understanding mechanisms | Relevant entities, actors, resources, relations, temporal/spatial/social/task context, state claims, unknowns, conflicts and confidence |
| Durable episodic memory | Memory subsystem | Experiences, events, associations, retrieval metadata and retention |
| Consolidated knowledge | Knowledge subsystem | Generalized information with source lineage and validity scope |
| Propositions and evidence | Belief subsystem | Claims, evidence, support/contradiction, epistemic status and revision history |
| Predictions | Prediction subsystem | Predicted outcome, horizon, conditions, confidence and immutable original record |
| Appraisal state | Appraisal subsystem | Context-sensitive estimates relevant to significance, urgency, opportunity, uncertainty and potential consequence |
| Attention allocation | Attention subsystem | Current allocation, selection rationale, resource cost and interruptions |
| Goals and plans | Goal/planning subsystem | Owner objectives, derived goals, versions, dependencies, budgets and checkpoints |
| Possible means / affordance hypotheses | Means-reasoning mechanisms | Context-dependent actor/resource/interactions, preconditions, effects, authority requirements, evidence, uncertainty and scope; not a closed capability registry |
| Decision records | Decision subsystem | Selected/deferred/rejected option, rationale, uncertainty and policy handoff |
| Interaction proposals and outcomes | Interaction/runtime boundary | Objective, actors/targets, proposed effects, authority context, exact execution binding where applicable, receipts, independently observed effects and reconciliation |
| Learning hypotheses and updates | Learning subsystem | Evidence, target mechanism, hypothesis, baseline, candidate update and evaluation |
| Self-model | Self-model subsystem | Capabilities, limitations, confidence, resource profile and measured performance |
| Structural change candidates | Evolution subsystem | Proposed mechanism/architecture change, isolation, comparison, approval and rollback |

Cross-domain references use stable IDs and explicit provenance. A consumer cannot mutate an owner's state by editing a shared object or directly writing its tables.


## 3.1 Open-world objective and interaction contract boundary

The cognitive mechanisms consume the objective, entity, relationship, situation, evidence, affordance-hypothesis, interaction-proposal and interaction-outcome concepts defined in [Open-World Interaction and Means Architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md). Their initial machine-readable design baseline is `schemas/world-interaction.v1.schema.json`, with a non-device, human-mediated scenario in `schemas/fixtures/world-interaction.fixture.json`. These contracts are intentionally design-only and non-dispatchable.

The objective is not a plan. An affordance hypothesis is not an executable operation or permission. An interaction proposal is not authorization. A provider receipt is not independent proof of an outcome. The runtime must preserve these distinctions through contract validation, persistence, governance and evaluation. The means model must allow zero, one or many possible routes, including routes involving people or resources that are not represented by device capability descriptors.

The current schema is an initial typed baseline, not a complete semantic closure: stable identifiers, temporal validity, cross-record referential integrity, ownership/retention rules, event bindings, command/query ownership and SQL migrations still require reconciliation and verification.

## 4. Mechanism contracts

### 4.1 Experience and observation

**Purpose:** Capture what was observed or experienced without silently asserting that the observation is true or complete.

**Inputs:** User interaction, environment observations, tool/provider receipts, sensor inputs when explicitly enabled, prior task outcomes and internal system events.

**Outputs:** Durable or transient experience records, source metadata, capture limitations, sensitivity classification and references for downstream representation.

**Invariants:**
- Preserve source and capture time.
- Distinguish direct observation, user assertion, model interpretation, external content and inferred result.
- Preserve uncertainty, missing data and possible corruption.
- Do not grant authority to untrusted content.
- Apply retention and deletion policy before indexing or external use.

### 4.2 Representation

**Purpose:** Construct useful interpretations of experiences for downstream processing.

**Inputs:** Experiences, available context, relevant memory/knowledge, modality-specific representations and processing constraints.

**Outputs:** One or more representation hypotheses, entity/relationship references, feature structures, confidence/uncertainty and links to source evidence.

**Invariants:**
- A representation is not the source observation.
- Multiple interpretations may coexist.
- Later evidence may revise or supersede an interpretation without rewriting source history.
- Transformations retain provenance and model/algorithm version.

### 4.3 Context

**Purpose:** Maintain the current relevant situation assembled from observations, representations, task state, memory and environment constraints.

**Inputs:** New observations, representations, active goals, retrieved memories, device/environment state and task events.

**Outputs:** Versioned context snapshots or deltas with temporal validity, relevance, source links and uncertainty.

**Invariants:**
- Context is task- and time-sensitive, not a universal global prompt.
- Stale information is identified rather than silently reused.
- Conflicting context is retained as conflict/uncertainty.
- Sensitive context is filtered by purpose and authority before disclosure.

### 4.4 Memory

**Purpose:** Retain and retrieve experiences and associations across time.

**Inputs:** Experiences, representations, context, retrieval queries, consolidation proposals, retention/deletion events.

**Outputs:** Provenance-linked memory records, retrieval candidates, associations, consolidation candidates and deletion receipts.

**Invariants:**
- Storage is not proof of learning.
- Retrieval includes provenance, relevance rationale and uncertainty.
- Memory may be incomplete, stale or contradictory.
- Retention, access and deletion rules are enforced independently of model preference.

### 4.5 Knowledge and beliefs

**Purpose:** Represent information and propositions with evidence, scope and revisable epistemic status.

**Inputs:** Experiences, representations, memory retrieval, external sources, inference results and contradictory evidence.

**Outputs:** Knowledge candidates, beliefs, evidence links, revision records, confidence estimates and unresolved conflicts.

**Invariants:**
- Evidence provenance is preserved.
- Support and contradiction remain separately inspectable.
- A belief revision creates history; it does not erase the prior state.
- Repetition alone does not prove truth.
- Confidence is calibrated and contextual; it is not automatically a probability.
- External content is evidence, not privileged instruction.

### 4.6 Prediction

**Purpose:** Generate explicit expectations about possible states, events or consequences before the outcome is known.

**Inputs:** Current context, beliefs, memory, candidate plans, capability knowledge, uncertainty and available compute.

**Outputs:** Prediction records containing target, expected outcome, conditions, horizon, confidence, relevant evidence and version.

**Invariants:**
- Original prediction and evaluation criteria are immutable.
- A prediction is stored before its outcome is observed when the test requires prospective evaluation.
- Missing or ambiguous outcomes remain unevaluated.
- Prediction confidence can be recalibrated from repeated evidence.

### 4.7 Appraisal

**Purpose:** Estimate the significance of current information and possible consequences relative to the system's current context, goals, constraints and learned experience.

**Inputs:** Context, beliefs, predictions, active goals, uncertainty, prior outcomes and current resource/authority constraints.

**Outputs:** Contextual appraisal state and rationale, including estimates relevant to urgency, relevance, novelty, opportunity, risk, conflict and expected consequence where applicable.

**Invariants:**
- Appraisal is a mechanism for evaluating context, not a fixed emotion label assigned to a stimulus.
- No universal stimulus→emotion, success→reward, failure→rejection or similar hardcoded mapping is permitted.
- Appraisal outputs are estimates with evidence and uncertainty, not unquestionable facts.
- Governance risk classification remains a separate safety mechanism and cannot be overridden by learned appraisal.

### 4.8 Attention

**Purpose:** Allocate limited processing resources among competing observations, goals, predictions, memories and unresolved questions.

**Inputs:** Appraisal, task relevance, novelty, uncertainty, predicted consequence, goal urgency, deadlines, resource budgets and interruption events.

**Outputs:** Versioned attention allocations, selection/defer decisions, resource budgets and rationale.

**Invariants:**
- Attention allocation can adapt from measured outcomes.
- A fixed priority list must not substitute for context-sensitive selection, although hard safety deadlines and resource limits remain explicit constraints.
- Attention cannot suppress mandatory governance checks, safety denials or owner authority.
- Preemption and starvation controls are observable and testable.

### 4.9 Reasoning

**Purpose:** Construct and evaluate hypotheses, explanations, alternatives and means to pursue goals using available evidence and mechanisms.

**Inputs:** Context, beliefs, memory, predictions, appraisals, attention allocation, capability knowledge, goals and constraints.

**Outputs:** Hypotheses, questions, candidate strategies, feasibility assessments, rationale and uncertainty.

**Invariants:**
- Separate known facts, assumptions, inferences and unknowns.
- Consider contradictory evidence and alternative explanations.
- Do not fabricate capabilities, permissions, interfaces or outcomes.
- A reasoning proposal is not a decision, authorization or execution receipt.
- Reasoning strategies may improve through evaluated experience; fixed task scripts are not the architecture.

### 4.10 Goals

**Purpose:** Represent owner objectives and derived objectives with explicit authority, priority, scope and lifecycle.

**Inputs:** Owner instructions, persistent objectives, context, constraints, progress and approved proactive-autonomy policies.

**Outputs:** Versioned goals, success conditions, priority rationale, dependencies, expiry and cancellation state.

**Invariants:**
- Owner authority and protected objectives cannot be silently rewritten by model output.
- Derived goals retain lineage to the source objective or owner instruction.
- Goal completion requires evidence, not a model assertion.
- Goal revisions preserve prior versions and reasons.

### 4.11 Planning

**Purpose:** Construct, compare and adapt plans for achieving goals.

**Inputs:** Goals, reasoning hypotheses, discovered capability descriptors, capability knowledge, permissions, resource budgets, predicted outcomes and current context.

**Outputs:** Versioned plans with steps, dependencies, preconditions, expected effects, budgets, checkpoints, alternatives and stop conditions.

**Invariants:**
- Plans reference discovered/versioned capability descriptors; they do not invent an operation because it would be convenient.
- Plans can be revised when new evidence, capability changes, denials or outcomes occur.
- A plan is not authority to execute.
- Hardcoded task→operation tables cannot substitute for planning.

### 4.12 Decision

**Purpose:** Select, defer, reject or request clarification for a proposed course of action.

**Inputs:** Candidate plans/options, expected outcomes, uncertainty, goal relevance, resource constraints and governance results.

**Outputs:** Decision record, rationale, rejected alternatives, unresolved questions and exact operation proposal when appropriate.

**Invariants:**
- The decision mechanism cannot grant permissions.
- If a necessary fact is unknown, the system may defer or ask rather than invent.
- Owner-reserved decisions remain with the owner.
- A decision to act still passes the independent execution-time policy gate.

### 4.13 Action and execution

**Purpose:** Carry out an exact authorized operation through a registered capability adapter and report what actually occurred.

**Inputs:** Exact operation proposal, capability descriptor/version, target, parameters, policy decision, approval reference, budget and cancellation state.

**Outputs:** Durable operation lifecycle, dispatch receipt, observed effects, verification evidence, error/uncertainty state and audit reference.

**Invariants:**
- Policy is enforced independently at the execution boundary.
- Android/OS permissions and AURIONS governance must both permit the operation.
- Unknown or changed parameters invalidate matching approval.
- Uncertain side effects are reconciled before retry.
- No model, worker or capability provider can self-escalate authority.

### 4.14 Outcome evaluation

**Purpose:** Compare what was expected with what was observed and determine what the evidence supports.

**Inputs:** Immutable prediction, plan expectations, operation receipts, independent observations, context changes and evaluation criteria.

**Outputs:** Outcome classification, prediction error/uncertainty, causal attribution hypotheses, confidence and linked learning evidence.

**Invariants:**
- Actual observed effects are distinct from provider-reported success.
- A missing receipt is not proof that an operation failed.
- Attribution must consider confounding factors and uncertainty.
- The evaluator cannot rewrite the original expectation to make it appear correct.

### 4.15 Learning

**Purpose:** Use evaluated experience to change future processing in a persistent, measurable and appropriately scoped way.

**Learning domains are distinct:**
1. **Episodic acquisition:** retaining a specific experience.
2. **Knowledge/belief revision:** changing the represented state of what is believed based on evidence.
3. **Capability learning:** improving knowledge of available interfaces, preconditions, effects, reliability and limits.
4. **Strategy/mechanism learning:** changing a reusable method or mechanism and evaluating its performance.
5. **Model training:** producing and evaluating a model artifact through the isolated worker pipeline.
6. **Architecture evolution:** proposing and testing structural changes through the governed evolution lifecycle.

**Inputs:** Outcome evaluations, prediction errors, repeated task evidence, held-out evaluations, capability-use history and explicit learning hypotheses.

**Outputs:** Learning hypotheses, candidate parameter/strategy/knowledge updates, experiment records, evaluation results and accepted updates.

**Invariants:**
- Each update identifies what changes, why, evidence, scope, expected effect and rollback path.
- Updates are versioned and attributable.
- A failed experience does not automatically become a universal prohibition; a successful experience does not automatically become a universal rule.
- Candidate changes are compared with a frozen baseline and tested on relevant unseen variations.
- Learning cannot weaken security, privacy, owner authority or governance policy.
- Model training and architecture evolution require their separate approval and validation paths.

### 4.16 Self-model

**Purpose:** Maintain an evidence-backed representation of AURIONS' own capabilities, limitations, confidence, resources, performance and current goals.

**Inputs:** Capability discovery, execution history, outcome evaluation, benchmark results, failures, resource telemetry and learning reports.

**Outputs:** Versioned self-model estimates with provenance, calibration and expiry.

**Invariants:**
- Self-claims are estimates, not authority.
- Confidence must be compared with actual outcomes.
- AURIONS cannot infer that it has a capability merely because a provider or model says it does.
- The self-model cannot grant permissions or approve its own changes.

### 4.17 Evolution

**Purpose:** Propose, test and govern changes to mechanisms or architecture when evidence indicates a limitation or opportunity.

**Inputs:** Self-model gaps, repeated failure patterns, evaluation results, resource constraints and owner objectives.

**Outputs:** Change proposals, impact/risk analysis, isolated candidates, comparison results, approval requests, activation records and rollback evidence.

**Invariants:**
- Production code, protected governance and core authority cannot be changed by an unreviewed self-modification.
- Candidates are isolated and cannot self-approve.
- Changes preserve provenance, reproducibility and rollback.
- AURIONS may propose foundational change, but protected owner authority and required approval remain enforced.

## 4.18 Canonical contract and persistence mapping

The canonical mechanism ownership, durable state, contract-family, work-package and verification mapping is maintained in [Cognitive and Capability Contract Matrix](COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md), Section 2. The field-level domain payload semantics are maintained in [Implementation-Ready Planning Contracts](../planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md).

This document defines cognitive mechanism responsibilities and interaction invariants; it does not duplicate the canonical table or schema definitions. If an owner, table, event or test mapping changes, update the matrix and contract source together, then verify all references. No mechanism may write another domain's authoritative state directly.

## 5. Interaction contracts

The following interactions must be explicit and testable. They are relationships, not a fixed order.

| Interaction | Required information flow | Failure/uncertainty behaviour |
|---|---|---|
| Experience → representation | Source, timestamp, modality, sensitivity, provenance | Preserve raw evidence; allow multiple/failed interpretations |
| Representation ↔ context | Entity, relation, temporal scope, confidence | Retain conflicting interpretations and stale context |
| Context ↔ memory/knowledge | Retrieval query, relevance, provenance, validity scope | Do not treat missing retrieval as proof of absence |
| Belief ↔ prediction | Proposition/evidence, assumptions, expected state, horizon | Preserve uncertainty; never rewrite prospective prediction |
| Appraisal ↔ attention | Contextual significance, novelty, urgency, risk, resource cost | Reassess when evidence or budgets change |
| Reasoning ↔ goals/planning | Candidate explanation/means, feasibility, constraints | Defer/ask when required inputs are unknown |
| Planning ↔ capability discovery | Capability IDs/versions, schemas, preconditions, effects | Rediscover or replan when descriptor is stale/unavailable |
| Decision ↔ governance | Exact proposed operation, target, parameters, data and effects | Deny/defer on mismatch, ambiguity or unavailable policy |
| Action ↔ environment | Authorized exact invocation and execution context | Capture receipt; mark uncertain when effect cannot be confirmed |
| Outcome ↔ prediction | Original expected outcome and independent observation | Preserve both even when evidence conflicts |
| Outcome ↔ memory/learning | Evidence, attribution hypotheses, scope and confidence | Do not generalize beyond supported context |
| Learning ↔ self-model | Accepted update, evaluation and performance evidence | Keep unvalidated candidates quarantined |
| Self-model ↔ evolution | Repeated limitations/opportunities and impact | Propose isolated candidate; never self-activate |
| Evolution ↔ governance | Exact change, risk, evidence, rollback and approval | No protected change without owner authority |

## 6. Orchestration, concurrency and interruption

The orchestrator manages:
- Event correlation and causal lineage.
- Work queues, priorities, deadlines and resource budgets.
- Concurrency limits and backpressure.
- Cancellation, preemption and safe checkpoints.
- Dependency readiness and stale-input detection.
- Retry classification and uncertain-operation reconciliation.
- Durable progress and recovery after restart.
- Observability without exposing sensitive content.

It must not impose a single linear cognitive pipeline. A new observation can revise context while another task is running; a permission revocation can invalidate a plan; a deadline can preempt optional reasoning; a new outcome can trigger evaluation and memory updates. Every such transition must be explicit and traceable.

A concurrent mechanism may consume a consistent versioned snapshot. If its inputs become stale before committing an update or dispatching an action, it must revalidate or abort safely.

### 6.1 Attention state durability and restart reconstruction

Attention allocation is primarily runtime state because relevance, urgency, uncertainty, deadlines and available resources can change continuously. A previous allocation is historical evidence, not a durable instruction and never an authorization.

Persist an attention-allocation event only when the allocation materially changes durable scheduling, preemption, resource reservation or task state. Such an event records:
- Allocation/event ID and algorithm/mechanism version.
- Referenced context version and active goal/task/plan versions.
- Candidate items considered, selected/deferred references and bounded selection rationale.
- Resource budget and observed resource state used for the allocation.
- Evidence/provenance references, uncertainty and creation time.
- Validity/expiry and invalidation conditions.

On restart, AURIONS MUST NOT blindly restore an old allocation as current truth. It reconstructs the candidate set from durable active goals, tasks, plans, checkpoints and current observations; re-evaluates current permissions, deadlines and resource availability; then computes a fresh allocation. Historical attention events may inform learning/evaluation but cannot override new observations, task cancellation, revoked authority or current safety constraints.

If required current inputs are unavailable, the scheduler enters a safe deferred/blocked state rather than treating stale priority as valid. Replay is idempotent and preserves the original event as history.


### 6.2 Causal lineage, versioned snapshots and concurrent commits

AURIONS does not assume a single global event order across the three SQLite stores or across cloud and mobile runtimes. Ordering is defined only within an explicitly named store/runtime stream. Cross-store and cross-runtime relationships use stable IDs, causal references and versioned domain state.

Every state-changing command that depends on previously read state must identify:
- The authoritative aggregate/domain identity being changed.
- The expected revision (or explicit absence for creation).
- The versions of context, goal, plan, capability descriptor, permission/grant and other dependencies that materially informed the proposed change.
- The causal parent event/command and correlation/task/operation identity where applicable.
- The idempotency key for retryable command submission.

A handler validates those expected revisions and dependency versions at the owning state boundary. If the authoritative revision has advanced, the handler must not silently overwrite newer state. It returns a typed conflict/stale-input result containing the current revision reference and the dependency that failed validation. The caller may retrieve current state, recompute its proposal and submit a new command with a new causal link. A stale proposal is never made current merely by replay.

Within one SQLite store, a state transition and its durable event/outbox record are committed in one local transaction. Across stores, use the documented local-transaction plus outbox/inbox and reconciliation pattern; do not claim distributed atomicity. A consumer checkpoint advances atomically with the consumer's local effect and is based on that store's durable sequence. Event IDs provide identity; per-store sequence provides local append order; neither is a global clock.

Concurrent reads may proceed against immutable snapshots. A result produced from a snapshot may be retained as a hypothesis or historical analysis, but any write or action that relies on it must revalidate the relevant dependency versions at commit/dispatch. This prevents a valid earlier inference from being treated as valid after a permission revocation, goal cancellation, context invalidation, descriptor change or plan supersession.

Conflict handling is domain-specific and preserves evidence:
- Append-only observations, receipts and outcome evidence are not overwritten; corrections or later observations append new records with causal links.
- Owner-authoritative governance and permission state is never merged by last-write-wins; the authoritative local policy boundary decides.
- Mutable cognitive projections use optimistic revision checks and domain-specific reconciliation; incompatible updates remain explicit conflicts for reasoning or owner resolution.
- Plan/task state changes require the current plan version and checkpoint lineage; stale work must replan rather than resume against changed dependencies.
- Learned estimates retain their source evidence and update lineage; concurrent candidate updates are evaluated against the same declared baseline or explicitly rebased and re-evaluated.

Cancellation and interruption are durable control signals. A handler checks cancellation before side effects and at documented safe points. If cancellation races with dispatch, the operation follows the durable operation state machine and may become uncertain; cancellation does not imply that an external effect was reversed. Reconciliation is required before a retry or a completion claim.

## 7. Persistent learning and behavioural change

For a learning claim, the system must show a chain:

1. A specific experience or outcome is captured with provenance.
2. An interpretation/evaluation is linked to that evidence.
3. A named mechanism or knowledge state proposes an update.
4. The update records its hypothesis, scope, baseline and expected effect.
5. The update is evaluated under the applicable standard.
6. An accepted update is committed with a version and rollback reference.
7. A later related task uses the updated state.
8. A paired test shows a measurable difference attributable to the update.
9. Related unseen variations test whether the change generalizes.
10. Regression checks detect unacceptable collateral degradation.

The chain must survive process restart where the state is intended to be durable. If a change affects only a transient prompt or untracked in-memory variable, it is not persistent learning.

## 8. Prohibited hardcoded behavioural substitutes

The following are architectural anti-patterns:
- Fixed stimulus→emotion or stimulus→appraisal lookup tables presented as acquired internal state.
- Fixed success/failure→reward/punishment or failure→avoidance mappings.
- Fixed task→tool/action recipes as the primary planner.
- A developer-authored closed Android operation list presented as AURIONS' discovered capabilities.
- Hardcoded claims that an operation succeeded without independent outcome evidence.
- Fixed confidence values that do not respond to calibration evidence.
- Manually authored "learned" memories or self-model claims presented as experience-derived.
- Rules that automatically convert one experience into a universal strategy without scope and evaluation.
- A scripted cognitive cycle that always invokes every mechanism in the same order regardless of context.

Explicit engineered constraints are not prohibited: schemas, safety invariants, permission boundaries, cryptographic protocols, resource ceilings, type validation, deterministic recovery logic and owner-protected authority rules are necessary. They constrain safe operation; they do not predetermine acquired behaviour.

## 9. Required verification scenarios

- **CM-001:** one experience supports multiple representations without changing the source record.
- **CM-002:** context revision marks stale dependent reasoning inputs.
- **CM-003:** contradictory evidence creates a belief revision while preserving prior evidence and history.
- **CM-004:** predictions are stored before outcome and cannot be rewritten after observation.
- **CM-005:** appraisal/attention allocations change in response to contextual evidence and resource constraints, not fixed stimulus mapping.
- **CM-006:** a new observation can interrupt or replan an active task safely.
- **CM-007:** a plan references discovered capability descriptors and fails safely when one is stale or unavailable.
- **CM-008:** decision output cannot bypass independent governance.
- **CM-009:** provider-reported success without verified postcondition remains unverified.
- **CM-010:** an uncertain external/device effect is reconciled before retry.
- **CM-011:** a learning update records evidence, hypothesis, scope, baseline, evaluation and rollback.
- **CM-012:** an accepted strategy update changes a later related task and survives restart.
- **CM-013:** the updated strategy is tested on related unseen variations and unrelated regression controls.
- **CM-014:** one failure does not automatically become a universal prohibition.
- **CM-015:** one success does not automatically become universal competence or permission.
- **CM-016:** a self-model capability estimate is calibrated against measured execution outcomes.
- **CM-017:** evolution candidates cannot self-approve or mutate protected governance.
- **CM-018:** resource exhaustion/cancellation preserves committed state and produces a recoverable task status.
- **CM-019:** no fixed task-to-action mapping is required to use a newly discovered compatible capability.
- **CM-020:** a later experience can trigger revision of an earlier belief/representation without erasing its provenance.
- **CM-021:** after restart, prior attention allocations are treated as historical; current allocation is reconstructed from current goals, task/checkpoint state, context, permissions and resource availability.


- **CM-022:** an objective's requested outcome, source, constraints and success evidence persist independently from derived goals and plans; revising a plan does not rewrite the objective.
- **CM-023:** a newly encountered entity and relationship remain provisional when evidence is indirect; conflicting or expired evidence revises the situation without erasing history.
- **CM-024:** the means-reasoning mechanism can consider a human-mediated or non-device route without inventing a platform adapter or capability descriptor.
- **CM-025:** when no sufficiently evidenced or authorized means exists, AURIONS can ask, observe, wait, delegate or stop without fabricating an executable action.
- **CM-026:** an affordance/means hypothesis is scoped to its context, preconditions and evidence; changing context or stale evidence lowers validity and triggers reassessment rather than universal reuse.
- **CM-027:** an interaction proposal remains non-executable until an independent authority boundary approves the exact actor, target, effects, scope and parameters; a proposal cannot authorize itself.
- **CM-028:** an interaction outcome distinguishes provider receipt, independent observation, unresolved effects and causal-attribution hypotheses; uncertain outcomes are not promoted to verified success.
- **CM-029:** a task spanning distinct contexts preserves separate identities, state ownership, provenance and authority; shared contracts do not imply shared access or atomic state.

These tests require fixtures, exact steps, durable-state assertions, negative controls and reproducible evidence before they can be marked VALIDATED.

## 10. Contract ownership and implementation mapping

Concrete schema definitions belong in the implementation-ready contract set, not duplicated in this document. That contract set must map each mechanism to:
- Owning C++ module/API.
- Authoritative persistence domain/table or artifact.
- Commands, queries, events and schema versions.
- Input/output/error/cancellation semantics.
- Provenance and sensitivity fields.
- State transition ownership.
- Allowed and forbidden dependencies.
- Unit, integration, failure and acceptance tests.

The Python worker boundary is limited to training, dataset preparation, experiments and evaluation. Workers return candidate artifacts and metrics; the C++ core validates them and retains authority over objectives, data permissions, release eligibility and production activation.

## 11. Completion criteria

This architecture remains IN PROGRESS until:
1. Every mechanism has an explicit owner, state domain, inputs, outputs, invariants and error semantics.
2. Interaction contracts map to concrete versioned schemas and authoritative persistence.
3. Concurrency, interruption, stale context, cancellation and recovery are specified end-to-end.
4. Learning types are distinct and their evidence requirements are enforceable.
5. No-hardcoding invariants are traced through objective interpretation, world/situation modeling, means reasoning, interaction governance and all context-specific realizations; Android is only one realization.
6. The canonical roadmap maps every mechanism to a work package and dependency.
7. Every CM-* scenario and the open-world objective/interaction scenario set is mapped to requirements, contract fixtures and the canonical test catalogue.
8. Architecture-wide consistency review finds no unresolved critical/high design contradiction.
9. The exact final revision receives independent review and required findings are resolved.
10. Owner planning-exit approval is obtained.
11. Attention allocation is reconstructed safely after restart and stale historical allocations cannot override current state.

**Current disposition:** IN PROGRESS. This document advances mechanism-level design but does not claim verified completeness, implementation or demonstrated learning.
