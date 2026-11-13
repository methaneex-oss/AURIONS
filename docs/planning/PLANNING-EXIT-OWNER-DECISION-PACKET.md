# AURIONS — Planning Exit Owner Decision Packet

- **Status:** Prepared for owner review; no decisions recorded by this document.
- **Branch:** `docs/complete-system-architecture`
- **Authority:** `INITIAL-ENGINEERING-SPECIFICATION.md`, the First Usable Release Definition, and the Project Directorship and Team Operating Standard remain authoritative.
- **Purpose:** Consolidate only decisions that the builder cannot make without changing product scope, personal authority, risk tolerance or owner intent.
- **Boundary:** This packet does not approve the product proposal, planning exit, implementation, PR merge, first Android action, or any synchronization topology.

## 1. Decisions required before planning exit

### D-01 — Accept or revise the First Usable Release Definition

**Proposal under review:** `docs/product/FIRST-USABLE-RELEASE-DEFINITION.md`, PR-01…PR-18.

The proposal makes the CLI the first user-facing interface and treats cloud and offline-capable mobile as concurrent first-release runtime targets using one cognitive-core implementation and common versioned contracts. Offline mobile must remain useful without cloud availability. It does not claim general intelligence, unrestricted autonomy, mature learning improvement, voice/continuous sensing, broad integrations or automatic cross-runtime synchronization.

**Owner decision required:** Accept the PR-01…PR-18 acceptance baseline as the first-release product definition, request specific revisions, or reject it.

**Consequence:** Until accepted, the acceptance matrix remains a builder proposal and WP-15 cannot treat it as an approved product contract.

### D-02 — Resolve cloud/mobile cognitive-history continuity

**Options in the topology analysis:**

| Option | First-release meaning | Main consequence |
|---|---|---|
| A — Independent full runtimes | Cloud and mobile run the same core/contracts but maintain separate authoritative histories; no first-release synchronization. | Lowest synchronization scope; experience learned in one context is not automatically available in the other. The product must disclose separate histories. |
| B — Dual runtime with selective domain synchronization | Both run the same core; a narrowly approved set of durable domain changes synchronizes through versioned changes, outboxes and reconciliation. | Supports continuity across contexts but adds first-release synchronization, conflict, deletion and recovery scope. |
| C — Mobile runtime with cloud compute/services | Mobile owns cognitive state and device authority; cloud is an optional compute/service plane, not a second full cognitive runtime. | Strong offline independence but may not satisfy the approved direction for concurrent full cloud operation. |

**Builder recommendation:** Option B only if one continuous personal intelligence across cloud and mobile is a first-release requirement. Option A is the clean fallback if the owner prefers no synchronization in the first release. Option C changes the meaning of the cloud target and should be selected only if that is the intended product.

**Non-negotiable boundary in every option:** Device-local permissions, credentials, approval secrets and authority over local effects remain local. Shared contracts never grant cross-context authority.

**Owner decision required:** Select A, B or C. If B, approve the exact first-release synchronization domain set and data classes before implementation planning can freeze.

### D-03 — Select the first permitted Android local action

The product proposal requires one narrow, explicitly permitted, reversible local action to validate the real interaction and authority lifecycle. The owner has not selected it.

**Owner decision required:** Identify the exact action and its target, allowed parameters/effects, reversibility expectation and any excluded data or destinations. The target device and Android/Termux environment must also be identified for empirical validation.

**Builder restriction:** No builder, model, capability descriptor, prior success or test fixture may choose or authorize this action. A proposal is not permission. OS permission and AURIONS governance must independently authorize the exact operation.

### D-04 — Accept the first-release command/query subset

The current registries contain 54 command records (52 mapped and two deferred) and 29 read-only query records. Registry presence does not mean every command/query belongs in the first release or is dispatchable.

**Owner decision required:** Review and accept or revise the proposed first-release subset in `FIRST-RELEASE-COMMAND-QUERY-SCOPE-AND-GAP-ANALYSIS.md`.

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
