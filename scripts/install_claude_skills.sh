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

# List of host-visible beacon sub-skills to install
BEACON_SUBSKILLS=(
    "beacon-archive"
    "beacon-brainstorm"
    "beacon-ceo-review"
    "beacon-change"
    "beacon-change-refreeze"
    "beacon-deep"
    "beacon-design-review"
    "beacon-doctor"
    "beacon-friction-intake"
    "beacon-help"
    "beacon-implement"
    "beacon-learn"
    "beacon-prd"
    "beacon-prd-bootstrap"
    "beacon-prototype"
    "beacon-qa"
    "beacon-real-project-validation"
    "beacon-release"
    "beacon-status"
    "beacon-test-case"
    "beacon-toolkit-branch-governance"
    "beacon-toolkit-lighthouse"
    "beacon-toolkit-metadata"
    "beacon-user-story"
    "using-beacon"
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

# Install all sub-skills as flat symlinks
echo ""
echo "Installing beacon sub-skills..."
for skill in "${BEACON_SUBSKILLS[@]}"; do
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
