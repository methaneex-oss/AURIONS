# AURIONS — Model Architecture and Training Owner Decisions

- **Status:** All 16 model-design decisions below are owner-selected and consolidated.
- **Authority:** Owner selections made in the AURIONS planning conversation on 2026-11-16. This record supersedes ambiguity about the model direction; it does not supersede unrelated product, security, governance or implementation gates.
- **Scope:** Primary model, training, data, evaluation, inference and model evolution.
- **Implementation status:** Specification only. This document does not authorize training, worker dispatch, production inference, model activation, deployment, PR merge or planning exit.
- **Related records:** [Initial Engineering Specification](INITIAL-ENGINEERING-SPECIFICATION.md); [PR-19 / PR-20 Model-Candidate Lifecycle Crosswalk](PR-19-PR-20-MODEL-CANDIDATE-LIFECYCLE-CROSSWALK.md); [domain payload schemas](../../schemas/domain-payloads.v1.schema.json); [memory migration v8](../../schemas/persistence/aurion_memory.migration_v8.sql).

## 1. Owner-approved model decisions

The identifiers MD-01 through MD-16 are local identifiers for this model decision register. They are not the repository's existing D-04 command/query-scope decision.

| ID | Owner decision | Consolidated requirement |
|---|---|---|
| MD-01 | General-purpose language foundation model | AURIONS develops its own general-purpose language foundation model. It is not a chatbot wrapper or a thin interface to a third-party hosted model. |
| MD-02 | Decoder-only Transformer | Use a decoder-only causal Transformer as the initial neural architecture. |
| MD-03 | Progressive parameter scaling | Begin with a small trainable baseline. Increase scale only after the data pipeline, training process, evaluation and resource measurements justify it. There is no permanent owner-imposed upper parameter cap. |
| MD-04 | Train and version a multilingual tokenizer | Develop AURIONS' own multilingual tokenizer, evaluate it, and freeze/version it for each model generation. Training and inference for a generation must use the matching tokenizer artifact. |
| MD-05 | Staged training objectives | Start with autoregressive next-token prediction. Introduce additional objectives only when controlled experiments demonstrate a benefit. |
| MD-06 | Staged, expanding data acquisition | Start with a curated multilingual, multi-domain corpus. Expand acquisition continuously under quality, provenance, authorization and evaluation controls. Information acquisition, memory retention and training-corpus approval remain distinct decisions. |
| MD-07 | Hybrid training compute | Use local resources for development, data preparation and appropriately small experiments; use replaceable cloud GPU compute when larger training requires it. Remote training compute is not a prerequisite for local/offline inference. |
| MD-08 | Multi-timescale continual learning | Support distinct timescales: immediate adaptation, persistent memory, controlled model-weight training and governed model evolution. Experience does not automatically modify model weights. |
| MD-09 | Layered evaluation and governed candidate progression | Evaluate training validity, held-out performance, capability, regression, safety/reliability and human-assessed outcomes as applicable. A trained candidate is quarantined until required evidence and owner approval are complete; training never auto-activates a candidate. |
| MD-10 | Hybrid, replaceable inference | Keep a stable model-independent inference interface. Support local separate-process inference and cloud-hosted inference, with useful local/offline operation. The cloud may host an AURIONS-owned model artifact; it does not silently substitute a third-party pretrained or hosted commercial model as AURIONS' primary brain. The C++ core remains authoritative and independent of the inference engine. |
| MD-11 | Staged instruction and behavior learning | Separate foundation training, instruction supervised fine-tuning, preference learning and outcome-based learning. Add later stages only where justified; version and evaluate each stage independently. |
| MD-12 | Progressive context-window scaling | Start by evaluating a 2K–4K context window. Measure quality, memory, latency and runtime cost before exploring 8K–16K or larger contexts. Context is not a substitute for persistent memory. |
| MD-13 | Text-first, extensible multimodal architecture | The first model generation is text-first. Preserve an extension path for image and audio capabilities; do not imply those modalities are already implemented. |
| MD-14 | Tiered multilingual development | Define core, priority-expansion and future language tiers. Nigerian languages must be considered explicitly in language/data evaluation. Language tiers and priorities are versioned configuration and dataset/evaluation data, not hardcoded language-to-behavior rules in application code. Tokenizer coverage alone is not evidence of language capability. |
| MD-15 | Adaptive, evidence-driven curriculum | Start with a broad, balanced foundation curriculum. Adjust data proportions and priorities using measured weaknesses and evaluation results. Curriculum policies and experiment manifests are configurable and versioned; do not hardcode subject-to-capability mappings or fixed behavioral outcomes. |
| MD-16 | Configurable, permission-governed training-data ingestion | Deny unapproved sources by default. Preserve source provenance and classification; check license and permitted use; require explicit authorization for private data; keep memory-retention permission separate from model-training permission; produce versioned, auditable datasets; and make revocation block future use while triggering an impact assessment for derived datasets and model artifacts. |

## 2. Binding interpretation and non-negotiable boundaries

1. **AURIONS owns the primary model.** The initial weights are randomly initialized. A later run may start from a prior AURIONS-owned checkpoint. Third-party pretrained weights and hosted commercial LLMs are not the primary brain under these decisions.
2. **Architecture is not a behavior script.** The Transformer, tokenizer, objectives, training pipeline, evaluation, memory and governance are engineered mechanisms. Learned behavior must arise through training and experience. Do not encode language-specific or subject-specific behavior mappings as fixed application logic.
3. **Memory is not training data.** Retaining an experience, retrieving it, including it in a dataset, and using it to update model weights are separate operations with separate authorization and lifecycle rules.
4. **Training is not activation.** A worker can produce an untrusted candidate artifact. Only the trusted AURIONS control path can validate lineage, run evaluation, obtain owner approval and activate a candidate.
5. **Cloud training and cloud inference are separate.** Remote compute may train an AURIONS model. Cloud inference may serve an AURIONS model artifact. Neither choice makes a third-party hosted model the system's brain or makes cloud availability mandatory for offline local operation.
6. **Context is not memory.** Increasing the context window does not replace persistent, provenance-bearing memory or governed retrieval.
7. **Multilingual and multimodal are evidence claims.** A language or modality is not supported merely because a tokenizer, schema or interface can represent it. Capability must be measured on appropriate data and evaluation sets.
8. **Deletion and revocation require lineage.** Removing a source record is not proof that information has been removed from derived datasets or model weights. Trace affected artifacts and assess quarantine, exclusion, retraining or validated unlearning; never claim exact removal without evidence.

## 3. Reconciliation with existing repository specifications

### Already specified or substantially aligned

- **Primary-model ownership:** The Initial Engineering Specification records the owner direction to build and train AURIONS' primary model from a randomly initialized baseline and not silently adopt pretrained third-party weights. It also distinguishes remote training compute from external model inference. See MP-06 and the model-groundwork discussion around §12.
- **Core/worker boundary:** The specification assigns authoritative runtime, cognition, memory, reasoning, learning/evolution coordination and tool policy to C++; Python owns ML training, dataset preparation, experiments and evaluation. C++ remains authoritative for data authorization, evaluation criteria and release eligibility. Worker processes use typed/versioned messages and cannot mutate live cognitive state or approve production artifacts.
- **Training and candidate lifecycle:** The current payload schema includes experiment requests/completions, worker requests/results, learning-candidate evaluation requests/results, evolution proposals and candidate actions. The schema carries learning-update, experiment, attempt and job identities plus configuration and artifact digests.
- **Persistence crosswalk:** Memory migration v8 adds owner-bound learning experiments, worker attempts, learning evaluations, source-learning lineage, candidate identity, a separate evolution evaluation, owner/mechanism-scoped active pointers and append-only pointer history. Its SQL contract includes lineage, owner-scope, evaluation and pointer-history checks.
- **Governed progression:** The command/event registries describe learning proposal, experiment submission, candidate evaluation, evolution proposal/evaluation, activation, rollback and generic owner approval/revocation. Their entries remain design-only and non-dispatchable.
- **Data handling foundations:** The engineering specification requires authorized dataset references before workers receive them, restricts workers from broadening access, records artifact provenance/classification/retention, tracks model and dataset licensing, and requires deletion impact assessment where source data influenced model weights.
- **Cloud/mobile continuity:** The existing planning record selects dual runtimes with selective synchronization of approved durable domains. Governance authority, credentials, permissions and execution authority are not ordinary synchronized data.

### New owner-selected specificity not yet fully represented as normative model configuration

The repository's general model-groundwork section deliberately left architecture, parameter count, tokenizer algorithm, corpus and compute provider for evaluation. MD-01 through MD-16 now resolve the owner-level direction for those areas. The following details remain engineering parameters to establish through implementation experiments rather than further owner preference questions:

- Transformer depth/width, parameter count for the first baseline, initialization details and scaling schedule.
- Tokenizer algorithm, vocabulary size, normalization rules, language coverage measurements and tokenizer training/evaluation corpus.
- Exact training corpus composition, source acquisition mechanisms, deduplication, quality filters, contamination controls and per-language sampling.
- Optimizer, learning-rate schedule, batch/sequence packing, precision, checkpoint cadence, distributed-training strategy and compute budget.
- Exact objective schedule and measurable entry/exit criteria for instruction, preference and outcome-learning stages.
- Evaluation datasets, held-out/unseen controls, thresholds, regression suites, human-assessment protocol and release criteria.
- Local/cloud inference engine selection, quantization, serving topology, latency/memory budgets and offline behavior.
- Evidence-based timing for image/audio modality work and larger context windows.

These parameters must be versioned in model, tokenizer, dataset, training and evaluation manifests. Do not turn provisional values into permanent architecture rules without measurement.

## 4. MD-16 dataset-rights contracts and remaining enforcement gap

MD-16 now has machine-readable source/manifest schemas, five event-specific payload schemas, positive fixtures, eleven dataset-rights negative controls and validator cross-binding. Five trusted non-command events are registered and reconciled across the producer/consumer matrix, ingress-trigger matrix and integrated scenario INT-004.

**Machine contracts now present:**

- `datasetSourceAuthorization` binds immutable source identity/content digest, acquisition provenance, rights basis, license/terms reference and digest, permitted purposes, explicit training permission, separate memory-retention permission, private-data classification/authorization evidence, owner/model scope, validity, policy version, status and revocation evidence.
- `datasetManifest` binds included source digests to authorization IDs and authorization/terms digests, records exclusions, preprocessing/deduplication/quality/curriculum references, split digests, rights-policy snapshot and derived-artifact references.
- Event payloads cover authorization decided, authorization revoked, manifest sealed, admission blocked and revocation impact assessed. Event registry entries, producer/consumer rows, ingress-trigger rows and INT-004 acceptance references are aligned.
- The 11 dataset-rights negative controls cover source-rights basis, private-data authorization, manifest source membership/emptiness, activation/rollback evidence and invalid authorization/manifest lifecycle event payloads.
- `validate_schemas.py` checks exact source/content/authorization/terms digests, owner/model/purpose scope and cross-event authorization/manifest identity consistency.

**Persistence contracts now present:**

- Governance migration v5 defines immutable authorization versions and append-only revocation evidence, using the existing governance approval-request and local-outbox boundaries.
- Memory migration v9 defines immutable manifest metadata, source membership, exclusions, split digests, seal evidence, lifecycle events, admission decisions and revocation-impact lineage.
- The existing events-store operation/step/recovery tables represent the revocation-impact saga; no additional events-store migration is currently justified.
- SQLite smoke assertions for the new governance and memory records, append-only behavior, complete manifest sealing and admission without a seal are added to the host DDL validator.

**Still missing before nontrivial corpus ingestion or training:**

1. Execute the current 20-file SQLite chain on host SQLite and validate the new governance v5 and memory v9 migrations; prior host evidence covers the previous 18-file chain only.
2. Implement and verify authorization checks at acquisition, dataset construction, artifact registration and immediately before worker dispatch. Workers must receive immutable, non-expandable source scope and cannot authorize themselves.
3. Make final admission fail closed for unknown, denied, expired, revoked, digest-mismatched, out-of-scope or unavailable governance state, independent of event-relay delay.
4. Implement revocation impact assessment over dependent manifests, experiments, checkpoints, candidates, backups and synchronized copies. Preserve unknown training influence explicitly; do not claim automatic unlearning.
5. Add cross-store crash/replay, outbox relay, worker cancellation, restore and target-device SQLite tests.
6. Complete candidate-ID mismatch and canonical activation/rollback operation-digest fixtures, plus runtime authenticated approval verification.

The schema, event and DDL contracts are specification-level artifacts, not proof of runtime enforcement. Unapproved and ambiguous sources remain denied. No nontrivial corpus ingestion or training is authorized until the remaining gates are implemented and verified.


## 5. Model lifecycle contract status

| Layer | Current repository evidence | Honest status |
|---|---|---|
| Model ownership and initialization | Initial Engineering Specification; learningExperimentRequest initialization fields | Specified; no production trainer |
| Experiment/worker identity | learningExperimentRequest, learningExperimentCompleted, workerRequest, workerResult | Schema specified; runtime handlers not implemented |
| Artifact provenance and quarantine | artifactManifest and artifact registry events | Source/manifest and event schemas plus governance v5/memory v9 DDL contracts specified; runtime rights enforcement and exact-head migration validation remain open |
| Learning evaluation | learningCandidateEvaluationRequest and learningCandidateEvaluated; migration v8 evaluation table | Contract and proposed persistence specified; executable evaluator/held-out improvement not established |
| Evolution evaluation | evolutionCandidateActionRequest/lifecycle; migration v8 evolution evaluation table | Contract and proposed persistence specified; runtime evaluator not implemented |
| Owner approval | approvalRequested, approvalDecision, approval/revocation registry entries | Governance contract specified; authenticated runtime verification not demonstrated |
| Activation and rollback | action-specific request conditions; migration v8 active pointer and append-only history | Persistence contract specified; cross-store saga/handlers and crash-recovery execution not demonstrated |
| Local/cloud inference | replaceable inference interface and dual-runtime planning | Architecture direction specified; runtime and target-device measurements outstanding |

All related command/event registry entries remain design-only and non-dispatchable. Schema presence and SQL constraints do not establish working C++ handlers, Python workers, applied migrations, authenticated governance, model training, candidate activation or rollback.

## 6. Required work-package order

1. Execute and validate the MD-16 governance v5/memory v9 persistence contracts, then implement and verify source-rights enforcement before admitting private or otherwise ambiguous data.
2. Consolidate MD-01 through MD-16 into the normative model/training specification and align the Initial Engineering Specification and PR-19/PR-20 crosswalk.
3. Complete schema/fixture/validator alignment for model configuration, tokenizer, dataset authorization, training manifests and staged objectives.
4. Implement the bounded C++ supervisor ↔ Python worker contract and verify matching positive/negative fixtures at both ends.
5. Implement dataset preparation and artifact provenance/authorization enforcement before training runs.
6. Establish the first small randomly initialized Transformer baseline and run reproducible local experiments; use measured evidence to decide when cloud GPU training is necessary.
7. Implement layered held-out evaluation and regression before any candidate can be considered for approval.
8. Implement authenticated owner approval, activation saga, pointer compare-and-swap, append-only history, recovery and separately authorized rollback.
9. Benchmark local inference, cloud-hosted AURIONS inference, context-window scaling and device resource behavior. Keep cloud inference optional for offline operation.
10. Add later training stages, language tiers and modalities only when their versioned data and evaluation evidence support them.

This order is a dependency sequence, not a claim that the work packages are implemented or that the global planning-exit gate has been met.

## 7. Separate outstanding repository gates

- Existing D-04 command/query subset acceptance is separate from MD-01…MD-16. Closing this model questionnaire does not accept or alter that registry proposal.
- The Initial Engineering Specification states that planning exit requires consolidated mission/non-goals, owner decisions, architecture, schemas/migrations, contracts, authorization/privacy, recovery/deletion, tests, dependency/license review, device limits, work-package dependencies and acceptance evidence, followed by owner approval of the consolidated specification and roadmap.
- The current model lifecycle registry is design-only/non-dispatchable. No implementation, training, activation, deployment or PR merge is authorized by this decision record.
- Independent review and executable runtime evidence remain separate from documentation consistency.

## 8. Acceptance of this record

This document records the 16 owner-selected model decisions and their engineering consequences. It does not imply that every decision has already been implemented in code or fully encoded in machine contracts. Any later change to these owner decisions requires an explicit owner decision; implementation details within the approved boundaries are engineering work and should be resolved by evidence, measurement and tests.
