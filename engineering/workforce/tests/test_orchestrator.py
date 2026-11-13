import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workforce.orchestrator import (
    BUILDERS, ROLES, OrchestrationError, _task_brief, _task_contract, _worker_tokens,
    validate_manifest, workspace_manifest, run_work_package,
)


def valid_manifest():
    roles = {}
    for role in ROLES:
        paths = ["engineering/workforce/src/workforce"] if role == "lead_builder" else (
            ["engineering/workforce/tests"] if role == "specialist_builder" else []
        )
        roles[role] = {
            "task": f"Perform the {role} assignment with exact evidence.",
            "permitted_paths": paths,
            "context_files": [],
            "max_model_calls": 2,
            "max_tokens": 4000,
            "max_completion_tokens": 1024,
            "max_duration_minutes": 30,
        }
    return {
        "work_package_id": "WF-ORCHESTRATOR-TEST",
        "run_id": "wf-orchestrator-test",
        "authorization_ref": "director-approved-test-001",
        "objective": "Test the six-role orchestrator contract",
        "base_commit_sha": "a" * 40,
        "canonical_sources": ["workforce constitution"],
        "acceptance_criteria": ["all six role records exist"],
        "test_plan": ["orchestrator unit tests"],
        "review_plan": ["independent review"],
        "stop_conditions": ["budget exhausted"],
        "roles": roles,
    }


class OrchestratorTests(unittest.TestCase):
    def test_manifest_requires_exactly_six_roles(self):
        value = valid_manifest()
        del value["roles"]["negative_tester"]
        with self.assertRaises(OrchestrationError):
            validate_manifest(value)

    def test_agent_brief_contains_objective_acceptance_and_read_only_scope(self):
        value = valid_manifest()
        brief = _task_brief(value, "integration_verifier")
        self.assertIn(value["objective"], brief)
        self.assertIn(value["acceptance_criteria"][0], brief)
        self.assertIn(value["roles"]["integration_verifier"]["task"], brief)
        self.assertIn("READ-ONLY: no write paths", brief)
        self.assertIn(value["base_commit_sha"], brief)

    def test_manifest_rejects_shell_and_unapproved_test_commands(self):
        value = valid_manifest()
        value["test_commands"] = [["bash", "-c", "echo unsafe"]]
        with self.assertRaisesRegex(OrchestrationError, "not allowed"):
            validate_manifest(value)
        value["test_commands"] = [["python", "arbitrary_script.py"]]
        with self.assertRaisesRegex(OrchestrationError, "Python test commands"):
            validate_manifest(value)
        value["test_commands"] = [["/usr/bin/python", "-m", "unittest"]]
        with self.assertRaisesRegex(OrchestrationError, "not allowed"):
            validate_manifest(value)

    def test_manifest_accepts_explicit_cmake_and_ctest_commands(self):
        value = valid_manifest()
        value["test_commands"] = [
            ["cmake", "-S", "core/cpp", "-B", "build"],
            ["cmake", "--build", "build", "--parallel", "2"],
            ["ctest", "--test-dir", "build", "--output-on-failure"],
        ]
        self.assertEqual(validate_manifest(value)["test_commands"], value["test_commands"])

    def test_test_snapshot_copies_only_declared_inputs_and_skips_secrets(self):
        from workforce.orchestrator import _copy_test_snapshot
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = Path(source_dir)
            target = Path(target_dir)
            (source / "engineering/workforce/src").mkdir(parents=True)
            (source / "engineering/workforce/tests").mkdir(parents=True)
            (source / "core/cpp").mkdir(parents=True)
            (source / "engineering/workforce/src/module.py").write_text("value = 1\n", encoding="utf-8")
            (source / "engineering/workforce/tests/test_module.py").write_text("assert True\n", encoding="utf-8")
            (source / "core/cpp/main.cpp").write_text("int main() {}\n", encoding="utf-8")
            (source / "core/cpp/api_key.json").write_text("must not copy", encoding="utf-8")
            (source / "core/cpp/.env.production").write_text("must not copy", encoding="utf-8")
            _copy_test_snapshot(source, target, ["core/cpp"])
            self.assertTrue((target / "core/cpp/main.cpp").is_file())
            self.assertTrue((target / "engineering/workforce/src/module.py").is_file())
            self.assertFalse((target / "core/cpp/api_key.json").exists())
            self.assertFalse((target / "core/cpp/.env.production").exists())

    def test_manifest_rejects_non_string_base_sha(self):
        value = valid_manifest()
        value["base_commit_sha"] = ["a" * 40]
        with self.assertRaisesRegex(OrchestrationError, "full Git SHA"):
            validate_manifest(value)

    def test_integration_verifier_is_read_only(self):
        value = valid_manifest()
        value["roles"]["integration_verifier"]["permitted_paths"] = ["engineering/workforce"]
        with self.assertRaisesRegex(OrchestrationError, "integration_verifier is read-only"):
            validate_manifest(value)

    def test_manifest_rejects_unfilled_placeholders(self):
        value = valid_manifest()
        value["authorization_ref"] = "REPLACE_WITH_DIRECTOR_APPROVAL"
        with self.assertRaisesRegex(OrchestrationError, "placeholder"):
            validate_manifest(value)

    def test_manifest_reserves_time_for_evidence_finalization(self):
        value = valid_manifest()
        value["max_total_duration_minutes"] = 180
        with self.assertRaisesRegex(OrchestrationError, "five minutes"):
            validate_manifest(value)

    def test_manifest_caps_total_runtime_below_hosted_job_timeout(self):
        value = valid_manifest()
        value["max_total_duration_minutes"] = 331
        with self.assertRaisesRegex(OrchestrationError, "cleanup time"):
            validate_manifest(value)

    def test_manifest_rejects_role_durations_above_total_runtime(self):
        value = valid_manifest()
        value["max_total_duration_minutes"] = 100
        with self.assertRaisesRegex(OrchestrationError, "five minutes"):
            validate_manifest(value)

    def test_builder_write_scopes_must_be_disjoint(self):
        value = valid_manifest()
        value["roles"]["specialist_builder"]["permitted_paths"] = ["engineering/workforce"]
        with self.assertRaisesRegex(OrchestrationError, "overlap"):
            validate_manifest(value)

    def test_reviewers_cannot_receive_write_allowlists(self):
        value = valid_manifest()
        value["roles"]["code_reviewer"]["permitted_paths"] = ["engineering/workforce/tests"]
        with self.assertRaisesRegex(OrchestrationError, "read-only"):
            validate_manifest(value)

    def test_role_budgets_are_bounded(self):
        value = valid_manifest()
        value["roles"]["lead_builder"]["max_tokens"] = 200001
        with self.assertRaisesRegex(OrchestrationError, "max_tokens"):
            validate_manifest(value)

    def test_manifest_generates_a_unique_run_id(self):
        result = validate_manifest(valid_manifest())
        self.assertRegex(result["run_id"], r"^[A-Za-z0-9_-]{1,32}$")

    def test_task_contract_gives_read_only_roles_no_write_scope(self):
        value = validate_manifest(valid_manifest())
        contract = _task_contract(value, "code_reviewer")
        self.assertEqual(contract["permitted_paths"], [])
        self.assertEqual(contract["max_tokens"], 4000)

    def test_worker_registry_requires_one_strong_token_per_role(self):
        registry = {
            f"worker-{index}": {
                "token": f"worker-token-{index}-" + ("x" * 40),
                "role": role,
            }
            for index, role in enumerate(ROLES)
        }
        with patch.dict(os.environ, {"WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry)}, clear=True):
            result = _worker_tokens()
        self.assertEqual(set(result), set(ROLES))

    def test_worker_registry_rejects_missing_role(self):
        registry = {
            "worker-1": {"token": "x" * 40, "role": "lead_builder"},
        }
        with patch.dict(os.environ, {"WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry)}, clear=True):
            with self.assertRaisesRegex(OrchestrationError, "exactly one"):
                _worker_tokens()

    def test_full_orchestration_dry_run_creates_six_tasks_and_director_packet(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "engineering/workforce/src/workforce").mkdir(parents=True)
            (root / "engineering/workforce/tests").mkdir(parents=True)
            (root / "engineering/workforce/src/workforce/__init__.py").write_text("", encoding="utf-8")
            (root / "engineering/workforce/tests/__init__.py").write_text("", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Workforce Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()

            manifest = valid_manifest()
            manifest["base_commit_sha"] = base
            manifest["run_id"] = "test-run-001"
            registry = {
                f"worker-{index}": {"token": f"worker-token-{index}-" + ("x" * 40), "role": role}
                for index, role in enumerate(ROLES)
            }
            api_calls = []
            task_state = {}
            task_evidence = {}
            worker_ids = {entry["role"]: worker_id for worker_id, entry in registry.items()}
            agent_runs = []

            def fake_post(url, *, headers, payload):
                api_calls.append((url, headers, payload))
                if url.endswith("/v1/tasks"):
                    task_state[payload["task_id"]] = {
                        "task_id": payload["task_id"],
                        "role": payload["role"],
                        "state": "QUEUED",
                        "contract_json": payload["contract"],
                        "attempt_count": 0,
                    }
                    return {"task_id": payload["task_id"], "state": "QUEUED"}
                task_id = url.split("/v1/tasks/", 1)[1].split("/", 1)[0]
                target = payload.get("target")
                current = task_state[task_id]["state"]
                if target in {"TESTING", "REVIEWING", "INTEGRATION", "AWAITING_DIRECTOR"}:
                    stage = {
                        "TESTING": "CANDIDATE",
                        "REVIEWING": "TEST",
                        "INTEGRATION": "REVIEW_BUNDLE",
                        "AWAITING_DIRECTOR": "INTEGRATED",
                    }[target]
                    task_evidence.setdefault(task_id, []).append({
                        "stage": stage,
                        "sha256": payload["evidence_sha256"],
                        "evidence_ref": payload["evidence_ref"],
                        "actor": "orchestrator",
                        "attempt_count": task_state[task_id]["attempt_count"],
                    })
                task_state[task_id]["state"] = target if current != "AWAITING_DIRECTOR" else current
                return {"state": task_state[task_id]["state"]}

            def fake_get(url, *, headers, allow_404=False):
                if url.endswith("/evidence"):
                    task_id = url.split("/v1/tasks/", 1)[1].split("/", 1)[0]
                    return task_evidence.get(task_id, [])
                task_id = url.rsplit("/", 1)[-1]
                return task_state.get(task_id)

            real_run = subprocess.run
            def fake_run(command, **kwargs):
                if command and command[0] == "git":
                    return real_run(command, **kwargs)
                if "workforce.agents.runner" in command:
                    role = command[command.index("--role") + 1]
                    task_id = kwargs["env"]["WORKFORCE_TASK_ID"]
                    report_rel = command[command.index("--report-path") + 1]
                    report = root / report_rel
                    report.parent.mkdir(parents=True, exist_ok=True)
                    report.write_text(json.dumps({
                        "task_id": task_id,
                        "role": role,
                        "status": "CANDIDATE_READY",
                        "final": f"dry-run report for {role}",
                    }), encoding="utf-8")
                    if role == "lead_builder":
                        (root / "engineering/workforce/src/workforce/lead_output.py").write_text("value = 1\n", encoding="utf-8")
                    if role == "specialist_builder":
                        (root / "engineering/workforce/tests/generated_test.py").write_text("assert True\n", encoding="utf-8")
                    digest = hashlib.sha256(report.read_bytes()).hexdigest()
                    task_state[task_id]["state"] = "CANDIDATE_READY"
                    task_state[task_id]["attempt_count"] = 1
                    task_evidence[task_id] = [{
                        "stage": "WORKER_OUTPUT",
                        "actor": worker_ids[role],
                        "attempt_count": 1,
                        "sha256": digest,
                        "evidence_ref": report_rel,
                    }]
                    agent_runs.append(role)
                    return subprocess.CompletedProcess(command, 0, stdout="dry-run", stderr="")
                return subprocess.CompletedProcess(command, 0, stdout="tests passed", stderr="")

            with patch.dict(os.environ, {
                "WORKFORCE_CONTROL_PLANE_URL": "https://control.example",
                "DIRECTOR_APPROVAL_TOKEN": "d" * 40,
                "WORKFORCE_ORCHESTRATOR_TOKEN": "o" * 40,
                "WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps(registry),
                "GROQ_API_KEY": "not-used",
                "CLOUDFLARE_API_TOKEN": "not-used",
                "CLOUDFLARE_ACCOUNT_ID": "not-used",
                "WORKFORCE_TEST_DOCKER_IMAGE": "aurions-workforce-test-runner:unit",
            }, clear=True):
                with patch("workforce.orchestrator._post", side_effect=fake_post):
                    with patch("workforce.orchestrator._get", side_effect=fake_get):
                        with patch("workforce.orchestrator.subprocess.run", side_effect=fake_run):
                            result = run_work_package(
                                manifest,
                                root,
                                root / "engineering/workforce/.workforce-artifacts",
                            )
                            resumed = run_work_package(
                                manifest,
                                root,
                                root / "engineering/workforce/.workforce-artifacts",
                            )

            created = [call for call in api_calls if call[0].endswith("/v1/tasks")]
            transitions = [call for call in api_calls if call[0].endswith("/transition")]
            self.assertEqual(len(created), 6)
            self.assertEqual(len(transitions), 8)
            self.assertEqual(len(agent_runs), 6, "resume must not invoke any already-completed agent again")
            self.assertEqual(resumed["status"], "AWAITING_DIRECTOR_REVIEW")
            created_scopes = {call[2]["role"]: call[2]["contract"]["permitted_paths"] for call in created}
            self.assertEqual(created_scopes["lead_builder"], ["engineering/workforce/src/workforce"])
            self.assertEqual(created_scopes["specialist_builder"], ["engineering/workforce/tests"])
            for role in ("architecture_reviewer", "code_reviewer", "negative_tester", "integration_verifier"):
                self.assertEqual(created_scopes[role], [])
            self.assertEqual(result["status"], "AWAITING_DIRECTOR_REVIEW")
            self.assertTrue((root / result["director_packet"]).is_file())
            self.assertTrue((root / result["candidate_manifest"]).is_file())
            self.assertEqual(set(result["role_reports"]), set(ROLES))
            journal = root / "engineering/workforce/.workforce-artifacts/test-run-001-orchestration-state.json"
            self.assertTrue(journal.is_file())
            self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["status"], "AWAITING_DIRECTOR_REVIEW")

    def test_candidate_test_container_is_read_only_host_isolated_and_credential_filtered(self):
        from workforce.orchestrator import _docker_run
        with tempfile.TemporaryDirectory() as temp:
            with patch("workforce.orchestrator.subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess(["docker"], 0, stdout="ok", stderr="")
                _docker_run(
                    [sys.executable, "-m", "unittest", "discover"],
                    test_root=Path(temp),
                    environment={"PYTHONPATH": "/workspace/engineering/workforce/src", "CI": "1"},
                    image="trusted-test-image:ci",
                    network="internal-test-network",
                    timeout=30,
                )
                command = run.call_args.args[0]
                self.assertIn("--network", command)
                self.assertIn("internal-test-network", command)
                self.assertIn("--read-only", command)
                self.assertIn("--cap-drop=ALL", command)
                self.assertIn("--security-opt=no-new-privileges:true", command)
                self.assertIn("--pids-limit=128", command)
                self.assertIn("--memory=4g", command)
                self.assertIn("--cpus=2", command)
                self.assertIn("python3", command)
                self.assertNotIn("GROQ_API_KEY", " ".join(command))
                self.assertNotIn("CLOUDFLARE_API_TOKEN", " ".join(command))

    def test_candidate_test_container_rejects_provider_credentials(self):
        from workforce.orchestrator import _docker_run
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(OrchestrationError, "unapproved variable"):
                _docker_run(
                    ["python3", "-m", "unittest"],
                    test_root=Path(temp),
                    environment={"GROQ_API_KEY": "must-never-enter-test"},
                    image="trusted-test-image:ci",
                    network="internal-test-network",
                    timeout=30,
                )

    def test_evidence_digest_verification_detects_tampering(self):
        from workforce.orchestrator import _verify_artifact_digest
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = root / "report.json"
            artifact.write_text('{"status":"ok"}', encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            verified = _verify_artifact_digest(root, "report.json", digest)
            self.assertTrue(verified["verified"])
            artifact.write_text('{"status":"altered"}', encoding="utf-8")
            with self.assertRaisesRegex(OrchestrationError, "digest mismatch"):
                _verify_artifact_digest(root, "report.json", digest)

    def test_candidate_file_verification_detects_post_snapshot_changes(self):
        from workforce.orchestrator import _verify_candidate_files
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate = root / "src/example.py"
            candidate.parent.mkdir()
            candidate.write_text("value = 1\n", encoding="utf-8")
            raw = candidate.read_bytes()
            records = [{
                "path": "src/example.py",
                "status": "present",
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }]
            self.assertTrue(_verify_candidate_files(root, records)[0]["verified"])
            candidate.write_text("value = 2\n", encoding="utf-8")
            with self.assertRaisesRegex(OrchestrationError, "changed after snapshot"):
                _verify_candidate_files(root, records)

    def test_workspace_manifest_hashes_only_scoped_candidate_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "engineering/workforce/src/workforce").mkdir(parents=True)
            source = root / "engineering/workforce/src/workforce/example.py"
            source.write_text("original = True\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Workforce Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            source.write_text("original = False\n", encoding="utf-8")
            (root / "engineering/workforce/tests").mkdir(parents=True)
            (root / "engineering/workforce/tests/new_test.py").write_text("assert True\n", encoding="utf-8")
            (root / ".workforce-artifacts").mkdir()
            (root / ".workforce-artifacts/report.json").write_text("{}\n", encoding="utf-8")
            records = workspace_manifest(
                root, base,
                ["engineering/workforce/src/workforce", "engineering/workforce/tests"],
            )
            self.assertEqual({record["path"] for record in records}, {
                "engineering/workforce/src/workforce/example.py",
                "engineering/workforce/tests/new_test.py",
            })
            self.assertTrue(all(record["sha256"] for record in records))

    def test_workspace_manifest_rejects_out_of_scope_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "engineering/workforce/src/workforce").mkdir(parents=True)
            source = root / "engineering/workforce/src/workforce/example.py"
            source.write_text("value = 1\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Workforce Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            (root / "src").mkdir()
            (root / "src/unauthorized.py").write_text("bad = True\n", encoding="utf-8")
            with self.assertRaisesRegex(OrchestrationError, "outside builder write scopes"):
                workspace_manifest(root, base, ["engineering/workforce/src/workforce"])


if __name__ == "__main__":
    unittest.main()
