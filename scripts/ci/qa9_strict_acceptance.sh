#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

PROJECT_ROOT="${PROJECT_ROOT:-${ROOT_DIR}}"
VERSION="${VERSION:-v1.0.2}"
FEATURE="${FEATURE:-qa9-llm-adaptive-automation-closure}"
UI_RUNNER="${UI_RUNNER:-browser-use}"

slugify() {
  local text="$1"
  text="$(echo "${text}" | tr '[:upper:]' '[:lower:]')"
  text="${text// /-}"
  echo "${text}"
}

FEATURE_SLUG="$(slugify "${FEATURE}")"
QA_MATRIX_PATH="${QA_MATRIX_PATH:-${PROJECT_ROOT}/docs/beacon/${VERSION}/qa/test-cases/${FEATURE_SLUG}.qa9-matrix.json}"
REPORT_PATH="${PROJECT_ROOT}/.beacon/qa9-strict-gate.json"
STUB_CMD="python3 ${PROJECT_ROOT}/scripts/ci/qa9_stub_runner.py"

echo "== [1/4] Generate QA9 test-case matrix =="
python3 -m beacon.main test-case create "${FEATURE}" \
  --project "${PROJECT_ROOT}" \
  --version "${VERSION}" \
  --qa-profile web-full \
  --llm-auto \
  --llm-mode auto

echo "QA_MATRIX_PATH=${QA_MATRIX_PATH}"
test -f "${QA_MATRIX_PATH}"

# Bootstrap minimal story + implementation marker for strict coverage gates.
mkdir -p "${PROJECT_ROOT}/docs/beacon/${VERSION}/user-story"
cat > "${PROJECT_ROOT}/docs/beacon/${VERSION}/user-story/${FEATURE_SLUG}.md" <<EOF
# User Story: ${FEATURE}

| AC ID | Description |
| --- | --- |
| AC-001 | ${FEATURE} should complete core flow |
EOF
mkdir -p "${PROJECT_ROOT}/.beacon/state"
cat > "${PROJECT_ROOT}/.beacon/state/implementation-${FEATURE_SLUG}.json" <<EOF
{"feature":"${FEATURE}","version":"${VERSION}","status":"completed"}
EOF

echo "== [2/4] Run QA9 auto-test =="
python3 -m beacon.main auto-test create qa9 \
  --project "${PROJECT_ROOT}" \
  --qa-matrix-path "${QA_MATRIX_PATH}" \
  --ui-runner "${UI_RUNNER}" \
  --unit-command "${STUB_CMD}" \
  --interface-command "${STUB_CMD}" \
  --contract-command "${STUB_CMD}" \
  --integration-command "${STUB_CMD}" \
  --smoke-command "${STUB_CMD}" \
  --functional-command "${STUB_CMD}" \
  --regression-command "${STUB_CMD}" \
  --exception-command "${STUB_CMD}" \
  --compatibility-command "${STUB_CMD}" \
  --require-fresh-evidence \
  --require-junit \
  --require-assertion-count \
  --rerun-flaky 1 \
  --max-flaky-rate 0.02

echo "== [3/4] Sync test progress =="
python3 -m beacon.main test-progress sync --project "${PROJECT_ROOT}"

# Bootstrap minimal execution artifacts required by strict release gate.
EXEC_DIR="${PROJECT_ROOT}/docs/beacon/${VERSION}/execution"
mkdir -p "${EXEC_DIR}"
if [[ ! -f "${EXEC_DIR}/boundaries.md" ]]; then
  cat > "${EXEC_DIR}/boundaries.md" <<EOF
# ${FEATURE} boundaries

- scope: qa9 strict acceptance
- in: test-case -> auto-test -> gate
- out: release publish action
EOF
fi

python3 - "${EXEC_DIR}/terminal.json" "${QA_MATRIX_PATH}" "${PROJECT_ROOT}" <<'PY'
import json
import pathlib
import sys

terminal_path = pathlib.Path(sys.argv[1])
matrix_path = pathlib.Path(sys.argv[2])
project_root = pathlib.Path(sys.argv[3]).resolve()
try:
    matrix_ref = str(matrix_path.resolve().relative_to(project_root))
except Exception:
    matrix_ref = str(matrix_path)
payload = {
    "status": "Pass",
    "traceability": {
        "evidence_refs": [
            ".beacon/auto-test-status.json",
            ".beacon/test-progress.json",
            matrix_ref,
        ]
    },
}
terminal_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
PY

python3 - "${PROJECT_ROOT}" "${VERSION}" <<'PY'
import json
import pathlib
import sys

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.workflow_memory import append_lifecycle_event

project_root = pathlib.Path(sys.argv[1]).resolve()
version = str(sys.argv[2])
status_path = project_root / ".beacon" / "auto-test-status.json"
status = json.loads(status_path.read_text(encoding="utf-8"))
run_id = str(status.get("execution", {}).get("run_id") or "run-qa9-strict-acceptance")
run_state_path = project_root / ".beacon" / "runs" / run_id / "state.json"
run_state_path.parent.mkdir(parents=True, exist_ok=True)
write_json(
    run_state_path,
    {
        "run_id": run_id,
        "workflow": "workflow.start",
        "feature": "qa9-strict-acceptance",
        "version": version,
        "status": "completed",
        "started_at": now_iso(),
        "ended_at": now_iso(),
    },
)

refs = [
    ".beacon/auto-test-status.json",
    ".beacon/test-progress.json",
    ".beacon/raw-command-log.jsonl",
    ".beacon/gate-report.json",
    str(run_state_path.relative_to(project_root)),
    f"docs/beacon/{version}/execution/boundaries.md",
    f"docs/beacon/{version}/execution/terminal.json",
]

for stage in ("think", "user-story", "prd", "test-case", "implementation", "verify"):
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="stage_started",
        source="qa9.strict.acceptance",
        evidence_ref=refs,
        details={"synthetic": True},
    )
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="stage_context_injected",
        source="qa9.strict.acceptance",
        evidence_ref=refs,
        details={"synthetic": True},
    )
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="stage_finished",
        source="qa9.strict.acceptance",
        evidence_ref=refs,
        details={"synthetic": True, "status": "completed"},
    )
    append_lifecycle_event(
        project_root,
        run_id=run_id,
        stage=stage,
        event="memory_writeback",
        source="qa9.strict.acceptance",
        evidence_ref=refs,
        details={"synthetic": True},
    )

append_lifecycle_event(
    project_root,
    run_id=f"release:{version}",
    stage="release",
    event="release_decision_recorded",
    source="qa9.strict.acceptance",
    evidence_ref=refs,
    details={"workflow_run_id": run_id, "synthetic": True},
)

write_json(
    project_root / ".beacon" / "gate-report.json",
    {
        "stage": "verify",
        "mode": "strict",
        "status": "Pass" if str(status.get("status", "")).lower() == "passed" else "Blocked",
        "issues": [],
        "updated_at": now_iso(),
    },
)

# Keep evidence manifest hash aligned after synthetic gate-report/lifecycle bootstrap.
manifest_path = project_root / ".beacon" / "evidence-manifest.json"
entries = []
if manifest_path.exists():
    try:
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict) and isinstance(loaded.get("entries"), list):
            entries = [x for x in loaded.get("entries", []) if isinstance(x, dict)]
    except Exception:  # noqa: BLE001
        entries = []
by_path = {str(item.get("path")): item for item in entries if str(item.get("path", "")).strip()}
by_path.pop(".beacon/evidence-manifest.json", None)
for ref in refs + [".beacon/gate-report.json", ".beacon/auto-test-status.json"]:
    full = project_root / ref
    if not full.exists() or not full.is_file():
        continue
    by_path[ref] = {
        "path": ref,
        "sha256": __import__("hashlib").sha256(full.read_bytes()).hexdigest(),
        "updated_at": now_iso(),
    }
write_json(manifest_path, {"schema_version": "1.0", "entries": list(by_path.values()), "updated_at": now_iso()})
PY

echo "== [4/4] Strict release gate =="
python3 -m beacon.main gate check release \
  --mode strict \
  --qa-policy qa9-strict \
  --min-automation-rate 0.85 \
  --require-qa-types unit,interface,contract,integration,smoke,functional,regression,exception,compatibility \
  --json \
  --project-root "${PROJECT_ROOT}" \
  > "${REPORT_PATH}"

python3 - "${PROJECT_ROOT}" "${REPORT_PATH}" <<'PY'
import json
import pathlib
import sys

project_root = pathlib.Path(sys.argv[1])
report_path = pathlib.Path(sys.argv[2])
raw = report_path.read_text(encoding="utf-8")
payload = json.loads(raw[raw.find("{"):])
assert payload.get("status") == "Pass", payload
assert int(payload.get("blocked_count", 0)) == 0, payload

auto_test_status = json.loads((project_root / ".beacon" / "auto-test-status.json").read_text(encoding="utf-8"))
assert str(auto_test_status.get("status", "")).lower() == "passed", auto_test_status
print("OK: qa9 strict acceptance passed")
PY

echo "✅ QA9 strict acceptance succeeded"
echo "Gate report: ${REPORT_PATH}"
