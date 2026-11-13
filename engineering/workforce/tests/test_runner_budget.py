import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

from workforce.agents.runner import MANDATORY_GOVERNANCE_FILES, TOOLS, Worker


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

    def test_provider_reported_usage_over_budget_fails_closed(self):
        worker = self.make_worker(12000)
        with patch("workforce.agents.runner.httpx.post", return_value=self.response(12001)):
            with self.assertRaisesRegex(RuntimeError, "exceeded the configured aggregate token budget"):
                worker.run("small task", [])
        self.assertEqual(worker.total_tokens, 0)


if __name__ == "__main__":
    unittest.main()
