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

    def test_path_policy_blocks_traversal_and_prohibited_paths(self):
        permitted = ("engineering/workforce",)
        prohibited = ("docs/governance", "src/aurions")
        self.assertTrue(path_is_permitted("engineering/workforce/src/api.py", permitted, prohibited))
        self.assertFalse(path_is_permitted("docs/governance/policy.md", permitted, prohibited))
        self.assertFalse(path_is_permitted("engineering/workforce/../../main.py", permitted, prohibited))

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
