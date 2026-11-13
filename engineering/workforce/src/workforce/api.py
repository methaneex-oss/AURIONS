"""Small PostgreSQL-backed control-plane API. No model or GitHub credentials are exposed here."""
from __future__ import annotations

import hmac
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg
from fastapi import FastAPI, Header, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

from .domain import ContractError, TaskContract, TaskState, TransitionError, validate_transition

app = FastAPI(title="AURIONS Workforce Control Plane", version="0.1.0")
DATABASE_URL = os.environ.get("DATABASE_URL", "")


def connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


class CreateTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:12]}")
    role: str
    contract: dict[str, Any]


class ClaimTask(BaseModel):
    worker_id: str
    lease_seconds: int = Field(default=90, ge=15, le=900)


class Heartbeat(BaseModel):
    worker_id: str
    lease_token: str
    lease_seconds: int = Field(default=90, ge=15, le=900)


class Checkpoint(BaseModel):
    worker_id: str
    lease_token: str
    checkpoint_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    context_sha256: str


class Transition(BaseModel):
    target: TaskState
    actor: str
    reason: str
    director_decision_ref: str | None = None


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
def create_task(body: CreateTask):
    try:
        contract = TaskContract.from_dict(body.contract)
    except (ContractError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if body.role not in {"lead_builder", "specialist_builder", "architecture_reviewer", "code_reviewer", "negative_tester", "integration_verifier"}:
        raise HTTPException(status_code=422, detail="unknown workforce role")
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO wf_tasks(task_id, role, state, contract_json, base_commit_sha)
                       VALUES (%s, %s, 'QUEUED', %s::jsonb, %s)
                       RETURNING task_id, role, state, base_commit_sha, created_at""",
                    (body.task_id, body.role, json.dumps(body.contract), contract.base_commit_sha))
        row = cur.fetchone()
        cur.execute("INSERT INTO wf_audit_events(task_id, event_type, actor, payload_json) VALUES (%s,'TASK_CREATED','orchestrator',%s::jsonb)",
                    (body.task_id, json.dumps({"authorization_ref": contract.authorization_ref, "work_package_id": contract.work_package_id})))
        return row


@app.get("/v1/tasks")
def list_tasks():
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT task_id, role, state, base_commit_sha, created_at, updated_at FROM wf_tasks ORDER BY created_at DESC LIMIT 200")
        return cur.fetchall()


@app.post("/v1/tasks/{task_id}/claim")
def claim_task(task_id: str, body: ClaimTask):
    token = uuid.uuid4().hex
    expires = datetime.now(timezone.utc) + timedelta(seconds=body.lease_seconds)
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""UPDATE wf_tasks SET state='CLAIMED', lease_worker=%s, lease_token_hash=encode(digest(%s,'sha256'),'hex'), lease_expires_at=%s, updated_at=now()
                       WHERE task_id=%s AND state='QUEUED' RETURNING task_id, state, lease_expires_at""",
                    (body.worker_id, token, expires, task_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=409, detail="task is unavailable or not QUEUED")
        cur.execute("INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json) VALUES (%s,'TASK_CLAIMED',%s,%s::jsonb)",
                    (task_id, body.worker_id, json.dumps({"lease_expires_at": expires.isoformat()})))
        return {**row, "lease_token": token}


@app.post("/v1/tasks/{task_id}/heartbeat")
def heartbeat(task_id: str, body: Heartbeat):
    expires = datetime.now(timezone.utc) + timedelta(seconds=body.lease_seconds)
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""UPDATE wf_tasks SET lease_expires_at=%s, updated_at=now()
                       WHERE task_id=%s AND lease_worker=%s
                         AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                         AND lease_expires_at > now() AND state IN ('CLAIMED','RUNNING','CHECKPOINTED')
                       RETURNING task_id, lease_expires_at""",
                    (expires, task_id, body.worker_id, body.lease_token))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=409, detail="lease invalid, expired, or task not active")
        return row


@app.post("/v1/tasks/{task_id}/checkpoint", status_code=201)
def checkpoint(task_id: str, body: Checkpoint):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""SELECT 1 FROM wf_tasks WHERE task_id=%s AND lease_worker=%s
                       AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                       AND lease_expires_at > now() AND state IN ('RUNNING','CHECKPOINTED') FOR UPDATE""",
                    (task_id, body.worker_id, body.lease_token))
        if not cur.fetchone():
            raise HTTPException(status_code=409, detail="valid active lease required")
        cur.execute("INSERT INTO wf_checkpoints(task_id, worker_id, checkpoint_name, payload_json, context_sha256) VALUES (%s,%s,%s,%s::jsonb,%s) RETURNING checkpoint_id, created_at",
                    (task_id, body.worker_id, body.checkpoint_name, json.dumps(body.payload), body.context_sha256))
        row = cur.fetchone()
        cur.execute("UPDATE wf_tasks SET state='CHECKPOINTED', updated_at=now() WHERE task_id=%s AND state='RUNNING'", (task_id,))
        cur.execute("INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json) VALUES (%s,'CHECKPOINT_WRITTEN',%s,%s::jsonb)",
                    (task_id, body.worker_id, json.dumps({"checkpoint_id": row["checkpoint_id"], "name": body.checkpoint_name})))
        return row


@app.post("/v1/tasks/{task_id}/transition")
def transition(task_id: str, body: Transition, x_director_approval_token: str | None = Header(default=None, alias="X-Director-Approval-Token")):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT state FROM wf_tasks WHERE task_id=%s FOR UPDATE", (task_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="task not found")
        current = TaskState(row["state"])
        director_token = os.environ.get("DIRECTOR_APPROVAL_TOKEN", "")
        director_ok = (body.target == TaskState.ACCEPTED and bool(director_token)
                       and bool(x_director_approval_token)
                       and hmac.compare_digest(director_token, x_director_approval_token)
                       and bool(body.director_decision_ref))
        try:
            validate_transition(current, body.target, director_decision=director_ok)
        except TransitionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if body.target == TaskState.ACCEPTED and not director_ok:
            raise HTTPException(status_code=403, detail="valid Director approval credential and decision reference required")
        cur.execute("UPDATE wf_tasks SET state=%s, updated_at=now() WHERE task_id=%s RETURNING task_id,state,updated_at",
                    (body.target.value, task_id))
        updated = cur.fetchone()
        cur.execute("INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json) VALUES (%s,'STATE_TRANSITION',%s,%s::jsonb)",
                    (task_id, body.actor, json.dumps({"from": current.value, "to": body.target.value, "reason": body.reason, "director_decision_ref": body.director_decision_ref})))
        return updated
