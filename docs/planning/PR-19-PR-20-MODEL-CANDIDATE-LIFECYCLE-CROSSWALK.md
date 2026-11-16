# AURIONS — PR-19 / PR-20 Model-Candidate Lifecycle Crosswalk

- **Status:** Builder-authored technical proposal; specified for owner review, not implemented or runtime-validated.
- **Revision baseline:** `docs/complete-system-architecture` audited at `66a1a05659600f5261170d4318fd7b7d494e9524`; subsequent documentation consolidation is recorded in the current branch history.
- **Authority:** Owner-accepted first-release product baseline PR-01…PR-20; D-04 command/query subset remains a builder proposal pending owner acceptance.
- **Purpose:** Define one traceable, enforceable path from a model-training experiment to a governed active model artifact and a verifiable rollback.
- **Model decision register:** [MD-01…MD-16 — Model Architecture and Training Owner Decisions](MODEL-ARCHITECTURE-AND-TRAINING-OWNER-DECISIONS.md).
- **Boundary:** This document does not authorize training, worker dispatch, model activation, implementation, PR merge or planning exit. Existing registries remain design-only/non-dispatchable.

## 1. Finding

The current branch now contains most of the model-candidate identity and persistence crosswalk that the earlier draft identified as missing. The payload schemas and memory migration v8 have advanced; the earlier gap list was not updated consistently and must not be read as a description of the current files.

Current contract coverage includes:

- `learningExperimentRequest` requires the learning-update identity, experiment identity, configuration digest, dataset split, training manifest, initialization method/artifact, architecture configuration, tokenizer artifact and random seed.
- `learningExperimentCompleted`, `workerRequest` and `workerResult` carry the learning-update, experiment, attempt and job identities plus configuration-digest continuity.
- Candidate-evaluation request/result payloads bind the source learning update, experiment, attempt, candidate artifact digest, baseline, dataset and protocol digests.
- `evolutionProposed` carries candidate identity, source-learning lineage and candidate artifact digest when a candidate artifact is present. `evolutionCandidateActionRequest` has action-specific non-null requirements for activation and rollback.
- Memory migration v8 adds owner-bound experiment/attempt/evaluation persistence, source-learning lineage, candidate identity and digest, a separate evolution evaluation, owner/mechanism-scoped active pointers, and append-only pointer history with compare-and-swap/history checks.

The material remaining gaps are now narrower:

1. **Dataset-rights machine and persistence contracts are now specified; runtime enforcement remains open.** Source/manifest schemas, five event payload schemas, positive fixtures, eleven dataset-rights negative controls, validator cross-binding, five registered events, both event matrices, INT-004, governance v5 and memory v9 now encode source/content/terms digests, owner/model scope, purpose, private-data authorization, separate memory/training permissions and source-to-manifest identity. The new migrations have not yet been executed; admission/revocation handlers and end-to-end runtime enforcement remain open.
2. **Lifecycle event schemas now require state-specific evidence.** `candidate.activated.v1` and `candidate.rolled_back.v1` reference dedicated schema definitions. Activation requires non-null approval, candidate digest, both evaluation references/digests and pointer revision. Rollback requires non-null approval, rollback reference, previous candidate, restored artifact reference/digest and pointer revision. Positive and negative fixtures are included.
3. **Candidate-ID source validation exists; runtime conformance does not.** `scripts/validate_schemas.py` recomputes the canonical UUIDv5 from the positive identity fixture and checks the proposal binding. This is a host-side fixture/validator check, not evidence that runtime command handlers recompute and reject mismatches. Add a negative mismatch fixture and runtime conformance tests after authorization.
4. **Approval digest verification and cross-store saga execution remain runtime work.** The memory DDL can bind pointer history to operation/approval references, but cannot itself prove authenticated owner identity or atomically verify governance-store approval consumption. The coordinator, recovery and reconciliation handlers are not implemented.
5. **The migration is a proposed persistence contract, not an applied user database migration.** Host validation of selected DDL invariants does not prove target-device migration, application-handler, crash/replay or rollback behavior.
6. **All related command/event entries remain design-only and non-dispatchable.** Schema and registry presence do not establish working runtime handlers. The event registry correctly models `learning.update.accepted.v1` as a Learning-supervisor transition consuming the generic owner-approval path; a separate public `learning.accept` command is not required.

These are the current contract and implementation boundaries, not evidence that a working training, activation or rollback runtime exists.

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

**Model-ownership constraint:** The primary model is AURIONS-owned and trained under AURIONS control from a randomly initialized baseline. Pretrained third-party weights and a hosted commercial LLM are not the system's brain. A training run may start from the initial AURIONS random-initialization artifact or a prior AURIONS-owned checkpoint only. The experiment manifest must bind the initialization method, seed, architecture/configuration version, tokenizer version/artifact, initialization/baseline artifact digest and canonical training-configuration digest. Approved cloud/remote compute may execute training when local resources are insufficient; local inference and offline operation must remain independent of that remote training environment. This does not preselect architecture, parameter count, tokenizer algorithm, corpus or compute provider.

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

The identity and persistence amendments listed in the earlier draft are now present in the current machine contracts:

- Learning experiment and worker payloads carry the learning-update, experiment, attempt and job identities plus configuration-digest continuity.
- Candidate-evaluation payloads bind the source learning update, experiment and attempt to exact candidate, baseline, dataset and protocol digests.
- Evolution proposal and action-request payloads carry candidate identity, source-learning lineage, candidate digest, evaluation references and action-specific activation/rollback requirements.
- Memory migration v8 adds durable experiment/attempt/evaluation records, owner-bound source lineage, separate learning/evolution evaluations, owner/mechanism-scoped active pointers, append-only pointer history and compare-and-swap/history triggers.
- Approval request/decision rows remain in `aurion_governance.db`; cross-store operation/saga intent and recovery remain in `aurion_events.db`; active pointers and candidate/artifact projections remain in `aurion_memory.db`. No cross-file foreign key or distributed ACID transaction is implied.

**Remaining contract amendments before implementation:**

- The [MD-16 dataset-source rights and training-authorization contract](DATASET-SOURCE-RIGHTS-AND-TRAINING-AUTHORIZATION-CONTRACT.md) is now represented by source-authorization and manifest schemas, five event payload schemas, positive fixtures, eleven schema-negative controls, registered events, producer/consumer and ingress matrices, and INT-004 for source authorization/content/terms/owner/purpose binding. Governance v5 and memory v9 now define the durable persistence contracts; still required: exact-head host SQLite execution, executable supervisor/worker enforcement and cross-store recovery tests.
- `candidate.activated.v1` and `candidate.rolled_back.v1` now use state-specific payload schemas and positive/negative fixtures. Runtime verification of approval digests, pointer revision and restored artifact identity remains unimplemented.
- Add canonical activation/rollback operation-digest fixtures and negative candidate-ID mismatch coverage. The positive UUIDv5 fixture and validator recomputation already exist; runtime handler conformance remains unimplemented.
- Complete command/event producer-consumer, ingress-trigger and store-local saga matrices against the current registries. Preserve the existing design-only/non-dispatchable status until runtime handlers and acceptance tests exist.
- Keep legacy rows without verified candidate identity non-activatable; never backfill identity by inference.

The current payload schemas and migrations v8/v9 are specification/persistence contracts, not proof of runtime implementation. Historical host run [43939457017](https://github.com/methaneex-oss/AURIONS/actions/runs/43939457017) passed all nine steps on commit `da136f617757ce73265971a921c64e8e1ffdcd9d`, including the prior eighteen-file SQLite execution; it predates dataset-rights migrations v5/v9 and selected v8 positive/negative invariants. The later exact-head host run [43945221654](https://github.com/methaneex-oss/AURIONS/actions/runs/43945221654) also passed all nine steps on `66a1a05659600f5261170d4318fd7b7d494e9524`. Neither result proves that migration v8 has been applied to a user database or that C++/Python handlers, governance verification, cross-store recovery or target-device behavior work.

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

- **Specified:** model ownership/initialization, experiment and worker identity, artifact/evaluation lineage, candidate identity, approval-digest content, activation/rollback saga boundaries and persistence responsibilities.
- **Machine contracts present and host-validated:** experiment/attempt/job/configuration lineage; candidate artifact digest and separate learning/evolution evaluation records; owner/mechanism active pointers and append-only pointer history; positive UUIDv5 candidate-identity fixture with validator recomputation; memory migration v8 and selected DDL invariants.
- **Machine-contract gaps still open:** durable source-rights/dataset-manifest persistence; canonical activation/rollback operation-digest fixtures; negative candidate-ID mismatch coverage; runtime worker/evaluator/governance enforcement.
- **Not implemented:** training worker, experiment execution, dataset-rights enforcement, candidate registry handlers, approval consumer, authenticated digest verification, active-pointer saga coordinator or runtime handlers. Migration v8 is a proposed DDL contract, not an applied user database migration.
- **Not validated:** target-device training/resource feasibility, C++/Python runtime conformance, crash/replay/rollback execution, held-out model improvement, data-revocation impact handling or independent review.
- **Owner gate:** D-04 remains a separate command/query-subset acceptance gate; it is not one of the 16 model decisions. Planning exit and implementation authorization remain separate explicit owner decisions.

No model, worker or generated artifact may approve, activate or roll back its own candidate.
