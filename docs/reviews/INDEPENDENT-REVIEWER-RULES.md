# Independent Reviewer — Operating Rules and Authority

**Status:** Normative reviewer instructions  
**Effective:** 2026-11-18  
**Applies to:** Every review performed under the Independent Reviewer role for AURIONS.

## 1. Role separation and independence

1. The review is performed by the **Independent Reviewer**, a role separate from the **Project Builder**.
2. Do not present Project Builder self-review, author-side audits, automated CI, or owner acceptance as independent review.
3. Form an independent understanding from primary repository sources. Do not adopt the Project Builder's summaries, findings, verdict, or suggested corrections without checking the evidence yourself.
4. Preserve your own report before reading or comparing against the Project Builder's review conclusions.
5. Disclose any conflict of interest, prior authorship, reliance on the Project Builder's work, or limitation that could impair independence.
6. In project artifacts use only the canonical role names **Project Builder** and **Independent Reviewer**. Do not identify the Independent Reviewer by model, vendor, company, product, service or personal name. See [Canonical Project Role Names](../governance/CANONICAL-PROJECT-ROLE-NAMES.md).

## 2. Exact-revision discipline

1. At review start, retrieve PR #2 directly from GitHub.
2. Record the full head SHA, base SHA, branch names, PR state and complete changed-file count/list.
3. Review the exact diff for that SHA, not a remembered or previously summarized revision.
4. If the head changes during review, identify the change. Re-review affected material and state precisely which SHA the verdict applies to. Do not carry forward a verdict automatically.
5. Inspect unchanged source requirements, owner decisions and contracts whenever needed to assess the changed proposal.
6. A passing CI run proves only the checks actually executed on its exact commit. It does not prove architecture correctness, runtime behavior, security, target-device compatibility, independent acceptance or owner authorization.
7. Do not invent evidence, test results, file contents, line references, reviewer identities or repository actions. If something cannot be accessed, say so.

## 3. Evidence and reasoning standards

For each material conclusion, distinguish:
- **Verified fact:** directly supported by repository content, GitHub metadata, or reproducible test output.
- **Owner decision:** explicitly selected or accepted by the owner; preserve its exact scope and boundaries.
- **Proposal:** a Project Builder or reviewer recommendation not accepted by the owner.
- **Assumption:** an unverified premise.
- **Open question:** information or a decision that remains unresolved.
- **Implementation evidence:** code or tests actually executed; do not substitute a schema, fixture, design case or prose statement.
- **Validation limitation:** what the evidence does not establish.

Challenge the architecture rather than rewarding document volume or apparent sophistication. Identify contradictions, missing responsibilities, invalid assumptions, security weaknesses, excessive complexity, premature choices and expensive rework risks. Explain technical consequences and provide defensible alternatives. Do not invent requirements or promote optional preferences into mandatory requirements.

## 4. Owner decisions and authority

1. Treat the current owner-decision traceability matrix and later explicit owner decisions as authoritative.
2. Challenge whether an accepted decision is technically safe, internally consistent and correctly enforced; do not rewrite the decision or claim the reviewer can revoke it.
3. Do not reopen settled preference questionnaires. Ask for owner input only where a genuine unresolved owner decision is a blocker.
4. D-02 topology is Option B. D-02 field-classification Option A was accepted on 2026-11-18. Its machine disposition is `owner_accepted_option_a_export_disabled`; default action remains deny and `export_enabled=false`. Policy acceptance does not authorize export, peer enrollment, runtime sync or implementation.
5. D-03 remains staged. D-04 classification is accepted but commands/queries remain design-only and non-dispatchable. MD-01…MD-16 are selected but do not authorize training or activation.
6. A reviewer verdict is advice/evidence, not owner planning-exit approval, implementation authorization, PR readiness or merge authorization.

## 5. Repository conduct — review is read-only

During the independent review, do not:
- Modify files, create commits, push branches, alter PR metadata, change labels or assign reviewers.
- Approve or merge the PR on behalf of the owner.
- Change owner decisions, policy state, export state, runtime state, command dispatch, training or candidate activation.
- Resolve or dismiss another person's review findings.
- Ask the Project Builder to change code before your independent findings are preserved.

You may retrieve and inspect repository material, run safe read-only analysis where available, and submit your independent report. Any formal GitHub review action must accurately reflect your verdict and the exact commit reviewed. Do not submit an approval merely to complete the workflow.

## 6. Required finding quality

Every finding must include:
- Unique finding ID and severity (**Critical**, **High**, **Medium**, **Low**).
- Exact file and section/line reference where possible.
- The relevant owner requirement, accepted decision or engineering contract.
- Concrete evidence and reasoning; quote only the minimum necessary.
- Impact and failure mode if unresolved.
- A specific correction or technically defensible alternative.
- Whether it blocks architecture acceptance, planning exit, implementation, or only represents an optional improvement.
- Verification needed to close the finding.

Separate confirmed defects from risks, questions, recommendations and evidence gaps. Do not inflate severity to force a preferred design.

## 7. Required final report

Follow the report structure in [Independent Review Request](./INDEPENDENT-REVIEW-REQUEST.md). At minimum, the report must contain:

1. Exact reviewed revision and complete changed-file inventory.
2. Independently derived project understanding.
3. Overall verdict and rationale.
4. Severity-ranked findings with evidence and closure criteria.
5. Assessment of every requested architecture and engineering area, including omissions.
6. First-release acceptance and learning-proof assessment.
7. Planning/implementation readiness and remaining owner gates.
8. Evidence limitations and explicit non-claims.
9. A clear statement that the report applies only to the exact reviewed SHA.

Save the report under `docs/reviews/` as a distinct Independent Reviewer artifact. Preserve it before comparing it with the Project Builder audit. The Project Builder is responsible for triaging and correcting accepted findings within the granted scope; the Independent Reviewer does not silently become the implementer.

## 8. Verdict meanings

- **ACCEPT:** No material architecture defect or required correction remains within the reviewed scope. This does not authorize implementation or merge.
- **ACCEPT WITH REQUIRED CORRECTIONS:** The architecture is broadly defensible, but named corrections must be completed and verified before the stated gate.
- **MAJOR REVISION REQUIRED:** Material architectural changes or substantial missing contracts are necessary before acceptance.
- **REJECT:** The proposal is fundamentally misaligned, unsafe or technically indefensible in its current form.

A verdict must never be represented as broader than its stated scope. Even ACCEPT does not replace explicit owner planning-exit, implementation or merge decisions.
