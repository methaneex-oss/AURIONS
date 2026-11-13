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
- A durable supervisor that recovers expired leases, preserves checkpoints for retry, caps attempts and enforces task-duration deadlines.
- Separate API and supervisor containers with non-root, read-only filesystems.
- Six distinct pinned model assignments and per-process hard ceilings (100 calls, 32,768 completion tokens/call, 200,000 reported total tokens and 360 minutes); prompt bytes plus protocol overhead are reserved before inference.
- Paid inference fallback remains disabled.

## Required deployment secrets

Provide these values through a protected secret manager or deployment environment; never commit them:

- `WORKFORCE_DB_PASSWORD`
- `DIRECTOR_APPROVAL_TOKEN`
- `WORKFORCE_ORCHESTRATOR_TOKEN`
- `WORKFORCE_WORKER_CREDENTIALS_JSON` — JSON mapping worker IDs to an individual token and exactly one role, for example:
  `{"builder-01":{"token":"...","role":"lead_builder"},"reviewer-01":{"token":"...","role":"code_reviewer"}}`

The API rejects missing credentials. Rotate credentials if exposed. Use distinct random tokens for every actor. The Director token is required to authorize task creation and accept a completed task; the orchestrator token cannot accept work. Worker tokens are role-scoped.

Provider secrets remain separate:
- `GROQ_API_KEY` for the three Groq roles.
- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` for the three Cloudflare roles.

## Deployment

Run `docker compose -f engineering/workforce/compose.yaml up --build` from the repository root after setting the protected environment variables. The API binds to loopback port 8000. PostgreSQL data is persisted in the named volume. The supervisor runs independently and polls every five seconds.

Apply new SQL files in `migrations/` to an existing database in lexical order (including `003_immutable_evidence.sql`). The initial Postgres image initialization applies migrations only on an empty data volume; existing deployments must apply newly added migrations explicitly.

## Verification

The workforce test workflow starts a disposable PostgreSQL 17 service, applies every migration, compiles the source and runs the full unittest suite. No provider calls are made by this CI workflow.

## Explicit status and limitations

The control-plane security, evidence and recovery work is an implementation candidate until the PostgreSQL integration suite and independent review pass. Evidence references record hashes and locations; an independent verifier must still retrieve each artifact and confirm its bytes match the recorded digest. Provider connectivity and role qualification are separate gates: configured model assignments do not prove that credentials work or that agents are competent. The runner's call/token ceilings are per process and reset on a retry; a durable cross-process/per-agent inference ledger and provider quota reconciliation remain required before claiming global budget enforcement. No persistent multi-agent run, GitHub write broker or AURIONS runtime implementation is authorized by this infrastructure work.

The first-run workflow remains dormant. No merge to `main`, paid fallback, production activation or AURIONS runtime implementation is authorized.
