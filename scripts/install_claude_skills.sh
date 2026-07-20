#!/bin/bash
# Install Beacon skills for Claude Code with flat first-level structure.
# Claude Code discovers skills only in the first level of ~/.claude/skills/
#
# Scheme A (default): only 1+6 public surface flat links.
#   beacon-goal plan truth design implement qa release
# Does NOT install package root ~/.claude/skills/beacon (repo/package leak).
#
# INSTALL_ALL=1: install every sub-skill + package root (legacy full surface).

set -euo pipefail

BEACON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT_SOURCE="${BEACON_ROOT}"
SKILLS_SOURCE="${BEACON_ROOT}/skills/beacon"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo "=== Beacon Skills Installer for Claude Code ==="
echo "Beacon root: ${BEACON_ROOT}"
echo "Skills source: ${SKILLS_SOURCE}"
echo "Claude skills dir: ${CLAUDE_SKILLS_DIR}"
echo ""

mkdir -p "${CLAUDE_SKILLS_DIR}"

WHITELIST_BEACON=(
  beacon-goal beacon-plan beacon-truth beacon-design beacon-implement beacon-qa beacon-release
)
INSTALL_ALL="${INSTALL_ALL:-0}"

# Collect all packaged sub-skills
BEACON_SUBSKILLS=()
while IFS= read -r skill; do
    BEACON_SUBSKILLS+=("${skill}")
done < <(
    find "${SKILLS_SOURCE}" -mindepth 2 -maxdepth 2 -name "SKILL.md" -print \
        | sed "s#${SKILLS_SOURCE}/##; s#/SKILL.md##" \
        | sort
)

# Package root: only under INSTALL_ALL (recursive discovery leak otherwise)
PACKAGE_LINK="${CLAUDE_SKILLS_DIR}/beacon"
if [[ "${INSTALL_ALL}" == "1" ]]; then
  echo "INSTALL_ALL=1: installing package root + all sub-skills..."
  if [ -L "${PACKAGE_LINK}" ] || [ -e "${PACKAGE_LINK}" ]; then
    rm -rf "${PACKAGE_LINK}"
  fi
  ln -sfn "${REPO_ROOT_SOURCE}" "${PACKAGE_LINK}"
  echo "  ✓ beacon (package) -> ${REPO_ROOT_SOURCE}"
else
  echo "Scheme A: flat 1+6 only (removing package root if present)..."
  if [ -L "${PACKAGE_LINK}" ] || [ -e "${PACKAGE_LINK}" ]; then
    rm -rf "${PACKAGE_LINK}"
    echo "  ✓ removed package root ${PACKAGE_LINK}"
  fi
fi

echo ""
if [[ "${INSTALL_ALL}" == "1" ]]; then
  echo "Installing ALL beacon sub-skills..."
else
  echo "Installing Scheme A whitelist (1+6 public surface)..."
fi

# Remove stale flat beacon-* not in install set
if [[ "${INSTALL_ALL}" != "1" ]]; then
  for existing in "${CLAUDE_SKILLS_DIR}"/beacon-*; do
    [ -e "${existing}" ] || continue
    base="$(basename "${existing}")"
    keep=0
    for w in "${WHITELIST_BEACON[@]}"; do
      if [[ "${base}" == "${w}" ]]; then keep=1; break; fi
    done
    if [[ "${keep}" != "1" ]]; then
      if [ -L "${existing}" ]; then
        rm "${existing}"
        echo "  ✓ removed stale ${base}"
      fi
    fi
  done
fi

for skill in "${BEACON_SUBSKILLS[@]}"; do
  if [[ "${INSTALL_ALL}" != "1" ]]; then
    keep=0
    for w in "${WHITELIST_BEACON[@]}"; do
      if [[ "${skill}" == "${w}" ]]; then keep=1; break; fi
    done
    if [[ "${keep}" != "1" ]]; then
      continue
    fi
  fi
  target="${CLAUDE_SKILLS_DIR}/${skill}"
  source="${SKILLS_SOURCE}/${skill}"

  if [ ! -d "${source}" ]; then
    echo "  ⚠ Warning: ${skill} not found at ${source}"
    continue
  fi

  if [ -L "${target}" ]; then
    rm "${target}"
  elif [ -e "${target}" ]; then
    echo "  ⚠ Warning: ${skill} exists but is not a symlink, skipping"
    continue
  fi

  ln -sfn "${source}" "${target}"
  echo "  ✓ ${skill}"
done

echo ""
echo "=== Installation Complete ==="
echo "Installed skills:"
ls -1 "${CLAUDE_SKILLS_DIR}" | grep -E '^beacon' | grep -v backup | sort || true
echo ""
echo "Next steps:"
echo "1. Restart Claude Code"
echo "2. Verify: find ~/.claude/skills -maxdepth 1 -name 'beacon*' | sort"
echo "3. Scheme A expect only: beacon-goal plan truth design implement qa release"
