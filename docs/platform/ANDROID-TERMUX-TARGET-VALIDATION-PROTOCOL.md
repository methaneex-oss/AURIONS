# Android / Termux Target Baseline Validation Protocol

**Status:** Builder procedure; target measurements NOT YET RECORDED.  
**Finding:** BR-006.  
**Authority boundary:** This protocol does not select a target device, authorize a first Android action, grant permissions, or approve an Android integration.

## 1. Purpose

Establish reproducible evidence for the exact Android device and Termux environment on which AURIONS platform feasibility will be evaluated. Do not infer device capabilities from Android version alone, assume root, or treat a successful host build as Android validation.

The target must be explicitly selected by the project owner. If no target is selected, record this protocol as prepared and the empirical gate as BLOCKED — TARGET NOT SELECTED.

## 2. Required identity record

Record all of the following from the same device and test session:

| Field | Required evidence |
|---|---|
| Manufacturer and commercial model | Device settings and `ro.product.manufacturer` / `ro.product.model` |
| Android release and API level | Settings plus `ro.build.version.release` and `ro.build.version.sdk` |
| Build identity | Full `ro.build.fingerprint`; security patch level |
| ABI and process bitness | `uname -m`, `getprop ro.product.cpu.abi`, `getconf LONG_BIT` |
| Termux distribution/version | `termux-info` output, install source and package version |
| Runtime/toolchain | Python, C/C++ compiler, linker and package versions actually installed |
| SQLite | CLI/library version, compile options, JSON function probe, foreign-key probe, WAL probe |
| Storage | Available bytes/inodes for app home and intended database/artifact locations |
| Memory/resource envelope | `/proc/meminfo`, process limits, measured peak RSS and CPU for representative probes |
| Permission state | Exact Android runtime permissions, special app access, Termux:API availability and granted status |
| Power/background state | Battery optimization state, background restriction state, screen-off and process-reclaim observations |
| Network | Connectivity state and any OS/VPN/data-saver restrictions relevant to the test |

Redact account identifiers, serial numbers, Android ID, phone numbers, Wi-Fi names, tokens and unrelated personal data from the evidence bundle. The build fingerprint is retained only in the restricted project validation record.

## 3. Collection

From the selected Termux installation, run:

```sh
sh scripts/probe_android_termux.sh
```

Preserve the raw output, date/time, device identity, Termux install source and operator notes. Do not manually edit raw output; add interpretation in a separate report.

If a command is unavailable, record `NOT INSTALLED` or `UNAVAILABLE`; do not silently omit it. If a value is permission-restricted, record the exact denial.

## 4. SQLite acceptance

The target must demonstrate all of the following against the actual SQLite library used by the eventual runtime:

1. Version is at least the proposed 3.38.0 baseline, or a documented architecture decision changes the baseline before implementation.
2. `STRICT` table creation succeeds.
3. `json_valid('{}')` returns 1 and malformed JSON returns 0.
4. `PRAGMA foreign_keys` returns 1 on each opened connection after application initialization.
5. A foreign-key violation is rejected.
6. WAL mode can be enabled where required, and checkpoint/backup behaviour is recorded.
7. The complete base/migration chain passes on a clean database and on every supported upgrade fixture.
8. The process can reopen each database after normal termination; interrupted migration and restore tests are separately recorded.

A CLI SQLite version is not sufficient if the runtime links a different SQLite library. Record the actual library version and compile options from the runtime binding used by AURIONS.

## 5. Android lifecycle and permission acceptance

For each proposed platform integration (without selecting an action in this protocol), record:
- API/permission required, protection level and user-grant path.
- Whether permission can be revoked while the process is running.
- Behaviour after process death, force-stop, reboot, screen-off and battery optimization.
- Whether the operation requires foreground service, notification, user interaction or special app access.
- Exact denial, timeout, cancellation and partial-completion behaviour.
- Evidence that OS permission and AURIONS owner authorization are checked independently.
- Evidence that stale grants or stale capability observations cannot authorize execution.

Do not infer that Termux can access arbitrary Android APIs, private application data, unrestricted background execution or protected settings. Validate each API against official Android documentation for the recorded API level and actual device behaviour.

## 6. Resource and reliability measurements

For each representative workload, record:
- Input size and fixture identifier.
- Wall-clock duration and CPU time.
- Peak resident memory.
- Database size before/after and WAL growth.
- Storage available before/after.
- Battery/thermal conditions.
- Whether the process was throttled, reclaimed, paused or terminated.
- Repetition count, median and worst observed result.

Do not invent performance thresholds. Establish baselines first, then propose thresholds with workload rationale for owner approval.

## 7. Required test cases

- Fresh install and clean database initialization.
- Existing supported upgrade path for each store.
- Process termination before migration commit and after commit.
- Low-storage and read-only database handling.
- Database busy/locked and corruption handling.
- Backup and restore to a separate location.
- App backgrounding, screen-off, process reclaim and reboot.
- Permission denial, revocation and re-grant.
- Network unavailable and network transition where relevant.
- Repeated start/stop and recovery without duplicate external effects.

Each case must include exact steps, expected result, actual result, logs/diagnostic references and tested build identity. A test not run is marked NOT RUN, never PASS.

## 8. Evidence package and verdict

The validation package must contain:
1. Raw probe output.
2. Redacted device/build identity sheet.
3. Exact Termux package/toolchain inventory.
4. SQLite runtime and compile-option evidence.
5. Test-case execution matrix with logs.
6. Resource measurements and reproducible commands.
7. Official Android API references pinned to the tested API level.
8. Deviations, unsupported assumptions and residual risks.

Verdicts:
- **PASS** — all required cases for the selected target passed.
- **PASS WITH LIMITATIONS** — limitations are bounded and explicitly accepted by the owner.
- **FAIL** — a required case failed.
- **BLOCKED** — target or required access/evidence is unavailable.

## 9. Current builder status

The protocol and collection script are builder deliverables. No device has been selected by this protocol, and no target measurements or Android lifecycle tests are claimed. BR-006 remains open until the owner-selected target is measured and the required empirical cases are executed.
