# AURIONS contract schemas

This directory is the proposed canonical machine-readable schema source. The initial schema dialect is JSON Schema Draft 2020-12; validator/generator library selection remains subject to the dependency and licence audit.

- `message-envelope.v1.schema.json`: common versioned message envelope.
- `capability-descriptor-body.v1.schema.json`: extensible evidence-backed descriptor body.
- `domain-payloads.v1.schema.json`: versioned payloads for command/query envelopes and responses, compatibility negotiation, errors, experience, representation, context and context invalidation, evidence, belief, prediction, appraisal, attention, reasoning, memory, knowledge, goals, plans, decisions, capability descriptor records/discovery/knowledge, operation lifecycle, outcome observation/evaluation, learning, self-model, evolution, governance, checkpoints, synchronization, artifact lineage, disclosure, retention/deletion, worker protocol and experiment/candidate lifecycle. The descriptor record references the separately defined extensible descriptor body schema.
- `fixtures/domain-payloads.fixture.json`: 52 generic domain and protocol payload examples; it is test data, not production memory or real operations.
- `fixtures/message-envelope.fixture.json`: common envelope fixture containing a generic decision event.
- `fixtures/negative/`: 13 intentionally invalid fixtures covering descriptor authority injection, missing provenance, invalid selected-decision shape, invalid owner identity type and invalid operation risk class, artifact digest, approval risk class, worker required identity, sync conflict lineage, disclosure digest, command type binding, query consistency and error side-effect state. Capability IDs and provider-defined interface names are data, not closed enums.
- `fixtures/capability-descriptor.fixture.json`: deliberately generic fixture for contract-shape validation only; it is not a real Android capability or product operation.
- `fixtures/decision-recorded.fixture.json`: decision event body fixture; it is not a selected owner decision.
- `fixtures/provider-lifecycle.fixture.json`: generic provider lifecycle, typed provider failure and compatibility negotiation examples; these do not validate a production provider.

Rules:
1. Schema validity never implies permission, trust or authorization.
2. Capability descriptors describe observed interfaces; invocation code remains in trusted adapters.
3. New capability providers must be representable without adding task-specific branches to the cognitive core.
4. Unknown or unsupported semantics remain unknown; extension fields cannot change authority or policy.
5. Schemas are versioned. Breaking changes require a new major schema version and compatibility tests.
6. The schemas are planning artifacts until validated by the selected C++/Python toolchain and integrated into CI.
7. The positive fixture set currently contains 52 domain/protocol payload fixtures. 13 negative fixtures are included; their current custom structural subset results are recorded in the planning completion register. This check is not a full JSON Schema Draft 2020-12 validator; official schema conformance, format handling, cross-language compatibility and CI enforcement remain open.
