# AURIONS — Cloud and Offline-Mobile Runtime Topology Decision

- **Status:** Builder decision analysis; unresolved.
- **Decision authority:** Owner. This document does not reinterpret the approved deployment direction.
- **Related owner decision:** Cloud operation and offline-capable mobile operation are concurrent first-release targets. Offline mobile must remain functional without cloud availability. Both contexts use shared versioned contracts and the authoritative cognitive-core implementation.
- **Related existing proposal:** General multi-device synchronization and handoff are currently excluded from first release. The relationship between this proposal and the concurrent deployment decision requires explicit reconciliation.

## 1. The unresolved distinction

Three concepts must not be conflated:

1. **Shared cognitive implementation:** cloud and mobile run the same authoritative C++ cognitive-core implementation and versioned contracts. This prevents two separately designed intelligences.
2. **Shared live cognitive state:** both contexts operate on one continuous set of experiences, beliefs, memories, goals, plans and learning updates.
3. **Cross-runtime synchronization:** state changes made in one runtime become available to the other, including offline queuing, conflict handling, deletion propagation and recovery.

Shared implementation does not automatically provide shared state. Shared state across independently operating cloud and mobile runtimes requires a defined synchronization or shared-authority mechanism.

## 2. Constraints already established

- Cloud and offline-capable mobile are concurrent first-release targets, not sequential phases.
- Mobile must perform its required local workflows without cloud connectivity.
- A local Android action is authorized and enforced at the device boundary; a cloud planner cannot authorize it remotely.
- The cognitive core and contracts must remain common rather than fork into two intelligence implementations.
- SQLite stores are local to a runtime; SQLite database files must not be replicated directly.
- Versioned domain changes, outboxes, idempotency, receipts, tombstones and reconciliation are the approved direction for any synchronization.
- General multi-device synchronization/handoff is currently outside the proposed first-release scope.
- No first Android operation or capability catalogue is selected.

## 3. Architecture options

| Option | Runtime model | State continuity | Consequence |
|---|---|---|---|
| A — Independent full runtimes | Cloud and mobile each run the same core implementation and contracts, with their own authoritative local state. | None in first release. | Satisfies concurrent availability and offline operation without first-release sync, but the user's cloud and mobile cognitive histories diverge. They are two instances of one system, not one continuous state. |
| B — Dual runtime with selective domain synchronization | Both run the same core. Each owns local execution state; a defined set of owner-authorized domain changes is synchronized through versioned changes/outboxes. | Defined continuity for selected domains; offline changes reconcile on reconnect. | Best supports one continuous assistant across cloud and mobile, but requires a minimum synchronization subset in first release. This revises the current proposal to defer all multi-device synchronization. |
| C — Mobile runtime with cloud compute/services | Mobile owns the cognitive state and device authority. Cloud supplies optional stateless or job-scoped compute/inference/training services. | Mobile remains authoritative; cloud does not host a separate full cognitive state. | Strong offline independence and less synchronization complexity, but may not satisfy the owner's intended meaning of a concurrent full cloud operation target. |

## 4. The constraint conflict

If "cloud operation" and "offline mobile operation" both mean full independently running AURIONS runtimes, and both must share one continuous cognitive state, then some form of synchronization is required.

Therefore the following three statements cannot all be true at once:
- Full cloud and mobile runtimes are both first-release targets.
- They share continuous cognitive state.
- No cross-runtime synchronization is included in the first release.

The architecture must explicitly relax or qualify one of these statements. It must not conceal the conflict behind the phrase "shared contracts."

## 5. Builder recommendation

Retain one cognitive-core implementation and common versioned contracts in every option. Keep local Android authorization and execution authority on the device in every option.

Before implementation planning is finalized, select whether first-release cloud/mobile operation requires shared cognitive-state continuity:

- If **yes**, choose Option B and define the smallest justified synchronized domain set, conflict rules, deletion propagation, offline queueing and recovery as first-release scope. General device handoff and broad ecosystem synchronization can remain later work.
- If **no**, choose Option A and explicitly accept separate cloud/mobile cognitive histories for the first release.
- If cloud is intended only as an optional compute/service plane, choose Option C and revise the meaning and acceptance criteria of "cloud operation" accordingly.

This is a product/authority clarification, not a detail that can be safely guessed by the builder.

## 6. Acceptance consequences

Whichever option is selected, first-release acceptance must prove:
- Both required deployment contexts use the same core implementation and compatible contract versions.
- Mobile completes its required local workflow with network access disabled.
- No remote component can bypass local device permissions or AURIONS governance.
- State ownership is unambiguous for every domain.
- Restart, crash, stale data, duplicate delivery and deletion behaviour are specified.
- The system never reports cross-context continuity unless the relevant state has actually been reconciled and verified.

Option B additionally requires executable SY tests for the selected domain set. Option A requires tests proving isolation and explicit UI disclosure of context-local history. Option C requires tests proving remote services cannot become mandatory for local cognition or execution.

## 7. Current disposition

**UNRESOLVED — owner clarification required.**

Until this is resolved, WP-15's cloud/mobile integration topology and state-continuity exit criteria are not implementation-ready. This does not block continued builder work on unrelated planning layers and does not authorize implementation.
