# Project Builder → Independent Reviewer: Review Request

**Status:** Active review handoff  
**Issued:** 2026-11-18  
**Repository:** `methaneex-oss/AURIONS`  
**Pull request:** [#2](https://github.com/methaneex-oss/AURIONS/pull/2)  
**Review branch:** `docs/complete-system-architecture` → `main`

## Request

Independent Reviewer: conduct a fresh, genuinely independent review of the complete AURIONS proposal and the exact live PR #2 revision. Establish the project's purpose from the source requirements, inspect the complete current PR diff and the unchanged governing contracts needed to evaluate it, then issue a written verdict and evidence-backed findings.

Do not treat any earlier review, Project Builder audit, CI result, summary, or handoff SHA as approval of the current revision. Fetch PR #2 immediately before starting and record the exact head SHA and complete changed-file count/list in the report. If the head changes during review, stop and rebase the review on the new exact revision.

## Read these repository instructions first

1. **Reviewer conduct and authority rules:** [`docs/reviews/INDEPENDENT-REVIEWER-RULES.md`](./INDEPENDENT-REVIEWER-RULES.md)
2. **Full technical review assignment, scope, required analysis and report format:** [`docs/reviews/INDEPENDENT-REVIEW-REQUEST.md`](./INDEPENDENT-REVIEW-REQUEST.md)
3. **Canonical role naming:** [`docs/governance/CANONICAL-PROJECT-ROLE-NAMES.md`](../governance/CANONICAL-PROJECT-ROLE-NAMES.md)
4. **Active planning status and remaining gates:** [`docs/planning/PLANNING-COMPLETION-REGISTER.md`](../planning/PLANNING-COMPLETION-REGISTER.md)
5. **Owner decisions and their boundaries:** [`docs/planning/OWNER-DECISION-TRACEABILITY-MATRIX.md`](../planning/OWNER-DECISION-TRACEABILITY-MATRIX.md)

The detailed assignment in `INDEPENDENT-REVIEW-REQUEST.md` is the technical scope. The rules file is normative for reviewer independence, conduct, evidence, repository permissions and authority limits. If any older handoff supplement conflicts with the latest owner decision or these current rules, use the latest authoritative owner decision and record the stale text as a consistency finding.

## Project Builder's current handoff facts

At the time this handoff was written, the live PR metadata reported:

- Head SHA: `b6564a8512cfcd718cc0baebd3f4fa5e2f6aed73`
- Changed files: 149
- PR state: open, draft, unmerged
- Base branch: `main`
- Mergeable: reported true by GitHub metadata; this is not approval or readiness.

These values are a starting reference only. **They are not a substitute for fetching the live head at review start.**

## Owner decisions that must not be misrepresented

- D-01 first-release definition: accepted.
- D-02 topology: Option B selected.
- D-02 field-classification policy: Option A accepted by the owner on 2026-11-18. The machine disposition is `owner_accepted_option_a_export_disabled`. This is acceptance of the bounded classification policy only. Default action remains deny and `export_enabled=false`; it does not authorize data export, peer enrollment, runtime synchronization or implementation.
- D-03 first Android action: staged; no first action selected or authorized.
- D-04 exact command/query classification: owner-accepted; entries remain design-only and non-dispatchable pending their own technical gates.
- MD-01…MD-16: owner decisions selected; this does not authorize training, candidate activation or implementation.

Do not reopen settled owner preference questions. Challenge the technical adequacy and consistency of accepted decisions, but do not silently replace them with reviewer preferences.

## Required deliverable

Create a separate, clearly attributed independent report in the repository under `docs/reviews/`, recording:

- Exact PR head SHA, base SHA and complete changed-file inventory reviewed.
- Project understanding derived from primary repository sources.
- One overall verdict: **ACCEPT**, **ACCEPT WITH REQUIRED CORRECTIONS**, **MAJOR REVISION REQUIRED**, or **REJECT**.
- A severity-ranked findings register with exact paths/sections (and line references where possible), evidence, requirement/decision, consequence, correction and whether each finding blocks acceptance or implementation.
- Assessment of every technical area required by the detailed request, including areas that are absent or unproven.
- Evidence limitations, inaccessible files and unverified claims.
- A clear distinction between mandatory corrections and optional recommendations.

Preserve the independent report before comparing it with the Project Builder's audit. Do not edit the PR branch or resolve findings during the review. Submit the report and, if available, a formal GitHub review against the exact reviewed head. A report saved elsewhere or a verbal verdict is not a repository review artifact.

## Current state

The Project Builder has not represented its own audit as an independent review. No independent verdict is implied by this handoff. PR #2 remains draft/open/unmerged and not approved for planning exit, implementation or merge.
