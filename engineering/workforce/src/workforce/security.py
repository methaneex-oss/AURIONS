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
    return bool(expected and supplied and len(expected) >= 32 and hmac.compare_digest(expected, supplied))


def _cross_role_collision(env_name: str, supplied: str) -> bool:
    for other_name in ("DIRECTOR_APPROVAL_TOKEN", "WORKFORCE_ORCHESTRATOR_TOKEN"):
        if other_name == env_name:
            continue
        other = os.environ.get(other_name, "")
        if other and hmac.compare_digest(other, supplied):
            return True
    raw = os.environ.get("WORKFORCE_WORKER_CREDENTIALS_JSON", "")
    if not raw:
        return False
    try:
        registry = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return True
    if not isinstance(registry, dict):
        return True
    for entry in registry.values():
        if not isinstance(entry, dict) or not isinstance(entry.get("token"), str):
            return True
        if hmac.compare_digest(entry["token"], supplied):
            return True
    return False


def require_orchestrator(token: str | None) -> Principal:
    if not _matches_configured_secret("WORKFORCE_ORCHESTRATOR_TOKEN", token):
        raise AuthenticationError("valid orchestrator credential required")
    if _cross_role_collision("WORKFORCE_ORCHESTRATOR_TOKEN", token):
        raise AuthenticationError("orchestrator credential must be unique to that authority")
    return Principal("orchestrator", "orchestrator")


def require_director(token: str | None) -> Principal:
    if not _matches_configured_secret("DIRECTOR_APPROVAL_TOKEN", token):
        raise AuthenticationError("valid Director credential required")
    if _cross_role_collision("DIRECTOR_APPROVAL_TOKEN", token):
        raise AuthenticationError("Director credential must be unique to that authority")
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
    seen_tokens: set[str] = set()
    # Reject ambiguous registries and compare every configured token.
    for worker_id, entry in credentials.items():
        if not isinstance(worker_id, str) or not isinstance(entry, dict):
            raise AuthenticationError("worker credential registry has an invalid entry")
        expected = entry.get("token")
        role = entry.get("role")
        if not isinstance(expected, str) or len(expected) < 32 or not isinstance(role, str) or role not in ROLES or not worker_id:
            raise AuthenticationError("worker credential registry has an invalid entry")
        if expected in seen_tokens:
            raise AuthenticationError("worker credential registry contains duplicate tokens")
        seen_tokens.add(expected)
        if hmac.compare_digest(expected, token):
            matched = Principal(worker_id, role)
    if matched is None:
        raise AuthenticationError("worker credential is invalid")
    for privileged_name in ("DIRECTOR_APPROVAL_TOKEN", "WORKFORCE_ORCHESTRATOR_TOKEN"):
        privileged = os.environ.get(privileged_name, "")
        if privileged and hmac.compare_digest(privileged, token):
            raise AuthenticationError("worker credential must not be shared with Director or orchestrator authority")
    return matched
