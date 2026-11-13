# AURIONS Workforce Control Plane — WF-01/WF-02

This directory contains engineering-workforce infrastructure only. It is not part of the AURIONS cognitive/runtime architecture.

## Implemented components

- PostgreSQL task, checkpoint and append-only audit storage.
- Strict task contracts and deterministic lifecycle transitions.
- Separate Director, orchestrator and role-scoped worker credentials.
- Worker identity and role derived from credentials, never caller-supplied IDs.
- Atomic role-matched task claims, lease generations and expiry fencing.
- Idempotent checkpoint writes tied to the current live lease, with authorized restoration after recovery.
- Append-only evidence digests and artifact references bound to each lifecycle gate; Director acceptance must reference the exact integrated evidence record.
- A durable supervisor that recovers expired leases, preserves checkpoints for retry, caps attempts and enforces the contract's absolute deadline while queued, then the earlier of that deadline or the maximum task lifetime measured from first claim.
- Separate API and supervisor containers with non-root, read-only filesystems.
- Six distinct pinned model assignments; runner hard ceilings of 100 calls, 32,768 completion tokens/call, 200,000 total tokens and 360 minutes. Every CLI task execution requires a live control-plane lease and atomically reserves/settles per-work-package/per-role token and call budgets in PostgreSQL. Reservations left by a crashed or fenced worker are conservatively charged at their full reserved amount.
- Paid inference fallback remains disabled.

## Required deployment secrets

Provide these values through a protected secret manager or deployment environment; never commit them:

- `WORKFORCE_DB_PASSWORD`
- `DIRECTOR_APPROVAL_TOKEN`
- `WORKFORCE_ORCHESTRATOR_TOKEN`
- `WORKFORCE_WORKER_CREDENTIALS_JSON` — JSON mapping worker IDs to an individual token and exactly one role, for example:
  `{"builder-01":{"token":"...","role":"lead_builder"},"reviewer-01":{"token":"...","role":"code_reviewer"}}`

The API rejects missing credentials. Rotate credentials if exposed. Use distinct random tokens for every actor. The Director token is required to authorize task creation and accept a completed task; the orchestrator token cannot accept work. Worker tokens are role-scoped.

The worker CLI requires `WORKFORCE_CONTROL_PLANE_URL`, `WORKFORCE_TASK_ID` and `WORKFORCE_WORKER_TOKEN`. It claims a role-matched task and starts it under a 15-minute lease; an optional `WORKFORCE_LEASE_TOKEN` resumes an existing lease. Each provider request renews the lease, reserves its token ceiling before sending, and settles reported usage afterward. On success, the CLI writes a report artifact, hashes it and publishes the evidence reference through the control plane. On execution failure it attempts a fail-closed task transition; any unsettled reservation is charged by supervisor recovery.

Provider secrets remain separate:
- `GROQ_API_KEY` for the three Groq roles.
- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` for the three Cloudflare roles.

## Deployment

Run `docker compose -f engineering/workforce/compose.yaml up --build` from the repository root after setting the protected environment variables. The API binds to loopback port 8000. PostgreSQL data is persisted in the named volume. The supervisor runs independently and polls every five seconds.

Apply new SQL files in `migrations/` to an existing database in lexical order (including `003_immutable_evidence.sql`, `004_agent_budget_ledger.sql`, `005_absolute_task_deadlines.sql` and `006_start_deadline_on_first_claim.sql`). The initial Postgres image initialization applies migrations only on an empty data volume; existing deployments must apply newly added migrations explicitly.

## Six-role orchestration

The CLI coordinates all six roles in one pinned workspace, sequentially: lead builder, specialist builder, candidate snapshot/tests, three independent read-only reviews, then integration verification. Builder write scopes must be disjoint. Reviewers receive the frozen candidate manifest and test evidence. The integration verifier receives all review reports. The orchestrator never commits, pushes, merges or accepts the work.

1. Start the API and supervisor with the Compose deployment above.
2. Create a Director-approved JSON work-package manifest from `work-package.template.json`. Replace every placeholder, set the exact base commit SHA, provide all six role task instructions, and define disjoint builder path allowlists.
3. Configure `WORKFORCE_CONTROL_PLANE_URL`, `DIRECTOR_APPROVAL_TOKEN`, `WORKFORCE_ORCHESTRATOR_TOKEN`, `WORKFORCE_WORKER_CREDENTIALS_JSON`, and the provider credentials in the orchestrator's protected environment.
4. Run `PYTHONPATH=engineering/workforce/src python -m workforce.orchestrator --manifest /secure/path/work-package.json --workspace .`.
5. Inspect the candidate files and `engineering/workforce/.workforce-artifacts/`. The final task stops at `AWAITING_DIRECTOR`; it is not accepted automatically.

The worker process receives only its own role token and its pinned provider credential. Repository tests run from an isolated copy with credentials removed. The orchestrator's test suite also runs from a separate snapshot. A disposable PostgreSQL test database is used only when `WORKFORCE_TEST_DATABASE_URL` and the three `WORKFORCE_TEST_*` credentials are explicitly supplied; it must never point at the live control-plane database.

The orchestrator is a bounded sequential dispatcher, not a distributed queue or parallel scheduler. Queued tasks do not consume their execution-duration budget until first claim; the absolute contract deadline still applies while queued. An unclaimed task is also failed after a 10-minute dispatch TTL so an orchestrator crash cannot leave an orphaned task indefinitely. The manifest's `test_paths` declares the source/test inputs copied into an isolated test snapshot. Optional `test_commands` are explicit argument arrays (never shell strings) and are limited to Python unittest/pytest/compileall, CMake configure/build, CTest and Ninja. Candidate-controlled test code runs in a read-only-root Docker container with a writable snapshot mount, no Linux capabilities, resource limits, and an internal-only network connected solely to a disposable PostgreSQL container. It receives ephemeral test-only actor/database credentials; provider, worker, Director, orchestrator and production database credentials are never passed into the test container. The image is built from `engineering/workforce/Dockerfile.test-runner` before any provider inference step. The control plane persists tasks, leases, checkpoints, evidence and per-work-package/per-role budgets. A new run ID creates new task records but consumes the same work-package budget when the same persistent database is used. If an orchestration process is interrupted, the supervisor recovers expired worker leases; a new orchestration attempt requires a clean workspace and a new run ID. Preserve the previous evidence folder before resetting or creating a fresh workspace.

For a supervised GitHub test run, use the **Manually approved six-role workforce run** workflow. First commit the code baseline. Then create a separate commit containing only the filled work-package manifest; set its `base_commit_sha` to the exact code-baseline commit immediately before the manifest-only commit. Select the branch containing that manifest commit, provide its committed manifest path, and set `confirm_run=true`. Before this PR is merged, the same workflow can be triggered on `feat/workforce-control-plane-hardening` by committing only `engineering/workforce/work-package.json` with a commit message containing the exact marker `[RUN-WORKFORCE]`. That marker is an explicit authorization to make provider inference calls; ordinary pushes do not run the job. The workflow creates an isolated Git worktree at the baseline SHA, so the manifest never needs to contain its own commit hash. The workflow generates ephemeral Director, orchestrator and six worker credentials inside the job; the orchestrator creates a separate internal-network PostgreSQL test database and ephemeral test-only actors. The workflow requires only the provider secrets `GROQ_API_KEY`, `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. It starts an isolated PostgreSQL control plane and a separate disposable integration-test database, runs all six roles, and uploads the candidate patch and Director evidence packet. It has read-only repository permissions and does not commit or merge. **This GitHub workflow's database is ephemeral**: its ledger is for one supervised run and is destroyed afterward. Use the Compose deployment with its persistent PostgreSQL volume for persistent local operation.

## Verification

The workforce test workflow starts a disposable PostgreSQL 17 service, applies every migration, compiles the source and runs the full unittest suite. No provider calls are made by this CI workflow.

## Explicit status and limitations

The control-plane security, evidence, recovery and self-claiming worker CLI are implementation candidates until the PostgreSQL integration suite and independent review pass. Evidence references record hashes and locations; an independent verifier must still retrieve each artifact and confirm its bytes match the recorded digest. Provider connectivity and role qualification are separate gates: configured model assignments do not prove that credentials work or that agents are competent. The PostgreSQL ledger enforces cumulative per-role budgets across tasks and retries in a work package; local process ceilings are an additional guard. Provider-side quota reconciliation remains separate because providers expose different accounting and shared daily limits. No persistent multi-agent run, GitHub write broker or AURIONS runtime implementation is authorized by this infrastructure work.

The first-run workflow remains dormant. No merge to `main`, paid fallback, production activation or AURIONS runtime implementation is authorized.
