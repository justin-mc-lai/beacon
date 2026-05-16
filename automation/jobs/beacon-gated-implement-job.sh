#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
WORKSPACE_MODE="worktree"
MODE="team"
RUNNER="codex-subagents"
RUNTIME="file"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/implement"
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
    --workspace-mode)
      WORKSPACE_MODE="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --runner)
      RUNNER="$2"
      shift 2
      ;;
    --runtime)
      RUNTIME="$2"
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

if [[ "${WORKSPACE_MODE}" != "worktree" && "${WORKSPACE_MODE}" != "local" ]]; then
  echo "Unsupported workspace mode: ${WORKSPACE_MODE}" >&2
  exit 2
fi

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
    if job.get("job_kind") != "implement":
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
  echo "No enabled implement features found in ${QUEUE_PATH}; gated implement window closed, skipping." >&2
  exit 0
fi

IMPLEMENT_STATUS=0
for feature in "${FEATURES[@]}"; do
  SAFE_NAME="$(printf '%s' "${feature}" | tr ' /' '__')"
  OUT_FILE="${OUTPUT_DIR}/implement-${SAFE_NAME}-${TIMESTAMP}.txt"
  set +e
  {
    echo "job=beacon-gated-implement-job"
    echo "timestamp=${TIMESTAMP}"
    echo "project_root=${PROJECT_ROOT}"
    echo "feature=${feature}"
    echo "host_runtime=${HOST_RUNTIME}"
    echo "workspace_mode=${WORKSPACE_MODE}"
    echo "mode=${MODE}"
    echo "runner=${RUNNER}"
    echo "runtime=${RUNTIME}"
    echo "beacon_bin=${BEACON_BIN}"
    echo
    "${BEACON_BIN}" implement run "${feature}" \
      --project "${PROJECT_ROOT}" \
      --version "${VERSION}" \
      --host-runtime "${HOST_RUNTIME}" \
      --mode "${MODE}" \
      --runner "${RUNNER}" \
      --runtime "${RUNTIME}" \
      --auto-switch-branch \
      --auto-review-spec \
      --auto-qa \
      --auto-qa-arg "--host-runtime" \
      --auto-qa-arg "${HOST_RUNTIME}"
  } | tee "${OUT_FILE}"
  FEATURE_STATUS=${PIPESTATUS[0]}
  set -e
  if [[ "${FEATURE_STATUS}" != "0" ]]; then
    IMPLEMENT_STATUS="${FEATURE_STATUS}"
  fi
done

LEDGER_ARTIFACT_PATH="${OUTPUT_DIR}/qa-feedback-ledger-${TIMESTAMP}.json"
CANONICAL_LEDGER_PATH="${PROJECT_ROOT}/.beacon/automation/qa-feedback-ledger.json"
QUEUE_UPDATE_ARTIFACT_PATH="${OUTPUT_DIR}/queue-update-${TIMESTAMP}.json"
SUMMARY_PATH="${OUTPUT_DIR}/implement-summary-${TIMESTAMP}.json"
SUMMARY_STATUS="passed"
if [[ "${IMPLEMENT_STATUS}" != "0" ]]; then
  SUMMARY_STATUS="blocked"
fi
SUMMARY_FEATURE_ARGS=()
for feature in "${FEATURES[@]}"; do
  SUMMARY_FEATURE_ARGS+=(--feature "${feature}")
done

"${BEACON_BIN}" automation summarize-qa \
  --project-root "${PROJECT_ROOT}" \
  "${SUMMARY_FEATURE_ARGS[@]}" \
  --json > "${LEDGER_ARTIFACT_PATH}"
mkdir -p "$(dirname "${CANONICAL_LEDGER_PATH}")"
cp "${LEDGER_ARTIFACT_PATH}" "${CANONICAL_LEDGER_PATH}"

"${BEACON_BIN}" automation update-queue \
  --project-root "${PROJECT_ROOT}" \
  --queue "${QUEUE_PATH}" \
  --json > "${QUEUE_UPDATE_ARTIFACT_PATH}"

"${BEACON_BIN}" automation build-summary \
  --project-root "${PROJECT_ROOT}" \
  --summary-kind functional \
  --job beacon-gated-implement \
  --layer implement-qa \
  --status "${SUMMARY_STATUS}" \
  --ledger-path "${LEDGER_ARTIFACT_PATH}" \
  --queue-update-path "${QUEUE_UPDATE_ARTIFACT_PATH}" \
  "${SUMMARY_FEATURE_ARGS[@]}" \
  --artifact qa_feedback_ledger="${LEDGER_ARTIFACT_PATH}" \
  --artifact queue_update="${QUEUE_UPDATE_ARTIFACT_PATH}" \
  --artifact queue="${QUEUE_PATH}" \
  > "${SUMMARY_PATH}"

echo "wrote ${SUMMARY_PATH}"
exit "${IMPLEMENT_STATUS}"
