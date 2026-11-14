"""Authenticated atomic inference-budget reservations and settlement."""
from __future__ import annotations

import json
import os
import uuid

import psycopg
from fastapi import APIRouter, Header, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel, ConfigDict, Field

from .security import AuthenticationError, authenticate_worker

router = APIRouter(prefix="/v1/tasks", tags=["agent-budget"])


def connect():
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(database_url, row_factory=dict_row)


def worker_from_token(token: str | None):
    try:
        return authenticate_worker(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReserveBody(StrictModel):
    lease_token: str = Field(min_length=32, max_length=128)
    requested_tokens: int = Field(ge=1, le=200000)


class SettleBody(StrictModel):
    lease_token: str = Field(min_length=32, max_length=128)
    reservation_id: uuid.UUID
    actual_tokens: int = Field(ge=0, le=200000)


@router.post("/{task_id}/budget/reserve")
def reserve(
    task_id: str,
    body: ReserveBody,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = worker_from_token(x_worker_token)
    reservation_id = uuid.uuid4()
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT role,lease_generation,contract_json->>'work_package_id' AS work_package_id
                 FROM wf_tasks
                WHERE task_id=%s AND role=%s AND lease_worker=%s
                  AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                  AND lease_expires_at > now()
                  AND wf_task_deadline(started_at, contract_json) > now()
                  AND state IN ('CLAIMED','RUNNING','CHECKPOINTED') FOR UPDATE""",
            (task_id, worker.role, worker.actor_id, body.lease_token),
        )
        task = cur.fetchone()
        if not task:
            raise HTTPException(status_code=409, detail="current live lease required to reserve inference budget")
        cur.execute(
            """SELECT max_model_calls,max_tokens,used_model_calls,used_tokens,
                      reserved_calls,reserved_tokens
                 FROM wf_agent_budgets WHERE work_package_id=%s AND role=%s FOR UPDATE""",
            (task["work_package_id"], worker.role),
        )
        budget = cur.fetchone()
        if not budget:
            raise HTTPException(status_code=409, detail="durable agent budget account is missing")
        calls_left = budget["max_model_calls"] - budget["used_model_calls"] - budget["reserved_calls"]
        tokens_left = budget["max_tokens"] - budget["used_tokens"] - budget["reserved_tokens"]
        if calls_left <= 0 or tokens_left < body.requested_tokens:
            raise HTTPException(status_code=429, detail="per-agent work-package inference budget exhausted")
        cur.execute(
            """INSERT INTO wf_budget_reservations(
                   reservation_id,task_id,work_package_id,role,worker_id,
                   lease_generation,lease_token_hash,reserved_tokens,state)
               VALUES (%s,%s,%s,%s,%s,%s,encode(digest(%s,'sha256'),'hex'),%s,'RESERVED')""",
            (reservation_id, task_id, task["work_package_id"], worker.role, worker.actor_id,
             task["lease_generation"], body.lease_token, body.requested_tokens),
        )
        cur.execute(
            """UPDATE wf_agent_budgets
                  SET reserved_calls=reserved_calls+1,
                      reserved_tokens=reserved_tokens+%s,updated_at=now()
                WHERE work_package_id=%s AND role=%s""",
            (body.requested_tokens, task["work_package_id"], worker.role),
        )
        return {"reservation_id": str(reservation_id), "reserved_tokens": body.requested_tokens, "remaining_calls_after_reservation": calls_left - 1, "remaining_tokens_after_reservation": tokens_left - body.requested_tokens}


@router.post("/{task_id}/budget/settle")
def settle(
    task_id: str,
    body: SettleBody,
    x_worker_token: str | None = Header(default=None, alias="X-Worker-Token"),
):
    worker = worker_from_token(x_worker_token)
    overrun = False
    with connect() as conn, conn.cursor() as cur:
        # Lock task first, then reservation: the supervisor uses the same order
        # when expiring leases and abandoning orphaned reservations.
        cur.execute(
            """SELECT lease_generation,lease_token_hash,lease_worker
                 FROM wf_tasks
                WHERE task_id=%s AND role=%s AND lease_worker=%s
                  AND lease_token_hash=encode(digest(%s,'sha256'),'hex')
                  AND lease_expires_at > now()
                  AND wf_task_deadline(started_at, contract_json) > now()
                  AND state IN ('CLAIMED','RUNNING','CHECKPOINTED')
                FOR UPDATE""",
            (task_id, worker.role, worker.actor_id, body.lease_token),
        )
        task = cur.fetchone()
        if not task:
            raise HTTPException(status_code=409, detail="current live lease required to settle inference budget")
        cur.execute(
            """SELECT work_package_id,role,worker_id,reserved_tokens,state,
                      lease_generation,lease_token_hash
                 FROM wf_budget_reservations
                WHERE reservation_id=%s AND task_id=%s FOR UPDATE""",
            (body.reservation_id, task_id),
        )
        reservation = cur.fetchone()
        if (not reservation or reservation["state"] != "RESERVED"
                or reservation["worker_id"] != worker.actor_id
                or reservation["role"] != worker.role
                or reservation["lease_generation"] != task["lease_generation"]
                or reservation["lease_token_hash"] != task["lease_token_hash"]):
            raise HTTPException(status_code=409, detail="active reservation is missing, stale, settled, or belongs to another lease")
        actual = body.actual_tokens
        overrun = actual > reservation["reserved_tokens"]
        cur.execute(
            """UPDATE wf_agent_budgets
                  SET used_model_calls=used_model_calls+1,
                      used_tokens=used_tokens+%s,
                      reserved_calls=reserved_calls-1,
                      reserved_tokens=reserved_tokens-%s,
                      updated_at=now()
                WHERE work_package_id=%s AND role=%s""",
            (actual, reservation["reserved_tokens"], reservation["work_package_id"], reservation["role"]),
        )
        cur.execute(
            """UPDATE wf_budget_reservations SET actual_tokens=%s,state=%s,settled_at=now()
                 WHERE reservation_id=%s""",
            (actual, "OVERRUN" if overrun else "SETTLED", body.reservation_id),
        )
        if overrun:
            cur.execute(
                """UPDATE wf_tasks SET state='FAILED',lease_worker=NULL,lease_token_hash=NULL,
                          lease_expires_at=NULL,updated_at=now()
                     WHERE task_id=%s AND state IN ('CLAIMED','RUNNING','CHECKPOINTED')""",
                (task_id,),
            )
            cur.execute(
                """INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json)
                   VALUES (%s,'AGENT_BUDGET_OVERRUN',%s,%s::jsonb)""",
                (task_id, worker.actor_id, json.dumps({"reserved_tokens": reservation["reserved_tokens"], "actual_tokens": actual})),
            )
    if overrun:
        raise HTTPException(status_code=409, detail="provider usage exceeded reserved budget; task stopped and overrun recorded")
    return {"status": "settled", "actual_tokens": actual}
