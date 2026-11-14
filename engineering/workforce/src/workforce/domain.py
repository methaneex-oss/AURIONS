"""Deterministic task contracts and lifecycle rules for the workforce control plane."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class TaskState(StrEnum):
    QUEUED = "QUEUED"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    CHECKPOINTED = "CHECKPOINTED"
    CANDIDATE_READY = "CANDIDATE_READY"
    TESTING = "TESTING"
    REVIEWING = "REVIEWING"
    INTEGRATION = "INTEGRATION"
    AWAITING_DIRECTOR = "AWAITING_DIRECTOR"
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"
    RETRY_WAIT = "RETRY_WAIT"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


TRANSITIONS: dict[TaskState, frozenset[TaskState]] = {
    TaskState.QUEUED: frozenset({TaskState.CLAIMED, TaskState.BLOCKED, TaskState.CANCELLED}),
    TaskState.CLAIMED: frozenset({TaskState.RUNNING, TaskState.BLOCKED, TaskState.RETRY_WAIT, TaskState.FAILED, TaskState.CANCELLED}),
    TaskState.RUNNING: frozenset({TaskState.CHECKPOINTED, TaskState.CANDIDATE_READY, TaskState.BLOCKED, TaskState.RETRY_WAIT, TaskState.FAILED, TaskState.CANCELLED}),
    TaskState.CHECKPOINTED: frozenset({TaskState.RUNNING, TaskState.CANDIDATE_READY, TaskState.BLOCKED, TaskState.RETRY_WAIT, TaskState.FAILED, TaskState.CANCELLED}),
    TaskState.CANDIDATE_READY: frozenset({TaskState.TESTING, TaskState.REJECTED, TaskState.BLOCKED}),
    TaskState.TESTING: frozenset({TaskState.REVIEWING, TaskState.REJECTED, TaskState.BLOCKED, TaskState.FAILED}),
    TaskState.REVIEWING: frozenset({TaskState.INTEGRATION, TaskState.REJECTED, TaskState.BLOCKED}),
    TaskState.INTEGRATION: frozenset({TaskState.AWAITING_DIRECTOR, TaskState.REJECTED, TaskState.BLOCKED}),
    TaskState.AWAITING_DIRECTOR: frozenset({TaskState.ACCEPTED, TaskState.REJECTED, TaskState.BLOCKED}),
    TaskState.BLOCKED: frozenset({TaskState.QUEUED, TaskState.CANCELLED}),
    TaskState.RETRY_WAIT: frozenset({TaskState.QUEUED, TaskState.CLAIMED, TaskState.FAILED, TaskState.CANCELLED}),
    TaskState.FAILED: frozenset(), TaskState.REJECTED: frozenset(),
    TaskState.CANCELLED: frozenset(), TaskState.ACCEPTED: frozenset(),
}


class ContractError(ValueError):
    pass


class TransitionError(ValueError):
    pass


@dataclass(frozen=True)
class TaskContract:
    work_package_id: str
    authorization_ref: str
    objective: str
    base_commit_sha: str
    permitted_paths: tuple[str, ...]
    prohibited_paths: tuple[str, ...]
    canonical_sources: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    test_plan: tuple[str, ...]
    review_plan: tuple[str, ...]
    max_model_calls: int
    max_tokens: int
    max_duration_minutes: int
    deadline: str = "UNSET"
    stop_conditions: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TaskContract":
        if not isinstance(value, dict):
            raise ContractError("task contract must be an object")
        required = (
            "work_package_id", "authorization_ref", "objective", "base_commit_sha",
            "prohibited_paths", "canonical_sources",
            "acceptance_criteria", "test_plan", "review_plan",
            "max_model_calls", "max_tokens", "max_duration_minutes", "stop_conditions",
        )
        allowed_fields = set(cls.__dataclass_fields__)
        unknown = sorted(set(value) - allowed_fields)
        if unknown:
            raise ContractError(f"unknown task contract fields: {', '.join(unknown)}")
        missing = [key for key in required if key not in value or value[key] in (None, "", [])]
        if missing:
            raise ContractError(f"missing mandatory task contract fields: {', '.join(missing)}")
        deadline = value.get("deadline", "UNSET")
        if not isinstance(deadline, str):
            raise ContractError("deadline must be an ISO-8601 timestamp with timezone or UNSET")
        if deadline != "UNSET":
            try:
                parsed_deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContractError("deadline must be an ISO-8601 timestamp with timezone or UNSET") from exc
            if parsed_deadline.tzinfo is None or parsed_deadline.utcoffset() is None:
                raise ContractError("deadline must include an explicit timezone offset")
        for key in ("work_package_id", "authorization_ref", "objective"):
            if not isinstance(value[key], str) or not value[key].strip():
                raise ContractError(f"{key} must be a non-empty string")
        if value["authorization_ref"].strip().lower() in {"none", "tbd", "unset"} or value["authorization_ref"].strip().upper().startswith("REPLACE_"):
            raise ContractError("an explicit non-placeholder authorization reference is required")
        if value["work_package_id"].strip().upper().startswith("REPLACE_"):
            raise ContractError("work_package_id must not be a template placeholder")
        sha = value["base_commit_sha"]
        if not isinstance(sha, str):
            raise ContractError("base_commit_sha must be a string")
        if len(sha) != 40 or any(c not in "0123456789abcdefABCDEF" for c in sha) or set(sha) == {"0"}:
            raise ContractError("base_commit_sha must be a real full 40-character Git commit SHA")
        budget_ceilings = {"max_model_calls": 100, "max_tokens": 200000, "max_duration_minutes": 360}
        for key, ceiling in budget_ceilings.items():
            if not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] <= 0 or value[key] > ceiling:
                raise ContractError(f"{key} must be a positive integer no greater than {ceiling}")
        if "permitted_paths" not in value or not isinstance(value["permitted_paths"], list) or not all(
            isinstance(item, str) and item.strip() for item in value["permitted_paths"]
        ):
            raise ContractError("permitted_paths must be a list of non-empty strings (empty only for read-only roles)")
        for key in ("prohibited_paths", "canonical_sources", "acceptance_criteria", "test_plan", "review_plan", "stop_conditions"):
            if not isinstance(value[key], list) or not value[key] or not all(isinstance(item, str) and item.strip() for item in value[key]):
                raise ContractError(f"{key} must be a non-empty-string list")
        return cls(**{k: tuple(v) if isinstance(v, list) else v for k, v in value.items() if k in cls.__dataclass_fields__})


def validate_transition(current: TaskState, target: TaskState, *, director_decision: bool = False) -> None:
    if target not in TRANSITIONS[current]:
        raise TransitionError(f"invalid task transition: {current.value} -> {target.value}")
    if target == TaskState.ACCEPTED and not director_decision:
        raise TransitionError("only an explicit Director decision can accept a task")


def path_is_permitted(path: str, permitted: tuple[str, ...], prohibited: tuple[str, ...]) -> bool:
    """Conservative, platform-independent prefix policy; callers resolve filesystem paths separately."""
    raw = path.replace(chr(92), "/")
    if not raw or raw.startswith("/") or ":" in raw.split("/")[0]:
        return False
    normalized = raw.rstrip("/")
    parts = normalized.split("/")
    if not normalized or any(part in {"", ".", ".."} for part in parts):
        return False

    def matches(candidate: str, prefix: str) -> bool:
        clean = prefix.replace(chr(92), "/").strip("/")
        if not clean or clean.startswith("/") or ":" in clean.split("/")[0]:
            return False
        if any(part in {"", ".", ".."} for part in clean.split("/")):
            return False
        return candidate == clean or candidate.startswith(clean + "/")

    if any(matches(normalized, prefix) for prefix in prohibited):
        return False
    return any(matches(normalized, prefix) for prefix in permitted)
