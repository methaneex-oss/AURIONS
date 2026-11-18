# AURIONS — Schema Validation Results

- **Date:** 2026-11-12
- **Branch:** `docs/complete-system-architecture`
- **Workflow:** [Schema contract validation](https://github.com/methaneex-oss/AURIONS/actions/workflows/schema-validation.yml)
- **Successful run:** [successful run (GitHub Actions run 43217336534)](https://github.com/methaneex-oss/AURIONS/actions/runs/43217131284)
- **Validated revision:** `9db94d6d399c9e18bc15c117fc6ab80d02f49990`
- **Validator:** Python 3.12; `jsonschema[format]==4.26.0`; `Draft202012Validator`; format checker enabled.
- **Result:** PASS.

## Executed checks

The CI log reported:

```
PASS: 8 Draft 2020-12 schemas; 7 paired registry/fixture checks; 78 positive domain payloads; 29 negative controls.
```

The validator checks all eight top-level schema documents against the Draft 2020-12 meta-schema; validates seven registry/fixture pairs; validates each of the 78 named positive domain fixtures against its same-named reusable schema definition; validates additional decision-recorded and provider-lifecycle fixtures; and requires all 29 negative fixture files to be explicitly mapped and rejected. It also asserts the safety state of the registries: 45 unique commands, 21 unique queries, 84 non-dispatchable events and 35 seed errors with matching handler-contract fixture references. These are structural safety assertions, not runtime semantic validation.

## Defects found and corrected during test development

1. Initial workflow setup failed because pip caching used the default dependency-file path while the repository used `requirements-validation.txt`. The workflow now sets `cache-dependency-path` explicitly.
2. The first schema execution found an unresolvable relative external reference from the error-handler fixture schema to `contractError`. The reference was changed to the domain schema's canonical URN.
3. The domain schema's external capability-descriptor reference was likewise normalized to the canonical URN. Fixture fragment references in the validator now use canonical schema identifiers.

The final successful run includes these corrections and the additional registry safety assertions.

## Limits

This result does **not** prove C++ validator equivalence or C++/Python serialization compatibility; Android/Termux feasibility of the Python validation dependency; correct command/query/event handler semantics or authorization; runtime dispatch, persistence, migrations, recovery or learning behaviour; or that schema validity implies semantic correctness, permission, trust or successful real-world effects.

The registries remain design-only/non-dispatchable. This is a verified schema/fixture validation gate, not implementation completion or planning-exit approval.
