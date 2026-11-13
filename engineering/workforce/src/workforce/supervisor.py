"""Durable lease recovery and deadline enforcement loop."""
from __future__ import annotations

import logging
import os
import signal
import time

import psycopg
from psycopg.rows import dict_row

LOG = logging.getLogger("workforce.supervisor")
STOP = False


def _stop(_signum, _frame):
    global STOP
    STOP = True


def recover_once(conn) -> dict[str, int]:
    """Expire leases and enforce absolute task deadlines in one DB transaction."""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE wf_tasks
               SET state = CASE
                     WHEN created_at + make_interval(mins => (contract_json->>'max_duration_minutes')::int) <= now()
                       THEN 'FAILED'
                     WHEN attempt_count >= max_attempts THEN 'FAILED'
                     ELSE 'RETRY_WAIT'
                   END,
                   lease_worker = NULL,
                   lease_token_hash = NULL,
                   lease_expires_at = NULL,
                   retry_after = CASE
                     WHEN created_at + make_interval(mins => (contract_json->>'max_duration_minutes')::int) <= now()
                       OR attempt_count >= max_attempts THEN NULL
                     ELSE now() + interval '30 seconds'
                   END,
                   updated_at = now()
             WHERE state IN ('CLAIMED','RUNNING','CHECKPOINTED')
               AND lease_expires_at <= now()
            RETURNING task_id, state
        """)
        expired = cur.fetchall()
        for row in expired:
            cur.execute(
                "INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json) VALUES (%s,'LEASE_EXPIRED','supervisor',jsonb_build_object('resulting_state',%s))",
                (row["task_id"], row["state"]),
            )
        cur.execute("""
            UPDATE wf_tasks
               SET state='FAILED', lease_worker=NULL, lease_token_hash=NULL,
                   lease_expires_at=NULL, retry_after=NULL, updated_at=now()
             WHERE state IN ('QUEUED','RETRY_WAIT','CLAIMED','RUNNING','CHECKPOINTED','CANDIDATE_READY','TESTING','REVIEWING','INTEGRATION','AWAITING_DIRECTOR','BLOCKED')
               AND created_at + make_interval(mins => (contract_json->>'max_duration_minutes')::int) <= now()
            RETURNING task_id
        """)
        overdue = cur.fetchall()
        for row in overdue:
            cur.execute(
                "INSERT INTO wf_audit_events(task_id,event_type,actor,payload_json) VALUES (%s,'DEADLINE_EXCEEDED','supervisor',jsonb_build_object('enforced',true))",
                (row["task_id"],),
            )
    # A provider call may have completed just before a worker crash. Its usage is
    # unknowable if settlement never arrived, so charge the full reservation rather
    # than releasing it and risking budget reuse/double spending.
    with conn.cursor() as cur:
        cur.execute("""
            WITH abandoned AS (
                UPDATE wf_budget_reservations r
                   SET state='ABANDONED', actual_tokens=r.reserved_tokens, settled_at=now()
                  FROM wf_tasks t
                 WHERE r.task_id=t.task_id AND r.state='RESERVED'
                   AND (
                       t.lease_generation <> r.lease_generation
                       OR t.state NOT IN ('CLAIMED','RUNNING','CHECKPOINTED')
                       OR t.lease_expires_at IS NULL OR t.lease_expires_at <= now()
                       OR t.created_at + make_interval(mins => (t.contract_json->>'max_duration_minutes')::int) <= now()
                   )
                RETURNING r.work_package_id,r.role,r.reserved_tokens
            ),
            totals AS (
                SELECT work_package_id,role,count(*)::int AS calls,sum(reserved_tokens)::bigint AS tokens
                  FROM abandoned GROUP BY work_package_id,role
            )
            UPDATE wf_agent_budgets b
               SET used_model_calls=b.used_model_calls+totals.calls,
                   used_tokens=b.used_tokens+totals.tokens,
                   reserved_calls=b.reserved_calls-totals.calls,
                   reserved_tokens=b.reserved_tokens-totals.tokens,
                   updated_at=now()
              FROM totals
             WHERE b.work_package_id=totals.work_package_id AND b.role=totals.role
            RETURNING b.work_package_id,b.role
        """)
        abandoned_budget = cur.fetchall()
    return {"expired_leases": len(expired), "deadline_stops": len(overdue), "abandoned_budget_accounts": len(abandoned_budget)}


def main() -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")
    interval = max(2, int(os.environ.get("WORKFORCE_SUPERVISOR_INTERVAL_SECONDS", "5")))
    while not STOP:
        try:
            with psycopg.connect(database_url, row_factory=dict_row) as conn:
                result = recover_once(conn)
            if any(result.values()):
                LOG.warning("recovery actions: %s", result)
        except Exception:
            LOG.exception("supervisor cycle failed; next cycle will retry")
        for _ in range(interval * 10):
            if STOP:
                break
            time.sleep(0.1)


if __name__ == "__main__":
    main()
