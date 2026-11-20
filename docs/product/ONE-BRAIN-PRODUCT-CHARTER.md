# AURIONS — One-Brain Product Charter

**Owner clarification:** 2026-11-20  
**Purpose:** Governing product definition for implementation. This charter clarifies the intended product identity and system behaviour; it does not claim that the capabilities described below are already implemented.

## 1. Product identity

AURIONS is one persistent, personal AI intelligence that the owner can access across supported devices. It is intended to understand, learn, remember, adapt, reason, plan and operate digital environments on the owner's behalf.

AURIONS is not merely a chatbot, a collection of automations, a fixed command catalogue, or a thin wrapper around a third-party model. Conversation is one interface. The product is the evolving intelligence and the mechanisms that let it acquire and use experience.

The governing engineering principle is:

**Engineer the mechanisms; let behaviour be acquired through experience.**

## 2. One brain, two access paths

The product has one coherent identity and one evolving body of cognitive state, exposed through two primary access paths:

- **Local access:** Runs on the owner's primary device and remains useful without internet access. It uses local inference and local resources, maintains durable local state, and can interact with that device's operating system within granted permissions.
- **Cloud access:** Provides online inference, research, remote compute and connected services when useful. It is another access path to the same AURIONS identity, not a second assistant with a separate personality or unrelated memory.

Both paths use common cognitive semantics, versioned contracts and compatible state representations. Experiences and accepted learning from either path must become available to the other through reliable, provenance-preserving synchronization and reconciliation. Offline operation must not depend on cloud availability. Cloud services must not gain authority over a local device merely because they can communicate with it.

"One brain" means one coherent evolving intelligence and reconciled state; it does not require every device to run identical model weights or one continuously running process. Device-specific runtimes and model sizes may differ while preserving the same identity, memory semantics and learning lineage.

## 3. Devices and operating-system interaction

AURIONS is designed to extend across the owner's supported devices, including phones and PCs. The primary device is the main local operating environment; other devices are additional access points and execution environments.

System interaction must not be limited to a hardcoded list of user-facing commands. AURIONS should be able to interpret an objective, inspect the available environment, discover relevant interfaces and capabilities, reason about possible means, act through appropriate operating-system mechanisms, observe effects and recover from uncertainty.

The implementation may use OS accessibility interfaces, native APIs, shell/process interfaces, desktop automation, browser control or other context-appropriate mechanisms. These are implementation means, not a closed definition of what AURIONS can understand or attempt. New contexts and capabilities should be discoverable through evidence and compatible interfaces rather than requiring a new hardcoded task-to-action branch for every task.

Actual execution remains bounded by operating-system permissions, owner-granted authority, privacy policy and risk controls. AURIONS must distinguish what it can technically access from what it is authorized to do.

## 4. Learning from both online and local experience

Both online information and local experience feed the same learning cycle.

**Online sources** may include web pages, documentation, research, public datasets and connected services. AURIONS must assess source provenance, relevance, reliability, freshness, contradictions and applicable rights before treating material as knowledge or admitting it to training.

**Local sources** may include conversations, owner corrections, permitted files, observations, tasks, application/device context and action outcomes. Local data remains subject to privacy, consent, sensitivity and retention rules.

The learning cycle is:

1. Acquire an experience or information source.
2. Preserve source, time, context, provenance and uncertainty.
3. Interpret it into representations relevant to the current situation.
4. Retrieve and associate relevant prior experiences.
5. Update provisional knowledge and beliefs when evidence warrants it.
6. Compare predictions with independently observed outcomes.
7. Derive and evaluate reusable adaptations, strategies or skills.
8. Apply accepted changes to later reasoning and behaviour.
9. Consolidate and synchronize accepted durable learning across access paths.

Information acquisition is not automatically truth acquisition. Search results do not automatically become trusted knowledge, and retrieved content does not automatically become model-training data.

## 5. What "updating the brain" means

AURIONS must support distinct but cooperating forms of learning:

- **Working context:** information needed for the current task.
- **Episodic memory:** durable records of what happened, when, where and with what outcome.
- **Semantic knowledge:** evidence-backed facts, concepts and relationships.
- **Beliefs and world models:** provisional claims with confidence, provenance, contradiction and revision history.
- **Procedural knowledge and skills:** reusable methods whose performance can be evaluated across contexts.
- **Personal adaptation:** learned preferences, communication style, routines and workflow tendencies, with evidence and correction history.
- **Model parameters:** changes produced by controlled training or fine-tuning experiments and evaluated before activation.

These are not interchangeable. Adding a chat transcript to a database is not by itself learning. Changing model weights is not the only form of learning. AURIONS should first make persistent experience, retrieval, belief revision and behaviour adaptation work as a connected system, while developing its AURIONS-owned model and training path in parallel.

Model updates must be versioned, evaluated against held-out tasks and regression controls, and reversible. AURIONS must not silently train on private or unapproved data, or automatically activate an untested model candidate.

## 6. Local and cloud model strategy

The brain is not defined by a single inference provider. AURIONS must have a model-independent inference boundary that can route work between local models and cloud models according to capability, latency, privacy, connectivity, resource budget and task requirements.

Local inference is essential for offline operation and private/local tasks. Cloud inference and compute provide additional capacity for demanding reasoning, research and training where appropriate. Provider substitution must not split AURIONS into different identities or make a third-party hosted model a permanent required dependency.

The long-term model direction remains an AURIONS-owned model, trained and improved through a reproducible pipeline. External models may be optional tools or temporary development aids only within the applicable owner-approved boundaries.

## 7. Deployment and delivery principle

The architecture is cross-device from the beginning, but device support can be delivered incrementally. The first validated local target and first cloud target must establish the shared brain contracts, state ownership, local authority, offline operation and synchronization/reconciliation mechanisms. Additional PC, phone and other device realizations should extend those mechanisms rather than create separate assistants.

Do not claim "runs on every device" until each supported platform has actual compatibility and operational evidence. Do not let this evidence requirement shrink the intended product into a single-device chatbot.

## 8. Product acceptance test

A meaningful AURIONS demonstration must eventually show all of the following in one connected system:

- The owner can access the same AURIONS identity locally and through cloud access.
- Local operation continues without internet.
- Online research and local experience can both enter the learning cycle with provenance.
- AURIONS can remember and retrieve relevant past experiences.
- New evidence can revise beliefs or knowledge without silently erasing contradictions.
- Owner corrections and observed outcomes can change later behaviour.
- Accepted learning becomes available through both access paths after synchronization.
- AURIONS can inspect a supported operating environment, discover a suitable means for a previously unseen objective, execute within authority and verify the result.
- Local and cloud model resources can be changed or routed without replacing AURIONS identity or cognitive state.
- Model-weight changes are separately evaluated, versioned and reversible.

This is a product direction and acceptance target, not a claim that the current prototype already satisfies it.

## 9. Implementation priority

Implementation should prioritize the shortest real path to an integrated demonstration:

1. Preserve and reconcile the existing experience persistence with the canonical memory/event/governance persistence design.
2. Build contextual retrieval and a cognitive consumer that uses retrieved experience in reasoning.
3. Connect representation, evidence-backed knowledge/belief revision, prediction and outcome feedback.
4. Demonstrate persistent experience-dependent behavioural adaptation across restart.
5. Establish the local inference runtime and cloud inference adapter behind one model-independent interface.
6. Implement objective-led OS observation and interaction through discoverable, context-specific interfaces, with independently enforced authority and effect verification.
7. Implement durable brain-state synchronization and reconciliation between local and cloud access.
8. Develop the AURIONS-owned training pipeline and evaluate model candidates alongside the experience-learning mechanisms.
9. Extend the same brain to additional phone, PC and other device environments.

This ordering is an implementation priority, not a reason to postpone architectural compatibility for local/cloud and cross-device operation.

## 10. Non-negotiable distinctions

- One brain is not two independent assistants.
- Two access paths are not two unrelated memories.
- Local-first does not mean local-only.
- Cloud assistance does not mean cloud dependency.
- OS control is not a fixed command catalogue.
- Technical capability is not authorization.
- Search is not verification.
- Memory storage is not learning.
- Personalization is not necessarily model fine-tuning.
- Model training is not automatically safe or beneficial.
- A successful tool receipt is not proof that the intended effect occurred.
- Architecture documents and passing schema tests are not proof of a working cognitive system.
