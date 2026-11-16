# AURIONS — Dataset Source Rights and Training Authorization Contract

- **Status:** Builder technical contract proposal derived from owner decision MD-16; initial JSON Schema, fixture and validator coverage now exists. Durable persistence, trusted event contracts and executable enforcement remain open.
- **Authority:** [Model Architecture and Training Owner Decisions — MD-16](MODEL-ARCHITECTURE-AND-TRAINING-OWNER-DECISIONS.md).
- **Scope:** Source acquisition, training-use authorization, immutable dataset manifests, worker admission, revocation and derived-artifact impact.
- **Boundary:** This document does not authorize corpus ingestion, training, worker dispatch, model activation, implementation or planning exit. Unapproved sources are denied by default.

## 1. Governing invariants

1. Public accessibility is not proof of permission to train.
2. Source acquisition, memory retention, dataset inclusion, model-training use, evaluation use, external disclosure and model activation are distinct purposes and permissions.
3. Every included source must have an immutable source identity, content digest, provenance and a currently valid rights/authorization record covering the exact training purpose, owner, scope and validity interval.
4. A dataset manifest is immutable and versioned. Any change to source membership, content, transformation, split, rights evidence or policy creates a new manifest identity and digest.
5. Workers receive only a manifest and source artifacts already admitted by the trusted supervisor. A worker cannot add sources, change purpose, widen scope or self-authorize.
6. Revocation blocks future acquisition, dataset creation, worker admission and reuse immediately after the revocation is committed. Existing derived artifacts are traced and assessed; no automatic claim of weight removal is permitted.
7. Memory retention permission does not imply training permission. Training permission does not imply retention, disclosure or evaluation permission.
8. The source-rights and manifest records are governance/provenance evidence, not a way to encode learned behaviour or fixed source-to-behaviour mappings.

## 2. Source-rights authorization record

The proposed versioned `datasetSourceAuthorization` record must contain:

| Field | Requirement |
|---|---|
| `authorization_id` | Immutable UUID identifying one authorization grant/version |
| `owner_ref` | Exact owner/security principal that controls the authorization |
| `source_ref` | Stable source identity; not a display URL alone |
| `source_content_sha256` | Digest of the exact source bytes or immutable source revision |
| `source_origin` | Acquisition origin/method and timestamp, with provenance references |
| `rights_holder_ref` | Rights holder/licensor identity where applicable |
| `authorization_basis` | Verified basis such as license, contract, public-domain determination or explicit owner authorization; never merely “publicly accessible” |
| `license_or_terms_ref` | License/terms identifier and immutable reference |
| `license_or_terms_digest` | Digest of the exact terms version reviewed |
| `permitted_purposes` | Explicit purpose allowlist (e.g. foundation pretraining, instruction SFT, preference training, outcome training, evaluation) |
| `training_permission` | Explicit allow/deny decision for model-weight training |
| `memory_retention_permission` | Separate allow/deny decision; must not be inferred from training permission |
| `private_data_classification` | Explicit classification and privacy/sensitivity scope |
| `private_data_authorization_ref` | Required evidence reference when private/personal data is authorized |
| `owner_scope` | Owner, project/model family and permitted dataset scope |
| `valid_from`, `expires_at` | Validity interval; expiry is enforced at dataset admission and worker dispatch |
| `policy_version` | Exact policy version used to decide authorization |
| `status` | Pending, active, expired, revoked, denied or superseded |
| `revoked_at`, `revocation_ref` | Required for revoked state; immutable revocation evidence |
| `created_at`, `supersedes_authorization_id` | Audit chronology and explicit replacement lineage |

Authorization is purpose-specific and content-specific. A changed source digest, changed license terms, new purpose, changed owner scope or expired grant requires a new authorization decision. A source may be retained in memory while excluded from training.

## 3. Immutable dataset manifest

The proposed versioned `datasetManifest` record must contain:

- `dataset_manifest_id`, schema version, owner/model-family scope, creation time and immutable manifest digest.
- Exact training stage/purpose and intended model/tokenizer generation.
- A complete list of included source records, each binding `source_ref`, exact content digest, `authorization_id`, authorization/terms digest and transformation lineage.
- Explicit exclusions and reasons, including denied, expired, revoked, incompatible-license, duplicate, low-quality, private-without-authorization and evaluation-contamination sources.
- Versioned transformation/preprocessing pipeline and code/configuration digest.
- Deduplication and quality-filter reports, language/domain classification and sampling/curriculum configuration.
- Train/validation/held-out split identities and digests, with leakage/contamination checks.
- Rights/policy snapshot and authorization evaluation time; the manifest is not valid if any included grant is invalid for the exact purpose/scope.
- Derived-artifact lineage references for checkpoints, evaluation outputs and candidate artifacts produced from this dataset.

The manifest must be reproducible from its immutable source identities, transformation versions, split assignments and policy snapshot. Dataset digest alone does not prove rights; authorization evidence remains independently resolvable.

## 4. Admission and enforcement sequence

1. **Acquire:** record source provenance, exact content digest, classification and rights/terms evidence. Unknown rights remain denied.
2. **Authorize:** the trusted governance path records the source-specific grant. Private data requires explicit authorization evidence. License and permitted-purpose compatibility are checked.
3. **Curate:** the dataset builder proposes inclusion/exclusion and transformations. It cannot grant rights or override denied sources.
4. **Freeze manifest:** the supervisor validates every included source against active authorization, exact purpose, owner/model scope, validity, terms digest and policy version; then seals the manifest and digest.
5. **Admit worker:** immediately before dispatch, the supervisor rechecks manifest integrity, source authorization status, expiry/revocation, model purpose and resource budget. The worker receives only immutable admitted artifacts.
6. **Register outputs:** candidate/checkpoint manifests preserve dataset-manifest identity and source lineage. Artifact registration does not erase source rights or create new authorization.
7. **Evaluate and activate:** existing PR-19/PR-20 evaluation and approval gates remain mandatory; dataset authorization does not substitute for candidate evaluation or activation approval.

Any mismatch or unknown state fails closed. A worker result referencing an unadmitted source or changed manifest is rejected and quarantined.

## 5. Revocation and derived-artifact impact

Revocation is an append-only governance event against an exact authorization identity. It immediately blocks future use and initiates a lineage query over:

- Dataset manifests and derived dataset versions.
- Training experiments and attempts.
- Checkpoints, candidate artifacts and model generations.
- Evaluation datasets/reports and downstream candidate proposals.
- Backups, caches and synchronized copies where applicable.

The impact assessment records affected artifact identities/digests, source contribution where measurable, whether the artifact was merely staged or used in training, available mitigations, decision authority and outcome. Possible outcomes include exclusion from future manifests, quarantine of affected artifacts, retraining from a compliant dataset, or validated unlearning where a method and test evidence support it. If influence cannot be isolated, record the uncertainty and apply the conservative policy; do not assert that deletion of a source file erased its influence from weights.

Revocation must not silently rewrite historical manifests or experiment evidence. New manifests and artifacts carry the corrected rights state; historical records remain auditable subject to their own retention/deletion policy.

## 6. Persistence and event requirements

The current JSON Schema definitions `datasetSourceAuthorization` and `datasetManifest` encode the source-rights and immutable-manifest payload shapes. Positive fixtures and negative controls cover missing rights basis, private-data authorization, source authorization references and empty manifests; `validate_schemas.py` also checks the positive fixture's source/content/terms/owner/model-scope/purpose binding. These are shape and fixture checks, not persistence or runtime enforcement. The eventual persistence contract must store authorization versions in the governance authority boundary, immutable dataset manifests and source membership/lineage in the appropriate owning store, revocation records and derived-artifact impact assessments. It must enforce owner scope, uniqueness, immutable digests, valid status transitions, authorization expiry/revocation checks and referential lineage.

The state transitions still require trusted internal events for authorization granted/denied/revoked, dataset manifest sealed, admission blocked and revocation impact assessed. Those event entries have not been added. Their producer/consumer ownership, owner transitions, idempotency, outbox boundaries and recovery must be reconciled against the existing event registry and three-store saga model before adding them. Separately, candidate activation and rollback events now reference state-specific schemas that require the corresponding evidence. Do not invent public commands or make any registry entry dispatchable as part of this proposal; D-04 remains a separate owner gate.

A new additive SQLite migration is required only after the payload schema, fixtures, registry/event semantics and migration ownership are reconciled. It must not introduce cross-file foreign keys or imply distributed ACID transactions. The existing local-outbox and cross-store saga rules continue to apply.

## 7. Required acceptance evidence

- Positive: verified public-domain source; compatible licensed source; explicit private-data authorization; separate memory-retention and training permissions; multi-source manifest with exact digest and splits; reproducible manifest rebuild; valid worker admission.
- Negative: public URL with unknown rights; incompatible/restricted license; private source without explicit authorization; expired grant; revoked grant; terms digest changed; content digest changed; purpose mismatch; owner/model scope mismatch; worker attempts source expansion; manifest tampering; evaluation split leakage; duplicate source identity with different bytes.
- Revocation: future admission denied immediately; all dependent manifests/artifacts discovered; active candidate impact escalated to governance; retraining/unlearning claims require their own held-out verification; audit survives replay/restore without resurrecting revoked authorization.
- Recovery: crash before/after authorization commit, manifest seal, worker dispatch, revocation, impact assessment and outbox relay; idempotent replay and no blind worker retry.
- Security: worker cannot read governance secrets, change authorization state, broaden source scope or bypass owner approval.

These are planned acceptance cases until machine fixtures and executable handlers/tests exist.

## 8. Closure status

- **Owner decision:** MD-16 accepted.
- **Specified in this document:** source-rights record, dataset-manifest structure, admission checks, revocation/lineage behavior and acceptance evidence.
- **Machine contracts:** initial JSON Schema definitions, positive/negative fixtures and validator cross-binding checks are present for source authorization and dataset manifests; state-specific activation/rollback event schemas are also bound in the event registry. Dataset-rights persistence, authorization/revocation/sealing/admission/impact event definitions, event matrices and runtime enforcement remain open.
- **Runtime:** no dataset-rights enforcement, worker admission or revocation-impact handler is implemented or validated.
- **Gate:** do not admit nontrivial/ambiguous sources or begin training until the machine contracts and authorization enforcement are implemented and verified under the separately authorized implementation milestone.
