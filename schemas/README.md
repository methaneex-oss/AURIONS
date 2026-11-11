# AURIONS contract schemas

- [`persistence/`](./persistence/README.md): machine-readable proposed SQLite base schemas and additive migrations; unexecuted and pending target validation.

This directory is the proposed canonical machine-readable schema source. The initial schema dialect is JSON Schema Draft 2020-12. A validator candidate and an explicit no-code-generation baseline are documented in Section 12.1 of the implementation-ready contracts; neither has been integrated into the runtime or CI, and Android target feasibility remains unverified.

- `message-envelope.v1.schema.json`: common versioned message envelope.
- `command-query-registry.v1.schema.json`: schema for the command/query registry baseline.
- `command-query-registry.v1.json`: machine-readable registry for 43 schema-mapped command types, two explicitly deferred device commands and 21 typed query types. All 45 command registry records reference the common envelope (43 also bind request payload schemas; two are deferred without payload schemas), and all 21 query entries bind the common envelope, input/result schemas and generic payload-shape fixture references; task-control entries additionally bind their known revision, safe-point cancellation, side-effect and emitted-event contracts. Every entry is `design_only_not_dispatchable` or `deferred_by_scope`; unresolved execution semantics are explicit and null never means a default.
- `error-registry.v1.schema.json`: schema for extensible error-code registry entries and their default recovery metadata.
- `error-registry.v1.json`: 35-code, 13-category seed registry; every entry now links to a category-owned handler contract and one schema-shaped fixture, but all entries remain non-dispatchable until runtime handlers and recovery tests exist.
- `error-handler-fixtures.v1.schema.json`: schema for the error-handler contract fixture set.
- `fixtures/error-handler-cases.fixture.json`: one `contractError` payload fixture for each of the 35 seed codes, linked to its handler contract; fixtures validate payload shape only, not runtime recovery.
- `capability-descriptor-body.v1.schema.json`: extensible evidence-backed descriptor body.
- `domain-payloads.v1.schema.json`: versioned payloads for command/query envelopes and responses, compatibility negotiation, errors, experience, representation, context and context invalidation, evidence, belief, prediction, appraisal, attention, reasoning, memory, knowledge, goals, plans, decisions, capability descriptor records/discovery/knowledge, operation lifecycle, task-run status/transitions, outcome observation/evaluation, learning, self-model, evolution, governance, checkpoints, synchronization, artifact lineage, disclosure, retention/deletion, worker protocol and experiment/candidate lifecycle. The descriptor record references the separately defined extensible descriptor body schema.
- `fixtures/domain-payloads.fixture.json`: 78 domain, protocol, command and query payload examples; it is test data, not production memory or real operations.
- `fixtures/message-envelope.fixture.json`: common envelope fixture containing a generic decision event.
- `fixtures/negative/`: 28 intentionally invalid fixtures covering descriptor authority injection, missing provenance, invalid selected-decision shape, invalid owner identity type and invalid operation risk class, artifact digest, approval risk class, worker required identity, sync conflict lineage, disclosure digest, command type binding, query consistency, error side-effect state, missing task-run transition revision, dispatched-provider blind retry and incomplete error-registry entry. Capability IDs and provider-defined interface names are data, not closed enums.
- `fixtures/capability-descriptor.fixture.json`: deliberately generic fixture for contract-shape validation only; it is not a real Android capability or product operation.
- `fixtures/decision-recorded.fixture.json`: decision event body fixture; it is not a selected owner decision.
- `fixtures/provider-lifecycle.fixture.json`: neutral validated-provider, typed provider failure and compatibility negotiation examples; these do not validate a production provider.
- `fixtures/provider-lifecycle-enabled.fixture.json`: positive example proving that provider enablement carries separate governance-decision and current platform-permission evidence.
- `../docs/planning/ERROR-HANDLER-CONTRACT-MATRIX.md`: 13 category-level handler contracts and a 35-code mapping. Handler contracts are specified, not implemented or registered.

Rules:
1. Schema validity never implies permission, trust or authorization.
2. Capability descriptors describe observed interfaces; invocation code remains in trusted adapters.
3. New capability providers must be representable without adding task-specific branches to the cognitive core.
4. Unknown or unsupported semantics remain unknown; extension fields cannot change authority or policy.
5. Schemas are versioned. Breaking changes require a new major schema version and compatibility tests.
6. The schemas are planning artifacts until validated by the selected C++/Python toolchain and integrated into CI.
7. The fixture set contains 78 positive domain/protocol/command/query payload fixtures and 28 negative fixtures.
8. The command/query registry is a design traceability baseline, not a runtime dispatch registry. Production registration is prohibited while any entry has unresolved bindings, and the registry does not replace per-handler state, authorization, idempotency, side-effect, event, error, redaction or recovery contracts.
9. The proposed Corvus validator pairing is not yet an approved or target-validated dependency. Its Apache-2.0 project license does not remove the need to preserve its third-party Unicode notices and audit its full transitive dependency graph. A bounded structural subset audit in this revision passed all 78 positive domain payload examples, all three provider lifecycle examples, the command/query registry against its schema, the error registry against its schema and all 35 `contractError` payloads; it also rejected the three added negative fixtures for missing task-run revision, dispatched-provider blind retry and incomplete error-registry entry. The earlier custom checker had rejected the original 25 negative fixtures, but those 25 were not rerun in this audit. This remains a custom subset check, not a full JSON Schema Draft 2020-12 validator; official conformance, full negative-corpus rerun, format handling, cross-language compatibility and CI enforcement remain outstanding.
