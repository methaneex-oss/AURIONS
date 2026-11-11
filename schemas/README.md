# AURIONS contract schemas

This directory is the proposed canonical machine-readable schema source. The initial schema dialect is JSON Schema Draft 2020-12; validator/generator library selection remains subject to the dependency and licence audit.

- `message-envelope.v1.schema.json`: common versioned message envelope.
- `capability-descriptor-body.v1.schema.json`: extensible evidence-backed descriptor body. Capability IDs and provider-defined interface names are data, not closed enums.
- `fixtures/capability-descriptor.fixture.json`: deliberately generic fixture for contract-shape validation only; it is not a real Android capability or product operation.

Rules:
1. Schema validity never implies permission, trust or authorization.
2. Capability descriptors describe observed interfaces; invocation code remains in trusted adapters.
3. New capability providers must be representable without adding task-specific branches to the cognitive core.
4. Unknown or unsupported semantics remain unknown; extension fields cannot change authority or policy.
5. Schemas are versioned. Breaking changes require a new major schema version and compatibility tests.
6. The schemas are planning artifacts until validated by the selected C++/Python toolchain and integrated into CI.
