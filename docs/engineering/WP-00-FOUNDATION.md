# WP-00 — Foundation and Build System

**Status:** Foundation scaffold proposal only. Hosted GitHub Actions configure/build/test passed for commit `913e5626211b76776e70c8c5beef6aae00bf4365` in [run 43052743168](https://github.com/methaneex-oss/AURIONS/actions/runs/43052743168). Local clean build and target-device validation remain outstanding. WP-00 is not accepted and implementation is not authorized.

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

1. **Hosted CI evidence: PASSED.** Configure/build/test completed successfully in the recorded GitHub Actions run.
2. Fresh local host configure/build/test with reproducible toolchain versions: outstanding.
3. Reproducible build on the actual Termux target, with compiler/CMake versions recorded: outstanding.
4. Dependency and license inventory before adding external libraries: outstanding.
5. Confirmed project layout and build conventions against the final approved canonical roadmap: outstanding.

## Change discipline

Keep this work limited to foundation. Shared event/worker contracts belong to WP-01 in the current proposed roadmap and should be implemented only against the owner-approved planning baseline. See PR #2 and `docs/planning/CANONICAL-IMPLEMENTATION-ROADMAP.md` once that planning baseline is merged. Do not add dependencies merely to anticipate later work.


## Authority and merge status

This PR remains a draft proposal. It must not be merged or treated as the start of implementation until PR #2's planning baseline is reconciled, independently reviewed and explicitly approved by the owner. After the planning baseline is accepted, rebase/reconcile this branch against the accepted base and recheck the changed files before merging.
