import tempfile
import unittest
from pathlib import Path

from workforce.agents.runner import Worker, safe_path


class AgentPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        (self.root / "engineering/workforce").mkdir(parents=True)
        (self.root / "docs/governance").mkdir(parents=True)
        (self.root / ".env").write_text("secret", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_safe_path_blocks_workspace_escape_and_secret_files(self):
        with self.assertRaises(ValueError):
            safe_path(self.root, "../../outside.txt")
        with self.assertRaises(ValueError):
            safe_path(self.root, ".env")

    def test_read_only_role_cannot_write(self):
        worker = Worker.__new__(Worker)
        worker.workspace = self.root
        worker.role = "code_reviewer"
        worker.permitted_paths = ("engineering/workforce",)
        result = worker.invoke_tool("write_file", {"path": "engineering/workforce/new.py", "content": "print('x')"})
        self.assertTrue(result.startswith("DENIED"))
        self.assertFalse((self.root / "engineering/workforce/new.py").exists())

    def test_builder_cannot_write_outside_allowlist_or_to_governance(self):
        worker = Worker.__new__(Worker)
        worker.workspace = self.root
        worker.role = "lead_builder"
        worker.permitted_paths = ("engineering/workforce/src",)
        denied = worker.invoke_tool("write_file", {"path": "docs/governance/policy.md", "content": "changed"})
        allowed = worker.invoke_tool("write_file", {"path": "engineering/workforce/src/new.py", "content": "pass\n"})
        self.assertTrue(denied.startswith("DENIED"))
        self.assertTrue(allowed.startswith("WROTE"))


if __name__ == "__main__":
    unittest.main()
