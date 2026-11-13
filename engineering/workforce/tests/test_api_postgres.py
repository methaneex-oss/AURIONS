"""PostgreSQL-backed API integration tests. Run with migrations applied and test credentials set."""
from __future__ import annotations

import json
import os
import uuid
import unittest

import psycopg
from fastapi.testclient import TestClient

from workforce.api import app

DB = os.environ.get("DATABASE_URL", "")
DIRECTOR = os.environ.get("DIRECTOR_APPROVAL_TOKEN", "")
ORCHESTRATOR = os.environ.get("WORKFORCE_ORCHESTRATOR_TOKEN", "")
REGISTRY = json.loads(os.environ.get("WORKFORCE_WORKER_CREDENTIALS_JSON", "{}"))
BUILDER = REGISTRY.get("builder-01", {}).get("token", "")
REVIEWER = REGISTRY.get("reviewer-01", {}).get("token", "")


def contract():
    return {
        "work_package_id": "WF-TEST",
        "authorization_ref": "test-director-authorization",
        "objective": "Exercise the control-plane API",
        "base_commit_sha": "a" * 40,
        "permitted_paths": ["engineering/workforce/src"],
        "prohibited_paths": ["docs/governance", "src/aurions"],
        "canonical_sources": ["docs/workforce/WORKFORCE-CONSTITUTION.md"],
        "acceptance_criteria": ["all integration assertions pass"],
        "test_plan": ["PostgreSQL API integration suite"],
        "review_plan": ["independent review"],
        "max_model_calls": 5,
        "max_tokens": 10000,
        "max_duration_minutes": 60,
        "stop_conditions": ["budget exhausted", "deadline reached"],
    }


@unittest.skipUnless(DB and DIRECTOR and ORCHESTRATOR, "requires disposable PostgreSQL and test credentials")
class ControlPlaneApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        # Audit events are intentionally append-only; each test uses an isolated task ID.
        self.task_id = "test-" + uuid.uuid4().hex[:16]

    def create_task(self, role="lead_builder"):
        task_contract = contract()
        task_contract["work_package_id"] = self.task_id
        return self.client.post(
            "/v1/tasks",
            headers={
                "X-Orchestrator-Token": ORCHESTRATOR,
                "X-Director-Approval-Token": DIRECTOR,
            },
            json={"task_id": self.task_id, "role": role, "contract": task_contract},
        )

    def test_durable_budget_reserve_and_settle_are_atomic_and_persistent(self):
        self.assertEqual(self.create_task().status_code, 201)
        headers = {"X-Worker-Token": BUILDER}
        claim = self.client.post(f"/v1/tasks/{self.task_id}/claim", headers=headers, json={})
        self.assertEqual(claim.status_code, 200, claim.text)
        lease = claim.json()["lease_token"]
        reserved = self.client.post(
            f"/v1/tasks/{self.task_id}/budget/reserve",
            headers=headers,
            json={"lease_token": lease, "requested_tokens": 6000},
        )
        self.assertEqual(reserved.status_code, 200, reserved.text)
        self.assertEqual(reserved.json()["reserved_tokens"], 6000)
        settled = self.client.post(
            f"/v1/tasks/{self.task_id}/budget/settle",
            headers=headers,
            json={"lease_token": lease, "reservation_id": reserved.json()["reservation_id"], "actual_tokens": 1200},
        )
        self.assertEqual(settled.status_code, 200, settled.text)
        with psycopg.connect(DB) as conn:
            budget = conn.execute(
                """SELECT used_model_calls,used_tokens,reserved_calls,reserved_tokens
                     FROM wf_agent_budgets WHERE work_package_id=%s AND role='lead_builder'""",
                (self.task_id,),
            ).fetchone()
        self.assertEqual(budget, (1, 1200, 0, 0))
        too_large = self.client.post(
            f"/v1/tasks/{self.task_id}/budget/reserve",
            headers=headers,
            json={"lease_token": lease, "requested_tokens": 9000},
        )
        self.assertEqual(too_large.status_code, 429)

    def test_orphaned_budget_reservation_is_charged_on_lease_recovery(self):
        self.assertEqual(self.create_task().status_code, 201)
        headers = {"X-Worker-Token": BUILDER}
        claim = self.client.post(f"/v1/tasks/{self.task_id}/claim", headers=headers, json={})
        self.assertEqual(claim.status_code, 200, claim.text)
        lease = claim.json()["lease_token"]
        reserved = self.client.post(
            f"/v1/tasks/{self.task_id}/budget/reserve",
            headers=headers,
            json={"lease_token": lease, "requested_tokens": 1500},
        )
        self.assertEqual(reserved.status_code, 200, reserved.text)
        with psycopg.connect(DB) as conn:
            conn.execute("UPDATE wf_tasks SET lease_expires_at=now()-interval '1 second' WHERE task_id=%s", (self.task_id,))
        recovered = self.client.post(
            "/v1/maintenance/recover",
            headers={"X-Orchestrator-Token": ORCHESTRATOR},
        )
        self.assertEqual(recovered.status_code, 200, recovered.text)
        with psycopg.connect(DB) as conn:
            budget = conn.execute(
                """SELECT used_model_calls,used_tokens,reserved_calls,reserved_tokens
                     FROM wf_agent_budgets WHERE work_package_id=%s AND role='lead_builder'""",
                (self.task_id,),
            ).fetchone()
            reservation_state = conn.execute(
                "SELECT state,actual_tokens FROM wf_budget_reservations WHERE reservation_id=%s",
                (reserved.json()["reservation_id"],),
            ).fetchone()
        self.assertEqual(budget, (1, 1500, 0, 0))
        self.assertEqual(reservation_state, ("ABANDONED", 1500))

    def test_task_creation_requires_both_authorities_and_listing_is_private(self):
        payload = {"task_id": self.task_id, "role": "lead_builder", "contract": contract()}
        self.assertEqual(self.client.post("/v1/tasks", json=payload).status_code, 401)
        self.assertEqual(
            self.client.post("/v1/tasks", headers={"X-Orchestrator-Token": ORCHESTRATOR}, json=payload).status_code,
            401,
        )
        self.assertEqual(self.create_task().status_code, 201)
        self.assertEqual(self.client.get("/v1/tasks").status_code, 401)
        self.assertEqual(
            self.client.get("/v1/tasks", headers={"X-Orchestrator-Token": ORCHESTRATOR}).status_code,
            200,
        )

    def test_worker_identity_is_credential_derived_and_role_scoped(self):
        self.assertEqual(self.create_task(role="lead_builder").status_code, 201)
        wrong_role = self.client.post(
            f"/v1/tasks/{self.task_id}/claim",
            headers={"X-Worker-Token": REVIEWER},
            json={},
        )
        self.assertEqual(wrong_role.status_code, 409)
        forged = self.client.post(
            f"/v1/tasks/{self.task_id}/claim",
            headers={"X-Worker-Token": BUILDER},
            json={"worker_id": "director"},
        )
        self.assertEqual(forged.status_code, 422)
        claimed = self.client.post(
            f"/v1/tasks/{self.task_id}/claim",
            headers={"X-Worker-Token": BUILDER},
            json={},
        )
        self.assertEqual(claimed.status_code, 200, claimed.text)
        self.assertEqual(claimed.json()["worker_id"], "builder-01")

    def test_checkpoint_is_idempotent_and_requires_live_lease(self):
        self.assertEqual(self.create_task().status_code, 201)
        claimed = self.client.post(
            f"/v1/tasks/{self.task_id}/claim",
            headers={"X-Worker-Token": BUILDER},
            json={},
        ).json()
        headers = {"X-Worker-Token": BUILDER}
        started = self.client.post(
            f"/v1/tasks/{self.task_id}/start",
            headers=headers,
            json={"lease_token": claimed["lease_token"]},
        )
        self.assertEqual(started.status_code, 200, started.text)
        payload = {
            "lease_token": claimed["lease_token"],
            "checkpoint_name": "checkpoint-1",
            "payload": {"progress": "persisted"},
            "context_sha256": "b" * 64,
            "idempotency_key": "stable-checkpoint-key-001",
        }
        first = self.client.post(f"/v1/tasks/{self.task_id}/checkpoint", headers=headers, json=payload)
        second = self.client.post(f"/v1/tasks/{self.task_id}/checkpoint", headers=headers, json=payload)
        self.assertEqual(first.status_code, 201, first.text)
        self.assertEqual(second.status_code, 201, second.text)
        self.assertFalse(first.json()["idempotent_replay"])
        self.assertTrue(second.json()["idempotent_replay"])
        conflicting = {**payload, "payload": {"progress": "tampered"}}
        conflict = self.client.post(f"/v1/tasks/{self.task_id}/checkpoint", headers=headers, json=conflicting)
        self.assertEqual(conflict.status_code, 409)
        with psycopg.connect(DB) as conn:
            count = conn.execute("SELECT count(*) FROM wf_checkpoints WHERE task_id=%s", (self.task_id,)).fetchone()[0]
        self.assertEqual(count, 1)

    def test_expired_lease_is_fenced_and_recovered_for_retry(self):
        self.assertEqual(self.create_task().status_code, 201)
        headers = {"X-Worker-Token": BUILDER}
        old = self.client.post(f"/v1/tasks/{self.task_id}/claim", headers=headers, json={}).json()
        self.client.post(
            f"/v1/tasks/{self.task_id}/start",
            headers=headers,
            json={"lease_token": old["lease_token"]},
        )
        checkpoint = self.client.post(
            f"/v1/tasks/{self.task_id}/checkpoint",
            headers=headers,
            json={
                "lease_token": old["lease_token"],
                "checkpoint_name": "recoverable",
                "payload": {"durable_progress": 7},
                "context_sha256": "e" * 64,
                "idempotency_key": "recoverable-checkpoint-key-01",
            },
        )
        self.assertEqual(checkpoint.status_code, 201, checkpoint.text)
        with psycopg.connect(DB) as conn:
            conn.execute("UPDATE wf_tasks SET lease_expires_at=now()-interval '1 second' WHERE task_id=%s", (self.task_id,))
        heartbeat = self.client.post(
            f"/v1/tasks/{self.task_id}/heartbeat",
            headers=headers,
            json={"lease_token": old["lease_token"]},
        )
        self.assertEqual(heartbeat.status_code, 409)
        recovered = self.client.post(
            "/v1/maintenance/recover",
            headers={"X-Orchestrator-Token": ORCHESTRATOR},
        )
        self.assertEqual(recovered.status_code, 200, recovered.text)
        with psycopg.connect(DB) as conn:
            state = conn.execute("SELECT state FROM wf_tasks WHERE task_id=%s", (self.task_id,)).fetchone()[0]
            conn.execute("UPDATE wf_tasks SET retry_after=now()-interval '1 second' WHERE task_id=%s", (self.task_id,))
        self.assertEqual(state, "RETRY_WAIT")
        new = self.client.post(f"/v1/tasks/{self.task_id}/claim", headers=headers, json={})
        self.assertEqual(new.status_code, 200, new.text)
        self.assertNotEqual(new.json()["lease_token"], old["lease_token"])
        restored = self.client.get(
            f"/v1/tasks/{self.task_id}/checkpoints/latest",
            headers={**headers, "X-Worker-Lease-Token": new.json()["lease_token"]},
        )
        self.assertEqual(restored.status_code, 200, restored.text)
        self.assertEqual(restored.json()["payload_json"], {"durable_progress": 7})
        stale = self.client.post(
            f"/v1/tasks/{self.task_id}/start",
            headers=headers,
            json={"lease_token": old["lease_token"]},
        )
        self.assertEqual(stale.status_code, 409)

    def test_worker_must_supply_evidence_before_candidate_ready(self):
        self.assertEqual(self.create_task().status_code, 201)
        headers = {"X-Worker-Token": BUILDER}
        claimed = self.client.post(f"/v1/tasks/{self.task_id}/claim", headers=headers, json={}).json()
        started = self.client.post(
            f"/v1/tasks/{self.task_id}/start",
            headers=headers,
            json={"lease_token": claimed["lease_token"]},
        )
        self.assertEqual(started.status_code, 200, started.text)
        no_evidence = self.client.post(
            f"/v1/tasks/{self.task_id}/worker-transition",
            headers=headers,
            json={"lease_token": claimed["lease_token"], "target": "CANDIDATE_READY", "reason": "done"},
        )
        self.assertEqual(no_evidence.status_code, 422)
        completed = self.client.post(
            f"/v1/tasks/{self.task_id}/worker-transition",
            headers=headers,
            json={
                "lease_token": claimed["lease_token"],
                "target": "CANDIDATE_READY",
                "reason": "completed with evidence",
                "evidence_sha256": "d" * 64,
                "evidence_ref": "artifact://worker-output",
            },
        )
        self.assertEqual(completed.status_code, 200, completed.text)
        self.assertEqual(completed.json()["state"], "CANDIDATE_READY")

    def test_orchestrator_cannot_forge_worker_completion(self):
        self.assertEqual(self.create_task().status_code, 201)
        with psycopg.connect(DB) as conn:
            conn.execute("UPDATE wf_tasks SET state='RUNNING' WHERE task_id=%s", (self.task_id,))
        response = self.client.post(
            f"/v1/tasks/{self.task_id}/transition",
            headers={"X-Orchestrator-Token": ORCHESTRATOR},
            json={"target": "CANDIDATE_READY", "reason": "forged completion"},
        )
        self.assertEqual(response.status_code, 403)

    def test_orchestrator_gate_requires_and_records_stage_evidence(self):
        self.assertEqual(self.create_task().status_code, 201)
        with psycopg.connect(DB) as conn:
            conn.execute("UPDATE wf_tasks SET state='CANDIDATE_READY',attempt_count=1 WHERE task_id=%s", (self.task_id,))
        headers = {"X-Orchestrator-Token": ORCHESTRATOR}
        missing = self.client.post(
            f"/v1/tasks/{self.task_id}/transition",
            headers=headers,
            json={"target": "TESTING", "reason": "begin tests"},
        )
        self.assertEqual(missing.status_code, 422)
        passed = self.client.post(
            f"/v1/tasks/{self.task_id}/transition",
            headers=headers,
            json={
                "target": "TESTING",
                "reason": "candidate digest verified and tests started",
                "evidence_sha256": "a" * 64,
                "evidence_ref": "artifact://candidate-bundle",
            },
        )
        self.assertEqual(passed.status_code, 200, passed.text)
        with psycopg.connect(DB) as conn:
            evidence = conn.execute(
                "SELECT stage,sha256,evidence_ref FROM wf_task_evidence WHERE task_id=%s",
                (self.task_id,),
            ).fetchone()
        self.assertEqual(evidence, ("CANDIDATE", "a" * 64, "artifact://candidate-bundle"))
        manifest = self.client.get(
            f"/v1/tasks/{self.task_id}/evidence",
            headers={"X-Orchestrator-Token": ORCHESTRATOR},
        )
        self.assertEqual(manifest.status_code, 200, manifest.text)
        self.assertEqual(manifest.json()[0]["stage"], "CANDIDATE")

    def test_deadline_stops_review_stage_tasks(self):
        self.assertEqual(self.create_task().status_code, 201)
        with psycopg.connect(DB) as conn:
            conn.execute(
                "UPDATE wf_tasks SET state='REVIEWING', created_at=now()-interval '61 minutes' WHERE task_id=%s",
                (self.task_id,),
            )
        recovered = self.client.post(
            "/v1/maintenance/recover",
            headers={"X-Orchestrator-Token": ORCHESTRATOR},
        )
        self.assertEqual(recovered.status_code, 200, recovered.text)
        with psycopg.connect(DB) as conn:
            state = conn.execute("SELECT state FROM wf_tasks WHERE task_id=%s", (self.task_id,)).fetchone()[0]
        self.assertEqual(state, "FAILED")

    def test_only_director_can_accept_and_actor_cannot_be_spoofed(self):
        self.assertEqual(self.create_task().status_code, 201)
        with psycopg.connect(DB) as conn:
            conn.execute("UPDATE wf_tasks SET state='AWAITING_DIRECTOR',attempt_count=1 WHERE task_id=%s", (self.task_id,))
            conn.execute(
                """INSERT INTO wf_task_evidence(task_id,stage,sha256,evidence_ref,actor)
                   VALUES (%s,'INTEGRATED',%s,%s,'integration_verifier')""",
                (self.task_id, "c" * 64, "artifact://integrated-report"),
            )
        payload = {
            "target": "ACCEPTED",
            "reason": "test acceptance",
            "director_decision_ref": "decision-test",
            "evidence_sha256": "c" * 64,
            "evidence_ref": "artifact://integrated-report",
        }
        self.assertEqual(self.client.post(f"/v1/tasks/{self.task_id}/transition", json=payload).status_code, 401)
        self.assertEqual(
            self.client.post(
                f"/v1/tasks/{self.task_id}/transition",
                headers={"X-Orchestrator-Token": ORCHESTRATOR},
                json=payload,
            ).status_code,
            401,
        )
        forged = {**payload, "actor": "director"}
        self.assertEqual(
            self.client.post(
                f"/v1/tasks/{self.task_id}/transition",
                headers={"X-Director-Approval-Token": DIRECTOR},
                json=forged,
            ).status_code,
            422,
        )
        mismatched = {**payload, "evidence_sha256": "f" * 64}
        mismatch_response = self.client.post(
            f"/v1/tasks/{self.task_id}/transition",
            headers={"X-Director-Approval-Token": DIRECTOR},
            json=mismatched,
        )
        self.assertEqual(mismatch_response.status_code, 409)
        accepted = self.client.post(
            f"/v1/tasks/{self.task_id}/transition",
            headers={"X-Director-Approval-Token": DIRECTOR},
            json=payload,
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)
        self.assertEqual(accepted.json()["state"], "ACCEPTED")


if __name__ == "__main__":
    unittest.main()
