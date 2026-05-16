#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
RUNTIME="file"
MODE="team"
RUNNER="codex-subagents"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/repair-window"
BEACON_BIN="beacon"
FEATURE=""
DRY_RUN=0
ALLOW_DIRTY=0

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
    --runtime)
      RUNTIME="$2"
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
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --beacon-bin)
      BEACON_BIN="$2"
      shift 2
      ;;
    --feature)
      FEATURE="$2"
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
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
      echo "Another Beacon automation job is already running (pid=${EXISTING_PID}); skipping repair window." >&2
      exit 0
    fi
  fi
  echo "Removing stale Beacon automation lock: ${LOCK_DIR}" >&2
  rm -rf "${LOCK_DIR}"
  if mkdir "${LOCK_DIR}" 2>/dev/null; then
    LOCK_ACQUIRED=1
    printf '%s\n' "$$" > "${LOCK_PID_FILE}"
    trap cleanup_lock EXIT INT TERM
    return 0
  fi
  echo "Another Beacon automation job acquired the lock first; skipping repair window." >&2
  exit 0
}

acquire_lock

mkdir -p "${OUTPUT_DIR}"
TIMESTAMP="$(date '+%Y%m%dT%H%M%S')"
RUN_DIR="${OUTPUT_DIR}/${TIMESTAMP}"
mkdir -p "${RUN_DIR}"

FEATURE_LIST="$(
  python3 - "${QUEUE_PATH}" "${FEATURE}" <<'PY'
import json
import sys
from pathlib import Path

queue_path = Path(sys.argv[1])
requested = str(sys.argv[2] or "").strip()
payload = json.loads(queue_path.read_text(encoding="utf-8"))
features = []
for job in payload.get("jobs", []):
    if not isinstance(job, dict):
        continue
    if not job.get("enabled"):
        continue
    if job.get("job_kind") != "implement":
        continue
    selector = job.get("feature_selector") or {}
    if isinstance(selector, dict) and selector.get("mode") == "explicit_list":
        for feature in selector.get("features", []):
            text = str(feature or "").strip()
            if text:
                features.append(text)

if requested:
    features = [item for item in features if item == requested]

for feature in features:
    print(feature)
PY
)"

FEATURE_COUNT="$(printf '%s\n' "${FEATURE_LIST}" | sed '/^[[:space:]]*$/d' | wc -l | tr -d ' ')"
if [[ "${FEATURE_COUNT}" = "0" ]]; then
  SUMMARY_PATH="${RUN_DIR}/repair-window-summary.json"
  "${BEACON_BIN}" automation build-summary \
    --project-root "${PROJECT_ROOT}" \
    --summary-kind functional \
    --job beacon-repair-window \
    --layer implement-qa \
    --status skipped \
    --artifact queue="${QUEUE_PATH}" \
    > "${SUMMARY_PATH}"
  send_summary_notification "${SUMMARY_PATH}" "Beacon repair window"
  echo "No enabled implement feature found in ${QUEUE_PATH}${FEATURE:+ for ${FEATURE}}; repair window closed, skipping." >&2
  echo "wrote ${SUMMARY_PATH}"
  exit 0
fi
if [[ "${FEATURE_COUNT}" != "1" ]]; then
  echo "Repair window requires exactly one enabled implement feature; got ${FEATURE_COUNT}." >&2
  printf '%s\n' "${FEATURE_LIST}" >&2
  exit 2
fi

TARGET_FEATURE="$(printf '%s\n' "${FEATURE_LIST}" | sed '/^[[:space:]]*$/d' | head -n 1)"
SAFE_NAME="$(printf '%s' "${TARGET_FEATURE}" | tr ' /' '__')"
IMPLEMENT_OUT="${RUN_DIR}/implement-${SAFE_NAME}.txt"
QA_OUT="${RUN_DIR}/qa-${SAFE_NAME}.txt"
LEDGER_ARTIFACT_PATH="${RUN_DIR}/qa-feedback-ledger.json"
CANONICAL_LEDGER_PATH="${PROJECT_ROOT}/.beacon/automation/qa-feedback-ledger.json"
SUMMARY_PATH="${RUN_DIR}/repair-window-summary.json"
QUEUE_UPDATE_ARTIFACT_PATH="${RUN_DIR}/queue-update.json"

if [[ "${ALLOW_DIRTY}" != "1" ]] && git -C "${PROJECT_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [[ -n "$(git -C "${PROJECT_ROOT}" status --porcelain)" ]]; then
    "${BEACON_BIN}" automation build-summary \
      --project-root "${PROJECT_ROOT}" \
      --summary-kind exception \
      --job beacon-repair-window \
      --layer implement \
      --status blocked \
      --feature "${TARGET_FEATURE}" \
      --artifact queue="${QUEUE_PATH}" \
      > "${SUMMARY_PATH}"
    send_summary_notification "${SUMMARY_PATH}" "Beacon repair window"
    echo "Refusing repair window on dirty worktree. Re-run with --allow-dirty for an explicit controlled validation window." >&2
    echo "wrote ${SUMMARY_PATH}"
    exit 3
  fi
fi

set +e
{
  echo "job=beacon-repair-window-job"
  echo "phase=implement"
  echo "timestamp=${TIMESTAMP}"
  echo "project_root=${PROJECT_ROOT}"
  echo "feature=${TARGET_FEATURE}"
  echo "version=${VERSION}"
  echo "host_runtime=${HOST_RUNTIME}"
  echo "runtime=${RUNTIME}"
  echo "mode=${MODE}"
  echo "runner=${RUNNER}"
  echo "dry_run=${DRY_RUN}"
  echo "beacon_bin=${BEACON_BIN}"
  echo
  if [[ "${DRY_RUN}" = "1" ]]; then
    "${BEACON_BIN}" implement run "${TARGET_FEATURE}" \
      --project "${PROJECT_ROOT}" \
      --version "${VERSION}" \
      --host-runtime "${HOST_RUNTIME}" \
      --mode "${MODE}" \
      --runner "${RUNNER}" \
      --runtime "${RUNTIME}" \
      --auto-switch-branch \
      --dry-run
  else
    "${BEACON_BIN}" implement run "${TARGET_FEATURE}" \
      --project "${PROJECT_ROOT}" \
      --version "${VERSION}" \
      --host-runtime "${HOST_RUNTIME}" \
      --mode "${MODE}" \
      --runner "${RUNNER}" \
      --runtime "${RUNTIME}" \
      --auto-switch-branch
  fi
} | tee "${IMPLEMENT_OUT}"
IMPLEMENT_STATUS=${PIPESTATUS[0]}
set -e

if [[ "${DRY_RUN}" = "1" ]]; then
  "${BEACON_BIN}" automation build-summary \
    --project-root "${PROJECT_ROOT}" \
    --summary-kind functional \
    --job beacon-repair-window \
    --layer implement \
    --status dry_run \
    --feature "${TARGET_FEATURE}" \
    --artifact implement="${IMPLEMENT_OUT}" \
    --artifact queue="${QUEUE_PATH}" \
    > "${SUMMARY_PATH}"
  send_summary_notification "${SUMMARY_PATH}" "Beacon repair window"
  echo "wrote ${SUMMARY_PATH}"
  exit 0
fi

if [[ "${IMPLEMENT_STATUS}" != "0" ]]; then
  "${BEACON_BIN}" automation build-summary \
    --project-root "${PROJECT_ROOT}" \
    --summary-kind exception \
    --job beacon-repair-window \
    --layer implement \
    --status failed \
    --feature "${TARGET_FEATURE}" \
    --artifact implement="${IMPLEMENT_OUT}" \
    --artifact queue="${QUEUE_PATH}" \
    > "${SUMMARY_PATH}"
  send_summary_notification "${SUMMARY_PATH}" "Beacon repair window"
  echo "wrote ${SUMMARY_PATH}"
  exit "${IMPLEMENT_STATUS}"
fi

{
  echo "job=beacon-repair-window-job"
  echo "phase=qa"
  echo "timestamp=${TIMESTAMP}"
  echo "project_root=${PROJECT_ROOT}"
  echo "feature=${TARGET_FEATURE}"
  echo "version=${VERSION}"
  echo "host_runtime=${HOST_RUNTIME}"
  echo "beacon_bin=${BEACON_BIN}"
  echo
  "${BEACON_BIN}" qa run "${TARGET_FEATURE}" \
    --project-root "${PROJECT_ROOT}" \
    --version "${VERSION}" \
    --host-runtime "${HOST_RUNTIME}"
} | tee "${QA_OUT}"

"${BEACON_BIN}" automation summarize-qa \
  --project-root "${PROJECT_ROOT}" \
  --feature "${TARGET_FEATURE}" \
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
  --job beacon-repair-window \
  --layer implement-qa \
  --ledger-path "${LEDGER_ARTIFACT_PATH}" \
  --queue-update-path "${QUEUE_UPDATE_ARTIFACT_PATH}" \
  --artifact implement="${IMPLEMENT_OUT}" \
  --artifact qa="${QA_OUT}" \
  --artifact qa_feedback_ledger="${LEDGER_ARTIFACT_PATH}" \
  --artifact queue_update="${QUEUE_UPDATE_ARTIFACT_PATH}" \
  --artifact queue="${QUEUE_PATH}" \
  > "${SUMMARY_PATH}"

send_summary_notification "${SUMMARY_PATH}" "Beacon repair window"

echo "wrote ${SUMMARY_PATH}"
