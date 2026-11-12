# Builder Operating Protocol — Execution and Accountability

**Status:** Mandatory  
**Applies to:** All builders, implementation agents, reviewers and testers.  
**Scope:** All current and future development projects.

**Role/workflow authority:** The [Project Directorship and Team Operating Standard](PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md) governs director, builder, independent reviewer and tester authority, workflow gates, handoffs and acceptance. This protocol supplies the detailed execution and verification obligations for builders; it does not replace independent review, independent testing or director acceptance.

## 1. Core objective

Produce completed, working, independently verifiable deliverables. Optimize for measurable progress, not appearances of productivity, code volume, excessive planning, premature completion claims or unnecessary scope expansion.

## 2. Scope discipline

Before implementation, understand the existing project and architecture, identify requirements and constraints, define phase boundaries, and identify dependencies and acceptance criteria.

During implementation, avoid unrelated features and unjustified redesign. Record necessary discoveries and assess their impact before changing scope. Complete the agreed scope before proposing additional work.

## 3. Autonomous execution

Builders carry assigned work through implementation, self-review, testing and correction. Do not ask the project owner to supervise ordinary engineering decisions. Use judgment within assigned authority.

Escalate only material architecture/requirement changes, critical dependency blockers, significant security/data-loss/compatibility risks, or essential ambiguity that cannot safely be resolved. Autonomy is not permission for arbitrary architectural change.

## 4. Mandatory verification

Before declaring work complete:

1. Review implementation against requirements.
2. Examine affected architecture and integration points.
3. Run relevant tests and applicable integration/regression tests.
4. Investigate failures to root cause.
5. Correct defects and rerun affected tests.
6. Record actual results and remaining limitations.

Never claim an unexecuted test passed or claim independent review when none occurred.

## 5. Definition of done

A task is complete only when all agreed requirements are implemented, integration requirements are satisfied, relevant tests actually pass, known defects are resolved or documented, implementation is reviewed, and evidence supports the claim.

Code written is not functionality delivered. A successful build is not a successful system.

## 6. Progress reporting

Report requirements, implementation, verification, actual test results, remaining gaps, evidence and commit references. Distinguish exactly:

- **NOT STARTED**
- **IN PROGRESS**
- **IMPLEMENTED — UNVERIFIED**
- **TESTED — FAILURES**
- **VERIFIED COMPLETE**

Never use optimistic language to conceal unfinished work. Keep specification, implementation, test, builder review and independent review evidence distinct.

## 7. Independent accountability

Builders review their own work before requesting independent review. Reviewers independently examine the implementation rather than accepting builder conclusions. Testers exercise actual behavior rather than inspecting implementation claims. These responsibilities remain distinct.

## 8. Continuous improvement

For recurring mistakes, identify root causes, correct the underlying process, update project rules/documentation, and add enforceable checks where practical. Do not repeatedly address the same failure class through manual intervention.

## 9. Governing principle

High standards must produce reliable engineering processes, not endless supervision. The builder delivers verified results within agreed scope. Completion is demonstrated through evidence, not asserted through confidence.
