import unittest
from unittest.mock import patch

import httpx

from workforce.openrouter_limits import get_free_model_quota, require_free_model_quota


class OpenRouterFreeQuotaTests(unittest.TestCase):
    def response(self, payload, status=200):
        return httpx.Response(
            status,
            json=payload,
            request=httpx.Request("GET", "https://openrouter.ai/api/v1/key"),
        )

    def test_reads_daily_free_request_allowance(self):
        with patch(
            "workforce.openrouter_limits.httpx.get",
            return_value=self.response({
                "data": {
                    "free_model_daily_requests": {"used": 12, "limit": 50, "remaining": 38},
                    "limit_remaining": None,
                }
            }),
        ):
            self.assertEqual(
                get_free_model_quota("test-key"),
                {"used": 12, "limit": 50, "remaining": 38},
            )

    def test_stops_before_inference_when_reserved_quota_is_insufficient(self):
        with patch(
            "workforce.openrouter_limits.httpx.get",
            return_value=self.response({
                "data": {
                    "free_model_daily_requests": {"used": 35, "limit": 50, "remaining": 15},
                    "limit_remaining": None,
                }
            }),
        ):
            with self.assertRaisesRegex(RuntimeError, "15 remaining, 20 required"):
                require_free_model_quota("test-key", 20, "WF-03")

    def test_fails_closed_when_quota_metadata_is_missing(self):
        with patch(
            "workforce.openrouter_limits.httpx.get",
            return_value=self.response({"data": {}}),
        ):
            with self.assertRaisesRegex(RuntimeError, "did not return free_model_daily_requests"):
                get_free_model_quota("test-key")

    def test_rejects_inconsistent_quota_counters(self):
        with patch(
            "workforce.openrouter_limits.httpx.get",
            return_value=self.response({
                "data": {
                    "free_model_daily_requests": {"used": 40, "limit": 50, "remaining": 20},
                    "limit_remaining": None,
                }
            }),
        ):
            with self.assertRaisesRegex(RuntimeError, "counters are inconsistent"):
                get_free_model_quota("test-key")

    def test_stops_when_account_has_negative_credit_balance(self):
        with patch(
            "workforce.openrouter_limits.httpx.get",
            return_value=self.response({
                "data": {
                    "free_model_daily_requests": {"used": 1, "limit": 50, "remaining": 49},
                    "limit_remaining": -0.01,
                }
            }),
        ):
            with self.assertRaisesRegex(RuntimeError, "negative credit balance"):
                get_free_model_quota("test-key")


if __name__ == "__main__":
    unittest.main()
