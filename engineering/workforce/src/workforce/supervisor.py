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
    return {"expired_leases": len(expired), "deadline_stops": len(overdue)}


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
