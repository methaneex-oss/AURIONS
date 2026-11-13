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
    base_sha = value["base_commit_sha"]
    if not isinstance(base_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", base_sha) or base_sha == "0" * 40:
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
    if not isinstance(test_commands, list) or len(test_commands) > 20:
        raise OrchestrationError("test_commands must be a list of at most 20 argument arrays")
    allowed_commands = {"python", "python3", "pytest", "cmake", "ctest", "ninja"}
    for command in test_commands:
        if (not isinstance(command, list) or not command or len(command) > 100
                or not all(isinstance(arg, str) and arg and len(arg) <= 1024 for arg in command)):
            raise OrchestrationError("each test command must be a bounded non-empty argument array")
        executable = command[0]
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
        if role not in BUILDERS and paths:
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


def _task_brief(manifest: dict[str, Any], role: str) -> str:
    spec = manifest["roles"][role]
    permitted = spec["permitted_paths"] or ["READ-ONLY: no write paths"]
    sections = [
        f"Work package: {manifest['work_package_id']} (run {manifest.get('run_id', 'UNASSIGNED')})",
        f"Objective: {manifest['objective']}",
        f"Role: {role}",
        f"Role-specific assignment: {spec['task']}",
        f"Exact baseline commit: {manifest['base_commit_sha']}",
        "Acceptance criteria:\n" + "\n".join(f"- {item}" for item in manifest["acceptance_criteria"]),
        "Test plan:\n" + "\n".join(f"- {item}" for item in manifest["test_plan"]),
        "Review plan:\n" + "\n".join(f"- {item}" for item in manifest["review_plan"]),
        "Canonical sources:\n" + "\n".join(f"- {item}" for item in manifest["canonical_sources"]),
        "Stop conditions:\n" + "\n".join(f"- {item}" for item in manifest["stop_conditions"]),
        "Permitted write paths:\n" + "\n".join(f"- {item}" for item in permitted),
        f"Execution limits: {spec.get('max_model_calls', 8)} model calls; {spec.get('max_tokens', 16000)} total tokens; {spec.get('max_duration_minutes', {'lead_builder': 120, 'specialist_builder': 60, 'architecture_reviewer': 30, 'code_reviewer': 30, 'negative_tester': 30, 'integration_verifier': 45}[role])} minutes.",
        "Do not broaden scope, alter protected governance, claim unrun tests passed, or treat review comments as authorization to modify files.",
        "Return a precise completion report with changed files, test evidence, unresolved risks and any blocked acceptance criteria.",
    ]
    return "\n\n".join(sections)


def _task_contract(manifest: dict[str, Any], role: str) -> dict[str, Any]:
    spec = manifest["roles"][role]
    return {
        "work_package_id": manifest["work_package_id"],
        "authorization_ref": manifest["authorization_ref"],
        "objective": manifest["objective"],
        "base_commit_sha": manifest["base_commit_sha"],
        "permitted_paths": spec["permitted_paths"],
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


def _docker_run(
    command: list[str],
    *,
    test_root: Path,
    environment: dict[str, str],
    image: str,
    network: str,
    timeout: int,
) -> subprocess.CompletedProcess:
    """Run candidate-controlled tests in a network-restricted, credential-isolated container."""
    container_name = f"aurions-wf-test-{uuid.uuid4().hex[:12]}"
    allowed_env = {
        "PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "CI", "HOME", "TMPDIR",
        "CMAKE_BUILD_PARALLEL_LEVEL", "DATABASE_URL", "DIRECTOR_APPROVAL_TOKEN",
        "WORKFORCE_ORCHESTRATOR_TOKEN", "WORKFORCE_WORKER_CREDENTIALS_JSON",
    }
    if set(environment) - allowed_env:
        raise OrchestrationError("test environment contains an unapproved variable")
    uid = os.getuid() if hasattr(os, "getuid") else 10001
    gid = os.getgid() if hasattr(os, "getgid") else 10001
    executable = Path(command[0]).name
    argv = ["python3", *command[1:]] if executable.startswith("python") else command
    docker_command = [
        "docker", "run", "--rm", "--name", container_name,
        "--network", network, "--read-only",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=1g",
        "--cap-drop=ALL", "--security-opt=no-new-privileges:true",
        "--pids-limit=128", "--memory=4g", "--cpus=2",
        "--user", f"{uid}:{gid}",
        "--mount", f"type=bind,src={test_root.resolve()},dst=/workspace,rw",
        "--workdir", "/workspace",
    ]
    for key, value in sorted(environment.items()):
        docker_command.extend(["--env", f"{key}={value}"])
    docker_command.extend([image, *argv])
    try:
        return subprocess.run(
            docker_command, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["docker", "rm", "--force", container_name],
            capture_output=True, text=True, timeout=10, check=False,
        )
        raise


def _run_candidate_tests(
    *,
    test_root: Path,
    test_commands: list[list[str]],
    test_image: str,
    remaining_seconds,
) -> list[dict[str, Any]]:
    """Create a private PostgreSQL database and execute tests without host/provider access."""
    import secrets

    network = f"aurions-wf-net-{uuid.uuid4().hex[:10]}"
    database_container = f"aurions-wf-db-{uuid.uuid4().hex[:10]}"
    password = secrets.token_urlsafe(32)
    test_environment = {
        "PYTHONPATH": "/workspace/engineering/workforce/src",
        "PYTHONDONTWRITEBYTECODE": "1",
        "CI": "1",
        "HOME": "/tmp",
        "TMPDIR": "/tmp",
        "CMAKE_BUILD_PARALLEL_LEVEL": "2",
        "DATABASE_URL": f"postgresql://workforce:{password}@{database_container}:5432/workforce_test",
        "DIRECTOR_APPROVAL_TOKEN": secrets.token_urlsafe(32),
        "WORKFORCE_ORCHESTRATOR_TOKEN": secrets.token_urlsafe(32),
        "WORKFORCE_WORKER_CREDENTIALS_JSON": json.dumps({
            "builder-01": {"token": secrets.token_urlsafe(32), "role": "lead_builder"},
            "reviewer-01": {"token": secrets.token_urlsafe(32), "role": "code_reviewer"},
        }),
    }
    results: list[dict[str, Any]] = []

    def docker(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                ["docker", *args], capture_output=True, text=True,
                timeout=timeout, check=False,
            )
        except FileNotFoundError as exc:
            raise OrchestrationError("Docker is required for isolated candidate testing") from exc
        if result.returncode:
            raise OrchestrationError("isolated test infrastructure failed: " + result.stderr[-1200:])
        return result

    try:
        docker(["network", "create", "--internal", network])
        docker([
            "run", "--detach", "--name", database_container, "--network", network,
            "--env", "POSTGRES_USER=workforce",
            "--env", f"POSTGRES_PASSWORD={password}",
            "--env", "POSTGRES_DB=workforce_test",
            "postgres:17-alpine",
        ])
        ready = False
        deadline = time.monotonic() + min(60, max(5, remaining_seconds() - 5))
        while time.monotonic() < deadline:
            check = subprocess.run(
                ["docker", "exec", database_container, "pg_isready", "-U", "workforce", "-d", "workforce_test"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            if check.returncode == 0:
                ready = True
                break
            time.sleep(0.5)
        if not ready:
            raise OrchestrationError("isolated PostgreSQL test database did not become ready")

        migration_code = """import os
from pathlib import Path
import psycopg
paths = sorted(Path("engineering/workforce/migrations").glob("*.sql"))
if not paths:
    raise SystemExit("no workforce migrations found")
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    for path in paths:
        conn.execute(path.read_text(encoding="utf-8"), prepare=False)
"""
        migration_remaining = remaining_seconds()
        if migration_remaining < 10:
            raise OrchestrationError("work-package budget exhausted before test database migration")
        migrated = _docker_run(
            ["python3", "-c", migration_code],
            test_root=test_root, environment=test_environment, image=test_image,
            network=network, timeout=max(1, min(60, int(migration_remaining - 5))),
        )
        if migrated.returncode:
            raise OrchestrationError("isolated test database migration failed: " + migrated.stderr[-1200:])

        for command in test_commands:
            remaining = remaining_seconds()
            if remaining < 10:
                raise OrchestrationError("work-package wall-clock budget exhausted before test execution")
            try:
                run = _docker_run(
                    command, test_root=test_root, environment=test_environment,
                    image=test_image, network=network,
                    timeout=max(1, min(300, int(remaining - 5))),
                )
                result_record = {
                    "command": command,
                    "returncode": run.returncode,
                    "stdout": run.stdout[-12000:],
                    "stderr": run.stderr[-12000:],
                }
            except subprocess.TimeoutExpired as exc:
                result_record = {
                    "command": command,
                    "returncode": 124,
                    "stdout": str(exc.stdout or "")[-12000:],
                    "stderr": "test command exceeded its bounded container timeout",
                }
            results.append(result_record)
            if result_record["returncode"]:
                raise OrchestrationError("candidate test suite failed; no reviewer or integration task will proceed")
        return results
    finally:
        subprocess.run(
            ["docker", "rm", "--force", database_container],
            capture_output=True, text=True, timeout=15, check=False,
        )
        subprocess.run(
            ["docker", "network", "rm", network],
            capture_output=True, text=True, timeout=15, check=False,
        )


def run_work_package(manifest: dict[str, Any], workspace: Path, report_dir: Path) -> dict[str, Any]:
    manifest = validate_manifest(manifest)
    root = workspace.resolve()
    report_dir = report_dir.resolve()
    if root not in report_dir.parents:
        raise OrchestrationError("report directory must be inside the workspace")
    report_rel = report_dir.relative_to(root).as_posix()
    if Path(report_rel).parts[:3] != ("engineering", "workforce", ".workforce-artifacts"):
        raise OrchestrationError("report directory must be under engineering/workforce/.workforce-artifacts")
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
    from workforce.model_registry import role_assignment
    for role in ROLES:
        profile = role_assignment(role)
        if not os.environ.get(profile["key_env"]):
            raise OrchestrationError(f"required provider credential is missing for {role}: {profile['key_env']}")
        if profile["account_env"] and not os.environ.get(profile["account_env"]):
            raise OrchestrationError(f"required provider account identifier is missing for {role}: {profile['account_env']}")
        for context_file in manifest["roles"][role]["context_files"]:
            if not safe_path(root, context_file).is_file():
                raise OrchestrationError(f"required {role} context file does not exist: {context_file}")
    for test_path in manifest["test_paths"]:
        if not safe_path(root, test_path).exists():
            raise OrchestrationError(f"declared test input does not exist: {test_path}")
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

        test_commands = [
            ["python3", "-m", "compileall", "-q", "engineering/workforce/src", "engineering/workforce/tests"],
            ["python3", "-m", "unittest", "discover", "-s", "engineering/workforce/tests", "-v"],
            *manifest["test_commands"],
        ]
        test_results: list[dict[str, Any]] = []
        test_report = report_dir / f"{manifest['run_id']}-test-results.json"

        def persist_test_results(status: str) -> None:
            test_report.write_text(
                json.dumps({"status": status, "results": test_results}, indent=2),
                encoding="utf-8",
            )

        persist_test_results("RUNNING")
        with tempfile.TemporaryDirectory(prefix="workforce-package-tests-") as test_dir:
            test_root = Path(test_dir)
            _copy_test_snapshot(root, test_root, manifest["test_paths"])
            test_image = os.environ.get("WORKFORCE_TEST_DOCKER_IMAGE", "")
            if not test_image or not re.fullmatch(r"[A-Za-z0-9._:/@-]{1,200}", test_image):
                raise OrchestrationError("WORKFORCE_TEST_DOCKER_IMAGE must identify the prebuilt trusted test image")
            try:
                test_results.extend(_run_candidate_tests(
                    test_root=test_root,
                    test_commands=test_commands,
                    test_image=test_image,
                    remaining_seconds=remaining_orchestration_seconds,
                ))
            except OrchestrationError:
                persist_test_results("FAILED")
                raise
        persist_test_results("PASSED")

        test_bytes = test_report.read_bytes()
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
