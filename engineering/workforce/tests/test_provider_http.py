import unittest

from workforce.provider_http import (
    OPENROUTER_REFERER,
    USER_AGENT,
    authorization_headers,
    chat_completion_headers,
)


class ProviderHttpHeaderTests(unittest.TestCase):
    def test_primary_headers_have_stable_user_agent_and_no_router_metadata(self):
        headers = chat_completion_headers("test-key")
        self.assertEqual(headers["Authorization"], "Bearer test-key")
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertNotIn("HTTP-Referer", headers)
        self.assertNotIn("X-Title", headers)

    def test_openrouter_headers_are_explicit_and_identifiable(self):
        headers = chat_completion_headers("test-key", openrouter=True, title="AURIONS test")
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["HTTP-Referer"], OPENROUTER_REFERER)
        self.assertEqual(headers["X-Title"], "AURIONS test")

    def test_quota_headers_share_the_same_user_agent(self):
        self.assertEqual(authorization_headers("test-key")["User-Agent"], USER_AGENT)


if __name__ == "__main__":
    unittest.main()
