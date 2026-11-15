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
    def test_primary_only_mode_stops_on_retryable_primary_failure_without_fallback(self):
        env = {
            "GROQ_API_KEY": "test-primary-key",
            "OPENROUTER_API_KEY": "test-free-key",
            "AURIONS_QUALIFICATION_PRIMARY_ONLY": "true",
        }
        with patch.dict("os.environ", env, clear=True):
            with patch.object(
                qualification,
                "_post",
                side_effect=qualification.ProviderFailure("HTTP 429: rate limited", retryable=True),
            ) as post:
                with self.assertRaisesRegex(qualification.ProviderFailure, "primary-only qualification stopped"):
                    qualification._call("lead_builder", {"messages": [{"role": "user", "content": "test"}]})
        post.assert_called_once()
        self.assertFalse(post.call_args.kwargs.get("openrouter", False))
        self.assertNotIn("openrouter.ai", post.call_args.args[0])

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
