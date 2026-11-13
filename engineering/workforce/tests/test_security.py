import json
import unittest
from unittest.mock import patch

from workforce.security import (
    AuthenticationError, authenticate_worker, require_director, require_orchestrator,
)


class SecurityTests(unittest.TestCase):
    def test_missing_secrets_fail_closed(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(AuthenticationError):
                require_director("anything")
            with self.assertRaises(AuthenticationError):
                require_orchestrator("anything")
            with self.assertRaises(AuthenticationError):
                authenticate_worker("anything")

    def test_director_and_orchestrator_are_separate_authorities(self):
        with patch.dict("os.environ", {
            "DIRECTOR_APPROVAL_TOKEN": "director-secret",
            "WORKFORCE_ORCHESTRATOR_TOKEN": "orchestrator-secret",
        }, clear=True):
            self.assertEqual(require_director("director-secret").role, "director")
            self.assertEqual(require_orchestrator("orchestrator-secret").role, "orchestrator")
            with self.assertRaises(AuthenticationError):
                require_director("orchestrator-secret")
            with self.assertRaises(AuthenticationError):
                require_orchestrator("director-secret")

    def test_worker_identity_and_role_are_derived_from_secret_registry(self):
        registry = {
            "builder-01": {"token": "builder-secret", "role": "lead_builder"},
            "reviewer-01": {"token": "reviewer-secret", "role": "code_reviewer"},
        }
        with patch.dict("os.environ", {"WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry)}, clear=True):
            principal = authenticate_worker("reviewer-secret")
            self.assertEqual((principal.actor_id, principal.role), ("reviewer-01", "code_reviewer"))
            with self.assertRaises(AuthenticationError):
                authenticate_worker("invalid")

    def test_invalid_worker_registry_fails_closed(self):
        with patch.dict("os.environ", {"WORKFORCE_WORKER_CREDENTIALS_JSON": "{broken"}, clear=True):
            with self.assertRaises(AuthenticationError):
                authenticate_worker("token")


if __name__ == "__main__":
    unittest.main()
