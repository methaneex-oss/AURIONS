"""Deterministic task contracts and lifecycle rules for the workforce control plane."""
from __future__ import annotations

from dataclasses import dataclass
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
    TaskState.CLAIMED: frozenset({TaskState.RUNNING, TaskState.RETRY_WAIT, TaskState.FAILED, TaskState.CANCELLED}),
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
        required = (
            "work_package_id", "authorization_ref", "objective", "base_commit_sha",
            "permitted_paths", "prohibited_paths", "canonical_sources",
            "acceptance_criteria", "test_plan", "review_plan",
            "max_model_calls", "max_tokens", "max_duration_minutes", "stop_conditions",
        )
        missing = [key for key in required if key not in value or value[key] in (None, "", [])]
        if missing:
            raise ContractError(f"missing mandatory task contract fields: {', '.join(missing)}")
        if value["authorization_ref"].strip().lower() in {"none", "tbd", "unset"}:
            raise ContractError("an explicit authorization reference is required")
        sha = value["base_commit_sha"]
        if len(sha) != 40 or any(c not in "0123456789abcdefABCDEF" for c in sha):
            raise ContractError("base_commit_sha must be a full 40-character Git commit SHA")
        for key in ("max_model_calls", "max_tokens", "max_duration_minutes"):
            if not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] <= 0:
                raise ContractError(f"{key} must be a positive integer")
        for key in ("permitted_paths", "prohibited_paths", "canonical_sources", "acceptance_criteria", "test_plan", "review_plan", "stop_conditions"):
            if not isinstance(value[key], list) or not all(isinstance(item, str) and item.strip() for item in value[key]):
                raise ContractError(f"{key} must be a non-empty-string list")
        if not value["permitted_paths"]:
            raise ContractError("at least one permitted path is required")
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
