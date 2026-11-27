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
- A combined cognition-context command retrieves relevant experiences and current evidence-backed beliefs together, with confidence, revision and evidence provenance for a downstream reasoning consumer.
- Outcome-driven strategy selection uses caller-supplied candidate references, persists prospective predictions, and revises later selections from provenance-linked outcomes across process restarts.

The integration test proves that a prior of 0.5 rises to 0.8 after reliable supporting evidence, returns to 0.5 after equally reliable contradictory evidence, and remains unchanged after contextual evidence. The full revision chain and evidence provenance survive separate CLI process lifetimes. Exact-head CI run [44844792537](https://github.com/methaneex-oss/AURIONS/actions/runs/44844792537) passed CMake configure, C++ build and CTest. The expanded strategy-adaptation integration test also passed exact-head CI run [44918008543](https://github.com/methaneex-oss/AURIONS/actions/runs/44918205266), including configure, build and CTest (1/1).

This is a real but bounded learning primitive—not a complete learning brain. The evidence stance and reliability are currently supplied by the caller; AURIONS does not yet infer them from raw language or observations. The cognition-context command assembles relevant memory and belief state; it does not itself generate a reasoned natural-language answer. Bayesian belief revision is not, by itself, natural-language understanding, model reasoning, skill acquisition, prediction/outcome learning, behavioural adaptation, local/cloud inference or OS autonomy.

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
aurions cognition context <database> <query> [max-items 1-50]
aurions strategy choose <database> <context-ref> <strategy-ref> [strategy-ref ...]
aurions strategy outcome <database> <prediction-uuid> <experience-uuid> <success|failure>
```

Belief evidence stance is one of `supports`, `contradicts` or `contextualizes`. Reliability must be at least 0.5 and less than 1.0; relevance is between 0 and 1. The update uses log-odds evidence accumulation and preserves each revision. This first implementation assumes evidence is conditionally independent and does not yet model source dependence or automatically classify evidence.

The combined cognition context is an inspectable evidence packet, not a model response. It returns ranked experience evidence and matching belief snapshots in one result so a future reasoning/inference consumer can distinguish observations from provisional beliefs and their confidence/provenance.

## Outcome-driven strategy adaptation

AURIONS has a narrow, measurable form of experience-dependent adaptation. Given a context reference and a caller-supplied set of candidate strategy references, the selector explores unseen candidates and then uses an upper-confidence-bound policy over their recorded outcomes. Its displayed success estimate is the Beta(1,1) posterior mean. Each choice is persisted as a prediction; an outcome must reference an active experience record and is appended as a separate prediction evaluation. The next choice is computed from accumulated evaluation history, including after a process restart.

This is deliberately bounded. Candidate strategies and context references are supplied by the caller; the system does not discover strategies, understand natural-language objectives, execute the selected strategy, or independently classify success. The outcome label is caller-supplied and the evaluation records that limitation. The selector is evidence-driven adaptation for a supplied choice set, not general reasoning, autonomous learning, or proof of broad competence. It uses the canonical `predictions` and `prediction_evaluations` tables from the memory schema.


## Configurable OpenAI-compatible model runtime (initial)

A standard-library Python runtime can invoke compatible hosted endpoints or local loopback servers. Configure a model in JSON and keep credentials in environment variables:

```sh
export AURIONS_PROVIDER_API_KEY="..."
PYTHONPATH=ml/python python -m aurions_ml.provider_runtime --config ml/python/examples/provider-openai-compatible.json --prompt "Hello"
```

To keep prompt text out of process arguments, read it without echo and pipe it to stdin (note: do not put literal private prompt text in a shell command, which may be saved in shell history):

```sh
read -r -s -p "Prompt: " prompt
printf '\\n'
printf '%s' "$prompt" | PYTHONPATH=ml/python python -m aurions_ml.provider_runtime --config ml/python/examples/provider-openai-compatible.json --stdin
```

When input is piped, `--stdin` is optional. In interactive terminals, use `--prompt` or explicitly provide `--stdin` (which requires non-interactive input). HTTP is allowed only for loopback local endpoints; remote endpoints require HTTPS. Embedded credentials, query strings, unknown configuration fields and oversized requests/responses are rejected. Provider error bodies are not printed. This is a first functional integration primitive: it is **not yet connected to the C++ cognitive runtime/router, a UI, encrypted provider settings, or model selection policies**. No live provider is exercised in CI.
