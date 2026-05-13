#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/qa"
BEACON_BIN="${ROOT_DIR}/beacon-cli"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --queue)
      QUEUE_PATH="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --host-runtime)
      HOST_RUNTIME="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --beacon-bin)
      BEACON_BIN="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

mkdir -p "${OUTPUT_DIR}"
TIMESTAMP="$(date '+%Y%m%dT%H%M%S')"

mapfile -t FEATURES < <(
  python3 - "${QUEUE_PATH}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for job in payload.get("jobs", []):
    if not job.get("enabled"):
        continue
    if job.get("job_kind") != "qa":
        continue
    selector = job.get("feature_selector") or {}
    if isinstance(selector, dict) and selector.get("mode") == "explicit_list":
        for feature in selector.get("features", []):
            text = str(feature or "").strip()
            if text:
                print(text)
PY
)

if [[ ${#FEATURES[@]} -eq 0 ]]; then
  echo "No enabled QA features found in ${QUEUE_PATH}" >&2
  exit 1
fi

for feature in "${FEATURES[@]}"; do
  SAFE_NAME="$(printf '%s' "${feature}" | tr ' /' '__')"
  OUT_FILE="${OUTPUT_DIR}/qa-${SAFE_NAME}-${TIMESTAMP}.txt"
  {
    echo "job=beacon-qa-job"
    echo "timestamp=${TIMESTAMP}"
    echo "project_root=${PROJECT_ROOT}"
    echo "feature=${feature}"
    echo "host_runtime=${HOST_RUNTIME}"
    echo "beacon_bin=${BEACON_BIN}"
    echo
    "${BEACON_BIN}" qa run "${feature}" \
      --project-root "${PROJECT_ROOT}" \
      --version "${VERSION}" \
      --host-runtime "${HOST_RUNTIME}"
  } | tee "${OUT_FILE}"
done
