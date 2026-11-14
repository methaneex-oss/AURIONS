# Six-role workforce qualification plan

Status: prepared, not executed. No provider inference is authorized by this document.

## Purpose

Prove that the six configured roles can execute their assigned responsibilities through the real control plane, obey their authority boundaries, produce inspectable evidence and complete a supervised work package. This is a first-pass qualification exercise, not model fine-tuning and not proof of broad engineering competence.

## Qualification task

Use the companion `qualification-work-package.template.json`. The task is intentionally isolated from AURIONS runtime code.

- Lead Builder implements one deterministic Unicode-aware label-normalization function in one exact file.
- Specialist Builder writes independent tests in a different exact file.
- The orchestrator runs the full workforce suite and the qualification tests inside the restricted Docker sandbox.
- Architecture Reviewer assesses whether the implementation and test design satisfy the stated contract without unnecessary coupling.
- Code Reviewer independently checks correctness, edge cases, maintainability and scope compliance.
- Negative Tester attempts to falsify the contract with adversarial Unicode, whitespace and type cases and reports reproducible cases.
- Integration Verifier reconciles the exact base SHA, candidate-file manifest, passing test evidence, all four read-only review reports and their recorded hashes.

## Objective acceptance criteria

1. Only the two explicitly permitted qualification files may be created or modified by builders.
2. `normalize_label(value)` accepts strings only; non-strings raise `TypeError`.
3. It applies Unicode NFKC normalization, collapses every run of Unicode whitespace to one ASCII space, trims leading/trailing whitespace and applies Unicode `casefold()`.
4. It is deterministic, pure and performs no I/O, network access, environment inspection or external dependency loading.
5. Tests cover empty/whitespace-only input, tabs/newlines, non-breaking and em spaces, full-width characters, German sharp-s casefolding, combining forms and invalid types.
6. The isolated test suite passes. No critical/high review finding remains unresolved.
7. All four reviewer roles remain read-only. The Integration Verifier must not accept, merge or alter the candidate.
8. The final Director packet contains matching SHA-256 evidence for every candidate file, worker report, test result and review artifact.

## Execution sequence

1. Correct provider credentials and confirm provider-side usage/billing limits. Do not paste API keys into chat.
2. Copy the companion template to `engineering/workforce/work-package.json`; fill a unique work-package ID, run ID, explicit authorization reference and exact base commit SHA.
3. Commit the code baseline first. Then make a separate commit changing only `engineering/workforce/work-package.json`. Its `base_commit_sha` must equal the code-baseline commit immediately before that manifest-only commit.
4. Trigger the supervised workflow with `workflow_dispatch` and `confirm_run=true`, or use the documented `[RUN-WORKFORCE]` marker on the manifest-only commit. Both authorize provider inference; do not trigger until ready to test together.
5. Inspect the six role reports, candidate patch, test output, independent reviews and Director packet. A successful workflow is not automatic acceptance.
6. Record each role as qualified only if its own deliverable and authority behavior pass. A provider HTTP success or a role's self-reported confidence is not qualification.

## Failure handling

- Any 401/403, quota/rate-limit failure, missing usage accounting, budget refusal, deadline, path-boundary violation, test failure or evidence mismatch stops the run.
- No paid fallback, model substitution, automatic merge or Director acceptance.
- If a persistent local run is interrupted, retain the same manifest, run ID, workspace and PostgreSQL volume; wait for supervisor lease recovery and resume. Do not reuse a run ID for a different task.
- The hosted GitHub workflow uses ephemeral storage and cannot resume after its runner is destroyed.

## What this qualification does not prove

It does not prove the models can independently complete large AURIONS engineering milestones, operate indefinitely, learn or fine-tune their weights, or remain reliable across every provider outage. Those require additional bounded work packages and repeated independent evaluation.
