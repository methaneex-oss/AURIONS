import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from workforce.provider_http import USER_AGENT
from workforce.agents.runner import TOOLS


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "qualify_six_agents.py"
SPEC = importlib.util.spec_from_file_location("qualify_six_agents", SCRIPT)
qualification = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qualification)


class SixAgentQualificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "README.md").write_text("# test repository\n\nA test fixture.\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def first_response(self):
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": "call-readme",
                        "type": "function",
                        "function": {
                            "name": "read_file",
                            "arguments": json.dumps({"path": "README.md"}),
                        },
                    }],
                },
                "finish_reason": "tool_calls",
            }],
        }

    def successful_call(self, role, payload, max_tokens, fallback_model=None, fallback_primary_failure=None):
        if payload.get("tools"):
            self.initial_prompt = payload["messages"][0]["content"]
            return self.first_response(), "groq", "openai/gpt-oss-120b"
        self.assertEqual(payload["messages"][0]["content"], self.initial_prompt)
        tool_message = next(item for item in payload["messages"] if item["role"] == "tool")
        self.assertIn("Do not make another tool call", payload["messages"][-1]["content"])
        self.assertIn("README_CONTENT_START_", tool_message["content"])
        self.assertIn("README_CONTENT_END_", tool_message["content"])
        challenge = re.search(r"QUALIFICATION_CONTEXT_CHALLENGE: ([0-9a-f]+)", tool_message["content"]).group(1)
        answer = {
            "text": "I can generate text. TEXT_RESPONSE_OK",
            "value": 110,
            "parity": "even",
            "method": "multiply then subtract",
            "first_non_empty_line": "# test repository",
            "context_challenge": challenge,
        }
        return {
            "choices": [{
                "message": {"role": "assistant", "content": json.dumps(answer)},
                "finish_reason": "stop",
            }],
        }, "groq", "openai/gpt-oss-120b"

    def test_qualification_http_uses_shared_user_agent(self):
        response = httpx.Response(
            200,
            json={"model": "test-model"},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        with patch.object(qualification.httpx, "post", return_value=response) as post:
            result = qualification._post(
                "https://api.groq.com/openai/v1/chat/completions",
                "test-key",
                {"model": "test-model"},
            )
        self.assertEqual(result["model"], "test-model")
        self.assertEqual(post.call_args.kwargs["headers"]["User-Agent"], USER_AGENT)

    def test_main_reserves_quota_for_qualification_preflight_and_wf03(self):
        checks = (
            "connectivity",
            "text_response",
            "reasoning_training_simulation",
            "repository_tool_access",
        )

        def fake_qualify(role, repo_root, results):
            for check in checks:
                results.append({"role": role, "check": check, "status": "PASS"})

        def fake_probe(results):
            results.append({"role": "openrouter_fallback", "check": "probe", "status": "PASS"})

        with tempfile.TemporaryDirectory() as report_dir:
            report_path = Path(report_dir) / "qualification.json"
            env = {
                "OPENROUTER_API_KEY": "test-key",
                "QUALIFICATION_REPORT": str(report_path),
            }
            with patch.dict(os.environ, env, clear=True):
                with patch.object(
                    qualification,
                    "require_free_model_quota",
                    return_value={"used": 10, "limit": 50, "remaining": 40},
                ) as quota, patch.object(qualification, "qualify_role", side_effect=fake_qualify), patch.object(
                    qualification, "openrouter_free_probe", side_effect=fake_probe
                ), patch.object(
                    qualification, "groq_model_catalog_diagnostic", return_value={"status": "OK"}
                ):
                    self.assertEqual(qualification.main(), 0)
            self.assertEqual(quota.call_args.kwargs["minimum_remaining"], 40)
            self.assertTrue(report_path.is_file())

    def test_architecture_reviewer_qualification_uses_runtime_tools_and_named_read_file_choice(self):
        captured = []

        def capture_call(role, payload, max_tokens, fallback_model=None, fallback_primary_failure=None):
            captured.append(payload)
            return self.first_response(), "cloudflare", "@cf/zai-org/glm-4.7-flash"

        results = []
        with patch.object(qualification, "_call", side_effect=capture_call):
            qualification.qualify_role("architecture_reviewer", self.root, results)

        self.assertEqual(captured[0]["tools"], TOOLS)
        self.assertEqual(
            captured[0]["tool_choice"],
            {"type": "function", "function": {"name": "read_file"}},
        )

    def test_role_qualification_covers_four_capabilities_in_two_calls(self):
        results = []
        with patch.object(qualification, "_call", side_effect=self.successful_call) as call:
            qualification.qualify_role("lead_builder", self.root, results)
        self.assertEqual(call.call_count, 2)
        self.assertEqual(len(results), 4)
        self.assertEqual([item["status"] for item in results], ["PASS", "PASS", "PASS", "PASS"])
        self.assertEqual(
            [item["check"] for item in results],
            ["connectivity", "text_response", "reasoning_training_simulation", "repository_tool_access"],
        )

    def test_followup_budget_accounts_for_gemma_reasoning_output(self):
        calls = []

        def capture_call(role, payload, max_tokens, fallback_model=None, fallback_primary_failure=None):
            calls.append(max_tokens)
            if payload.get("tools"):
                return self.first_response(), "cloudflare", "@cf/google/gemma-4-26b-a4b-it"
            tool_message = next(item for item in payload["messages"] if item["role"] == "tool")
            challenge = re.search(r"QUALIFICATION_CONTEXT_CHALLENGE: ([0-9a-f]+)", tool_message["content"]).group(1)
            answer = {
                "text": "TEXT_RESPONSE_OK",
                "value": 110,
                "parity": "even",
                "method": "multiply then subtract",
                "first_non_empty_line": "# test repository",
                "context_challenge": challenge,
            }
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": json.dumps(answer)},
                    "finish_reason": "stop",
                }],
            }, "cloudflare", "@cf/google/gemma-4-26b-a4b-it"

        results = []
        with patch.object(qualification, "_call", side_effect=capture_call):
            qualification.qualify_role("specialist_builder", self.root, results)
        self.assertEqual(calls, [512, 4096])
        self.assertTrue(all(item["status"] == "PASS" for item in results))

    def test_context_extraction_prompt_excludes_wrapper_labels(self):
        results = []
        with patch.object(qualification, "_call", side_effect=self.successful_call) as call:
            qualification.qualify_role("lead_builder", self.root, results)
        followup = call.call_args_list[1].kwargs if call.call_args_list else {}
        payload = call.call_args_list[1].args[1]
        prompt = payload["messages"][-1]["content"]
        self.assertIn("README_CONTENT_START_", prompt)
        self.assertIn("ignore all wrapper labels", prompt)
        self.assertIn("Do not make another tool call", prompt)

    def test_unverified_followup_records_bounded_response_preview(self):
        def partial_call(role, payload, max_tokens, fallback_model=None, fallback_primary_failure=None):
            if payload.get("tools"):
                return self.first_response(), "cloudflare", "@cf/google/gemma-4-26b-a4b-it"
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "I read the README but could not return the required structured fields.",
                    },
                    "finish_reason": "stop",
                }],
            }, "cloudflare", "@cf/google/gemma-4-26b-a4b-it"

        results = []
        with patch.object(qualification, "_call", side_effect=partial_call):
            qualification.qualify_role("specialist_builder", self.root, results)
        repository = next(item for item in results if item["check"] == "repository_tool_access")
        self.assertEqual(repository["status"], "PARTIAL")
        self.assertEqual(repository["followup_context_use"], "not_verified")
        self.assertIn("could not return the required structured fields", repository["followup_response_preview"])
        self.assertLessEqual(len(repository["followup_response_preview"]), 180)

    def test_fallback_is_pinned_across_the_two_call_conversation(self):
        calls = []

        def fallback_call(role, payload, max_tokens, fallback_model=None, fallback_primary_failure=None):
            calls.append((fallback_model, payload))
            if len(calls) == 1:
                data = self.first_response()
                data["_qualification_primary_failure"] = "primary HTTP 429"
                return data, "openrouter-free-fallback", "example-model:free"
            tool_message = next(item for item in payload["messages"] if item["role"] == "tool")
            challenge = re.search(r"QUALIFICATION_CONTEXT_CHALLENGE: ([0-9a-f]+)", tool_message["content"]).group(1)
            answer = {
                "text": "TEXT_RESPONSE_OK",
                "value": 110,
                "parity": "even",
                "method": "multiply then subtract",
                "first_non_empty_line": "# test repository",
                "context_challenge": challenge,
            }
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": json.dumps(answer)},
                    "finish_reason": "stop",
                }],
                "_qualification_primary_failure": "primary HTTP 429",
            }, "openrouter-free-fallback", "example-model:free"

        results = []
        with patch.object(qualification, "_call", side_effect=fallback_call) as call:
            qualification.qualify_role("lead_builder", self.root, results)
        self.assertEqual(call.call_count, 2)
        self.assertIsNone(calls[0][0])
        self.assertEqual(calls[1][0], "example-model:free")
        self.assertTrue(all(item["status"] == "PASS_WITH_FREE_FALLBACK" for item in results))


if __name__ == "__main__":
    unittest.main()
