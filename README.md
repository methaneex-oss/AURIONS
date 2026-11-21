# AURIONS

**AURIONS** is the repository/system identifier; the final **S** denotes **System**.

AURIONS is one persistent, personal AI intelligence that the owner can access across supported devices. It is intended to understand, learn, remember, adapt, reason, plan and operate digital environments on the owner's behalf. Conversation is one interface, not the product's identity.

Its governing principle is:

> Engineer the mechanisms; let behaviour be acquired through experience.

The authoritative product direction is [AURIONS — One-Brain Product Charter](docs/product/ONE-BRAIN-PRODUCT-CHARTER.md).

## Product model

**One brain, two primary access paths:**

- **Local:** Runs on the owner's primary device, remains useful offline, uses local inference and local resources, retains durable state and can interact with the local operating system within granted permissions.
- **Cloud:** Adds online inference, research, remote compute and connected services. It is another access path to the same AURIONS identity, not a separate assistant.

Both paths must share cognitive semantics and reconcile accepted durable learning. AURIONS is designed to extend across phones, PCs and other supported devices. OS interaction must be objective-led and capable of discovering appropriate interfaces and means; it must not be reduced to a fixed task-to-command catalogue.

Online information and local experience both feed learning. AURIONS must preserve provenance, evaluate evidence, revise knowledge and beliefs, learn from outcomes and owner corrections, and distinguish memory/skill adaptation from model-weight training. Model candidates require evaluation before activation.

## Project status

**Implementation is underway.** The current C++/SQLite core now provides:
- Process-restart experience persistence with provenance and sensitivity metadata.
- Bounded lexical retrieval and memory-context evidence assembly.
- Persistent belief records with immutable, numbered revisions.
- Evidence-linked Bayesian confidence updates. Supporting and contradicting evidence changes confidence according to supplied reliability and relevance; contextual evidence is retained without shifting confidence.
- Evidence provenance, stance and revision history are returned for inspection. Duplicate use of the same experience as evidence for one belief is rejected.

The integration test proves that a prior of 0.5 rises to 0.8 after reliable supporting evidence, returns to 0.5 after equally reliable contradictory evidence, and remains unchanged after contextual evidence. The full revision chain and evidence provenance survive separate CLI process lifetimes. Exact-head CI run [44844792537](https://github.com/methaneex-oss/AURIONS/actions/runs/44844792537) passed CMake configure, C++ build and CTest.

This is a real but bounded learning primitive—not a complete learning brain. The evidence stance and reliability are currently supplied by the caller; AURIONS does not yet infer them from raw language or observations. Bayesian belief revision is not, by itself, natural-language understanding, model reasoning, skill acquisition, prediction/outcome learning, behavioural adaptation, local/cloud inference or OS autonomy.

Do not describe a subsystem, document, schema or passing host-side test as proof that the complete brain works. The next work is to connect evidence retrieval and belief revision to a cognitive consumer, then learn from predictions and independently observed outcomes. Reconcile this implementation with canonical persistence before broadening it.

## Start here

- [One-Brain Product Charter](docs/product/ONE-BRAIN-PRODUCT-CHARTER.md) — governing product identity, local/cloud access, device control and learning.
- [First Usable Release Product Definition](docs/product/FIRST-USABLE-RELEASE-DEFINITION.md) — bounded first-release workflows and acceptance boundaries.
- [System architecture](docs/architecture/COMPLETE-SYSTEM-ARCHITECTURE.md)
- [Open-world interaction and means architecture](docs/architecture/OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md) — objective-led understanding and means discovery across contexts.
- [Cognitive mechanism and interaction architecture](docs/architecture/COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md)
- [Cloud/offline-mobile topology decision](docs/architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md)
- [Canonical persistence reconciliation](docs/planning/QUERY-PROJECTION-AND-PERSISTENCE-RECONCILIATION.md)
- [Canonical implementation roadmap](docs/planning/CANONICAL-IMPLEMENTATION-ROADMAP.md)
- [Owner decision traceability matrix](docs/planning/OWNER-DECISION-TRACEABILITY-MATRIX.md)
- [Builder operating protocol](docs/governance/BUILDER-OPERATING-PROTOCOL.md)
- [Project directorship and team operating standard](docs/governance/PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md)

## Engineering direction

- C++ authoritative cognitive core and runtime.
- Python workers for data acquisition/curation, training, experiments and evaluation.
- AURIONS-owned model direction behind model-independent local/cloud inference interfaces.
- Durable experience, memory, knowledge, belief, learning and event state with explicit ownership and provenance.
- Local-first operation with optional cloud inference, research and compute.
- Objective-led operating-system interaction through context-appropriate, discoverable interfaces.
- Cross-device continuity through explicit synchronization, reconciliation, privacy and authority boundaries.
- Platform validation on actual target devices; do not infer compatibility from a host build.

## Repository integrity

Do not commit runtime databases, personal memory, model weights, secrets, credentials, private datasets or generated artifacts unless an explicit, reviewed policy permits it. Keep source, reproducible configuration, tests and non-sensitive documentation under version control.


## Current CLI capabilities

The C++ executable exposes the implemented experience and belief operations:

```text
aurions experience record <database> <source> <provenance> <sensitivity 0-4> <content>
aurions experience show <database> <experience-uuid>
aurions experience search <database> <query> [limit 1-100]
aurions experience context <database> <query> [max-items 1-50]

aurions belief create <database> <domain> <prior-confidence> <proposition>
aurions belief evidence <database> <belief-uuid> <experience-uuid> <stance> <reliability> [relevance]
aurions belief show <database> <belief-uuid>
```

Belief evidence stance is one of `supports`, `contradicts` or `contextualizes`. Reliability must be at least 0.5 and less than 1.0; relevance is between 0 and 1. The update uses log-odds evidence accumulation and preserves each revision. This first implementation assumes evidence is conditionally independent and does not yet model source dependence or automatically classify evidence.