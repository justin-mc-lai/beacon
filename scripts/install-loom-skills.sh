#!/usr/bin/env bash
# =============================================================================
# install-loom-skills.sh — Install only skills/loom for dual-track hosts
# =============================================================================
# Backend for Loom evolution track is the Rust CLI (beacon-v2 / loom), NOT the
# Python loom-py facade. This script only installs skill packages.
#
# Usage:
#   bash scripts/install-loom-skills.sh              # all known hosts
#   bash scripts/install-loom-skills.sh agents       # Codex ~/.agents/skills
#   bash scripts/install-loom-skills.sh claude       # flat ~/.claude/skills/loom-*
#   DRY_RUN=true bash scripts/install-loom-skills.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SOURCE="$REPO_ROOT/skills/loom"
DRY_RUN="${DRY_RUN:-false}"

log()  { echo "[install-loom-skills] $*"; }
warn() { echo "[install-loom-skills] WARN $*" >&2; }
fail() { echo "[install-loom-skills] FAIL $*" >&2; exit 1; }

[[ -d "$SKILLS_SOURCE" ]] || fail "missing $SKILLS_SOURCE"
[[ -f "$SKILLS_SOURCE/SKILL.md" ]] || fail "missing $SKILLS_SOURCE/SKILL.md"

install_package_host() {
  # hosts that discover package trees: ~/.HOST/skills/loom -> skills/loom
  local host="$1"
  local target_base="$HOME/.$host/skills"
  local target="$target_base/loom"
  mkdir -p "$target_base"
  if [[ -d "$target" && ! -L "$target" ]]; then
    warn "$target is a real directory; skip (remove manually to replace)"
    return 1
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "DRY_RUN would link $target -> $SKILLS_SOURCE"
    return 0
  fi
  if [[ -L "$target" ]]; then
    rm "$target"
  fi
  ln -sfn "$SKILLS_SOURCE" "$target"
  log "OK $target -> $SKILLS_SOURCE"
}

install_claude_flat() {
  # Claude Code: first-level skills only
  local claude_dir="$HOME/.claude/skills"
  mkdir -p "$claude_dir"
  # package root
  local pkg="$claude_dir/loom"
  if [[ "$DRY_RUN" == "true" ]]; then
    log "DRY_RUN would link $pkg -> $REPO_ROOT (or skills/loom tree)"
  else
    if [[ -L "$pkg" ]]; then rm "$pkg"; fi
    # Point at repo so skills/loom/* is reachable like beacon installer
    ln -sfn "$REPO_ROOT" "$pkg"
    log "OK $pkg -> $REPO_ROOT"
  fi
  # flat loom-* subskills
  while IFS= read -r skill; do
    local src="$SKILLS_SOURCE/$skill"
    local dst="$claude_dir/$skill"
    [[ -d "$src" ]] || continue
    if [[ "$DRY_RUN" == "true" ]]; then
      log "DRY_RUN would link $dst -> $src"
      continue
    fi
    if [[ -e "$dst" && ! -L "$dst" ]]; then
      warn "$dst exists and is not a symlink; skip"
      continue
    fi
    [[ -L "$dst" ]] && rm "$dst"
    ln -sfn "$src" "$dst"
    log "OK $dst -> $src"
  done < <(
    find "$SKILLS_SOURCE" -mindepth 2 -maxdepth 2 -name "SKILL.md" -print \
      | sed "s#${SKILLS_SOURCE}/##; s#/SKILL.md##" \
      | sort
  )
}

HOSTS=(agents codex cursor trae windsurf opencode pi qoder trellis reasonix)

main() {
  local arg="${1:-all}"
  log "source=$SKILLS_SOURCE"
  log "Rust backend: install via scripts/install-loom-cli.sh (beacon-v2 + loom)"
  log "Python loom-py is optional debug only — not the Loom product CLI"

  if [[ "$arg" == "all" ]]; then
    for h in "${HOSTS[@]}"; do
      install_package_host "$h" || true
    done
    install_claude_flat
  elif [[ "$arg" == "claude" ]]; then
    install_claude_flat
  else
    install_package_host "$arg"
  fi
  log "Done. Public entry: \$loom-goal (skills/loom/loom-goal) → Rust CLI loom / beacon-v2"
}

main "$@"
