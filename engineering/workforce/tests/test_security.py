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
            "DIRECTOR_APPROVAL_TOKEN": "dddddddddddddddddddddddddddddddddddddddd",
            "WORKFORCE_ORCHESTRATOR_TOKEN": "oooooooooooooooooooooooooooooooooooooooo",
        }, clear=True):
            self.assertEqual(require_director("dddddddddddddddddddddddddddddddddddddddd").role, "director")
            self.assertEqual(require_orchestrator("oooooooooooooooooooooooooooooooooooooooo").role, "orchestrator")
            with self.assertRaises(AuthenticationError):
                require_director("oooooooooooooooooooooooooooooooooooooooo")
            with self.assertRaises(AuthenticationError):
                require_orchestrator("dddddddddddddddddddddddddddddddddddddddd")

    def test_director_and_orchestrator_tokens_must_be_distinct(self):
        shared = "shared-authority-token-" + ("x" * 40)
        with patch.dict("os.environ", {
            "DIRECTOR_APPROVAL_TOKEN": shared,
            "WORKFORCE_ORCHESTRATOR_TOKEN": shared,
        }, clear=True):
            with self.assertRaises(AuthenticationError):
                require_director(shared)
            with self.assertRaises(AuthenticationError):
                require_orchestrator(shared)

    def test_worker_token_cannot_be_reused_for_director_authority(self):
        shared = "shared-worker-director-token-" + ("x" * 40)
        registry = {
            "builder-01": {"token": shared, "role": "lead_builder"},
        }
        with patch.dict("os.environ", {
            "DIRECTOR_APPROVAL_TOKEN": shared,
            "WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry),
        }, clear=True):
            with self.assertRaises(AuthenticationError):
                require_director(shared)
            with self.assertRaises(AuthenticationError):
                authenticate_worker(shared)

    def test_worker_identity_and_role_are_derived_from_secret_registry(self):
        registry = {
            "builder-01": {"token": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "role": "lead_builder"},
            "reviewer-01": {"token": "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", "role": "code_reviewer"},
        }
        with patch.dict("os.environ", {"WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry)}, clear=True):
            principal = authenticate_worker("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
            self.assertEqual((principal.actor_id, principal.role), ("reviewer-01", "code_reviewer"))
            with self.assertRaises(AuthenticationError):
                authenticate_worker("invalid")

    def test_weak_actor_secrets_are_rejected(self):
        with patch.dict("os.environ", {"DIRECTOR_APPROVAL_TOKEN": "short"}, clear=True):
            with self.assertRaises(AuthenticationError):
                require_director("short")

    def test_duplicate_worker_tokens_are_rejected(self):
        registry = {
            "worker-a": {"token": "same-token-value-that-is-long-enough-0001", "role": "lead_builder"},
            "worker-b": {"token": "same-token-value-that-is-long-enough-0001", "role": "code_reviewer"},
        }
        with patch.dict("os.environ", {"WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry)}, clear=True):
            with self.assertRaises(AuthenticationError):
                authenticate_worker("same-token-value-that-is-long-enough-0001")

    def test_invalid_worker_registry_fails_closed(self):
        with patch.dict("os.environ", {"WORKFORCE_WORKER_CREDENTIALS_JSON": "{broken"}, clear=True):
            with self.assertRaises(AuthenticationError):
                authenticate_worker("token")


if __name__ == "__main__":
    unittest.main()
