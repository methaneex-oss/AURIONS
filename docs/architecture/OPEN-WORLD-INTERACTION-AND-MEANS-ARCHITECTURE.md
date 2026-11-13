# AURIONS — Open-World Interaction and Means Architecture

- **Status:** Builder design in progress; foundational architecture proposal, not implementation authorization.
- **Scope:** Governs how AURIONS understands goals, the changing world, possible means, interaction, evidence and adaptation across digital, physical, social, institutional and mixed contexts.
- **Precedence:** This is the foundational interaction architecture. Platform-, provider-, device-, modality- and domain-specific designs are realizations beneath it, not the organizing model for intelligence.
- **Governing principle:** Engineer the mechanisms; let behaviour be acquired through experience.

## 1. The architectural correction

AURIONS is not fundamentally an Android agent, desktop agent, iOS agent, tool router, API catalogue or device-control system. It is an adaptive intelligence intended to understand and pursue authorized objectives in a changing world. Devices, operating systems, applications, services, people, organizations, physical objects, instruments, environments and other agents may be encountered as parts of that world. They are not an exhaustive or fixed list of environment types.

The architecture must therefore begin with the objective and the world in which it must be achieved—not with a platform, connector, tool inventory or preselected action set. A task may involve no external action, one interaction, a sequence of interactions, multiple contexts, a human-mediated step, waiting for a condition, or discovering that no currently supportable route exists. The system must reason about this from the task, evidence, context, constraints and authority available at that time.

This document supersedes any interpretation in which the Android environment/capability design is the general model for AURIONS. That Android design remains a platform-specific realization subject to this architecture.

## 2. Foundational distinctions

These concepts must not be collapsed into one another:

| Concept | Meaning | Must not be confused with |
|---|---|---|
| Objective / desired state | The outcome expressed or inferred from an instruction, with source, scope, constraints and uncertainty | A predetermined workflow or action sequence |
| World / situation | The relevant external and internal state in which the objective exists, including change outside AURIONS control | A device, app, screen or platform |
| Entity / actor | Anything represented as having identity or relevance: person, agent, organization, object, resource, system, process, place or event | A tool or capability |
| Observation / evidence | A sourced, contextualized report about a state, event, claim or interaction | Ground truth merely because it was received |
| Belief / world model | A revisable representation inferred from evidence, with provenance, confidence, scope and competing hypotheses | A static database of assumed facts |
| Affordance / possible means | A context-dependent hypothesis about what an actor or resource may make possible under specified conditions | A guaranteed ability, permission or executable API |
| Interaction | A proposed or performed exchange or intervention involving one or more entities, with expected effects and uncertainty | Necessarily a device command |
| Authority / consent | The legitimate permission to observe, disclose, decide or cause a particular effect | Technical access or discoverability |
| Outcome | The observed consequences of an interaction or non-action, including side effects and uncertainty | A tool/provider success response |
| Competence | A reusable, evidence-supported improvement in predicting or achieving outcomes | A stored procedure, one successful attempt or training loss |

An entity can be an actor in one relation and a resource in another. A person may provide information, approve an action, perform a task, or be affected by an outcome. A desktop may be a context, a resource, an interface host or irrelevant to a task. The model must represent relations and roles contextually rather than force each thing into one permanent device-centric category.

## 3. Objective-led operation

For each instruction, AURIONS must establish an explicit working interpretation before committing to a route:

1. Identify the requested outcome, the requester and authority, relevant scope, constraints, deadline and completion evidence.
2. Separate what is explicitly required from assumptions, preferences and unresolved ambiguity.
3. Determine what is already known about the relevant situation and what must be observed, retrieved, learned or clarified.
4. Construct or revise a task-relevant situation model, preserving uncertainty and alternative explanations.
5. Generate possible means from current evidence and learned models. Do not require a matching pre-authored task type, platform, tool or workflow.
6. Compare means by expected outcome, causal plausibility, prerequisites, authority, risk, reversibility, cost, resource limits, side effects and uncertainty.
7. Choose among acting, observing, asking, waiting, delegating, negotiating, combining means, revising the objective interpretation, or reporting that no adequately supported route is currently available.
8. Execute only through the applicable authority and interaction boundaries; observe consequences and re-evaluate after material change.
9. Preserve evidence and update beliefs, predictions, affordance estimates and competence only to the degree justified by the outcome.

This is a control discipline, not a fixed nine-step script. Mechanisms may iterate, run concurrently where safe, interrupt, or take a different order when context demands. The system must not mechanically execute every numbered stage when unnecessary.

## 4. World and situation representation

The world model must be open-ended and extensible. It should represent, where relevant and evidenced:

- Entities, identity hypotheses, attributes, state and lifecycle.
- Actors, roles, relationships, ownership, custody and responsibility.
- Places, contexts, boundaries and changing conditions.
- Resources, availability, dependencies, constraints and competing claims.
- Events, temporal order, duration, causality hypotheses and exogenous change.
- Goals, commitments, obligations, preferences and conflicting interests.
- Interfaces, channels, protocols and interaction histories.
- Observations, provenance, source reliability, uncertainty and contradiction.
- Expected state transitions, actual effects and unanticipated consequences.

This is not a mandate to implement a universal ontology or enumerate every possible entity class in advance. The representation must support extension, partial descriptions, unknown types, novel relations and revision. Typed contracts may define stable structural invariants while allowing domain-specific content and newly encountered concepts.

AURIONS must distinguish observed state, inferred state, reported state, predicted state and unknown state. It must preserve time and scope: a fact about one device, account, person, location or moment is not automatically transferable to another.

## 5. Means, affordances and capability knowledge

A possible means is discovered or hypothesized in relation to an objective and situation. It may arise from learned competence, a known interface, an available resource, an actor's offer, a human-mediated process, an external service, a physical interaction, a newly observed opportunity, or a composition of several means. This list is illustrative, not exhaustive.

AURIONS must be able to reason about:
- What entity or actor could contribute to the desired outcome.
- What interaction might be possible and what evidence supports that hypothesis.
- Preconditions, input/output meaning, expected effects and possible side effects.
- Required authority, consent, credentials, permissions and scope.
- Reliability, uncertainty, recency, reversibility and failure modes.
- Whether the means can be composed with other means without invalid assumptions.
- What observation or safe experiment could reduce uncertainty.
- Whether the means is unavailable, inaccessible, prohibited, unsafe, unknown or merely unverified.

Do not make a single universal capability registry the definition of possible action. A registry or index may be a useful implementation mechanism for particular discovered interfaces, but it cannot be the only source of means or a closed boundary around intelligence. Nor should AURIONS assume every possible means can be tested autonomously. Some evidence requires owner input, external validation, a human actor or a controlled environment.

Capability/affordance knowledge is contextual and revisable. A successful interaction in one context does not prove universal availability. Failure may be caused by changed conditions, wrong assumptions, missing authority, resource limits, inaccurate perception or a genuinely unavailable means; the system must investigate rather than encode a universal prohibition from one failure.

## 6. Interaction and effect boundaries

An interaction contract describes a particular proposed exchange or intervention, not a task-specific hardcoded behaviour. Depending on the context it may describe a message, request, query, negotiation, data transfer, API invocation, file operation, physical actuation, delegation, or another newly encountered interaction form.

Before an interaction that can cause consequential effects, the responsible enforcement boundary must validate:
- The actual actor, target, resource and context.
- The objective and permitted scope.
- The exact proposed effect and parameters.
- The authority of the requester and any required consent.
- Applicable external rules and local governance.
- Preconditions, freshness of observations and current state.
- Risk, reversibility, side effects and blast radius.
- Deadline, budget, cancellation and uncertainty semantics.
- What receipt and independent observation can establish completion.

Technical access is not consent. An available interface is not authorization. A model's plan is not an enforcement decision. A remote component cannot confer authority that belongs to a local system, owner, institution or affected party. Where authority is unclear, the system must not infer it from capability.

Not all useful work changes the external world. Analysis, retrieval, drafting, simulation, asking a question and waiting can be valid means. Their privacy, disclosure and resource implications still require appropriate controls.

## 7. Heterogeneous and changing contexts

A task may span multiple contexts or means, but AURIONS must not impose a universal platform hierarchy or assume that all contexts are interchangeable. It must reason from the objective and current evidence about where relevant information or means reside, what can interact, what authority applies, and where an effect will occur.

Android, desktop operating systems, iOS, cloud services, browsers, local processes, physical environments and human-mediated channels are examples of concrete contexts—not a closed platform list and not the top-level architecture. A context-specific integration must declare its actual scope, observable state, interface semantics, limitations, authority source, versioning, failure and recovery behaviour. Unsupported or unvalidated contexts remain explicitly unsupported or uncertain.

Cross-context work requires explicit treatment of identity, data movement, trust, provenance, state ownership, consistency, timing and handoff. No assumption of shared state, atomicity, identity equivalence, universal reachability or automatic synchronization is permitted.

## 8. Learning from interaction

Experience must change future competence through evidence-backed updates, not merely accumulate logs or procedures. Learning may revise:
- World-model hypotheses and entity relationships.
- Causal and predictive models of how situations change.
- Affordance/precondition/effect estimates.
- Source reliability and uncertainty calibration.
- Reasoning, attention and planning strategies.
- Resource and risk estimates.
- Reusable procedures or skills, where their scope and preconditions remain explicit.

Each update must retain source evidence, context, scope, time, confidence and revision history. Distinguish an observed event, a provider receipt, a verified external effect, a task outcome and a generalizable competence claim. Preserve contradictory evidence and avoid overgeneralizing from a single experience.

Claims of improvement require repeatable comparisons against a frozen baseline, relevant controls and held-out situations. A memory write, changed parameter, successful execution or lower training loss alone is not proof of improved competence. Learning must not grant itself authority or weaken governance.

## 9. Architecture layers and responsibility

The architecture separates responsibilities by meaning, not by deployment platform:

1. **Objective and intent interpretation:** instruction provenance, outcome, scope, constraints and ambiguity.
2. **Situation understanding:** observation, entity/relationship representation, context, temporal state and uncertainty.
3. **Knowledge and predictive understanding:** beliefs, causal hypotheses, predictions, memory and evidence.
4. **Means and affordance reasoning:** discovering or hypothesizing possible contributors and estimating conditions/effects.
5. **Deliberation and control:** reasoning, attention, goal management, planning, decision, replanning and stopping.
6. **Authority and governance:** identity, consent, policy, approvals, privacy, risk and revocation.
7. **Interaction execution:** context-specific protocols and providers, exact operation enforcement, receipts and recovery.
8. **Outcome evaluation and learning:** independent observation, causal attribution, memory revision and competence evaluation.

These are responsibility boundaries, not a prescribed process pipeline, microservice topology, agent count, language choice or fixed module decomposition. The cognitive architecture determines how they interact. Deployment may combine or distribute them as justified by measured requirements while preserving authoritative ownership and enforcement boundaries.

## 10. Required invariants

- No closed catalogue of tasks, behaviours, entity kinds, environments or means defines the system's intelligence.
- No developer-authored task-to-action mapping substitutes for objective-led reasoning.
- Platform integrations are subordinate realizations, never the universal model.
- Unknown, unobserved, inaccessible, prohibited and unavailable are distinct states.
- Discoverability, technical access, permission, consent and authorization remain distinct.
- Observations do not silently become facts; provider receipts do not silently become verified outcomes.
- Means are evaluated in context; success and failure do not generalize without evidence.
- AURIONS may ask, wait, delegate, choose an alternative or stop rather than force an action.
- New environments and interaction forms must be representable without redesigning the cognitive core or extending a closed task enum.
- External effects are enforced at the authority boundary closest to the affected resource.
- All consequential interactions are observable, attributable and recoverable to the extent technically possible.
- Learning preserves evidence and cannot self-authorize or silently weaken protected constraints.

## 11. Required design and verification work before planning exit

The builder must reconcile every dependent artifact against this architecture, including:
- Product scope, first-release definition and acceptance criteria.
- Cognitive mechanism and interaction architecture.
- Android architecture and cloud/offline topology.
- Entity, world-state, context, affordance, goal, plan, interaction and outcome contracts.
- Command/query/event registries, payload schemas and fixtures.
- Persistence ownership, lineage, temporal state and cross-context references.
- Governance, consent, privacy, identity and exact-effect authorization.
- Work-package boundaries, dependencies, implementation roadmap and test catalogue.
- No-hardcoding audits and all review/closure records.

Acceptance must include task-led scenarios that vary context and available means; novel entity/interface cases; human-mediated and non-device means; multi-context tasks; unknown and conflicting evidence; revoked or absent authority; no safe route; exogenous world changes; partial effects and uncertain receipts; recovery/replanning; and held-out learning tests. Scenarios are test probes, not a finite definition of the product's behaviour.

Before implementation planning is declared complete, every requirement must trace to an authoritative design, contract, owner decision or explicit unresolved gate, and to a verification method. Platform-specific validation remains separate and cannot be used as evidence that the general architecture is complete.

## 12. Decision boundary

This architecture does not decide the first external task, first action, first additional platform, universal access, or a promise of arbitrary autonomy. Existing owner decisions remain authoritative. The owner-selected Android target remains a concrete mobile target, not the sole environment or the definition of the capability model. Desktop and iOS are acknowledged as possible contexts; their exact integration scope and validation are not silently assumed.

No implementation authorization is created by this document.
