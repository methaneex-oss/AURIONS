# AURIONS

**AURIONS** is the repository/system identifier; the final **S** denotes **System**.

This repository is the implementation home for the adaptive, persistent intelligence system described in the planning specification. Its foundational principle is:

> Engineer the mechanisms; let behaviour be acquired through experience.

The system is not intended to be a chatbot wrapper or a collection of hardcoded stimulus-to-response rules. Learning must be demonstrated through persistent, experience-dependent changes and repeatable evaluation.

## Project status

**Current stage:** repository foundation / WP-00.

The initial planning design is consolidated. Implementation-readiness evidence gates remain; see the [planning status and owner gate](docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md). Do not interpret a documented design as implemented functionality.

## Build the C++ foundation

Requires CMake 3.20+ and a C++20-capable compiler. The C++20 setting is provisional until validated on the target Termux environment.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DAURIONS_BUILD_TESTS=ON
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

See [WP-00 foundation record](docs/engineering/WP-00-FOUNDATION.md) for scope and outstanding validation.

## Start here

- [Planning documentation index](docs/planning/README.md)
- [Complete initial engineering specification](docs/planning/INITIAL-ENGINEERING-SPECIFICATION.md)
- [Canonical Notion project control center](https://app.notion.com/p/41505b96eab381778361fc0d0ccf6344?pvs=204)

## Engineering direction

- C++ authoritative core and runtime.
- Python workers for training, datasets, experiments and evaluation.
- SQLite initially, with separate memory, event/recovery and governance stores.
- Model-independent inference interfaces.
- Offline-first operation with policy-controlled external resources.
- Explicit governance, authorization, audit, recovery and privacy boundaries.
- Build and validate on the actual Android/Termux target; do not infer device suitability from a successful basic inference run.

## Repository integrity

Do not commit runtime databases, personal memory, model weights, secrets, credentials, private datasets or generated artifacts unless an explicit, reviewed policy permits it. Keep source, reproducible configuration, tests and non-sensitive documentation under version control.
