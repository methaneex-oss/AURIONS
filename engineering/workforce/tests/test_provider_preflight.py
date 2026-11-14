import json
import os
import unittest
from unittest.mock import patch

import httpx

from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS
from workforce.provider_preflight import main


class ProviderPreflightTests(unittest.TestCase):
    def response(self, model):
        return httpx.Response(
            200,
            json={
                "model": model,
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
    }, clear=True)
    @patch("workforce.provider_preflight.httpx.post")
    def test_all_six_models_must_complete_tool_call_and_usage_contract(self, post):
        post.side_effect = [
            self.response(profile["model"])
            for profile in ROLE_MODEL_ASSIGNMENTS.values()
        ]
        self.assertEqual(main(), 0)
        self.assertEqual(post.call_count, 6)
        for call in post.call_args_list:
            payload = call.kwargs["json"]
            self.assertEqual(payload["tool_choice"], "required")
            self.assertIn("tools", payload)
            self.assertIn(payload["model"], {p["model"] for p in ROLE_MODEL_ASSIGNMENTS.values()})

    @patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq",
        "CLOUDFLARE_API_TOKEN": "test-cloudflare",
        "CLOUDFLARE_ACCOUNT_ID": "test-account",
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
            self.response(profile["model"])
            for profile in list(ROLE_MODEL_ASSIGNMENTS.values())[1:]
        ]
        self.assertEqual(main(), 1)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials_blocks_without_provider_calls(self):
        with patch("workforce.provider_preflight.httpx.post") as post:
            self.assertEqual(main(), 2)
            post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
