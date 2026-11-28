#!/usr/bin/env python3
"""Exercise the representation persistence CLI and JSON/provenance checks."""

import json
import pathlib
import subprocess
import sys
import tempfile


def run(*args: str) -> str:
    completed = subprocess.run(args, capture_output=True, text=True)
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {args!r}\n"
            f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        )
    return completed.stdout.strip()


def reject(*args: str, expected: str) -> None:
    completed = subprocess.run(args, capture_output=True, text=True)
    assert completed.returncode != 0, f"expected rejection: {args!r}"
    assert expected in completed.stderr, completed.stderr


def main() -> int:
    executable = str(pathlib.Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory(prefix="aurions-representation-cli-") as directory:
        db = str(pathlib.Path(directory) / "brain.sqlite")
        source = json.loads(run(
            executable, "experience", "record", db, "observation", "test:source",
            "0", "Observed a red object near the entrance.",
        ))["experience_id"]
        content = '{"entities":[{"type":"object","color":"red"}]}'
        uncertainty = '{"confidence":0.76,"unknowns":["distance"]}'
        saved = json.loads(run(
            executable, "representation", "record", db, source, "scene_graph",
            content, "parser-v1", uncertainty,
        ))
        assert saved["experience_id"] == source
        assert saved["representation_type"] == "scene_graph"
        assert json.loads(saved["content_json"]) == json.loads(content)
        assert json.loads(saved["uncertainty_json"]) == json.loads(uncertainty)

        fetched = json.loads(run(
            executable, "representation", "show", db, saved["representation_id"],
        ))
        assert fetched == saved

        listed = json.loads(run(
            executable, "representation", "list", db, source, "10",
        ))
        assert len(listed) == 1
        assert listed[0]["representation_id"] == saved["representation_id"]

        reject(
            executable, "representation", "record", db, source, "invalid", "{", "method", "{}",
            expected="insert representation",
        )
        reject(
            executable, "representation", "record", db,
            "00000000-0000-4000-8000-000000000000", "semantic", "{}",
            "method", "{}", expected="active source experience not found",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
