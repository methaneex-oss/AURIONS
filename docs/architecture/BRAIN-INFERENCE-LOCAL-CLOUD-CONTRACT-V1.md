# AURIONS — Brain/Inference Integration Contract v1 (Builder Proposal)

- **Status:** Contract plus an implemented first C++ conversation slice on `impl/experience-continuity`; not owner acceptance or production readiness.
- **Product invariant:** One AURIONS brain, two inference access paths (local/offline and cloud/online). These are not two assistants and must not maintain separate cognitive logic.
- **Authority:** The C++ cognitive runtime owns objectives, context, memory, beliefs, planning, governance, learning decisions and durable state. An inference backend generates candidate model output only.
- **Related owner decisions:** Concurrent cloud and offline-mobile operation; shared cognitive-core implementation; D-02 Option B selective synchronization. Mobile device authority remains local.

## 1. Non-negotiable system boundary

The model is not the brain. The brain selects and prepares context, chooses an allowed inference route, evaluates model output, decides whether additional retrieval/reasoning is needed, governs any proposed interaction, observes outcomes and decides what durable learning is justified.

Local and cloud inference are replaceable execution resources behind one versioned contract. A local model and a cloud model may have different capability, latency and cost, but they do not get separate memories, beliefs, goals, policies or identities.

The same C++ cognitive-core implementation must run in both deployment contexts. The local runtime must remain capable of its required workflows with all network access disabled. Cloud access adds online inference, web research and remote compute; it must not be required for the local brain to boot, retrieve memory, reason within its available model capability, or govern local actions.

## 2. Ownership

| Concern | Owner |
|---|---|
| User objective, task lifecycle and durable checkpoints | Cognitive runtime / goal and task owners |
| Experience capture, source and provenance | Experience subsystem |
| Context selection, redaction and evidence packet | Cognitive runtime and domain owners |
| Beliefs, confidence, contradictions and evidence lineage | Belief/knowledge owners |
| Model choice, route eligibility and fallback policy | Inference router under runtime policy |
| Token generation | Selected local or cloud model backend |
| Output validation and interpretation | Cognitive runtime |
| Tool/OS action proposal | Reasoning/means mechanisms |
| Authorization and dispatch | Local governance and device runtime |
| Actual result/receipt and independent observation | Interaction/runtime boundary |
| Learning decision and persistence | Learning subsystem and state-domain owners |
| Cloud/mobile synchronization | Dedicated sync subsystem; never direct DB replication |

No backend may write memory, beliefs, goals, policy, permissions, active model pointers or synchronization state.

## 3. Versioned request contract

The runtime sends one bounded request envelope to either backend:

```json
{
  "contract_version": "aurions.inference.v1",
  "request_id": "stable-unique-id",
  "runtime_id": "runtime-identity",
  "route": "local",
  "task": {
    "task_id": "stable-task-id",
    "objective_ref": "objective-id",
    "turn_ref": "turn-id",
    "purpose": "conversation|reasoning|planning|research_synthesis"
  },
  "input": {
    "messages": [
      {"role": "user", "content": "user message"}
    ],
    "context_ref": "immutable-context-snapshot-id",
    "evidence_refs": ["experience-or-belief-revision-id"]
  },
  "constraints": {
    "max_input_bytes": 32768,
    "max_output_tokens": 1024,
    "deadline_ms": 45000,
    "sensitivity_ceiling": "owner_private",
    "tools_enabled": false
  },
  "model": {
    "policy_ref": "inference-policy-version",
    "requested_capability": "general"
  }
}
```

This is a contract example, not a claim that these fields or limits are implemented. The schema must enforce exact fields, types, enumerations, size limits and cross-field invariants. The actual context body is obtained from the runtime-owned context snapshot; a backend cannot request arbitrary database access.

For cloud routing, a separate egress-policy decision must authorize the exact context fields before serialization. SENSITIVE and LOCAL_ONLY material is excluded. OWNER_PRIVATE content is not exported by default; any future exception requires an explicit, narrowly scoped policy. Network availability alone never authorizes cloud egress.

## 4. Versioned response contract

```json
{
  "contract_version": "aurions.inference.v1",
  "request_id": "same-request-id",
  "backend": {
    "kind": "local",
    "provider": "local-runtime",
    "model_id": "model-id",
    "model_revision": "immutable-revision"
  },
  "result": {
    "status": "completed",
    "message": "candidate generated text",
    "finish_reason": "stop",
    "proposed_interactions": []
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0
  }
}
```

Response is untrusted model output, not a decision, receipt, verified fact or authorization. Unknown fields, mismatched request IDs, wrong backend/model identity, invalid UTF-8, oversized text, malformed structured proposals, timeout, cancellation or non-success status must fail closed. Model output must never be interpreted as an instruction to change policy or grant authority.

## 5. Local/cloud routing and fallback

- Default route for the offline-capable mobile runtime is local.
- Cloud route is selected only when online and permitted by explicit inference/egress policy.
- Local route targets a local inference service or admitted local model runtime; remote network endpoints are not silently treated as local.
- Cloud route uses authenticated HTTPS and credential isolation. Redirects are rejected unless a future policy explicitly validates the destination and credential handling.
- Fallback is a new, explicit route decision. A failed cloud request may fall back to local only if the request's sensitivity and capability requirements permit it.
- No silent cloud upload when local inference is unavailable.
- Route and model identity are recorded with the result for reproducibility.
- Both paths feed the same C++ cognitive loop and same owner-scoped persistence semantics.
- Local and cloud model revisions may differ; model identity and evaluation state are explicit, while brain identity and state ownership remain common.

## 6. Online research as experience, not privileged truth

Online research is a source of observations. Search results and fetched pages must be captured with source URL, retrieval time, publisher/source identity where available, content hash, extraction method, limitations and sensitivity classification. The runtime distinguishes source text from model summaries and inferred claims.

Retrieved content is untrusted data. It cannot override system policy, developer instructions, owner decisions, permissions or runtime governance. Contradictory sources remain separately represented; belief confidence changes only through an explicit evidence-evaluation process. Offline operation uses previously captured and permitted local evidence; it must report when freshness or online retrieval is unavailable.

## 7. Cognitive closed loop

The intended recurrent loop is not a rigid hard-coded task script:

1. Accept an objective/message and create or resume durable task state.
2. Build a situation/context snapshot from current input, relevant experiences, beliefs, goals and observations.
3. Identify missing information; decide whether local retrieval, online research or clarification is appropriate.
4. Select an inference route based on capability, sensitivity, availability, latency/resource budget and policy.
5. Generate a candidate response, hypothesis, plan or interaction proposal.
6. Evaluate consistency, evidence, uncertainty, policy and task relevance; iterate or abstain where needed.
7. Present a response or submit an interaction proposal to governance. No model text directly dispatches an OS operation.
8. Observe actual result independently; distinguish dispatch receipt from verified effect.
9. Record the interaction and outcome as provenance-linked experience.
10. Let learning mechanisms decide whether a memory, belief, strategy, representation or model candidate should change. Persist the decision and its evidence.

Every durable step must be recoverable after process death. A task must not be reported complete solely because inference returned text.

## 8. Learning semantics

Three learning paths must remain distinct:

- **Experience/memory adaptation:** retrieve prior interactions and outcomes in later context.
- **Cognitive adaptation:** update evidence-backed beliefs, predictions, strategy estimates, representations or procedures from evaluated experience.
- **Model adaptation:** train or fine-tune candidate weights, evaluate against frozen baselines and regression suites, then quarantine pending admission. A training job or lower loss does not prove improved behavior.

User correction is valuable evidence, but it is not automatically a globally true fact. It must be scoped, attributed and reconciled with prior evidence. The runtime must be able to revise or retract a learned item while preserving lineage.

## 9. Local/cloud state continuity

The selected D-02 Option B is bounded selective synchronization, not replication of SQLite files. Local-only device authority, permissions, credentials, raw/sensitive observations and live operation state remain local. Only exact fields accepted by the sync allowlist may be synchronized through versioned domain changes, authenticated owner scope, idempotent outbox/inbox processing, causal revision checks, tombstones and recovery.

A locally committed change is not exported; an exported change is not received; a received change is not applied; an applied change is not reconciled. The brain must only use remote state after durable validation and application. A network partition must not block the local runtime.

The current sync field allowlist remains export-disabled pending the owner-acceptance gate in the selective-sync contract. Option B authorizes design of bounded synchronization, not silent export.

## 10. Failure and safety semantics

- Backend unavailable: use an eligible alternative route or return a truthful unavailable result.
- Cloud unavailable: local workflows continue.
- Local model unavailable: memory, task recovery and non-inference functions remain available; do not silently send private data to cloud.
- Invalid/partial model output: reject or request a bounded retry; do not persist it as fact.
- Context unavailable: report the limitation rather than inventing continuity.
- Cancellation/deadline: persist task state and stop worker; no late result may mutate the task.
- Duplicate response/replay: request ID and idempotency key prevent duplicate durable effects.
- Tool/OS proposal: require independent policy authorization at the local execution boundary.
- Crash between operation and observation: recover from durable operation state and independently reconcile; never infer success from process exit alone.

## 11. Required executable acceptance tests

1. Same cognition contract and test vectors run against local and cloud adapters.
2. Network-disabled mobile can start, retrieve memory, invoke local inference and persist experience.
3. Cloud route is rejected when egress policy disallows the context.
4. Sensitive/local-only fields never appear in cloud request bytes.
5. Cloud timeout does not stop local memory/task recovery.
6. Fallback occurs only when policy permits it and is recorded as a distinct route.
7. Model response cannot mutate memory, belief, policy or permission without the relevant owner mechanism.
8. Wrong request ID, schema version, model identity, oversized output and malformed response are rejected.
9. Conversation/task resumes after process restart without duplicate effects.
10. Prior experience demonstrably changes a later context/response; unrelated or sensitive experiences do not leak.
11. User correction and contradictory evidence preserve source lineage and revisions.
12. Online research is stored as source-attributed experience; source instructions cannot alter governance.
13. A cloud-synchronized learning revision becomes visible locally only after authenticated, durable apply/reconciliation.
14. Device permissions and local execution authority cannot be granted or bypassed by cloud output.
15. Candidate model adaptation is evaluated and quarantined; active model changes only through admission policy.

## 12. Implementation order

A. Harden and test the existing worker boundary and prompt privacy.
B. Implement the shared C++ inference request/response types and strict validation.
C. Adapt the existing quarantined local candidate worker and the existing OpenAI-compatible local/cloud provider runtime behind the same contract; do not fork cognition.
D. Implement a bounded C++ conversation/task loop that uses experience/belief context, returns a model candidate, validates it and records interaction experience.
E. Add task checkpoints and restart/replay behavior.
F. Integrate online research as source-attributed experience with egress controls.
G. Implement D-02 sync only after its exact field-policy acceptance and peer trust lifecycle are satisfied.
H. Run the same behavioral suite on Android offline and cloud runtime.

This sequence deliberately prioritizes one functioning brain loop and two replaceable inference routes over a UI, multi-agent workforce, or broad tool catalogue.


## 12. Implemented slice and verified boundaries (2026-11-27)

The current branch now contains a first C++-owned conversation path:

- `aurions cognition chat` accepts bounded stdin, retrieves existing experiences and evidence-backed beliefs, applies the current sensitivity filter, builds a bounded evidence prompt, and invokes the configured provider runtime.
- Local and cloud requests use the same C++ cognition path, SQLite experience/belief stores and context builder. The backend is an inference resource, not a separate AURIONS identity.
- The local route is restricted by the provider runtime to loopback endpoints. The cloud route requires HTTPS to a non-loopback endpoint, an explicit C++ `--allow-cloud` flag, and input sensitivity `0` (public).
- The C++ launcher passes only the selected provider credential environment variable to the child process; prompt text travels over stdin, not argv. Provider response bytes are bounded and the process has a deadline.
- After successful inference, the user message and assistant response are persisted as provenance-linked experiences with the supplied sensitivity. Later turns can retrieve them; non-public experiences are excluded from model context.
- Model output is emitted as `display_only`. It cannot dispatch OS actions or directly create beliefs, permissions, goals or policies.

The integration test uses a deterministic fake provider. It verifies retrieval across separate CLI process lifetimes, exclusion of sensitive prior experience, explicit cloud opt-in, and refusal to send non-public input through the cloud route. This is test evidence for the C++ path and policy gates, **not** proof of a live local model, live cloud service, or actual network-disabled operation.

Remaining gaps are material: no actual local model invocation with networking disabled, no live cloud provider invocation, no Android/Termux run, no durable goal/task lifecycle or crash-safe response commit, no independent response/evidence evaluator, no web research acquisition pipeline, no tool/OS authorization-and-observation loop, and no automatic belief/strategy update from conversation. The current provider request is a single user-message prompt with retrieved context, not the complete versioned request/response envelope described above. Do not describe this slice as a complete cognitive brain or autonomous agent.
