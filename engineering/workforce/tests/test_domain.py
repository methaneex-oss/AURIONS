import unittest
from workforce.domain import ContractError, TaskContract, TaskState, TransitionError, path_is_permitted, validate_transition


class DomainTests(unittest.TestCase):
    def test_acceptance_requires_director_decision(self):
        with self.assertRaises(TransitionError):
            validate_transition(TaskState.AWAITING_DIRECTOR, TaskState.ACCEPTED)
        validate_transition(TaskState.AWAITING_DIRECTOR, TaskState.ACCEPTED, director_decision=True)

    def test_invalid_transition_rejected(self):
        with self.assertRaises(TransitionError):
            validate_transition(TaskState.QUEUED, TaskState.ACCEPTED, director_decision=True)

    def test_retry_recovery_can_reclaim_after_backoff(self):
        validate_transition(TaskState.RETRY_WAIT, TaskState.CLAIMED)

    def test_checkpointed_lease_can_be_recovered(self):
        validate_transition(TaskState.CHECKPOINTED, TaskState.RETRY_WAIT)

    def test_path_policy_blocks_traversal_and_prohibited_paths(self):
        permitted = ("engineering/workforce",)
        prohibited = ("docs/governance", "src/aurions")
        self.assertTrue(path_is_permitted("engineering/workforce/src/api.py", permitted, prohibited))
        self.assertFalse(path_is_permitted("docs/governance/policy.md", permitted, prohibited))
        self.assertFalse(path_is_permitted("engineering/workforce/../../main.py", permitted, prohibited))

    def test_path_policy_blocks_windows_traversal_and_absolute_paths(self):
        permitted = ("engineering/workforce",)
        separator = chr(92)
        windows_traversal = "engineering" + separator + "workforce" + separator + ".." + separator + ".." + separator + "main.py"
        windows_absolute = "C:" + separator + "repo" + separator + "main.py"
        self.assertFalse(path_is_permitted(windows_traversal, permitted, ()))
        self.assertFalse(path_is_permitted(windows_absolute, permitted, ()))
        self.assertFalse(path_is_permitted("/etc/passwd", permitted, ()))

    def test_task_contract_accepts_complete_authorized_contract(self):
        value = {
            "work_package_id": "WF-01", "authorization_ref": "director-approval-001",
            "objective": "Build workforce control plane", "base_commit_sha": "a" * 40,
            "permitted_paths": ["engineering/workforce"], "prohibited_paths": ["docs/governance", "src/aurions"],
            "canonical_sources": ["docs/workforce/WORKFORCE-CONSTITUTION.md"],
            "acceptance_criteria": ["unit tests pass"], "test_plan": ["unit tests"],
            "review_plan": ["independent review"], "max_model_calls": 20,
            "max_tokens": 100000, "max_duration_minutes": 120, "stop_conditions": ["budget exhausted"]
        }
        self.assertEqual(TaskContract.from_dict(value).work_package_id, "WF-01")

    def test_contract_rejects_resource_budget_above_hard_ceiling(self):
        value = {
            "work_package_id": "WF-01", "authorization_ref": "director-approval-001", "objective": "Build",
            "base_commit_sha": "a" * 40, "permitted_paths": ["engineering/workforce"],
            "prohibited_paths": ["src/aurions"], "canonical_sources": ["constitution"],
            "acceptance_criteria": ["tests"], "test_plan": ["unit"], "review_plan": ["review"],
            "max_model_calls": 101, "max_tokens": 100, "max_duration_minutes": 1,
            "stop_conditions": ["budget"]
        }
        with self.assertRaises(ContractError):
            TaskContract.from_dict(value)

    def test_contract_rejects_missing_authorization(self):
        value = {
            "work_package_id": "WF-01", "authorization_ref": "UNSET", "objective": "Build",
            "base_commit_sha": "a" * 40, "permitted_paths": ["engineering/workforce"],
            "prohibited_paths": ["src/aurions"], "canonical_sources": ["constitution"],
            "acceptance_criteria": ["tests"], "test_plan": ["unit"], "review_plan": ["review"],
            "max_model_calls": 1, "max_tokens": 100, "max_duration_minutes": 1,
            "stop_conditions": ["budget"]
        }
        with self.assertRaises(ContractError):
            TaskContract.from_dict(value)


if __name__ == "__main__":
    unittest.main()
