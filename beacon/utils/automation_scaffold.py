"""Project-local scaffold generator for Beacon automation assets."""

from __future__ import annotations

import re
import shutil
import stat
from pathlib import Path
from typing import Any

from beacon.utils.automation_executors import executor_capability, normalize_executor, scaffold_scheduler_dir
from beacon.utils.automation_queue import build_automation_queue_validation_payload, default_queue_path
from beacon.utils.runtime import now_iso, write_json


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower())
    slug = slug.strip("-")
    return slug or "project"


def _default_beacon_bin() -> str:
    return shutil.which("beacon") or "beacon"


def _env_example() -> str:
    return """# Optional local notification transport for Beacon automation wrappers.
# Keep real webhook values in automation/.env only; do not commit automation/.env.
AUTOMATION_FEISHU_WEBHOOK=
AUTOMATION_FEISHU_SECRET=
"""


def _default_queue_payload(project_root: Path, *, executor: str) -> dict[str, Any]:
    capability = executor_capability(executor)
    target_agent = str(capability.get("executor") or "codex")
    return {
        "version": "v0",
        "project_root": str(project_root),
        "default_workspace_mode": "worktree",
        "jobs": [
            {
                "job_id": "beacon-morning-status",
                "job_kind": "status",
                "target_agent": target_agent,
                "enabled": True,
                "feature_selector": {"mode": "all_active"},
                "preconditions": [],
                "workspace_mode": "worktree",
                "risk_level": "low",
                "on_blocked": "report_only",
                "on_success": "report_only",
                "notes": "Read-only morning triage.",
            },
            {
                "job_id": "beacon-nightly-qa",
                "job_kind": "qa",
                "target_agent": target_agent,
                "enabled": False,
                "feature_selector": {"mode": "explicit_list", "features": []},
                "preconditions": ["implementation_evidence_present"],
                "workspace_mode": "worktree",
                "risk_level": "medium",
                "on_blocked": "report_only",
                "on_success": "report_only",
                "notes": str(capability.get("notes") or "Enable and populate features before use."),
            },
            {
                "job_id": "beacon-gated-implement",
                "job_kind": "implement",
                "target_agent": target_agent,
                "enabled": False,
                "feature_selector": {"mode": "explicit_list", "features": []},
                "preconditions": ["truth_frozen", "prototype_complete_if_required"],
                "workspace_mode": "worktree",
                "risk_level": "high",
                "on_blocked": "handoff_to_human",
                "on_success": "trigger_qa",
                "notes": (
                    "Never enable without explicit queue review."
                    if bool(capability.get("beacon_runtime_execution"))
                    else "Scaffolded for queue governance only; implement execution still requires a supported Beacon runtime adapter."
                ),
            },
        ],
    }


_NOTIFICATION_SHELL = r'''
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
'''


def _status_job_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/status"
BEACON_BIN="beacon"
""" + _NOTIFICATION_SHELL + r'''

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

mkdir -p "${OUTPUT_DIR}"
TIMESTAMP="$(date '+%Y%m%dT%H%M%S')"
OUT_FILE="${OUTPUT_DIR}/status-${TIMESTAMP}.txt"
SUMMARY_PATH="${OUTPUT_DIR}/status-summary-${TIMESTAMP}.json"

set +e
{
  echo "job=beacon-status-job"
  echo "timestamp=${TIMESTAMP}"
  echo "project_root=${PROJECT_ROOT}"
  echo "queue=${QUEUE_PATH}"
  echo "beacon_bin=${BEACON_BIN}"
  echo
  "${BEACON_BIN}" status --project-root "${PROJECT_ROOT}" --version "${VERSION}" show-status
} | tee "${OUT_FILE}"
STATUS_CODE=${PIPESTATUS[0]}
set -e

SUMMARY_STATUS="passed"
if [[ "${STATUS_CODE}" != "0" ]]; then
  SUMMARY_STATUS="failed"
fi

"${BEACON_BIN}" automation build-summary \
  --project-root "${PROJECT_ROOT}" \
  --summary-kind status \
  --job beacon-morning-status \
  --layer status \
  --status "${SUMMARY_STATUS}" \
  --artifact status="${OUT_FILE}" \
  --artifact queue="${QUEUE_PATH}" \
  > "${SUMMARY_PATH}"

send_summary_notification "${SUMMARY_PATH}" "Beacon morning status"

echo "wrote ${OUT_FILE}"
echo "wrote ${SUMMARY_PATH}"
exit "${STATUS_CODE}"
'''


def _qa_job_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/qa"
BEACON_BIN="beacon"
""" + _NOTIFICATION_SHELL + r'''

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
  "${BEACON_BIN}" automation build-summary \
    --project-root "${PROJECT_ROOT}" \
    --summary-kind nightly \
    --job beacon-nightly-qa \
    --layer qa \
    --status skipped \
    --artifact queue="${QUEUE_PATH}" \
    > "${SUMMARY_PATH}"
  send_summary_notification "${SUMMARY_PATH}" "Beacon nightly QA"
  echo "No enabled QA features found in ${QUEUE_PATH}; nightly QA window closed, skipping." >&2
  echo "wrote ${SUMMARY_PATH}"
  exit 0
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

send_summary_notification "${SUMMARY_PATH}" "Beacon nightly QA"
'''


def _hourly_qa_job_script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="${ROOT_DIR}"
QUEUE_PATH="${ROOT_DIR}/automation/beacon-automation-queue.json"
VERSION="auto"
HOST_RUNTIME="codex"
OUTPUT_DIR="${ROOT_DIR}/.beacon/automation-runs/hourly-qa"
BEACON_BIN="beacon"
""" + _NOTIFICATION_SHELL + r'''

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
'''


def _feishu_post_notifier_script() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys
import time
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a Feishu post notification for Beacon automation jobs.")
    parser.add_argument("--webhook", required=True, help="Feishu bot webhook URL.")
    parser.add_argument("--secret", default="", help="Optional Feishu bot signing secret.")
    parser.add_argument("--title", required=True, help="Post title.")
    parser.add_argument("--summary-path", required=True, help="Path to a Beacon automation summary JSON file.")
    return parser.parse_args()


def load_summary(path: Path) -> dict:
    if not path.exists():
        return {
            "notification": {
                "title": "Beacon automation summary missing",
                "lines": [f"summary_path={path}", "summary_missing=true"],
            }
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def build_payload(*, title: str, summary: dict) -> dict:
    notification = summary.get("notification") if isinstance(summary.get("notification"), dict) else {}
    lines = notification.get("lines") if isinstance(notification.get("lines"), list) else []
    resolved_title = str(notification.get("title") or title).strip() or title
    reconciliation = summary.get("reconciliation") if isinstance(summary.get("reconciliation"), dict) else {}
    required_features = reconciliation.get("required_features") if isinstance(reconciliation.get("required_features"), list) else []
    reprojection_targets = reconciliation.get("reprojection_targets") if isinstance(reconciliation.get("reprojection_targets"), list) else []
    if required_features:
        lines = list(lines)
        lines.append("")
        lines.append("reconciliation_summary")
        lines.append(f"required_features={', '.join(str(item).strip() for item in required_features if str(item).strip())}")
        lines.append(f"reprojection_targets={', '.join(str(item).strip() for item in reprojection_targets if str(item).strip()) or '-'}")
    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": resolved_title,
                    "content": [[{"tag": "text", "text": line}] for line in lines],
                }
            }
        },
    }


def attach_signature(payload: dict, *, secret: str) -> None:
    if not secret:
        return
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\\n{secret}"
    sign = base64.b64encode(
        hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    ).decode("utf-8")
    payload["timestamp"] = timestamp
    payload["sign"] = sign


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_path)
    summary = load_summary(summary_path)
    payload = build_payload(title=args.title, summary=summary)
    attach_signature(payload, secret=args.secret)
    request = urllib.request.Request(
        args.webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    result = json.loads(body) if body else {}
    status_code = result.get("StatusCode", result.get("code", 0))
    if status_code not in (0, "0", None):
        print(body, file=sys.stderr)
        return 1
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _gated_implement_job_script() -> str:
    return r"""#!/usr/bin/env bash
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
BEACON_BIN="beacon"

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
"""


def _repair_window_job_script() -> str:
    return """#!/usr/bin/env bash
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
""" + _NOTIFICATION_SHELL + r'''

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
'''


def _status_prompt(project_root: Path, queue_path: Path, *, executor: str) -> str:
    capability = executor_capability(executor)
    status_output = project_root / ".beacon" / "automation-runs" / "status"
    wrapper = project_root / "automation" / "jobs" / "beacon-status-job.sh"
    return f"""# Codex Automation Spec: Morning Status

Type: `standalone`

Schedule suggestion:

- Weekdays at `09:00`
- Or custom cron: `0 9 * * 1-5`

Workspace mode:

- Prefer `worktree`
- executor: `{executor}`
- tier: `{capability.get("tier", "")}`

Prompt:

```text
Use $beacon:beacon for this run.

Project root: {project_root}
Queue file: {queue_path}

Goal:
Run a low-risk morning Beacon status pass. Read current workflow state, active execution surfaces, QA status, implementation next tasks, and release-facing blockers. Do not modify requirement truth. Do not start implementation. Do not run release write actions.

Steps:
1. Run the host wrapper:
   {wrapper} \\
     --project-root {project_root} \\
     --queue {queue_path} \\
     --output-dir {status_output}
2. Read the generated artifact and summarize:
   - active features
   - blocked features
   - QA status and evidence gaps
   - implementation next task / blocked task signals
   - release-prep risks
3. Report only actionable findings. If there is nothing important, say so briefly.

Output:
- concise human summary
- artifact path
- recommended next route: status, qa, implement, change, or release-prep
```
"""


def _qa_prompt(project_root: Path, queue_path: Path, *, executor: str) -> str:
    capability = executor_capability(executor)
    output_dir = project_root / ".beacon" / "automation-runs" / "qa"
    wrapper = project_root / "automation" / "jobs" / "beacon-qa-job.sh"
    runtime_line = (
        f"     --host-runtime {capability.get('host_runtime_value')} \\\n"
        if capability.get("beacon_runtime_execution") and capability.get("host_runtime_value")
        else ""
    )
    capability_note = (
        "Run through a Beacon-supported runtime."
        if capability.get("beacon_runtime_execution")
        else "Do not claim native Beacon host-runtime support; use this as adapter guidance only."
    )
    return f"""# Automation Spec: Nightly QA

Type: `standalone`

Schedule suggestion:

- Daily at `23:00`
- Or custom cron: `0 23 * * *`

Workspace mode:

- Prefer `worktree`
- executor: `{executor}`
- tier: `{capability.get("tier", "")}`

Prompt:

```text
Use $beacon:beacon and $beacon:beacon-qa for this run.

Project root: {project_root}
Queue file: {queue_path}

Goal:
Run nightly Beacon QA for queued candidate features. Respect Beacon truth/gate boundaries. Do not rewrite frozen truth. Do not perform release write actions.

Steps:
1. Run the host wrapper:
   {wrapper} \\
     --project-root {project_root} \\
     --queue {queue_path} \\
{runtime_line}\
     --output-dir {output_dir}
2. Read the generated artifacts.
3. For each feature, report:
   - layered verdict summary
   - blockers
   - repair handoff needed or not
   - evidence paths
4. If a protected live surface blocks execution because session admission is missing, record it explicitly as blocked or skipped, not as product failure.
5. Capability note:
   - {capability_note}

Output:
- one section per feature
- pass / blocked / repair-needed summary
- evidence refs
- recommended next route
```
"""


def _implement_prompt(project_root: Path, queue_path: Path, *, executor: str) -> str:
    capability = executor_capability(executor)
    output_dir = project_root / ".beacon" / "automation-runs" / "implement"
    wrapper = project_root / "automation" / "jobs" / "beacon-gated-implement-job.sh"
    runtime_line = (
        f"     --host-runtime {capability.get('host_runtime_value')} \\\n"
        if capability.get("beacon_runtime_execution") and capability.get("host_runtime_value")
        else ""
    )
    capability_note = (
        "This executor can drive Beacon implement/qa directly."
        if capability.get("beacon_runtime_execution")
        else "This executor is scaffold-only here; do not claim native Beacon implement runtime support."
    )
    return f"""# Automation Spec: Gated Implement

Type: `standalone`

Schedule suggestion:

- Low frequency only
- Example custom cron: `0 13 * * 1-5`

Workspace mode:

- Prefer `worktree`
- executor: `{executor}`
- tier: `{capability.get("tier", "")}`

Prompt:

```text
Use $beacon:beacon and $beacon:beacon-implement for this run.

Project root: {project_root}
Queue file: {queue_path}

Goal:
Run a gated implementation window for explicitly queued features only. Never choose a feature opportunistically. Never reopen or rewrite requirement truth. Use Beacon gates to decide whether implementation may proceed.

Steps:
1. Run the host wrapper:
   {wrapper} \\
     --project-root {project_root} \\
     --queue {queue_path} \\
{runtime_line}\
     --workspace-mode worktree \\
     --output-dir {output_dir}
2. Read the generated artifacts.
3. Report:
   - executed candidates
   - skipped candidates with reasons
   - evidence refs
   - whether QA should run next

Constraints:
- do not force execution when gates fail
- do not edit the queue file during the run
- do not run release write actions
- capability note: {capability_note}
```
"""


def _launchd_plist(
    *,
    label: str,
    script_path: Path,
    project_root: Path,
    queue_path: Path,
    output_dir: Path,
    hour: int = 0,
    minute: int = 0,
    interval_seconds: int = 0,
    host_runtime: str = "",
    workspace_mode: str = "",
    version: str = "",
    mode: str = "",
    runner: str = "",
    runtime: str = "",
    beacon_bin: str = "",
    env_file: Path | None = None,
) -> str:
    extra_args = ""
    if version:
        extra_args += f"""
      <string>--version</string>
      <string>{version}</string>"""
    if host_runtime:
        extra_args += f"""
      <string>--host-runtime</string>
      <string>{host_runtime}</string>"""
    if workspace_mode:
        extra_args += f"""
      <string>--workspace-mode</string>
      <string>{workspace_mode}</string>"""
    if runtime:
        extra_args += f"""
      <string>--runtime</string>
      <string>{runtime}</string>"""
    if mode:
        extra_args += f"""
      <string>--mode</string>
      <string>{mode}</string>"""
    if runner:
        extra_args += f"""
      <string>--runner</string>
      <string>{runner}</string>"""
    if beacon_bin:
        extra_args += f"""
      <string>--beacon-bin</string>
      <string>{beacon_bin}</string>"""
    if env_file:
        extra_args += f"""
      <string>--env-file</string>
      <string>{env_file}</string>"""
    schedule = (
        f"""
    <key>StartInterval</key>
    <integer>{interval_seconds}</integer>"""
        if interval_seconds
        else f"""
    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key>
      <integer>{hour}</integer>
      <key>Minute</key>
      <integer>{minute}</integer>
    </dict>"""
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>{label}</string>

    <key>ProgramArguments</key>
    <array>
      <string>/bin/zsh</string>
      <string>{script_path}</string>
      <string>--project-root</string>
      <string>{project_root}</string>
      <string>--queue</string>
      <string>{queue_path}</string>{extra_args}
      <string>--output-dir</string>
      <string>{output_dir}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{project_root}</string>
{schedule}

    <key>RunAtLoad</key>
    <false/>

    <key>StandardOutPath</key>
    <string>{output_dir / "launchd.out"}</string>
    <key>StandardErrorPath</key>
    <string>{output_dir / "launchd.err"}</string>
  </dict>
</plist>
"""


def _automation_readme(project_root: Path, project_slug: str, *, executor: str) -> str:
    capability = executor_capability(executor)
    return f"""# Beacon Automation Sandbox

This directory holds host-level scheduling assets for Beacon-oriented automation in `{project_slug}`.

Generated by:

```bash
beacon automation init --project-root {project_root}
```

Principles:

- Beacon remains the truth-aware execution surface.
- Scheduling stays outside Beacon core commands.
- Queue governance is explicit.
- `implement` jobs must never run without an explicit candidate queue and gate checks.
- executor profile: `{executor}` / `{capability.get("tier", "")}` / `{capability.get("status", "")}`

Current contents:

- `beacon-automation-queue.json`
  - canonical queue for scheduled jobs
- `jobs/`
  - thin wrappers that call Beacon public CLI only
- `codex/`
  - Codex automation prompt specs
- `launchd/`
  - local macOS launch agents
- executor capability note:
  - {capability.get("notes", "")}

Quick start:

1. Bootstrap the scaffold:

```bash
beacon automation init --project-root .
```

2. Validate the queue:

```bash
beacon automation validate-queue --project-root .
```

3. Edit `automation/beacon-automation-queue.json` to enable QA or implement candidates.

Human-facing toolkit surface:

```bash
Use $beacon:beacon-toolkit-automation
```

Feedback loop:

- hourly/nightly QA should refresh:
  - `.beacon/automation/qa-feedback-ledger.json`
- hourly/nightly QA should also build:
  - `.beacon/automation-runs/hourly-qa/qa-summary-*.json`
  - `.beacon/automation-runs/qa/qa-summary-*.json`
- hourly/nightly QA should then update:
  - `automation/beacon-automation-queue.json`
- `repair-window` is the recommended controlled implement window:
  - queue must contain exactly one implement feature
  - dirty worktrees are blocked by default
  - successful implement automatically returns to QA and updates the queue
- `gated-implement` remains generated for compatibility, but should stay disabled unless an operator explicitly opens a governed implement window

Optional notification env:

- `AUTOMATION_FEISHU_WEBHOOK`
- `AUTOMATION_FEISHU_SECRET`
- Optional local file: `automation/.env`
- Example template: `automation/.env.example`
- Notification transport is host-plane only; it is not release truth.

Scaffolded helper:

- `automation/jobs/beacon-notify-feishu-post.py`

Automation prompt specs live under `automation/{scaffold_scheduler_dir(project_root, executor)}/`.

macOS launch agents live under `automation/launchd/`.

Reference capability guide:

- `docs/analysis/codex-automations-and-beacon-capability-guide.md`

Support reporting entrypoint:

```bash
beacon automation capabilities --project-root .
beacon automation validate-queue --project-root .
beacon automation summarize-qa --project-root .
beacon automation build-summary --project-root . --job beacon-nightly-qa --layer qa
beacon automation update-queue --project-root .
```
"""


def init_automation_scaffold(project_root: Path, *, force: bool = False, executor: str = "codex") -> dict[str, Any]:
    root = project_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    project_slug = _slug(root.name)
    resolved_executor = normalize_executor(executor)
    capability = executor_capability(resolved_executor)
    queue_path = default_queue_path(root)
    automation_root = root / "automation"
    jobs_root = automation_root / "jobs"
    prompts_dir_name = scaffold_scheduler_dir(root, resolved_executor)
    prompt_root = automation_root / prompts_dir_name
    launchd_root = automation_root / "launchd"
    env_example_path = automation_root / ".env.example"
    env_path = automation_root / ".env"
    beacon_bin = _default_beacon_bin()
    status_dir = root / ".beacon" / "automation-runs" / "status"
    qa_dir = root / ".beacon" / "automation-runs" / "qa"
    hourly_qa_dir = root / ".beacon" / "automation-runs" / "hourly-qa"
    implement_dir = root / ".beacon" / "automation-runs" / "implement"
    repair_window_dir = root / ".beacon" / "automation-runs" / "repair-window"

    actions: list[dict[str, str]] = []
    created_count = 0
    refreshed_count = 0
    unchanged_count = 0

    for directory in [
        automation_root,
        jobs_root,
        prompt_root,
        launchd_root,
        root / ".beacon" / "automation",
        status_dir,
        qa_dir,
        hourly_qa_dir,
        implement_dir,
        repair_window_dir,
    ]:
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        actions.append(
            {
                "path": str(directory.relative_to(root)),
                "kind": "directory",
                "action": "created" if not existed else "ensured",
            }
        )

    launchd_specs = {
        f"com.beacon.{project_slug}.morning-status.plist": _launchd_plist(
            label=f"com.beacon.{project_slug}.morning-status",
            script_path=jobs_root / "beacon-status-job.sh",
            project_root=root,
            queue_path=queue_path,
            output_dir=status_dir,
            hour=9,
            minute=0,
            beacon_bin=beacon_bin,
            env_file=env_path,
        ),
        f"com.beacon.{project_slug}.nightly-qa.plist": _launchd_plist(
            label=f"com.beacon.{project_slug}.nightly-qa",
            script_path=jobs_root / "beacon-qa-job.sh",
            project_root=root,
            queue_path=queue_path,
            output_dir=qa_dir,
            hour=23,
            minute=0,
            host_runtime=str(capability.get("host_runtime_value") or ""),
            beacon_bin=beacon_bin,
            env_file=env_path,
        ),
        f"com.beacon.{project_slug}.hourly-qa.plist": _launchd_plist(
            label=f"com.beacon.{project_slug}.hourly-qa",
            script_path=jobs_root / "beacon-hourly-qa-job.sh",
            project_root=root,
            queue_path=queue_path,
            output_dir=hourly_qa_dir,
            interval_seconds=3600,
            host_runtime=str(capability.get("host_runtime_value") or ""),
            beacon_bin=beacon_bin,
            env_file=env_path,
        ),
        f"com.beacon.{project_slug}.gated-implement.plist": _launchd_plist(
            label=f"com.beacon.{project_slug}.gated-implement",
            script_path=jobs_root / "beacon-gated-implement-job.sh",
            project_root=root,
            queue_path=queue_path,
            output_dir=implement_dir,
            hour=13,
            minute=0,
            host_runtime=str(capability.get("host_runtime_value") or ""),
            workspace_mode="worktree",
            beacon_bin=beacon_bin,
        ),
        f"com.beacon.{project_slug}.repair-window.plist": _launchd_plist(
            label=f"com.beacon.{project_slug}.repair-window",
            script_path=jobs_root / "beacon-repair-window-job.sh",
            project_root=root,
            queue_path=queue_path,
            output_dir=repair_window_dir,
            hour=2,
            minute=30,
            host_runtime=str(capability.get("host_runtime_value") or ""),
            runtime="file",
            mode="team",
            runner="codex-subagents",
            beacon_bin=beacon_bin,
            env_file=env_path,
        ),
    }

    file_specs: list[dict[str, Any]] = [
        {"path": queue_path, "kind": "json", "payload": _default_queue_payload(root, executor=resolved_executor)},
        {"path": jobs_root / "beacon-status-job.sh", "kind": "text", "content": _status_job_script(), "executable": True},
        {"path": jobs_root / "beacon-qa-job.sh", "kind": "text", "content": _qa_job_script(), "executable": True},
        {"path": jobs_root / "beacon-hourly-qa-job.sh", "kind": "text", "content": _hourly_qa_job_script(), "executable": True},
        {"path": jobs_root / "beacon-notify-feishu-post.py", "kind": "text", "content": _feishu_post_notifier_script(), "executable": True},
        {
            "path": jobs_root / "beacon-gated-implement-job.sh",
            "kind": "text",
            "content": _gated_implement_job_script(),
            "executable": True,
        },
        {
            "path": jobs_root / "beacon-repair-window-job.sh",
            "kind": "text",
            "content": _repair_window_job_script(),
            "executable": True,
        },
        {"path": prompt_root / "morning-status.md", "kind": "text", "content": _status_prompt(root, queue_path, executor=resolved_executor)},
        {"path": prompt_root / "nightly-qa.md", "kind": "text", "content": _qa_prompt(root, queue_path, executor=resolved_executor)},
        {"path": prompt_root / "gated-implement.md", "kind": "text", "content": _implement_prompt(root, queue_path, executor=resolved_executor)},
        {"path": automation_root / "README.md", "kind": "text", "content": _automation_readme(root, project_slug, executor=resolved_executor)},
        {"path": env_example_path, "kind": "text", "content": _env_example()},
    ]
    for filename, content in launchd_specs.items():
        file_specs.append({"path": launchd_root / filename, "kind": "text", "content": content})

    for spec in file_specs:
        path = Path(spec["path"])
        existed = path.exists()
        if existed and not force:
            action = "unchanged"
            unchanged_count += 1
        else:
            if spec["kind"] == "json":
                write_json(path, spec["payload"])
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(spec["content"]).rstrip("\n") + "\n", encoding="utf-8")
            if spec.get("executable"):
                current_mode = path.stat().st_mode
                path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            action = "refreshed" if existed else "created"
            if existed:
                refreshed_count += 1
            else:
                created_count += 1
        actions.append(
            {
                "path": str(path.relative_to(root)),
                "kind": str(spec["kind"]),
                "action": action,
            }
        )

    queue_validation = build_automation_queue_validation_payload(root, queue_path)
    project_root_text = str(root)
    launchd_dir = launchd_root
    prompt_root_text = str(prompt_root)
    install_dir = str((Path.home() / "Library" / "LaunchAgents").expanduser())
    next_steps = [
        f"beacon automation validate-queue --project-root {project_root_text}",
        f"beacon automation capabilities --project-root {project_root_text}",
        f"beacon automation summarize-qa --project-root {project_root_text} --json",
        f"cp {launchd_dir / f'com.beacon.{project_slug}.nightly-qa.plist'} {install_dir}/",
        f"cp {launchd_dir / f'com.beacon.{project_slug}.hourly-qa.plist'} {install_dir}/",
    ]
    return {
        "schema_version": "1.0",
        "status": "completed" if queue_validation.get("status") == "valid" else "failed",
        "command": "beacon automation init",
        "project_root": str(root),
        "automation_root": str(automation_root),
        "queue_path": str(queue_path),
        "executor": resolved_executor,
        "executor_capability": capability,
        "beacon_bin": beacon_bin,
        "prompt_root": str(prompt_root),
        "launchd_root": str(launchd_root),
        "readme_path": str(automation_root / "README.md"),
        "force": force,
        "generated_at": now_iso(),
        "created_count": created_count,
        "refreshed_count": refreshed_count,
        "unchanged_count": unchanged_count,
        "actions": actions,
        "queue_validation": {
            "status": str(queue_validation.get("status", "")),
            "error_count": int(queue_validation.get("error_count", 0) or 0),
            "errors": list(queue_validation.get("errors", []) or []),
        },
        "launchd_labels": sorted(spec["Label"] for spec in [
            {"Label": f"com.beacon.{project_slug}.morning-status"},
            {"Label": f"com.beacon.{project_slug}.nightly-qa"},
            {"Label": f"com.beacon.{project_slug}.hourly-qa"},
            {"Label": f"com.beacon.{project_slug}.gated-implement"},
            {"Label": f"com.beacon.{project_slug}.repair-window"},
        ]),
        "next_steps": next_steps,
        "toolkit": {
            "skill": "beacon-toolkit-automation",
            "entrypoint": f"beacon automation init --project-root {project_root_text}",
            "prompt_root": prompt_root_text,
            "launchd_install_dir": install_dir,
        },
    }


def render_automation_init_markdown(payload: dict[str, Any]) -> str:
    toolkit = payload.get("toolkit", {}) if isinstance(payload.get("toolkit"), dict) else {}
    lines = [
        "# Beacon Automation Scaffold",
        "",
        f"- status: `{payload.get('status', '')}`",
        f"- project_root: `{payload.get('project_root', '')}`",
        f"- beacon_bin: `{payload.get('beacon_bin', '')}`",
        f"- automation_root: `{payload.get('automation_root', '')}`",
        f"- queue_path: `{payload.get('queue_path', '')}`",
        f"- readme_path: `{payload.get('readme_path', '')}`",
        f"- prompt_root: `{payload.get('prompt_root', '')}`",
        f"- launchd_root: `{payload.get('launchd_root', '')}`",
        f"- created_count: `{payload.get('created_count', 0)}`",
        f"- refreshed_count: `{payload.get('refreshed_count', 0)}`",
        f"- unchanged_count: `{payload.get('unchanged_count', 0)}`",
        "",
        "## Toolkit",
        f"- skill: `{toolkit.get('skill', '')}`",
        f"- entrypoint: `{toolkit.get('entrypoint', '')}`",
        f"- launchd_install_dir: `{toolkit.get('launchd_install_dir', '')}`",
        "",
        "## Launchd Labels",
    ]
    for label in payload.get("launchd_labels", []) or []:
        lines.append(f"- `{label}`")
    queue_validation = payload.get("queue_validation", {}) if isinstance(payload.get("queue_validation"), dict) else {}
    lines.extend(
        [
            "",
            "## Queue Validation",
            f"- status: `{queue_validation.get('status', '')}`",
            f"- error_count: `{queue_validation.get('error_count', 0)}`",
            "",
            "## Actions",
        ]
    )
    for item in payload.get("actions", []) or []:
        if not isinstance(item, dict):
            continue
        lines.append(f"- `{item.get('action', '')}` `{item.get('path', '')}`")
    next_steps = payload.get("next_steps") if isinstance(payload.get("next_steps"), list) else []
    if next_steps:
        lines.extend(["", "## Next Steps"])
        for command in next_steps:
            lines.append(f"- `{command}`")
    return "\n".join(lines) + "\n"
