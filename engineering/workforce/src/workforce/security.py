"""Fail-closed authentication primitives for workforce control-plane actors."""
from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass

ROLES = frozenset({
    "lead_builder", "specialist_builder", "architecture_reviewer",
    "code_reviewer", "negative_tester", "integration_verifier",
})


class AuthenticationError(ValueError):
    pass


@dataclass(frozen=True)
class Principal:
    actor_id: str
    role: str


def _matches_configured_secret(env_name: str, supplied: str | None) -> bool:
    expected = os.environ.get(env_name, "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def require_orchestrator(token: str | None) -> Principal:
    if not _matches_configured_secret("WORKFORCE_ORCHESTRATOR_TOKEN", token):
        raise AuthenticationError("valid orchestrator credential required")
    return Principal("orchestrator", "orchestrator")


def require_director(token: str | None) -> Principal:
    if not _matches_configured_secret("DIRECTOR_APPROVAL_TOKEN", token):
        raise AuthenticationError("valid Director credential required")
    return Principal("director", "director")


def authenticate_worker(token: str | None) -> Principal:
    if not token:
        raise AuthenticationError("worker credential required")
    raw = os.environ.get("WORKFORCE_WORKER_CREDENTIALS_JSON", "")
    if not raw:
        raise AuthenticationError("worker credentials are not configured")
    try:
        credentials = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise AuthenticationError("worker credential registry is invalid") from exc
    if not isinstance(credentials, dict) or not credentials:
        raise AuthenticationError("worker credential registry is empty or invalid")
    matched: Principal | None = None
    # Compare every configured token to avoid leaking which worker ID matched.
    for worker_id, entry in credentials.items():
        if not isinstance(worker_id, str) or not isinstance(entry, dict):
            raise AuthenticationError("worker credential registry has an invalid entry")
        expected = entry.get("token")
        role = entry.get("role")
        if not isinstance(expected, str) or not expected or role not in ROLES:
            raise AuthenticationError("worker credential registry has an invalid entry")
        if hmac.compare_digest(expected, token):
            matched = Principal(worker_id, role)
    if matched is None:
        raise AuthenticationError("worker credential is invalid")
    return matched
