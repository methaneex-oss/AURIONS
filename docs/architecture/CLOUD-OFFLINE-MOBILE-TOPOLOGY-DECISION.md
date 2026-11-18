# AURIONS — Cloud and Offline-Mobile Runtime Topology Decision

- **Status:** Owner selected Option B on 2026-11-16. The allowlist and separate classification-policy schema/registry enumerate 106 exact paths and 21 local-only controls; exact parity and export-disabled/default-deny status passed exact-head CI run 44278564389 on 32ceea9. Memory v10 and the full 21-file DDL chain are host-validated. Field policy remains a builder proposal pending owner disposition. Peer trust/key lifecycle, runtime handlers, target validation and executable SY acceptance remain IN PROGRESS.
- **Decision authority:** Builder owns the technical topology proposal. Owner approval is required only if the selected topology changes the product's cross-context continuity or first-release synchronization scope. This document does not reinterpret the approved deployment direction.
- **Related owner decision:** Cloud operation and offline-capable mobile operation are concurrent first-release targets. Offline mobile must remain functional without cloud availability. Both contexts use shared versioned contracts and the authoritative cognitive-core implementation.
- **Scope clarification:** D-02 selects bounded cloud/mobile selective synchronization for first release. General multi-device synchronization and seamless handoff remain excluded; this decision supersedes earlier no-sync wording in the product proposal.

## 1. Runtime and state-continuity distinctions

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
- Bounded selective synchronization between the first-release cloud and offline-mobile runtimes is in scope under D-02; general multi-device synchronization/handoff remains outside first release.
- No first Android operation or capability catalogue is selected.

## 3. Architecture options

| Option | Runtime model | State continuity | Consequence |
|---|---|---|---|
| A — Independent full runtimes | Cloud and mobile each run the same core implementation and contracts, with their own authoritative local state. | None in first release. | Satisfies concurrent availability and offline operation without first-release sync, but the user's cloud and mobile cognitive histories diverge. They are two instances of one system, not one continuous state. |
| B — Dual runtime with selective domain synchronization | Both run the same core. Each owns local execution state; a defined set of approved domain changes is synchronized through versioned changes/outboxes. | Defined continuity for selected domains; offline changes reconcile on reconnect. | Selected by the owner for first release. It replaces the earlier no-sync proposal with bounded cloud/mobile synchronization; general multi-device synchronization and seamless handoff remain deferred. |
| C — Mobile runtime with cloud compute/services | Mobile owns the cognitive state and device authority. Cloud supplies optional stateless or job-scoped compute/inference/training services. | Mobile remains authoritative; cloud does not host a separate full cognitive state. | Strong offline independence and less synchronization complexity, but may not satisfy the owner's intended meaning of a concurrent full cloud operation target. |

## 4. The constraint conflict

If "cloud operation" and "offline mobile operation" both mean full independently running AURIONS runtimes, and both must share one continuous cognitive state, then some form of synchronization is required.

The former three-way conflict is resolved by the owner's D-02 decision: the first release includes bounded selective synchronization between the cloud and offline-mobile runtimes. The remaining design problem is to define exactly which durable domain changes may synchronize, how conflicts/deletions/replay/recovery work, and which state remains local. The phrase "shared contracts" alone is not evidence of state continuity.

## 5. Decision rationale

Retain one cognitive-core implementation and common versioned contracts in every option. Keep local Android authorization and execution authority on the device in every option.

**Pre-decision builder rationale:** Option B — dual runtimes with selective domain synchronization — best preserves one persistent cognitive history across cloud and offline mobile. Without continuity, Option A would create two separate histories: an experience or belief learned in one runtime would be unavailable to the other until manually transferred.

The selected scope is deliberately narrower than general multi-device synchronization. The initial candidate domains are durable experiences/provenance, representations, memory, evidence-backed knowledge/belief revisions, objectives/derived goals and explicitly approved immutable model-version references. Device-local operation state, Android permissions, device credentials, owner approval secrets, dispatch state and governance authority remain local. Raw/sensitive observations remain local by default. Field-level allowlists, retention/deletion propagation, conflict semantics and crash recovery must be specified before implementation.

The owner selected Option B on 2026-11-16. No further owner decision is needed to design this bounded subset. Expanding the domain set, transferring local authority or enabling general device handoff requires a separate owner decision.

Option A remains the historical no-sync alternative; it is not the selected topology. Option C is not selected.

**Owner decision recorded 2026-11-16: Option B selected.** Both runtimes remain independent and offline-capable where required, using the same core and versioned contracts. This authorizes detailed selective-sync design only, not unrestricted replication or implementation.

## 6. Acceptance consequences

Under selected Option B, first-release acceptance must prove:
- Both required deployment contexts use the same core implementation and compatible contract versions.
- Mobile completes its required local workflow with network access disabled.
- No remote component can bypass local device permissions or AURIONS governance.
- State ownership is unambiguous for every domain.
- Restart, crash, stale data, duplicate delivery and deletion behaviour are specified.
- The system never reports cross-context continuity unless the relevant state has actually been reconciled and verified.

Product acceptance PR-15 through PR-18 applies. Option B additionally requires executable SY tests for each synchronized aggregate/domain. These tests must prove allowlist enforcement; local-only data and authority rejection; idempotent outbox delivery and replay; causal revision handling and explicit conflicts; deletion tombstones and retention; offline queuing/reconciliation; and crash/restart recovery.

## 7. Detailed synchronization contract

The bounded field-level allowlist, classification rules, local-only classes, runtime identity, causal revisions, conflicts, tombstone/deletion propagation, retention, offline replay and recovery semantics are specified in the [Cloud/Mobile Selective Synchronization Contract](CLOUD-MOBILE-SELECTIVE-SYNC-CONTRACT.md). This is a builder technical proposal within selected Option B, not an additional owner decision.

## 8. Current disposition

**OWNER DECISION: OPTION B SELECTED — 2026-11-16.** WP-15 must include bounded selective synchronization. The v2 change/conflict/tombstone payload definitions, versioned default-deny field allowlist, separate classification-policy schema/registry, five event-to-SY acceptance bindings and SY-001…SY-015 machine specifications are recorded. Exact-head CI run 44278564389 on 32ceea9 passed the 11-schema corpus, exact parity across 106 paths/21 local-only controls and the 21-file host SQLite chain including Memory v10. This is host/schema evidence only. The allowlist/classification policy remains builder-proposed, default-deny and export-disabled pending owner disposition. Remaining pre-implementation gates are authenticated peer enrollment/revocation and signing/encryption key lifecycle; runtime projection/receiver/receipt/outbox atomicity and recovery handlers; C++/Python canonicalization; and executed cloud plus target Android/Termux fault/replay/restore evidence.

The selected topology is resolved at the option level. WP-15's detailed state-continuity contracts are not yet implementation-ready. This does not authorize implementation.
