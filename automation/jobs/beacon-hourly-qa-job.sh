#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/hourly-qa"
BEACON_BIN="beacon"

ENV_FILE="${ROOT_DIR}/automation/.env"
NOTIFY_HELPER="${ROOT_DIR}/automation/jobs/beacon-notify-feishu-post.py"
FEISHU_WEBHOOK=""
FEISHU_SECRET=""

load_notification_env() {
  if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    set +a
  fi
  FEISHU_WEBHOOK="${AUTOMATION_FEISHU_WEBHOOK:-}"
  FEISHU_SECRET="${AUTOMATION_FEISHU_SECRET:-}"
}

record_notification_status() {
  local summary_path="$1"
  local status="$2"
  python3 - "${summary_path}" "${status}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
artifacts["feishu_status"] = sys.argv[2]
payload["artifacts"] = artifacts
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

summary_status() {
  python3 - "$1" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(payload.get("status") or "").strip())
PY
}

send_summary_notification() {
  local summary_path="$1"
  local title_prefix="$2"
  load_notification_env
  if [[ -n "${FEISHU_WEBHOOK}" && -x "${NOTIFY_HELPER}" ]]; then
    local notify_status
    notify_status="$(summary_status "${summary_path}")"
    if python3 "${NOTIFY_HELPER}" \
      --webhook "${FEISHU_WEBHOOK}" \
      --secret "${FEISHU_SECRET}" \
      --title "${title_prefix} ${notify_status:-update}" \
      --summary-path "${summary_path}"; then
      record_notification_status "${summary_path}" sent
    else
      record_notification_status "${summary_path}" failed
    fi
  else
    record_notification_status "${summary_path}" skipped
  fi
}


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
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

LOCK_DIR="${PROJECT_ROOT}/.beacon/automation-runs/qa-global.lock"
LOCK_PID_FILE="${LOCK_DIR}/pid"
LOCK_ACQUIRED=0

cleanup_lock() {
  if [[ "${LOCK_ACQUIRED}" = "1" ]]; then
    rm -rf "${LOCK_DIR}"
  fi
}

acquire_lock() {
  mkdir -p "$(dirname "${LOCK_DIR}")"
  if mkdir "${LOCK_DIR}" 2>/dev/null; then
    LOCK_ACQUIRED=1
    printf '%s\n' "$$" > "${LOCK_PID_FILE}"
    trap cleanup_lock EXIT INT TERM
    return 0
  fi
  if [[ -f "${LOCK_PID_FILE}" ]]; then
    EXISTING_PID="$(cat "${LOCK_PID_FILE}" 2>/dev/null || true)"
    if [[ "${EXISTING_PID}" =~ ^[0-9]+$ ]] && kill -0 "${EXISTING_PID}" 2>/dev/null; then
      echo "Another Beacon QA automation job is already running (pid=${EXISTING_PID}); skipping hourly QA." >&2
      exit 0
    fi
  fi
  echo "Removing stale Beacon QA automation lock: ${LOCK_DIR}" >&2
  rm -rf "${LOCK_DIR}"
  if mkdir "${LOCK_DIR}" 2>/dev/null; then
    LOCK_ACQUIRED=1
    printf '%s\n' "$$" > "${LOCK_PID_FILE}"
    trap cleanup_lock EXIT INT TERM
    return 0
  fi
  echo "Another Beacon QA automation job acquired the lock first; skipping hourly QA." >&2
  exit 0
}

acquire_lock

mkdir -p "${OUTPUT_DIR}"
TIMESTAMP="$(date '+%Y%m%dT%H%M%S')"
LEDGER_ARTIFACT_PATH="${OUTPUT_DIR}/qa-feedback-ledger-${TIMESTAMP}.json"
CANONICAL_LEDGER_PATH="${PROJECT_ROOT}/.beacon/automation/qa-feedback-ledger.json"
QUEUE_UPDATE_ARTIFACT_PATH="${OUTPUT_DIR}/queue-update-${TIMESTAMP}.json"
SUMMARY_PATH="${OUTPUT_DIR}/qa-summary-${TIMESTAMP}.json"

FEATURE_LIST="$(
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
)"

if [[ -z "${FEATURE_LIST}" ]]; then
  "${BEACON_BIN}" automation build-summary \
    --project-root "${PROJECT_ROOT}" \
    --summary-kind hourly \
    --job beacon-hourly-qa \
    --layer qa \
    --status skipped \
    --artifact queue="${QUEUE_PATH}" \
    > "${SUMMARY_PATH}"
  send_summary_notification "${SUMMARY_PATH}" "Beacon hourly QA"
  echo "No enabled QA features found in ${QUEUE_PATH}; hourly QA window closed, skipping." >&2
  echo "wrote ${SUMMARY_PATH}"
  exit 0
fi

while IFS= read -r feature; do
  [[ -n "${feature}" ]] || continue
  SAFE_NAME="$(printf '%s' "${feature}" | tr ' /' '__')"
  OUT_FILE="${OUTPUT_DIR}/qa-${SAFE_NAME}-${TIMESTAMP}.txt"
  {
    echo "job=beacon-hourly-qa-job"
    echo "timestamp=${TIMESTAMP}"
    echo "project_root=${PROJECT_ROOT}"
    echo "feature=${feature}"
    echo "version=${VERSION}"
    echo "host_runtime=${HOST_RUNTIME}"
    echo "beacon_bin=${BEACON_BIN}"
    echo
    "${BEACON_BIN}" qa run "${feature}" \
      --project-root "${PROJECT_ROOT}" \
      --version "${VERSION}" \
      --host-runtime "${HOST_RUNTIME}"
  } | tee "${OUT_FILE}"
done <<< "${FEATURE_LIST}"

"${BEACON_BIN}" automation summarize-qa \
  --project-root "${PROJECT_ROOT}" \
  --json > "${LEDGER_ARTIFACT_PATH}"

mkdir -p "$(dirname "${CANONICAL_LEDGER_PATH}")"
cp "${LEDGER_ARTIFACT_PATH}" "${CANONICAL_LEDGER_PATH}"

"${BEACON_BIN}" automation update-queue \
  --project-root "${PROJECT_ROOT}" \
  --queue "${QUEUE_PATH}" \
  --json > "${QUEUE_UPDATE_ARTIFACT_PATH}"

"${BEACON_BIN}" automation build-summary \
  --project-root "${PROJECT_ROOT}" \
  --summary-kind hourly \
  --job beacon-hourly-qa \
  --layer qa \
  --ledger-path "${LEDGER_ARTIFACT_PATH}" \
  --queue-update-path "${QUEUE_UPDATE_ARTIFACT_PATH}" \
  --artifact qa_feedback_ledger="${LEDGER_ARTIFACT_PATH}" \
  --artifact queue_update="${QUEUE_UPDATE_ARTIFACT_PATH}" \
  --artifact queue="${QUEUE_PATH}" \
  > "${SUMMARY_PATH}"

send_summary_notification "${SUMMARY_PATH}" "Beacon hourly QA"

echo "wrote ${SUMMARY_PATH}"
