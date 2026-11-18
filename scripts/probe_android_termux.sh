#!/system/bin/sh
# Read-only Android/Termux baseline collector. Run with:
#   sh scripts/probe_android_termux.sh
# Output is diagnostic evidence; redact unrelated identifiers before sharing.

set -u

section() { printf '\n===== %s =====\n' "$1"; }
run() {
  label="$1"; shift
  printf '\n--- %s ---\n' "$label"
  "$@" 2>&1 || printf '[UNAVAILABLE / FAILED: exit=%s]\n' "$?"
}

section "Collection metadata"
date -u '+utc=%Y-%m-%dT%H:%M:%SZ' 2>&1 || true
printf 'shell=%s\n' "${SHELL:-unknown}"
printf 'prefix=%s\n' "${PREFIX:-unknown}"
printf 'home=%s\n' "${HOME:-unknown}"

section "Android build properties"
if command -v getprop >/dev/null 2>&1; then
  for key in ro.product.manufacturer ro.product.model ro.product.device \
    ro.build.version.release ro.build.version.sdk ro.build.version.security_patch \
    ro.build.fingerprint ro.product.cpu.abi ro.product.cpu.abilist; do
    printf '%s=' "$key"
    getprop "$key" 2>&1 || true
  done
else
  printf 'getprop=NOT AVAILABLE\n'
fi

section "Kernel and ABI"
run "uname" uname -a
run "process bitness" getconf LONG_BIT
run "memory summary" sh -c 'grep -E "^(MemTotal|MemAvailable|SwapTotal|SwapFree):" /proc/meminfo'

section "Termux installation"
if command -v termux-info >/dev/null 2>&1; then
  termux-info 2>&1 || true
else
  printf 'termux-info=NOT INSTALLED\n'
fi
run "package manager" sh -c 'command -v pkg; command -v apt; command -v dpkg'
run "compiler inventory" sh -c 'command -v clang; command -v c++; command -v cmake; command -v ninja; command -v python; command -v python3'

section "SQLite CLI"
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 --version 2>&1 || true
  printf '\n--- SQLite compile options ---\n'
  sqlite3 :memory: 'PRAGMA compile_options;' 2>&1 || true
  printf '\n--- SQLite JSON probe ---\n'
  sqlite3 :memory: "SELECT json_valid('{}'), json_valid('{');" 2>&1 || true
  printf '\n--- SQLite foreign-key probe ---\n'
  sqlite3 :memory: 'PRAGMA foreign_keys=ON; PRAGMA foreign_keys;' 2>&1 || true
  printf '\n--- SQLite WAL probe ---\n'
  sqlite3 :memory: 'PRAGMA journal_mode=WAL;' 2>&1 || true
else
  printf 'sqlite3=NOT INSTALLED\n'
fi

section "Storage"
run "filesystem capacity" df -h "${HOME:-.}"
run "filesystem inodes" df -i "${HOME:-.}"

section "Optional Termux API"
if command -v termux-battery-status >/dev/null 2>&1; then
  termux-battery-status 2>&1 || true
else
  printf 'termux-battery-status=NOT INSTALLED\n'
fi
if command -v termux-wake-lock >/dev/null 2>&1; then
  printf 'termux-wake-lock=AVAILABLE (not invoked)\n'
else
  printf 'termux-wake-lock=NOT INSTALLED\n'
fi

section "Collection boundary"
printf '%s\n' 'This script is read-only. It does not change permissions, acquire wake locks, install packages, create databases, or test Android lifecycle behaviour.'
