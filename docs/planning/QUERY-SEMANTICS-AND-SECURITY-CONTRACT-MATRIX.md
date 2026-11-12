# Query Semantics and Security Contract Matrix

**Status:** Builder contract proposal; not owner-approved as a product/API release and not dispatchable.  
**Scope:** BR-002 — all 21 query registry entries.  
**Authority boundary:** This document completes query-side semantic design where it can be determined from the existing architecture. It does not select the first Android action, settle cloud/mobile history topology, authorize implementation, or promote any query to runtime dispatch.

## 1. Normative query invariants

Every query is read-only with respect to domain state. Diagnostic/audit telemetry emitted by the runtime is not a query side effect and MUST NOT be exposed as a domain mutation. A query MUST NOT create a memory, update a belief, refresh a capability descriptor, allocate attention, advance a task, reconcile an operation, grant permission, or alter an approval.

The authenticated execution context is authoritative for `owner_id`, actor identity and device identity. Values supplied in `domainQuery.filters` are selectors only; they cannot replace or widen the authenticated scope. Every table/view/derived join in a query must be constrained by the same owner scope before projection, aggregation, ranking, count calculation or pagination. A missing owner binding is a denial, not an unscoped query. Cross-owner and unknown-object results use the same externally observable denial/not-found shape to avoid existence disclosure.

Queries return evidence with its source and revision where the result schema permits it. A query projection MUST NOT convert a hypothesis, inferred value, provider descriptor or cached value into an observed fact. A descriptor is not an authorization grant; a permission projection is not a capability; a task status is not an operation outcome.

### 1.1 Consistency contract

- `snapshot`: one consistent read snapshot within the owning database. All rows, counts, ordering and cursor watermark in one response come from that same snapshot.
- `local_committed`: include all commits visible to the owning store at the read transaction's start. This is the required mode for read-after-write verification within the same store.
- `eventual`: permitted only for explicitly derived/search projections whose staleness is disclosed with source watermark and freshness metadata. It is never permitted for permission, approval, audit, task-control or operation-dispatch authority/status decisions.
- The handler MUST refuse an unsupported requested mode. It MUST NOT silently downgrade consistency.
- A query spanning more than one owning database has no implicit cross-store snapshot. Such a query is unsupported until a versioned cross-store consistency protocol is specified; do not fabricate a global transaction.

### 1.2 Ordering, cursor and pagination contract

For collection queries, the owner domain defines a total order with a stable unique final tie-breaker. Cursors are opaque, authenticated tokens bound to owner ID, actor/device scope where relevant, query type/version, normalized filter digest, sort definition/version, consistency mode, snapshot/watermark and expiry. A cursor from another owner, actor scope, query, filter, sort, schema version or expired snapshot is rejected without returning rows.

Snapshot pagination must preserve one snapshot across pages. If the store cannot retain that snapshot, the cursor expires explicitly; it must not silently continue against a new view. For mutable state queries that cannot retain a snapshot, use keyset pagination against a declared revision/watermark and return an explicit stale-cursor conflict when the view changes. Offset pagination is not an acceptable substitute for deterministic keyset/snapshot semantics.

Single-record inspect/get/status queries use an immutable record identifier and return at most one record. They do not accept collection cursors. If a query supports both single-record and collection mode, the mode is explicit in its input contract and cannot be inferred from missing filters.

### 1.3 Resource and freshness contract

The generic schema bounds are validation ceilings, not safe per-endpoint budgets. Every handler must receive a non-null effective policy containing deadline, maximum rows, maximum serialized response bytes and any expensive-field/compute budget. Values must be calibrated against target storage/runtime measurements and then pinned in the release configuration. Until those measurements and values exist, the query remains non-dispatchable; this document does not invent performance thresholds.

A timeout, row cap or byte cap returns a typed bounded error with no partial result unless the response schema explicitly supports a continuation token tied to the same snapshot. The handler must not silently truncate, omit sensitive fields without redaction metadata, or return a partial result as complete.

Only immutable content may be cached, keyed by owner scope, object ID, object revision, schema version and classification policy version. Mutable context, belief, prediction, appraisal, attention, goal, plan, decision, task, operation, permission and audit state is not served from an unvalidated cache. Capability descriptors and knowledge may be cached only with exact descriptor/knowledge revision, expiry and invalidation watermark; freshness is disclosed. Permission and audit queries are never cached for authorization decisions.

### 1.4 Classification and redaction contract

Classification is assigned by the owning domain to each field before query projection:
- `OWNER_PRIVATE`: owner data, personal context, memory, evidence, beliefs, plans, decisions and task content. Return only to the authenticated owner or explicitly authorized exact-scope delegate.
- `SENSITIVE`: environment observations, private memory content, interaction targets/parameters, operation receipts, capability details that reveal device state, and personal inferences. Require purpose/scope authorization; redact from generic diagnostics and broad list results.
- `SECURITY_RESTRICTED`: permission/grant details, approval nonces/references, policy internals, key metadata, security audit payloads and sensitive actor/session details. Return only through governance-authorized fields and purpose-specific access. Never return secret material or key bytes.
- `PUBLIC` is not inferred from absence of a classification. A field may be public only when the owning domain explicitly marks it public and the owner policy permits disclosure.

Redaction is deterministic and schema-aware. It must not be implemented by deleting arbitrary JSON keys after serialization. Each query defines which fields are returned, redacted with a typed marker, or cause whole-query denial. A redacted response identifies the redaction class/reason without disclosing the protected value. Counts, facets, snippets, error messages and timing must not leak the existence or contents of unauthorized records.

## 2. Per-query contract bindings

All queries below retain their current registry owner, aggregate, store and result schema. The entries remain `design_only_not_dispatchable` until the listed domain binding is implemented and tested. "Snapshot" means the owning-store snapshot defined in §1.1, not a global snapshot.

| Query | Exact scope and purpose | Classification / redaction | Consistency and ordering | Freshness / cache |
|---|---|---|---|---|
| `environment.inspect` | Authenticated owner; device/resource filters must be within owner-authorized observation scope. Return recorded observations only; no sensing is triggered by query. | OWNER_PRIVATE + SENSITIVE. Redact raw sensor payload, precise location, identifiers and unrelated actors unless exact purpose permits. | Snapshot. Collection mode uses observed_at DESC, then observation_id ASC; cursor binds observation watermark. | No cache for current environment state. Historical immutable observation may be revision-cached; freshness/source time always shown. |
| `capability.search` | Owner-scoped descriptors; filter by context/provider/status without implying permission or universal competence. | OWNER_PRIVATE + SENSITIVE. Redact provider internals, device identifiers and unsupported private parameters. | Snapshot for descriptor inventory; total order descriptor revision DESC, descriptor_id ASC. | Cache only exact descriptor version with expiry and registry invalidation watermark. |
| `capability.inspect` | One descriptor ID, owner-scoped; return descriptor/provenance/verification status, not permission. | OWNER_PRIVATE + SENSITIVE. Redact raw provider diagnostics and secret/config values. | Local_committed for read-after-write verification; one record, no cursor. | Cache only immutable descriptor revision; verification freshness and revocation watermark are returned. |
| `capability.knowledge.inspect` | Owner-scoped knowledge revision and linked evidence; no learning/update side effect. | OWNER_PRIVATE + SENSITIVE. Preserve provenance and contradiction references; redact protected evidence payloads by field policy. | Snapshot; revision DESC, knowledge_revision_id ASC. | Immutable revision cache only; invalidated by accepted successor or evidence tombstone. |
| `representation.inspect` | One representation or bounded owner-scoped collection; include source experience lineage. | OWNER_PRIVATE. Content and source evidence are sensitive; redact source payloads not authorized for current purpose. | Local_committed for exact representation ID; collection uses revision DESC, representation_id ASC. | Immutable revision cache only; never substitute a newer revision for the requested revision. |
| `context.get` | Owner-scoped context snapshot; expose assembled inputs and their versions, not authority or current world certainty. | OWNER_PRIVATE + SENSITIVE. Redact private memory/environment fragments and restricted policy material. | Snapshot; context revision DESC, context_id ASC. | Immutable context revision cache may be used only while all dependency revisions match; otherwise recompute or return stale. |
| `memory.search` | Owner-scoped retrieval over authorized memory records and links; query terms do not widen owner/data scope. | OWNER_PRIVATE + SENSITIVE. Snippets, embeddings, scores and linked evidence are private; redact protected source fields and never expose raw embeddings by default. | Snapshot; relevance score DESC, created_at DESC, memory_id ASC. Cursor binds normalized query/filter digest and snapshot. | Search index watermark and source revision returned. Eventual allowed only when explicitly requested and labeled; no cache across memory/retention revisions. |
| `knowledge.search` | Owner-scoped knowledge items with evidence and validity; distinguish source fact, inference and hypothesis. | OWNER_PRIVATE; source-derived sensitive content retains source classification. | Snapshot; relevance DESC, revision DESC, knowledge_item_id ASC. | Cache immutable item revision only; evidence change or tombstone invalidates derived result. |
| `belief.inspect` | Owner-scoped belief/revision and supporting/contradicting evidence. | OWNER_PRIVATE. Confidence, source and contradiction lineage remain visible; redact protected evidence content. | Snapshot; belief_id ASC then revision DESC for history; single-record mode has no cursor. | Revision-bound cache only; new evidence/revision invalidates current projection. |
| `prediction.inspect` | Owner-scoped prediction, horizon, expected outcome and evaluation linkage; prediction remains distinct from observed outcome. | OWNER_PRIVATE; target/context may be SENSITIVE. | Snapshot; prediction revision DESC, prediction_id ASC. | Immutable revision cache; evaluation state requires current evaluation watermark. |
| `appraisal.inspect` | Owner-scoped appraisal record and inputs; does not trigger appraisal recomputation. | OWNER_PRIVATE + SENSITIVE. Internal valuation/context fields are not exposed to unrelated principals or generic diagnostics. | Snapshot; appraisal time DESC, appraisal_id ASC. | Revision-bound only; dependent context/evidence change invalidates derived appraisal view. |
| `attention.inspect` | Owner-scoped current or recorded attention allocation in the event store; no allocation or reprioritization side effect. | OWNER_PRIVATE; task/context labels may be SENSITIVE. | Local_committed for current allocation; event history ordered by store sequence ASC, event_id ASC. | No cache for current allocation; immutable historical event pages may be snapshot-cached. |
| `reasoning.inspect` | Owner-scoped reasoning assessment and linked evidence/artifacts; expose uncertainty and rejected alternatives where permitted. | OWNER_PRIVATE + SENSITIVE. Redact protected artifact contents and provider diagnostics. | Snapshot; assessment revision DESC, assessment_id ASC. | Immutable assessment revision cache; linked artifact availability and retention status checked at read. |
| `goal.get` | Owner-scoped derived goal only; must not alias an objective or plan. | OWNER_PRIVATE; success criteria and context may be SENSITIVE. | Local_committed for one goal ID; goal_id ASC, revision DESC for history. | Revision-bound cache only; goal mutation invalidates. |
| `plan.get` | Owner-scoped plan and steps/dependencies; include objective and goal revision references and current validity. | OWNER_PRIVATE + SENSITIVE. Redact private operation parameters and protected target details. | Snapshot; plan revision DESC, plan_id ASC. | Cache only immutable plan revision; current executability requires revalidation of every dependency and policy/permission version. |
| `decision.inspect` | Owner-scoped decision record and options/evidence; no decision is made by reading it. | OWNER_PRIVATE + SENSITIVE. Redact secret policy internals and protected alternatives. | Snapshot; decision time DESC, decision_id ASC. | Immutable decision revision cache; approval/policy status must be read from authoritative governance state, not cached here. |
| `task.status` | Owner-scoped task run and checkpoint metadata; actor must have task-read scope. | OWNER_PRIVATE; task payload/checkpoint details may be SENSITIVE. Redact worker diagnostics and unrelated operation parameters. | Local_committed; current state by task_run_id, history by revision DESC. No eventual mode for current task state. | No cache for current state; checkpoint artifacts are revision-bound and retention-checked. |
| `operation.status` | Owner-scoped operation, steps and provider receipts; never treat receipt as observed outcome. | OWNER_PRIVATE + SENSITIVE. Redact credentials, raw provider payloads and secret target parameters. | Local_committed; state/attempt revisions are authoritative; history ordered by attempt_number ASC then event sequence ASC. No eventual mode for dispatch/reconciliation decisions. | No cache for current state or revocation/approval; historical immutable receipts may be cached by revision with redaction re-evaluated. |
| `permission.inspect` | Authenticated owner and exact actor/device scope; return effective grants and policy version, not a grant-creation mechanism. | SECURITY_RESTRICTED. Only explicit effective fields; redact approval nonce, internal policy expressions, keys and unrelated device/actor data. | Local_committed; no eventual mode, no cursor unless a governance-authorized audit use explicitly requires one. | Never cached for authorization decisions; current policy/grant/OS permission must be re-read at enforcement time. |
| `audit.lookup` | Governance-authorized actor, owner scope and explicit audit purpose/time range; not a general memory search. | SECURITY_RESTRICTED. Field allowlist per audit purpose; redact secret values, key material, approval nonces and unrelated owners. | Snapshot in governance store; event sequence/time plus audit_record_id tie-breaker. | No cache for security investigations or authorization; immutable records may be paginated only within a stable snapshot. |
| `device.capabilities` | Owner-scoped descriptors for one authenticated, paired device; no device pairing, permission grant or live probing occurs. | OWNER_PRIVATE + SENSITIVE. Redact hardware identifiers, app inventory and raw OS/provider details unless exact purpose permits. | Local_committed for descriptor set; descriptor revision DESC, descriptor_id ASC. | Cache exact descriptor version with explicit probe time, expiry and invalidation on permission/device/provider changes. |

## 3. Mandatory executable query test set

The following cases apply to every query; domain-specific additions are listed after the common set. A query is not dispatch-ready until tests execute against its actual handler and assert both response and absence of writes.

| Test | Injection | Required assertion |
|---|---|---|
| QRY-001 owner isolation | Query owner A using owner B record IDs and filters | Same denial/not-found shape; no row/count/snippet/timing disclosure; no cross-owner read |
| QRY-002 actor scope | Authenticated actor lacks exact read grant | Denied; caller-supplied actor/owner filter cannot widen authority |
| QRY-003 classification | Mix OWNER_PRIVATE, SENSITIVE and SECURITY_RESTRICTED fields | Exact field allowlist/redaction; no secret in response, logs or diagnostics |
| QRY-004 read-only | Snapshot DB state and event/outbox counts before query | No domain write, event, outbox, receipt or state transition |
| QRY-005 consistency | Request unsupported consistency or inject concurrent commit | Refuse unsupported mode; snapshot response is internally consistent; no silent downgrade |
| QRY-006 cursor binding | Reuse cursor with another owner, actor, query, filter, sort, version or expired snapshot | Reject before row return; no fallback to offset pagination |
| QRY-007 pagination mutation | Insert/update/delete between pages | Snapshot stays stable or cursor returns explicit stale-view conflict; no silent duplicate/skip |
| QRY-008 deadline | Expire deadline during storage/index read | Bounded timeout; no unmarked partial result |
| QRY-009 row/byte budget | Exceed configured result rows and serialized bytes independently | Typed bounded result/error; no silent truncation |
| QRY-010 freshness | Expire descriptor/context/index watermark or change policy version | Stale data is labeled/refused; authorization state is never served from cache |
| QRY-011 malformed filters | Invalid filter type, unknown field, oversized expression or injection-shaped value | Reject before query execution; parameterized query only |
| QRY-012 unavailable store | Lock, disconnect or corrupt owning store | Typed unavailable/integrity error; no fallback to another owner's/store's data |
| QRY-013 source lineage | Remove/expire linked evidence or artifact | Preserve missing/tombstoned status; do not synthesize source or silently drop provenance |
| QRY-014 no side effects on retry | Repeat identical query and cursor request | Same view/continuation semantics; no mutation or implicit refresh |

Domain-specific assertions:
- `memory.search`: retrieval scores do not become beliefs; snippets preserve memory/evidence provenance; retention tombstones suppress results.
- `belief.inspect`: contradictory evidence remains visible as contradiction, not overwritten.
- `prediction.inspect`: prediction remains distinct from evaluation and observed outcome.
- `plan.get`: stale dependency or policy revision is disclosed; query does not repair or replan.
- `task.status`: pending pause/cancel is distinct from paused/cancelled; dispatched operation state is not inferred from task state.
- `operation.status`: provider receipt, independently observed outcome and reconciliation result remain separate.
- `permission.inspect`: effective OS permission and owner policy are distinguished; stale grant is not reported as effective.
- `audit.lookup`: filtering/redaction cannot disclose another owner or secret-bearing audit payload.
- `device.capabilities`: query reads last evidenced descriptor state only; it does not probe, request permissions or imply the capability is authorized.

## 4. Remaining measured and external gates

The semantic contract matrix is specified. The following cannot be claimed complete without evidence:
1. Per-query numerical timeout/row/byte budgets calibrated on the target runtime and representative data.
2. Concrete field-level classification annotations in each result schema and owning domain projection.
3. Handler-level executable tests for all 21 query entries, including database read-only assertions.
4. Target SQLite snapshot/cursor behaviour and concurrency tests.
5. Owner approval of the proposed first-release workflow/query subset.

Until those gates pass, the machine registry must retain all query entries as `design_only_not_dispatchable`. This matrix does not change registry dispatch status or imply implementation authorization.
