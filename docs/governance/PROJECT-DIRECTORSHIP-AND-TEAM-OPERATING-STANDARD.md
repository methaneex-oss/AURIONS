# Project Governance Reform — Directorship and Team Operating Standard

**Status:** Mandatory  
**Effective date:** 12 November 2026  
**Applies to:** All project directors, builders, independent reviewers, testers and supporting agents.  
**Scope:** All current and future projects governed by this team.

This standard governs role authority, workflow gates, handoffs, scope control and acceptance. It complements the [Builder Operating Protocol](BUILDER-OPERATING-PROTOCOL.md), which defines the builder's execution and verification obligations. Existing project vision, approved requirements, architecture and non-negotiable constraints remain in force.

## Part A — The new project directorship

The project director is responsible for direction, priorities, boundaries and final acceptance.

The director must:

1. Establish measurable milestones before implementation.
2. Define what constitutes completion.
3. Protect the original project vision and architecture.
4. Prevent uncontrolled scope expansion.
5. Delegate implementation decisions within clearly defined authority.
6. Evaluate evidence rather than repeatedly requesting assurances.
7. Make timely decisions when evidence is sufficient.
8. Avoid unnecessary intervention in ordinary engineering decisions.

The director must not:

- Constantly supervise routine implementation.
- Change requirements without evaluating the consequences.
- Introduce new work before existing commitments are completed.
- Confuse activity with measurable progress.
- Accept completion claims without evidence.
- Demand unnecessary repeated reviews after sufficient verification.

The director retains authority over project direction and acceptance, not every individual implementation decision.

## Part B — Builder accountability

The builder owns the complete implementation responsibility.

Before implementation, the builder must:

- Read the authoritative project documentation.
- Understand the existing architecture and previous decisions.
- Identify dependencies and constraints.
- Confirm scope and acceptance criteria.
- Identify risks before introducing changes.

During implementation, the builder must:

- Complete the entire assigned scope.
- Preserve architectural consistency.
- Avoid unnecessary redesign.
- Investigate root causes.
- Avoid superficial patches.
- Document significant decisions.
- Keep implementation aligned with project objectives.

Before handoff, the builder must:

- Inspect every relevant change.
- Perform self-review.
- Run relevant tests.
- Fix discovered defects.
- Check integration points.
- Document unresolved issues honestly.
- Prepare a complete handoff with evidence.

A builder must never transfer responsibility for unfinished self-review or obvious defects to the reviewer or tester.

## Part C — Independent reviewer accountability

The reviewer operates independently from the builder.

The reviewer must examine:

1. Requirement completeness.
2. Architectural compliance.
3. Implementation correctness.
4. Integration with existing mechanisms.
5. Unnecessary complexity.
6. Missing functionality.
7. Error handling and failure conditions.
8. Maintainability and regression risks.
9. Deviations from established project decisions.

Every finding must include:

- Severity.
- Exact location or affected component.
- Explanation of the problem.
- Evidence.
- Required correction or justified recommendation.

Review verdicts:

- **APPROVED**
- **APPROVED WITH DOCUMENTED NON-BLOCKING ISSUES**
- **REJECTED — CORRECTIONS REQUIRED**

The reviewer must not approve work merely because the builder claims it is complete. The reviewer must not silently redesign the project or introduce new requirements.

## Part D — Independent tester accountability

The tester verifies actual behaviour independently.

Testing must cover, where applicable:

- Unit tests.
- Integration tests.
- End-to-end behaviour.
- Regression tests.
- Boundary conditions.
- Invalid inputs.
- Failure handling.
- Persistence and state transitions.
- Relevant performance and reliability requirements.

The tester must:

- Verify the actual implementation.
- Use reproducible test procedures.
- Record actual outcomes.
- Preserve failure evidence.
- Distinguish untested behaviour from passing behaviour.
- Rerun failed tests after corrections.
- Identify test coverage gaps.

Test verdicts:

- **PASS**
- **PASS WITH DOCUMENTED NON-BLOCKING LIMITATIONS**
- **FAIL**
- **BLOCKED**

A blocked test must never be represented as a passing test.

## Part E — Workflow and handoff control

The mandatory sequence is:

1. Director authorizes a bounded milestone.
2. Builder implements and self-verifies.
3. Builder submits a complete handoff.
4. Independent reviewer examines the complete scope.
5. Builder resolves review findings.
6. Reviewer confirms corrections.
7. Independent tester executes the test plan.
8. Builder corrects implementation defects.
9. Tester verifies corrections.
10. Director evaluates final evidence and authorizes completion.

Do not start independent review while the builder is still making unrelated implementation changes. Do not start final testing against an unstable implementation. Maintain a clear record of implementation, review, correction and testing outcomes.

## Part F — Scope and change control

Every milestone must have a defined scope.

New discoveries must be classified as:

- Required to complete current scope.
- Critical defect.
- Architectural dependency.
- Future improvement.
- Unrelated suggestion.

Only necessary changes should enter the current milestone. Future improvements must be recorded without automatically expanding current commitments.

Any material change must include its justification, impact and approval.

## Part G — Completion and evidence

A deliverable is complete only when:

- The agreed scope is implemented.
- Builder self-review is complete.
- Independent review has reached an acceptable verdict.
- Required corrections are verified.
- Independent testing has reached an acceptable verdict.
- Remaining limitations are documented.
- Evidence is available.
- Director acceptance is recorded.

A successful build alone is insufficient. A passing isolated test suite alone is insufficient. A large implementation alone is insufficient.

## Part H — Continuous improvement

Recurring failures must result in process improvements.

Teams must:

- Identify recurring root causes.
- Correct underlying engineering practices.
- Improve automated checks where practical.
- Update authoritative documentation.
- Prevent previously resolved defects from recurring.

Do not create unnecessary rules for every isolated incident. Improve the underlying process where evidence justifies it.

## Part I — Governing principle

The project must not depend on constant director intervention to maintain engineering quality.

- Builders own implementation.
- Reviewers own independent technical scrutiny.
- Testers own independent behavioural verification.
- The director owns direction, boundaries and final acceptance.

Every role is accountable for its responsibilities.

**The objective is not merely to build more. It is to build the right things, finish them, verify them and make measurable progress without repeatedly losing ground.**

**Build completely. Review independently. Test rigorously. Correct properly. Deliver verifiable results.**

## Mandatory pre-run governance gate — applies to every execution

**This gate is mandatory for every run, without exception.** Before beginning any work in a run—whether a small edit, investigation, review, test, correction, documentation change, or large implementation—the person or agent performing that role must freshly retrieve and read the current authoritative governance standard and the applicable role-specific protocol. A copy read in an earlier run, remembered instructions, a summary, or a prior chat does not satisfy this gate.

The gate applies independently to:

- **Director:** before each direction-setting, scope, priority, approval or acceptance run.
- **Builder:** before each implementation, investigation, documentation, self-review or correction run.
- **Independent reviewer:** before each review or review-correction verification run.
- **Tester:** before each test-planning, execution, failure-investigation or retest run.
- **Supporting agents:** before each assigned run, including delegated research or validation.

At the start of each run, the role must record the authoritative document revision (commit/blob identifier or equivalent), confirm that it has read the current requirements, and identify the applicable role duties and workflow gate. If the authoritative source cannot be retrieved or its current revision cannot be established, work must stop; do not proceed from memory. A material governance update discovered during a run requires the role to re-read the changed requirements before continuing.

This is an execution precondition, not a reminder or documentation-only recommendation. No role may waive it because a task is small, urgent, routine, previously performed, or believed to be low risk. Automated checks may verify that this rule remains present, but cannot by themselves prove that a human or agent actually complied on a particular run; each run must retain its own evidence.

## Part J — EBT-01: mandatory engineering behaviour and accountable ownership

**Status: MANDATORY. Applies to all builders, independent reviewers, testers and supporting agents.** This part changes required engineering conduct; it is not satisfied by acknowledging, copying or linking this text.

### 1. Independent professional judgment

Every role must exercise the judgment expected of its discipline without waiting for the director to identify obvious next steps. This includes identifying missing requirements, detecting contradictions, investigating root causes, anticipating integration failures, challenging weak assumptions and proposing evidence-backed corrections within the role's authority.

### 2. Role ownership and complete handoffs

- **Builders own implementation quality:** requirement interpretation within approved scope, implementation, integration, self-review, relevant testing, correction and an evidence-complete handoff.
- **Reviewers own independent scrutiny:** they must independently establish scope, inspect evidence and implementation, challenge unsupported conclusions, identify omissions and issue a reasoned verdict. They must not outsource obvious review work to the director.
- **Testers own behavioural verification:** they must derive and execute appropriate tests, investigate failures, preserve reproducible evidence, identify coverage gaps and verify corrections. They must not treat a builder's test report as their own test evidence.
- **Supporting agents own their delegated deliverables:** they must complete and verify the assigned work, disclose limitations and provide traceable evidence before handoff.

No role may transfer unfinished responsibilities downstream merely to obtain another role's attention or approval.

### 3. Scope discipline

Classify discoveries as necessary current-scope work, a critical defect, an architectural dependency, a future improvement or an unrelated suggestion. Complete authorised commitments first. Include essential corrections and dependencies in the current scope; record optional improvements separately. Do not expand scope without the required authority and impact assessment.

### 4. Evidence-based reporting

Reports must distinguish at minimum:
- **Specified** — a requirement or design is documented.
- **Implemented** — the change exists in the target artifact or code.
- **Verified** — the stated verification procedure was actually executed and passed, with identifiable evidence.
- **Independently reviewed** — a separate reviewer examined the exact revision and recorded a verdict.
- **Accepted** — the authorized director explicitly accepted the deliverable.

These states are not interchangeable. Never use confidence, activity, document existence, a successful unrelated check or a promise as evidence for a stronger state. State what was not run, what remains unverified and what is blocked.

### 5. Evidence-backed professional disagreement

Every role must challenge materially incorrect director assumptions, incomplete builder work, weak review conclusions and insufficient test coverage when evidence supports the challenge. Explain the disputed assumption, evidence, impact and a proportionate correction. Respectful disagreement is a required engineering control, not insubordination. Escalate only when the decision exceeds the role's authority or presents material project risk.

### 6. Autonomous correction within authority

When a role discovers a defect or omission within its authority, it must investigate the cause and correct it, then verify the correction and record the evidence. Do not merely report an obvious in-scope defect and wait for the director to prescribe the fix. Do not autonomously change owner-reserved decisions, approved requirements, material architecture, security posture or milestone scope; present evidence and escalate those decisions.

### 7. Behavioural compliance and evaluation

Compliance is demonstrated through completed milestones, quality of handoffs, independently discovered findings, root-cause corrections, behavioural test evidence, regression prevention and delivery quality—not by acknowledging this standard or reporting activity. The director evaluates the team's conduct through those artifacts and outcomes.

**Required transition:** from instruction-following activity to accountable engineering ownership. This part is enforceable alongside the existing role boundaries, workflow stages, scope controls and mandatory fresh-read-before-every-run gate.
