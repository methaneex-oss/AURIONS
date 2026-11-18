#!/usr/bin/env python3
"""Enforce the presence and key workflow invariants of mandatory governance docs.

This is a documentation-integrity check. It cannot prove that people follow the
process or replace independent review, behavioural testing, or director acceptance.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"required governance file missing: {relative}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    standard_path = "docs/governance/PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md"
    builder_path = "docs/governance/BUILDER-OPERATING-PROTOCOL.md"
    standard = read(standard_path)
    builder = read(builder_path)

    required_sections = [
        "Part A — The new project directorship",
        "Part B — Builder accountability",
        "Part C — Independent reviewer accountability",
        "Part D — Independent tester accountability",
        "Part E — Workflow and handoff control",
        "Part F — Scope and change control",
        "Part G — Completion and evidence",
        "Part H — Continuous improvement",
        "Part I — Governing principle",
    ]
    for heading in required_sections:
        if heading not in standard:
            fail(f"team operating standard missing required section: {heading}")

    workflow = [
        "Director authorizes a bounded milestone.",
        "Builder implements and self-verifies.",
        "Builder submits a complete handoff.",
        "Independent reviewer examines the complete scope.",
        "Builder resolves review findings.",
        "Reviewer confirms corrections.",
        "Independent tester executes the test plan.",
        "Builder corrects implementation defects.",
        "Tester verifies corrections.",
        "Director evaluates final evidence and authorizes completion.",
    ]
    positions = [standard.find(step) for step in workflow]
    if any(position < 0 for position in positions):
        fail("team operating standard is missing one or more mandatory workflow stages")
    if positions != sorted(positions):
        fail("mandatory workflow stages are not in the prescribed order")

    if "Project Directorship and Team Operating Standard" not in builder:
        fail("builder protocol does not defer role/workflow authority to team operating standard")

    # The fresh-read gate is a mandatory precondition for every role and every run.
    required_pre_run_standard = [
        "Mandatory pre-run governance gate",
        "This gate is mandatory for every run, without exception.",
        "Director:",
        "Builder:",
        "Independent reviewer:",
        "Tester:",
        "Supporting agents:",
        "A copy read in an earlier run, remembered instructions, a summary, or a prior chat does not satisfy this gate.",
        "If the authoritative source cannot be retrieved or its current revision cannot be established, work must stop",
        "No role may waive it because a task is small, urgent, routine, previously performed, or believed to be low risk.",
    ]
    for phrase in required_pre_run_standard:
        if phrase not in standard:
            fail(f"team operating standard missing mandatory pre-run rule: {phrase}")

    required_pre_run_builder = [
        "Mandatory fresh governance read before every run",
        "Before every execution run, regardless of size or type",
        "Previous reads, remembered rules, summaries and prior-chat context do not satisfy the requirement.",
        "If the current authoritative documents cannot be retrieved or revision currency cannot be established, stop",
    ]
    for phrase in required_pre_run_builder:
        if phrase not in builder:
            fail(f"builder protocol missing mandatory pre-run rule: {phrase}")

    # EBT-01: enforce the presence of accountable engineering behaviour rules.
    required_ebt_standard = [
        "Part J — EBT-01: mandatory engineering behaviour and accountable ownership",
        "Independent professional judgment",
        "Role ownership and complete handoffs",
        "Scope discipline",
        "Evidence-based reporting",
        "Evidence-backed professional disagreement",
        "Autonomous correction within authority",
        "Behavioural compliance and evaluation",
        "from instruction-following activity to accountable engineering ownership",
    ]
    for phrase in required_ebt_standard:
        if phrase not in standard:
            fail(f"team operating standard missing EBT-01 requirement: {phrase}")

    required_ebt_builder = [
        "## 11. EBT-01 — builder behaviour and ownership",
        "Independently derive the necessary next engineering steps",
        "Correct defects within builder authority autonomously",
        "Report specification, implementation, verification, independent review and acceptance as separate states.",
        "Compliance is judged by the completed artifact",
    ]
    for phrase in required_ebt_builder:
        if phrase not in builder:
            fail(f"builder protocol missing EBT-01 requirement: {phrase}")

    entrypoints = {
        "README.md": read("README.md"),
        "docs/planning/README.md": read("docs/planning/README.md"),
        "docs/planning/PLANNING-COMPLETION-REGISTER.md": read(
            "docs/planning/PLANNING-COMPLETION-REGISTER.md"
        ),
    }
    for path, content in entrypoints.items():
        if "PROJECT-DIRECTORSHIP-AND-TEAM-OPERATING-STANDARD.md" not in content:
            fail(f"{path} does not link the mandatory project governance standard")

    print(
        "PASS: nine governance sections, ten ordered workflow stages, "
        "builder-protocol alignment, mandatory fresh-read gate and three project entry-point links."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
