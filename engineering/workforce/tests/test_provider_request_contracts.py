import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from workforce.agents.runner import MANDATORY_GOVERNANCE_FILES, Worker, provider_error_detail
from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS


class ProviderRequestContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in MANDATORY_GOVERNANCE_FILES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test governance source\\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_every_role_uses_its_registry_completion_parameter(self):
        expected = {
            "lead_builder": "max_completion_tokens",
            "specialist_builder": "max_completion_tokens",
            "architecture_reviewer": "max_completion_tokens",
            "code_reviewer": "max_completion_tokens",
            "negative_tester": "max_completion_tokens",
            "integration_verifier": "max_tokens",
        }
        for role, profile in ROLE_MODEL_ASSIGNMENTS.items():
            with self.subTest(role=role):
                env = {
                    "GROQ_API_KEY": "test-groq",
                    "CLOUDFLARE_API_TOKEN": "test-cloudflare",
                    "CLOUDFLARE_ACCOUNT_ID": "test-account",
                }
                with patch.dict("os.environ", env, clear=True):
                    worker = Worker(self.root, role, [], 1, 512, 12000)
                response = httpx.Response(
                    200,
                    json={
                        "model": profile["model"],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
                        "choices": [{"message": {"role": "assistant", "content": "contract-ok"}}],
                    },
                    request=httpx.Request("POST", profile["api_url"].replace("{account_id}", "test-account")),
                )
                with patch("workforce.agents.runner.httpx.post", return_value=response) as post:
                    result = worker.run("contract test", [])
                payload = post.call_args.kwargs["json"]
                self.assertIn(expected[role], payload)
                other = "max_tokens" if expected[role] == "max_completion_tokens" else "max_completion_tokens"
                self.assertNotIn(other, payload)
                self.assertEqual(payload["model"], profile["model"])
                self.assertEqual(result["final"], "contract-ok")


    def test_cloudflare_errors_array_is_extracted_without_copying_untrusted_fields(self):
        response = httpx.Response(
            403,
            json={
                "success": False,
                "errors": [
                    {"code": 10000, "message": "Invalid API token", "documentation_url": "do-not-copy"},
                    {"code": 10001, "message": "Second diagnostic"},
                ],
                "debug": "do-not-copy",
            },
            headers={"x-private-debug": "do-not-copy"},
            request=httpx.Request("POST", "https://api.cloudflare.com/client/v4/accounts/test/ai/run"),
        )
        rendered = provider_error_detail(response, ("test-secret",))
        self.assertIn('"cloudflare_errors"', rendered)
        self.assertIn("Invalid API token", rendered)
        self.assertIn("10001", rendered)
        self.assertNotIn("documentation_url", rendered)
        self.assertNotIn("do-not-copy", rendered)

    def test_rfc9457_problem_details_are_extracted_and_secrets_redacted(self):
        response = httpx.Response(
            403,
            json={
                "type": "https://example.invalid/problems/permission",
                "title": "Forbidden",
                "detail": "Token test-secret lacks Workers AI permission",
                "status": 403,
                "instance": "do-not-copy",
            },
            request=httpx.Request("POST", "https://api.cloudflare.com/client/v4/accounts/test/ai/run"),
        )
        rendered = provider_error_detail(response, ("test-secret",))
        self.assertIn('"problem"', rendered)
        self.assertIn("Forbidden", rendered)
        self.assertIn("[REDACTED]", rendered)
        self.assertNotIn("test-secret", rendered)
        self.assertNotIn("instance", rendered)


    def test_generic_groq_403_does_not_trigger_openrouter_fallback(self):
        env = {
            "GROQ_API_KEY": "test-groq",
            "OPENROUTER_API_KEY": "test-openrouter",
        }
        with patch.dict("os.environ", env, clear=True):
            worker = Worker(self.root, "lead_builder", [], 1, 512, 12000)
        denied = httpx.Response(
            403,
            json={"error": {"message": "account access denied", "type": "forbidden", "code": "account_access_denied"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        with patch("workforce.agents.runner.httpx.post", return_value=denied) as post:
            with self.assertRaisesRegex(RuntimeError, r"primary provider permission denied \(HTTP 403\)"):
                worker.run("bounded test", [])
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.args[0], "https://api.groq.com/openai/v1/chat/completions")


if __name__ == "__main__":
    unittest.main()
