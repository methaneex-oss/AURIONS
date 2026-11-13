import os
import unittest
from pathlib import Path
from unittest.mock import patch

from workforce.agents.runner import Worker, is_sensitive_path, safe_path
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
            self.assertTrue(profile["key_env"].endswith(("_API_KEY", "_API_TOKEN")))
            self.assertIn(profile["cost_class"], {"free", "free_daily_allowance"})
            if profile["provider"] == "cloudflare":
                self.assertEqual(profile["account_env"], "CLOUDFLARE_ACCOUNT_ID")
            else:
                self.assertEqual(profile["account_env"], "")

    def test_groq_role_uses_pinned_model_and_secret(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-secret"}, clear=True):
            worker = Worker(Path.cwd(), "lead_builder", [], 1, 128, 256)
        self.assertEqual(worker.provider, "groq")
        self.assertEqual(worker.model, "openai/gpt-oss-120b")
        self.assertEqual(worker.api_url, "https://api.groq.com/openai/v1/chat/completions")

    def test_cloudflare_role_resolves_account_scoped_endpoint(self):
        with patch.dict(
            os.environ,
            {
                "CLOUDFLARE_API_TOKEN": "test-secret",
                "CLOUDFLARE_ACCOUNT_ID": "account-test",
            },
            clear=True,
        ):
            worker = Worker(Path.cwd(), "architecture_reviewer", [], 1, 128, 256)
        self.assertEqual(worker.provider, "cloudflare")
        self.assertEqual(worker.model, "@cf/zai-org/glm-4.7-flash")
        self.assertEqual(
            worker.api_url,
            "https://api.cloudflare.com/client/v4/accounts/account-test/ai/v1/chat/completions",
        )

    def test_model_override_is_rejected(self):
        with patch.dict(
            os.environ,
            {"GROQ_API_KEY": "test-secret", "MODEL_ID": "unapproved/model"},
            clear=True,
        ):
            with self.assertRaises(RuntimeError):
                Worker(Path.cwd(), "lead_builder", [], 1, 128, 256)

    def test_missing_provider_secret_is_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                Worker(Path.cwd(), "lead_builder", [], 1, 128, 256)

    def test_unknown_role_is_rejected(self):
        with self.assertRaises(ValueError):
            role_assignment("combined_builder_reviewer")

    def test_sensitive_credential_paths_are_denied(self):
        root = Path("/tmp/workspace")
        for relative in (
            ".env.production", ".aws/credentials", ".ssh/id_ed25519",
            "config/private.pem", "secrets.json", "service-account-prod.json",
        ):
            with self.subTest(relative=relative):
                with self.assertRaises(ValueError):
                    safe_path(root, relative)

    def test_ordinary_source_files_remain_readable(self):
        self.assertFalse(is_sensitive_path(Path("src/workforce/runner.py")))
        self.assertFalse(is_sensitive_path(Path("docs/workforce/constitution.md")))

    def test_yaml_duplicate_registry_is_removed(self):
        self.assertFalse((Path(__file__).resolve().parents[3] / "model_registry.yaml").exists())


if __name__ == "__main__":
    unittest.main()
