import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "qualify_six_agents.py"
SPEC = importlib.util.spec_from_file_location("aurions_qualify_six_agents", SCRIPT_PATH)
qualification = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(qualification)


class QualificationModeTests(unittest.TestCase):
    def test_primary_only_retries_one_transient_primary_failure_without_fallback(self):
        env = {
            "GROQ_API_KEY": "test-primary-key",
            "OPENROUTER_API_KEY": "test-free-key",
            "AURIONS_QUALIFICATION_PRIMARY_ONLY": "true",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch.object(
                qualification,
                "_post",
                side_effect=[
                    qualification.ProviderFailure("network ReadTimeout", retryable=True),
                    {"model": "openai/gpt-oss-120b"},
                ],
            ) as post:
                data, provider, model = qualification._call(
                    "lead_builder", {"messages": [{"role": "user", "content": "test"}]}
                )
        self.assertEqual(data["model"], "openai/gpt-oss-120b")
        self.assertEqual(provider, "groq")
        self.assertEqual(model, "openai/gpt-oss-120b")
        self.assertEqual(post.call_count, 2)
        self.assertTrue(all(not call.kwargs.get("openrouter", False) for call in post.call_args_list))
        self.assertTrue(all("openrouter.ai" not in call.args[0] for call in post.call_args_list))

    def test_primary_only_stops_after_two_transient_primary_failures(self):
        env = {
            "GROQ_API_KEY": "test-primary-key",
            "AURIONS_QUALIFICATION_PRIMARY_ONLY": "true",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch.object(
                qualification,
                "_post",
                side_effect=qualification.ProviderFailure("network ReadTimeout", retryable=True),
            ) as post:
                with self.assertRaisesRegex(qualification.ProviderFailure, "after 2 primary attempts"):
                    qualification._call("lead_builder", {"messages": [{"role": "user", "content": "test"}]})
        self.assertEqual(post.call_count, 2)

    def test_primary_retry_does_not_repeat_permanent_groq_model_permission_403(self):
        env = {
            "GROQ_API_KEY": "test-primary-key",
            "AURIONS_QUALIFICATION_PRIMARY_ONLY": "true",
        }
        failure = qualification.ProviderFailure(
            "HTTP 403: model permission blocked",
            retryable=True,
            status_code=403,
            provider_error_type="permissions_error",
            provider_error_code="model_permission_blocked_project",
        )
        with patch.dict("os.environ", env, clear=True):
            with patch.object(qualification, "_post", side_effect=failure) as post:
                with self.assertRaisesRegex(qualification.ProviderFailure, "model permission blocked"):
                    qualification._call(
                        "lead_builder",
                        {"messages": [{"role": "user", "content": "test"}]},
                    )
        post.assert_called_once()

    def test_groq_request_too_large_429_is_not_retryable(self):
        response = qualification.httpx.Response(
            429,
            json={"error": {"message": "Request too large for model on output tokens per minute", "type": "rate_limit_error", "code": "rate_limit_exceeded"}},
            request=qualification.httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        with patch.object(qualification.httpx, "post", return_value=response):
            with self.assertRaises(qualification.ProviderFailure) as raised:
                qualification._post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    "test-key",
                    {"model": "qwen/qwen3.8-27b"},
                    groq_primary=True,
                )
        self.assertFalse(raised.exception.retryable)
        self.assertIn("Request too large", str(raised.exception))

    def test_code_reviewer_uses_small_qualification_followup_budget(self):
        self.assertEqual(qualification._followup_completion_budget("code_reviewer"), 256)
        self.assertEqual(qualification._followup_completion_budget("specialist_builder"), 4096)

    def test_default_mode_retains_free_only_fallback(self):
        env = {
            "GROQ_API_KEY": "test-primary-key",
            "OPENROUTER_API_KEY": "test-free-key",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch.object(
                qualification,
                "_post",
                side_effect=[
                    qualification.ProviderFailure("HTTP 503: primary unavailable", retryable=True),
                    qualification.ProviderFailure("HTTP 429: fallback rate limited", retryable=True, status_code=429),
                    {"model": "verified-test-model:free"},
                ],
            ) as post:
                data, provider, model = qualification._call(
                    "lead_builder", {"messages": [{"role": "user", "content": "test"}]}
                )
        self.assertEqual(provider, "openrouter-free-fallback")
        self.assertEqual(model, "verified-test-model:free")
        self.assertEqual(data["model"], "verified-test-model:free")
        self.assertEqual(post.call_count, 3)
        self.assertTrue(post.call_args_list[1].kwargs["openrouter"])
        self.assertTrue(post.call_args_list[2].kwargs["openrouter"])
        self.assertEqual(post.call_args_list[1].args[2]["model"], "openrouter/free")
        self.assertEqual(post.call_args_list[2].args[2]["model"], "openrouter/free")

    def test_primary_only_main_skips_all_openrouter_access(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "qualification.json"
            env = {
                "AURIONS_QUALIFICATION_PRIMARY_ONLY": "true",
                "QUALIFICATION_REPORT": str(report_path),
            }

            def fake_qualify_role(role, repo_root, results):
                results.extend(
                    {
                        "role": role,
                        "check": check,
                        "status": "PASS",
                        "provider": "primary-test",
                        "model": "primary-model",
                        "evidence": "mocked primary-only qualification",
                    }
                    for check in (
                        "connectivity",
                        "text_response",
                        "reasoning_training_simulation",
                        "repository_tool_access",
                    )
                )

            with patch.dict("os.environ", env, clear=True):
                with patch.object(qualification, "require_free_model_quota") as quota:
                    with patch.object(qualification, "qualify_role", side_effect=fake_qualify_role):
                        with patch.object(qualification, "openrouter_free_probe") as probe:
                            with patch.object(qualification, "groq_model_catalog_diagnostic", return_value={"status": "OK"}):
                                self.assertEqual(qualification.main(), 0)

            quota.assert_not_called()
            probe.assert_not_called()
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["qualification_mode"], "primary_only")
            self.assertEqual(report["passed"], 24)
            self.assertEqual(report["failed"], 0)
            self.assertEqual(report["not_run"], 1)
            self.assertEqual(report["total"], 25)
            evidence = report["fallback_qualification_evidence"]
            self.assertEqual(evidence["status"], "NOT_RUN_PRIMARY_ONLY_MODE")
            self.assertFalse(evidence["fresh_execution"])


if __name__ == "__main__":
    unittest.main()
