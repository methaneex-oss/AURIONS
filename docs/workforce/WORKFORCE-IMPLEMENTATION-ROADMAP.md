# Workforce Implementation Roadmap

**Operating mode:** Supervised autonomy  
**Initial team:** Six specialist agents  
**Project repository:** `methaneex-oss/AURIONS`  
**Workforce branch:** `feat/engineering-workforce-foundation`  
**Status:** Proposed staged setup; no AURIONS runtime implementation authorized

## 1. Scope boundary

The workforce is being established inside the existing AURIONS repository because the repository already contains the authoritative project context and engineering history. No separate workforce repository will be created.

Workforce documentation and eventual orchestration tooling must remain isolated from AURIONS runtime/cognitive code. The workforce is engineering infrastructure, not an AURIONS cognitive subsystem.

This branch is based on PR #2's verified head `a5f671f9252f7b33508ab53d29d467c7e88c4075` as observed on 13 November 2026. It is a separate branch and does not modify PR #1, PR #2, `main` or their existing branches.

The workforce branch must be reconciled with the latest repository state before any PR is opened. It must not be merged by implication.

## 2. Architecture

Initial components:
1. Deterministic orchestrator API and scheduler.
2. PostgreSQL persistent task, run, checkpoint and audit state.
3. Model gateway with OpenRouter first and provider adapters behind an interface.
4. Nemotron as an initially evaluated builder model, subject to live capability and quota checks.
5. Six role-specialized agents: lead builder, specialist builder, architecture reviewer, code reviewer, negative tester, integration/verification agent.
6. Isolated disposable worker containers.
7. GitHub App credential broker and task-scoped authorization policy.
8. Durable artifact storage for logs, test results and evidence.
9. Director dashboard and approval interface.

Recommended initial stack:
- Python and FastAPI for orchestration;
- PostgreSQL for durable state and initially a database-backed queue;
- Docker for isolated workers;
- GitHub App for repository operations;
- OpenRouter for model access;
- secret-manager-backed credentials;
- S3-compatible artifact storage when durable external artifacts are required;
- lightweight dashboard after the control plane is reliable.

Do not introduce Kubernetes, Kafka or multiple queue systems until measured requirements justify them.

## 3. Stages and gates

### WF-00 — Constitution and context foundation

Deliver:
- mandatory workforce constitution;
- role contracts and operating protocol;
- canonical context index;
- current-state refresh procedure;
- authority and approval matrix;
- version/hash acknowledgement requirement.

Acceptance:
- every agent role has the same authoritative project principles and governance;
- all canonical source documents are discoverable;
- stale snapshots are detected;
- unresolved owner decisions are explicit;
- no agent can treat a prompt acknowledgement as a permission grant;
- automated validation checks required policy fields and references.

### WF-01 — Orchestrator and persistent state

Deliver:
- orchestrator API;
- PostgreSQL schema and migrations;
- task state machine;
- leases and heartbeats;
- checkpoint and recovery records;
- append-only audit events;
- pause/cancel controls.

Acceptance:
- task survives orchestrator restart;
- worker crash resumes from last verified checkpoint;
- expired worker loses authority;
- invalid state transitions are rejected;
- duplicate side effects are detected or idempotent;
- audit records survive restart.

### WF-02 — Model gateway and one builder

Deliver:
- OpenRouter adapter;
- configurable model registry;
- Nemotron capability/availability probe;
- structured tool-call loop;
- usage accounting and request limits;
- one isolated builder worker.

Acceptance:
- one bounded demonstration task completes in a disposable demo workspace;
- model cannot access secrets;
- tool calls pass policy validation;
- quota/rate-limit failures pause safely;
- free-only mode is enforced;
- exact output commit and evidence are recorded.

### WF-03 — Independent review and negative testing

Deliver:
- architecture reviewer;
- code reviewer;
- negative tester;
- immutable candidate handoff;
- severity and finding lifecycle;
- evidence collection.

Acceptance:
- all roles receive the exact candidate SHA;
- reviewers cannot edit the candidate;
- a deliberately defective sample is detected;
- high/critical findings block progression;
- builder cannot approve itself;
- review independence is recorded and auditable.

### WF-04 — Parallel builders and integration

Deliver:
- second builder;
- branch/workspace isolation;
- dependency-aware scheduling;
- integration agent;
- conflict and ownership detection.

Acceptance:
- two non-overlapping tasks run concurrently;
- conflicting file ownership is blocked or serialized;
- integration verifies exact parent and candidate SHAs;
- regression suite runs after integration;
- integration agent cannot merge to main.

### WF-05 — Operational hardening

Deliver:
- worker supervision;
- crash/restart recovery;
- retry/backoff policy;
- model and compute budgets;
- metrics, alerts and dashboard;
- backup/restore procedures;
- security and prompt-injection tests.

Acceptance:
- orchestrator crash recovery passes;
- worker crash recovery passes;
- budget exhaustion pauses all affected work safely;
- retry caps are enforced;
- secret exposure tests pass;
- unauthorized branch/path/merge operations are denied;
- backups restore task state and evidence references.

### WF-06 — AURIONS pilot authorization

This stage is not automatically approved by completing WF-00 through WF-05.

The Project Director must explicitly authorize:
- the pilot work package;
- its base commit and branch;
- permitted paths;
- acceptance criteria;
- agent/model assignments;
- budget and duration;
- test and review requirements.

The first AURIONS pilot must use a bounded, low-risk task already permitted by the project's current governance. It must not be used to bypass planning exit or runtime implementation approval.

Acceptance:
- complete builder → tester → independent review → integration → Director decision cycle;
- reproducible evidence on exact commits;
- no unauthorized changes;
- no loss of state during injected worker interruption;
- Director makes the final acceptance decision.

## 4. Runtime and hosting assumptions

Recommended first deployment: one persistent cloud VM or equivalent persistent container host for the orchestrator, PostgreSQL and worker supervisor, with disposable isolated worker containers.

The system must remain recoverable if the VM or worker process restarts. A persistent host does not imply persistent privileged workers. Untrusted project code should run in ephemeral isolated environments without access to host secrets.

Initial concurrency target:
- up to two builders;
- one or two review jobs;
- one negative-test job;
- one integration job, scheduled after dependencies are met.

This is a ceiling for initial scheduling, not a requirement to keep all agents active continuously.

## 5. Cost policy

Initial configuration:
- OpenRouter free models only;
- paid fallback disabled;
- per-request token cap;
- per-task call and token budget;
- per-agent and global daily budget;
- bounded retry count;
- no repeated identical model loops;
- compute time, CPU, memory and storage limits;
- pause and report on budget exhaustion.

The system must measure actual model consumption from pilot tasks. Do not assume that free access is unlimited or that multiple API keys multiply account quotas.

Any paid inference, additional provider subscription or hosting expansion requires a cost proposal and Director authorization.

## 6. Timeline policy

No completion date is approved in this roadmap. Stage dates are `UNSET` until the Project Director approves them.

The orchestrator may provide effort estimates and dependency-aware schedules. It must not convert estimates into commitments or silently impose deadlines on AURIONS.

## 7. Workforce acceptance suite

Before the workforce can receive AURIONS write access, demonstrate:
1. constitution and project snapshot version validation;
2. stale context rejection;
3. role and tool permission enforcement;
4. unauthorized path write rejection;
5. protected branch and merge denial;
6. builder crash and checkpoint recovery;
7. orchestrator restart recovery;
8. duplicate operation/idempotency protection;
9. reviewer independence;
10. tester exact-SHA pinning;
11. injected defect detection;
12. rate-limit and provider outage handling;
13. free-only budget enforcement;
14. secret non-disclosure;
15. prompt-injection resistance;
16. immutable evidence and audit record retention;
17. backup/restore verification;
18. Director pause and cancellation.

Critical security, authority, persistence and evidence tests must pass. A visually functioning dashboard or successful demo is not sufficient.

## 8. Open infrastructure decisions

The following remain to be measured or approved:
- cloud host/provider and monthly cost;
- secret manager choice;
- artifact storage choice;
- GitHub App installation and exact permissions;
- database backup and retention policy;
- exact model IDs and reviewer diversity;
- whether a second direct provider is needed in addition to OpenRouter;
- dashboard hosting and authentication;
- operational alert channel.

Do not hardcode provider-specific assumptions into agent roles.

## 9. Current implementation status

- WF-00 documentation: drafted in this branch.
- WF-01 through WF-06: NOT STARTED.
- Orchestrator runtime: NOT IMPLEMENTED.
- PostgreSQL workforce schema: NOT IMPLEMENTED.
- OpenRouter integration: NOT IMPLEMENTED.
- Nemotron execution: NOT IMPLEMENTED.
- GitHub App broker: NOT IMPLEMENTED.
- Worker containers: NOT IMPLEMENTED.
- Reviewer/tester execution: NOT IMPLEMENTED.
- Dashboard: NOT IMPLEMENTED.
- AURIONS workforce pilot: NOT AUTHORIZED.

This status must be updated only with commit and test evidence.
