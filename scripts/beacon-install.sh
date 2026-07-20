#!/usr/bin/env bash
# =============================================================================
# beacon-install.sh — Idempotent Scheme A host skill installer
# =============================================================================
# Usage:
#   bash scripts/beacon-install.sh               # install for all hosts
#   bash scripts/beacon-install.sh agents        # install for one host
#   DRY_RUN=true bash scripts/beacon-install.sh  # preview only
#   INSTALL_ALL=1 bash scripts/beacon-install.sh # legacy full package surface
#
# Scheme A (default):
#   Creates flat symlinks: ~/.<host>/skills/beacon-{goal,plan,...}
#   Removes package root ~/.<host>/skills/beacon (recursive discovery leak).
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SOURCE="$REPO_ROOT/skills/beacon"
DRY_RUN="${DRY_RUN:-false}"
INSTALL_ALL="${INSTALL_ALL:-0}"

WHITELIST_BEACON=(
  beacon-goal beacon-plan beacon-truth beacon-design beacon-implement beacon-qa beacon-release
)
HOSTS=(agents codex cursor trae windsurf opencode pi qoder trellis reasonix)

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
  local package_target="$target_base/beacon"

  log "Host: .$host -> $target_base"
  mkdir -p "$target_base"

  if [[ "$INSTALL_ALL" == "1" ]]; then
    if [[ -d "$package_target" && ! -L "$package_target" ]]; then
      warn "$package_target is a REAL directory (not a symlink)."
      warn "  rm -rf $package_target && bash scripts/beacon-install.sh $host"
      return 1
    fi
    if [[ "$DRY_RUN" == "true" ]]; then
      info "[DRY RUN] ln -sfn $SKILLS_SOURCE $package_target"
      return 0
    fi
    ln -sfn "$SKILLS_SOURCE" "$package_target"
    info "Linked package: $package_target -> $SKILLS_SOURCE"
    return 0
  fi

  # Scheme A: remove package root
  if [[ -L "$package_target" || -e "$package_target" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      info "[DRY RUN] rm package root $package_target"
    else
      rm -rf "$package_target"
      info "Removed package root: $package_target"
    fi
  fi

  for skill in "${WHITELIST_BEACON[@]}"; do
    local src="$SKILLS_SOURCE/$skill"
    local dst="$target_base/$skill"
    [[ -d "$src" ]] || { warn "missing $src"; continue; }
    if [[ "$DRY_RUN" == "true" ]]; then
      info "[DRY RUN] ln -sfn $src $dst"
      continue
    fi
    if [[ -e "$dst" && ! -L "$dst" ]]; then
      warn "$dst exists and is not a symlink; skip"
      continue
    fi
    ln -sfn "$src" "$dst"
    info "Linked: $dst -> $src"
  done
}

check_prereqs

HOST="${1:-all}"

if [[ "$HOST" == "all" ]]; then
  failed=0
  for h in "${HOSTS[@]}"; do
    install_host "$h" || ((failed++)) || true
  done
  echo ""
  log "Done. $((${#HOSTS[@]} - failed))/${#HOSTS[@]} hosts installed (Scheme A flat 1+6)."
  [[ $failed -eq 0 ]] || warn "$failed host(s) had warnings — review above."
else
  install_host "$HOST"
  log "Done."
fi

echo ""
log "Verify: find ~/.agents/skills -maxdepth 1 \\( -name 'beacon*' -o -name 'loom*' \\) | sort"
log "Expected package roots absent: ~/.agents/skills/beacon and ~/.agents/skills/loom"
