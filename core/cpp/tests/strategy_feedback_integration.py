#!/usr/bin/env python3
"""Exercise durable strategy selection, evidence recording, and reuse guards."""

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
    assert completed.returncode != 0, f"expected command rejection: {args!r}"
    assert expected in completed.stderr, (
        f"rejection mismatch: expected {expected!r}, got {completed.stderr!r}"
    )


def main() -> int:
    executable = str(pathlib.Path(sys.argv[1]).resolve())
    with tempfile.TemporaryDirectory(prefix="aurions-strategy-") as directory:
        db = str(pathlib.Path(directory) / "brain.sqlite")
        exp1 = json.loads(run(
            executable, "experience", "record", db, "evaluation", "test:alpha",
            "0", "Alpha strategy succeeded in the controlled test.",
        ))["experience_id"]
        exp2 = json.loads(run(
            executable, "experience", "record", db, "evaluation", "test:beta",
            "0", "Beta strategy failed in the controlled test.",
        ))["experience_id"]

        first = json.loads(run(
            executable, "strategy", "choose", db, "context:test", "strategy:alpha",
            "strategy:beta",
        ))
        assert first["strategy_ref"] == "strategy:alpha"
        assert first["selection_basis"] == "untried"
        assert first["trials"] == 0

        recorded = json.loads(run(
            executable, "strategy", "outcome", db, first["prediction_id"], exp1, "success",
        ))
        assert recorded["outcome"] == "success"
        assert recorded["evaluation_result"] == "correct"

        learned = json.loads(run(
            executable, "strategy", "choose", db, "context:test", "strategy:alpha",
        ))
        assert learned["strategy_ref"] == "strategy:alpha"
        assert learned["trials"] == 1
        assert learned["successes"] == 1
        assert abs(learned["posterior_success_probability"] - (2.0 / 3.0)) < 1e-12
        assert learned["selection_basis"] == "ucb1"

        explore = json.loads(run(
            executable, "strategy", "choose", db, "context:test", "strategy:alpha",
            "strategy:beta",
        ))
        assert explore["strategy_ref"] == "strategy:beta"
        assert explore["selection_basis"] == "untried"

        failure = json.loads(run(
            executable, "strategy", "outcome", db, explore["prediction_id"], exp2, "failure",
        ))
        assert failure["outcome"] == "failure"
        assert failure["evaluation_result"] == "incorrect"

        reject(
            executable, "strategy", "outcome", db, first["prediction_id"], exp1, "success",
            expected="prediction is not open for outcome evaluation",
        )
        another = json.loads(run(
            executable, "strategy", "choose", db, "context:test", "strategy:alpha",
        ))
        reject(
            executable, "strategy", "outcome", db, another["prediction_id"], exp1, "success",
            expected="outcome experience has already been used for strategy learning",
        )
        reject(
            executable, "strategy", "outcome", db, another["prediction_id"], exp2, "maybe",
            expected="outcome must be success or failure",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
