#!/usr/bin/env python3
"""Validate the checked-in AURIONS JSON Schema corpus and fixture expectations.

This is a design-contract validation gate. It does not prove runtime handler
semantics, C++/Python equivalence, authorization correctness, or production
readiness.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIXTURES = SCHEMAS / "fixtures"


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    schema_paths = sorted(SCHEMAS.glob("*.schema.json"))
    schema_docs = {path.name: load(path) for path in schema_paths}
    if not schema_docs:
        fail("No top-level schema files found")

    registry = Registry()
    for name, schema in schema_docs.items():
        if schema.get("$schema") != Draft202012Validator.META_SCHEMA["$id"]:
            fail(f"{name}: missing or incorrect Draft 2020-12 dialect declaration")
        Draft202012Validator.check_schema(schema)
        resource = Resource.from_contents(schema)
        schema_id = schema.get("$id", "")
        if schema_id.startswith("urn:"):
            registry = registry.with_resource(schema_id, resource)

    def validate(instance, schema, label: str) -> None:
        validator = Draft202012Validator(
            schema, registry=registry, format_checker=FormatChecker()
        )
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            detail = "; ".join(
                f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
                for error in errors[:5]
            )
            fail(f"{label}: {detail}")

    # Core registries and their fixtures.
    pairs = [
        ("command-query-registry.v1.json", "command-query-registry.v1.schema.json"),
        ("event-registry.v1.json", "event-registry.v1.schema.json"),
        ("error-registry.v1.json", "error-registry.v1.schema.json"),
        ("fixtures/error-handler-cases.fixture.json", "error-handler-fixtures.v1.schema.json"),
        ("fixtures/message-envelope.fixture.json", "message-envelope.v1.schema.json"),
        ("fixtures/capability-descriptor.fixture.json", "capability-descriptor-body.v1.schema.json"),
        ("fixtures/world-interaction.fixture.json", "world-interaction.v1.schema.json"),
    ]
    for instance_path, schema_name in pairs:
        validate(load(SCHEMAS / instance_path), schema_docs[schema_name], instance_path)

    # Guard the safety status of design registries. Structural validity
    # must never accidentally promote an incomplete contract to dispatchable.
    command_registry = load(SCHEMAS / "command-query-registry.v1.json")
    commands = command_registry["commands"]
    queries = command_registry["queries"]
    if len(commands) != 45 or len({item["command_type"] for item in commands}) != 45:
        fail("command registry must contain 45 unique command types")
    if len(queries) != 21 or len({item["query_type"] for item in queries}) != 21:
        fail("query registry must contain 21 unique query types")
    command_matrix_path = ROOT / "docs/planning/COMMAND-TRANSITION-AND-RECOVERY-CONTRACT-MATRIX.md"
    if not command_matrix_path.is_file():
        fail("missing per-command transition and recovery contract matrix")
    command_matrix = command_matrix_path.read_text(encoding="utf-8")
    error_registry = load(SCHEMAS / "error-registry.v1.json")
    known_error_codes = {entry["error_code"] for entry in error_registry["entries"]}
    event_registry = load(SCHEMAS / "event-registry.v1.json")
    known_event_types = set(event_registry["events"])
    command_acceptance_ids = set()
    mapped_command_types = set()
    for item in commands:
        command_type = item["command_type"]
        if not item.get("unresolved_bindings"):
            fail(f"{command_type}: missing explicit unresolved-binding ledger")
        if item.get("dispatch_status") not in {
            "design_only_not_dispatchable", "deferred_by_scope"
        }:
            fail(f"{command_type}: unsafe dispatch status")
        matrix_row = f"| `{command_type}` |"
        if matrix_row not in command_matrix:
            fail(f"{command_type}: missing per-command transition matrix row")
        if item["dispatch_status"] == "deferred_by_scope":
            if item.get("acceptance_case_id") or item.get("error_code_bindings") or item.get("emitted_event_bindings"):
                fail(f"{command_type}: deferred command must not have active contract bindings")
            continue
        mapped_command_types.add(command_type)
        for field in (
            "expected_revision_contract",
            "authorization_contract",
            "idempotency_contract",
            "deadline_cancellation_contract",
            "side_effect_contract",
        ):
            if not isinstance(item.get(field), str) or not item[field].strip():
                fail(f"{command_type}: missing populated {field}")
        if not item.get("error_code_bindings"):
            fail(f"{command_type}: missing command-specific error bindings")
        unknown_errors = set(item["error_code_bindings"]) - known_error_codes
        if unknown_errors:
            fail(f"{command_type}: unknown error bindings {sorted(unknown_errors)}")
        unknown_events = set(item.get("emitted_event_bindings", [])) - known_event_types
        if unknown_events:
            fail(f"{command_type}: unknown event bindings {sorted(unknown_events)}")
        case_id = item.get("acceptance_case_id")
        if not isinstance(case_id, str) or not case_id.startswith("CC-") or case_id in command_acceptance_ids:
            fail(f"{command_type}: missing or duplicate command acceptance case ID")
        command_acceptance_ids.add(case_id)
        if f"| `{case_id}` | `{command_type}` |" not in command_matrix:
            fail(f"{command_type}: acceptance case {case_id} missing from matrix catalogue")
        if item.get("dispatch_status") != "design_only_not_dispatchable":
            fail(f"{command_type}: mapped command unexpectedly dispatchable")
    matrix_command_rows = {
        line.split("|", 2)[1].strip().strip("`")
        for line in command_matrix.splitlines()
        if line.startswith("| `") and line.count("|") >= 4
        and line.split("|", 2)[1].strip().strip("`") in {item["command_type"] for item in commands}
    }
    if matrix_command_rows != {item["command_type"] for item in commands}:
        fail("command transition matrix rows do not exactly match registry inventory")
    if len(command_acceptance_ids) != len(mapped_command_types):
        fail("every mapped command must have exactly one unique acceptance case")

    query_contract_fields = (
        "authorization_contract",
        "data_classification",
        "redaction_contract",
        "consistency_contract",
        "ordering_cursor_contract",
        "limits_contract",
        "freshness_cache_contract",
    )
    query_matrix_path = ROOT / "docs/planning/QUERY-SEMANTICS-AND-SECURITY-CONTRACT-MATRIX.md"
    if not query_matrix_path.is_file():
        fail("missing per-query semantic contract matrix")
    query_matrix = query_matrix_path.read_text(encoding="utf-8")
    for item in queries:
        query_type = item["query_type"]
        if not item.get("unresolved_bindings"):
            fail(f"{query_type}: missing explicit unresolved-binding ledger")
        if item.get("dispatch_status") != "design_only_not_dispatchable":
            fail(f"{query_type}: unsafe dispatch status")
        if item.get("read_only") is not True:
            fail(f"{query_type}: query must remain read-only")
        for field in query_contract_fields:
            if not isinstance(item.get(field), str) or not item[field].strip():
                fail(f"{query_type}: missing populated {field}")
        if set(item["unresolved_bindings"]) != {
            "measured_endpoint_resource_budgets",
            "handler_level_executable_positive_negative_redaction_consistency_and_read_only_tests",
        }:
            fail(f"{query_type}: unresolved ledger does not match the verified query contract boundary")
        matrix_row = f"| `{query_type}` |"
        if matrix_row not in query_matrix:
            fail(f"{query_type}: missing per-query matrix row")

    matrix_query_rows = [
        line for line in query_matrix.splitlines()
        if line.startswith("| `") and line.count("|") >= 5
    ]
    if len(matrix_query_rows) != len(queries):
        fail(
            f"query contract matrix expected {len(queries)} rows, "
            f"found {len(matrix_query_rows)}"
        )

    event_registry = load(SCHEMAS / "event-registry.v1.json")
    events = event_registry["events"]
    if len(events) != 84:
        fail(f"event registry expected 84 entries, found {len(events)}")

    def resolve_pointer(document, pointer: str, label: str):
        if not pointer.startswith("#/"):
            fail(f"{label}: expected a non-root JSON Pointer fragment")
        value = document
        for raw_part in pointer[2:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")
            if isinstance(value, list):
                try:
                    index = int(part)
                except ValueError:
                    fail(f"{label}: non-integer array index {part!r}")
                if index < 0 or index >= len(value):
                    fail(f"{label}: array index {index} is out of range")
                value = value[index]
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                fail(f"{label}: unresolved JSON Pointer segment {part!r}")
        return value

    fixture_cache = {}
    for event_type, item in events.items():
        if item.get("dispatch_status") != "design_only_not_dispatchable":
            fail(f"{event_type}: event unexpectedly dispatchable")
        if not item.get("unresolved_bindings"):
            fail(f"{event_type}: missing event binding ledger")

        schema_ref = item.get("payload_schema_ref", "")
        schema_path, separator, schema_pointer = schema_ref.partition("#")
        if not separator or not schema_path.startswith("schemas/"):
            fail(f"{event_type}: malformed payload schema reference {schema_ref!r}")
        schema_name = Path(schema_path).name
        payload_schema = schema_docs.get(schema_name)
        if payload_schema is None:
            fail(f"{event_type}: missing payload schema file {schema_path!r}")
        payload_definition = resolve_pointer(
            payload_schema, "#" + schema_pointer, f"{event_type} payload schema"
        )
        if not isinstance(payload_definition, dict):
            fail(f"{event_type}: payload schema reference does not resolve to a schema object")
        if not payload_schema.get("$schema"):
            fail(f"{event_type}: referenced schema has no dialect declaration")
        # Validate against a local wrapper carrying the source schema's full
        # $defs. This avoids resolving a relative file-name $id as though it
        # were a registered absolute URI, while preserving internal refs.
        payload_validation_schema = {
            "$schema": payload_schema["$schema"],
            "$defs": payload_schema.get("$defs", {}),
            "$ref": "#" + schema_pointer,
        }

        fixture_refs = item.get("fixture_refs", [])
        if not fixture_refs:
            fail(f"{event_type}: no event-body fixture references")
        for fixture_ref in fixture_refs:
            fixture_path, fixture_separator, fixture_pointer = fixture_ref.partition("#")
            if not fixture_separator or not fixture_path.startswith("schemas/fixtures/"):
                fail(f"{event_type}: malformed fixture reference {fixture_ref!r}")
            if fixture_path not in fixture_cache:
                path = ROOT / fixture_path
                if not path.is_file():
                    fail(f"{event_type}: fixture file does not exist: {fixture_path}")
                fixture_cache[fixture_path] = load(path)
            fixture_payload = resolve_pointer(
                fixture_cache[fixture_path],
                "#" + fixture_pointer,
                f"{event_type} fixture {fixture_ref}",
            )
            validate(fixture_payload, payload_validation_schema, f"{event_type} fixture {fixture_ref}")

    error_registry = load(SCHEMAS / "error-registry.v1.json")
    error_cases = load(FIXTURES / "error-handler-cases.fixture.json")["cases"]
    if len(error_registry["entries"]) != 35 or len(error_cases) != 35:
        fail("error registry and fixture corpus must each contain 35 entries")
    if len({item["error_code"] for item in error_registry["entries"]}) != 35:
        fail("error registry contains duplicate error codes")
    case_by_code = {case["payload"]["error_code"]: case for case in error_cases}
    for item in error_registry["entries"]:
        if item.get("status") != "seed":
            fail(f"{item['error_code']}: seed status changed without runtime handler gate")
        if item["error_code"] not in case_by_code:
            fail(f"{item['error_code']}: no matching error fixture")
        if case_by_code[item["error_code"]]["handler_contract_ref"] != item["handler_mapping_ref"]:
            fail(f"{item['error_code']}: handler mapping and fixture disagree")

    # Reconcile the machine registry against the normative per-code mapping
    # table. This verifies mapping integrity, not that a runtime handler exists.
    import re

    matrix_path = ROOT / "docs/planning/ERROR-HANDLER-CONTRACT-MATRIX.md"
    matrix_rows = {}
    for line_number, line in enumerate(
        matrix_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.startswith("| `") or "[EH-" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            fail(f"error-handler matrix line {line_number}: expected five cells")
        code = cells[0].strip("`")
        handler_match = re.fullmatch(r"\[EH-(\d{3})\]\(#eh-\d{3}\)", cells[1])
        fixture_match = re.search(r"EHC-(\d{3})", cells[4])
        if not handler_match or not fixture_match:
            fail(f"error-handler matrix line {line_number}: malformed handler/fixture reference")
        if code in matrix_rows:
            fail(f"{code}: duplicate code-level handler mapping")
        matrix_rows[code] = {
            "handler_ref": (
                "docs/planning/ERROR-HANDLER-CONTRACT-MATRIX.md#eh-"
                + handler_match.group(1)
            ),
            "side_effect": cells[2].strip("`"),
            "retry": cells[3].strip("`"),
            "fixture_ref": (
                "schemas/fixtures/error-handler-cases.fixture.json#/cases/"
                + str(int(fixture_match.group(1)) - 1)
            ),
        }
    if len(matrix_rows) != 35:
        fail(f"error-handler matrix expected 35 code mappings, found {len(matrix_rows)}")
    registry_by_code = {item["error_code"]: item for item in error_registry["entries"]}
    if set(matrix_rows) != set(registry_by_code):
        fail(
            "error-handler mapping inventory mismatch: "
            f"matrix_only={sorted(set(matrix_rows) - set(registry_by_code))}; "
            f"registry_only={sorted(set(registry_by_code) - set(matrix_rows))}"
        )
    for code, row in matrix_rows.items():
        item = registry_by_code[code]
        if item["handler_mapping_ref"] != row["handler_ref"]:
            fail(f"{code}: machine registry handler differs from code-level matrix")
        if item["default_side_effect_state"] != row["side_effect"]:
            fail(f"{code}: default side-effect state differs from code-level matrix")
        if item["default_retry_posture"] != row["retry"]:
            fail(f"{code}: default retry posture differs from code-level matrix")
        if row["fixture_ref"] not in item["fixture_refs"]:
            fail(f"{code}: machine registry omits code-level matrix fixture")

    recovery_rows = {}
    for line_number, line in enumerate(
        matrix_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.startswith("| EHR-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            fail(f"recovery assertion line {line_number}: expected five cells")
        test_id = cells[0].strip("`")
        code = cells[1].strip("`")
        fixture_match = re.fullmatch(r"EHC-(\d{3})", cells[4])
        if not re.fullmatch(r"EHR-\d{3}", test_id) or not fixture_match:
            fail(f"recovery assertion line {line_number}: malformed test or fixture ID")
        if not cells[2] or not cells[3]:
            fail(f"{test_id}: required assertion or forbidden-result text is empty")
        if test_id in recovery_rows or code in recovery_rows.values():
            fail(f"{test_id}/{code}: duplicate per-code recovery assertion")
        recovery_rows[test_id] = code
        if code not in registry_by_code:
            fail(f"{test_id}: references unknown error code {code}")
        expected_fixture = (
            "schemas/fixtures/error-handler-cases.fixture.json#/cases/"
            + str(int(fixture_match.group(1)) - 1)
        )
        if expected_fixture not in registry_by_code[code]["fixture_refs"]:
            fail(f"{test_id}: fixture does not match registry entry {code}")
    if len(recovery_rows) != 35:
        fail(f"expected 35 code-specific recovery assertions, found {len(recovery_rows)}")
    if set(recovery_rows.values()) != set(registry_by_code):
        fail("code-specific recovery assertions do not cover the exact error registry inventory")

    # Every positive domain fixture is validated against the correspondingly
    # named reusable definition, not merely parsed as JSON.
    domain_schema = schema_docs["domain-payloads.v1.schema.json"]
    domain_fixture = load(FIXTURES / "domain-payloads.fixture.json")
    for name, payload in domain_fixture.items():
        if name not in domain_schema["$defs"]:
            fail(f"domain fixture {name}: no same-named schema definition")
        validate(payload, {"$ref": f"{domain_schema['$id']}#/$defs/{name}"},
                 f"positive domain fixture {name}")

    # Additional focused positive fixtures.
    for fixture_name, definition in [
        ("decision-recorded.fixture.json", "decisionRecorded"),
        ("provider-lifecycle.fixture.json", None),
        ("provider-lifecycle-enabled.fixture.json", None),
    ]:
        payload = load(FIXTURES / fixture_name)
        if definition:
            validate(payload, {"$ref": f"{domain_schema['$id']}#/$defs/{definition}"},
                     fixture_name)
        else:
            for name, value in payload.items():
                validate(value, {"$ref": f"{domain_schema['$id']}#/$defs/{name}"},
                         f"{fixture_name}:{name}")

    # Negative controls are explicit: each must fail its intended schema.
    negative_cases = {
        "approval-request-invalid-risk.invalid.json": ("domain-payloads.v1.schema.json", "approvalRequested"),
        "artifact-manifest-invalid-hash.invalid.json": ("domain-payloads.v1.schema.json", "artifactManifest"),
        "capability-descriptor-missing-provenance.invalid.json": ("capability-descriptor-body.v1.schema.json", None),
        "capability-descriptor-unknown-authority-field.invalid.json": ("capability-descriptor-body.v1.schema.json", None),
        "capability-discovery-missing-constraints.invalid.json": ("domain-payloads.v1.schema.json", "capabilityDiscoveryRequest"),
        "capability-discovery-missing-scope.invalid.json": ("domain-payloads.v1.schema.json", "capabilityDiscoveryRequest"),
        "capability-verification-invalid-version.invalid.json": ("domain-payloads.v1.schema.json", "capabilityVerificationRequest"),
        "command-envelope-missing-type.invalid.json": ("domain-payloads.v1.schema.json", "commandEnvelope"),
        "context-assembly-missing-scope.invalid.json": ("domain-payloads.v1.schema.json", "contextAssemblyRequest"),
        "contract-error-missing-side-effect-state.invalid.json": ("domain-payloads.v1.schema.json", "contractError"),
        "decision-selected-without-option.invalid.json": ("domain-payloads.v1.schema.json", "decisionRecorded"),
        "disclosure-invalid-digest.invalid.json": ("domain-payloads.v1.schema.json", "externalDisclosureRecord"),
        "domain-query-invalid-limit.invalid.json": ("domain-payloads.v1.schema.json", "domainQuery"),
        "error-registry-missing-side-effect.invalid.json": ("error-registry.v1.schema.json", None),
        "learning-experiment-missing-protocol.invalid.json": ("domain-payloads.v1.schema.json", "learningExperimentRequest"),
        "memory-retrieval-invalid-limit.invalid.json": ("domain-payloads.v1.schema.json", "memoryRetrievalQuery"),
        "message-envelope-invalid-owner-type.invalid.json": ("message-envelope.v1.schema.json", None),
        "operation-control-invalid-action.invalid.json": ("domain-payloads.v1.schema.json", "operationControlRequest"),
        "operation-proposal-invalid-risk-class.invalid.json": ("world-interaction.v1.schema.json", "interactionProposal"),
        "outcome-evaluation-missing-observed.invalid.json": ("domain-payloads.v1.schema.json", "outcomeEvaluation"),
        "provider-failure-dispatched-blind-retry.invalid.json": ("domain-payloads.v1.schema.json", "providerFailure"),
        "query-envelope-invalid-consistency.invalid.json": ("domain-payloads.v1.schema.json", "queryEnvelope"),
        "query-response-missing-result-schema.invalid.json": ("domain-payloads.v1.schema.json", "queryResponse"),
        "sync-conflict-missing-remote.invalid.json": ("domain-payloads.v1.schema.json", "syncConflictRecord"),
        "task-control-invalid-action.invalid.json": ("domain-payloads.v1.schema.json", "taskControlRequest"),
        "task-control-missing-version.invalid.json": ("domain-payloads.v1.schema.json", "taskControlRequest"),
        "task-run-transition-missing-revision.invalid.json": ("domain-payloads.v1.schema.json", "taskRunTransition"),
        "worker-result-missing-job.invalid.json": ("domain-payloads.v1.schema.json", "workerResult"),
        "world-entity-missing-evidence.invalid.json": ("world-interaction.v1.schema.json", "entity"),
    }
    negative_dir = FIXTURES / "negative"
    actual_negative = {p.name for p in negative_dir.glob("*.invalid.json")}
    if actual_negative != set(negative_cases):
        fail(
            "Negative fixture inventory mismatch: "
            f"unmapped={sorted(actual_negative - set(negative_cases))}; "
            f"missing={sorted(set(negative_cases) - actual_negative)}"
        )

    for filename, (schema_name, definition) in negative_cases.items():
        instance = load(negative_dir / filename)
        schema = schema_docs[schema_name]
        if definition and schema_name == "world-interaction.v1.schema.json":
            target = {
                "$schema": Draft202012Validator.META_SCHEMA["$id"],
                "$defs": schema["$defs"],
                "$ref": f"#/$defs/{definition}",
            }
        elif definition:
            target = {"$ref": f"{schema['$id']}#/$defs/{definition}"}
        else:
            target = schema
        try:
            validate(instance, target, f"negative control {filename}")
        except AssertionError:
            continue
        fail(f"negative control unexpectedly validated: {filename}")

    print(
        f"PASS: {len(schema_docs)} Draft 2020-12 schemas; "
        f"{len(pairs)} paired registry/fixture checks; "
        f"{len(domain_fixture)} positive domain payloads; "
        f"{len(negative_cases)} negative controls; "
        f"{len(recovery_rows)} code-specific recovery assertions."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # Keep CI output concise and actionable.
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
