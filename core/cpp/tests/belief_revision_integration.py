#!/usr/bin/env python3
"""Exercise belief revisions, evidence provenance, confidence updates, and guards."""

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
    with tempfile.TemporaryDirectory(prefix="aurions-belief-") as directory:
        db = str(pathlib.Path(directory) / "brain.sqlite")
        supporting = json.loads(run(
            executable, "experience", "record", db, "observation", "test:support",
            "0", "Observed rover tracks near the northern ridge.",
        ))["experience_id"]
        contradicting = json.loads(run(
            executable, "experience", "record", db, "observation", "test:counter",
            "2", "A later private observation contradicts the rover track hypothesis.",
        ))["experience_id"]

        initial = json.loads(run(
            executable, "belief", "create", db, "planetary-observation", "0.5",
            "A rover crossed the northern ridge.",
        ))
        belief_id = initial["belief_id"]
        assert len(initial["revisions"]) == 1
        assert initial["revisions"][0]["confidence"] == 0.5
        assert initial["revisions"][0]["evidence_count"] == 0

        supported = json.loads(run(
            executable, "belief", "evidence", db, belief_id, supporting,
            "supports", "0.8", "1.0",
        ))
        support_revision = supported["revisions"][-1]
        assert support_revision["revision"] == 2
        assert support_revision["confidence"] > 0.5
        assert support_revision["evidence_count"] == 1
        assert support_revision["evidence_stance"] == "supports"
        assert support_revision["evidence_sensitivity"] == 0

        revised = json.loads(run(
            executable, "belief", "evidence", db, belief_id, contradicting,
            "contradicts", "0.7", "0.8",
        ))
        counter_revision = revised["revisions"][-1]
        assert counter_revision["revision"] == 3
        assert counter_revision["confidence"] < support_revision["confidence"]
        assert counter_revision["evidence_count"] == 1
        assert counter_revision["evidence_stance"] == "contradicts"
        assert counter_revision["evidence_sensitivity"] == 2

        # A belief cannot count the same experience as evidence twice.
        reject(
            executable, "belief", "evidence", db, belief_id, supporting,
            "supports", "0.8", "1.0",
            expected="experience has already been used as evidence for this belief",
        )
        reject(
            executable, "belief", "evidence", db, belief_id, supporting,
            "invalid-stance", "0.8",
            expected="stance must be supports, contradicts, or contextualizes",
        )
        reject(
            executable, "belief", "evidence", db, belief_id, supporting,
            "supports", "0.4",
            expected="reliability must be at least 0.5",
        )

        unverified = json.loads(run(
            executable, "belief", "create", db, "planetary-observation", "0.5",
            "A second rover crossed the northern ridge.",
        ))
        context = json.loads(run(
            executable, "cognition", "context", db, "rover northern ridge", "10",
        ))
        returned = {item["belief_id"]: item for item in context["beliefs"]}
        assert belief_id in returned
        assert unverified["belief_id"] in returned
        assert returned[unverified["belief_id"]]["revision"] == 1
        assert returned[unverified["belief_id"]]["evidence_stance"] == ""
        assert returned[unverified["belief_id"]]["evidence_sensitivity"] == -1
        assert returned[belief_id]["confidence"] == counter_revision["confidence"]
        assert returned[belief_id]["revision"] == 3

        # A separate CLI process reads the complete revision history.
        reopened = json.loads(run(executable, "belief", "show", db, belief_id))
        assert [revision["revision"] for revision in reopened["revisions"]] == [1, 2, 3]
        assert reopened["revisions"][-1]["evidence_sensitivity"] == 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
