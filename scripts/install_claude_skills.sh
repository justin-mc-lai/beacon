#!/bin/bash
# Install Beacon skills for Claude Code with flat structure
# Claude Code only discovers skills in the first level of ~/.claude/skills/

set -e

BEACON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT_SOURCE="${BEACON_ROOT}"
SKILLS_SOURCE="${BEACON_ROOT}/skills/beacon"
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

echo "=== Beacon Skills Installer for Claude Code ==="
echo "Beacon root: ${BEACON_ROOT}"
echo "Repo root source: ${REPO_ROOT_SOURCE}"
echo "Skills source: ${SKILLS_SOURCE}"
echo "Claude skills dir: ${CLAUDE_SKILLS_DIR}"
echo ""

# Create Claude skills directory if it doesn't exist
mkdir -p "${CLAUDE_SKILLS_DIR}"

BEACON_SUBSKILLS=()
while IFS= read -r skill; do
    BEACON_SUBSKILLS+=("${skill}")
done < <(
    find "${SKILLS_SOURCE}" -mindepth 2 -maxdepth 2 -name "SKILL.md" -print \
        | sed "s#${SKILLS_SOURCE}/##; s#/SKILL.md##" \
        | sort
)

# Install main beacon skill as repo root so Claude can scan
# ~/.claude/skills/beacon/SKILL.md and packaged tree under skills/beacon/
echo "Installing main beacon skill..."
if [ -L "${CLAUDE_SKILLS_DIR}/beacon" ]; then
    echo "  Removing existing beacon symlink"
    rm "${CLAUDE_SKILLS_DIR}/beacon"
fi
ln -sf "${REPO_ROOT_SOURCE}" "${CLAUDE_SKILLS_DIR}/beacon"
echo "  ✓ beacon -> ${REPO_ROOT_SOURCE}"

# Scheme A: default host-visible whitelist (INSTALL_ALL=1 installs every sub-skill)
WHITELIST_BEACON=(
  beacon-goal beacon-plan beacon-truth beacon-design beacon-implement beacon-qa beacon-release
)
INSTALL_ALL="${INSTALL_ALL:-0}"

# Install sub-skills as flat symlinks
echo ""
if [[ "${INSTALL_ALL}" == "1" ]]; then
  echo "Installing ALL beacon sub-skills (INSTALL_ALL=1)..."
else
  echo "Installing Scheme A whitelist (1+6 public surface)..."
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
        echo "  Updating ${skill}"
        rm "${target}"
    elif [ -e "${target}" ]; then
        echo "  ⚠ Warning: ${skill} exists but is not a symlink, skipping"
        continue
    fi

    ln -sf "${source}" "${target}"
    echo "  ✓ ${skill}"
done

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Installed skills:"
ls -1 "${CLAUDE_SKILLS_DIR}" | grep "^beacon" | grep -v "backup" | sort

echo ""
echo "Next steps:"
echo "1. Restart Claude Code (quit and relaunch)"
echo "2. Verify skills are available with: ls -la ~/.claude/skills/beacon*"
echo "3. Test with: /beacon-help or /beacon-status"
echo ""
echo "To verify installation:"
echo "  find ~/.claude/skills -maxdepth 1 -name 'beacon*' -type l"
