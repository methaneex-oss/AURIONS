# AURIONS — Main-Builder Pre-Review Audit

- **Audit date:** 2026-11-12
- **Repository:** `methaneex-oss/AURIONS`
- **Branch:** `docs/complete-system-architecture`
- **Pull request:** #2 — `docs: establish system architecture and first-release product definition`
- **Audit purpose:** Main-builder quality gate before any fresh independent architecture review.
- **Disposition:** **NOT READY for independent review or planning-exit approval.**
- **Implementation authorization:** Not granted by this audit.
- **Authority:** Owner decisions remain authoritative. This audit records engineering findings; it does not make owner decisions or claim empirical evidence.

## 1. Review standard

The builder review checks whether the current planning baseline is internally coherent, traceable, specific enough that an implementation builder is not forced to guess, and honest about evidence boundaries. A document or schema existing is not proof that its contract is complete. A generic payload fixture is not a multi-step scenario test. Static reference checks are not semantic verification. Proposed SQL is not executed SQL. A successful host build is not an Android/Termux build.

The governing invariant remains: **Engineer the mechanisms; let behaviour be acquired through experience.** The architecture must not replace learning, discovery or reasoning with developer-authored behaviour maps, fixed task-to-action recipes, a closed capability catalogue or hardcoded outcome claims.

## 2. Exact revision and scope

The audit began from PR #2 head `b1073b0789b47eb105a2d5e8fc357138ae3056b9`. The PR was open, draft, unmerged, and contained 68 changed files. During this audit, the implementation-contract introduction was corrected to distinguish 86 reusable JSON Schema definitions from 78 named positive payload examples. That correction was committed as `d616036d9b7a6b9276bcb7a20af515ea6b9f828a`. The PR head must be re-fetched after this audit document is committed; no claim is made here about a later head until verified.

The reviewed scope included the planning completion register, implementation-ready contracts, canonical roadmap, owner-decision traceability matrix, Android environment/capability architecture, cognitive mechanism architecture, cognitive/capability contract matrix, schema README, domain-payload schema and fixtures, command/query registry, error registry, persistence DDL files and error-handler contract matrix.

## 3. Reproducible structural checks performed

The following checks were performed against repository content fetched from the named branch:

| Check | Observed result | Interpretation |
|---|---:|---|
| Reusable definitions in `domain-payloads.v1.schema.json` | 86 | Definition inventory, not number of scenario tests. |
| Named entries in `domain-payloads.fixture.json` | 78 | Positive payload-shape examples, not multi-step behavioural scenarios. |
| Command registry records | 45 | 43 schema-mapped commands; two device commands deferred. |
| Query registry records | 21 | All 21 have typed input/result schema references. |
| Commands with non-empty unresolved bindings | 45 | Includes two explicitly deferred device commands; none is dispatchable. |
| Queries with non-empty unresolved bindings | 21 | None is dispatchable. |
| Error registry entries | 35 | All 35 remain `seed`; no production handler is registered. |
| Error-handler fixture coverage | 35 payload fixtures | Payload-shape coverage only; no executable code-specific recovery tests. |
| Proposed DDL execution | Not performed | Static DDL inventories cannot establish SQL validity or migration safety. |
| Android/Termux target validation | Not performed | No device measurement or platform integration result is claimed. |

The command registry inspection found unresolved per-command revision/transition, scope/risk, idempotency/replay, cancellation/deadline, side-effect/reconciliation, error mapping, emitted-event/outbox and conflict/replay/recovery assertions. The query registry inspection found unresolved per-query owner/device scope, classification/redaction, consistency, ordering/cursors, timeout/byte/result bounds, freshness/cache and redaction/consistency fixtures.

Additional reference-integrity checks on those parsed artifacts found:
- No JSON parse failures in the fetched domain schema, domain fixture, command/query registry or error registry.
- Every command request/response/envelope schema reference resolves to a declared domain-schema definition; every command fixture pointer resolves to one of the 78 fixture entries.
- Every query input/response/result/envelope schema reference resolves; every query fixture pointer resolves.
- All 35 error entries have a handler-contract reference and a fixture pointer whose index is within the 35-case fixture array.
- A second static crosswalk pass additionally found:
- The 76 named event types in the event catalogue each appear exactly once in the event-body binding table, including the grouped `operation.*.v1` family; no missing, duplicate or extra event name was found.
- Every event-body payload name in that table resolves to a definition in `domain-payloads.v1.schema.json`.
- The six proposed SQL files contain 57 distinct table declarations (35 memory, 13 events/recovery and 9 governance). All 51 distinct table names referenced by the command/query registry exist in the declared owning store.
- This does not verify event-to-payload semantic suitability, SQL syntax, foreign-key enforcement, indexes, transaction semantics, migrations or runtime behaviour.

These checks validate pointer existence and basic structural consistency only. They do not prove that a binding is semantically correct, that a handler exists, or that any recovery branch executes.

These counts were derived by parsing the fetched JSON documents. They are not a full JSON Schema Draft 2020-12 conformance result.

### Current fixture inventory correction
The current PR file inventory contains 78 named positive domain-payload examples and 28 negative fixture files. The earlier bounded-check evidence covers the original 25 negative fixtures and three later additions; it does not establish that every one of the current 28 has been rerun after all subsequent edits. The register was corrected to preserve that evidence boundary. A fresh full negative-corpus run remains a builder validation task.

## 4. Builder findings — open and blocking

### BR-001 — Command contracts are not dispatch-ready

**Severity:** Critical  
**Evidence:** All 45 command registry entries have unresolved bindings; 43 are mapped to request payload schemas and two are deferred.  
**Required builder closure:**
- Define the authoritative aggregate revision and legal state transitions for each mapped command.
- Bind each command to exact owner/device/resource/data scope and risk semantics.
- Define canonical idempotency scope, digest, duplicate replay and key-collision rejection.
- Define deadline, cancellation safe points and dispatch-race outcomes.
- Define per-command side-effect and reconciliation semantics.
- Bind exact error codes/recovery branches and emitted immutable event bodies.
- Define the local transaction/outbox boundary and per-entry conflict/replay/recovery assertions.
- Keep deferred device pairing/revocation outside first-release dispatch until separately scoped and approved.

**Current disposition:** OPEN. The registry is a design traceability baseline only; no command may be registered for production dispatch.

### BR-002 — Query contracts are not dispatch-ready

**Severity:** Critical  
**Evidence:** All 21 query entries have unresolved bindings.  
**Required builder closure:**
- Define owner/device/resource scope for every query.
- Classify each returned field and define field-level redaction and denial behaviour.
- Specify exact snapshot/eventual/local-committed guarantees for each owning store.
- Define deterministic ordering, stable cursor semantics and mutation behaviour during pagination.
- Set per-query timeout, row/result and byte budgets.
- Define cacheability, freshness and invalidation rules.
- Add positive and negative authorization/redaction/consistency fixtures.

**Current disposition:** OPEN. Read-only intent and schema bounds do not make query handlers safe or complete.

### BR-003 — Error registry remains a seed, not an operational recovery contract

**Severity:** High  
**Evidence:** 35/35 registry entries have status `seed`. Category-level contracts and payload fixtures exist, but code-specific recovery branches and executable tests do not.  
**Required builder closure:** Map every code to its owning handler and legal disposition; define when fresh evidence, state reconciliation, user intervention, quarantine or permanent rejection is required; add executable recovery and no-blind-retry tests; prove that error handling cannot grant authority or convert uncertain effects into success.

**Current disposition:** OPEN. No registry entry is production-dispatchable.

### BR-004 — Architecture scenarios are crosswalked, not executable

**Severity:** High  
**Evidence:** CM-001…CM-021 and AD-001…AD-015 have payload and catalogue crosswalks, but the repository explicitly says multi-step scenario fixtures/assertions are not yet present. CAP/AU/OP/DB/SY/LE scenario coverage also needs concrete execution-level fixtures.  
**Required builder closure:** Specify reproducible multi-step fixture inputs, deterministic fakes, expected transitions, durable-state assertions, negative controls, restart/replay/concurrency/cancellation/fault controls and acceptance thresholds. Tests must prove persistent experience-dependent change against frozen baselines and unseen controls; memory writes or training loss alone are insufficient.

**Current disposition:** OPEN. Crosswalk presence is not behavioural verification.

### BR-005 — Proposed persistence contracts have not been executed

**Severity:** Critical  
**Evidence:** Six proposed SQLite base/migration files and static table/FK inventories exist; no DDL or migration execution has occurred.  
**Required builder closure:** Complete canonical-entity-to-DDL and index/constraint reconciliation; pin the actual SQLite version/compile options available in the selected Termux/Android target; execute each store's migration sequence; run integrity, foreign-key, rollback/restart, crash, outbox/inbox, backup/restore, deletion/tombstone and cross-store fault tests. Do not claim distributed atomicity across separate SQLite files.

**Current disposition:** OPEN and partly dependent on target environment evidence. SQL execution must not be replaced with prose or static parsing.

### BR-006 — Android platform baseline and capability feasibility remain unvalidated

**Severity:** High  
**Evidence:** Android architecture defines general discovery and OS/AURIONS authorization separation, but no exact target device/API baseline or actual platform permission/lifecycle validation is recorded.  
**Required builder closure:** Write a target-device validation protocol that records manufacturer/model, Android release/API level, build fingerprint, Termux version, ABI, available SQLite version/compile options, background execution limits, permission state, storage constraints, resource budgets and reproducible measurements. Reconcile each Android API assumption against the pinned target baseline and official platform documentation. Do not assume root, unrestricted filesystem access, arbitrary background execution or privileges that Android does not grant.

**Current disposition:** OPEN. Device selection/availability and measurements are external evidence gates; the protocol itself is builder work.

### BR-007 — Validator and schema CI are not selected or integrated

**Severity:** High  
**Evidence:** Corvus is a proposal only; Android/Bionic artifacts are not published; full Draft 2020-12 conformance, C++/Python equivalence, transitive SBOM/license review and CI enforcement remain open.  
**Required builder closure:** Complete a reproducible comparison of viable validators, pin source/version/hash and toolchains, prove host C++ and Python result equivalence against the complete positive and negative corpus, determine Android cross-build feasibility, complete transitive license/SBOM/vulnerability review and add CI only after the tool choice is accepted.

**Current disposition:** OPEN. A custom structural subset checker is not a standards-compliant validator.

### BR-008 — Semantic cross-document reconciliation is incomplete

**Severity:** High  
**Evidence:** Identifier-presence audits and table bindings exist, but semantic verification of all 76 event-to-payload mappings, command/query handlers, error mappings, canonical entities, DDL transitions, security invariants and product acceptance paths is explicitly outstanding.  
**Required builder closure:** Reconcile every owner requirement and decision to its normative source, owning component, state transition, schema, command/query/event, persistence record, failure/recovery path, work package and acceptance evidence. Resolve contradictions and record unresolved assumptions with explicit owner/external dependencies. Re-fetch and compare the final PR diff after corrections.

**Current disposition:** OPEN.

### BR-009 — Security and key lifecycle are specified, not validated

**Severity:** High  
**Evidence:** SEC-001…SEC-011, threat scenarios and key hierarchy are specified. Android Keystore, cloud KMS, worker isolation, signing, data egress, backup/recovery and key revocation are not implemented or tested.  
**Required builder closure:** Complete provider-independent interface contracts, trust-boundary/data-flow maps, key lifecycle and recovery decisions that can be made without owner authority, host-fake test procedures, supply-chain pinning/SBOM procedures and explicit platform/cloud evidence gates. Never describe the specification as an implemented control.

**Current disposition:** OPEN; implementation and platform integration evidence remain later gates.

### BR-010 — Work-package and scaffold reconciliation is not complete

**Severity:** High  
**Evidence:** WP-00…WP-16 and the dependency graph exist; PR #1 is a separate scaffold. The roadmap still requires component-to-work-package traceability, measurable exits, target build evidence and post-approval scaffold reconciliation.  
**Required builder closure:** Complete each package's exact inputs/outputs, owned interfaces, acceptance evidence, failure/recovery tests and prerequisites; verify every dependency edge and the first-release path; reconcile PR #1 against the final approved contracts without silently expanding or changing its scope.

**Current disposition:** OPEN.

## 5. Owner decisions and external evidence — not to be fabricated by the builder

These items are deliberately separated from builder-owned work:

- The first Android action/capability has not been selected by the owner. Examples are not selections.
- Cloud/offline-mobile cognitive-history continuity remains an owner decision; the builder's topology recommendation is not an approval.
- Actual target-device measurements, Android OS behaviour and Termux integration require the target device.
- SQLite migration/fault tests require an executable target environment.
- Cloud KMS/provider selection and production key recovery require explicit product/security decisions and integration evidence.
- Independent review of the exact final revision and owner planning-exit/implementation approval are separate authority gates.

The builder must make each choice point explicit and prepare decision-quality alternatives, but must not choose on the owner's behalf.

## 6. No-hardcoding and learning review

The architecture's separation between engineered constraints and acquired behaviour is directionally correct. The builder must still ensure the implementation contracts and tests do not turn the examples into a closed operation catalogue or hardcoded task planner.

A learning claim must retain the full evidence chain: captured experience and provenance; interpretation/evaluation; proposed update with hypothesis/scope/baseline; reproducible evaluation; accepted versioned update with rollback; later use of the updated state; paired measurable difference; unseen generalization; and regression controls. The tests must survive restart where the updated state is intended to be durable.

## 7. Required order of closure

1. Close semantic ownership and transitions for the first-release command/query/event subset without pretending all 43 commands and 21 queries are immediately needed by the first release. Explicitly mark deferred interfaces and prevent their dispatch.
2. Complete code-specific error/recovery mappings and executable contract fixtures.
3. Complete the multi-step scenario/test specifications and trace every first-release requirement to those tests.
4. Reconcile persistence entities, migrations and transaction/recovery semantics; prepare runnable validation scripts and target protocol.
5. Complete validator/toolchain decision and full corpus conformance/CI plan.
6. Complete Android baseline protocol, security/data-flow review and remaining work-package traceability.
7. Run a complete architecture-wide semantic reconciliation; fix all builder findings.
8. Only after builder-owned work is closed, perform a separate final builder review of the exact resulting revision. Any unresolved owner or empirical gate must be explicitly isolated and must not be described as complete.
9. Only then request the main independent reviewer to assess that exact revision. Do not merge PR #2 or authorize implementation by implication.

## 8. Builder verdict

**NOT READY.** The current branch contains substantial planning artifacts, but the evidence above proves that several contracts are still deliberately non-dispatchable, scenario crosswalks are not executable tests, proposed DDL is unexecuted, and platform/security/toolchain validation is outstanding. Calling the planning phase complete now would be inaccurate and would force the next builder to guess.

This audit is a closure ledger, not an independent review and not a claim that the builder work is finished. The next builder action is to resolve the builder-owned findings above and update the canonical completion register with evidence. The main independent reviewer has not been requested by this audit.


## Additional builder finding — open-world architecture correction (2026-11-12)

**Status: OPEN; builder reconciliation in progress.** The previous architecture was still organized around an Android environment/capability architecture even though it prohibited a fixed Android operation catalogue. That is insufficient: it makes one platform the conceptual frame and risks forcing all possible means through device adapters and a capability registry. A new foundational `OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md` now organizes the system around objectives and changing situations, and distinguishes world/entity/evidence/belief/affordance/authority/interaction/outcome. Android is explicitly demoted to one context-specific realization. The Android document, contract matrix, roadmap and completion register have received first-pass scope corrections.

This does **not** close the finding. Remaining dependent documents and machine-readable contracts have not yet been fully reconciled or semantically verified. In particular, the entity/world/context/affordance/interaction model is not yet fully represented in schemas, event contracts, authoritative persistence ownership, command/query contracts, work-package acceptance and executable fixtures. Desktop, iOS, human-mediated, physical and other contexts are examples of possible contexts, not commitments that their integrations are implemented or validated. No implementation authorization or planning-exit claim follows.
\n\n## Follow-on reconciliation — objective/world/means contracts and persistence (2026-11-12)\n\n**Status: IN PROGRESS; not yet semantically or executably verified.** Added `schemas/world-interaction.v1.schema.json` with eight initial context-independent contract definitions: objective, entity, relationship, situation, evidence, affordance hypothesis, interaction proposal and interaction outcome. Added a positive fixture demonstrating a human-mediated/non-device possible means and an unexecuted proposal, plus a negative fixture rejecting an entity with no evidence. Added proposed `schemas/persistence/aurion_memory.migration_v4.sql` for owner-scoped, versioned entities, relationships, situation snapshots, affordance hypotheses, interaction proposals and outcomes. Reconciled the system architecture, cognitive state ownership, first-release definition, schema index and persistence index.\n\n**Evidence boundary:** The schema and fixture files have been created and their JSON syntax will be checked; no official JSON Schema Draft 2020-12 validation is claimed. The SQL migration is proposed only and has not been executed. New definitions are not yet registered to event types, command/query handlers, C++ owners, or complete executable scenarios. Stable identifier format, cross-record referential integrity, cross-store interaction-operation linkage, lifecycle/retention/deletion semantics, and semantic acceptance remain open. The new contracts do not close BR-001…BR-010 or authorize implementation.\n

## Event-contract expansion — open-world domain events (2026-11-12)

The event catalogue in the implementation-ready contract supplement now adds eight context-independent event families: `evidence.recorded.v1`, `objective.created.v1`, `world.entity.observed.v1`, `world.relationship.revised.v1`, `situation.snapshot.created.v1`, `means.affordance.proposed.v1`, `interaction.proposed.v1` and `interaction.outcome.observed.v1`. Their body mappings point to the new `world-interaction.v1.schema.json` definitions or the existing evidence payload. This expands the documented event catalogue from 76 to 84 event types. The textual event-to-payload mapping has been updated; machine-enforced event registry validation, event-specific fixtures, command/query bindings, handler ownership and end-to-end consumer tests are still outstanding. Do not treat the catalogue addition as dispatchable event support.
