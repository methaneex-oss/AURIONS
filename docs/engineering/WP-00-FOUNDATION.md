# WP-00 — Foundation and Build System

**Status:** Initial scaffold committed to the WP-00 working branch. Not yet validated by a local clean build or CI run.

## Scope

WP-00 establishes repository hygiene, a minimal C++ build/test entry point, and continuous integration. It does not implement cognition, persistence, inference, memory, autonomous actions, or learning.

## Repository layout

- `core/cpp/include/aurions/` — public C++ interfaces.
- `core/cpp/src/` — C++ implementation.
- `core/cpp/tests/` — C++ tests.
- `workers/python/` — reserved for later isolated Python workers; no worker protocol is implemented yet.
- `docs/planning/` — imported planning baseline.
- `docs/engineering/` — implementation records and engineering decisions.
- `.github/workflows/` — CI workflows.

## Build

Requires CMake 3.20+ and a C++ compiler with C++20 support.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DAURIONS_BUILD_TESTS=ON
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

C++20 is a provisional project baseline for this scaffold, not a final device-validated toolchain decision. The actual Android/Termux compiler and clean-build path must be measured before the baseline is locked.

## Current baseline

- One dependency-free static library target: `aurions_core`.
- One smoke test proving the core target can be linked and called.
- CTest registration.
- GitHub Actions workflow for configure, build and test.
- Ignore rules for build output, runtime databases, model weights, datasets, credentials and local environments.

The version function is build scaffolding only. It is not an application runtime or an assistant capability.

## Explicitly not done

- No third-party runtime dependency has been selected or pinned.
- No SQLite schema has been executed or validated.
- No JSON/message contract has been implemented.
- No Python worker exists.
- No Android/Termux build has been run from this repository.
- No performance, memory, thermal, battery or background-execution claim is made.
- No security boundary or live tool execution exists.

## WP-00 exit evidence still required

1. Clean configure/build/test on a fresh checkout.
2. Green CI run for this branch.
3. Reproducible build on the actual Termux target, with compiler/CMake versions recorded.
4. Dependency and license inventory before adding external libraries.
5. Confirmed project layout and build conventions.

## Change discipline

Keep this work limited to foundation. Shared event/worker contracts belong to WP-01 and should be implemented only against the approved specification. Do not add dependencies merely to anticipate later work.
