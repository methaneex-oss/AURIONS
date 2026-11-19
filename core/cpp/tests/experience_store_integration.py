#!/usr/bin/env python3
"""Exercise persistence across separate CLI process lifetimes."""

import json
import pathlib
import subprocess
import sys
import tempfile


def run(*args: str) -> str:
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def main() -> int:
    executable = str(pathlib.Path(sys.argv[1]).resolve())
    payload = 'Observed event: line one\nline two with "quoted" text.'
    provenance = "integration-test:source-001"

    with tempfile.TemporaryDirectory(prefix="aurions-experience-") as directory:
        database = str(pathlib.Path(directory) / "memory.db")

        created = json.loads(run(
            executable, "experience", "record", database,
            "integration_test", provenance, "2", payload,
        ))
        experience_id = created["experience_id"]

        # A second OS process opens the same database and retrieves the record.
        retrieved = json.loads(run(
            executable, "experience", "show", database, experience_id,
        ))

        assert retrieved["experience_id"] == experience_id
        assert retrieved["source_type"] == "integration_test"
        assert retrieved["content"] == payload
        assert retrieved["provenance_ref"] == provenance
        assert retrieved["sensitivity"] == 2
        assert retrieved["observed_at_ms"] > 0
        assert retrieved["recorded_at_ms"] > 0

    print("Experience survived process exit/restart with identity and provenance intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
