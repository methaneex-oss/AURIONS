import contextlib
import io
import json
import os
import unittest
from unittest.mock import patch

import httpx

from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS
from workforce.provider_preflight import main


class ProviderPreflightTests(unittest.TestCase):
    def response(self, model, returned_model=None):
        return httpx.Response(
            200,
            json={
                "model": returned_model or model,
                "choices": [{
                    "message": {
                        "tool_calls": [{
                            "id": "call-1",
                            "type": "function",
                            "function": {"name": "read_file", "arguments": json.dumps({"path": "README.md"})},
                        }]
                    }
                }],
                "usage": {"total_tokens": 12},
            },
            request=httpx.Request("POST", "https://provider.example/chat/completions"),
        )

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
        "OPENROUTER_API_KEY": "test-openrouter",
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_all_six_models_must_complete_tool_call_and_usage_contract(self, post):
        post.side_effect = [
            *[self.response(profile["model"]) for profile in ROLE_MODEL_ASSIGNMENTS.values()],
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
        ]
        self.assertEqual(main(), 0)
        self.assertEqual(post.call_count, 7)
        for call in post.call_args_list[:6]:
            payload = call.kwargs["json"]
            self.assertEqual(payload["tool_choice"], "required")
            self.assertIn("tools", payload)
            self.assertIn(payload["model"], {p["model"] for p in ROLE_MODEL_ASSIGNMENTS.values()})

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
        "OPENROUTER_API_KEY": "test-openrouter",
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_groq_permission_403_uses_verified_free_fallback(self, post):
        denied = httpx.Response(
            403,
            json={"error": {"message": "model blocked", "type": "permissions_error",
                            "code": "model_permission_blocked_project"}},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        free_response = self.response("openrouter/free", "openai/gpt-oss-20b:free")
        post.side_effect = [
            denied,
            free_response,
            *[self.response(profile["model"]) for profile in list(ROLE_MODEL_ASSIGNMENTS.values())[1:]],
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(), 0)
        self.assertEqual(post.call_count, 8)
        fallback_payload = post.call_args_list[1].kwargs["json"]
        self.assertEqual(fallback_payload["model"], "openrouter/free")
        self.assertIn("max_tokens", fallback_payload)
        self.assertNotIn("max_completion_tokens", fallback_payload)
        self.assertIn("PASS_WITH_FREE_FALLBACK lead_builder", output.getvalue())
        self.assertIn("model_permission_blocked_project", output.getvalue())

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
        "OPENROUTER_API_KEY": "test-openrouter",
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_unexpected_primary_model_identity_blocks_preflight(self, post):
        profiles = list(ROLE_MODEL_ASSIGNMENTS.values())
        post.side_effect = [
            self.response(profiles[0]["model"], "unexpected/model"),
            *[self.response(profile["model"]) for profile in profiles[1:]],
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
        ]
        self.assertEqual(main(), 1)
        self.assertEqual(post.call_count, 7)

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
        "OPENROUTER_API_KEY": "test-openrouter",
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_one_rejected_model_blocks_preflight(self, post):
        post.side_effect = [
            httpx.Response(
                400,
                json={"error": {"message": "unsupported test parameter", "code": "invalid_request"}},
                request=httpx.Request("POST", "https://provider.example/chat/completions"),
            )
        ] + [
            *[self.response(profile["model"]) for profile in list(ROLE_MODEL_ASSIGNMENTS.values())[1:]],
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
        ]
        self.assertEqual(main(), 1)

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq-secret",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare-secret",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
        "OPENROUTER_API_KEY": "test-openrouter",
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_rate_limited_preflight_uses_free_fallback_and_preserves_safe_diagnostics(self, post):
        limited = httpx.Response(
            429,
            json={"error": {"message": "quota limited", "type": "rate_limit_error",
                            "code": "requests_per_day", "private": "do not copy"}},
            headers={"retry-after": "3600", "x-ratelimit-remaining-requests": "0",
                     "authorization": "Bearer test-groq-secret", "x-private": "hidden"},
            request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
        )
        post.side_effect = [
            limited,
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
            *[self.response(profile["model"]) for profile in list(ROLE_MODEL_ASSIGNMENTS.values())[1:]],
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(), 0)
        # First role is lead_builder (Groq); safe limit evidence is retained, credentials are not.
        self.assertEqual(post.call_count, 8)
        self.assertIn("PASS_WITH_FREE_FALLBACK lead_builder", output.getvalue())
        self.assertIn('"retry-after": "3600"', output.getvalue())
        self.assertIn('"x-ratelimit-remaining-requests": "0"', output.getvalue())
        self.assertIn("requests_per_day", output.getvalue())
        self.assertNotIn("test-groq-secret", output.getvalue())
        self.assertNotIn("do not copy", output.getvalue())
        self.assertNotIn("hidden", output.getvalue())

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
        "OPENROUTER_API_KEY": "test-openrouter",
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_cloudflare_403_does_not_trigger_free_fallback(self, post):
        denied = httpx.Response(
            403,
            json={"error": {"message": "permission denied", "type": "forbidden"}},
            request=httpx.Request("POST", "https://api.cloudflare.com/client/v4/accounts/test-account/ai/v1/chat/completions"),
        )
        profiles = list(ROLE_MODEL_ASSIGNMENTS.values())
        post.side_effect = [
            self.response(profiles[0]["model"]),
            denied,
            *[self.response(profile["model"]) for profile in profiles[2:]],
            self.response("openrouter/free", "openai/gpt-oss-20b:free"),
        ]
        self.assertEqual(main(), 1)
        self.assertEqual(post.call_count, 7)
        self.assertNotEqual(
            post.call_args_list[2].args[0],
            "https://openrouter.ai/api/v1/chat/completions",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials_blocks_without_provider_calls(self):
        with patch("workforce.provider_preflight.httpx.post") as post:
            self.assertEqual(main(), 2)
            post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
