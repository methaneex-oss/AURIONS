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
        with psycopg.connect(DB) as conn:
            conn.execute("DELETE FROM wf_audit_events")
            conn.execute("DELETE FROM wf_checkpoints")
            conn.execute("DELETE FROM wf_tasks")
        self.task_id = "test-" + uuid.uuid4().hex[:16]

    def tearDown(self):
        with psycopg.connect(DB) as conn:
            conn.execute("DELETE FROM wf_audit_events WHERE task_id=%s", (self.task_id,))
            conn.execute("DELETE FROM wf_checkpoints WHERE task_id=%s", (self.task_id,))
            conn.execute("DELETE FROM wf_tasks WHERE task_id=%s", (self.task_id,))

    def create_task(self, role="lead_builder"):
        return self.client.post(
            "/v1/tasks",
            headers={
                "X-Orchestrator-Token": ORCHESTRATOR,
                "X-Director-Approval-Token": DIRECTOR,
            },
            json={"task_id": self.task_id, "role": role, "contract": contract()},
        )

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
        with psycopg.connect(DB) as conn:
            count = conn.execute("SELECT count(*) FROM wf_checkpoints WHERE task_id=%s", (self.task_id,)).fetchone()[0]
        self.assertEqual(count, 1)

    def test_expired_lease_is_fenced_and_recovered_for_retry(self):
        self.assertEqual(self.create_task().status_code, 201)
        headers = {"X-Worker-Token": BUILDER}
        old = self.client.post(f"/v1/tasks/{self.task_id}/claim", headers=headers, json={}).json()
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
            conn.execute("UPDATE wf_tasks SET state='AWAITING_DIRECTOR' WHERE task_id=%s", (self.task_id,))
        payload = {"target": "ACCEPTED", "reason": "test acceptance", "director_decision_ref": "decision-test", "evidence_sha256": "c" * 64}
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
        accepted = self.client.post(
            f"/v1/tasks/{self.task_id}/transition",
            headers={"X-Director-Approval-Token": DIRECTOR},
            json=payload,
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)
        self.assertEqual(accepted.json()["state"], "ACCEPTED")


if __name__ == "__main__":
    unittest.main()
