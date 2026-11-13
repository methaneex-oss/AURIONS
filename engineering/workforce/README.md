# AURIONS Workforce Control Plane — WF-01/WF-02

This directory contains engineering-workforce infrastructure only. It is not part of the AURIONS cognitive/runtime architecture.

## Implemented foundation

- FastAPI control-plane service and PostgreSQL task/checkpoint/audit schema.
- Mandatory task-contract validation and deterministic task-state transition rules.
- Expiring worker leases, checkpoint writes and append-only audit events.
- Six exclusive role identities with one pinned, unique model per role.
- Mandatory fresh-read governance, EBT-01 and role-induction context on every worker run.
- Read-only reviewer/tester roles and builder path allowlists.
- No arbitrary shell tool; the only execution tool runs the fixed workforce test suite.
- Free-only model registry, provider-specific credentials and per-agent call/token ceilings.
- Docker Compose deployment definition with a non-root, read-only API container.

## Selected model roster

See [WORKFORCE-MODEL-SELECTION.md](../../docs/workforce/WORKFORCE-MODEL-SELECTION.md) for rationale and current free-tier limits.

| Role | Provider | Model |
|---|---|---|
| Lead builder | Groq direct | `openai/gpt-oss-120b` |
| Specialist builder | Cloudflare Workers AI | `@cf/google/gemma-4-26b-a4b-it` |
| Architecture reviewer | Cloudflare Workers AI | `@cf/zai-org/glm-4.7-flash` |
| Code reviewer | Groq direct | `qwen/qwen3.8-27b` |
| Negative tester | Groq direct | `openai/gpt-oss-20b` |
| Integration verifier | Cloudflare Workers AI | `@cf/mistralai/mistral-small-3.1-24b-instruct` |

Each role has a unique model assignment. These assignments are provisional selections, not agent qualifications.

## Required GitHub Actions secrets

- `GROQ_API_KEY` for lead builder, code reviewer and negative tester.
- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` for specialist builder, architecture reviewer and integration verifier.

Set them under repository Settings → Secrets and variables → Actions. Never put keys in source files, workflow YAML, prompts, artifacts or chat. Paid fallback is disabled. Cloudflare's daily free Neuron allowance is shared across the three Cloudflare roles.

## First supervised run

The existing `.github/workflows/workforce-first-long-run.yml` still contains a prewritten WF-01 workforce-infrastructure task. It is manually gated and must not be dispatched as the user's first task. Replace its task instructions with the Director-approved task contract before execution. Its current pipeline is finite and is not a persistent overnight supervisor.

## Local deployment

Set WORKFORCE_DB_PASSWORD and DIRECTOR_APPROVAL_TOKEN through a protected environment. Do not commit .env files or credentials.

Run: `docker compose -f compose.yaml up --build`

The API listens on 127.0.0.1:8000; health check: GET /health.

## Explicit limitations

This is an initial implementation candidate, not a production-ready autonomous workforce. The runner operates within GitHub Actions job isolation and returns candidate artifacts; it does not yet provide a persistent cloud worker supervisor, GitHub write broker, full API authentication, deployment/backup hardening, or production-grade lease recovery. Do not connect repository write credentials or launch AURIONS runtime implementation until those controls are independently tested and authorized.

## Status

WF-01/WF-02 foundation code is present. The model roster is selected but not yet executed or qualified. No AURIONS runtime implementation or merge is authorized.
