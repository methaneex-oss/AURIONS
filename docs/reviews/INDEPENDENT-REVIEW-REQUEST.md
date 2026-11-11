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
4. Inspect existing work packages, engineering plans, build scaffold and relevant documentation.
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

Revision to inspect: `991f3d1f341934cd4fd5e947772e87556a1ffb26`

Review all three changed files:
- `docs/architecture/COMPLETE-SYSTEM-ARCHITECTURE.md`
- `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md`
- `docs/reviews/AUTHOR-SIDE-ARCHITECTURE-REVIEW.md`

The author-side review record is included for transparency. **Do not treat its findings, verdict or corrections as authoritative.** Complete and preserve your own project-understanding and architecture assessment before using that record as a comparison. Identify where you agree and disagree, with evidence.

If the branch has advanced, record the exact revision actually reviewed and inspect the complete changed-file set.

## Phase 3 — Independent technical assessment

Evaluate at least:

1. Architectural coherence: component boundaries, ownership, dependencies and consistency.
2. Cognitive architecture: whether it supports interacting mechanisms rather than disconnected modules or hardcoded behaviour.
3. Learning and adaptation: memory updates, knowledge revision, strategy learning, model training and architecture evolution; measurable evidence.
4. First usable release: scope, utility, feasibility, exclusions and end-to-end acceptance tests.
5. Persistence and memory: storage ownership, transactions, migrations, recovery, retention and deletion.
6. Runtime and technology: C++, Python, SQLite, inference, platform interfaces and process boundaries.
7. Android and target-device feasibility: unsupported assumptions and required measurements.
8. Multi-device architecture: identity, pairing, synchronization, conflicts, offline operation, deletion propagation and task handoff.
9. Security and governance: authentication, permissions, approval binding, risk classification, execution-boundary enforcement, data disclosure, encryption and recovery.
10. Autonomy: proactive bounded autonomy without unrestricted authority.
11. Failure handling: crash recovery, uncertain side effects, retries, idempotency, cancellation, resource budgets and reconciliation.
12. Implementation sequencing: whether planning and work-package order is correct and whether implementation choices are premature.
13. Maintainability and complexity: unnecessary abstractions, premature infrastructure, coupling and avoidable costs.
14. Evidence quality: distinguish requirements, tested facts, assumptions, proposals and unverified claims.

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
Define what must work end-to-end for the first usable local release. Identify measurable acceptance tests and reject superficial demonstrations.

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
- Do not alter repository files, branches, pull requests or owner decisions during the review.
- Preserve your independent report before comparing it with the author's report.
- Disclose any repository material you could not access or verify.

The objective is not to approve the author's work. It is to determine whether the proposed architecture genuinely serves the system the owner wants to build.
