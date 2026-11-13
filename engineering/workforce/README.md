# AURIONS Workforce Control Plane — WF-01/WF-02

This directory contains engineering-workforce infrastructure only. It is not part of the AURIONS cognitive/runtime architecture.

## Implemented foundation

- FastAPI control-plane service and PostgreSQL task/checkpoint/audit schema.
- Mandatory task-contract validation and deterministic state-transition rules.
- Expiring worker leases, checkpoint writes and append-only audit events.
- OpenRouter tool-calling runner with six role identities.
- Read-only reviewer/tester roles and builder path allowlists.
- No arbitrary shell tool; the only execution tool runs the fixed workforce test suite.
- Free-model-only enforcement and per-agent call/token ceilings.
- Docker Compose deployment definition with a non-root, read-only API container.

## First supervised run

The first-run workflow runs two sequential builders, three independent reviewers/testers, and an integration verifier. It operates on a candidate artifact and does not push commits, open PRs, merge, or modify AURIONS cognitive/runtime code. Candidate identity is frozen with SHA-256 before review.

The workflow requires the repository Actions secret OPENROUTER_API_KEY. Set it under repository Settings → Secrets and variables → Actions. Never place the key in source files, workflow YAML, prompts, artifacts, or chat. The configured model is nvidia/nemotron-3.5-lightning:free; there is no paid fallback.

## Local deployment

Set WORKFORCE_DB_PASSWORD and DIRECTOR_APPROVAL_TOKEN through a protected environment. Do not commit .env files or credentials.

Run: docker compose -f compose.yaml up --build

The API listens on 127.0.0.1:8000; health check: GET /health.

## Explicit limitations

This is an initial implementation candidate, not a production-ready autonomous workforce. The runner operates within GitHub Actions job isolation and returns candidate artifacts; it does not yet provide a persistent cloud worker supervisor, GitHub write broker, full API authentication, deployment/backup hardening, or production-grade lease recovery. Do not connect repository write credentials or launch AURIONS runtime implementation until those controls are independently tested and authorized.

## Status

WF-01/WF-02 foundation code is present. CI and the first six-role run are the next validation gates. No AURIONS runtime implementation or merge is authorized.
