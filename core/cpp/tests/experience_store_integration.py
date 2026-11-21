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

        # Optional limits must not be mistaken for the query argument.
        ranked_default = json.loads(run(
            executable, "experience", "search", database, "AURIONS local brain",
        ))
        assert ranked_default[0]["content"] == strongest

        # Queries without lexical tokens are rejected before SQL execution.
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

        # The default context limit must preserve the query rather than reading
        # a missing optional argument.
        context_default = json.loads(run(
            executable, "experience", "context", database, "AURIONS local brain",
        ))
        assert context_default["query"] == "AURIONS local brain"
        assert len(context_default["evidence"]) >= 1

        # JSON escaping must be included in the context budget and survive
        # round-tripping for quotes and embedded newlines.
        escaped_context = json.loads(run(
            executable, "experience", "context", database, "Observed event", "1",
        ))
        assert escaped_context["evidence"][0]["content"] == payload
        assert escaped_context["payload_bytes"] <= 16 * 1024

        # Evidence-backed belief revision must change durable state, retain
        # provenance, and incorporate contradictory evidence in a later process.
        support = parse_json(run(
            executable, "experience", "record", database,
            "observation", "belief-support-001", "0",
            "AURIONS completed the local task successfully.",
        ))
        contradiction = parse_json(run(
            executable, "experience", "record", database,
            "observation", "belief-contradiction-001", "0",
            "AURIONS failed the local task under the same conditions.",
        ))
        context_evidence = parse_json(run(
            executable, "experience", "record", database,
            "observation", "belief-context-001", "0",
            "The local task was performed on a test device.",
        ))

        initial_belief = parse_json(run(
            executable, "belief", "create", database, "task-outcomes", "0.5",
            "AURIONS completes the local task successfully.",
        ))
        belief_id = initial_belief["belief_id"]
        assert len(initial_belief["revisions"]) == 1
        assert initial_belief["revisions"][0]["confidence"] == 0.5

        supported = parse_json(run(
            executable, "belief", "evidence", database, belief_id,
            support["experience_id"], "supports", "0.8",
        ))
        assert len(supported["revisions"]) == 2
        assert abs(supported["revisions"][-1]["confidence"] - 0.8) < 1e-9
        assert supported["revisions"][-1]["evidence_source_ref"] == "belief-support-001"
        assert supported["revisions"][-1]["evidence_stance"] == "supports"

        duplicate_evidence = subprocess.run(
            [executable, "belief", "evidence", database, belief_id,
             support["experience_id"], "supports", "0.8"],
            capture_output=True, text=True,
        )
        assert duplicate_evidence.returncode != 0

        contradicted = parse_json(run(
            executable, "belief", "evidence", database, belief_id,
            contradiction["experience_id"], "contradicts", "0.8",
        ))
        assert len(contradicted["revisions"]) == 3
        assert abs(contradicted["revisions"][-1]["confidence"] - 0.5) < 1e-9
        assert contradicted["revisions"][-1]["evidence_source_ref"] == "belief-contradiction-001"

        contextualized = parse_json(run(
            executable, "belief", "evidence", database, belief_id,
            context_evidence["experience_id"], "contextualizes", "0.9",
        ))
        assert len(contextualized["revisions"]) == 4
        assert abs(contextualized["revisions"][-1]["confidence"] - 0.5) < 1e-9

        # A fresh CLI process must recover the complete immutable revision chain.
        recovered_belief = parse_json(run(
            executable, "belief", "show", database, belief_id,
        ))
        assert [r["revision"] for r in recovered_belief["revisions"]] == [1, 2, 3, 4]
        assert recovered_belief["revisions"][1]["evidence_source_ref"] == "belief-support-001"
        assert recovered_belief["revisions"][2]["evidence_stance"] == "contradicts"
        assert recovered_belief["revisions"][3]["evidence_stance"] == "contextualizes"

        # The cognitive context combines recalled experiences with the
        # current evidence-backed belief, rather than exposing either alone.
        cognitive_context = parse_json(run(
            executable, "cognition", "context", database,
            "AURIONS completes local task successfully",
        ))
        assert cognitive_context["query"] == "AURIONS completes local task successfully"
        assert len(cognitive_context["memory_evidence"]) >= 1
        assert len(cognitive_context["beliefs"]) == 1
        assert cognitive_context["beliefs"][0]["belief_id"] == belief_id
        assert abs(cognitive_context["beliefs"][0]["confidence"] - 0.5) < 1e-9
        assert cognitive_context["beliefs"][0]["evidence_stance"] == "contextualizes"

        invalid_context = subprocess.run(
            [executable, "experience", "context", database, "AURIONS local brain", "51"],
            capture_output=True, text=True,
        )
        assert invalid_context.returncode != 0

    print("Experience survives restart and contextual retrieval ranks relevant memories with provenance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
