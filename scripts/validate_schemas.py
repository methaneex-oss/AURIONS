#!/usr/bin/env python3
"""Validate the checked-in AURIONS JSON Schema corpus and fixture expectations.

This is a design-contract validation gate. It does not prove runtime handler
semantics, C++/Python equivalence, authorization correctness, or production
readiness.
"""
from __future__ import annotations

import json
import re
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
        ("fixtures/scenario-contracts.fixture.json", "scenario-contracts.v1.schema.json"),
    ]
    for instance_path, schema_name in pairs:
        validate(load(SCHEMAS / instance_path), schema_docs[schema_name], instance_path)

    # Guard the safety status of design registries. Structural validity
    # must never accidentally promote an incomplete contract to dispatchable.
    command_registry = load(SCHEMAS / "command-query-registry.v1.json")
    commands = command_registry["commands"]
    queries = command_registry["queries"]
    command_counts = command_registry.get("counts", {})
    mapped_commands = [
        item for item in commands
        if item.get("dispatch_status") == "design_only_not_dispatchable"
    ]
    deferred_commands = [
        item for item in commands
        if item.get("dispatch_status") == "deferred_by_scope"
    ]
    expected_total = (
        command_counts.get("mapped_command_types", -1)
        + command_counts.get("deferred_command_types", -1)
    )
    if len(commands) != expected_total or len({item["command_type"] for item in commands}) != len(commands):
        fail("command registry inventory differs from its declared mapped/deferred counts or contains duplicate types")
    if len(mapped_commands) != command_counts.get("mapped_command_types"):
        fail("mapped command count differs from registry inventory metadata")
    semantic_report_path = ROOT / "docs/planning/SEMANTIC-ARCHITECTURE-RECONCILIATION-REPORT.md"
    semantic_report = semantic_report_path.read_text(encoding="utf-8")
    expected_inventory_lines = (
        f"- {len(commands)} command entries: {len(mapped_commands)} mapped to typed request/response",
        f"- {len(mapped_commands)} mapped commands have unique CC-001…CC-{len(mapped_commands):03d} positive/negative acceptance assertions.",
        f"- {len(commands)} unique command types, {len(queries)} unique query types and 89 event types.",
        f"- All {len(mapped_commands)} mapped command entries have semantic fields, known error/event bindings and unique CC-001…CC-{len(mapped_commands):03d} acceptance IDs; the two device commands are deferred.",
    )
    for expected_line in expected_inventory_lines:
        if expected_line not in semantic_report:
            fail(f"semantic architecture report has stale command/query inventory summary: {expected_line}")
    if len(deferred_commands) != command_counts.get("deferred_command_types"):
        fail("deferred command count differs from registry inventory metadata")
    if command_counts.get("command_envelope_bindings") != len(commands):
        fail("command envelope binding count differs from registry inventory")
    if command_counts.get("proposed_ddl_mapped_commands") != len(mapped_commands):
        fail("proposed DDL mapped-command count differs from mapped command inventory")
    if len(queries) != 29 or len({item["query_type"] for item in queries}) != 29:
        fail("query registry must contain 29 unique query types")
    command_matrix_path = ROOT / "docs/planning/COMMAND-TRANSITION-AND-RECOVERY-CONTRACT-MATRIX.md"
    if not command_matrix_path.is_file():
        fail("missing per-command transition and recovery contract matrix")
    command_matrix = command_matrix_path.read_text(encoding="utf-8")
    transaction_matrix_path = ROOT / "docs/planning/STORE-LOCAL-OUTBOX-AND-CROSS-STORE-SAGA-MATRIX.md"
    if not transaction_matrix_path.is_file():
        fail("missing store-local outbox and cross-store saga ownership matrix")
    transaction_matrix = transaction_matrix_path.read_text(encoding="utf-8")
    expected_command_types = {item["command_type"] for item in commands}
    transaction_rows = {}
    for line in transaction_matrix.splitlines():
        if not line.startswith("| ") or line.count("|") < 5:
            continue
        command_name = line.split("|", 2)[1].strip().strip(chr(96))
        if command_name in expected_command_types:
            transaction_rows[command_name] = line
    if set(transaction_rows) != expected_command_types:
        fail(
            "transaction matrix command inventory mismatch: "
            f"missing={sorted(expected_command_types - set(transaction_rows))}; "
            f"unexpected={sorted(set(transaction_rows) - expected_command_types)}"
        )
    error_registry = load(SCHEMAS / "error-registry.v1.json")
    known_error_codes = {entry["error_code"] for entry in error_registry["entries"]}
    event_registry = load(SCHEMAS / "event-registry.v1.json")
    known_event_types = set(event_registry["events"])
    # Every authoritative write store must own its transactional outbox.
    # The central event archive is populated asynchronously by relays; it cannot
    # make a separate domain-store commit atomic.
    store_ddl_files = {
        "aurion_memory.db": [
            "aurion_memory.base.sql", "aurion_memory.migration_v2.sql",
            "aurion_memory.migration_v3.sql", "aurion_memory.migration_v4.sql",
            "aurion_memory.migration_v5.sql", "aurion_memory.migration_v6.sql",
            "aurion_memory.migration_v7.sql",
        ],
        "aurion_events.db": [
            "aurion_events.base.sql", "aurion_events.migration_v2.sql",
            "aurion_events.migration_v3.sql", "aurion_events.migration_v4.sql",
            "aurion_events.migration_v5.sql", "aurion_events.migration_v6.sql",
        ],
        "aurion_governance.db": [
            "aurion_governance.base.sql", "aurion_governance.migration_v2.sql",
            "aurion_governance.migration_v3.sql", "aurion_governance.migration_v4.sql",
        ],
    }
    store_tables = {}
    for store, filenames in store_ddl_files.items():
        ddl_text = "\n".join(
            (ROOT / "schemas/persistence" / filename).read_text(encoding="utf-8")
            for filename in filenames
        )
        store_tables[store] = set(re.findall(
            r"CREATE TABLE(?: IF NOT EXISTS)?\s+([A-Za-z_][A-Za-z0-9_]*)",
            ddl_text,
            flags=re.IGNORECASE,
        ))
        if "outbox" not in store_tables[store]:
            fail(f"{store}: missing store-local transactional outbox table")

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
        if item["dispatch_status"] != "deferred_by_scope":
            matching_rows = [
                line for line in command_matrix.splitlines()
                if line.startswith(matrix_row)
            ]
            if len(matching_rows) != 1:
                fail(f"{command_type}: expected exactly one per-command transition row")
            row_cells = [
                cell.strip()
                for cell in matching_rows[0].strip().strip("|").split("|")
            ]
            if len(row_cells) != 4:
                fail(f"{command_type}: transition row must have four columns")
            matrix_events = set(re.findall(
                r"\\b[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+\\.v\\d+\\b",
                row_cells[2],
            ))
            registry_events = set(item.get("emitted_event_bindings", []))
            if matrix_events != registry_events:
                fail(
                    f"{command_type}: transition-matrix event boundary differs from registry; "
                    f"matrix={sorted(matrix_events)}; registry={sorted(registry_events)}"
                )
        if item["dispatch_status"] == "deferred_by_scope":
            if item.get("acceptance_case_id") or item.get("error_code_bindings") or item.get("emitted_event_bindings"):
                fail(f"{command_type}: deferred command must not have active contract bindings")
            continue
        mapped_command_types.add(command_type)
        bindings = item.get("table_bindings", [])
        binding_stores = [binding["store"] for binding in bindings]
        if len(binding_stores) != len(set(binding_stores)):
            fail(f"{command_type}: duplicate table-binding store")
        bindings_by_store = {
            binding["store"]: set(binding["tables"])
            for binding in bindings
        }
        stores = item.get("persistence_stores", [])
        transaction_contract = item.get("transaction_contract", "")
        for binding in bindings:
            store = binding["store"]
            role = binding.get("binding_role")
            if store not in store_tables:
                fail(f"{command_type}: table binding names unknown store {store}")
            missing_tables = set(binding["tables"]) - store_tables[store]
            if missing_tables:
                fail(f"{command_type}: {store} binding names absent DDL tables {sorted(missing_tables)}")
            if store in stores:
                if role != "authoritative_write":
                    fail(f"{command_type}: persistence store {store} must have authoritative_write binding role")
            elif role == "async_archive":
                if store != "aurion_events.db" or not {"events", "outbox"}.issubset(set(binding["tables"])):
                    fail(f"{command_type}: async_archive must bind events/outbox in aurion_events.db")
            elif role == "read_dependency":
                if "outbox" in binding["tables"]:
                    fail(f"{command_type}: read_dependency {store} must not bind its write outbox")
            else:
                fail(f"{command_type}: extra store {store} must be read_dependency or async_archive")
        if set(stores) - set(binding_stores):
            fail(f"{command_type}: authoritative persistence store lacks table binding")
        matrix_row = transaction_rows[command_type]
        expected_mode = (
            "DEFERRED" if item["dispatch_status"] == "deferred_by_scope"
            else "CROSS_STORE_SAGA" if len(stores) > 1
            else "SINGLE_STORE_LOCAL_OUTBOX"
        )
        if f"| {expected_mode} |" not in matrix_row:
            fail(f"{command_type}: transaction matrix mode differs from registry boundary")
        if len(stores) == 1 and not transaction_contract.startswith("SINGLE_STORE_LOCAL_OUTBOX:"):
            fail(f"{command_type}: single-store command lacks explicit local-outbox transaction contract")
        if len(stores) > 1:
            if not transaction_contract.startswith("CROSS_STORE_SAGA:"):
                fail(f"{command_type}: multi-store command lacks explicit saga transaction contract")
            coordinator = next(
                (binding for binding in item.get("table_bindings", [])
                 if binding["store"] == "aurion_events.db"),
                None,
            )
            if "aurion_events.db" not in stores or coordinator is None:
                fail(f"{command_type}: cross-store saga must bind the event/recovery coordinator")
            if not {"operations", "operation_steps", "recovery_journal", "outbox"}.issubset(set(coordinator["tables"])):
                fail(f"{command_type}: saga coordinator must bind operations, operation_steps, recovery_journal and outbox")
        for store in stores:
            if store not in store_tables:
                fail(f"{command_type}: unknown persistence store {store}")
            if "outbox" not in store_tables[store]:
                fail(f"{command_type}: {store} has no local outbox DDL")
            if "outbox" not in bindings_by_store.get(store, set()):
                fail(f"{command_type}: {store} binding omits its local outbox")
        for field in (
            "expected_revision_contract",
            "authorization_contract",
            "idempotency_contract",
            "deadline_cancellation_contract",
            "side_effect_contract",
            "transaction_contract",
        ):
            if not isinstance(item.get(field), str) or not item[field].strip():
                fail(f"{command_type}: missing populated {field}")
        if not item.get("error_code_bindings"):
            fail(f"{command_type}: missing command-specific error bindings")
        if not item.get("emitted_event_bindings"):
            fail(f"{command_type}: mapped command has no explicit emitted-event binding")
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
        "projection_contract",
    )
    query_matrix_path = ROOT / "docs/planning/QUERY-SEMANTICS-AND-SECURITY-CONTRACT-MATRIX.md"
    if not query_matrix_path.is_file():
        fail("missing per-query semantic contract matrix")
    query_matrix = query_matrix_path.read_text(encoding="utf-8")
    projection_matrix_path = ROOT / "docs/planning/QUERY-PROJECTION-AND-PERSISTENCE-RECONCILIATION.md"
    if not projection_matrix_path.is_file():
        fail("missing query projection and persistence reconciliation matrix")
    projection_matrix = projection_matrix_path.read_text(encoding="utf-8")
    query_acceptance_ids = set()
    query_types = {item["query_type"] for item in queries}
    matrix_query_types = set()
    for item in queries:
        query_type = item["query_type"]
        if not item.get("unresolved_bindings"):
            fail(f"{query_type}: missing explicit unresolved-binding ledger")
        if item.get("dispatch_status") != "design_only_not_dispatchable":
            fail(f"{query_type}: unsafe dispatch status")
        if item.get("read_only") is not True:
            fail(f"{query_type}: query must remain read-only")
        query_bindings = item.get("table_bindings", [])
        query_binding_stores = [binding["store"] for binding in query_bindings]
        if len(query_binding_stores) != len(set(query_binding_stores)):
            fail(f"{query_type}: duplicate query table-binding store")
        if set(query_binding_stores) != set(item.get("persistence_stores", [])):
            fail(f"{query_type}: read-projection table stores differ from declared persistence stores")
        for binding in query_bindings:
            if binding.get("binding_role") != "read_projection":
                fail(f"{query_type}: query table binding must be read_projection")
            store = binding["store"]
            if store not in store_tables:
                fail(f"{query_type}: unknown query projection store {store}")
            missing_tables = set(binding["tables"]) - store_tables[store]
            if missing_tables:
                fail(f"{query_type}: {store} projection names absent DDL tables {sorted(missing_tables)}")
        unresolved_projection_fields = item.get("projection_unresolved_fields", [])
        if len(unresolved_projection_fields) != len(set(unresolved_projection_fields)):
            fail(f"{query_type}: duplicate unresolved projection fields")
        result_ref = item["result_item_schema"]
        result_path, result_pointer = result_ref.split("#", 1)
        result_document = load(ROOT / result_path)
        result_node = result_document
        for token in result_pointer.lstrip("/").split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            result_node = result_node[token]
        result_fields = set(result_node.get("properties", {}))
        resolved_projection_fields = item.get("projection_resolved_fields", [])
        if len(resolved_projection_fields) != len(set(resolved_projection_fields)):
            fail(f"{query_type}: duplicate resolved projection fields")
        unresolved_set = set(unresolved_projection_fields)
        resolved_set = set(resolved_projection_fields)
        if unresolved_set & resolved_set:
            fail(f"{query_type}: a projection field is both resolved and unresolved")
        if unresolved_set | resolved_set != result_fields:
            fail(
                f"{query_type}: projection field inventory does not exactly cover result schema; "
                f"missing={sorted(result_fields - (unresolved_set | resolved_set))}; "
                f"unknown={sorted((unresolved_set | resolved_set) - result_fields)}"
            )
        if "UNVERIFIED" not in item.get("projection_contract", ""):
            fail(f"{query_type}: projection contract must preserve unverified evidence boundary")
        section_start = projection_matrix.find(f"### {chr(96)}{query_type}{chr(96)}")
        if section_start < 0:
            fail(f"{query_type}: missing field-level projection section")
        next_section = projection_matrix.find("\n### ", section_start + 1)
        projection_section = projection_matrix[section_start:] if next_section < 0 else projection_matrix[section_start:next_section]
        for field_name in unresolved_projection_fields:
            marker = f"- {chr(96)}{field_name}{chr(96)} → **UNMAPPED"
            if marker not in projection_section:
                fail(f"{query_type}: projection matrix omits unresolved field {field_name}")
        for field_name in resolved_projection_fields:
            marker = f"- {chr(96)}{field_name}{chr(96)} → "
            if marker not in projection_section or marker + "**UNMAPPED" in projection_section:
                fail(f"{query_type}: resolved projection field {field_name} lacks a proposed source/derivation")
        # Every relational source named by a field mapping must be part of
        # this query's declared read projection. Parenthetical text is a
        # derivation/annotation (for example an event type), not a table join.
        bound_query_tables = {
            table for binding in query_bindings for table in binding["tables"]
        }
        for projection_line in projection_section.splitlines():
            if not projection_line.startswith("- `") or " → " not in projection_line:
                continue
            source_expression = projection_line.split(" → ", 1)[1].split("(", 1)[0]
            source_tables = {
                table for table, _column in re.findall(
                    r"\b([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)\b",
                    source_expression,
                )
            }
            undeclared_sources = source_tables - bound_query_tables
            if undeclared_sources:
                field_name = projection_line.split("`", 2)[1]
                fail(
                    f"{query_type}: projection field {field_name} references "
                    f"undeclared read tables {sorted(undeclared_sources)}"
                )
        for field in query_contract_fields:
            if not isinstance(item.get(field), str) or not item[field].strip():
                fail(f"{query_type}: missing populated {field}")
        if set(item["unresolved_bindings"]) != {
            "measured_endpoint_resource_budgets",
            "handler_level_executable_positive_negative_redaction_consistency_and_read_only_tests",
        }:
            fail(f"{query_type}: unresolved ledger does not match the verified query contract boundary")
        for field in (
            "acceptance_positive_assertion",
            "acceptance_negative_assertion",
            "read_only_invariant",
        ):
            if not isinstance(item.get(field), str) or not item[field].strip():
                fail(f"{query_type}: missing populated {field}")
        case_id = item.get("acceptance_case_id")
        if not isinstance(case_id, str) or not case_id.startswith("QCC-") or case_id in query_acceptance_ids:
            fail(f"{query_type}: missing or duplicate query acceptance case ID")
        query_acceptance_ids.add(case_id)
        matrix_row = f"| `{query_type}` |"
        if matrix_row not in query_matrix:
            fail(f"{query_type}: missing per-query matrix row")
        case_row = f"| `{case_id}` | `{query_type}` |"
        if case_row not in query_matrix:
            fail(f"{query_type}: acceptance case {case_id} missing from query matrix")
        matrix_query_types.add(query_type)

    if matrix_query_types != query_types:
        fail("query contract matrix rows do not exactly match registry inventory")
    if len(query_acceptance_ids) != len(queries):
        fail("every query must have exactly one unique acceptance case")

    event_registry = load(SCHEMAS / "event-registry.v1.json")
    events = event_registry["events"]
    if len(events) != 89:
        fail(f"event registry expected 89 entries, found {len(events)}")

    # Reconcile event producer declarations bidirectionally with command
    # emissions. An event with no command producer remains explicitly
    # unresolved; it is not silently assumed to be an external or internal
    # producer. Consumer and owner-transition semantics remain separate gates.
    expected_event_producers = {event_type: set() for event_type in events}
    for command in commands:
        for event_type in command.get("emitted_event_bindings", []):
            if event_type not in expected_event_producers:
                fail(
                    f"{command['command_type']}: emitted event {event_type} "
                    "is absent from the event registry"
                )
            expected_event_producers[event_type].add(command["command_type"])
    for event_type, event in events.items():
        declared = event.get("command_producers")
        if not isinstance(declared, list) or len(declared) != len(set(declared)):
            fail(f"{event_type}: command_producers must be a unique array")
        expected = expected_event_producers[event_type]
        if set(declared) != expected:
            fail(
                f"{event_type}: command producer mismatch; "
                f"declared={sorted(declared)} expected={sorted(expected)}"
            )
        expected_status = "bound" if expected else "unresolved"
        if event.get("command_producer_binding_status") != expected_status:
            fail(
                f"{event_type}: command producer status must be "
                f"{expected_status!r}"
            )

    event_matrix_path = ROOT / "docs/planning/EVENT-PRODUCER-AND-CONSUMER-SEMANTICS-MATRIX.md"
    if not event_matrix_path.is_file():
        fail("missing event producer/consumer semantics matrix")
    event_matrix = event_matrix_path.read_text(encoding="utf-8")
    matrix_event_rows = {}
    for line in event_matrix.splitlines():
        if not line.startswith("| `") or line.count("|") < 4:
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        event_type = cells[0].strip("`")
        producer_cell = cells[1]
        payload_name = cells[2].strip("`")
        producers = {
            part for index, part in enumerate(producer_cell.split("`"))
            if index % 2 == 1 and part
        }
        consumer_transition_summary = cells[3] if len(cells) > 3 else ""
        matrix_event_rows[event_type] = (producers, payload_name, consumer_transition_summary)
    if set(matrix_event_rows) != set(events):
        fail("event producer/consumer matrix inventory does not exactly match event registry")
    for event_type, event in events.items():
        matrix_producers, matrix_payload, matrix_summary = matrix_event_rows[event_type]
        if matrix_producers != set(event["command_producers"]):
            fail(f"{event_type}: event matrix command producers do not match event registry")
        schema_pointer = event["payload_schema_ref"].split("#", 1)[1]
        expected_payload = schema_pointer.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~")
        if matrix_payload != expected_payload:
            fail(
                f"{event_type}: event matrix payload {matrix_payload!r} "
                f"does not match schema definition {expected_payload!r}"
            )
        if matrix_summary != event.get("consumer_transition_summary"):
            fail(f"{event_type}: event matrix consumer/transition summary does not match registry")
        for field in (
            "producer_origin", "producer_trigger_contract", "owning_component",
            "consumer_contracts", "owner_transition_contract",
            "ordering_idempotency_contract", "failure_recovery_contract",
        ):
            if not event.get(field):
                fail(f"{event_type}: missing event field {field}")
        if event.get("specification_status") != "specified_not_runtime_validated":
            fail(f"{event_type}: event specification status is misleading")
        if event["command_producers"] and event["producer_origin"] != "command":
            fail(f"{event_type}: command-produced event has inconsistent producer origin")
        if not event["command_producers"] and event["producer_origin"] == "command":
            fail(f"{event_type}: unbound event cannot claim command producer origin")
        expected_unresolved = ["runtime_handler", "event_specific_acceptance_execution"]
        if set(event.get("unresolved_bindings", [])) != set(expected_unresolved):
            fail(f"{event_type}: unresolved event bindings do not match implementation evidence boundary")

    operation_matrix_path = ROOT / "docs/planning/OPERATION-LIFECYCLE-TRANSITION-MATRIX.md"
    if not operation_matrix_path.is_file():
        fail("missing operation lifecycle transition matrix")
    operation_matrix = operation_matrix_path.read_text(encoding="utf-8")
    operation_rows = {}
    for line in operation_matrix.splitlines():
        if not line.startswith("| `operation."):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 4:
            fail("operation lifecycle matrix row must have four cells")
        operation_rows[cells[0].strip("`")] = (cells[2], cells[3])
    operation_matrix_events = set(operation_rows)
    action_gateway_events = {
        event_type for event_type, event in events.items()
        if event.get("producer_origin") == "action_gateway_internal_transition"
    }
    if len(action_gateway_events) != 15 or operation_matrix_events != action_gateway_events:
        fail("operation lifecycle matrix must exactly cover the 15 Action Gateway internal events")
    operation_states = set(
        schema_docs["domain-payloads.v1.schema.json"]["$defs"]["operationLifecycleEvent"]
        ["properties"]["state"]["enum"]
    )
    for event_type in events:
        if event_type.startswith("operation.") and event_type != "operation.reconciled.v1":
            target_state = event_type.removeprefix("operation.").removesuffix(".v1")
            if target_state not in operation_states:
                fail(f"{event_type}: event target state is absent from operation lifecycle schema")
        # Reconciliation is an evidence-bearing transition event, not a
        # persistent operation state; it resolves to a supported state.

    for event_type in action_gateway_events:
        if operation_rows.get(event_type) != (
            events[event_type]["producer_trigger_contract"],
            events[event_type]["owner_transition_contract"],
        ):
            fail(f"{event_type}: operation lifecycle matrix trigger/transition differs from event registry")
        cells = next(
            [cell.strip() for cell in line.split("|")[1:-1]]
            for line in operation_matrix.splitlines()
            if line.startswith(f"| `{event_type}` |")
        )
        predecessor_states = {state.strip() for state in cells[1].split(",")}
        if not predecessor_states or not predecessor_states <= operation_states:
            fail(f"{event_type}: predecessor state is absent from operation lifecycle schema")
        target_state = event_type.removeprefix("operation.").removesuffix(".v1")
        if target_state in predecessor_states:
            fail(f"{event_type}: self-transition is not permitted")
    for event_type in action_gateway_events:
        event = events[event_type]
        trigger = event.get("producer_trigger_contract", "")
        if (
            "No public command producer is bound" in trigger
            or "exact runtime trigger remains unimplemented" in trigger
            or "exact_internal_producer_trigger" in event.get("unresolved_bindings", [])
        ):
            fail(f"{event_type}: Action Gateway internal producer trigger is still generic/unresolved")

    non_command_events = {
        event_type for event_type, event in events.items()
        if not event.get("command_producers")
        and event.get("producer_origin") != "action_gateway_internal_transition"
    }
    ingress_matrix_path = ROOT / "docs/planning/EVENT-INGRESS-AND-INTERNAL-PRODUCER-TRIGGER-MATRIX.md"
    if not ingress_matrix_path.is_file():
        fail("missing non-command event ingress/internal producer trigger matrix")
    ingress_matrix = ingress_matrix_path.read_text(encoding="utf-8")
    ingress_matrix_events = set(
        re.findall(r"`([a-z][a-z0-9_.]+\.v1)`", ingress_matrix)
    )
    if len(non_command_events) != 22 or ingress_matrix_events != non_command_events:
        fail("non-command event trigger matrix must exactly cover the 22 non-command/non-Action-Gateway events")
    ingress_rows = {}
    for line in ingress_matrix.splitlines():
        if not line.startswith("| `") or line.count("|") < 4:
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 4:
            continue
        event_type = cells[0].strip("`")
        if event_type in non_command_events:
            ingress_rows[event_type] = (cells[1], cells[2], cells[3])
    for event_type in non_command_events:
        event = events[event_type]
        if ingress_rows.get(event_type) != (
            event["producer_origin"],
            event["producer_trigger_contract"],
            event["owner_transition_contract"],
        ):
            fail(f"{event_type}: non-command trigger matrix differs from event registry")
    for event_type in non_command_events:
        event = events[event_type]
        trigger = event.get("producer_trigger_contract", "")
        if (
            "No public command producer is bound" in trigger
            or "exact runtime trigger remains unimplemented" in trigger
            or "exact_internal_producer_trigger" in event.get("unresolved_bindings", [])
        ):
            fail(f"{event_type}: non-command producer trigger is still generic/unresolved")

    scenario_contracts = load(SCHEMAS / "fixtures/scenario-contracts.fixture.json")
    scenarios = scenario_contracts["scenarios"]
    expected_scenario_ids = {
        *(f"INT-{index:03d}" for index in range(1, 4)),
        *(f"CM-{index:03d}" for index in range(1, 22)),
        *(f"AD-{index:03d}" for index in range(1, 16)),
    }
    scenario_ids = {item["scenario_id"] for item in scenarios}
    step_count = sum(len(item["steps"]) for item in scenarios)
    negative_control_count = sum(len(item["negative_controls"]) for item in scenarios)
    if len(scenarios) != 39 or scenario_ids != expected_scenario_ids:
        fail("scenario contract fixture must contain INT-001…003, CM-001…021 and AD-001…015")
    if step_count != 172 or negative_control_count != 45:
        fail(
            f"scenario fixture expected 172 ordered steps and 45 negative controls; "
            f"found {step_count} steps and {negative_control_count} controls"
        )
    command_types = {item["command_type"] for item in commands}
    query_types = {item["query_type"] for item in queries}
    domain_payload_defs = set(schema_docs["domain-payloads.v1.schema.json"].get("$defs", {}))
    world_payload_defs = set(schema_docs["world-interaction.v1.schema.json"].get("$defs", {}))
    expected_event_scenario_refs = {}
    for scenario in scenarios:
        for step in scenario["steps"]:
            for event_type in step.get("expected_events", []):
                expected_event_scenario_refs.setdefault(event_type, set()).add(scenario["scenario_id"])
    for event_type, event in events.items():
        if set(event.get("acceptance_scenario_refs", [])) != expected_event_scenario_refs.get(event_type, set()):
            fail(f"{event_type}: acceptance scenario references do not match scenario fixture coverage")
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        if scenario.get("execution_status") != "specified_not_executed" or scenario.get("execution_authority") != "none":
            fail(f"{scenario_id}: scenario fixture must not imply execution or authority")
        for field in (
            "initial_state", "steps", "negative_controls", "restart_replay_controls",
            "concurrency_controls", "fault_controls", "held_out_controls",
        ):
            if not scenario.get(field):
                fail(f"{scenario_id}: missing scenario field {field}")
        if not scenario.get("acceptance_thresholds", {}).get("hard_invariants"):
            fail(f"{scenario_id}: missing hard acceptance invariants")
        if not scenario.get("acceptance_thresholds", {}).get("evidence_requirement"):
            fail(f"{scenario_id}: missing evidence requirement")
        for reference in scenario.get("contract_refs", []):
            if reference.startswith("payload:"):
                payload_name = reference.split(":", 1)[1]
                if payload_name not in domain_payload_defs | world_payload_defs:
                    fail(f"{scenario_id}: unknown payload reference {payload_name}")
            elif reference in command_types or reference in query_types or reference in events:
                continue
            elif reference.startswith("catalogue:"):
                if not reference.split(":", 1)[1]:
                    fail(f"{scenario_id}: empty catalogue reference")
            else:
                # Catalogue IDs use a stable PREFIX-NNN form.
                parts = reference.split("-")
                if len(parts) < 2 or not parts[-1].isdigit():
                    fail(f"{scenario_id}: unresolved contract reference {reference!r}")
        for step in scenario["steps"]:
            action = step.get("contract_action", "")
            if action.startswith("command:") and action.split(":", 1)[1] not in command_types:
                fail(f"{scenario_id}/{step.get('step_id')}: unknown command action {action}")
            if action.startswith("query:") and action.split(":", 1)[1] not in query_types:
                fail(f"{scenario_id}/{step.get('step_id')}: unknown query action {action}")
            if not step.get("expected_transitions") or not step.get("durable_assertions"):
                fail(f"{scenario_id}/{step.get('step_id')}: missing transition or durable-state assertions")
            unknown_step_events = set(step.get("expected_events", [])) - set(events)
            if unknown_step_events:
                fail(f"{scenario_id}/{step.get('step_id')}: unknown events {sorted(unknown_step_events)}")
        for control in scenario["negative_controls"]:
            if not control.get("expected_disposition") or not control.get("must_not_change"):
                fail(f"{scenario_id}/{control.get('control_id')}: incomplete negative control")
        if scenario_id in {"INT-001", "CM-012", "CM-013", "CM-016", "AD-009"}:
            metric_rule = scenario["acceptance_thresholds"].get("learning_metric_rule", "")
            if "pre-register" not in metric_rule.lower() and "pre-register" not in scenario["acceptance_thresholds"].get("learning_metric_rule","").lower():
                fail(f"{scenario_id}: learning scenario lacks pre-registered metric rule")

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

    def resolve_schema_reference(reference: str, label: str):
        schema_path, separator, pointer = reference.partition("#")
        if not separator or not schema_path.startswith("schemas/"):
            fail(f"{label}: malformed schema reference {reference!r}")
        schema_name = Path(schema_path).name
        document = schema_docs.get(schema_name)
        if document is None:
            fail(f"{label}: schema file {schema_path!r} is not in the validated schema set")
        target = resolve_pointer(document, "#" + pointer, f"{label} schema")
        if not isinstance(target, dict):
            fail(f"{label}: schema pointer does not resolve to a schema object")
        return document, pointer

    fixture_cache = {}

    # Shared cache must exist before command/query fixture validation invokes the helper.
    fixture_cache = {}

    def validate_bound_fixture(reference: str, selected_schema_ref: str, label: str):
        fixture_path, separator, fixture_pointer = reference.partition("#")
        if not separator or not fixture_path.startswith("schemas/fixtures/"):
            fail(f"{label}: malformed fixture reference {reference!r}")
        if fixture_path not in fixture_cache:
            path = ROOT / fixture_path
            if not path.is_file():
                fail(f"{label}: fixture file does not exist: {fixture_path}")
            fixture_cache[fixture_path] = load(path)
        payload = resolve_pointer(
            fixture_cache[fixture_path], "#" + fixture_pointer, f"{label} fixture"
        )
        schema_document, schema_pointer = resolve_schema_reference(selected_schema_ref, label)
        wrapper = {
            "$schema": schema_document["$schema"],
            "$defs": schema_document.get("$defs", {}),
            "$ref": "#" + schema_pointer,
        }
        validate(payload, wrapper, f"{label} fixture {reference}")

    for item in commands:
        if item["dispatch_status"] == "deferred_by_scope":
            continue
        command_type = item["command_type"]
        for fixture_ref in item["fixture_refs"]:
            leaf = fixture_ref.rsplit("/", 1)[-1]
            selected = (
                item["envelope_schema"] if leaf == "commandEnvelope"
                else item["response_schema"] if leaf == "commandResponse"
                else item["request_schema"]
            )
            validate_bound_fixture(fixture_ref, selected, command_type)

    for item in queries:
        query_type = item["query_type"]
        for fixture_ref in item["fixture_refs"]:
            leaf = fixture_ref.rsplit("/", 1)[-1]
            input_schema_leaf = item["input_schema"].rsplit("/", 1)[-1]
            selected = (
                item["envelope_schema"] if leaf == "queryEnvelope"
                else item["response_schema"] if leaf == "queryResponse"
                else item["input_schema"] if leaf == input_schema_leaf
                else item["result_item_schema"]
            )
            validate_bound_fixture(fixture_ref, selected, query_type)

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

    # Validate integrated scenario contracts as design fixtures, not runtime tests.
    scenario_document = load(FIXTURES / "scenario-contracts.fixture.json")
    scenarios = scenario_document["scenarios"]
    if len(scenarios) != 39:
        fail(f"scenario contract fixture expected 39 scenarios, found {len(scenarios)}")
    known_commands = {item["command_type"] for item in commands}
    known_queries = {item["query_type"] for item in queries}
    known_scenario_ids = {
        *(f"CM-{number:03d}" for number in range(1, 30)),
        *(f"AD-{number:03d}" for number in range(1, 16)),
    }
    scenario_ids = set()
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        if scenario_id in scenario_ids:
            fail(f"{scenario_id}: duplicate integrated scenario ID")
        scenario_ids.add(scenario_id)
        unknown_sources = set(scenario["source_scenario_ids"]) - known_scenario_ids
        if unknown_sources:
            fail(f"{scenario_id}: unknown source scenario IDs {sorted(unknown_sources)}")
        step_ids = [step["step_id"] for step in scenario["steps"]]
        if len(step_ids) != len(set(step_ids)):
            fail(f"{scenario_id}: duplicate step IDs")
        control_ids = [item["control_id"] for item in scenario["negative_controls"]]
        if len(control_ids) != len(set(control_ids)):
            fail(f"{scenario_id}: duplicate negative-control IDs")
        for step in scenario["steps"]:
            kind, separator, name = step["contract_action"].partition(":")
            if not separator:
                fail(f"{scenario_id}/{step['step_id']}: malformed contract action")
            if kind == "command" and name not in known_commands:
                fail(f"{scenario_id}/{step['step_id']}: unknown command {name}")
            if kind == "query" and name not in known_queries:
                fail(f"{scenario_id}/{step['step_id']}: unknown query {name}")
            if kind == "event" and name not in known_event_types:
                fail(f"{scenario_id}/{step['step_id']}: unknown event action {name}")
            unknown_events = set(step["expected_events"]) - known_event_types
            if unknown_events:
                fail(
                    f"{scenario_id}/{step['step_id']}: unknown expected events "
                    f"{sorted(unknown_events)}"
                )
        if scenario["execution_status"] != "specified_not_executed" or scenario["execution_authority"] != "none":
            fail(f"{scenario_id}: scenario fixture cannot imply execution or authority")

    required_scenario_ids = {
        *(f"INT-{number:03d}" for number in range(1, 4)),
        *(f"CM-{number:03d}" for number in range(1, 22)),
        *(f"AD-{number:03d}" for number in range(1, 16)),
    }
    if scenario_ids != required_scenario_ids:
        fail(
            "scenario fixture inventory mismatch: "
            f"missing={sorted(required_scenario_ids - scenario_ids)}; "
            f"unexpected={sorted(scenario_ids - required_scenario_ids)}"
        )

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
