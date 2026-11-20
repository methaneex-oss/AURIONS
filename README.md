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

**Implementation is underway.** The current implementation branch contains a C++/SQLite experience store with process-restart persistence, contextual lexical retrieval and a bounded memory-context evidence packet builder. Retrieval searches active experience content and provenance, ranks by query-term coverage/content matches, and preserves provenance and sensitivity metadata. The context builder assembles ranked evidence under item and serialized-payload budgets for a downstream cognitive consumer. This is a foundation, not semantic/vector retrieval, model reasoning over retrieved evidence, belief revision, an integrated learning cycle, behavioural adaptation, local/cloud inference or operating-system autonomy. Integration tests cover restart persistence, retrieval ranking/provenance and context assembly, but this branch's new C++ code has not yet been built or run in CI.

Do not describe a subsystem, document, schema or passing host-side test as proof that the complete brain works. The next implementation work is to validate the C++ build and tests, reconcile experience persistence with the canonical persistence design, connect the evidence packet to the cognitive reasoning path, and then implement evidence-backed belief revision and prediction/outcome learning.

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
