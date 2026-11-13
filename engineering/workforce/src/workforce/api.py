"""Authenticated PostgreSQL-backed workforce control plane."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any

import psycopg
from fastapi import FastAPI, Header, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel, ConfigDict, Field

from .domain import ContractError, TaskContract, TaskState, TransitionError, validate_transition
from .budget_api import router as budget_router
from .security import (
    AuthenticationError, Principal, authenticate_worker,
    require_director, require_orchestrator,
)

app = FastAPI(title="AURIONS Workforce Control Plane", version="0.2.0")
app.include_router(budget_router)
DATABASE_URL = os.environ.get("DATABASE_URL", "")
def connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def _auth(call, token: str | None) -> Principal:
    try:
        return call(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateTask(StrictModel):
    task_id: str = Field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:12]}", min_length=3, max_length=100)
    role: str
    contract: dict[str, Any]


class ClaimTask(StrictModel):
    lease_seconds: int = Field(default=90, ge=15, le=900)


class Heartbeat(StrictModel):
    lease_token: str = Field(min_length=32, max_length=128)
    lease_seconds: int = Field(default=90, ge=15, le=900)


class Checkpoint(StrictModel):
    lease_token: str = Field(min_length=32, max_length=128)
    checkpoint_name: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)
    context_sha256: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    idempotency_key: str = Field(min_length=16, max_length=128)


class WorkerTransition(StrictModel):
    lease_token: str = Field(min_length=32, max_length=128)
    target: TaskState
    reason: str = Field(min_length=1, max_length=1000)
    evidence_sha256: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{64}$")
    evidence_ref: str | None = Field(default=None, min_length=1, max_length=512)


class Transition(StrictModel):
    target: TaskState
    reason: str = Field(min_length=1, max_length=1000)
    director_decision_ref: str | None = Field(default=None, max_length=300)
    evidence_sha256: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{64}$")
    evidence_ref: str | None = Field(default=None, min_length=1, max_length=512)


@app.get("/health")
def health():
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc


@app.post("/v1/tasks", status_code=201)
def create_task(
    body: CreateTask,
    x_orchestrator_token: str | None = Header(default=None, alias="X-Orchestrator-Token"),
    x_director_approval_token: str | None = Header(default=None, alias="X-Director-Approval-Token"),
):
    orchestrator = _auth(require_orchestrator, x_orchestrator_token)
    _auth(require_director, x_director_approval_token)
    try:
        contract = TaskContract.from_dict(body.contract)
    except (ContractError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if body.role not in {
        "lead_builder", "specialist_builder", "architecture_reviewer",
        "code_reviewer", "negative_tester", "integration_verifier",
    }:
        raise HTTPException(status_code=422, detail="unknown workforce role")
    builder_roles = {"lead_builder", "specialist_builder"}
    if body.role in builder_roles and not contract.permitted_paths:
        raise HTTPException(status_code=422, detail="builder tasks require at least one permitted write path")
    if body.role not in builder_roles and contract.permitted_paths:
        raise HTTPException(status_code=422, detail="review and integration roles must have an empty write scope")
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO wf_tasks(task_id, role, state, contract_json, base_commit_sha)
               VALUES (%s, %s, 'QUEUED', %s::jsonb, %s)
               RETURNING task_id, role, state, base_commit_sha, created_at""",
            (body.task_id, body.role, json.dumps(body.contract), contract.base_commit_sha),
        )
        row = cur.fetchone()
        cur.execute(
            """INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json)
               VALUES (%s,'TASK_CREATED',%s,%s::jsonb)""",
            (body.task_id, orchestrator.actor_id,
             json.dumps({"authorization_ref": contract.authorization_ref, "work_package_id": contract.work_package_id})),
        )
        return row


@app.get("/v1/tasks")
def list_tasks(x_orchestrator_token: str | None = Header(default=None, alias="X-Orchestrator-Token")):
    _auth(require_orchestrator, x_orchestrator_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT task_id, role, state, base_commit_sha, attempt_count,
                      max_attempts, lease_expires_at, retry_after, created_at, updated_at
               FROM wf_tasks ORDER BY created_at DESC LIMIT 200"""
        )
        return cur.fetchall()


@app.get("/v1/tasks/{task_id}")
def get_task(
    task_id: str,
    x_orchestrator_token: str | None = Header(default=None, alias="X-Orchestrator-Token"),
):
    _auth(require_orchestrator, x_orchestrator_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT task_id,role,state,contract_json,base_commit_sha,
                      attempt_count,max_attempts,lease_worker,lease_generation,
                      lease_expires_at,retry_after,created_at,updated_at
                 FROM wf_tasks WHERE task_id=%s""",
            (task_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="task not found")
        return row


@app.get("/v1/tasks/{task_id}/evidence")
def list_task_evidence(
    task_id: str,
    x_orchestrator_token: str | None = Header(default=None, alias="X-Orchestrator-Token"),
):
    _auth(require_orchestrator, x_orchestrator_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT stage,sha256,evidence_ref,actor,attempt_count,created_at
                 FROM wf_task_evidence WHERE task_id=%s
                ORDER BY attempt_count,created_at,evidence_id""",
            (task_id,),
        )
        return cur.fetchall()


@app.post("/v1/tasks/{task_id}/claim")
def claim_task(
    task_id: str,
    body: ClaimTask,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = _auth(authenticate_worker, x_worker_token)
    token = uuid.uuid4().hex + uuid.uuid4().hex
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE wf_tasks
                  SET state='CLAIMED', started_at=COALESCE(started_at, now()), lease_worker=%s,
                      lease_token_hash=encode(digest(%s,'sha256'),'hex'),
                      lease_generation=lease_generation+1,
                      lease_expires_at=now() + (%s * interval '1 second'), attempt_count=attempt_count+1,
                      retry_after=NULL, updated_at=now()
                WHERE task_id=%s AND role=%s
                  AND state IN ('QUEUED','RETRY_WAIT')
                  AND (retry_after IS NULL OR retry_after <= now())
                  AND attempt_count < max_attempts
                  AND wf_task_deadline(started_at, contract_json) > now()
                  AND (state <> 'QUEUED' OR started_at IS NOT NULL OR created_at + interval '10 minutes' > now())
             RETURNING task_id, role, state, lease_generation, attempt_count, lease_expires_at""",
            (worker.actor_id, token, body.lease_seconds, task_id, worker.role),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=409, detail="task unavailable, not yet retryable, expired, or assigned to another role")
        cur.execute(
            """INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json)
               VALUES (%s,'TASK_CLAIMED',%s,%s::jsonb)""",
            (task_id, worker.actor_id,
             json.dumps({"role": worker.role, "lease_generation": row["lease_generation"], "attempt": row["attempt_count"], "lease_expires_at": row["lease_expires_at"].isoformat()})),
        )
        return {**row, "worker_id": worker.actor_id, "lease_token": token}


@app.post("/v1/tasks/{task_id}/heartbeat")
def heartbeat(
    task_id: str,
    body: Heartbeat,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = _auth(authenticate_worker, x_worker_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE wf_tasks SET lease_expires_at=now() + (%s * interval '1 second'), updated_at=now()
                 WHERE task_id=%s AND role=%s AND lease_worker=%s
                   AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                   AND lease_expires_at > now()
                   AND wf_task_deadline(started_at, contract_json) > now()
                   AND state IN ('CLAIMED','RUNNING','CHECKPOINTED')
             RETURNING task_id, lease_generation, lease_expires_at""",
            (body.lease_seconds, task_id, worker.role, worker.actor_id, body.lease_token),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=409, detail="lease invalid, expired, stale, or task deadline reached")
        return row


@app.post("/v1/tasks/{task_id}/start")
def start_task(
    task_id: str,
    body: Heartbeat,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = _auth(authenticate_worker, x_worker_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE wf_tasks SET state='RUNNING', started_at=COALESCE(started_at, now()), lease_expires_at=GREATEST(lease_expires_at, now() + (%s * interval '1 second')), updated_at=now()
                 WHERE task_id=%s AND role=%s AND lease_worker=%s
                   AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                   AND lease_expires_at > now()
                   AND wf_task_deadline(started_at, contract_json) > now()
                   AND state IN ('CLAIMED','CHECKPOINTED','RUNNING')
             RETURNING task_id,state,lease_generation""",
            (body.lease_seconds, task_id, worker.role, worker.actor_id, body.lease_token),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=409, detail="valid current lease required to start or resume task")
        cur.execute(
            "INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json) VALUES (%s,'TASK_STARTED',%s,jsonb_build_object('lease_generation',%s))",
            (task_id, worker.actor_id, row["lease_generation"]),
        )
        return row


@app.post("/v1/tasks/{task_id}/checkpoint", status_code=201)
def checkpoint(
    task_id: str,
    body: Checkpoint,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = _auth(authenticate_worker, x_worker_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT lease_generation FROM wf_tasks
                 WHERE task_id=%s AND role=%s AND lease_worker=%s
                   AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                   AND lease_expires_at > now()
                   AND wf_task_deadline(started_at, contract_json) > now()
                   AND state IN ('RUNNING','CHECKPOINTED') FOR UPDATE""",
            (task_id, worker.role, worker.actor_id, body.lease_token),
        )
        lease = cur.fetchone()
        if not lease:
            raise HTTPException(status_code=409, detail="valid current lease required; stale workers cannot checkpoint")
        cur.execute(
            """INSERT INTO wf_checkpoints(task_id,worker_id,checkpoint_name,payload_json,context_sha256,idempotency_key)
               VALUES (%s,%s,%s,%s::jsonb,%s,%s)
               ON CONFLICT (task_id,idempotency_key) WHERE idempotency_key IS NOT NULL DO NOTHING
               RETURNING checkpoint_id,created_at""",
            (task_id, worker.actor_id, body.checkpoint_name, json.dumps(body.payload), body.context_sha256, body.idempotency_key),
        )
        row = cur.fetchone()
        replay = row is None
        if replay:
            cur.execute(
                "SELECT checkpoint_id,created_at,worker_id,checkpoint_name,context_sha256,payload_json FROM wf_checkpoints WHERE task_id=%s AND idempotency_key=%s",
                (task_id, body.idempotency_key),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=409, detail="idempotency conflict")
            if (row["worker_id"] != worker.actor_id or row["checkpoint_name"] != body.checkpoint_name
                    or row["context_sha256"].strip() != body.context_sha256
                    or row["payload_json"] != body.payload):
                raise HTTPException(status_code=409, detail="idempotency key was already used for different checkpoint content")
        else:
            cur.execute("UPDATE wf_tasks SET state='CHECKPOINTED',updated_at=now() WHERE task_id=%s", (task_id,))
            cur.execute(
                """INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json)
                   VALUES (%s,'CHECKPOINT_WRITTEN',%s,%s::jsonb)""",
                (task_id, worker.actor_id,
                 json.dumps({"checkpoint_id": row["checkpoint_id"], "name": body.checkpoint_name, "lease_generation": lease["lease_generation"]})),
            )
        return {"checkpoint_id": row["checkpoint_id"], "created_at": row["created_at"], "idempotent_replay": replay}


@app.get("/v1/tasks/{task_id}/checkpoints/latest")
def latest_checkpoint(
    task_id: str,
    lease_token: str = Header(..., alias="X-Worker-Lease-Token"),
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = _auth(authenticate_worker, x_worker_token)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT 1 FROM wf_tasks
                 WHERE task_id=%s AND role=%s AND lease_worker=%s
                   AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                   AND lease_expires_at > now()
                   AND wf_task_deadline(started_at, contract_json) > now()
                   AND state IN ('CLAIMED','RUNNING','CHECKPOINTED')""",
            (task_id, worker.role, worker.actor_id, lease_token),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=409, detail="valid current lease required to restore checkpoints")
        cur.execute(
            """SELECT checkpoint_id,worker_id,checkpoint_name,payload_json,context_sha256,created_at
                 FROM wf_checkpoints WHERE task_id=%s
                ORDER BY created_at DESC, checkpoint_id DESC LIMIT 1""",
            (task_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="no checkpoint exists for this task")
        return row


@app.post("/v1/tasks/{task_id}/worker-transition")
def worker_transition(
    task_id: str,
    body: WorkerTransition,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = _auth(authenticate_worker, x_worker_token)
    if body.target not in {TaskState.CANDIDATE_READY, TaskState.BLOCKED, TaskState.FAILED, TaskState.CANCELLED}:
        raise HTTPException(status_code=403, detail="worker target is not permitted")
    if body.target == TaskState.CANDIDATE_READY and (not body.evidence_sha256 or not body.evidence_ref):
        raise HTTPException(status_code=422, detail="completed worker output requires an evidence SHA-256 and artifact reference")
    if body.target != TaskState.CANDIDATE_READY and (body.evidence_sha256 or body.evidence_ref):
        raise HTTPException(status_code=422, detail="worker evidence is only valid when publishing candidate output")
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT state,lease_generation,attempt_count FROM wf_tasks
                 WHERE task_id=%s AND role=%s AND lease_worker=%s
                   AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                   AND lease_expires_at > now()
                   AND wf_task_deadline(started_at, contract_json) > now() FOR UPDATE""",
            (task_id, worker.role, worker.actor_id, body.lease_token),
        )
        row = cur.fetchone()
        if not row:
            cur.execute(
                "SELECT state,attempt_count FROM wf_tasks WHERE task_id=%s AND role=%s FOR UPDATE",
                (task_id, worker.role),
            )
            current_task = cur.fetchone()
            if body.target == TaskState.CANDIDATE_READY and current_task and current_task["state"] == TaskState.CANDIDATE_READY.value:
                cur.execute(
                    """SELECT 1 FROM wf_task_evidence
                         WHERE task_id=%s AND stage='WORKER_OUTPUT' AND actor=%s
                           AND attempt_count=%s AND sha256=%s AND evidence_ref=%s""",
                    (task_id, worker.actor_id, current_task["attempt_count"], body.evidence_sha256.lower(), body.evidence_ref),
                )
                if cur.fetchone():
                    return {"task_id": task_id, "state": TaskState.CANDIDATE_READY.value, "idempotent_replay": True}
            raise HTTPException(status_code=409, detail="valid current lease required")
        current = TaskState(row["state"])
        if body.target == TaskState.CANDIDATE_READY and current not in {TaskState.RUNNING, TaskState.CHECKPOINTED}:
            raise HTTPException(status_code=409, detail="only a running worker can publish a candidate")
        try:
            validate_transition(current, body.target)
        except TransitionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if body.target == TaskState.CANDIDATE_READY:
            cur.execute(
                """INSERT INTO wf_task_evidence(task_id,stage,sha256,evidence_ref,actor,attempt_count)
                   VALUES (%s,'WORKER_OUTPUT',%s,%s,%s,%s)""",
                (task_id, body.evidence_sha256.lower(), body.evidence_ref, worker.actor_id, row["attempt_count"]),
            )
        cur.execute(
            """UPDATE wf_tasks SET state=%s,lease_worker=NULL,lease_token_hash=NULL,
                      lease_expires_at=NULL,updated_at=now()
                 WHERE task_id=%s RETURNING task_id,state,updated_at""",
            (body.target.value, task_id),
        )
        updated = cur.fetchone()
        cur.execute(
            """INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json)
               VALUES (%s,'WORKER_TASK_TRANSITION',%s,%s::jsonb)""",
            (task_id, worker.actor_id, json.dumps({"from": current.value, "to": body.target.value, "reason": body.reason, "evidence_sha256": body.evidence_sha256, "evidence_ref": body.evidence_ref})),
        )
        return updated


@app.post("/v1/tasks/{task_id}/transition")
def transition(
    task_id: str,
    body: Transition,
    x_orchestrator_token: str | None = Header(default=None, alias="X-Orchestrator-Token"),
    x_director_approval_token: str | None = Header(default=None, alias="X-Director-Approval-Token"),
):
    if body.target == TaskState.ACCEPTED:
        principal = _auth(require_director, x_director_approval_token)
        if not body.director_decision_ref:
            raise HTTPException(status_code=422, detail="Director decision reference is mandatory")
        if not body.evidence_sha256 or not body.evidence_ref:
            raise HTTPException(status_code=422, detail="Director acceptance requires the integrated evidence SHA-256 and artifact reference")
    else:
        principal = _auth(require_orchestrator, x_orchestrator_token)
        if body.director_decision_ref:
            raise HTTPException(status_code=422, detail="Director decision reference is only valid for acceptance")
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT state,attempt_count,
                      CASE WHEN state IN ('CLAIMED','RUNNING','CHECKPOINTED','RETRY_WAIT')
                                  OR (state='QUEUED' AND started_at IS NOT NULL)
                           THEN wf_task_deadline(started_at, contract_json) > now()
                           ELSE wf_task_absolute_deadline(contract_json) > now()
                      END AS before_deadline
                 FROM wf_tasks WHERE task_id=%s FOR UPDATE""",
            (task_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="task not found")
        if not row["before_deadline"]:
            raise HTTPException(status_code=409, detail="task deadline has passed; further transitions are forbidden")
        current = TaskState(row["state"])
        if principal.role == "orchestrator":
            replay_stages = {
                TaskState.TESTING: "CANDIDATE",
                TaskState.REVIEWING: "TEST",
                TaskState.INTEGRATION: "REVIEW_BUNDLE",
                TaskState.AWAITING_DIRECTOR: "INTEGRATED",
            }
            if current == body.target and body.target in replay_stages:
                if not body.evidence_sha256 or not body.evidence_ref:
                    raise HTTPException(status_code=422, detail="idempotent lifecycle replay requires the original evidence")
                cur.execute(
                    """SELECT 1 FROM wf_task_evidence
                         WHERE task_id=%s AND stage=%s AND attempt_count=%s
                           AND sha256=%s AND evidence_ref=%s""",
                    (task_id, replay_stages[body.target], row["attempt_count"],
                     body.evidence_sha256.lower(), body.evidence_ref),
                )
                if cur.fetchone():
                    return {"task_id": task_id, "state": current.value, "idempotent_replay": True}
                raise HTTPException(status_code=409, detail="lifecycle state already advanced with different evidence")
            allowed = {
                TaskState.QUEUED: {TaskState.BLOCKED, TaskState.CANCELLED},
                TaskState.CLAIMED: {TaskState.BLOCKED, TaskState.FAILED, TaskState.CANCELLED},
                TaskState.RUNNING: {TaskState.BLOCKED, TaskState.FAILED, TaskState.CANCELLED},
                TaskState.CHECKPOINTED: {TaskState.BLOCKED, TaskState.FAILED, TaskState.CANCELLED},
                TaskState.CANDIDATE_READY: {TaskState.TESTING, TaskState.REJECTED, TaskState.BLOCKED},
                TaskState.TESTING: {TaskState.REVIEWING, TaskState.REJECTED, TaskState.BLOCKED, TaskState.FAILED},
                TaskState.REVIEWING: {TaskState.INTEGRATION, TaskState.REJECTED, TaskState.BLOCKED},
                TaskState.INTEGRATION: {TaskState.AWAITING_DIRECTOR, TaskState.REJECTED, TaskState.BLOCKED},
                TaskState.AWAITING_DIRECTOR: {TaskState.REJECTED, TaskState.BLOCKED},
                TaskState.BLOCKED: {TaskState.QUEUED, TaskState.CANCELLED},
                TaskState.RETRY_WAIT: {TaskState.QUEUED, TaskState.FAILED, TaskState.CANCELLED},
            }
            if body.target not in allowed.get(current, set()):
                raise HTTPException(status_code=403, detail="orchestrator transition is outside its lifecycle authority")
            evidence_stages = {
                (TaskState.CANDIDATE_READY, TaskState.TESTING): "CANDIDATE",
                (TaskState.TESTING, TaskState.REVIEWING): "TEST",
                (TaskState.REVIEWING, TaskState.INTEGRATION): "REVIEW_BUNDLE",
                (TaskState.INTEGRATION, TaskState.AWAITING_DIRECTOR): "INTEGRATED",
            }
            evidence_stage = evidence_stages.get((current, body.target))
            if evidence_stage and (not body.evidence_sha256 or not body.evidence_ref):
                raise HTTPException(status_code=422, detail="lifecycle advancement requires an evidence digest and artifact reference")
            if not evidence_stage and (body.evidence_sha256 or body.evidence_ref):
                raise HTTPException(status_code=422, detail="evidence may only be attached to a defined lifecycle gate")
        elif body.evidence_sha256 and principal.role == "director" and body.target != TaskState.ACCEPTED:
            raise HTTPException(status_code=422, detail="Director evidence is only accepted with final acceptance")
        if principal.role == "director":
            cur.execute(
                "SELECT sha256,evidence_ref FROM wf_task_evidence WHERE task_id=%s AND stage='INTEGRATED' AND attempt_count=%s",
                (task_id, row["attempt_count"]),
            )
            integrated = cur.fetchone()
            if (not integrated or integrated["sha256"].strip().lower() != body.evidence_sha256.lower()
                    or integrated["evidence_ref"] != body.evidence_ref):
                raise HTTPException(status_code=409, detail="Director acceptance must reference the exact recorded integrated evidence")
        elif evidence_stage:
            cur.execute(
                """INSERT INTO wf_task_evidence(task_id,stage,sha256,evidence_ref,actor,attempt_count)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                (task_id, evidence_stage, body.evidence_sha256.lower(), body.evidence_ref, principal.actor_id, row["attempt_count"]),
            )
        try:
            validate_transition(current, body.target, director_decision=(principal.role == "director"))
        except TransitionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        cur.execute(
            """UPDATE wf_tasks SET state=%s,
                      lease_worker=CASE WHEN %s IN ('CLAIMED','RUNNING','CHECKPOINTED') THEN lease_worker ELSE NULL END,
                      lease_token_hash=CASE WHEN %s IN ('CLAIMED','RUNNING','CHECKPOINTED') THEN lease_token_hash ELSE NULL END,
                      lease_expires_at=CASE WHEN %s IN ('CLAIMED','RUNNING','CHECKPOINTED') THEN lease_expires_at ELSE NULL END,
                      updated_at=now()
                 WHERE task_id=%s RETURNING task_id,state,updated_at""",
            (body.target.value, body.target.value, body.target.value, body.target.value, task_id),
        )
        updated = cur.fetchone()
        cur.execute(
            """INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json)
               VALUES (%s,'STATE_TRANSITION',%s,%s::jsonb)""",
            (task_id, principal.actor_id,
             json.dumps({"from": current.value, "to": body.target.value, "reason": body.reason, "director_decision_ref": body.director_decision_ref, "evidence_sha256": body.evidence_sha256, "evidence_ref": body.evidence_ref})),
        )
        return updated


@app.post("/v1/maintenance/recover")
def recover_expired_tasks(x_orchestrator_token: str | None = Header(default=None, alias="X-Orchestrator-Token")):
    _auth(require_orchestrator, x_orchestrator_token)
    from .supervisor import recover_once
    with connect() as conn:
        return recover_once(conn)
