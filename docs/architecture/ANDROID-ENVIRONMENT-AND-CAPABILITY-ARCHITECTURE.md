# AURIONS — Android Platform Interaction Realization

- **Status:** Platform-specific realization; IN PROGRESS and not platform-validated.
- **Applies to:** The Android context only. It does not define AURIONS's general model of the world, objectives, possible means or interaction.
- **Governing architecture:** [Open-World Interaction and Means Architecture](OPEN-WORLD-INTERACTION-AND-MEANS-ARCHITECTURE.md) is foundational and takes precedence. This document specifies only one Android realization beneath it.
- **Authority:** Owner-approved mission and foundational principles in the initial engineering specification.
- **Governing principle:** Engineer the mechanisms; let behaviour and capability use be acquired through experience.
- **Scope warning:** Examples of phone operations are illustrative test scenarios only. They are not a fixed capability catalogue, product boundary or predetermined first action.

## 1. Purpose\n> **Scope and precedence correction:** This document is not the system-wide capability architecture. Its observer, discovery broker, registry and execution gateway are Android-specific implementation mechanisms. They must be interpreted as one possible source and realization of means under the open-world, objective-led architecture. They do not constrain AURIONS to devices, apps, APIs, registered tools or platform adapters. A task may be pursued through other actors, resources, contexts or means, or through no external interaction at all. Android-specific discovery evidence must not be generalized beyond its observed scope.\n

Within the broader open-world interaction architecture, the Android realization must build and maintain an evidence-based understanding of the Android context when that context is relevant to an objective. It must discover what interfaces and capabilities are actually available to its installation and owner, understand their constraints, reason about which discovered means could advance an objective, use them only through authorized boundaries, observe what happened, and improve its future capability knowledge and use through experience.

This is not a conventional phone assistant implemented as a developer-authored menu of operations. Nor is it a promise that Android exposes every system or application capability to third-party software. The operating system, application interfaces, device configuration, user grants and security model define the real boundary. AURIONS must discover and represent that boundary rather than assume or bypass it.

## 2. Architectural invariants

1. **No fixed behaviour catalogue.** Developers must not encode a closed list of desired Android behaviours or fixed task-to-operation mappings as the system's intelligence.
2. **Mechanisms are engineered; capability knowledge is evidence-derived.** Discovery, representation, evaluation, planning, authorization, execution, verification and learning are engineered mechanisms. What a particular device or app exposes, how reliable it is, and how to use it are represented from evidence and experience.
3. **Discoverability is not permission.** Finding an interface does not grant access or authorize its use.
4. **OS authority and AURIONS authority are separate.** Both must permit an operation. AURIONS cannot grant Android permissions to itself, bypass user consent or elevate privileges.
5. **No assumed universal access.** No root, privileged shell, hidden API, exploit, accessibility abuse, arbitrary app-private data access or whole-filesystem access is implied.
6. **Unknown remains unknown.** Missing evidence must not be converted into an assumed capability, permission, precondition or successful outcome.
7. **Capability knowledge is contextual and revisable.** It is tied to device, OS/build, app/provider version, user grant, execution context and evidence time. It can become stale or be invalidated.
8. **Execution is observable and recoverable.** Consequential operations require durable intent, policy decision, operation identity, execution receipt, observed outcome and reconciliation of uncertainty.
9. **Cloud does not own local authority.** Offline mobile must discover and use its permitted local capabilities without cloud connectivity. Remote reasoning cannot bypass the local device's execution gate.
10. **Examples are not scope.** App launch, volume adjustment and file handling are examples only, not the limit or full set of Android capabilities.

## 3. Logical architecture

The Android capability system consists of cooperating mechanisms. These are logical responsibilities; they do not require one process or package per responsibility.

### 3.1 Environment observer

Collects only observations available through supported interfaces and current grants. Its observations may describe:
- Device and OS identity/version/build characteristics.
- Runtime state, resource availability and lifecycle constraints.
- Installed or visible application metadata to the extent Android permits.
- Publicly exposed application interfaces and integration metadata.
- Available platform services and interface versions.
- Current permission/grant state and restrictions.
- User-authorized connectors, selected resources and provider availability.
- Results of prior discovery and execution attempts.

Each observation records source, timestamp, device context, collection method, scope, sensitivity, confidence/limitations and applicable version. Observation is not equivalent to capability or permission.

### 3.2 Discovery broker

Coordinates discovery without embedding a closed operation list. Discovery sources may include:
- Supported Android framework/service introspection.
- Public SDK contracts and version-aware platform metadata.
- Application-published intents, deep links, content/document interfaces or documented integration contracts where visible and supported.
- Explicit user-authorized integrations or connectors.
- Runtime evidence from prior authorized use.
- Additional adapters introduced through a versioned extension interface.

The broker records what was discovered, how it was discovered, the evidence supporting the claim, required conditions and what could not be determined. It must not probe by causing unapproved side effects. Safe metadata inspection and active capability verification are separate activities; active verification requires its own risk assessment and authorization.

Discovery is bounded by Android package visibility, exported-component rules, permissions, app sandboxing, API level, device manufacturer restrictions and the actual interfaces an application publishes. AURIONS must report these limitations instead of inventing access.

### 3.3 Capability registry

Stores discovered capability descriptions as versioned data. It is not a developer-maintained catalogue of desired behaviours.

A capability descriptor must be able to represent, where known:

| Field group | Required meaning |
|---|---|
| Identity | Stable capability ID, descriptor version, provider/device identity |
| Provenance | Discovery source, evidence references, observation time, verification status |
| Interface | Input/output schema, invocation contract, supported API/provider version |
| Preconditions | Required environment state, target availability, user/session context |
| Authority | Android permissions, user grants, AURIONS policy scope and approval requirements |
| Effects | Expected state changes, data access/disclosure, side effects and affected resources |
| Constraints | Availability, OS/app version, rate/size limits, offline status and environmental conditions |
| Risk | Effect-based risk classification, reversibility and potential blast radius |
| Operations | Timeout, cancellation, idempotency, retry and uncertain-outcome semantics |
| Verification | Observable postconditions, evidence source and verification confidence |
| Resources | Expected CPU, memory, storage, network, battery and execution time |
| Lifecycle | Discovered, unverified, verified, unavailable, permission-required, revoked, stale or retired |

Unknown fields remain explicitly unknown. Descriptor schemas are extensible and versioned; adding a new capability does not require changing a fixed enum or editing a task-to-action table. A schema change is not permission to execute.

### 3.4 Capability knowledge and relationship model

The registry describes interfaces. A separate evidence-backed knowledge layer represents what AURIONS has learned about using them:
- Observed preconditions and environmental dependencies.
- Which inputs were accepted and under what versions/context.
- Observed effects versus expected effects.
- Reliability, latency, resource use and failure patterns.
- Safe composition relationships between capabilities.
- Known limitations and counter-evidence.
- Confidence, uncertainty, provenance and recency.

A single success does not establish universal reliability. A single failure does not prove the capability is permanently unusable. Evidence must be interpreted in context and may revise prior knowledge without erasing history.

### 3.5 Reasoning and planning interface

The cognitive core receives a goal, relevant context and the currently discoverable capability knowledge. It may:
1. Determine what outcome is being sought.
2. Identify missing information or capability knowledge.
3. Generate candidate means from available evidence rather than fixed task mappings.
4. Evaluate preconditions, likely effects, risk, permissions, reversibility, uncertainty and resource budgets.
5. Compare alternatives, including asking the owner, waiting, using another capability or explaining that no safe supported route is known.
6. Produce a versioned plan whose steps reference capability descriptors and exact parameter schemas.
7. Reassess when observations, permissions, environment state or execution outcomes change.

The planner must not treat a capability description as authorization. It must not invent an interface because a task appears achievable in natural language. Unknown or unsupported steps remain unresolved.

### 3.6 Local authorization and execution gateway

All device actions pass through a local gateway independent of model reasoning.

Before dispatch, it revalidates:
- Capability identity/version and provider availability.
- Exact operation, parameters, target and expected effects.
- Preconditions and current environment state.
- Current Android permission/grant state.
- AURIONS policy, risk class, scope and any required owner approval.
- Deadline, resource budget, cancellation and idempotency constraints.
- Whether the approval digest still matches the exact operation.

The gateway creates durable operation intent before dispatch, records authorization, invokes only the supported platform adapter, captures the execution receipt, verifies observable postconditions and records the result. If the effect may have occurred but confirmation is missing, the operation becomes uncertain and is reconciled before retry. No model-authored shell string, hidden API or unregistered direct call may bypass this gateway.

### 3.7 Outcome evaluation and learning

After execution, AURIONS compares:
- The predicted result and its confidence.
- The actual execution receipt.
- Independently observed postconditions.
- Environmental changes and possible confounding factors.
- Resource cost, latency, failures and safety outcomes.

It can update capability knowledge, precondition estimates, reliability estimates, strategy selection and future planning. The update must preserve provenance and distinguish:
- A capability was discovered.
- A permission was granted or denied.
- An operation was attempted.
- An operation completed.
- The expected effect was verified.
- A reusable competence hypothesis was learned.
- A strategy change passed evaluation.

These are different claims. A completed action is not automatically proof of learning. General improvement claims require controlled comparisons and held-out evaluation under the project's learning-evidence standard. The system may not learn to bypass permissions, lower governance requirements or authorize itself.

### 3.8 Capability lifecycle and rediscovery

The environment changes. Installed applications update/uninstall, permissions change, OS versions change, providers become unavailable and user grants are revoked.

AURIONS therefore needs:
- Discovery epochs and freshness/expiry rules.
- Version and environment fingerprints.
- Invalidation when relevant state changes.
- Revalidation before execution, not merely at planning time.
- Revocation propagation to queued plans and active operations.
- Safe handling of unavailable or changed interfaces.
- Migration of capability knowledge only when evidence supports compatibility.
- Audit history for discovery, verification, revocation and descriptor changes.

Cached capability metadata is advisory until revalidated against the current device and policy state.

## 4. Permission, trust and privacy boundaries

There are at least three distinct questions:
1. **Does an interface exist?** Discovery evidence answers this.
2. **Can this installation invoke it now?** Android platform permissions, app contracts and runtime conditions answer this.
3. **May AURIONS use it for this exact purpose and effect?** AURIONS governance and owner authority answer this.

All three must be satisfied. AURIONS must distinguish permission to observe from permission to modify, permission to access a resource from permission to disclose it, and permission for one exact operation from standing authority.

Sensitive observations are classified before persistence, indexing, prompt construction, synchronization or external transfer. Local discovery must not silently export installed-app inventories, files, notifications, sensor data or other private context. Remote services receive only minimum purpose-bound data under the existing disclosure policy.

Accessibility services, notification access, VPN, device-admin, usage access, package visibility and other powerful Android facilities are not assumed. If any is considered, it requires a separate necessity analysis, platform-policy review, explicit owner consent, least-privilege scope, disclosure and revocation path. None may be used as a general bypass for application or OS security.

## 5. Offline and cloud operation

The Android device agent and local authorization gateway remain authoritative for local operations. Offline operation must support:
- Local environment observation and capability discovery from locally available interfaces.
- Local capability registry and evidence store.
- Local reasoning/inference where configured and feasible.
- Local planning, authorization, execution and outcome capture.
- Durable queue/checkpoint/reconciliation when connectivity is absent.

Cloud services may provide optional compute, model inference or coordination only through shared versioned contracts and explicit data-egress authorization. A cloud plan is a proposal; the device revalidates capability availability, exact parameters, current permissions and policy locally before execution. Loss of cloud connectivity cannot silently disable a required offline workflow or leave an operation in an untracked state.

## 6. Extension and evolution model

New discovery adapters and capability providers can be added without rewriting the cognitive core. They must implement versioned contracts and declare trust, permissions, schemas, effects, budgets and verification semantics.

Extension installation does not automatically grant access. New providers are quarantined or unavailable until their provenance, compatibility, security and declared effects are evaluated. A provider cannot register itself as trusted, change governance policy or approve its own operations. Capability knowledge learned from one provider/device/version must not be generalized to another without evidence.

### 6.1 Provider identity, trust and lifecycle

A discovery provider is a source or adapter that reports environment observations or capability descriptors. A provider's ability to report a descriptor is not evidence that the descriptor is truthful, safe, compatible or authorized. Provider trust and capability confidence are separate records.

Every provider record must retain, where applicable:
- Stable provider identity and provider type as extensible data, not a closed list of desired Android operations.
- Origin and acquisition path (platform-bundled adapter, AURIONS-bundled adapter, owner-authorized integration or externally supplied extension).
- Publisher/signing identity and artifact digest where executable code or signed metadata is involved.
- Declared interface and schema versions, supported platform ranges and dependency requirements.
- Requested Android permissions, AURIONS data scopes, declared effects and resource limits.
- Provenance of security review, compatibility checks, owner approval and revocation.
- Last successful health/compatibility check, current lifecycle state and reasons for any restriction.

Provider lifecycle is a governed state machine, not a learned behaviour:
1. **observed** — provider metadata is visible; no trust is implied.
2. **quarantined** — metadata and artifacts may be inspected in isolation; invocation is disabled.
3. **validated** — integrity, schema, compatibility and declared-scope checks passed for a specific version and environment; this is not owner authorization.
4. **enabled** — provider use is permitted within an explicit governance grant and current OS permissions.
5. **degraded** — provider is retained but temporarily unavailable or unreliable; new operations are blocked or restricted according to the failure class.
6. **revoked** — grants or trust have been withdrawn; queued work is invalidated and active work is cancelled/reconciled safely.
7. **retired** — provider is no longer offered; historical evidence remains available for audit and learning.

Transitions require a recorded cause, actor, evidence, timestamp and applicable provider/version identity. A provider cannot validate, enable, approve or restore itself. Re-enabling after revocation requires a fresh validation and the required owner/governance action. A provider version change creates a new validation subject; trust is not inherited merely because the name is unchanged.

### 6.2 Provider and discovery failure semantics

Errors must distinguish at least:
- **not visible** — platform visibility rules prevent observation;
- **not supported** — the current OS/provider contract does not expose the interface;
- **permission required / permission denied** — Android or provider permission is absent or refused;
- **owner authorization required / denied** — AURIONS governance has not granted the exact use;
- **stale descriptor** — provider, OS, app or permission context changed after discovery;
- **incompatible schema/version** — request or response contract cannot be safely interpreted;
- **provider unavailable** — provider is absent, stopped, offline or unhealthy;
- **rate/resource limited** — a declared budget, quota, deadline or device resource limit prevents work;
- **cancelled** — cancellation was observed before dispatch or at a documented safe point;
- **outcome uncertain** — dispatch may have caused an effect but no authoritative receipt/postcondition is available;
- **integrity/trust failure** — signature, digest, provenance or isolation validation failed;
- **internal adapter failure** — unexpected adapter fault, reported without leaking secrets.

Every error carries a stable machine code, retryability classification, side-effect state (`not_dispatched`, `dispatched`, `unknown` or `not_applicable`), correlation/operation identity where applicable, provider and descriptor versions, a safe diagnostic reference (or explicit null when no safe artifact exists) and user-action requirement. `dispatched` means invocation may have occurred; it does not prove the effect. Confirmed effects are recorded through provider receipts and independent outcome evidence. Human-readable messages are not used for control flow.

Retry is not inferred from a generic failure. It is allowed only when the error classification and side-effect state prove that retry is safe or when the operation's idempotency/reconciliation contract explicitly permits it. A `dispatched` or `unknown` side-effect state enters durable uncertainty handling and requires reconciliation before retry; neither may trigger a blind retry. Permission denial, owner denial, trust failure and unsupported-interface errors are not automatically retried.

### 6.3 Capability knowledge and provider lifecycle interaction

Provider lifecycle events invalidate or constrain dependent capability descriptors and plans:
- Provider version change invalidates descriptors whose compatibility has not been re-established.
- Provider degradation lowers availability confidence but does not rewrite historical success/failure evidence.
- Permission revocation invalidates the affected authority claims immediately, regardless of learned reliability.
- Provider revocation blocks new dispatch, invalidates queued plans and routes active operations through cancellation/reconciliation.
- Provider retirement prevents new use while preserving provenance and outcome history.
- Re-discovery creates new evidence and descriptor revisions; it does not mutate old evidence or silently reactivate a revoked provider.

Learned reliability estimates can influence candidate ranking and resource estimates only. They cannot change provider trust state, Android permissions, AURIONS grants, risk class, approval requirements or execution-gateway decisions.


### 6.4 Canonical provider lifecycle and failure payload binding

The machine-readable payload definitions are maintained in `schemas/domain-payloads.v1.schema.json` under `providerLifecycle`, `providerFailure` and `compatibilityNegotiationState`; neutral validated-provider and enabled-provider examples are in `schemas/fixtures/provider-lifecycle.fixture.json` and `schemas/fixtures/provider-lifecycle-enabled.fixture.json`; the dispatched-blind-retry negative control is in `schemas/fixtures/negative/provider-failure-dispatched-blind-retry.invalid.json`. These schemas make the lifecycle and failure contract machine-readable, but they do not validate a provider or grant it authority.

Normative lifecycle constraints:
- A provider first observed from an environment is recorded as `observed` and remains non-invocable until validation and independent policy enablement have occurred.
- `quarantined` is the safe holding state for unknown, incomplete or integrity-unverified providers. Validation evidence must bind the exact provider identity, version, artifact digest and interface/schema versions.
- `validated` records technical validation only. It does not grant Android permissions, owner authorization or execution eligibility by itself.
- `enabled` requires a separate trusted policy decision and currently required platform permissions. The provider cannot issue or approve that decision for itself.
- `degraded` constrains or suspends use when health, compatibility or reliability evidence changes; it does not silently retain prior eligibility.
- `revoked` is immediately non-invocable. `retired` is terminal for that provider version; a new version is a new validation subject.
- Any provider artifact, version, interface schema, permission scope or trust-root change invalidates prior validation for the affected version. Capability descriptors and plans referencing the changed provider are revalidated or invalidated before dispatch.
- Provider reliability learning may inform estimates and discovery prioritization only. It MUST NOT alter provider trust state, platform permission, owner approval, risk classification or action-gateway policy.

Normative failure constraints:
- Every discovery/provider failure identifies a stable machine category, retryability, side-effect state, correlation identity and provider/descriptor version when known.
- If side-effect state is `dispatched` or `unknown`, retryability MUST be `reconcile_before_retry`; no blind retry is permitted.
- Permission denial, owner-authorization denial, unsupported capability, stale descriptor, schema incompatibility and provider unavailability remain distinct outcomes. They must not be collapsed into a generic failure or interpreted as a learned universal inability.
- A cancelled request does not prove that an already-dispatched provider operation was cancelled. The operation receipt/reconciliation path remains authoritative for effects.
- Compatibility negotiation selects only a mutually supported schema/envelope version. It never upgrades an unsupported message by guessing or silently dropping security-relevant fields.

## 7. Required interfaces

The implementation contract must provide versioned equivalents of:

- Environment observation query and observation event.
- Discovery request, discovery result and discovery failure.
- Capability descriptor publication, update, invalidation and revocation.
- Capability knowledge/evidence query and revision event.
- Capability feasibility/precondition evaluation.
- Plan proposal referencing capability IDs and descriptor versions.
- Exact-operation authorization request/decision.
- Durable operation dispatch, receipt, verification and uncertainty reconciliation.
- Outcome/prediction evaluation and learning-update proposal.
- Capability rediscovery trigger and environment-change event.

Each contract must define schema version, stable IDs, provenance, timestamps, correlation/causation, owner/device scope, sensitivity, idempotency, errors, cancellation, durability and compatibility. The implementation-ready planning contract must own the concrete schemas; this architecture document defines their semantics and ownership.

### 7.1 Canonical contract and ownership mapping

The canonical mechanism-to-component/state/API/work-package/test crosswalk is maintained in [Cognitive and Capability Contract Matrix](COGNITIVE-AND-CAPABILITY-CONTRACT-MATRIX.md), Section 3. The field-level environment, discovery, capability descriptor, capability-knowledge, plan-step, operation-proposal and execution-receipt semantics are maintained in [Implementation-Ready Planning Contracts](../planning/IMPLEMENTATION-READY-PLANNING-CONTRACTS.md), Section 4.4.

These documents are the single sources of truth for the mapping and payload semantics; this architecture document defines Android-specific behaviour and invariants. Do not create a second capability catalogue or duplicate schemas here.

The critical authority boundaries remain:
- The environment/discovery component owns observations, discovery provenance, descriptor versions and capability knowledge references; it does not own permission grants.
- Android remains authoritative for platform permission state. AURIONS governance independently evaluates owner authority and exact-operation policy.
- The action gateway owns durable dispatch and operation lifecycle. Outcome evaluation owns postcondition evidence and learning proposals.
- The cognitive planner references discovered descriptor IDs/versions; it never treats a descriptor as permission or as proof that an operation is currently feasible.

## 8. Required verification scenarios

These are mechanism tests, not a fixed set of product capabilities:

- **AD-001 Discovery without authority:** a capability can be described as discovered while execution remains denied for missing permission.
- **AD-002 Unknown interface:** an unavailable or undocumented interface remains unknown; AURIONS does not fabricate an invocation.
- **AD-003 New provider:** a newly introduced provider can be discovered and represented without editing a hardcoded task-to-action map.
- **AD-004 Version change:** app/OS/provider update invalidates stale metadata and forces revalidation.
- **AD-005 Revocation:** permission revocation blocks queued and future execution; active work follows safe cancellation/reconciliation.
- **AD-006 Exact authorization:** a changed target, parameter, effect, data category or descriptor version invalidates approval.
- **AD-007 Outcome verification:** a successful invocation with an unverified postcondition is not reported as a verified effect.
- **AD-008 Contextual learning:** an observed failure revises context-specific capability knowledge without creating a universal fixed prohibition.
- **AD-009 Strategy adaptation:** a later related task selects a different evidence-supported strategy after prior outcome feedback; unrelated controls do not regress.
- **AD-010 No authority learning:** repeated success cannot remove permission checks, lower risk or create owner approval.
- **AD-011 Offline execution:** local discovery and an authorized local operation complete without network access.
- **AD-012 Cloud proposal boundary:** a remote plan cannot execute until the device independently revalidates and authorizes it.
- **AD-013 Sensitive observation:** private environment data is not placed in external prompts or sync payloads without authorization.
- **AD-014 Crash uncertainty:** a process death around dispatch yields a reconciled or explicitly uncertain operation, never an unsafe blind retry.
- **AD-015 Extensible descriptor:** a capability with a new schema-compatible descriptor can be represented without adding a hardcoded behaviour branch to the cognitive core.

Each scenario requires fixtures, exact steps, durable state assertions, negative controls and reproducible evidence before its status can become VALIDATED.

## 9. Platform validation and unresolved engineering work

The following cannot be settled by prose alone:
- Exact Android API level, package visibility and application-interface discovery limits on the target OS/build.
- Which discovery sources are available without additional permissions and which require explicit user grants.
- Kotlin/native adapter boundary and JNI/shared-library versus IPC based on measured stability, memory and lifecycle.
- Foreground service, background execution, process-death and reboot behaviour under the actual device vendor's Android configuration.
- Secure key storage and authentication integration.
- Performance, battery, thermal and storage costs under representative capability-discovery and execution workloads.
- Platform-policy and Play distribution constraints if distribution outside the owner's device is later intended.

These are validation gates. No exact operation catalogue, first Android action, broad permission grant or privileged access assumption is selected by this document.

## 10. Completion criteria

This architecture section is not complete until:
1. The discovery, registry, capability knowledge, planning, governance, execution, verification and learning mechanisms have explicit component ownership.
2. Their interfaces and data lifecycles are reconciled with the C++ core, memory/events/governance stores and implementation-ready contracts.
3. Failure, cancellation, uncertainty, revocation, stale metadata and recovery paths are specified.
4. Cloud/offline-mobile authority and data boundaries are consistent with owner decisions.
5. The AD-* scenarios are incorporated into the canonical test catalogue and mapped to requirements.
6. The no-hardcoding invariant is traceable through the architecture, product definition, contracts and roadmap.
7. The exact revised design passes architecture consistency review and independent re-review.
8. Platform-dependent claims remain explicitly unvalidated until actual device evidence exists.

**Current disposition:** IN PROGRESS. This document materially expands the Android architecture but does not itself close the design, platform validation, independent-review or owner-approval gates.
