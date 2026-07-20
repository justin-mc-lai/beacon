#!/bin/bash
# Install the latest Beacon CLI and sync host-visible skills across supported agents.
# Scheme A default: flat 1+6 for Codex (~/.agents/skills) and Claude; no package-root leak.

set -euo pipefail

BEACON_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_CLI_VERSION="$(
BEACON_ROOT="${BEACON_ROOT}" python3 - <<'PY'
import json
import os
from pathlib import Path

truth_path = Path(os.environ["BEACON_ROOT"]) / "beacon" / "version-truth.json"
truth = json.loads(truth_path.read_text())
print(truth["current_runtime_release_line"])
PY
)"
CLI_VERSION="${1:-${DEFAULT_CLI_VERSION}}"
INSTALL_ALL="${INSTALL_ALL:-0}"

echo "=== Beacon Unified Installer ==="
echo "Beacon root: ${BEACON_ROOT}"
echo "Target docs/runtime line: ${CLI_VERSION}"
echo "INSTALL_ALL=${INSTALL_ALL}"
echo

echo "[1/6] Installing Beacon CLI"
python3 -m pip install -e "${BEACON_ROOT}[dev]" --upgrade
echo

echo "[2/6] Syncing global Codex/agents skill root (Scheme A flat 1+6)"
mkdir -p "${HOME}/.agents/skills"
rm -rf "${HOME}/.codex/skills/beacon"
rm -f "${HOME}/.codex/skills/beacon.bak-"*
# Prefer Python installer (handles package-root removal + loom dual-track)
python3 - <<PY
from beacon.utils.agent_surface import (
    install_global_agents_beacon_skills,
    verify_global_agents_beacon_skills,
)
print(install_global_agents_beacon_skills(beacon_root="${BEACON_ROOT}", dry_run=False))
print(verify_global_agents_beacon_skills())
PY
echo

echo "[3/6] Syncing global Claude Code skill roots"
INSTALL_ALL="${INSTALL_ALL}" "${BEACON_ROOT}/scripts/install_claude_skills.sh"
echo

echo "[4/6] Syncing Loom dual-track host skills (Scheme A flat)"
INSTALL_ALL="${INSTALL_ALL}" bash "${BEACON_ROOT}/scripts/install-loom-skills.sh" || true
echo

echo "[5/6] Materializing project-local agent surfaces"
for agent in codex claude trae cursor windsurf; do
    echo "  setup-agent-surface: ${agent}"
    python3 -m beacon.main doctor setup-agent-surface \
        --project-root "${BEACON_ROOT}" \
        --version "${CLI_VERSION}" \
        --agent "${agent}" \
        --force
done
echo

echo "[6/6] Verifying agent surfaces"
for agent in codex claude trae cursor windsurf; do
    echo "  verify-agent-surface: ${agent}"
    python3 -m beacon.main doctor verify-agent-surface \
        --project-root "${BEACON_ROOT}" \
        --version "${CLI_VERSION}" \
        --agent "${agent}" \
        --strict
done
echo

echo "=== Unified install complete ==="
echo "CLI:"
beacon --version || true
echo
echo "Global Codex/agents flat surface:"
find "${HOME}/.agents/skills" -maxdepth 1 \( -name 'beacon*' -o -name 'loom*' \) | sort
echo
echo "Global Claude flat surface:"
find "${HOME}/.claude/skills" -maxdepth 1 \( -name 'beacon*' -o -name 'loom*' \) 2>/dev/null | sort || true
