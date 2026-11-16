# AURIONS — Planning Exit Owner Decision Packet

- **Status:** Partially resolved by owner decisions dated 2026-11-16; planning exit not approved.
- **Branch:** `docs/complete-system-architecture`
- **Authority:** `INITIAL-ENGINEERING-SPECIFICATION.md`, the First Usable Release Definition, and the Project Directorship and Team Operating Standard remain authoritative.
- **Purpose:** Consolidate only decisions that the builder cannot make without changing product scope, personal authority, risk tolerance or owner intent.
- **Boundary:** D-01 is accepted and D-02 Option B is selected. D-03 remains staged; D-04 remains pending owner acceptance. This packet does not approve planning exit, implementation, PR merge or a concrete Android action.

## 1. Decisions required before planning exit

### D-01 — First Usable Release Definition: ACCEPTED

**Proposal under review:** `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md`, PR-01…PR-20.

The proposal defines AURIONS as a trainable AI system with an evolving cognitive architecture, not a personal-assistant product or chatbot. It requires a bounded, reproducible model-training path alongside experience-dependent adaptation; PR-19 covers training provenance and reproducibility, while PR-20 covers held-out evaluation, candidate quarantine, governed activation and rollback. It does not claim general intelligence or improvement beyond the evaluated distribution. The CLI remains the first interface, with cloud and offline-capable mobile as concurrent first-release targets. Voice, continuous sensing, broad integrations and automatic cross-runtime synchronization remain separately scoped.

**Owner decision: ACCEPTED — 2026-11-16.** The owner accepted PR-01…PR-20 as the first-release product baseline. This is not implementation or validation evidence.

**Consequence:** The accepted PR-01…PR-20 baseline may be used by WP-15 as the product contract, subject to remaining topology, command/query, evidence and authorization gates.

### D-02 — Cloud/mobile cognitive-history continuity: OPTION B SELECTED

**Options in the topology analysis:**

| Option | First-release meaning | Main consequence |
|---|---|---|
| A — Independent full runtimes | Cloud and mobile run the same core/contracts but maintain separate authoritative histories; no first-release synchronization. | Lowest synchronization scope; experience learned in one context is not automatically available in the other. The product must disclose separate histories. |
| B — Dual runtime with selective domain synchronization | Both run the same core; a narrowly approved set of durable domain changes synchronizes through versioned changes, outboxes and reconciliation. | Supports continuity across contexts but adds first-release synchronization, conflict, deletion and recovery scope. |
| C — Mobile runtime with cloud compute/services | Mobile owns cognitive state and device authority; cloud is an optional compute/service plane, not a second full cognitive runtime. | Strong offline independence but may not satisfy the approved direction for concurrent full cloud operation. |

**Historical pre-decision builder recommendation (retained for provenance):** Option B was recommended to preserve one persistent cognitive history across cloud and offline mobile. This recommendation is superseded by the owner's explicit Option B selection recorded below.

**Non-negotiable boundary in every option:** Device-local permissions, credentials, approval secrets and authority over local effects remain local. Shared contracts never grant cross-context authority.

**Owner decision: OPTION B SELECTED — 2026-11-16.** Proceed with dual runtime and selective domain synchronization. Exact field-level allowlists, classification, conflict, deletion and recovery semantics remain required before sync implementation.

### D-03 — Select the first permitted Android local action

The product proposal requires one narrow, explicitly permitted, reversible local action to validate the real interaction and authority lifecycle. The owner has not selected it.

**Owner disposition: STAGED — 2026-11-16.** Do not select or authorize an action until target-device and Android/Termux validation is complete.

**Builder restriction:** No builder, model, capability descriptor, prior success or test fixture may choose or authorize this action. A proposal is not permission. OS permission and AURIONS governance must independently authorize the exact operation.

### D-04 — Accept the first-release command/query subset

The current registries contain 54 command records (52 mapped and two deferred) and 29 read-only query records. Registry presence does not mean every command/query belongs in the first release or is dispatchable.

**Builder proposal:** The registry-derived subset and exact identifiers are recorded in [First-Release Command/Query Scope and Gap Analysis §12](FIRST-RELEASE-COMMAND-QUERY-SCOPE-AND-GAP-ANALYSIS.md). The PR-19/PR-20 lifecycle crosswalk is recorded in [the candidate lifecycle crosswalk](PR-19-PR-20-MODEL-CANDIDATE-LIFECYCLE-CROSSWALK.md); its payload/DDL/validator additions remain a pre-implementation contract-reconciliation task. **Owner acceptance remains pending.** Unselected entries remain design-only/non-dispatchable.

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

The builder must finish the remaining repository-wide semantic audit, reconcile all artifacts to one exact HEAD, publish the final builder self-review and verify the full CI result. The independent reviewer must then review that exact HEAD, not a previous revision.

The current planning branch is not yet declared planning-complete. The scenario specification increment and its CI run do not close runtime, target-platform, independent-review or owner-approval gates.

## 4. Planning-exit authorization record

Planning exit is a separate owner decision after the final builder review and independent review. Approval must identify:

1. The exact PR #2 HEAD being accepted.
2. The accepted product definition and command/query scope.
3. The selected cloud/mobile topology and any synchronization scope.
4. The selected first Android action and target environment, or an explicit decision to stage that work.
5. Which external validation gates are passed versus staged, with restrictions.
6. The exact first implementation milestone, allowed work packages, acceptance criteria and exclusions.

No implementation starts until the owner explicitly approves that milestone. PR #2 remains draft/open/unmerged until separately authorized.
