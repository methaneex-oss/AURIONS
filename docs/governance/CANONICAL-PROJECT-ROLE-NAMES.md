# Canonical Project Role Names

**Status:** Owner-directed, normative naming rule  
**Effective:** 2026-11-18  
**Applies:** Retroactively to interpretation of historical records, to all current records, and to every future project artifact.

## Canonical role names

- **Project Builder** — the role responsible for project research, architecture, planning, implementation within explicit authorization, verification, documentation, self-review and handoff. In this project, the assistant performing that role is always identified as **Project Builder** in documentation.
- **Independent Reviewer** — the separate reviewer responsible for independently examining the exact revision, requirements, architecture, evidence, security properties and findings. The role is identified only as **Independent Reviewer** in project documentation.

## Mandatory naming rules

1. Use the exact role labels **Project Builder** and **Independent Reviewer** in headings, tables, handoffs, review requests, audit records, decision packets, PR descriptions and future documentation.
2. Do not identify the Independent Reviewer by model, vendor, company, product, service or personal name in project documentation. Do not embed provider identity in filenames, role descriptions, review metadata or historical supplements.
3. Do not identify the Project Builder by assistant/model/vendor/product name. The project role label is **Project Builder**.
4. Historical references such as “builder”, “builder review”, “builder self-review” or “author-side builder audit” are interpreted as references to the **Project Builder** role. Historical references to an independent reviewer are interpreted as the **Independent Reviewer** role. This normalization does not rewrite historical evidence, dates, authorship facts, review verdicts or commit history.
5. Preserve the distinction between Project Builder self-review and Independent Reviewer review. They are different responsibilities; the Project Builder must never represent its own review as independent.
6. This naming rule does not grant repository permissions, review authority, implementation authorization, planning-exit approval, PR readiness or merge authority.
7. If a historical artifact is revised, preserve its original evidence and append a clearly dated correction or superseding note where necessary. Do not silently rewrite historical facts merely to make the record appear contemporaneous.

## Review handoff naming

All independent-review work packages must refer to the recipient only as **Independent Reviewer** and the authoring/execution role only as **Project Builder**. Review must be performed against the exact live commit and complete changed-file set. A review of a historical commit does not carry forward to a later revision.

## Enforcement

The Project Builder must use these names consistently in all future project documentation and must correct role-label drift when updating existing artifacts. The Independent Reviewer remains separate from Project Builder self-review. Any conflict between an older role label and this standard is resolved by this standard without changing the underlying historical evidence.
