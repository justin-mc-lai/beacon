#!/bin/bash
# Install the latest Beacon CLI and sync host-visible skills across supported agents.

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

echo "=== Beacon Unified Installer ==="
echo "Beacon root: ${BEACON_ROOT}"
echo "Target docs/runtime line: ${CLI_VERSION}"
echo

echo "[1/5] Installing Beacon CLI"
python3 -m pip install -e "${BEACON_ROOT}[dev]" --upgrade
echo

echo "[2/5] Syncing global Codex skill root"
mkdir -p "${HOME}/.agents/skills"
rm -rf "${HOME}/.codex/skills/beacon"
rm -f "${HOME}/.codex/skills/beacon.bak-"*
ln -sfn "${BEACON_ROOT}/skills/beacon" "${HOME}/.agents/skills/beacon"
echo "  linked ~/.agents/skills/beacon -> ${BEACON_ROOT}/skills/beacon"
echo

echo "[3/5] Syncing global Claude Code skill roots"
"${BEACON_ROOT}/scripts/install_claude_skills.sh"
echo

echo "[4/5] Materializing project-local agent surfaces"
for agent in codex claude trae cursor windsurf; do
    echo "  setup-agent-surface: ${agent}"
    python3 -m beacon.main doctor setup-agent-surface \
        --project-root "${BEACON_ROOT}" \
        --version "${CLI_VERSION}" \
        --agent "${agent}" \
        --force
done
echo

echo "[5/5] Verifying agent surfaces"
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
beacon --version
echo
echo "Global roots:"
ls -ld "${HOME}/.agents/skills/beacon" "${HOME}/.claude/skills/beacon"
