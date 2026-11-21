#!/usr/bin/env python3
"""Exercise persistence across separate CLI process lifetimes."""

import json
import pathlib
import subprocess
import sys
import tempfile


def run(*args: str) -> str:
    completed = subprocess.run(args, capture_output=True, text=True)
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {args!r}\\n"
            f"stdout: {completed.stdout}\\nstderr: {completed.stderr}"
        )
    return completed.stdout.strip()

def parse_json(output: str):
    """Reject duplicate object keys instead of silently accepting ambiguous JSON."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise AssertionError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(output, object_pairs_hook=unique_object)


def main() -> int:
    executable = str(pathlib.Path(sys.argv[1]).resolve())
    payload = 'Observed event: line one\nline two with "quoted" text.'
    provenance = "integration-test:source-001"

    with tempfile.TemporaryDirectory(prefix="aurions-experience-") as directory:
        database = str(pathlib.Path(directory) / "memory.db")

        created = parse_json(run(
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

        # Record competing memories and prove that query context, not merely
        # insertion order, determines retrieval ranking.
        run(executable, "experience", "record", database,
            "conversation", "local-preference-001", "1",
            "I prefer local offline operation for the primary device.")
        run(executable, "experience", "record", database,
            "research", "architecture-note-002", "0",
            "AURIONS local inference and memory retrieval design.")
        strongest = "AURIONS local brain should learn from experience and adapt."
        run(executable, "experience", "record", database,
            "owner_correction", "owner-guidance-003", "1", strongest)

        ranked = json.loads(run(
            executable, "experience", "search", database, "AURIONS local brain", "10",
        ))
        assert len(ranked) >= 2, f"expected multiple lexical matches; got {ranked!r}"
        assert ranked[0]["content"] == strongest
        assert ranked[0]["relevance"] > ranked[1]["relevance"]
        assert ranked[0]["source_type"] == "owner_correction"
        assert ranked[0]["provenance_ref"] == "owner-guidance-003"

        # Query terms are bound parameters and LIKE wildcards are not interpreted
        # as caller-controlled SQL patterns.
        empty = subprocess.run(
            [executable, "experience", "search", database, "%%"],
            capture_output=True, text=True,
        )
        assert empty.returncode != 0

        no_match = json.loads(run(
            executable, "experience", "search", database, "quantum-banana-xyz",
        ))
        assert no_match == []

        # The cognitive consumer receives a bounded evidence packet rather
        # than raw storage access or an unstructured transcript dump.
        context = json.loads(run(
            executable, "experience", "context", database, "AURIONS local brain", "1",
        ))
        assert context["query"] == "AURIONS local brain"
        assert len(context["evidence"]) == 1
        assert context["evidence"][0]["content"] == strongest
        assert context["evidence"][0]["provenance_ref"] == "owner-guidance-003"
        assert context["payload_bytes"] <= 16 * 1024
        assert context["omitted_count"] >= 1
        assert context["evidence"][0]["recorded_at_ms"] > 0

        # JSON escaping must be included in the context budget and survive
        # round-tripping for quotes and embedded newlines.
        escaped_context = json.loads(run(
            executable, "experience", "context", database, "Observed event", "1",
        ))
        assert escaped_context["evidence"][0]["content"] == payload
        assert escaped_context["payload_bytes"] <= 16 * 1024

        invalid_context = subprocess.run(
            [executable, "experience", "context", database, "AURIONS local brain", "51"],
            capture_output=True, text=True,
        )
        assert invalid_context.returncode != 0

    print("Experience survives restart and contextual retrieval ranks relevant memories with provenance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
