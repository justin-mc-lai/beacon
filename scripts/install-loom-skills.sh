#!/usr/bin/env bash
# =============================================================================
# install-loom-skills.sh — Install only skills/loom for dual-track hosts
# =============================================================================
# Backend for Loom evolution track is the Rust CLI (beacon-v2 / loom), NOT the
# Python loom-py facade. This script only installs skill packages.
#
# Scheme A (default): flat 1+6 only. No package root ~/.HOST/skills/loom that
# recursively exposes progressive/internal skills to host discovery.
#
# Usage:
#   bash scripts/install-loom-skills.sh              # all known hosts
#   bash scripts/install-loom-skills.sh agents       # Codex ~/.agents/skills flat
#   bash scripts/install-loom-skills.sh claude       # flat ~/.claude/skills/loom-*
#   INSTALL_ALL=1 bash scripts/install-loom-skills.sh
#   DRY_RUN=true bash scripts/install-loom-skills.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SOURCE="$REPO_ROOT/skills/loom"
DRY_RUN="${DRY_RUN:-false}"

WHITELIST_LOOM=(
  loom-goal loom-plan loom-truth loom-design loom-implement loom-qa loom-release
)
INSTALL_ALL="${INSTALL_ALL:-0}"

log()  { echo "[install-loom-skills] $*"; }
warn() { echo "[install-loom-skills] WARN $*" >&2; }
fail() { echo "[install-loom-skills] FAIL $*" >&2; exit 1; }

[[ -d "$SKILLS_SOURCE" ]] || fail "missing $SKILLS_SOURCE"
[[ -f "$SKILLS_SOURCE/SKILL.md" ]] || fail "missing $SKILLS_SOURCE/SKILL.md"

install_flat_host() {
  # hosts that previously used package trees — now Scheme A flat whitelist
  local host="$1"
  local target_base="$HOME/.$host/skills"
  local package_target="$target_base/loom"
  mkdir -p "$target_base"

  if [[ "$INSTALL_ALL" == "1" ]]; then
    if [[ -d "$package_target" && ! -L "$package_target" ]]; then
      warn "$package_target is a real directory; skip"
      return 1
    fi
    if [[ "$DRY_RUN" == "true" ]]; then
      log "DRY_RUN would link $package_target -> $SKILLS_SOURCE"
      return 0
    fi
    [[ -L "$package_target" ]] && rm "$package_target"
    ln -sfn "$SKILLS_SOURCE" "$package_target"
    log "OK package $package_target -> $SKILLS_SOURCE"
    return 0
  fi

  # Scheme A: remove package root leak
  if [[ -L "$package_target" || -e "$package_target" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      log "DRY_RUN would remove package root $package_target"
    else
      rm -rf "$package_target"
      log "OK removed package root $package_target"
    fi
  fi

  for skill in "${WHITELIST_LOOM[@]}"; do
    local src="$SKILLS_SOURCE/$skill"
    local dst="$target_base/$skill"
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
  done
}

install_claude_flat() {
  local claude_dir="$HOME/.claude/skills"
  mkdir -p "$claude_dir"
  local pkg="$claude_dir/loom"

  if [[ "$INSTALL_ALL" == "1" ]]; then
    if [[ "$DRY_RUN" == "true" ]]; then
      log "DRY_RUN would link $pkg -> $REPO_ROOT"
    else
      [[ -L "$pkg" || -e "$pkg" ]] && rm -rf "$pkg"
      ln -sfn "$REPO_ROOT" "$pkg"
      log "OK $pkg -> $REPO_ROOT"
    fi
  else
    if [[ -L "$pkg" || -e "$pkg" ]]; then
      if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY_RUN would remove package root $pkg"
      else
        rm -rf "$pkg"
        log "OK removed package root $pkg"
      fi
    fi
  fi

  # remove stale loom-* outside whitelist when Scheme A
  if [[ "$INSTALL_ALL" != "1" && "$DRY_RUN" != "true" ]]; then
    for existing in "$claude_dir"/loom-*; do
      [[ -e "$existing" ]] || continue
      base="$(basename "$existing")"
      keep=0
      for w in "${WHITELIST_LOOM[@]}"; do
        if [[ "$base" == "$w" ]]; then keep=1; break; fi
      done
      if [[ "$keep" != "1" && -L "$existing" ]]; then
        rm "$existing"
        log "OK removed stale $base"
      fi
    done
  fi

  while IFS= read -r skill; do
    local src="$SKILLS_SOURCE/$skill"
    local dst="$claude_dir/$skill"
    [[ -d "$src" ]] || continue
    if [[ "$INSTALL_ALL" != "1" ]]; then
      local ok=0
      for w in "${WHITELIST_LOOM[@]}"; do
        if [[ "$skill" == "$w" ]]; then ok=1; break; fi
      done
      if [[ "$ok" != "1" ]]; then
        continue
      fi
    fi
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
  log "INSTALL_ALL=${INSTALL_ALL} scheme_a=$([ "$INSTALL_ALL" = "1" ] && echo no || echo yes)"

  if [[ "$arg" == "all" ]]; then
    for h in "${HOSTS[@]}"; do
      install_flat_host "$h" || true
    done
    install_claude_flat
  elif [[ "$arg" == "claude" ]]; then
    install_claude_flat
  else
    install_flat_host "$arg"
  fi
  log "Done. Public entry: \$loom-goal → Rust CLI loom / beacon-v2"
}

main "$@"
