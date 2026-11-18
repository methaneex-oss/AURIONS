# AURIONS — Cloud/Mobile Selective Synchronization Contract

- Status: Builder technical contract proposal for the owner-selected D-02 Option B. It is not implementation, runtime validation or expanded owner authorization.
- Scope: First-release synchronization between the AURIONS cloud runtime and the offline-capable Android/mobile runtime only.
- Authority: D-02 Option B was selected by the owner on 2026-11-16. This document specifies the bounded subset; it does not authorize general multi-device replication, seamless handoff, authority transfer or runtime implementation.
- Normative rule: Synchronization transfers selected owner-scoped domain revisions. It never transfers execution authority, OS permissions, governance authority, credentials or live operation state.

## 1. Decision and runtime boundaries

Both runtimes use the same authoritative cognitive-core implementation and versioned domain contracts. Each runtime remains independently operable while disconnected and owns its local execution, device and governance state. A synchronized domain revision becomes available on the other runtime only after the receiving runtime has authenticated the peer and owner scope, checked the field allowlist and policy version, validated causality and applied the change durably.

The system must distinguish four states:

1. Locally committed: the source runtime has committed the aggregate revision and its local outbox record.
2. Exported: the source synchronization engine has selected and authenticated the exact eligible change and recorded its export ledger.
3. Received/applied: the destination has authenticated, validated and idempotently applied the change.
4. Reconciled: both sides have the required durable receipts/checkpoints and any conflict or deletion obligations are resolved.

An exported change is not proof of remote receipt. A received envelope is not proof of application. A remote acknowledgement is not proof that a local permission or operation was authorized. The UI and cognitive core must not report cross-context continuity before the relevant aggregate reaches the required reconciled state.

SQLite database files are never copied or replicated. Only versioned domain changes and encrypted artifact references cross the boundary. Each database retains its own transaction, outbox and recovery ownership.

## 2. First-release synchronized domain allowlist

The allowlist is positive and versioned. Unknown domains, fields, nested paths, schema versions or allowlist versions are rejected and quarantined; absence from the list never means allowed.

**Owner-acceptance gate (hard stop):** the machine allowlist and the separate `schemas/sync-classification-policy.d02.v1.json` registry both have status `builder_proposal_not_owner_accepted`. The latter maps every exact default, conditional and excluded allowlist leaf to a named classification and transfer/denial treatment, and CI cross-checks both registries for exact path parity. These are builder proposals, not enabled export entitlements. Until the owner explicitly accepts the exact field paths, classifications, conditional rules and policy version, every domain/field remains export-disabled. An implementation must fail closed and quarantine attempted changes; it must not treat presence in `default_paths` as permission to synchronize. D-02 Option B selects the topology, not this detailed field policy.

| Domain | Default synchronized field paths | Conditional fields | Excluded by default |
|---|---|---|---|
| Experience/provenance | experience_id, source_type, observed_at, recorded_at, provenance.source_kind, provenance.external_origin, capture_method, capture_limitations, retention_class | provenance.source_ref, actor_ref and device_ref only when the referenced identity is owner-scoped and separately classified OWNER_PRIVATE; content_ref only for an explicitly selected aggregate with an approved encrypted artifact reference | Raw observation content, audio/video/image bytes, precise location, third-party identifiers, unredacted source payloads |
| Representation | representation_id, experience_id, representation_type, method_id, method_version, source_refs, created_at and revision lineage (`revision_number`, `supersedes_revision_id`) | None in v1; a later version may add exact typed/classified leaf paths | `content`, `uncertainty`, all nested paths under those generic objects, and raw source material |
| Memory | memory_id, memory_type, status, created_at, updated_at, retention_until, deleted_at | summary and content_ref only when the owner explicitly selects that memory aggregate for synchronization and its fields pass classification and retention checks | Raw memory bytes, embeddings, retrieval scores and unselected memory content |
| Knowledge | knowledge_id, domain, status, created_at, updated_at | proposition only for an explicitly selected owner-scoped knowledge item; source-derived classification follows the strictest source | Unselected propositions, source payloads and security-restricted evidence |
| Evidence references (not standalone evidence records) | `beliefRevision.evidence_refs` carries only owner-scoped, non-content evidence reference identifiers when each exact path is allowed | Any standalone evidence metadata requires a separately approved domain/schema and allowlist revision; it is not part of D-02 v1 | Raw evidence content, source documents, reliability assertions and third-party private data |
| Belief revisions | belief_id, knowledge_id, revision_id, revision_number, epistemic_status, confidence, evidence_refs, created_at | revision_reason only when the owner selects the exact belief and the text passes classification/redaction | Unselected belief content and raw evidence |
| Objectives/goals | objective_id, owner_ref, version, status, created_at; goal_id, revision, state, priority, objective_id, objective_version, created_at | objective statement, success_evidence, goal description and reason_ref only for owner-selected aggregates and exact approved paths | objective assumptions/constraints/uncertainty and goal constraints (generic untyped objects), unclassified intent text, local plans and task execution state |
| Immutable model-version references | artifact_id, artifact_kind, schema_version, media_type, byte_size, sha256, owner_id, provenance producer_id/source_refs, lineage parent_artifact_refs/derived_from, retention_class, lifecycle, created_at | Transfer of artifact bytes only through a separate explicit artifact-transfer authorization and integrity-verified resumable protocol | storage_ref values, local paths, active-pointer mutation, candidate activation, training credentials and worker state |

The field paths above are a builder proposal for the bounded Option B subset. Evidence is reference-only through an approved belief/knowledge revision; there is no standalone `evidence` synchronization domain in v1. The exact machine-readable default/conditional/excluded paths are in [`schemas/sync-field-allowlist.d02.v1.json`](../../schemas/sync-field-allowlist.d02.v1.json); their proposed named classifications and conditions are in [`schemas/sync-classification-policy.d02.v1.json`](../../schemas/sync-classification-policy.d02.v1.json). A field is not eligible merely because it appears in a domain schema. The owning domain must classify it, the exact path must be present in the versioned allowlist, and the transfer must pass authorization and retention rules below.

Arbitrary object fields are not safe to synchronize as a whole. In D-02 v1, representation.content/uncertainty, objective.assumptions/constraints/uncertainty, goal.constraints and entity attributes remain excluded. The machine allowlist contains no wildcard patterns; a future allowlist version must enumerate each exact leaf path only after its nested schema and classification are defined and accepted. This is a concrete schema gap, not permission to serialize the whole object.

## 3. Classification, consent and local-only data

Use the named classifications already established in the query/security contract:

- PUBLIC: sync only when the owning domain explicitly marks the exact field PUBLIC and policy permits it. PUBLIC is never inferred from missing classification.
- OWNER_PRIVATE: eligible only between authenticated runtimes for the same owner, for a domain the owner has enabled, with encryption and exact owner scope.
- SENSITIVE: local by default. Transfer requires explicit per-aggregate authorization naming exact field paths, purpose, destination runtime, policy version and expiry. A broad domain toggle is insufficient.
- SECURITY_RESTRICTED: never synchronized in the first-release contract.

If a field has only the current numeric sensitivity value 0–4 and no authoritative mapping to the named classification, treat it as ineligible. Do not infer that numeric zero means PUBLIC or that a numeric value can override the owning domain's classification.

The following remain local-only regardless of ordinary domain synchronization settings:

- Android OS permissions, app grants, accessibility/service state, device pairing secrets, hardware identifiers and device credentials.
- Owner authentication secrets, approval nonces, session tokens, private keys, key bytes, security-restricted policy internals and governance authorization material.
- Command dispatch state, provider receipts, active operations, task checkpoints, worker jobs/attempts, cancellation state and device-side action results.
- Local outbox/inbox rows, transport checkpoints, peer keys and per-runtime recovery journals.
- Raw sensor/media payloads, precise location, unredacted third-party data and any source field whose classification or retention status is unknown.
- Active model pointers and activation/rollback state. An approved immutable model-version reference may synchronize; it cannot activate or select that model on the receiving runtime.

A remote change can update only the allowlisted domain aggregate. It cannot create or widen an Android permission, grant a capability, approve an operation, alter a governance policy or dispatch an action.

## 4. Required change envelope

The machine-readable `syncChange` definition now encodes the D-02 v2 envelope fields in `schemas/domain-payloads.v1.schema.json`. The `source_device_id` property is optional metadata (and may be null); `source_runtime_id` and `target_runtime_id` are mandatory. The schema binds base/result aggregate revisions, sorted unique field paths, allowlist/classification/retention-policy versions, authorization reference, encryption/signature profile and key-version references, SHA-256 payload digest and tombstone metadata. The exact cryptographic profile and key-rotation mechanism remain unselected implementation/security work.

| Field | Required meaning |
|---|---|
| change_id | Globally unique immutable change identity; duplicate identity with a different payload digest is quarantined |
| owner_id | Derived from authenticated peer context and checked against the envelope; never trusted from payload alone |
| source_runtime_id / target_runtime_id | Explicit cloud/mobile runtime identities; source_device_id is optional metadata for a physical device, not a substitute for runtime identity |
| domain / aggregate_id | Exact allowlisted owner-scoped aggregate |
| schema_version / allowlist_version / classification_policy_version | Exact versions used to validate and project the payload |
| base_aggregate_version / aggregate_version | Expected predecessor and resulting aggregate revision; the source change must advance beyond its base |
| causal_parent_ids | Exact prior change identities on which this revision causally depends |
| field_paths | Sorted, unique set of transferred paths; every path must be a subset of the selected domain/version allowlist |
| payload_hash | SHA-256 of the canonical projected payload, checked before application |
| encrypted_payload_ref / encryption metadata | Authenticated encrypted payload reference plus `encryption_profile_id` and `encryption_key_version_ref`; key material never travels in the envelope. A tombstone carries no encrypted content payload |
| authorization_ref | Exact owner/domain/field-path authorization when the classification requires it; null only when the selected paths do not require additional per-aggregate consent |
| retention_class / retention_policy_version | Retention decision and policy version applied to this change |
| tombstone / deletion_id | Explicit deletion semantics; tombstones carry no content payload |
| idempotency_key / created_at | Stable replay identity and source event time |

The envelope must be signed by an authenticated source runtime and bound to the authenticated destination and owner. The receiver validates signature, peer identity, owner scope, policy/allowlist versions, schema compatibility, payload digest, field paths, retention and causality before mutation. The exact cryptographic profile and key-rotation mechanism must be selected in the security implementation design; do not invent a cipher or treat a key reference as key material.

Event-specific payload schemas now distinguish ordinary `syncChange`, `syncTombstoneChange`, pending `syncConflictDetectedRecord` and `syncConflictResolvedRecord`. Tombstones require an explicit deletion ID/revision, retention-policy version, causal parents and authorization reference, with no content field paths or encrypted content reference. Conflict resolution binds both source change IDs, the common base, local/remote runtime and aggregate revisions, expected conflict revision, authenticated actor/approval reference, resolution digest and appended resolution reference. These are schema-level constraints, not proof that handlers enforce them.

## 5. Causality, revisions and conflict resolution

No last-writer-wins rule is permitted for owner cognitive state.

- A change applies only when its declared base_aggregate_version equals the receiver's current aggregate version and its causal parents are satisfied.
- A duplicate change_id with the same digest returns the original receipt and causes no second mutation, event, outbox entry or revision.
- A duplicate change_id with a different digest is an integrity/security conflict and is quarantined; it is never interpreted as a new revision.
- A replayed ancestor already represented in the current causal history is a no-op. It cannot overwrite a descendant.
- Two distinct changes based on the same predecessor are concurrent siblings. Preserve both source revisions, create a conflict record and block the aggregate's current projection from silently choosing either.
- A merge is automatic only for an explicitly declared commutative field/operation with a deterministic, versioned merge rule. No free-form representation, memory, belief, objective or goal text is auto-merged.
- Conflict resolution requires an authenticated owner decision bound to the exact conflict ID, both source revision/change IDs, expected conflict revision, chosen resolution and current policy. Append a new revision; retain both original revisions and the resolution lineage.

The machine-readable `syncConflictRecord` now records owner/domain/aggregate scope, both source change IDs, common base, local/remote runtime and aggregate revisions, version references, causal parents, conflict revision and policy versions. The pending and resolved event-specific schemas enforce distinct `resolution_state` values; the resolved schema additionally requires the expected conflict revision, actor/approval references, resolution digest, resolution policy and immutable successor reference. The schema does not authenticate the actor or approval; runtime trust/governance enforcement remains open.

## 6. Deletion, retention and tombstone propagation

Deletion is a monotonic replicated state transition, not a missing row.

1. The source runtime first removes the content from active local visibility and commits a deletion tombstone with its local outbox in one transaction.
2. The tombstone names owner, domain, aggregate, deletion ID, deletion revision, retention policy version and causal parents. It contains no deleted content.
3. Each destination applies the tombstone before accepting any older content change for that aggregate. An older replay cannot resurrect content.
4. The destination returns a durable acknowledgement bound to the tombstone ID and aggregate revision. A transport acknowledgement without committed destination state is insufficient.
5. Content and derived indexes are purged according to the applicable retention policy. Tombstone metadata is retained until all required peers have acknowledged and the supported retry/backup restore horizon has elapsed.
6. If a peer remains offline, propagation remains pending. The system must not report deletion complete across contexts and must not discard the tombstone needed to suppress replay.
7. A restored backup must replay tombstones before making restored content queryable. Expired/unknown retention policy or uncertain deletion state fails closed for visibility.

Deletion of source material and the impact of that material on trained model weights are distinct. A tombstone does not prove unlearning. Model retraining, unlearning assessment or candidate rollback remains a separate governed decision.

## 7. Offline queueing, replay and recovery

- Every eligible local aggregate commit writes its local outbox record in the same transaction. No network operation occurs while holding the aggregate's SQLite write transaction.
- Delivery is at least once. The receiver commits the aggregate change, its event/outbox and its inbox/idempotency receipt atomically in the destination store.
- Retries use the same change_id and idempotency key. Retry never creates a new semantic change.
- Per-aggregate order follows causal parents and aggregate revisions, not wall-clock timestamps. Wall-clock time is diagnostic metadata, not conflict authority.
- Missing predecessors are held for reconciliation. Unknown schema/allowlist/policy versions, invalid signatures, owner mismatches and malformed tombstones are quarantined; they are not partially applied.
- Crash after destination commit but before source acknowledgement is recovered by replaying the same change and returning the original durable receipt.
- Crash before destination commit leaves no partial aggregate mutation; retry resumes from the source outbox.
- A local runtime remains usable offline. It may accumulate eligible local changes, but it must mark cross-context state stale/unreconciled until delivery and conflict checks complete.
- Network loss, a stale peer or unavailable governance state must never trigger broad replication, last-writer-wins, deletion suppression or authority fallback.

## 8. Acceptance scenarios required for D-02

The following 15 SY cases are the minimum first-release acceptance set. All are now present as machine-readable design specifications in `schemas/fixtures/scenario-contracts.fixture.json`, each with five ordered steps, two negative controls, restart/replay, concurrency, fault and held-out controls. The full corpus contains 63 scenarios, 368 ordered steps and 89 scenario negative controls. They remain unexecuted specifications, not runtime evidence.

| Scenario | Required proof |
|---|---|
| SY-001 Allowlisted projection | An exact allowed field set is exported; an extra nested or unknown field is rejected before export |
| SY-002 Local-only rejection | SECURITY_RESTRICTED, unclassified and local-only fields never enter the envelope or payload |
| SY-003 Owner/runtime isolation | A valid change for another owner or an unpaired runtime is rejected without existence disclosure |
| SY-004 Duplicate replay | Same change ID and digest applied twice produces one mutation and one durable receipt |
| SY-005 Identity/digest mismatch | Same change ID with a different payload digest is quarantined |
| SY-006 Offline queue/reconnect | Offline local commit remains durable and later reconciles without loss or duplicate application |
| SY-007 Concurrent revisions | Two sibling revisions create an explicit conflict; neither silently wins |
| SY-008 Stale ancestor replay | A previously superseded change cannot overwrite a descendant |
| SY-009 Tombstone precedence | A deletion tombstone suppresses stale content replay and backup restore resurrection |
| SY-010 Tombstone retention | Tombstone remains until peer acknowledgements and the replay/backup horizon are satisfied |
| SY-011 Crash after destination commit | Replay after lost acknowledgement returns the existing receipt without a second mutation |
| SY-012 Unknown contract version | Unknown schema, allowlist or policy version is quarantined without partial application |
| SY-013 Owner conflict resolution | Resolution is authenticated and binds both source revisions and expected conflict revision |
| SY-014 Model reference is not activation | An approved immutable model reference may sync, but active pointer and activation state do not change |
| SY-015 No authority transfer | A remote change cannot create an Android permission, governance approval or local action dispatch |

Acceptance requires deterministic state assertions, event/outbox/inbox counts, restart/replay, concurrency and fault injection. A document-only scenario statement is not executed evidence.

## 9. Machine-contract status before implementation

The D-02 machine specification has advanced beyond the initial contract draft. The following artifacts are now specified and present:

- The `syncChange` v2 envelope and `syncConflictRecord` definitions are present in `schemas/domain-payloads.v1.schema.json`. The event-specific `syncTombstoneChange`, `syncConflictDetectedRecord` and `syncConflictResolvedRecord` definitions and positive payload examples are also present.
- The versioned default-deny field allowlist is present in `schemas/sync-field-allowlist.d02.v1.json` as `d02-cloud-mobile.v1`. The separate builder-proposed `schemas/sync-classification-policy.d02.v1.json` maps every exact default, conditional and excluded leaf to a named class and treatment; CI requires exact path parity. Neither registry is owner-accepted, and export remains disabled.
- The five synchronization events have payload-schema and fixture references. Their nonempty `acceptance_scenario_refs` match the SY scenario steps that emit them.
- SY-001…SY-015 are present in `schemas/fixtures/scenario-contracts.fixture.json`. The complete corpus contains 63 specifications, 368 ordered steps and 89 scenario negative controls. The 15 SY scenarios each contain explicit negative controls and restart/replay, concurrency, fault and held-out controls.
- The SY negative controls cover unlisted fields, local-only and unclassified data, overbroad authorization, owner/runtime mismatch, duplicate/digest mismatch, unknown policy versions, stale and concurrent revisions, tombstone replay/retention, conflict approval misbinding, model-reference activation and attempted authority transfer. They are behavioral test specifications, not executed tests. The separate schema-negative payload fixture set currently has only limited sync-specific coverage; static payload fixtures do not substitute for runtime authentication, replay or fault tests.

The following work remains before implementation:

- Complete the versioned field-classification policy and authoritative mapping for every eligible field path. Owner/domain acceptance is still required for conditional paths, exact SENSITIVE-field authorization and treatment of numeric sensitivity values that lack an authoritative named-class mapping. Missing or unknown classification remains deny-by-default.
- Complete peer bootstrap, authenticated runtime enrollment, pairing and revocation, signature verification, cryptographic-profile selection and signing/encryption key lifecycle. The envelope carries identity and profile/key-version references; this does not prove those controls exist or work.
- **Builder-proposed persistence allocation (not yet represented by DDL):** keep synchronization transport state local to each runtime and in the owning SQLite store; never replicate these records.
  - `aurion_memory.db` is the authoritative store for the synchronized cognitive aggregates and should own the D-02 transport ledger: immutable `sync_export_ledger` rows linked to the memory-local outbox message, append-only export-state events, immutable `sync_inbox_receipts` keyed by source-runtime/change identity, quarantined-envelope evidence, peer acknowledgement receipts bound to the exact export and digest, append-only causal-gap events, immutable conflict records plus append-only owner resolutions, immutable tombstone records plus per-peer tombstone receipts, and append-only restore events carrying the required/applied tombstone frontier.
  - The receiving aggregate mutation, its inbox receipt and the memory-local outbox publication intent must commit in one destination-memory transaction. A duplicate change with the same digest returns the existing receipt; the same identity with a different digest creates quarantine evidence and never a second aggregate mutation.
  - The source export ledger is distinct from the generic local outbox: the outbox publishes the domain event to the central event archive, while the export ledger tracks delivery to a specific peer runtime. An acknowledgement is accepted only when peer runtime, change ID and payload digest match the immutable export record.
  - `aurion_events.db` remains the central event archive and generic saga/recovery coordinator. Its existing event receipts are not substitutes for destination-domain inbox receipts; no additional events migration is proposed at this stage.
  - `aurion_governance.db` remains authoritative for owner authorization and any accepted peer-trust decisions. Memory records contain only opaque authorization/peer references; private keys, key bytes, credentials and pairing secrets remain local-only and are not added to these tables.
  - No cross-file foreign keys or distributed ACID transaction are introduced. The proposed records are append-only or event-sourced; status is derived from immutable transition events. Peer enrollment, trust bootstrap, signing/encryption profiles and key lifecycle remain a separate security/owner gate.
  - Memory migration v10 now defines these D-02 local records, and the host SQLite validator exercises their structural and append-only transition invariants. This does not validate runtime projection/receiver atomicity, peer authentication, C++/Python canonicalization, crash/replay recovery or target Android/Termux behaviour.
- Implement and verify export projection, exact authorization/classification/retention checks, signature and digest validation, receiver admission, idempotent receipts, conflict handling, tombstone precedence and crash/replay recovery. No runtime handler or durable sync behavior is established by the schema fixtures.
- Verify canonical serialization and digest parity across C++ and Python, then execute the SY fault, restart/replay, concurrency, deletion/restore and recovery cases against the cloud runtime and the selected Android/Termux SQLite target.

## 10. Closure boundary

- D-02 Option B topology is owner-selected (2026-11-16); the separate D-02 field-classification policy was owner-accepted as Option A on 2026-11-18.
- This document specifies the bounded first-release domain/field policy, authority boundary, causality, conflict, deletion, retention, replay and recovery semantics. Policy acceptance does not enable export or authorize runtime synchronization.
- The v2 change/conflict payload definitions, event-specific tombstone and conflict payload definitions, positive payload examples and versioned default-deny field allowlist are present in the machine-readable schema set.
- The five sync events have nonempty acceptance-scenario references that match the SY-001…SY-015 machine scenario steps. The 15 SY scenarios remain `specified_not_executed` with `execution_authority: none`.
- Runtime enforcement of the durable per-runtime synchronization persistence and complete runtime classification-policy enforcement, authenticated peer lifecycle/key management, runtime projection and receiver handlers, C++/Python conformance, executed SY fault/recovery tests and cloud/Android target conformance remain IN PROGRESS. This document does not authorize implementation or change the owner-selected D-02 Option B scope.
