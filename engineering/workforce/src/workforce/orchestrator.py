"""Bounded six-role work-package orchestrator.

Runs roles sequentially against one pinned workspace and one durable control plane.
It never commits, pushes, merges, or grants builders repository credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

from workforce.agents.runner import ROLE_INSTRUCTIONS, is_sensitive_path, safe_path
from workforce.domain import path_is_permitted

ROLES = tuple(ROLE_INSTRUCTIONS)
BUILDERS = ("lead_builder", "specialist_builder")
REVIEWERS = ("architecture_reviewer", "code_reviewer", "negative_tester")
MAX_REPORT_BYTES = 1_000_000


class OrchestrationError(RuntimeError):
    pass


def _path_overlap(left: str, right: str) -> bool:
    a = left.replace(chr(92), "/").strip("/")
    b = right.replace(chr(92), "/").strip("/")
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OrchestrationError("manifest root must be a JSON object")
    required = (
        "work_package_id", "authorization_ref", "objective", "base_commit_sha",
        "canonical_sources", "acceptance_criteria", "test_plan", "review_plan",
        "stop_conditions", "roles",
    )
    missing = [key for key in required if key not in value]
    if missing:
        raise OrchestrationError("manifest is missing: " + ", ".join(missing))
    for key in ("work_package_id", "authorization_ref", "objective"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise OrchestrationError(f"{key} must be a non-empty string")
        if value[key].strip().upper().startswith("REPLACE_"):
            raise OrchestrationError(f"{key} still contains a template placeholder")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(value["base_commit_sha"])) or set(value["base_commit_sha"]) == {"0"}:
        raise OrchestrationError("base_commit_sha must be a real full Git SHA")
    if not isinstance(value["roles"], dict) or set(value["roles"]) != set(ROLES):
        raise OrchestrationError("manifest must define each of the six roles exactly once")
    for key in ("canonical_sources", "acceptance_criteria", "test_plan", "review_plan", "stop_conditions"):
        if not isinstance(value[key], list) or not value[key] or not all(isinstance(x, str) and x.strip() for x in value[key]):
            raise OrchestrationError(f"{key} must be a non-empty list of strings")
    max_total = value.get("max_total_duration_minutes", 330)
    if not isinstance(max_total, int) or isinstance(max_total, bool) or not 1 <= max_total <= 330:
        raise OrchestrationError("max_total_duration_minutes must be between 1 and 330 to preserve workflow cleanup time")
    value["max_total_duration_minutes"] = max_total
    test_paths = value.get("test_paths", ["engineering/workforce/src", "engineering/workforce/tests"])
    if not isinstance(test_paths, list) or not test_paths or not all(
        isinstance(path, str) and path_is_permitted(path, (path,), ()) for path in test_paths
    ):
        raise OrchestrationError("test_paths must be a non-empty list of safe repository-relative paths")
    value["test_paths"] = test_paths
    test_commands = value.get("test_commands", [])
    if not isinstance(test_commands, list):
        raise OrchestrationError("test_commands must be a list of argument arrays")
    allowed_commands = {"python", "python3", "pytest", "cmake", "ctest", "ninja", "cargo", "go", "dotnet"}
    for command in test_commands:
        if not isinstance(command, list) or not command or not all(isinstance(arg, str) and arg for arg in command):
            raise OrchestrationError("each test command must be a non-empty argument array")
        executable = Path(command[0]).name
        if executable not in allowed_commands:
            raise OrchestrationError(f"test executable is not allowed: {executable}")
        if executable in {"python", "python3"} and (len(command) < 3 or command[1] != "-m" or command[2] not in {"unittest", "pytest", "compileall"}):
            raise OrchestrationError("Python test commands must use unittest, pytest or compileall modules")
        if executable == "cmake" and (len(command) < 2 or command[1] not in {"-S", "--build"}):
            raise OrchestrationError("CMake commands must configure with -S or build with --build")
        if executable == "ctest" and (len(command) < 2 or command[1] != "--test-dir"):
            raise OrchestrationError("CTest commands must specify --test-dir")
        if executable == "ninja" and (len(command) < 2 or command[1] != "-C"):
            raise OrchestrationError("Ninja commands must specify -C")
        if executable in {"cargo", "go", "dotnet"} and (len(command) < 2 or command[1] != "test"):
            raise OrchestrationError(f"{executable} commands must use the test subcommand")
        if any(re.search(r"(?:password|passwd|secret|token|api[_-]?key)", arg, re.IGNORECASE) for arg in command[1:]):
            raise OrchestrationError("test commands must not embed credentials or secret-like arguments")
    value["test_commands"] = test_commands
    default_durations = {
        "lead_builder": 120, "specialist_builder": 60,
        "architecture_reviewer": 30, "code_reviewer": 30,
        "negative_tester": 30, "integration_verifier": 45,
    }
    for role in ROLES:
        spec = value["roles"][role]
        if not isinstance(spec, dict) or not isinstance(spec.get("task"), str) or not spec["task"].strip():
            raise OrchestrationError(f"{role} requires a non-empty task instruction")
        if spec["task"].strip().upper().startswith("REPLACE_"):
            raise OrchestrationError(f"{role} task still contains a template placeholder")
        paths = spec.get("permitted_paths", [])
        contexts = spec.get("context_files", [])
        if not isinstance(paths, list) or not all(isinstance(x, str) and x.strip() for x in paths):
            raise OrchestrationError(f"{role}.permitted_paths must be a list of non-empty strings")
        if role in BUILDERS and not paths:
            raise OrchestrationError(f"{role} must have an explicit write allowlist")
        if any(not path_is_permitted(path, (path,), ()) for path in paths):
            raise OrchestrationError(f"{role} contains an unsafe or non-relative write path")
        if role in REVIEWERS and paths:
            raise OrchestrationError(f"{role} is read-only and must not receive write paths")
        if not isinstance(contexts, list) or not all(isinstance(x, str) and x.strip() for x in contexts):
            raise OrchestrationError(f"{role}.context_files must be a list of non-empty strings")
        for field, default, ceiling in (
            ("max_model_calls", 8, 100),
            ("max_tokens", 16000, 200000),
            ("max_completion_tokens", 3072, 32768),
            ("max_duration_minutes", default_durations[role], 360),
        ):
            number = spec.get(field, default)
            if not isinstance(number, int) or isinstance(number, bool) or number < 1 or number > ceiling:
                raise OrchestrationError(f"{role}.{field} must be between 1 and {ceiling}")
    total_role_minutes = sum(value["roles"][role].get("max_duration_minutes", default_durations[role]) for role in ROLES)
    if total_role_minutes + 5 > max_total:
        raise OrchestrationError("role duration ceilings must leave at least five minutes for verification and evidence finalization")
    left = value["roles"]["lead_builder"]["permitted_paths"]
    right = value["roles"]["specialist_builder"]["permitted_paths"]
    for a in left:
        for b in right:
            if _path_overlap(a, b):
                raise OrchestrationError(f"builder write scopes overlap: {a!r} and {b!r}")
    value.setdefault("run_id", uuid.uuid4().hex[:12])
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", str(value["run_id"])) or str(value["run_id"]).upper().startswith("REPLACE_"):
        raise OrchestrationError("run_id must be a unique non-placeholder identifier (max 32 characters)")
    return value


def _post(url: str, *, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    response = httpx.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code >= 400:
        raise OrchestrationError(f"control-plane request failed (HTTP {response.status_code})")
    data = response.json()
    if not isinstance(data, dict):
        raise OrchestrationError("control plane returned a non-object response")
    return data


def _worker_tokens() -> dict[str, tuple[str, str]]:
    try:
        registry = json.loads(os.environ["WORKFORCE_WORKER_CREDENTIALS_JSON"])
    except (KeyError, json.JSONDecodeError) as exc:
        raise OrchestrationError("WORKFORCE_WORKER_CREDENTIALS_JSON must contain the six role credentials") from exc
    if not isinstance(registry, dict):
        raise OrchestrationError("worker credential registry must be a JSON object")
    result: dict[str, tuple[str, str]] = {}
    seen_tokens: set[str] = set()
    for worker_id, item in registry.items():
        if not isinstance(item, dict):
            raise OrchestrationError("worker credential entries must be objects")
        token, role = item.get("token"), item.get("role")
        if not isinstance(token, str) or len(token) < 32 or role not in ROLES:
            raise OrchestrationError("worker credentials must have a strong token and a known role")
        if role in result:
            raise OrchestrationError(f"more than one worker credential is configured for {role}")
        if token in seen_tokens:
            raise OrchestrationError("worker credentials must use distinct tokens")
        seen_tokens.add(token)
        result[role] = (worker_id, token)
    if set(result) != set(ROLES):
        raise OrchestrationError("exactly one worker credential is required for each of the six roles")
    director = os.environ.get("DIRECTOR_APPROVAL_TOKEN", "")
    orchestrator = os.environ.get("WORKFORCE_ORCHESTRATOR_TOKEN", "")
    if director or orchestrator:
        if len(director) < 32 or len(orchestrator) < 32 or director == orchestrator:
            raise OrchestrationError("Director and orchestrator credentials must be distinct strong tokens")
    privileged = [director, orchestrator]
    if any(token == value for _, token in result.values() for value in privileged if value):
        raise OrchestrationError("worker credentials must be distinct from Director and orchestrator credentials")
    return result


def _task_contract(manifest: dict[str, Any], role: str) -> dict[str, Any]:
    spec = manifest["roles"][role]
    return {
        "work_package_id": manifest["work_package_id"],
        "authorization_ref": manifest["authorization_ref"],
        "objective": manifest["objective"],
        "base_commit_sha": manifest["base_commit_sha"],
        "permitted_paths": spec["permitted_paths"] or ["engineering/workforce"],
        "prohibited_paths": ["docs/governance", "docs/workforce", "src/aurions", "core", ".github/workflows"],
        "canonical_sources": manifest["canonical_sources"],
        "acceptance_criteria": manifest["acceptance_criteria"],
        "test_plan": manifest["test_plan"],
        "review_plan": manifest["review_plan"],
        "max_model_calls": spec.get("max_model_calls", 8),
        "max_tokens": spec.get("max_tokens", 16000),
        "max_duration_minutes": spec.get("max_duration_minutes", {
            "lead_builder": 120, "specialist_builder": 60,
            "architecture_reviewer": 30, "code_reviewer": 30,
            "negative_tester": 30, "integration_verifier": 45,
        }[role]),
        "deadline": manifest.get("deadline", "UNSET"),
        "stop_conditions": manifest["stop_conditions"],
    }


def _git(root: Path, args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, timeout=20, check=False,
    )
    if result.returncode:
        raise OrchestrationError("Git evidence command failed: " + result.stderr.decode("utf-8", "replace")[-1000:])
    return result.stdout


def workspace_manifest(root: Path, base_sha: str, permitted_builder_paths: list[str]) -> list[dict[str, Any]]:
    changed = set(filter(None, _git(root, ["diff", "--name-only", "-z", base_sha]).decode().split("\0")))
    untracked = set(filter(None, _git(root, ["ls-files", "--others", "--exclude-standard", "-z"]).decode().split("\0")))
    paths = sorted(p for p in changed | untracked if ".workforce-artifacts" not in p.split("/"))
    records: list[dict[str, Any]] = []
    for rel in paths:
        if not path_is_permitted(rel, tuple(permitted_builder_paths), ()):
            raise OrchestrationError(f"candidate contains a file outside builder write scopes: {rel}")
        path = (root / rel).resolve()
        if path != root and root not in path.parents:
            raise OrchestrationError(f"candidate path escapes workspace: {rel}")
        if path.is_file():
            raw = path.read_bytes()
            records.append({"path": rel, "status": "present", "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        else:
            records.append({"path": rel, "status": "deleted", "bytes": 0, "sha256": None})
    return records


def _copy_test_snapshot(root: Path, destination: Path, test_paths: list[str]) -> None:
    selected = list(dict.fromkeys(["engineering/workforce/src", "engineering/workforce/tests", *test_paths]))
    excluded_dirs = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".workforce-artifacts", ".aws", ".ssh", ".gnupg"}
    for relative in selected:
        original = root / relative
        if original.is_symlink():
            raise OrchestrationError(f"test input must not be a symlink: {relative}")
        source = safe_path(root, relative)
        if not source.exists():
            raise OrchestrationError(f"declared test input does not exist: {relative}")
        if source.is_file():
            if is_sensitive_path(source):
                raise OrchestrationError(f"test input is classified as sensitive: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            continue
        for current, directories, files in os.walk(source, topdown=True, followlinks=False):
            current_path = Path(current)
            directories[:] = [
                name for name in directories
                if name not in excluded_dirs
                and not (current_path / name).is_symlink()
                and not is_sensitive_path(current_path / name)
            ]
            relative_dir = current_path.relative_to(root)
            target_dir = destination / relative_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            for name in files:
                source_file = current_path / name
                if source_file.is_symlink() or is_sensitive_path(source_file):
                    continue
                target_file = target_dir / name
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)


def run_work_package(manifest: dict[str, Any], workspace: Path, report_dir: Path) -> dict[str, Any]:
    manifest = validate_manifest(manifest)
    root = workspace.resolve()
    report_dir = report_dir.resolve()
    if root not in report_dir.parents:
        raise OrchestrationError("report directory must be inside the workspace")
    report_rel = report_dir.relative_to(root).as_posix()
    if ".workforce-artifacts" not in report_rel.split("/"):
        raise OrchestrationError("report directory must be under an ignored .workforce-artifacts directory")
    control = os.environ.get("WORKFORCE_CONTROL_PLANE_URL", "").rstrip("/")
    director = os.environ.get("DIRECTOR_APPROVAL_TOKEN", "")
    orchestrator = os.environ.get("WORKFORCE_ORCHESTRATOR_TOKEN", "")
    if not all((control, director, orchestrator)):
        raise OrchestrationError("control-plane URL, Director token and orchestrator token are required")
    workers = _worker_tokens()
    actual_base = _git(root, ["rev-parse", "HEAD"]).decode().strip()
    if _git(root, ["status", "--porcelain", "--untracked-files=all"]).strip():
        raise OrchestrationError("workspace must be clean before the authorized work package starts")
    if actual_base.lower() != manifest["base_commit_sha"].lower():
        raise OrchestrationError(f"workspace HEAD {actual_base} does not match authorized base SHA")
    report_dir.mkdir(parents=True, exist_ok=True)
    headers = {"X-Orchestrator-Token": orchestrator, "X-Director-Approval-Token": director}
    task_ids = {role: f"wf-{manifest['run_id']}-{role}" for role in ROLES}
    created: set[str] = set()
    completed: set[str] = set()

    reports: dict[str, dict[str, Any]] = {};
    orchestration_started = time.monotonic()
    orchestration_budget_seconds = manifest["max_total_duration_minutes"] * 60

    def remaining_orchestration_seconds() -> float:
        return orchestration_budget_seconds - (time.monotonic() - orchestration_started)

    def run_role(role: str, extra_context: list[str] | None = None) -> None:
        spec = manifest["roles"][role]
        # Create each role task immediately before dispatch. Later roles remain
        # absent rather than sitting in QUEUED while earlier agents work.
        if role not in created:
            _post(f"{control}/v1/tasks", headers=headers, payload={
                "task_id": task_ids[role], "role": role, "contract": _task_contract(manifest, role),
            })
            created.add(role)
        worker_id, worker_token = workers[role]
        from workforce.model_registry import role_assignment
        profile = role_assignment(role)
        # Workers receive only their own role token and the one provider credential
        # required by their pinned model. Director/orchestrator/other-agent secrets
        # never enter the model worker process.
        env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", str(root)),
            "PYTHONPATH": str(root / "engineering/workforce/src"),
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "CI": os.environ.get("CI", "0"),
            "WORKFORCE_CONTROL_PLANE_URL": control,
            "WORKFORCE_TASK_ID": task_ids[role],
            "WORKFORCE_WORKER_TOKEN": worker_token,
            profile["key_env"]: os.environ.get(profile["key_env"], ""),
        }
        if profile["account_env"]:
            env[profile["account_env"]] = os.environ.get(profile["account_env"], "")
        report_path = report_dir / f"{manifest['run_id']}-{role}.json"
        remaining_seconds = remaining_orchestration_seconds()
        if remaining_seconds < 60:
            raise OrchestrationError("work-package wall-clock budget exhausted before next role")
        role_minutes = min(
            spec.get("max_duration_minutes", {
                "lead_builder": 120, "specialist_builder": 60,
                "architecture_reviewer": 30, "code_reviewer": 30,
                "negative_tester": 30, "integration_verifier": 45,
            }[role]),
            max(1, int((remaining_seconds - 15) // 60)),
        )
        command = [
            sys.executable, "-m", "workforce.agents.runner",
            "--role", role, "--task", spec["task"], "--workspace", str(root),
            "--max-calls", str(spec.get("max_model_calls", 8)),
            "--max-tokens", str(spec.get("max_completion_tokens", 3072)),
            "--max-total-tokens", str(spec.get("max_tokens", 16000)),
            "--max-duration-minutes", str(role_minutes),
            "--report-path", report_path.relative_to(root).as_posix(),
        ]
        for path in spec["permitted_paths"]:
            command.extend(["--permitted-path", path])
        from workforce.agents.runner import safe_path
        for path in spec["context_files"] + (extra_context or []):
            context_path = safe_path(root, path)
            if not context_path.is_file():
                raise OrchestrationError(f"{role} context file does not exist: {path}")
            command.extend(["--context-file", path])
        try:
            result = subprocess.run(
                command, cwd=root, env=env, capture_output=True, text=True,
                timeout=min(role_minutes * 60 + 15, max(1, remaining_seconds - 5)), check=False,
            )
        except subprocess.TimeoutExpired as exc:
            try:
                _post(f"{control}/v1/tasks/{task_ids[role]}/transition",
                      headers={"X-Orchestrator-Token": orchestrator},
                      payload={"target": "FAILED", "reason": "orchestrator process timeout; lease fenced"})
            finally:
                raise OrchestrationError(f"{role} exceeded its wall-clock execution limit") from exc
        if result.returncode != 0:
            raise OrchestrationError(
                f"{role} failed (exit {result.returncode}); report: {report_path}; "
                f"stderr: {result.stderr[-1200:]}"
            )
        if not report_path.is_file() or report_path.stat().st_size > MAX_REPORT_BYTES:
            raise OrchestrationError(f"{role} did not produce a bounded report artifact")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("task_id") != task_ids[role] or report.get("status") != "CANDIDATE_READY":
            raise OrchestrationError(f"{role} report identity/status mismatch")
        reports[role] = {
            "task_id": task_ids[role],
            "worker_id": worker_id,
            "report_ref": report_path.relative_to(root).as_posix(),
            "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "status": "CANDIDATE_READY",
        }
        completed.add(role)

    try:
        # Builders work sequentially in disjoint path scopes. Reviewers only see
        # the frozen candidate and test evidence produced after both builders.
        for role in BUILDERS:
            run_role(role)

        builder_paths = manifest["roles"]["lead_builder"]["permitted_paths"] + manifest["roles"]["specialist_builder"]["permitted_paths"]
        candidate_files = workspace_manifest(root, manifest["base_commit_sha"], builder_paths)
        candidate = {
            "run_id": manifest["run_id"],
            "work_package_id": manifest["work_package_id"],
            "base_commit_sha": manifest["base_commit_sha"],
            "candidate_files": candidate_files,
            "builder_reports": {r: reports[r] for r in BUILDERS},
        }
        candidate_path = report_dir / f"{manifest['run_id']}-candidate-manifest.json"
        candidate_bytes = json.dumps(candidate, indent=2).encode("utf-8")
        candidate_path.write_bytes(candidate_bytes)
        candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()

        # Never point the test suite at the live control-plane database. Full
        # PostgreSQL tests run only when an explicit disposable test DB is supplied.
        test_env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(root / "engineering/workforce/src"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "CI": "1",
        }
        test_database = os.environ.get("WORKFORCE_TEST_DATABASE_URL", "")
        if test_database:
            required_test = (
                "WORKFORCE_TEST_DIRECTOR_TOKEN",
                "WORKFORCE_TEST_ORCHESTRATOR_TOKEN",
                "WORKFORCE_TEST_WORKER_CREDENTIALS_JSON",
            )
            missing = [key for key in required_test if not os.environ.get(key)]
            if missing:
                raise OrchestrationError("disposable integration DB requires: " + ", ".join(missing))
            test_env.update({
                "DATABASE_URL": test_database,
                "DIRECTOR_APPROVAL_TOKEN": os.environ["WORKFORCE_TEST_DIRECTOR_TOKEN"],
                "WORKFORCE_ORCHESTRATOR_TOKEN": os.environ["WORKFORCE_TEST_ORCHESTRATOR_TOKEN"],
                "WORKFORCE_WORKER_CREDENTIALS_JSON": os.environ["WORKFORCE_TEST_WORKER_CREDENTIALS_JSON"],
            })
        test_commands = [
            [sys.executable, "-m", "compileall", "-q", "engineering/workforce/src", "engineering/workforce/tests"],
            [sys.executable, "-m", "unittest", "discover", "-s", "engineering/workforce/tests", "-v"],
        ]
        test_results = []
        # Run the suite against a read-only-intent snapshot, not the live candidate
        # workspace. Test code cannot mutate the candidate or access its credentials.
        with tempfile.TemporaryDirectory(prefix="workforce-package-tests-") as test_dir:
            test_root = Path(test_dir)
            _copy_test_snapshot(root, test_root, manifest["test_paths"])
            test_env["PYTHONPATH"] = str(test_root / "engineering/workforce/src")
            test_env["HOME"] = str(test_root)
            test_env["TMPDIR"] = str(test_root)
            test_env["CARGO_HOME"] = str(test_root / ".cargo")
            test_env["GOCACHE"] = str(test_root / ".go-cache")
            test_env["CMAKE_BUILD_PARALLEL_LEVEL"] = "2"
            test_commands.extend(manifest["test_commands"])
            for command in test_commands:
                test_remaining = remaining_orchestration_seconds()
                if test_remaining < 10:
                    raise OrchestrationError("work-package wall-clock budget exhausted before test execution")
                run = subprocess.run(
                    command, cwd=test_root, env=test_env, capture_output=True, text=True,
                    timeout=max(1, min(300, test_remaining - 5)), check=False,
                )
                test_results.append({
                    "command": command[1:],
                    "returncode": run.returncode,
                    "stdout": run.stdout[-12000:],
                    "stderr": run.stderr[-12000:],
                })
                if run.returncode:
                    raise OrchestrationError("candidate test suite failed; no reviewer or integration task will proceed")
        test_report = report_dir / f"{manifest['run_id']}-test-results.json"
        test_bytes = json.dumps(test_results, indent=2).encode("utf-8")
        test_report.write_bytes(test_bytes)
        test_sha = hashlib.sha256(test_bytes).hexdigest()

        shared_context = [
            candidate_path.relative_to(root).as_posix(),
            test_report.relative_to(root).as_posix(),
        ]
        for role in REVIEWERS:
            run_role(role, shared_context)

        integration_context = shared_context + [reports[r]["report_ref"] for r in REVIEWERS]
        run_role("integration_verifier", integration_context)

        review_records = [reports[r] for r in REVIEWERS]
        review_bundle = json.dumps(review_records, sort_keys=True, separators=(",", ":")).encode()
        review_path = report_dir / f"{manifest['run_id']}-review-bundle.json"
        review_path.write_bytes(review_bundle)
        review_sha = hashlib.sha256(review_bundle).hexdigest()
        integrated = {
            "run_id": manifest["run_id"],
            "work_package_id": manifest["work_package_id"],
            "base_commit_sha": manifest["base_commit_sha"],
            "candidate_manifest_sha256": candidate_sha,
            "test_results_sha256": test_sha,
            "review_reports": review_records,
            "integration_verifier_report": reports["integration_verifier"],
            "status": "AWAITING_DIRECTOR_REVIEW",
        }
        integrated_path = report_dir / f"{manifest['run_id']}-director-packet.json"
        integrated_bytes = json.dumps(integrated, indent=2).encode("utf-8")
        integrated_path.write_bytes(integrated_bytes)
        integrated_sha = hashlib.sha256(integrated_bytes).hexdigest()

        integration_task = task_ids["integration_verifier"]
        transitions = [
            ("TESTING", "candidate evidence recorded", candidate_sha, candidate_path.relative_to(root).as_posix()),
            ("REVIEWING", "test evidence recorded", test_sha, test_report.relative_to(root).as_posix()),
            ("INTEGRATION", "independent review evidence bundled", review_sha, review_path.relative_to(root).as_posix()),
            ("AWAITING_DIRECTOR", "integrated evidence packet prepared", integrated_sha, integrated_path.relative_to(root).as_posix()),
        ]
        for target, reason, digest, ref in transitions:
            _post(f"{control}/v1/tasks/{integration_task}/transition",
                  headers={"X-Orchestrator-Token": orchestrator},
                  payload={"target": target, "reason": reason, "evidence_sha256": digest, "evidence_ref": ref})
        return {
            "run_id": manifest["run_id"],
            "task_ids": task_ids,
            "role_reports": reports,
            "candidate_manifest": candidate_path.relative_to(root).as_posix(),
            "test_results": test_report.relative_to(root).as_posix(),
            "director_packet": integrated_path.relative_to(root).as_posix(),
            "director_packet_sha256": integrated_sha,
            "status": "AWAITING_DIRECTOR_REVIEW",
        }
    except Exception:
        for role in created:
            if role in completed:
                continue
            try:
                _post(f"{control}/v1/tasks/{task_ids[role]}/transition",
                      headers={"X-Orchestrator-Token": orchestrator},
                      payload={"target": "CANCELLED", "reason": "work package stopped after upstream failure"})
            except Exception:
                pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the six-role workforce against one authorized work-package manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--report-dir", default="engineering/workforce/.workforce-artifacts")
    args = parser.parse_args()
    root = Path(args.workspace).resolve()
    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        parser.error("manifest file does not exist")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = run_work_package(manifest, root, root / args.report_dir)
    except (json.JSONDecodeError, OrchestrationError, OSError, ValueError) as exc:
        raise SystemExit(f"workforce orchestration stopped: {type(exc).__name__}: {str(exc)[:1500]}") from exc
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
