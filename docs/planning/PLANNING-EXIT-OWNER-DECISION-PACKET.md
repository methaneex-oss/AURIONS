# AURIONS — Planning Exit Owner Decision Packet

- **Status:** Owner product/model decisions recorded; builder schema/contract reconciliation and exact-head host validation current through 2026-11-17; planning exit not approved pending remaining owner gates and independent review.
- **Branch:** `docs/complete-system-architecture`
- **Authority:** `INITIAL-ENGINEERING-SPECIFICATION.md`, the First Usable Release Definition, and the Project Directorship and Team Operating Standard remain authoritative.
- **Purpose:** Consolidate only decisions that the builder cannot make without changing product scope, personal authority, risk tolerance or owner intent.
- **Boundary:** D-01 is accepted; D-02 Option B is selected; D-03 remains staged; D-04's exact §12 command/query classification was owner-accepted on 2026-11-17. This packet does not approve planning exit, implementation, PR merge or a concrete Android action.

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

**Owner decision: OPTION B SELECTED — 2026-11-16.** Proceed with dual runtime and selective domain synchronization. The builder has recorded the default-deny field-path proposal, syncChange v2 and event-specific tombstone/conflict schemas, SY-001…SY-015 specifications, and Memory migration v10 for local export/inbox/acknowledgement/checkpoint/causal-gap/conflict/tombstone/restore persistence. The 21-file three-store DDL chain passed exact-head host CI on 2026-11-17 (run 44174936993, SQLite 3.46.1). Owner/domain acceptance of exact field classifications and conditional paths, authenticated peer enrollment/revocation, runtime enforcement, C++/Python conformance and executed cloud/Android target evidence remain required before sync implementation.

### D-03 — Select the first permitted Android local action

The product proposal requires one narrow, explicitly permitted, reversible local action to validate the real interaction and authority lifecycle. The owner has not selected it.

**Owner disposition: STAGED — 2026-11-16.** Do not select or authorize an action until target-device and Android/Termux validation is complete.

**Builder restriction:** No builder, model, capability descriptor, prior success or test fixture may choose or authorize this action. A proposal is not permission. OS permission and AURIONS governance must independently authorize the exact operation.

### D-04 — Accept the first-release command/query subset

The current registries contain 54 command records (52 mapped and two deferred) and 29 read-only query records. Registry presence does not mean every command/query belongs in the first release or is dispatchable.

**Owner decision: ACCEPTED — 2026-11-17.** The owner accepted the exact §12 registry classification on the builder's recommendation, without changes: 27 P0 public/owner-facing commands; 14 P0 internal/protected commands; 9 conditional P1 commands; 2 internal maintenance/optional commands; 2 deferred commands; and 29 queries comprising 18 P0 read-only, 6 conditional P1 and 5 internal diagnostics. The complete registry-derived identifiers and rationale remain in [First-Release Command/Query Scope and Gap Analysis §12](FIRST-RELEASE-COMMAND-QUERY-SCOPE-AND-GAP-ANALYSIS.md). This is acceptance of scope classification only. It does not authorize dispatch, grant permissions, select an Android action, or waive entry-specific contract, security, implementation and verification gates. Unselected entries remain design-only/non-dispatchable.

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

The builder has completed the D-02 schema/host-invariant increment and reconciled the principal planning, persistence, model-lifecycle, topology, command/query, event and work-package crosswalks. The latest exact-head validation before this packet refresh was [run 44175253865](https://github.com/methaneex-oss/AURIONS/actions/runs/44175253865) on `0cd5da71dec13b1469cbdc2d9aaee6cad1d8d41c`; all nine workflow steps passed, including the 21-file SQLite chain. The final packet/register refresh is documentation-only and receives its own automatic PR CI.

The builder self-review is not an independent semantic/security review. The independent reviewer must review the final exact PR head, including D-04 classification, 94 event producer/consumer contracts, 42 non-command triggers, query semantics/security, persistence ownership and work-package readiness. The planning branch is not yet declared planning-complete. Runtime, peer-trust, target-platform, C++/Python, supply-chain, executed SY and owner-approval gates remain open or explicitly staged.

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

1. **D-02 field-level acceptance:** accept or explicitly stage the exact versioned default-deny field-path classifications and conditional paths in `CLOUD-MOBILE-SELECTIVE-SYNC-CONTRACT.md` and `schemas/sync-field-allowlist.d02.v1.json`. The owner's selected domain direction (durable experience/provenance, representations, memory, evidence-backed knowledge/belief revisions, objectives/derived goals and governed model-version references) is preserved. Raw sensitive observations, transient context, plans/tasks/checkpoints, capabilities, permissions, credentials, approvals, dispatch state and governance authority remain local by default. The exact nested field paths/conditions are still a builder proposal, not silently promoted to owner acceptance.
2. **D-04 — ACCEPTED 2026-11-17:** the exact §12 classification and counts are owner-approved. The six technical consistency/contract checks in §12 remain readiness gates before any affected entry can become dispatch-ready; they are not conditions that reverse or narrow the recorded scope acceptance.
3. **D-03:** retain the already-recorded staged status until a target Android device/runtime is selected and validated; no action or permission is selected here.
4. **External evidence gates:** explicitly stage, with responsible owner and implementation restrictions, target Android/Termux, C++/Python conformance, dependency/SBOM/license/vulnerability review, production key custody and lifecycle, runtime crash/replay/restore/concurrency and executed SY acceptance. Host CI does not substitute for these.
5. **Independent review:** an independent reviewer must review the exact final PR head and resolve findings. The builder cannot self-approve this gate.
6. **Planning exit:** after independent review, record explicit owner approval against the exact PR head, accepted D-04 scope, D-02 field-policy disposition, D-03 staged status, external gates/staging restrictions and a named first implementation milestone. Planning-exit approval is not implementation authorization; implementation and PR merge remain separate decisions.

**Builder-proposed first implementation milestone for owner consideration:** M0 — WP-00 repository/build foundation and WP-01 shared contracts/schema baseline only. Exit evidence: reproducible host C++ build and CTest, pinned toolchain/dependencies, schema/fixture validation, contract ownership/compatibility checks, offline build instructions and supply-chain inventory. Exclusions: runtime command dispatch, Android action, sync runtime, model training, candidate activation and production key custody. This is a proposal, not authorization.
