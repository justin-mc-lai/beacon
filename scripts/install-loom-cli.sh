#!/usr/bin/env bash
# =============================================================================
# install-loom-cli.sh — Install Rust Loom / Beacon-v2 CLI only
# =============================================================================
# Does NOT touch production Python `beacon` launcher.
# Builds packages/beacon-rs beacon-cli and installs:
#   - beacon-v2  (canonical Rust binary name)
#   - loom       (brand alias → same binary)
#
# Usage:
#   bash scripts/install-loom-cli.sh
#   PREFIX=$HOME/.local bash scripts/install-loom-cli.sh
#   SKIP_BUILD=1 bash scripts/install-loom-cli.sh   # install from existing release build
#
# PATH governance:
#   After install, `type -a loom` must list PREFIX/bin/loom (Rust) before any
#   Python loom-py / site-packages script. Remove stale Python `loom` entry via:
#     pip install -e .   # after pyproject renamed loom -> loom-py
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RS_ROOT="$REPO_ROOT/packages/beacon-rs"
PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="${PREFIX}/bin"
SKIP_BUILD="${SKIP_BUILD:-0}"
PROFILE="${PROFILE:-release}"

log()  { echo "[install-loom-cli] $*"; }
fail() { echo "[install-loom-cli] FAIL: $*" >&2; exit 1; }

command -v cargo >/dev/null 2>&1 || fail "cargo not found (Rust toolchain required)"

mkdir -p "$BIN_DIR"

if [[ "$SKIP_BUILD" != "1" ]]; then
  log "Building beacon-cli ($PROFILE) in $RS_ROOT"
  (
    cd "$RS_ROOT"
    if [[ "$PROFILE" == "release" ]]; then
      cargo build --release -p beacon-cli
    else
      cargo build -p beacon-cli
    fi
  )
else
  log "SKIP_BUILD=1 — using existing artifacts"
fi

if [[ "$PROFILE" == "release" ]]; then
  ART_DIR="$RS_ROOT/target/release"
else
  ART_DIR="$RS_ROOT/target/debug"
fi

SRC_V2="$ART_DIR/beacon-v2"
SRC_LOOM="$ART_DIR/loom"

[[ -x "$SRC_V2" ]] || fail "missing binary: $SRC_V2 (build failed?)"

# Prefer cargo-built loom bin if present; else copy beacon-v2 as loom
if [[ -x "$SRC_LOOM" ]]; then
  SRC_FOR_LOOM="$SRC_LOOM"
else
  SRC_FOR_LOOM="$SRC_V2"
fi

# Never overwrite production beacon
if [[ -e "$BIN_DIR/beacon" || -L "$BIN_DIR/beacon" ]]; then
  log "Preserving existing $BIN_DIR/beacon (production Python CLI — not modified)"
fi

install_bin() {
  local src="$1"
  local name="$2"
  local dest="$BIN_DIR/$name"
  cp -f "$src" "$dest"
  chmod +x "$dest"
  log "Installed $dest"
}

install_bin "$SRC_V2" "beacon-v2"
install_bin "$SRC_FOR_LOOM" "loom"

# Hard guard: refuse to write beacon
if [[ -e "$BIN_DIR/beacon" ]]; then
  if file "$BIN_DIR/beacon" 2>/dev/null | grep -qi 'mach-o\|elf'; then
    # only warn if someone put a rust beacon there — still don't touch
    :
  fi
fi

log "Verifying..."
"$BIN_DIR/beacon-v2" --help >/dev/null
"$BIN_DIR/loom" --help >/dev/null

# PATH advice
case ":$PATH:" in
  *":$BIN_DIR:"*) log "PATH already contains $BIN_DIR" ;;
  *)
    log "WARN: $BIN_DIR is not on PATH. Add:"
    log "  export PATH=\"$BIN_DIR:\$PATH\""
    ;;
esac

# Detect Python loom shadowing
if command -v loom >/dev/null 2>&1; then
  first="$(command -v loom)"
  if head -1 "$first" 2>/dev/null | grep -q python; then
    log "WARN: first loom on PATH is Python: $first"
    log "  Re-run: pip install -e .  (loom console script removed → loom-py only)"
    log "  Ensure $BIN_DIR precedes that directory on PATH"
  elif [[ "$first" == "$BIN_DIR/loom" ]]; then
    log "OK: loom resolves to Rust binary at $first"
  else
    log "NOTE: loom resolves to $first (ensure it is the Rust install)"
  fi
fi

log "Done."
log "  beacon-v2 → $BIN_DIR/beacon-v2"
log "  loom      → $BIN_DIR/loom"
log "  production beacon CLI is unchanged"
