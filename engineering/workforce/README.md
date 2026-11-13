# AURIONS Workforce Control Plane — WF-01

This directory contains engineering-workforce infrastructure only. It is not part of the AURIONS cognitive/runtime architecture.

## Current vertical slice

- FastAPI control-plane service.
- PostgreSQL task, checkpoint and append-only audit tables.
- Mandatory task-contract validation before queueing.
- Deterministic task state-transition rules; ACCEPTED requires a Director decision reference and separate approval credential.
- Expiring worker leases with opaque lease tokens; only the token hash is persisted.
- Checkpoint writes require a live lease.
- Docker Compose deployment definition with a non-root, read-only API container.

## Local deployment

Set WORKFORCE_DB_PASSWORD and DIRECTOR_APPROVAL_TOKEN through a local secret manager or protected environment. Do not commit .env files or credentials.

Run: docker compose -f compose.yaml up --build

The API listens on 127.0.0.1:8000; health check: GET /health.

## Important limitations — not yet an agent workforce

This WF-01 slice is the durable control-plane foundation. It does not yet execute model calls, create isolated builder containers, broker GitHub credentials, enforce Git path permissions at a GitHub write boundary, provide a Director dashboard, or run the six specialist agents. Those capabilities require subsequent integration and security gates. Do not connect repository write credentials or launch AURIONS work until those controls are implemented and tested.

## State

WF-01 implementation candidate. Requires CI execution, independent review, security testing, deployment configuration and Director acceptance before operational use.
