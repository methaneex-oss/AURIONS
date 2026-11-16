# AURIONS — PR-19 / PR-20 Model-Candidate Lifecycle Crosswalk

- **Status:** Builder-authored technical proposal; specified for owner review, not implemented or runtime-validated.
- **Revision baseline:** `docs/complete-system-architecture` at `62599932254bc5e17556ea368fe94c52df438691`.
- **Authority:** Owner-accepted first-release product baseline PR-01…PR-20; D-04 command/query subset remains a builder proposal pending owner acceptance.
- **Purpose:** Define one traceable, enforceable path from a model-training experiment to a governed active model artifact and a verifiable rollback.
- **Boundary:** This document does not authorize training, worker dispatch, model activation, implementation, PR merge or planning exit. Existing registries remain design-only/non-dispatchable.

## 1. Finding

The repository already specifies the individual learning, worker, artifact, evaluation, approval and evolution mechanisms. The missing part is the end-to-end identity and persistence crosswalk between them.

The existing payloads expose distinct identifiers—`learning_update_id`, `experiment_id`, `attempt_id`, `job_id`, `artifact_id`, `evaluation_id`, `proposal_id`, `candidate_id`, approval `request_id` and active-pointer revision—but do not yet require all of the links needed to prove that they refer to the same candidate.

Specific gaps confirmed against the current schemas and DDL:

1. `learningExperimentRequest` and `learningExperimentCompleted` do not carry a required `learning_update_id`; the worker request/result contracts do not explicitly carry the experiment/attempt identity and training-configuration digest.
2. `learningCandidateEvaluationRequest` and `learningCandidateEvaluated` identify the candidate artifact, but do not require its source learning update, experiment and attempt identities.
3. `learning_update_details` persists baseline/candidate/protocol/metrics/regression artifact IDs, but not experiment ID, attempt ID or the immutable candidate-evaluation ID.
4. `evolution_proposals` stores a proposal ID and candidate artifact reference, but has no candidate ID, no explicit source-learning lineage and no candidate-specific artifact digest field. The lifecycle request/event schemas require candidate IDs.
5. The proposed DDL has no owner-scoped, versioned active-candidate pointer or append-only pointer-transition history, although activation and rollback contracts depend on an exact active-pointer revision.
6. Approval records can bind an exact operation digest, but the model-candidate activation digest's complete field set is not yet stated in one canonical contract.
7. The `learning.update.accepted.v1` producer is an internal Learning-supervisor transition. Its trigger matrix says it consumes an authenticated owner/governance decision, but the event text incorrectly calls a public learning-acceptance command an API gap. The generic `approval.request` / `approval.decide` path can carry that decision; no separate `learning.accept` command is required if the exact target and digest are bound as specified below.

These are design-contract omissions, not evidence that a working training or activation implementation exists.

## 2. Identity model — identifiers are not interchangeable

| Identifier | Meaning | Authority/source |
|---|---|---|
| `learning_update_id` | The durable proposed change to a learning mechanism/model target | Learning subsystem |
| `experiment_id` | One immutable experiment definition, including baseline, dataset, protocol, code/config digest, seed and budget | Learning supervisor |
| `attempt_id` | One execution attempt of that experiment; retries create new attempt IDs | Worker supervisor |
| `job_id` | One isolated worker job; linked to exactly one experiment attempt | Worker supervisor |
| `artifact_id` + SHA-256 | Immutable bytes, such as dataset manifest, baseline, trained candidate, metrics or regression report | Artifact registry |
| `evaluation_id` | One immutable held-out evaluation result for an exact candidate/baseline/dataset/protocol set | Learning evaluator |
| `proposal_id` | The rationale, impact/risk and proposed evolution transition | Evolution subsystem |
| `candidate_id` | One candidate lifecycle identity bound to one proposal and one immutable candidate artifact digest | Evolution subsystem |
| approval `request_id` / `decision_id` | One exact owner decision request and its authenticated decision | Governance subsystem |
| active-pointer revision | Monotonic version of the active artifact selection for one owner/mechanism | Evolution activation manager |

A candidate is not its proposal, artifact, evaluation or approval. The proposal explains why a change is proposed; the artifact identifies bytes; the evaluation identifies evidence; the candidate ID identifies the lifecycle object; the approval identifies the owner's decision.

**Candidate identity rule:** generate a canonical UUIDv5 from the fixed namespace URL and the exact string `aurions:candidate:v1:{owner_ref}:{proposal_id}:{artifact_sha256}`. Persist that candidate ID in lifecycle events and the active-pointer/history records. Every command must recompute it from the owner-scoped proposal and artifact manifest and reject a mismatch. A proposal may bind one candidate artifact under the current DDL shape; multiple candidate artifacts require separate proposal records rather than silently replacing an existing candidate.

## 3. Canonical lifecycle

### 3.1 Propose and prepare learning

1. `learning.update.propose` creates a quarantined learning update with evidence lineage, target mechanism, hypothesis, scope, frozen baseline and evaluation protocol. It does not alter active memory or model state.
2. `learning.experiment.submit` creates an immutable experiment definition linked to that `learning_update_id`. It must bind baseline artifact ID/digest, dataset-manifest ID/digest and split, training/evaluation protocol ID/digest, code revision, canonical training-configuration digest, seed where supported, resource budget and deadline.
3. The Learning supervisor creates a new `attempt_id` and a `job_id`, persists the experiment/attempt mapping, and emits `worker.job.requested.v1`. The worker receives only declared immutable inputs and bounded resources; it has no production database credentials, owner authenticator, governance keys or activation authority.
4. A retry is a new attempt, never a mutation of the prior attempt. A worker timeout or cancellation does not imply that the job did not run.

### 3.2 Register and evaluate the trained artifact

5. Worker output is untrusted. The Artifact registry validates bytes, SHA-256, size, media type, owner, sensitivity, license/provenance and storage reference, then registers the artifact in quarantine. Registration is not acceptance or activation.
6. `learning.experiment.completed.v1` is emitted only after the Learning supervisor matches the terminal worker result to the persisted `job_id`, `experiment_id` and `attempt_id`; verifies code/data/config hashes, budget/deadline and candidate manifest; and records the result. Failed, partial or unverifiable output cannot be treated as a successful candidate.
7. `learning.candidate.evaluate` evaluates the exact candidate artifact digest against the frozen baseline, leakage-controlled held-out dataset, evaluation protocol and regression suite. Its immutable `evaluation_id` must reference the exact `learning_update_id`, `experiment_id`, `attempt_id`, candidate artifact digest and baseline/dataset/protocol revisions.
8. Evaluation status is `passed`, `failed` or `inconclusive`. Missing evidence is not a pass. A passed evaluation means only that the candidate met its predefined thresholds on the stated evaluation distribution; it does not prove general intelligence or unrestricted improvement.

### 3.3 Accept the learning update

9. The owner decision uses the existing `approval.request` and `approval.decide` commands. The approval request's `target_ref` identifies the exact learning update/candidate; its `operation_digest` binds the learning-update ID, candidate artifact ID and digest, baseline, evaluation ID/digest, dataset/protocol revisions, decision scope, policy version and expiry.
10. After receiving `approval.decided.v1`, the Learning supervisor independently verifies authenticated owner identity, exact target, approved digest, current policy, expiry, owner scope and the passing evaluation. It then emits `learning.update.accepted.v1` as an internal event and records the approval/evaluation lineage. This event records acceptance only; it does not activate the model.
11. No separate public `learning.accept` command is required. The generic approval API is the owner-facing decision surface; the Learning supervisor is the trusted producer of the acceptance event. The event producer matrix and registry must state this consistently.

### 3.4 Propose and evaluate governed evolution

12. `evolution.change.propose` creates a proposal linked to the exact learning update, experiment, attempt, learning evaluation and candidate artifact digest. It assigns the candidate lifecycle ID using the rule in §2. The candidate remains quarantined.
13. `evolution.candidate.evaluate` is distinct from `learning.candidate.evaluate`. The latter proves model-training performance on held-out data; the former records the governed evolution/system-regression assessment for the proposed active-runtime change. Neither event substitutes for the other.
14. For a model candidate, activation requires both the passing PR-20 learning evaluation and the passing governed evolution evaluation. The proposal and candidate lifecycle records must preserve both evaluation references and their artifact digests.

### 3.5 Exact owner approval and activation

15. A separate approval request is bound to the exact activation operation. Its canonical digest covers at least: authenticated owner reference; operation ID; action (`candidate.activate`); target mechanism; candidate ID; proposal ID; candidate artifact ID and SHA-256; learning evaluation ID and report digest; evolution evaluation ID and report digest; current active-pointer revision and previous candidate ID; policy version; scope; and expiry.
16. The activation command must require a non-null `approval_ref` and `evaluation_ref`. It verifies that the approval request and decision belong to the authenticated owner, match the exact operation ID and recomputed digest, are approved and unexpired, have not been revoked, and are valid under current policy. The candidate artifact digest and both required evaluations are rechecked at commit time.
17. Activation is a durable cross-store saga, not a distributed ACID transaction: the events store records intent/steps/recovery; governance records exact approval consumption and audit in its local transaction; memory commits the owner/mechanism active-pointer compare-and-swap and append-only transition history in its local transaction. Each store has its own outbox.
18. The active pointer advances only if its expected revision matches. `candidate.activated.v1` is a saga-completion event and is emitted only after all required steps are reconciled. A partial/interrupted saga remains pending or uncertain; it must not be reported as activated.

### 3.6 Rollback

19. Rollback is a new, separately authorized operation. It identifies the exact active candidate, the exact previously approved candidate/artifact to restore, the expected active-pointer revision and the reason/evidence.
20. The rollback approval digest binds the current candidate, exact prior candidate/artifact digest, target mechanism, pointer revision, operation ID, owner and policy. The request must carry non-null `approval_ref` and `rollback_ref`.
21. The saga restores the exact prior artifact pointer, verifies its digest, appends rollback history and governance audit, and reconciles every store. It preserves the failed candidate and all experiment/evaluation evidence. `candidate.rolled_back.v1` is emitted only after reconciliation. Rollback is not deletion and does not rewrite the original evaluation.

## 4. Persistence and registry reconciliation required before implementation

The following are the proposed contract amendments, not claims about the current files:

- Extend learning payloads with explicit `learning_update_id`, `experiment_id`, `attempt_id`, `job_id`, `configuration_digest` and `evaluation_id` bindings where applicable. A model-training worker request/result must echo its experiment/attempt identity and configuration digest.
- Extend candidate-evaluation request/result payloads with the source learning update, experiment and attempt IDs and exact candidate artifact SHA-256.
- Extend evolution proposal/lifecycle payloads with candidate identity, candidate artifact digest and source learning/evaluation references.
- Add action-specific schema conditions: activation requires a non-null evaluation and approval reference; rollback requires a non-null approval and exact rollback reference. A nullable property being present is not equivalent to a valid reference.
- Add an additive memory migration (next memory migration version) for the experiment/attempt/evaluation references in `learning_update_details`; source-learning lineage and candidate artifact ID/digest in `evolution_proposals`; an owner/mechanism-scoped `active_candidate_pointers` table with monotonic revision; and append-only candidate activation/rollback history. Existing proposals without verified candidate identity must remain non-activatable until explicitly reconciled; do not invent/backfill identities by inference.
- Keep approval request/decision rows in `aurion_governance.db`; keep cross-store saga intent, steps and recovery in `aurion_events.db`; keep the active pointer and candidate/artifact projection in `aurion_memory.db`. No cross-file foreign key or distributed transaction is implied.
- Update the command/event registries, fixtures, command transition matrix, event producer/consumer matrix, ingress trigger matrix, store-local saga matrix and validator assertions together. Do not make any registry entry dispatchable.

The current DDL does not yet provide these experiment/evaluation links or the active-pointer projection. Until the additive schema and validator changes are committed and checked, this crosswalk is a complete **design proposal**, not a closed machine-contract or runtime implementation.

## 5. Acceptance evidence mapping

| Requirement | Existing contract/evidence IDs | Required proof |
|---|---|---|
| PR-19 reproducible training/provenance | LE-001…LE-004; CC-033; `learning.experiment.submit`; worker/artifact contracts | Exact baseline/dataset/config/code/seed/budget; attempt/job linkage; immutable candidate artifact digest; rerun and failure/cancellation/retry evidence |
| PR-20 held-out evaluation/quarantine | LE-005…LE-007; CC-034; `learning.candidate.evaluate` | Frozen baseline; leakage-controlled held-out and unseen controls; repeatable metrics; regression result; candidate remains quarantined |
| Owner acceptance | `approval.request`, `approval.decide`, `approval.decided.v1`, `learning.update.accepted.v1` | Authenticated owner, exact target and digest, current policy, expiry/revocation checks; no model self-approval |
| Governed candidate evaluation | CC-037; `evolution.candidate.evaluate`; `evolution.candidate.evaluated.v1` | Candidate/proposal/artifact/evaluation identity parity; independent system-regression result |
| Activation | CC-038; `candidate.activated.v1`; cross-store saga matrix | Exact owner approval digest, expected active-pointer revision, verified artifact/evaluations, successful saga reconciliation |
| Rollback | CC-039; `candidate.rolled_back.v1`; cross-store saga matrix | Separate exact rollback approval, exact prior artifact digest, pointer restoration, preserved failed-candidate lineage and recovery evidence |

Relevant integrated scenarios include CM-011…CM-013 for learning/outcome feedback and CM-017 for governed evolution. These scenarios are specifications, not executed runtime tests.

## 6. Closure boundary

- **Specified by this document:** identifier semantics, lifecycle ordering, approval binding, activation/rollback saga boundary and the exact schema/DDL/validator work still required.
- **Not yet reconciled in machine contracts:** the payload additions and additive memory migration listed in §4.
- **Not implemented:** training worker, experiment store, candidate registry, approval consumer, active pointer, saga coordinator or runtime handlers.
- **Not validated:** target-device training/resource feasibility, C++/Python conformance, crash/replay/rollback execution, held-out improvement or independent review.
- **Owner gate:** D-04 remains pending owner acceptance of the exact command/query subset and its crosswalk. Planning exit and implementation authorization remain separate explicit owner decisions.

No model, worker or generated artifact may approve, activate or roll back its own candidate.
