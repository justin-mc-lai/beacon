#!/usr/bin/env bash

set -uo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_iteration_governance.sh <quick|delivery|full> [--project-root PATH] [--version VERSION]

Modes:
  quick     Run docs/current-contract convergence checks
  delivery  Run delivery/release verification checks
  full      Run quick + delivery

Options:
  --project-root PATH   Target Beacon repository root. Defaults to the repository containing this script.
  --version VERSION     Release line to validate. Defaults to auto.
  -h, --help            Show help
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

MODE=""
PROJECT_ROOT=""
VERSION="auto"

while [[ $# -gt 0 ]]; do
  case "$1" in
    quick|delivery|full)
      MODE="$1"
      shift
      ;;
    --project-root|--repo-root)
      PROJECT_ROOT="${2:-}"
      shift 2
      ;;
    --version)
      VERSION="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${MODE}" ]]; then
  usage >&2
  exit 2
fi

if [[ -z "${PROJECT_ROOT}" ]]; then
  PROJECT_ROOT="${DEFAULT_PROJECT_ROOT}"
fi

PROJECT_ROOT="$(cd "${PROJECT_ROOT}" && pwd)"
RUN_ID="iter-gov-$(date +%Y%m%d%H%M%S)"
REPORT_DIR="${PROJECT_ROOT}/.beacon/iteration-governance/${RUN_ID}"
LATEST_PATH="${PROJECT_ROOT}/.beacon/iteration-governance/latest.json"
STEPS_TSV="${REPORT_DIR}/steps.tsv"
OVERALL_EXIT=0

mkdir -p "${REPORT_DIR}"
: > "${STEPS_TSV}"

record_step() {
  local step_name="$1"
  local status="$2"
  local log_rel="$3"
  local rendered_cmd="$4"
  printf '%s\t%s\t%s\t%s\n' "${step_name}" "${status}" "${log_rel}" "${rendered_cmd}" >> "${STEPS_TSV}"
}

run_step() {
  local step_name="$1"
  shift
  local log_file="${REPORT_DIR}/${step_name}.log"
  local log_rel="${log_file#${PROJECT_ROOT}/}"
  local rendered_cmd=""
  printf -v rendered_cmd '%q ' "$@"
  rendered_cmd="${rendered_cmd% }"

  if (
    cd "${PROJECT_ROOT}" &&
    "$@"
  ) >"${log_file}" 2>&1; then
    record_step "${step_name}" "passed" "${log_rel}" "${rendered_cmd}"
    return 0
  fi

  OVERALL_EXIT=1
  record_step "${step_name}" "failed" "${log_rel}" "${rendered_cmd}"
  return 1
}

run_quick() {
  run_step docs-current-contract \
    python3 -m pytest -q \
    tests/test_docs_current_contract.py \
    tests/test_skill_standard_layout.py \
    tests/test_skill_command_alignment.py

  run_step docs-material-audit \
    python3 -m beacon.main doctor verify-materials \
    --project-root "${PROJECT_ROOT}" \
    --version "${VERSION}" \
    --json
}

run_delivery() {
  run_step delivery-audit \
    python3 -m beacon.main doctor verify-delivery \
    --project-root "${PROJECT_ROOT}" \
    --version "${VERSION}" \
    --json

  run_step release-gate \
    python3 -m beacon.main gate check release \
    --project-root "${PROJECT_ROOT}" \
    --version "${VERSION}" \
    --json

  run_step release-readiness \
    python3 -m beacon.main release check "${VERSION}" \
    --project "${PROJECT_ROOT}"
}

case "${MODE}" in
  quick)
    run_quick
    ;;
  delivery)
    run_delivery
    ;;
  full)
    run_quick
    run_delivery
    ;;
esac

python3 - "${REPORT_DIR}" "${PROJECT_ROOT}" "${MODE}" "${VERSION}" "${STEPS_TSV}" "${OVERALL_EXIT}" "${LATEST_PATH}" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

report_dir = Path(sys.argv[1])
project_root = Path(sys.argv[2])
mode = sys.argv[3]
version = sys.argv[4]
steps_tsv = Path(sys.argv[5])
overall_exit = int(sys.argv[6])
latest_path = Path(sys.argv[7])

steps = []
for line in steps_tsv.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    name, status, log_path, command = line.split("\t", 3)
    steps.append(
        {
            "name": name,
            "status": status,
            "log_path": log_path,
            "command": command,
        }
    )

payload = {
    "schema_version": "1.0",
    "run_id": report_dir.name,
    "mode": mode,
    "project_root": str(project_root),
    "version": version,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "status": "passed" if overall_exit == 0 else "failed",
    "steps": steps,
}

summary_json = report_dir / "summary.json"
summary_md = report_dir / "summary.md"
summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Beacon Iteration Governance Summary",
    "",
    f"- run_id: `{payload['run_id']}`",
    f"- mode: `{mode}`",
    f"- version: `{version}`",
    f"- status: `{payload['status']}`",
    "",
    "## Steps",
]
for step in steps:
    lines.append(f"- `{step['status']}` `{step['name']}` -> `{step['log_path']}`")
summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

latest_path.parent.mkdir(parents=True, exist_ok=True)
latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps(payload, ensure_ascii=False, indent=2))
PY

exit "${OVERALL_EXIT}"
