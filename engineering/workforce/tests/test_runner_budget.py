import json
import tempfile
import unittest
import sys
import hashlib
import subprocess
from pathlib import Path
from unittest.mock import patch

import httpx

from workforce.agents import runner as runner_module
from workforce.agents.runner import MANDATORY_GOVERNANCE_FILES, TOOLS, Worker, is_sensitive_path, safe_path


class RunnerBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in MANDATORY_GOVERNANCE_FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("approved governance context\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def make_worker(self, total_tokens, duration_minutes=120):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key-only"}, clear=True):
            return Worker(self.root, "lead_builder", [], 2, 512, total_tokens, duration_minutes)

    def response(self, total_tokens=100):
        return httpx.Response(
            200,
            json={
                "usage": {"prompt_tokens": 80, "completion_tokens": total_tokens - 80, "total_tokens": total_tokens},
                "choices": [{"message": {"role": "assistant", "content": "bounded result"}, "finish_reason": "stop"}],
            },
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )

    def test_constructor_rejects_budget_above_hard_ceiling(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key-only"}, clear=True):
            with self.assertRaises(ValueError):
                Worker(self.root, "lead_builder", [], 101, 512, 12000)

    def test_prompt_budget_is_reserved_before_provider_call(self):
        worker = self.make_worker(64)
        with patch("workforce.agents.runner.httpx.post") as provider:
            with self.assertRaisesRegex(RuntimeError, "provider request was not sent"):
                worker.run("small task", [])
            provider.assert_not_called()
        self.assertEqual(worker.calls, 0)

    def test_completion_limit_leaves_room_for_prompt_and_protocol(self):
        worker = self.make_worker(12000)
        with patch("workforce.agents.runner.httpx.post", return_value=self.response(100)) as provider:
            result = worker.run("small task", [])
        payload = provider.call_args.kwargs["json"]
        prompt_bytes = len(json.dumps(
            {"messages": payload["messages"], "tools": TOOLS}, ensure_ascii=False
        ).encode("utf-8"))
        self.assertLessEqual(payload["max_completion_tokens"], 12000 - prompt_bytes - 256)
        self.assertEqual(result["total_tokens"], 100)
        self.assertEqual(result["calls"], 1)

    def test_duration_budget_stops_before_provider_call(self):
        worker = self.make_worker(12000, duration_minutes=1)
        with patch("workforce.agents.runner.time.monotonic", side_effect=[100.0, 161.0]):
            with patch("workforce.agents.runner.httpx.post") as provider:
                with self.assertRaisesRegex(RuntimeError, "task duration budget exhausted"):
                    worker.run("small task", [])
                provider.assert_not_called()

    def test_runner_reserves_and_settles_durable_budget_around_provider_call(self):
        env = {
            "GROQ_API_KEY": "test-key-only",
            "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
            "WORKFORCE_TASK_ID": "task-001",
            "WORKFORCE_WORKER_TOKEN": "w" * 40,
            "WORKFORCE_LEASE_TOKEN": "l" * 64,
        }
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        calls = []
        def fake_post(url, **kwargs):
            calls.append(url)
            request = httpx.Request("POST", url)
            if url.endswith("/heartbeat"):
                return httpx.Response(200, json={"task_id": "task-001", "lease_generation": 1}, request=request)
            if url.endswith("/budget/reserve"):
                amount = kwargs["json"]["requested_tokens"]
                return httpx.Response(200, json={"reservation_id": "reservation-001", "reserved_tokens": amount}, request=request)
            if url.endswith("/budget/settle"):
                return httpx.Response(200, json={"status": "settled"}, request=request)
            return self.response(100)
        with patch("workforce.agents.runner.httpx.post", side_effect=fake_post):
            result = worker.run("small task", [])
        self.assertEqual(result["total_tokens"], 100)
        self.assertEqual(len(calls), 4)
        self.assertTrue(calls[0].endswith("/heartbeat"))
        self.assertTrue(calls[1].endswith("/budget/reserve"))
        self.assertIn("api.groq.com", calls[2])
        self.assertTrue(calls[3].endswith("/budget/settle"))

    def test_runner_stops_before_provider_when_durable_budget_denies_reservation(self):
        env = {
            "GROQ_API_KEY": "test-key-only",
            "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
            "WORKFORCE_TASK_ID": "task-001",
            "WORKFORCE_WORKER_TOKEN": "w" * 40,
            "WORKFORCE_LEASE_TOKEN": "l" * 64,
        }
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        def deny_reservation(url, **kwargs):
            status = 200 if url.endswith("/heartbeat") else 429
            body = {"task_id": "task-001"} if status == 200 else {"detail": "budget exhausted"}
            return httpx.Response(status, json=body, request=httpx.Request("POST", url))
        with patch("workforce.agents.runner.httpx.post", side_effect=deny_reservation) as provider:
            with self.assertRaisesRegex(RuntimeError, "budget refused request"):
                worker.run("small task", [])
        self.assertEqual(worker.calls, 0)
        self.assertEqual(provider.call_count, 2)

    def test_provider_reported_usage_over_budget_fails_closed(self):
        worker = self.make_worker(12000)
        with patch("workforce.agents.runner.httpx.post", return_value=self.response(12001)):
            with self.assertRaisesRegex(RuntimeError, "exceeded the configured aggregate token budget"):
                worker.run("small task", [])
        self.assertEqual(worker.total_tokens, 0)

    def test_secret_and_token_filename_patterns_are_denied(self):
        names = [
            "settings.api_key.json",
            "production-password.txt",
            "oauth_access_token.json",
            "client_secret.json",
            "private_key.pem",
            ".env.production",
            ".ssh/id_ed25519",
        ]
        for name in names:
            with self.subTest(name=name):
                self.assertTrue(is_sensitive_path(Path(name)))
                with self.assertRaises(ValueError):
                    safe_path(self.root, name)

    def test_test_subprocess_does_not_inherit_provider_or_control_plane_secrets(self):
        env = {
            "GROQ_API_KEY": "provider-secret",
            "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
            "WORKFORCE_TASK_ID": "task-001",
            "WORKFORCE_WORKER_TOKEN": "w" * 40,
            "WORKFORCE_LEASE_TOKEN": "l" * 64,
            "DIRECTOR_APPROVAL_TOKEN": "d" * 40,
            "WORKFORCE_ORCHESTRATOR_TOKEN": "o" * 40,
            "WORKFORCE_WORKER_CREDENTIALS_JSON": "{}",
            "DATABASE_URL": "postgresql://user:password@localhost/db",
        }
        (self.root / "engineering/workforce/src").mkdir(parents=True)
        (self.root / "engineering/workforce/tests").mkdir(parents=True)
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("workforce.agents.runner.subprocess.run", return_value=completed) as run:
            worker.invoke_tool("run_workforce_tests", {})
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            child_env = call.kwargs["env"]
            for secret_name in env:
                self.assertNotIn(secret_name, child_env)
            self.assertIn("PYTHONPATH", child_env)
            self.assertIn("PATH", child_env)
            self.assertNotEqual(call.kwargs["cwd"], self.root)

    def test_cli_claims_starts_runs_and_publishes_report_evidence(self):
        env = {
            "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
            "WORKFORCE_TASK_ID": "task-001",
            "WORKFORCE_WORKER_TOKEN": "w" * 40,
        }
        calls = []
        class FakeWorker:
            def __init__(self, *args, **kwargs):
                pass
            def run(self, task, context_files):
                return {"role": "lead_builder", "final": "bounded fake result"}

        def fake_post(url, **kwargs):
            calls.append((url, kwargs))
            request = httpx.Request("POST", url)
            if url.endswith("/claim"):
                return httpx.Response(200, json={"lease_token": "l" * 64}, request=request)
            if url.endswith("/start"):
                return httpx.Response(200, json={"task_id": "task-001", "state": "RUNNING"}, request=request)
            if url.endswith("/worker-transition"):
                return httpx.Response(200, json={"state": "CANDIDATE_READY"}, request=request)
            raise AssertionError(f"unexpected control-plane endpoint: {url}")

        with patch.dict("os.environ", env, clear=True):
            with patch.object(sys, "argv", [
                "runner", "--role", "lead_builder", "--task", "test task",
                "--workspace", str(self.root), "--report-path", "reports/lead.json",
            ]):
                with patch.object(runner_module, "Worker", FakeWorker):
                    with patch.object(runner_module.httpx, "post", side_effect=fake_post):
                        runner_module.main()

        self.assertEqual(len(calls), 3)
        self.assertTrue(calls[0][0].endswith("/claim"))
        self.assertTrue(calls[1][0].endswith("/start"))
        self.assertTrue(calls[2][0].endswith("/worker-transition"))
        report = self.root / "reports/lead.json"
        self.assertTrue(report.is_file())
        payload = calls[2][1]["json"]
        self.assertEqual(payload["target"], "CANDIDATE_READY")
        self.assertEqual(payload["evidence_sha256"], hashlib.sha256(report.read_bytes()).hexdigest())
        self.assertEqual(payload["evidence_ref"], "reports/lead.json")

    def test_cli_retries_candidate_publication_after_ambiguous_response(self):
        env = {
            "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
            "WORKFORCE_TASK_ID": "task-ambiguous",
            "WORKFORCE_WORKER_TOKEN": "w" * 40,
        }
        calls = []
        class FakeWorker:
            def __init__(self, *args, **kwargs):
                pass
            def run(self, task, context_files):
                return {"role": "lead_builder", "final": "candidate"}

        def fake_post(url, **kwargs):
            calls.append(url)
            request = httpx.Request("POST", url)
            if url.endswith("/claim"):
                return httpx.Response(200, json={"lease_token": "l" * 64}, request=request)
            if url.endswith("/start"):
                return httpx.Response(200, json={"task_id": "task-ambiguous", "state": "RUNNING"}, request=request)
            if url.endswith("/worker-transition") and calls.count(url) == 1:
                return httpx.Response(503, json={"detail": "response unavailable"}, request=request)
            if url.endswith("/worker-transition"):
                return httpx.Response(200, json={"state": "CANDIDATE_READY", "idempotent_replay": True}, request=request)
            raise AssertionError(url)

        with patch.dict("os.environ", env, clear=True):
            with patch.object(sys, "argv", ["runner", "--role", "lead_builder", "--task", "test", "--workspace", str(self.root)]):
                with patch.object(runner_module, "Worker", FakeWorker):
                    with patch.object(runner_module.httpx, "post", side_effect=fake_post):
                        runner_module.main()
        self.assertEqual(len(calls), 4)
        self.assertEqual(sum(url.endswith("/worker-transition") for url in calls), 2)

    def test_cli_uses_existing_lease_without_claiming_again(self):
        env = {
            "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
            "WORKFORCE_TASK_ID": "task-002",
            "WORKFORCE_WORKER_TOKEN": "w" * 40,
            "WORKFORCE_LEASE_TOKEN": "l" * 64,
        }
        calls = []
        class FakeWorker:
            def __init__(self, *args, **kwargs):
                pass
            def run(self, task, context_files):
                return {"role": "lead_builder", "final": "resume result"}

        def fake_post(url, **kwargs):
            calls.append(url)
            request = httpx.Request("POST", url)
            if url.endswith("/start"):
                return httpx.Response(200, json={"task_id": "task-002", "state": "RUNNING"}, request=request)
            return httpx.Response(200, json={"state": "CANDIDATE_READY"}, request=request)

        with patch.dict("os.environ", env, clear=True):
            with patch.object(sys, "argv", ["runner", "--role", "lead_builder", "--task", "resume", "--workspace", str(self.root)]):
                with patch.object(runner_module, "Worker", FakeWorker):
                    with patch.object(runner_module.httpx, "post", side_effect=fake_post):
                        runner_module.main()
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[0].endswith("/start"))
        self.assertTrue(calls[1].endswith("/worker-transition"))


if __name__ == "__main__":
    unittest.main()
