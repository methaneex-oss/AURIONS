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
from workforce.agents.runner import MAX_INLINE_CONTEXT_BYTES, MANDATORY_GOVERNANCE_FILES, TOOLS, Worker, is_sensitive_path, safe_path


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
                "model": "openai/gpt-oss-120b",
                "usage": {"prompt_tokens": 80, "completion_tokens": total_tokens - 80, "total_tokens": total_tokens},
                "choices": [{"message": {"role": "assistant", "content": "bounded result"}, "finish_reason": "stop"}],
            },
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )

    def test_constructor_rejects_budget_above_hard_ceiling(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": "test-key-only"}, clear=True):
            with self.assertRaises(ValueError):
                Worker(self.root, "lead_builder", [], 101, 512, 12000)

    def test_prompt_estimator_uses_a_conservative_byte_ratio(self):
        sample = ("word " * 1000).encode("utf-8")
        estimate = (len(sample) + 2) // 3
        self.assertGreater(estimate, 1000)
        self.assertLess(estimate, len(sample))

    def test_governance_sources_are_hashed_but_only_compact_brief_is_injected(self):
        worker = self.make_worker(12000)
        for relative in MANDATORY_GOVERNANCE_FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("LARGE_GOVERNANCE_BODY_SENTINEL\\n" + ("x" * 12000), encoding="utf-8")
        brief = self.root / "docs/workforce/AGENT-RUNTIME-GOVERNANCE-BRIEF.md"
        brief.write_text("COMPACT_BRIEF_SENTINEL\\n", encoding="utf-8")

        context, records = worker.load_mandatory_governance()
        combined = "\\n".join(context)

        self.assertIn("COMPACT_BRIEF_SENTINEL", combined)
        self.assertNotIn("LARGE_GOVERNANCE_BODY_SENTINEL", combined)
        self.assertEqual(len(records), len(MANDATORY_GOVERNANCE_FILES))
        for record in records:
            source = self.root / record["path"]
            self.assertEqual(record["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_oversized_task_context_is_referenced_instead_of_injected(self):
        worker = self.make_worker(12000)
        large = self.root / "large-context.md"
        large.write_text("TASK_CONTEXT_BODY_SENTINEL\\n" + ("x" * (MAX_INLINE_CONTEXT_BYTES + 1000)), encoding="utf-8")

        with patch("workforce.agents.runner.httpx.post", return_value=self.response(100)) as provider:
            worker.run("small task", ["large-context.md"])

        system_content = provider.call_args.kwargs["json"]["messages"][0]["content"]
        self.assertIn("TASK CONTEXT NOT INLINED; use read_file: large-context.md", system_content)
        self.assertNotIn("TASK_CONTEXT_BODY_SENTINEL", system_content)

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
        self.assertIs(payload["parallel_tool_calls"], False)
        prompt_bytes = len(json.dumps(
            {"messages": payload["messages"], "tools": TOOLS}, ensure_ascii=False
        ).encode("utf-8"))
        prompt_estimate = (prompt_bytes + 2) // 3 + 256
        self.assertLessEqual(payload["max_completion_tokens"], 7000 - prompt_estimate)
        self.assertLessEqual(prompt_estimate + payload["max_completion_tokens"], 7000)
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

    def test_provider_http_429_preserves_allowlisted_rate_limit_diagnostics_and_redacts_secrets(self):
        worker = self.make_worker(12000)
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        rejected = httpx.Response(
            429,
            json={"error": {"message": "rate limit reached", "type": "rate_limit_error",
                            "code": "tokens_per_minute", "debug": "do not copy"}},
            headers={
                "retry-after": "17",
                "x-ratelimit-limit-requests": "30",
                "x-ratelimit-remaining-requests": "0",
                "x-ratelimit-reset-requests": "1m",
                "x-ratelimit-remaining-tokens": "0",
                "authorization": "Bearer must-not-appear",
                "x-private-debug": "must-not-appear",
            },
            request=request,
        )
        with patch("workforce.agents.runner.httpx.post", return_value=rejected):
            with self.assertRaisesRegex(RuntimeError, r"primary provider transient failure \(HTTP 429\)") as raised:
                worker.run("small task", [])
        detail = str(raised.exception)
        self.assertIn("tokens_per_minute", detail)
        self.assertIn('"retry-after": "17"', detail)
        self.assertIn('"x-ratelimit-remaining-requests": "0"', detail)
        self.assertNotIn("do not copy", detail)
        self.assertNotIn("must-not-appear", detail)
        self.assertIn("OPENROUTER_API_KEY is not configured", detail)

    def test_transient_primary_failure_uses_only_verified_openrouter_free_route(self):
        env = {"GROQ_API_KEY": "test-key-only", "OPENROUTER_API_KEY": "test-openrouter-key"}
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        primary = httpx.Response(
            429,
            json={"error": {"message": "rate limited", "type": "rate_limit_error"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        fallback = httpx.Response(
            200,
            json={
                "model": "openai/gpt-oss-20b:free",
                "usage": {"prompt_tokens": 80, "completion_tokens": 20, "total_tokens": 100},
                "choices": [{"message": {"role": "assistant", "content": "bounded result"}, "finish_reason": "stop"}],
            },
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )
        with patch("workforce.agents.runner.httpx.post", side_effect=[primary, fallback]) as provider:
            result = worker.run("small task", [])
        self.assertEqual(provider.call_count, 2)
        self.assertIn("api.groq.com", provider.call_args_list[0].args[0])
        fallback_call = provider.call_args_list[1]
        self.assertEqual(fallback_call.args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(fallback_call.kwargs["json"]["model"], "openrouter/free")
        self.assertIn("max_tokens", fallback_call.kwargs["json"])
        self.assertNotIn("max_completion_tokens", fallback_call.kwargs["json"])
        self.assertEqual(fallback_call.kwargs["headers"]["Authorization"], "Bearer test-openrouter-key")
        self.assertEqual(result["provider"], "openrouter-free-fallback")
        self.assertEqual(result["model"], "openai/gpt-oss-20b:free")
        self.assertEqual(result["primary_provider"], "groq")
        self.assertEqual(result["route_history"][-1]["provider"], "openrouter-free-fallback")
        self.assertIn("primary HTTP 429", result["route_history"][-1]["primary_failure"])
        self.assertEqual(result["total_tokens"], 100)

    def test_openrouter_free_model_is_pinned_for_the_worker_conversation(self):
        env = {"GROQ_API_KEY": "test-key-only", "OPENROUTER_API_KEY": "test-openrouter-key"}
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 3, 512, 12000)
        primary_failure = httpx.Response(
            503, json={"error": {"message": "temporarily unavailable"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        tool_response = httpx.Response(
            200,
            json={
                "model": "openai/gpt-oss-20b:free",
                "usage": {"prompt_tokens": 80, "completion_tokens": 20, "total_tokens": 100},
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": "call-1",
                            "type": "function",
                            "function": {"name": "read_file", "arguments": json.dumps({"path": "README.md"})},
                        }],
                    },
                    "finish_reason": "tool_calls",
                }],
            },
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )
        final_response = httpx.Response(
            200,
            json={
                "model": "openai/gpt-oss-20b:free",
                "usage": {"prompt_tokens": 90, "completion_tokens": 10, "total_tokens": 100},
                "choices": [{"message": {"role": "assistant", "content": "bounded result"}, "finish_reason": "stop"}],
            },
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )
        self.assertTrue((self.root / "README.md").write_text("AURIONS README FIRST LINE\\n", encoding="utf-8"))
        with patch(
            "workforce.agents.runner.httpx.post",
            side_effect=[primary_failure, tool_response, final_response],
        ) as provider:
            result = worker.run("small task", [])
        self.assertEqual(result["final"], "bounded result")
        self.assertEqual(provider.call_count, 3)
        first_fallback = provider.call_args_list[1].kwargs["json"]
        second_fallback = provider.call_args_list[2].kwargs["json"]
        self.assertEqual(first_fallback["model"], "openrouter/free")
        self.assertEqual(second_fallback["model"], "openai/gpt-oss-20b:free")
        self.assertEqual(worker.openrouter_fallback_model, "openai/gpt-oss-20b:free")
        self.assertEqual(
            [entry["model"] for entry in result["route_history"]],
            ["openai/gpt-oss-20b:free", "openai/gpt-oss-20b:free"],
        )

    def test_groq_model_permission_403_uses_only_verified_free_fallback(self):
        env = {"GROQ_API_KEY": "test-key-only", "OPENROUTER_API_KEY": "test-openrouter-key"}
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        denied = httpx.Response(
            403,
            json={"error": {"message": "model permission blocked", "type": "permissions_error",
                            "code": "model_permission_blocked_project"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        fallback = httpx.Response(
            200,
            json={
                "model": "openai/gpt-oss-20b:free",
                "usage": {"prompt_tokens": 80, "completion_tokens": 20, "total_tokens": 100},
                "choices": [{"message": {"role": "assistant", "content": "bounded result"}, "finish_reason": "stop"}],
            },
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )
        with patch("workforce.agents.runner.httpx.post", side_effect=[denied, fallback]) as provider:
            result = worker.run("small task", [])
        self.assertEqual(provider.call_count, 2)
        self.assertEqual(result["provider"], "openrouter-free-fallback")
        self.assertEqual(result["model"], "openai/gpt-oss-20b:free")
        self.assertIn("primary HTTP 403", result["route_history"][-1]["primary_failure"])

    def test_primary_401_never_triggers_openrouter_fallback(self):
        env = {"GROQ_API_KEY": "test-key-only", "OPENROUTER_API_KEY": "test-openrouter-key"}
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        denied = httpx.Response(
            401,
            json={"error": {"message": "invalid API key", "type": "authentication_error"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        with patch("workforce.agents.runner.httpx.post", return_value=denied) as provider:
            with self.assertRaisesRegex(RuntimeError, "provider rejected request"):
                worker.run("small task", [])
        provider.assert_called_once()

    def test_cloudflare_403_does_not_trigger_openrouter_fallback(self):
        env = {
            "CLOUDFLARE_API_TOKEN": "test-cloudflare-key",
            "CLOUDFLARE_ACCOUNT_ID": "test-account",
            "OPENROUTER_API_KEY": "test-openrouter-key",
        }
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "architecture_reviewer", [], 2, 512, 12000)
        denied = httpx.Response(
            403,
            json={"errors": [{"code": 10000, "message": "permission denied"}]},
            request=httpx.Request("POST", worker.api_url),
        )
        with patch("workforce.agents.runner.httpx.post", return_value=denied) as provider:
            with self.assertRaisesRegex(RuntimeError, "fallback is not enabled for this provider"):
                worker.run("small task", [])
        provider.assert_called_once()

    def test_primary_response_model_identity_mismatch_is_rejected(self):
        worker = self.make_worker(12000)
        invalid = httpx.Response(
            200,
            json={
                "model": "unexpected/model",
                "usage": {"prompt_tokens": 80, "completion_tokens": 20, "total_tokens": 100},
                "choices": [{"message": {"role": "assistant", "content": "wrong model"}}],
            },
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        with patch("workforce.agents.runner.httpx.post", return_value=invalid):
            with self.assertRaisesRegex(RuntimeError, "unexpected model identity"):
                worker.run("small task", [])

    def test_openrouter_response_without_free_model_identity_is_rejected(self):
        env = {"GROQ_API_KEY": "test-key-only", "OPENROUTER_API_KEY": "test-openrouter-key"}
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        primary = httpx.Response(
            503, json={"error": {"message": "unavailable"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        fallback = httpx.Response(
            200, json={"model": "openai/gpt-oss-20b"},
            request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
        )
        with patch("workforce.agents.runner.httpx.post", side_effect=[primary, fallback]):
            with self.assertRaisesRegex(RuntimeError, "refusing any potentially paid route"):
                worker.run("small task", [])

    def test_provider_http_400_preserves_bounded_structured_error_without_secrets(self):
        worker = self.make_worker(12000)
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        rejected = httpx.Response(
            400,
            json={
                "error": {
                    "message": "Unsupported parameter temperature for this model",
                    "type": "invalid_request_error",
                    "param": "temperature",
                    "code": "unsupported_parameter",
                    "debug": "must not be copied",
                }
            },
            request=request,
        )
        with patch("workforce.agents.runner.httpx.post", return_value=rejected):
            with self.assertRaisesRegex(
                RuntimeError,
                r"provider rejected request \(HTTP 400\).*unsupported_parameter",
            ) as raised:
                worker.run("small task", [])
        self.assertIn("Unsupported parameter temperature", str(raised.exception))
        self.assertNotIn("must not be copied", str(raised.exception))
        self.assertNotIn("test-key-only", str(raised.exception))

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

    def test_worker_cannot_execute_candidate_tests_in_provider_process(self):
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
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 2, 512, 12000)
        tool_names = {item["function"]["name"] for item in TOOLS}
        self.assertNotIn("run_workforce_tests", tool_names)
        self.assertEqual(worker.invoke_tool("run_workforce_tests", {}), "DENIED: unknown tool.")

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
