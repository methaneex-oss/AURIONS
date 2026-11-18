# AURIONS — Dataset Rights Persistence and Trusted-Event Crosswalk

- **Status:** Builder technical contract integrated into schemas, event registry/matrices, governance v5 and memory v9 migrations, and INT-004. Exact-head host SQLite execution passed in run 44035128973; runtime enforcement and target-device/cross-store fault validation remain open.
- **Authority:** MD-16 in [Model Architecture and Training Owner Decisions](MODEL-ARCHITECTURE-AND-TRAINING-OWNER-DECISIONS.md); normative model requirements in [Initial Engineering Specification §27](INITIAL-ENGINEERING-SPECIFICATION.md).
- **Current machine baseline:** Source authorization and manifest schemas, five event-specific payload schemas, positive fixtures, eleven dataset-rights negative controls, validator cross-binding, five registered events, both event matrices and INT-004 are present. Governance v5 and memory v9 DDL contracts and SQLite smoke assertions passed exact-head run 44035128973 (20 ordered DDL files, host SQLite 3.46.1).
- **Boundary:** No new public commands, dispatch permission, corpus-ingestion permission, worker execution, training, model activation, implementation authorization or planning-exit approval is created here.

## 1. Authority and storage boundaries

The data-rights path crosses three existing SQLite authority boundaries. Each store owns its own durable state and local outbox. Cross-store references are opaque stable IDs/digests, not foreign keys.

| Store | Proposed authoritative records | Must not become authoritative for |
|---|---|---|
| `aurion_governance.db` | Immutable source-authorization versions; exact license/terms evidence references/digests; purpose/owner/model scope; private-data authorization evidence; append-only revocation records; governance decision/audit linkage | Dataset contents, worker output, model artifacts or active-model pointer |
| `aurion_memory.db` | Immutable dataset-manifest artifact/metadata; source-to-manifest membership; exclusions; preprocessing and split references; dataset-to-experiment/checkpoint/candidate lineage; durable revocation-impact findings over memory-owned artifacts | Granting or revoking source rights; owner authentication; governance decisions |
| `aurion_events.db` | Durable cross-store revocation-impact operation, ordered steps, idempotency keys, receipts, recovery journal and central event archive | Source-rights truth or dataset membership truth; distributed ACID transaction |

The existing store-local outbox rule remains mandatory: a governance mutation commits with the governance outbox; a memory mutation commits with the memory outbox; the event archive receives each envelope asynchronously. No cross-file foreign key, distributed transaction or synchronous central-archive dependency is implied.

## 2. Governance persistence contract — migration v5

`schemas/persistence/aurion_governance.migration_v5.sql` adds immutable authorization versions and append-only revocation records. It uses the existing governance approval-request table and governance-local outbox. No cross-store foreign key is introduced.

### 2.1 Immutable authorization versions

Proposed logical record: `dataset_source_authorizations`.

Minimum persisted identity and evidence:

- Authorization UUID and owner/security principal.
- Stable source identity and exact source-content SHA-256.
- Acquisition origin/method and timestamp.
- Rights-holder reference, authorization basis, immutable license/terms reference and digest.
- Permitted-purpose set, explicit training permission and separate memory-retention permission.
- Privacy classification and explicit private-data authorization evidence where required.
- Project/model-family/dataset scope, policy version, validity interval and creation chronology.
- Immutable record digest and optional superseded-authorization identity.

Authorization records should be immutable snapshots. A changed source digest, terms digest, owner/model scope, permitted purpose or authorization basis creates a new version; it must not rewrite an earlier grant.

### 2.2 Append-only revocation

Proposed logical record: `dataset_source_authorization_revocations`.

Each revocation binds one exact authorization ID and record digest, owner, revocation reason/evidence, actor/approval reference, policy version and timestamp. The revocation record is append-only and unique/idempotent for the authorization and revocation operation.

The effective authorization check is: exact authorization version exists; its record digest matches; the grant permits the requested purpose and scope; it is currently valid; and no committed revocation/superseding state blocks it. A stale cached `status=active` value is never sufficient after revocation.

Do not update a grant in place to erase its prior state. The effective revoked state is derived from the immutable revocation record and the authorization-version history. If the payload representation needs a post-revocation snapshot, it must reference the prior grant and revocation evidence without mutating historical bytes.

## 3. Memory persistence contract — migration v9

Add an additive memory migration only after the dataset payloads, artifact ownership and query projections are reconciled.

### 3.1 Sealed manifest projection

Proposed logical record: `dataset_manifests`, keyed by immutable manifest UUID and linked to the existing artifact registry entry that stores the canonical manifest bytes.

Persist owner/model-family scope, training purpose, model generation, tokenizer artifact, manifest digest, rights-policy snapshot reference/digest, authorization evaluation time, lifecycle and creation time. A manifest is sealed once; any change creates a new manifest ID/digest.

### 3.2 Source membership and exclusions

Proposed logical records:

- `dataset_manifest_sources`: manifest ID, stable source identity, source artifact/content digest, authorization ID and record digest, license/terms digest, transformation lineage and owner/model scope.
- `dataset_manifest_exclusions`: manifest ID, source identity, exclusion reason and evidence reference.
- `dataset_manifest_splits`: manifest ID, split identity (train/validation/held-out), split artifact/reference and digest, leakage/contamination evidence.

Authorization IDs are references into governance storage and deliberately have no cross-database foreign key. Before sealing and again before worker admission, the trusted supervisor resolves them against the authoritative governance database and verifies exact digest, status, purpose, scope, expiry and revocation.

### 3.3 Derived-artifact impact

Proposed logical record: `dataset_revocation_impacts`, owned by memory because it describes the effect on memory-owned dataset and model artifacts. It binds an exact revocation ID/digest to the affected manifest, experiment, attempt, checkpoint, candidate/evaluation artifact references, observed influence, uncertainty, disposition and evidence. Historical manifests and experiment records are not rewritten.

## 4. Registered trusted internal event contracts

The five event definitions below are registered as design-only/non-dispatchable trusted internal events. They are not public commands. The existing generic `approval.request`, `approval.decide` and `approval.revoke` governance path remains the owner-facing decision surface where an owner decision is required. No `dataset.authorize`, `dataset.revoke` or other new public command is introduced by this design.

| Proposed event | Trusted producer | Owning store | Required transition |
|---|---|---|---|
| `dataset.source.authorization.decided.v1` | Governance supervisor consuming the exact authenticated approval decision | Governance | Append immutable active/denied authorization version bound to exact source bytes, terms, purpose, owner/model scope and policy |
| `dataset.source.authorization.revoked.v1` | Governance supervisor after exact revocation is durably committed | Governance | Append revocation and immediately make future authorization checks fail; no waiting for event-archive relay |
| `dataset.manifest.sealed.v1` | Dataset supervisor after validating every included source against current governance state and sealing the immutable manifest | Memory | Append sealed manifest and source membership; no worker dispatch is implied |
| `dataset.admission.blocked.v1` | Learning/worker supervisor at pre-dispatch revalidation | Memory or worker-owned store according to the actual admission aggregate | Record exact manifest/source/authorization mismatch and deny dispatch; never ask the worker to decide rights |
| `dataset.revocation.impact.assessed.v1` | Trusted revocation-impact coordinator after required owning-store findings are reconciled | Events coordinator, with memory-owned impact evidence | Record affected artifacts, uncertainty and governed disposition; do not claim automatic removal from model weights |

The five dataset-rights events are already reconciled across payload schemas/fixtures, event-registry entries, producer/consumer rows, ingress-trigger rows and integrated scenario INT-004. The exact-head validator checks the 94-event registry against the producer/consumer matrix and checks the 27 non-Action-Gateway non-command triggers against the ingress matrix. The current inventory is 94 events: 52 have exact command-producer bindings; 42 have no command producer binding (15 Action Gateway lifecycle transitions and 27 other trusted/internal triggers). All 94 remain design-only/non-dispatchable. This is structural reconciliation, not independent semantic acceptance or runtime validation.

Before runtime implementation, preserve and test for every event: payload schema and fixture; exact producer origin, owning store, trigger and consumer; producer/consumer and ingress matrix parity; outbox/saga semantics; idempotency and causal ordering; and crash/replay, poison-event and recovery behavior. Independent semantic review and owner acceptance of the 42 non-command trigger specifications remain outstanding.

## 5. Revocation sequence and fail-closed behavior

1. Governance validates the exact owner/approval/policy scope and commits the append-only revocation record with its local outbox.
2. From that commit onward, any source authorization check fails for the revoked authorization ID. Dataset sealing and worker admission must query the authoritative governance state; if governance is unavailable or the state cannot be resolved, deny admission.
3. The governance outbox relay publishes the revocation envelope to the event archive. Relay delay does not weaken the immediate local authorization check.
4. The event coordinator creates or resumes a stable revocation-impact operation with deterministic step IDs and idempotency keys.
5. Memory locates all manifests and derived artifacts referencing the authorization ID/digest; it records findings and quarantines affected unstarted datasets/artifacts where policy requires.
6. The supervisor identifies active worker attempts. It requests safe cancellation where supported; an uncertain or unresponsive worker attempt remains uncertain and its outputs remain quarantined.
7. The impact assessment records whether the source was merely staged, included in a manifest, consumed by training, or contributed to a checkpoint/candidate. Unknown influence is recorded as uncertainty, not guessed away.
8. A governed disposition decides exclusion, quarantine, compliant retraining or validated unlearning. Active-candidate impact requires the existing evolution/governance approval and rollback process where applicable.
9. Each owning store commits its mutation and local outbox atomically. The coordinator records receipts and recovery evidence; replay is idempotent and cannot resurrect revoked authorization.

## 6. Migration ordering and acceptance gates

The schema/event contract and persistence design stages have now been encoded in the current planning artifacts. The remaining sequence is:

1. **Completed as specification:** payload schemas, fixtures, validator cross-binding and five event-specific negative controls.
2. **Completed as specification:** five trusted event payloads, registry entries, producer/consumer rows, ingress triggers and INT-004 references.
3. **DDL added:** governance migration v5 defines immutable authorization versions, append-only revocation evidence and use of the governance-local outbox.
4. **DDL added:** memory migration v9 defines sealed manifests, source membership/exclusions/splits and derived-artifact impact lineage with memory-local outbox enforcement.
5. **No events migration added:** the existing events-store operation/step/recovery schema already represents the saga operation, ordered steps and recovery journal; add an events migration only if later tests identify a concrete missing durable field/table.
6. **Host SQLite smoke executed:** exact-head PR run [44035128973](https://github.com/methaneex-oss/AURIONS/actions/runs/44035128973) on commit `99552edca1bc6174d7ec76ee75b03bdd2ca15caa` passed all nine workflow steps and executed the complete 20-file three-store DDL chain on host SQLite 3.46.1, including governance v5 and memory v9 dataset-rights assertions. Cross-store crash/replay, target-device compatibility and runtime-handler evidence remain open.

Required negative tests include unknown rights, denied/expired/revoked authorization, changed source or terms digest, purpose/owner/model-scope mismatch, private data without evidence, manifest tampering, worker source expansion, duplicate source identity with different bytes, replay after revocation and attempted resurrection from backup/sync.

## 7. Current disposition

- **Owner decision MD-16:** recorded and closed.
- **Payload schema/fixtures:** initial machine definitions and positive/negative validation coverage are present.
- **Activation/rollback lifecycle events:** state-specific payload schemas are present and event-registry bindings are updated.
- **Persistence:** governance v5 and memory v9 DDL contracts passed exact-head host SQLite execution in run 44035128973; target Android/Termux behavior, cross-store crash/replay and runtime enforcement remain unverified.
- **Trusted dataset-rights events:** five events are registered and reconciled across both event matrices and INT-004.
- **Runtime:** no source authorization, dataset sealing, worker admission or revocation-impact handler is implemented or validated.
- **Dispatch/training:** all registries remain design-only/non-dispatchable; no corpus ingestion or training is authorized by this document.
