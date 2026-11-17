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

| Domain | Default synchronized field paths | Conditional fields | Excluded by default |
|---|---|---|---|
| Experience/provenance | experience_id, source_type, observed_at, recorded_at, provenance.source_kind, provenance.external_origin, capture_method, capture_limitations, retention_class | provenance.source_ref, actor_ref and device_ref only when the referenced identity is owner-scoped and separately classified OWNER_PRIVATE; content_ref only for an explicitly selected aggregate with an approved encrypted artifact reference | Raw observation content, audio/video/image bytes, precise location, third-party identifiers, unredacted source payloads |
| Representation | representation_id, experience_id, representation_type, method_id, method_version, uncertainty, source_refs, created_at and revision lineage | content paths only after each nested path has a typed schema, explicit classification and allowlist entry | Unclassified or arbitrary nested content objects; raw source material |
| Memory | memory_id, memory_type, status, created_at, updated_at, retention_until, deleted_at | summary and content_ref only when the owner explicitly selects that memory aggregate for synchronization and its fields pass classification and retention checks | Raw memory bytes, embeddings, retrieval scores and unselected memory content |
| Knowledge | knowledge_id, domain, status, created_at, updated_at | proposition only for an explicitly selected owner-scoped knowledge item; source-derived classification follows the strictest source | Unselected propositions, source payloads and security-restricted evidence |
| Evidence | evidence_id, source_experience_id, evidence_type, observed_at, recorded_at | source_ref and reliability only when the exact source reference is owner-scoped and the field classification permits transfer | Raw evidence content, protected source documents and third-party private data |
| Belief revisions | belief_id, knowledge_id, revision_id, revision_number, epistemic_status, confidence, evidence_refs, created_at | revision_reason only when the owner selects the exact belief and the text passes classification/redaction | Unselected belief content and raw evidence |
| Objectives/goals | objective_id, owner_ref, version, status, created_at; goal_id, revision, state, priority, objective_id, objective_version, created_at | objective statement, success_evidence, goal description and reason_ref only for owner-selected aggregates; constraints, assumptions and uncertainty only after typed nested schemas and path allowlists exist | Arbitrary constraint objects, unclassified intent text, local plans and task execution state |
| Immutable model-version references | artifact_id, artifact_kind, schema_version, media_type, byte_size, sha256, owner_id, provenance producer_id/source_refs, lineage parent_artifact_refs/derived_from, retention_class, lifecycle, created_at | Transfer of artifact bytes only through a separate explicit artifact-transfer authorization and integrity-verified resumable protocol | storage_ref values, local paths, active-pointer mutation, candidate activation, training credentials and worker state |

The field paths above are a builder proposal for the bounded Option B subset. A field is not eligible merely because it appears in a domain schema. The owning domain must classify it, the exact path must be present in the versioned allowlist, and the transfer must pass the authorization and retention rules below.

Arbitrary object fields are not safe to synchronize as a whole. In the current schemas, representation.content, representation.uncertainty, goal.constraints, objective.constraints, objective.uncertainty and entity attributes are generic objects. Those fields remain excluded until they have typed nested schemas and field-level classifications. This is a concrete schema gap, not permission to serialize the whole object.

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

The existing syncChange definition is only a preliminary v1 shape. It is insufficient as the final Option B contract. Before implementation, introduce a versioned sync envelope with these required semantic fields:

| Field | Required meaning |
|---|---|
| change_id | Globally unique immutable change identity; duplicate identity with a different payload digest is quarantined |
| owner_id | Derived from authenticated peer context and checked against the envelope; never trusted from payload alone |
| source_runtime_id / target_runtime_id | Explicit cloud/mobile runtime identities; source_device_id is optional metadata for a physical device, not a substitute for runtime identity |
| domain / aggregate_id | Exact allowlisted owner-scoped aggregate |
| schema_version / allowlist_version / classification_policy_version | Exact versions used to validate and project the payload |
| base_aggregate_version / aggregate_version | Expected predecessor and resulting aggregate revision |
| causal_parent_ids | Exact prior change identities on which this revision causally depends |
| field_paths | Sorted, unique set of transferred paths; every path must be a subset of the selected domain/version allowlist |
| payload_hash | SHA-256 of the canonical projected payload, checked before application |
| encrypted_payload_ref / encryption metadata | Authenticated encrypted payload reference, encryption profile and key-version reference; key material never travels in the envelope |
| authorization_ref | Exact owner/domain/field-path authorization when the classification requires it |
| retention_class / retention_policy_version | Retention decision and policy version applied to this change |
| tombstone / deletion_id | Explicit deletion semantics; tombstones carry no content payload |
| idempotency_key / created_at | Stable replay identity and source event time |

The envelope must be signed by an authenticated source runtime and bound to the authenticated destination and owner. The receiver validates signature, peer identity, owner scope, policy/allowlist versions, schema compatibility, payload digest, field paths, retention and causality before mutation. The exact cryptographic profile and key-rotation mechanism must be selected in the security implementation design; do not invent a cipher or treat a key reference as key material.

A critical existing-schema defect: syncChange currently requires source_device_id. The cloud runtime is not necessarily a physical device. The v2 contract must require source_runtime_id and make source_device_id optional. It must also add the base revision, destination runtime, allowlist/policy versions, field paths, classification/authorization evidence and signature/integrity metadata. The existing generic payload_hash minLength rule must become an exact digest format.

## 5. Causality, revisions and conflict resolution

No last-writer-wins rule is permitted for owner cognitive state.

- A change applies only when its declared base_aggregate_version equals the receiver's current aggregate version and its causal parents are satisfied.
- A duplicate change_id with the same digest returns the original receipt and causes no second mutation, event, outbox entry or revision.
- A duplicate change_id with a different digest is an integrity/security conflict and is quarantined; it is never interpreted as a new revision.
- A replayed ancestor already represented in the current causal history is a no-op. It cannot overwrite a descendant.
- Two distinct changes based on the same predecessor are concurrent siblings. Preserve both source revisions, create a conflict record and block the aggregate's current projection from silently choosing either.
- A merge is automatic only for an explicitly declared commutative field/operation with a deterministic, versioned merge rule. No free-form representation, memory, belief, objective or goal text is auto-merged.
- Conflict resolution requires an authenticated owner decision bound to the exact conflict ID, both source revision/change IDs, expected conflict revision, chosen resolution and current policy. Append a new revision; retain both original revisions and the resolution lineage.

The current syncConflictRecord shape is insufficient for this proof. Its next version must include owner/runtime scope, both change IDs, common base revision, local/remote aggregate revisions, causal ancestry, conflict revision, resolution actor/approval evidence and a digest of the exact resolution. A resolution reference alone is not enough to prove which revisions were resolved.

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

The following SY cases are the minimum first-release acceptance set. They are proposed here; they are not yet present in the current 48-scenario machine fixture corpus and must be added with exact event bindings and negative controls before D-02 is marked implementation-ready.

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

## 9. Required machine-contract changes before implementation

- Add syncChange v2 and syncConflictRecord v2 definitions; retain compatibility only through explicit version negotiation.
- Add a versioned domain/field-path allowlist and a classification-policy registry. Do not encode arbitrary nested object fields as syncable.
- Add runtime identity and peer-authentication bindings. Cloud/mobile runtime identity must not be inferred from a physical device ID.
- Add exact payload digest/signature verification and authorization/retention policy version checks.
- Add durable per-store sync inbox, export ledger, peer acknowledgement, aggregate checkpoint and tombstone propagation state, with local transaction boundaries and recovery invariants.
- Bind sync.change.exported.v1, sync.change.applied.v1, sync.tombstone.applied.v1, sync.conflict.detected.v1 and sync.conflict.resolved.v1 to the SY scenario set. Their current event registry acceptance_scenario_refs are empty.
- Add negative fixtures for unknown fields, local-only field injection, owner/runtime mismatch, missing authorization, unknown allowlist/policy version, stale base revision, conflicting sibling changes, same-ID/different-digest replay and tombstone resurrection.
- Add the 15 SY scenarios to the canonical machine scenario corpus and validator; current event/schema CI does not prove synchronization behaviour.
- Validate the design against the selected Android/Termux target and the cloud runtime. No database-file replication is permitted.

## 10. Closure boundary

- D-02 Option B is owner-selected.
- This document specifies a bounded builder-proposed first-release domain/field policy, authority boundary, causality, conflict, deletion, retention, replay and recovery semantics.
- The current machine syncChange/syncConflictRecord schemas do not yet encode the required v2 fields. The five sync events have no command producers and currently have empty acceptance scenario references; their internal trigger definitions are present.
- The current scenario corpus has no SY scenarios. No synchronization runtime, inbox/outbox application, peer authentication, conflict resolver or deletion propagation has been implemented or executed.
- Therefore D-02's topology decision is resolved, but its detailed machine contract and executable acceptance remain IN PROGRESS. This document does not authorize implementation or change the owner-selected Option B scope.
