import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from workforce.agents.runner import MANDATORY_GOVERNANCE_FILES, Worker
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


if __name__ == "__main__":
    unittest.main()
