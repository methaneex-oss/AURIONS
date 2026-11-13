import unittest

from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS, role_assignment, validate_registry


class ModelRegistryTests(unittest.TestCase):
    def test_registry_has_exactly_six_exclusive_roles(self):
        validate_registry()
        self.assertEqual(
            set(ROLE_MODEL_ASSIGNMENTS),
            {
                "lead_builder",
                "specialist_builder",
                "architecture_reviewer",
                "code_reviewer",
                "negative_tester",
                "integration_verifier",
            },
        )

    def test_each_role_has_a_distinct_model(self):
        models = [entry["model"] for entry in ROLE_MODEL_ASSIGNMENTS.values()]
        self.assertEqual(len(models), len(set(models)))

    def test_roles_have_one_provider_profile_and_secret(self):
        for role in ROLE_MODEL_ASSIGNMENTS:
            profile = role_assignment(role)
            self.assertIn(profile["provider"], {"groq", "cloudflare"})
            self.assertTrue(profile["api_url"].startswith("https://"))
            self.assertTrue(profile["key_env"].endswith("_API_KEY"))
            self.assertIn(profile["cost_class"], {"free", "free_daily_allowance"})
            if profile["provider"] == "cloudflare":
                self.assertEqual(profile["account_env"], "CLOUDFLARE_ACCOUNT_ID")
            else:
                self.assertEqual(profile["account_env"], "")

    def test_unknown_role_is_rejected(self):
        with self.assertRaises(ValueError):
            role_assignment("combined_builder_reviewer")
