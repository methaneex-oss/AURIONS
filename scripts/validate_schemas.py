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
        if schema.get("$id"):
            registry = registry.with_resource(schema["$id"], resource)

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

    # Every positive domain fixture is validated against the correspondingly
    # named reusable definition, not merely parsed as JSON.
    domain_schema = schema_docs["domain-payloads.v1.schema.json"]
    domain_fixture = load(FIXTURES / "domain-payloads.fixture.json")
    for name, payload in domain_fixture.items():
        if name not in domain_schema["$defs"]:
            fail(f"domain fixture {name}: no same-named schema definition")
        validate(payload, {"$ref": f"domain-payloads.v1.schema.json#/$defs/{name}"},
                 f"positive domain fixture {name}")

    # Additional focused positive fixtures.
    for fixture_name, definition in [
        ("decision-recorded.fixture.json", "decisionRecorded"),
        ("provider-lifecycle.fixture.json", None),
        ("provider-lifecycle-enabled.fixture.json", None),
    ]:
        payload = load(FIXTURES / fixture_name)
        if definition:
            validate(payload, {"$ref": f"domain-payloads.v1.schema.json#/$defs/{definition}"},
                     fixture_name)
        else:
            for name, value in payload.items():
                validate(value, {"$ref": f"domain-payloads.v1.schema.json#/$defs/{name}"},
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
        target = ({"$ref": f"{schema_name}#/$defs/{definition}"}
                  if definition else schema)
        try:
            validate(instance, target, f"negative control {filename}")
        except AssertionError:
            continue
        fail(f"negative control unexpectedly validated: {filename}")

    print(
        f"PASS: {len(schema_docs)} Draft 2020-12 schemas; "
        f"{len(pairs)} paired registry/fixture checks; "
        f"{len(domain_fixture)} positive domain payloads; "
        f"{len(negative_cases)} negative controls."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # Keep CI output concise and actionable.
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
