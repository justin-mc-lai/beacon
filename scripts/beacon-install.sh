#!/usr/bin/env bash
# =============================================================================
# beacon-install.sh — Idempotent single-root installer for Beacon skills
# =============================================================================
# Usage:
#   bash scripts/beacon-install.sh               # install for all hosts
#   bash scripts/beacon-install.sh agents        # install for one host
#   DRY_RUN=true bash scripts/beacon-install.sh  # preview only
#
# What it does:
#   Creates a symlink: ~/.<host>/skills/beacon -> <repo>/skills/beacon
#   Guards against accidental duplicate real-directory installs.
#   Safe to re-run — existing correct symlinks are left unchanged.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SOURCE="$REPO_ROOT/skills/beacon"
DRY_RUN="${DRY_RUN:-false}"

HOSTS=(agents codex cursor trae windsurf opencode pi qoder trellis reasonix)

# --- helpers ------------------------------------------------------------------
log()  { echo "[beacon-install] $*"; }
info() { echo "  OK $*"; }
warn() { echo "  WARN $*" >&2; }
fail() { echo "  FAIL $*" >&2; exit 1; }

check_prereqs() {
  [[ -d "$SKILLS_SOURCE" ]] || fail "Skills source not found: $SKILLS_SOURCE"
  command -v python3 >/dev/null 2>&1 || warn "python3 not found — beacon doctor may fail"
}

install_host() {
  local host="$1"
  local target_base="$HOME/.$host/skills"
  local target="$target_base/beacon"

  log "Host: .$host -> $target"

  # Guard: real directory (not symlink) = likely a duplicate install
  if [[ -d "$target" && ! -L "$target" ]]; then
    warn "$target is a REAL directory (not a symlink)."
    warn "This may cause duplicate-skill discovery. To fix:"
    warn "  rm -rf $target && bash scripts/beacon-install.sh $host"
    return 1
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    info "[DRY RUN] ln -sfn $SKILLS_SOURCE $target"
    return 0
  fi

  mkdir -p "$target_base"

  if [[ -L "$target" ]]; then
    current="$(readlink "$target")"
    if [[ "$current" == "$SKILLS_SOURCE" ]]; then
      info "Already linked correctly — skipping."
      return 0
    else
      info "Re-linking (was: $current)"
    fi
  fi

  ln -sfn "$SKILLS_SOURCE" "$target"
  info "Linked: $target -> $SKILLS_SOURCE"
}

# --- main ---------------------------------------------------------------------
check_prereqs

HOST="${1:-all}"

if [[ "$HOST" == "all" ]]; then
  failed=0
  for h in "${HOSTS[@]}"; do
    install_host "$h" || ((failed++)) || true
  done
  echo ""
  log "Done. $((${#HOSTS[@]} - failed))/${#HOSTS[@]} hosts installed."
  [[ $failed -eq 0 ]] || warn "$failed host(s) had warnings — review above."
else
  install_host "$HOST"
  log "Done."
fi

echo ""
log "Run 'beacon doctor verify-install' to confirm all surfaces are healthy."
