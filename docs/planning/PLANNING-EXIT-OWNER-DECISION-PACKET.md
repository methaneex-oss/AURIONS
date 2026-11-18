# AURIONS — Planning Exit Owner Decision Packet

- **Status:** Builder-owned schema and cross-document reconciliation are current through source head 3a3dc7d; exact-head host CI passed. The pointer refresh below is documentation-only.
- **Branch:** `docs/complete-system-architecture`
- **Authority:** `INITIAL-ENGINEERING-SPECIFICATION.md`, the First Usable Release Definition, and the Project Directorship and Team Operating Standard remain authoritative.
- **Purpose:** Consolidate only decisions that the builder cannot make without changing product scope, personal authority, risk tolerance or owner intent.
- **Boundary:** D-01 is accepted; D-02 Option B topology and field-classification Option A are owner-accepted (2026-11-18); D-03 remains staged; D-04 exact §12 command/query classification was owner-accepted on 2026-11-17. This packet does not approve planning exit, implementation, PR merge or a concrete Android action.

## 1. Decisions required before planning exit

### D-01 — First Usable Release Definition: ACCEPTED

**Proposal under review:** `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md`, PR-01…PR-20.

The proposal defines AURIONS as a trainable AI system with an evolving cognitive architecture, not a personal-assistant product or chatbot. It requires a bounded, reproducible model-training path alongside experience-dependent adaptation; PR-19 covers training provenance and reproducibility, while PR-20 covers held-out evaluation, candidate quarantine, governed activation and rollback. It does not claim general intelligence or improvement beyond the evaluated distribution. The CLI remains the first interface, with cloud and offline-capable mobile as concurrent first-release targets. Voice, continuous sensing, broad integrations, unrestricted replication and seamless handoff remain separately scoped; D-02 separately selects bounded cloud/mobile selective synchronization for the first release.

**Owner decision: ACCEPTED — 2026-11-16.** The owner accepted PR-01…PR-20 as the first-release product baseline. This is not implementation or validation evidence.

**Consequence:** The accepted PR-01…PR-20 baseline may be used by WP-15 as the product contract, subject to D-02 field-classification/peer-trust/runtime/target gates, the owner-accepted D-04 scope's per-entry technical gates, external evidence gates and implementation authorization.

### D-02 — Cloud/mobile cognitive-history continuity: OPTION B SELECTED

**Options in the topology analysis:**

| Option | First-release meaning | Main consequence |
|---|---|---|
| A — Independent full runtimes | Cloud and mobile run the same core/contracts but maintain separate authoritative histories; no first-release synchronization. | Lowest synchronization scope; experience learned in one context is not automatically available in the other. The product must disclose separate histories. |
| B — Dual runtime with selective domain synchronization | Both run the same core; a narrowly approved set of durable domain changes synchronizes through versioned changes, outboxes and reconciliation. | Supports continuity across contexts but adds first-release synchronization, conflict, deletion and recovery scope. |
| C — Mobile runtime with cloud compute/services | Mobile owns cognitive state and device authority; cloud is an optional compute/service plane, not a second full cognitive runtime. | Strong offline independence but may not satisfy the approved direction for concurrent full cloud operation. |

**Historical pre-decision builder recommendation (retained for provenance):** Option B was recommended to preserve one persistent cognitive history across cloud and offline mobile. This recommendation is superseded by the owner's explicit Option B selection recorded below.

**Non-negotiable boundary in every option:** Device-local permissions, credentials, approval secrets and authority over local effects remain local. Shared contracts never grant cross-context authority.

**Owner decision: OPTION B SELECTED — 2026-11-16.** Proceed with dual runtime and selective domain synchronization. The builder has recorded the default-deny field-path proposal, syncChange v2 and event-specific tombstone/conflict schemas, SY-001…SY-015 specifications, and Memory migration v10 for local export/inbox/acknowledgement/checkpoint/causal-gap/conflict/tombstone/restore persistence. The 21-file three-store DDL chain has passed host SQLite CI. **The exact field allowlist remains `builder_proposal_not_owner_accepted`; neither `default_paths` nor `conditional_paths` is an export entitlement. Until the owner accepts the exact paths/conditions/classification version, all synchronized domains remain export-disabled and receivers must fail closed/quarantine.** Authenticated peer enrollment/revocation, runtime enforcement, C++/Python conformance and executed cloud/Android target evidence remain required before sync implementation.

### D-03 — Select the first permitted Android local action

The product proposal requires one narrow, explicitly permitted, reversible local action to validate the real interaction and authority lifecycle. The owner has not selected it.

**Owner disposition: STAGED — 2026-11-16.** Do not select or authorize an action until target-device and Android/Termux validation is complete.

**Builder restriction:** No builder, model, capability descriptor, prior success or test fixture may choose or authorize this action. A proposal is not permission. OS permission and AURIONS governance must independently authorize the exact operation.

### D-04 — Accept the first-release command/query subset

The current registries contain 54 command records (52 mapped and two deferred) and 29 read-only query records. Registry presence does not mean every command/query belongs in the first release or is dispatchable.

**Owner decision: ACCEPTED — 2026-11-17.** The owner accepted the exact §12 registry classification on the builder's recommendation, without changes: 27 P0 public/owner-facing commands; 14 P0 internal/protected commands; 9 conditional P1 commands; 2 internal maintenance/optional commands; 2 deferred commands; and 29 queries comprising 18 P0 read-only, 6 conditional P1 and 5 internal diagnostics. The complete registry-derived identifiers and rationale remain in [First-Release Command/Query Scope and Gap Analysis §12](FIRST-RELEASE-COMMAND-QUERY-SCOPE-AND-GAP-ANALYSIS.md) and the machine-readable `schemas/first-release-command-query-scope.d04.v1.json` registry. The schema validator checks that the 27/14/9/2/2 command groups and 18/6/5 query groups form disjoint, exhaustive partitions of the live registry and preserve non-dispatchable status. This is acceptance of scope classification only. It does not authorize dispatch, grant permissions, select an Android action, or waive entry-specific contract, security, implementation and verification gates. Unselected entries remain design-only/non-dispatchable.

**Consequence:** Unselected entries remain design-only/non-dispatchable. No registry-wide dispatch enablement is implied.

## 2. Evidence gates to stage or assign

These are not product choices, but they require explicit ownership, environment or acceptance treatment before implementation can proceed safely:

| Gate | Evidence required | What the builder cannot fabricate |
|---|---|---|
| Target platform | Owner-selected Android device; actual Termux/runtime SQLite version and compile options; API/permission/lifecycle/resource measurements | Device identity, measured performance or OS behaviour |
| C++/Python conformance | Equivalent schema/serialization behaviour and pinned compiler/runtime/toolchain evidence | Compatibility without executing the selected toolchains |
| Dependency and supply chain | Selected dependency versions, reproducible build, SBOM, license and vulnerability review | A meaningful SBOM for dependencies not yet selected |
| Security/key custody | Selected production key provider/custodian and verified key lifecycle, IPC, egress and recovery enforcement | Production security assurance from host fakes or interface documents |
| Independent review | Independent review of the exact final planning revision; findings resolved | Independent acceptance by the builder who authored the work |

Each gate must be either passed or explicitly staged by the owner with a bounded scope, responsible owner, required evidence and restriction on what implementation may proceed.

## 3. Builder completion and independent-review handoff

The builder has completed the D-02 local persistence schema increment, added a machine-readable D-04 owner-scope registry and exact registry partition checks, and strengthened PR-19/PR-20 fixture consistency across experiment output, held-out evaluation/report, canonical candidate identity, proposal, lifecycle, activation/rollback and operation digest. Two additional negative fixtures reject candidate activation/rollback with non-passing evaluation status. Historical exact-head run 44182835494 validated the earlier 10-schema revision. The current exact PR #2 head `32ceea9f9f07a5b751120ee1f5b15fb636123c78` passed all nine workflow steps in [run 44278564389](https://github.com/methaneex-oss/AURIONS/actions/runs/44278564389): 11 Draft 2020-12 schemas, 95 positive payloads, 48 schema-negative controls, 106 D-02 classified paths/21 local-only controls, 17 work packages/62 acyclic dependencies and all 21 host SQLite DDL files with Memory v10 invariants.

The builder self-review is not an independent semantic/security review. GitHub reports no submitted PR review or inline review thread for the current head. No eligible reviewer identity/team has been verified; none is fabricated. The independent reviewer must inspect the complete current PR diff, including D-04 classification, all 94 event producer/consumer contracts, 42 non-command triggers, query semantics/security, the new D-02 field-classification policy, persistence ownership and work-package readiness. Planning exit remains blocked pending independent review and owner approval. Runtime, peer-trust, target-platform, C++/Python, supply-chain, executed SY and external evidence gates remain open or staged.

## 4. Planning-exit authorization record

Planning exit is a separate owner decision after the final builder review and independent review. Approval must identify:

1. The exact PR #2 HEAD being accepted.
2. The accepted product definition and command/query scope.
3. The selected cloud/mobile topology and any synchronization scope.
4. The selected first Android action and target environment, or an explicit decision to stage that work.
5. Which external validation gates are passed versus staged, with restrictions.
6. The exact first implementation milestone, allowed work packages, acceptance criteria and exclusions.

No implementation starts until the owner explicitly approves that milestone. PR #2 remains draft/open/unmerged until separately authorized.


## 2026-11-17 exact-head builder evidence update

- PR #2 exact head at this validation point: `235f03552e1ce1d0e26ba1f146b4127ddf1e7fb6`.
- Automatic workflow [44174936993](https://github.com/methaneex-oss/AURIONS/actions/runs/44174936993) passed all nine steps. It executed 21 ordered DDL files across the three stores on host SQLite 3.46.1, with FK/integrity checks and Memory v10 sync-persistence invariants. Schema/fixture, governance, work-package traceability and Android probe shell syntax steps also passed.
- The failed first attempt [44174795063](https://github.com/methaneex-oss/AURIONS/actions/runs/44174795063) exposed a literal escaped-newline defect in one v10 trigger. The SQL was corrected without weakening validation; the subsequent run above passed.
- Builder schema work is complete for the v10 persistence increment. The remaining D-02 gates are owner/domain classification acceptance, authenticated peer/key lifecycle, runtime export/receiver/recovery enforcement, C++/Python conformance, executed SY fault/replay/concurrency/restore tests and cloud/Android/Termux evidence.
- D-03 remains staged by owner. D-04 exact §12 command/query classification was owner-accepted on 2026-11-17; per-entry contract, security, handler and executable verification gates remain open. Independent review of the final exact PR head and explicit owner planning-exit approval remain separate gates. Implementation authorization and PR merge remain ungranted.


## 5. Consolidated owner actions still required — no prior decisions reopened

The following already-recorded decisions are not being re-asked: D-01 accepted PR-01…PR-20; D-02 Option B selected; D-03 first Android action staged; MD-01…MD-16 all selected. They remain binding.

1. **D-02 field-level policy — OWNER-ACCEPTED OPTION A (2026-11-18):** the owner accepted the bounded proposal as written: 106 exact default/conditional/excluded paths across eight domains and 21 cross-domain local-only controls. Default OWNER_PRIVATE metadata retains same-authenticated-owner, enrolled/non-revoked runtime, explicit domain enablement, exact supported allowlist/policy versions, typed-leaf/exclusion, retention, strictest-source-classification, signature/digest and destination-binding checks. Conditional fields require exact per-aggregate authorization naming owner, domain, aggregate, field paths, purpose, destination runtime, policy version and expiry, with current/non-revoked governance verification, source-classification checks, encryption/integrity and no embedded raw sensor/media/source-document content. Excluded and local-only paths remain denied; no PUBLIC classification is inferred; unlisted paths and unmapped numeric sensitivity deny/quarantine. The registry records `owner_accepted_option_a_export_disabled`. **This accepts policy scope only: default action remains deny and `export_enabled=false`; no domain export, peer enrollment or runtime synchronization is authorized.**
2. **D-04 — ACCEPTED 2026-11-17:** the exact §12 classification and counts are owner-approved. The six technical consistency/contract checks in §12 remain readiness gates before any affected entry can become dispatch-ready; they are not conditions that reverse or narrow the recorded scope acceptance.
3. **D-03:** retain the already-recorded staged status until a target Android device/runtime is selected and validated; no action or permission is selected here.
4. **External evidence gates:** explicitly stage, with responsible owner and implementation restrictions, target Android/Termux, C++/Python conformance, dependency/SBOM/license/vulnerability review, production key custody and lifecycle, runtime crash/replay/restore/concurrency and executed SY acceptance. Host CI does not substitute for these.
5. **Independent review:** an independent reviewer must review the exact final PR head and resolve findings. The builder cannot self-approve this gate.
6. **Planning exit:** after independent review, record explicit owner approval against the exact PR head, accepted D-04 scope, D-02 field-policy disposition, D-03 staged status, external gates/staging restrictions and a named first implementation milestone. Planning-exit approval is not implementation authorization; implementation and PR merge remain separate decisions.

**Builder-proposed first implementation milestone for owner consideration:** M0 — WP-00 repository/build foundation and WP-01 shared contracts/schema baseline only. Exit evidence: reproducible host C++ build and CTest, pinned toolchain/dependencies, schema/fixture validation, contract ownership/compatibility checks, offline build instructions and supply-chain inventory. Exclusions: runtime command dispatch, Android action, sync runtime, model training, candidate activation and production key custody. This is a proposal, not authorization.

### D-02 field-policy owner options

- **A — Accept the bounded proposal as written.** Listed default metadata is eligible only after same-owner/runtime authentication, explicit domain enablement, allowlist/version, retention and integrity checks. Conditional fields require exact per-aggregate owner authorization. Excluded and local-only fields remain denied. This best preserves Option B continuity while retaining field-level consent. Builder recommendation: A.
- **B — Metadata-only v1.** Accept only default OWNER_PRIVATE metadata paths and reject every conditional path in v1. Revisit content-bearing paths after target/security evidence. Safer and simpler, but with less continuity.
- **C — Stage all domain export.** Keep Option B topology selected but export-disabled for every domain until security and target evidence is available. This minimizes near-term transfer risk but delays practical cross-runtime continuity.

If no option is selected, C remains the active safe state because the policy is default-deny and export-disabled. These are policy dispositions, not new topology choices. None authorizes runtime sync, peer enrollment, production cryptographic profile/key custody, Android action, training or dispatch.

## 2026-11-18 current-head handoff

- Last CI-validated PR #2 HEAD: 3a3dc7d1d18b19af360c44834b82ce2704fbecc1; 148 changed files; base main; open/draft/unmerged at that validation point.
- Automatic exact-head CI [44280128976](https://github.com/methaneex-oss/AURIONS/actions/runs/44280128976) passed all nine steps on `3a3dc7d1d18b19af360c44834b82ce2704fbecc1`: 11 Draft 2020-12 schemas, 9 paired registry/fixture checks, 95 positive payloads, 48 schema-negative controls, one semantic candidate-ID mismatch, two canonical operation-digest vectors, 35 recovery assertions, 106 D-02 classified field paths plus 21 local-only controls, 17 work packages/62 acyclic dependencies, all 21 ordered SQLite DDL files on host SQLite 3.46.1 with FK/integrity and Memory v10 invariants, and Android probe shell syntax. SQLite evidence is host smoke testing only; Android/Termux, crash/restore, concurrency, cross-store recovery and runtime handlers remain unverified.
- D-02 field-classification Option A was owner-accepted on 2026-11-18 and is recorded in the machine registry. CI enforces exact allowlist/domain/schema/path parity; default-deny and export-disabled remain mandatory.
- D-04 remains owner-accepted exactly as recorded on 2026-11-17. All command/query records remain design-only/non-dispatchable; per-entry readiness gates remain open.
- D-03 remains staged; no Android action or permission is selected. D-01 and MD-01…MD-16 dispositions remain unchanged.
- Independent review remains outstanding. No reviewer identity/team is fabricated and no review submission or inline thread is recorded for the current head.
- Planning exit requires D-02 policy disposition, independent review of the exact final PR diff, findings resolution, owner/staging records for external evidence gates and explicit owner planning-exit approval. Proposed M0 WP-00+WP-01 is not authorization.
- Implementation, runtime dispatch, sync export, training, candidate activation, PR ready-state and merge remain unauthorized.

## 2026-11-18 final documentation-reconciliation revision

- Last CI-validated PR #2 HEAD: 3a3dc7d1d18b19af360c44834b82ce2704fbecc1; 148 changed files; base main; open/draft/unmerged at that validation point.
- Automatic exact-head CI [44280128976](https://github.com/methaneex-oss/AURIONS/actions/runs/44280128976) passed all nine steps on `3a3dc7d1d18b19af360c44834b82ce2704fbecc1`: 11 Draft 2020-12 schemas, 9 paired registry/fixture checks, 95 positive payloads, 48 schema-negative controls, one semantic candidate-ID mismatch, two canonical operation-digest vectors, 35 recovery assertions, 106 D-02 classified field paths plus 21 local-only controls, 17 work packages/62 acyclic dependencies, all 21 ordered SQLite DDL files on host SQLite 3.46.1 with FK/integrity and Memory v10 invariants, and Android probe shell syntax. SQLite evidence is host smoke testing only; Android/Termux, crash/restore, concurrency, cross-store recovery and runtime handlers remain unverified.
- This revision reconciles the topology decision, WP-15 exit row, owner-decision traceability matrix and semantic architecture report with the current classification-policy proposal and D-04 disposition. The D-02 policy remains a builder proposal, default-deny and export-disabled.
- No PR review or inline review thread has been submitted for this exact head. The historic independent re-review is not applicable. Planning exit remains blocked until the owner disposes of the D-02 field policy, an independent reviewer inspects this exact diff and findings are resolved, external evidence gates are staged/passed, and the owner explicitly approves planning exit.

## Final pointer-refresh rule — 2026-11-18

The SHA above is the last fully CI-validated source revision. The pointer refresh committed after it is documentation-only and must receive its own automatic CI. Before independent review, fetch the live PR #2 head and complete changed-file set again; the reviewer must inspect that exact live diff, not a historical baseline.


## D-02 field-classification owner decision — 2026-11-18

- **Owner decision:** Option A — accept the bounded proposal as written.
- **Accepted scope:** policy `d02-classification.v1` against allowlist `d02-cloud-mobile.v1`; 106 exact field paths across eight domains and 21 cross-domain local-only controls. Default metadata retains owner/runtime/domain/version/retention/integrity gates. Conditional paths retain exact per-aggregate authorization, purpose, destination, policy-version and expiry requirements. Excluded/local-only paths remain denied; unlisted paths and unmapped numeric sensitivity deny/quarantine.
- **Machine record:** `schemas/sync-classification-policy.d02.v1.json` records `owner_accepted_option_a_export_disabled`, accepted date 2026-11-18 and decision reference `owner-confirmation-2026-11-18-option-A`. Schema and validator enforce consistent acceptance metadata.
- **Authority boundary:** `default_action=deny`; `export_enabled=false`. This is not export, peer enrollment, runtime sync, Android action, dispatch, implementation, training, activation, planning-exit, PR-ready or merge authorization.
- **Preserved decisions:** D-01 accepted; D-02 topology Option B selected; D-03 staged; D-04 exact §12 scope accepted; MD-01…MD-16 selected. No prior decision reopened or altered.
- **Still open:** exact-live-head independent review, reviewer identity, findings correction, external evidence gate disposition/staging, target/runtime/security evidence and explicit owner planning-exit approval. Planning remains IN PROGRESS/BLOCKED; proposed M0 WP-00+WP-01 is not authorization.
