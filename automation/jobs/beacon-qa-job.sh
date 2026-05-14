#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/qa"
BEACON_BIN="${ROOT_DIR}/beacon-cli"
FEISHU_WEBHOOK="${AUTOMATION_FEISHU_WEBHOOK:-}"
FEISHU_SECRET="${AUTOMATION_FEISHU_SECRET:-}"
NOTIFY_HELPER="${ROOT_DIR}/automation/jobs/beacon-notify-feishu-post.py"

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
LEDGER_ARTIFACT_PATH="${OUTPUT_DIR}/qa-feedback-ledger-${TIMESTAMP}.json"
CANONICAL_LEDGER_PATH="${PROJECT_ROOT}/.beacon/automation/qa-feedback-ledger.json"
QUEUE_UPDATE_ARTIFACT_PATH="${OUTPUT_DIR}/queue-update-${TIMESTAMP}.json"
SUMMARY_PATH="${OUTPUT_DIR}/qa-summary-${TIMESTAMP}.json"

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
  --summary-kind nightly \
  --job beacon-nightly-qa \
  --layer qa \
  --ledger-path "${LEDGER_ARTIFACT_PATH}" \
  --queue-update-path "${QUEUE_UPDATE_ARTIFACT_PATH}" \
  --artifact qa_feedback_ledger="${LEDGER_ARTIFACT_PATH}" \
  --artifact queue_update="${QUEUE_UPDATE_ARTIFACT_PATH}" \
  > "${SUMMARY_PATH}"

if [[ -n "${FEISHU_WEBHOOK}" && -x "${NOTIFY_HELPER}" ]]; then
  NOTIFY_STATUS="$(python3 - "${SUMMARY_PATH}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(str(payload.get("status") or "").strip())
PY
)"
  if python3 "${NOTIFY_HELPER}" \
    --webhook "${FEISHU_WEBHOOK}" \
    --secret "${FEISHU_SECRET}" \
    --title "Beacon nightly QA ${NOTIFY_STATUS:-update}" \
    --summary-path "${SUMMARY_PATH}"; then
    python3 - "${SUMMARY_PATH}" sent <<'PY'
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
  else
    python3 - "${SUMMARY_PATH}" failed <<'PY'
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
  fi
else
  python3 - "${SUMMARY_PATH}" skipped <<'PY'
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
fi
