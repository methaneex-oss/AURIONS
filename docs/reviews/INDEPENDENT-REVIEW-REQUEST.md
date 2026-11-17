# Independent Architecture Review Request — AURIONS

## Assignment

Conduct a genuinely independent, evidence-based architectural review of AURIONS and its proposed system architecture.

You did not author the architecture. Do not assume it is correct, complete, necessary or aligned with the owner's actual objectives. Your responsibility is to assess it critically and identify what should be retained, changed, rejected or investigated.

## Phase 1 — Understand the repository and system before reviewing the proposal

**Do not begin by reviewing PR #2 in isolation.**

Repository: https://github.com/methaneex-oss/AURIONS

First inspect the repository and establish its current state:

1. Read the repository README and planning index.
2. Read `docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md` in full.
3. Read `docs/planning/REVIEW-AND-IMPORT-NOTES.md`.
4. Read `docs/planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md` in full; inspect existing work packages, engineering plans, build scaffold and relevant documentation.
5. Inspect current branches and open pull requests, particularly PR #1 and PR #2.
6. Distinguish explicitly owner-approved decisions from engineering proposals, unresolved questions and claims supported by implementation/test evidence.

Retrieve the source material yourself. Do not rely on a summary from the architecture author.

### Establish what AURIONS is intended to become

Before judging the architecture, explain in your own words:

- The actual purpose and intended capabilities of AURIONS.
- What distinguishes it from a chatbot or thin LLM wrapper.
- Its principle: **Engineer the mechanisms; let behaviour be acquired through experience.**
- Its cognitive architecture and intended experience-to-learning feedback cycle.
- Its memory, knowledge, belief revision, prediction, reasoning, planning, action and evolution responsibilities.
- Its local-first and multi-device objectives.
- Its bounded autonomy, owner authority, security and governance requirements.
- Its first milestone and the evidence required to demonstrate it.

Do not confuse an aspirational capability with an implemented capability.

## Phase 2 — Inspect the exact proposed revision

Target PR: https://github.com/methaneex-oss/AURIONS/pull/2

Branch: `docs/complete-system-architecture`

Revision to inspect: **the exact current PR #2 head at the time you begin review**. Record the full commit SHA in your report. The author must not send this request until the planning supplement and all cross-document updates are committed and the PR diff has been rechecked.

Review the complete changed-file set returned by GitHub for the exact PR head. At the current planning revision, the expected files include:
- `README.md`
- `docs/architecture/COMPLETE-SYSTEM-ARCHITECTURE.md`
- `docs/architecture/CLOUD-OFFLINE-MOBILE-TOPOLOGY-DECISION.md`
- `docs/architecture/ANDROID-ENVIRONMENT-AND-CAPABILITY-ARCHITECTURE.md`
- `docs/architecture/COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md`
- `docs/architecture/COGNITIVE-MECHANISM-AND-INTERACTION-ARCHITECTURE.md`
- `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md`
- `docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md`
- `docs/planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md`
- `docs/planning/CANONICAL-IMPLEMENTATION-ROADMAP.md`
- `docs/planning/PLANNING-COMPLETION-REGISTER.md`
- `docs/planning/OWNER-DECISION-TRACEABILITY-MATRIX.md`
- `docs/planning/README.md`
- `schemas/README.md`
- `schemas/message-envelope.v1.schema.json`
- `schemas/capability-descriptor-body.v1.schema.json`
- `schemas/domain-payloads.v1.schema.json`
- all positive and negative schema fixtures under `schemas/fixtures/`
- `schemas/first-release-command-query-scope.d04.v1.json` and its Draft 2020-12 schema
- candidate lifecycle negative fixtures covering activation/rollback with non-passing evaluations
- Memory migration v10 and its SQLite host validator/invariant checks
- the D-04 command/query scope reconciliation and PR-19/PR-20 candidate identity/evaluation/digest validator changes
- `docs/reviews/AUTHOR-SIDE-ARCHITECTURE-REVIEW.md`
- `docs/reviews/INDEPENDENT-REVIEW-REQUEST.md`
- `docs/reviews/INDEPENDENT-ARCHITECTURE-REVIEW-RE-REVIEW.md`

The author-side review record, planning-contract supplement, Android capability architecture, cognitive/capability contract matrix, owner-decision traceability matrix, planning completion register and canonical implementation roadmap are included for transparency. Earlier author-side completion statements apply only to the historical revision and are superseded by the current completion register. The schema fixtures have only passed a custom structural subset check, not a full JSON Schema Draft 2020-12 validator or C++/Python conformance test. The cloud/mobile state-continuity topology remains unresolved. None of these documents claims runtime implementation or target-device validation. **Do not treat its findings, verdict or corrections as authoritative.** Complete and preserve your own project-understanding and architecture assessment before using that record as a comparison. Identify where you agree and disagree, with evidence.

If the branch has advanced, record the exact revision actually reviewed and inspect the complete changed-file set. Do not treat the expected file list above as a substitute for checking GitHub's actual changed-file list.

## Phase 3 — Independent technical assessment

Evaluate at least:

1. Architectural coherence: component boundaries, ownership, dependencies and consistency.
2. Cognitive architecture: whether it supports interacting, iterative and interruptible mechanisms rather than disconnected modules or hardcoded behaviour.
3. No-hardcoding invariant: whether behaviour/capabilities are acquired from evidence and experience rather than fixed task-to-action mappings, while explicit safety invariants remain engineered.
4. Learning and adaptation: memory updates, knowledge revision, strategy learning, model training and architecture evolution; measurable evidence.
5. First usable release: scope, utility, feasibility, exclusions and end-to-end acceptance tests.
6. Persistence and memory: storage ownership, transactions, migrations, recovery, retention and deletion.
7. Runtime and technology: C++, Python, SQLite, inference, platform interfaces and process boundaries.
8. Android and target-device feasibility: general environment observation, capability discovery, dynamic capability representation, permission/authority separation, execution verification, experience-driven capability learning, unsupported assumptions and required measurements.
9. Multi-device architecture: identity, pairing, synchronization, conflicts, offline operation, deletion propagation and task handoff.
10. Security and governance: authentication, permissions, approval binding, risk classification, execution-boundary enforcement, data disclosure, encryption and recovery.
11. Autonomy: proactive bounded autonomy without unrestricted authority.
12. Failure handling: crash recovery, uncertain side effects, retries, idempotency, cancellation, resource budgets and reconciliation.
13. Implementation sequencing: whether planning and work-package order is correct and whether implementation choices are premature.
14. Maintainability and complexity: unnecessary abstractions, premature infrastructure, coupling and avoidable costs.
15. Evidence quality: distinguish requirements, tested facts, assumptions, proposals and unverified claims.

## Phase 4 — Challenge the design

Actively search for:
- Contradictions with owner-approved decisions.
- Missing capabilities or responsibilities.
- Unjustified technology choices.
- Incomplete interfaces and contracts.
- Security weaknesses or authority bypasses.
- Learning claims that cannot be demonstrated.
- Requirements that have been silently weakened.
- Decisions likely to cause expensive rework.
- Features unnecessarily postponed or prematurely introduced.
- Reasons to reject rather than revise the architecture.

When disagreeing, explain why and offer a technically defensible alternative.

Do not invent requirements or replace owner decisions with personal preferences. Distinguish defects from optional improvements.

## Phase 5 — Report format

### A. Project understanding
Explain what AURIONS is, what it is intended to build and its governing principles.

### B. Overall verdict
Choose one:
- ACCEPT
- ACCEPT WITH REQUIRED CORRECTIONS
- MAJOR REVISION REQUIRED
- REJECT

Explain the reasoning.

### C. Findings register
For every finding include:
- Unique ID.
- Severity: Critical, High, Medium or Low.
- Exact file/section reference.
- Relevant owner decision or requirement.
- Evidence and technical reasoning.
- Consequence if unresolved.
- Required correction or recommended alternative.
- Whether it blocks architecture acceptance or implementation.

### D. Architecture assessment
Evaluate all 14 areas in Phase 3. Do not omit an area because the architecture does not define it; report the omission and its significance.

### E. First-release assessment
Define what must work end-to-end for the first usable release. Identify measurable acceptance tests and reject superficial demonstrations.

### F. Learning-proof assessment
Specify how the system should demonstrate repeatable improvement against a baseline on held-out tasks, related unseen variations and regression checks. Distinguish genuine learning from stored history, state mutation and successful model training.

### G. Planning and implementation readiness
Identify incomplete planning deliverables, owner decisions required and whether implementation should remain blocked.

### H. Recommended corrections
Provide a prioritized actionable correction list. Separate mandatory corrections from optional improvements.

### I. Final independent conclusion
State whether the architecture is technically sound, aligned with the owner's requirements and sufficiently complete to proceed.

## Independence and reporting rules

- Do not copy or endorse the author's conclusions without independent verification.
- Do not assume a detailed document is necessarily correct.
- Do not equate code volume, module count or technology sophistication with architectural quality.
- Do not invent repository facts, tests or implementation evidence.
- Do not recommend implementation merely to create a sense of progress.
- Do not alter repository files, branches, pull requests or owner decisions during the review. The author-side planning supplement is not a checklist that limits your review: independently identify defects, contradictions, omissions and unnecessary complexity across the whole proposal.
- Preserve your independent report before comparing it with the author's report.
- Disclose any repository material you could not access or verify.

The objective is not to approve the author's work. It is to determine whether the proposed architecture genuinely serves the system the owner wants to build.

## Current independent-review handoff supplement — 2026-11-17

This supplement updates the review brief for the live PR #2 revision. It does not replace the complete-review instructions above or preselect a verdict.

### Owner decisions and authority boundaries to preserve

- D-01 PR-01…PR-20 is owner-accepted.
- D-02 Option B is owner-selected. The field allowlist remains a builder proposal (`builder_proposal_not_owner_accepted`). Its listed default/conditional paths are not enabled export entitlements; no domain export is authorized until the owner accepts exact paths, conditional rules and classification-policy version. This fail-closed gate is explicit in the selective-sync contract.
- D-03 remains staged; no first Android local action is selected.
- D-04's exact command/query classification was owner-accepted. A machine-readable registry now records the accepted 27/14/9/2/2 command and 18/6/5 query groups; CI checks that the groups are disjoint, exhaustive against the live registry and that every entry remains non-dispatchable.
- MD-01…MD-16 remain the owner's selected model direction. Their selection does not authorize training, candidate activation or runtime implementation.

### New machine-contract/fixture changes requiring independent challenge

- The D-04 registry schema and validator exact-set check should be reviewed for completeness, future versioning and resistance to category drift.
- The schema validator's SQLite table inventory now includes Memory migration v10; check it against the ordered DDL smoke validator and the authoritative migration sequence.
- The PR-19/PR-20 synthetic fixtures now form a cross-checked lineage from worker experiment completion through held-out evaluation/report artifact, canonical candidate UUIDv5, evolution proposal and candidate lifecycle to activation/rollback digest vectors. Two negative fixtures require a passing evaluation for activation and rollback.
- The fixtures contain synthetic `passed` states for testing schema/transition acceptance only. They do not represent a real training run, held-out improvement, owner approval, activation or rollback.
- D-02 sync scenarios and persistence invariants remain specifications/host-side DDL checks, not executed cloud/mobile runtime behavior.

### Review baseline and independence

At the start of review, fetch PR #2 from GitHub, record the exact current head SHA and inspect the complete current changed-file set. Prior review record `docs/reviews/INDEPENDENT-ARCHITECTURE-REVIEW-RE-REVIEW.md` reviewed historical commit `238dc0f138a855a6f555c2c5c9bde8483df83fa2`; it is not a review of the live PR revision. Do not rely on builder summaries or this supplement as evidence in place of retrieving and checking the source. Preserve the independent report separately before comparing it with the author-side review.

The reviewer must be different from the PR author and must not be the builder's self-review. A reviewer identity/team has not yet been verified or assigned; the review remains outstanding until an eligible independent reviewer submits a review against the exact live head.
