#!/usr/bin/env python3
"""Validate canonical work-package and roadmap traceability.

This checks inventory and dependency-graph integrity only. It does not prove
semantic completeness, owner approval, implementation readiness or acceptance.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "docs/planning/CANONICAL-IMPLEMENTATION-ROADMAP.md"
MATRIX = ROOT / "docs/planning/WORK-PACKAGE-TRACEABILITY-AND-EXIT-MATRIX.md"
PRODUCT = ROOT / "docs/product/FIRST-USABLE-RELEASE-DEFINITION.md"
ACCEPTANCE_MATRIX = ROOT / "docs/planning/FIRST-RELEASE-ACCEPTANCE-TRACEABILITY-MATRIX.md"


class TraceabilityError(AssertionError):
    pass


def fail(message: str) -> None:
    raise TraceabilityError(message)


def parse_wp_ids(text: str) -> list[str]:
    """Expand exact WP IDs and inclusive ranges such as WP-00…WP-13."""
    found: list[str] = []
    pattern = re.compile(
        r"WP-(\d{2})(?:\s*(?:…|\.\.\.|-|–|—)\s*WP-(\d{2}))?"
    )
    for match in pattern.finditer(text):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        if end < start:
            fail(f"descending work-package range: {match.group(0)}")
        found.extend(f"WP-{number:02d}" for number in range(start, end + 1))
    return found


def has_cycle(graph: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for dependency in graph[node]:
            if dependency in graph and visit(dependency):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph if node not in visited)


def parse_table_rows(path: Path, label: str) -> dict[str, list[str]]:
    if not path.is_file():
        fail(f"missing {label}: {path.relative_to(ROOT)}")
    rows: dict[str, list[str]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("| WP-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        match = re.match(r"^(WP-\d{2})\b", cells[0])
        if not match:
            fail(f"{label}:{line_number}: malformed work-package identifier")
        wp_id = match.group(1)
        if wp_id in rows:
            fail(f"{label}:{line_number}: duplicate {wp_id} row")
        rows[wp_id] = cells
    return rows



def parse_acceptance_rows(path: Path, label: str) -> dict[str, list[str]]:
    if not path.is_file():
        fail(f"missing {label}: {path.relative_to(ROOT)}")
    rows: dict[str, list[str]] = {}
    in_acceptance_section = label != "product acceptance definition"
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if label == "product acceptance definition":
            if line.startswith("## 6. First-release acceptance protocol"):
                in_acceptance_section = True
                continue
            if in_acceptance_section and line.startswith("## 7. "):
                break
        if not in_acceptance_section or not line.startswith("| PR-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        match = re.match(r"^(PR-\\d{2})\\b", cells[0])
        if not match:
            fail(f"{label}:{line_number}: malformed acceptance identifier")
        acceptance_id = match.group(1)
        if acceptance_id in rows:
            fail(f"{label}:{line_number}: duplicate {acceptance_id} row")
        rows[acceptance_id] = cells
    return rows


def validate_acceptance_crosswalk() -> tuple[int, int]:
    product_rows = parse_acceptance_rows(PRODUCT, "product acceptance definition")
    matrix_rows = parse_acceptance_rows(ACCEPTANCE_MATRIX, "first-release acceptance matrix")
    expected = {f"PR-{number:02d}" for number in range(1, 19)}
    for label, rows in (("product acceptance definition", product_rows),
                        ("first-release acceptance matrix", matrix_rows)):
        actual = set(rows)
        if actual != expected:
            fail(
                f"{label} inventory mismatch: missing={sorted(expected - actual)}; "
                f"unexpected={sorted(actual - expected)}"
            )
    known_wps = {f"WP-{number:02d}" for number in range(17)}
    for acceptance_id, cells in matrix_rows.items():
        if len(cells) != 7:
            fail(f"{acceptance_id}: acceptance traceability row must have seven cells, found {len(cells)}")
        for label, cell in zip(
            cells[1:],
            ("contract/architecture trace", "accountable work packages",
             "scenario/test evidence", "required acceptance evidence", "owner/external gate"),
        ):
            if not cell:
                fail(f"{acceptance_id}: missing {label}")
        wp_refs = set(parse_wp_ids(cells[2]))
        if not wp_refs:
            fail(f"{acceptance_id}: no accountable work package is mapped")
        unknown = wp_refs - known_wps
        if unknown:
            fail(f"{acceptance_id}: unknown work-package references {sorted(unknown)}")
    return len(product_rows), len(matrix_rows)


def validate() -> tuple[int, int]:
    roadmap_rows = parse_table_rows(ROADMAP, "canonical roadmap")
    matrix_rows = parse_table_rows(MATRIX, "work-package matrix")
    expected = {f"WP-{number:02d}" for number in range(17)}

    for label, rows in (("roadmap", roadmap_rows), ("work-package matrix", matrix_rows)):
        actual = set(rows)
        if actual != expected:
            fail(
                f"{label} inventory mismatch: missing={sorted(expected - actual)}; "
                f"unexpected={sorted(actual - expected)}"
            )

    graph: dict[str, set[str]] = {}
    edge_count = 0
    for wp_id, cells in roadmap_rows.items():
        if len(cells) != 5:
            fail(f"{wp_id}: roadmap row must have five cells, found {len(cells)}")
        dependencies = set(parse_wp_ids(cells[3]))
        graph[wp_id] = dependencies
        edge_count += len(dependencies)

    known = set(graph)
    for wp_id, dependencies in graph.items():
        missing = dependencies - known
        if missing:
            fail(f"{wp_id}: references unknown dependencies {sorted(missing)}")
        if wp_id in dependencies:
            fail(f"{wp_id}: self-dependency is prohibited")

    if has_cycle(graph):
        fail("canonical work-package dependency graph contains a cycle")

    # First-release path is explicit: WP-15 depends on WP-00…WP-13.
    expected_first_release = {f"WP-{number:02d}" for number in range(14)}
    if graph["WP-15"] != expected_first_release:
        fail(
            "WP-15 dependencies must be exactly WP-00…WP-13; "
            f"found {sorted(graph['WP-15'])}"
        )
    if "WP-14" in graph["WP-15"]:
        fail("WP-14 fine-tuning infrastructure must not become a first-release prerequisite")
    if graph["WP-16"] != {"WP-15"}:
        fail(f"WP-16 must depend on accepted WP-15 only; found {sorted(graph['WP-16'])}")

    # Each matrix row must carry all ownership and evidence dimensions.
    for wp_id, cells in matrix_rows.items():
        if len(cells) != 7:
            fail(f"{wp_id}: traceability row must have seven cells, found {len(cells)}")
        for column, label in zip(
            cells[1:],
            ("logical owners", "inputs", "outputs", "acceptance evidence",
             "failure/recovery evidence", "external/owner gate"),
        ):
            if not column:
                fail(f"{wp_id}: missing {label}")

    # Unit-level controls for the parser and graph-cycle detector.
    if set(parse_wp_ids("WP-00…WP-03, WP-06")) != {
        "WP-00", "WP-01", "WP-02", "WP-03", "WP-06"
    }:
        fail("work-package range parser self-test failed")
    if not has_cycle({"WP-00": {"WP-01"}, "WP-01": {"WP-00"}}):
        fail("dependency-cycle detector self-test failed")

    product_count, acceptance_count = validate_acceptance_crosswalk()
    if product_count != 18 or acceptance_count != 18:
        fail("first-release acceptance crosswalk must cover PR-01…PR-18 exactly")

    return len(graph), edge_count


def main() -> int:
    package_count, edge_count = validate()
    print(
        f"PASS: {package_count} roadmap packages and {package_count} traceability rows; "
        f"{edge_count} dependency edges; graph acyclic; WP-15 first-release path "
        "and WP-14/WP-16 boundaries preserved; PR-01…PR-18 acceptance crosswalk exact."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
