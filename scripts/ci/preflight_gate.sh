#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

ARTIFACT_ROOT="${ROOT_DIR}/.artifacts/preflight"
mkdir -p "${ARTIFACT_ROOT}"

echo "== [1/7] Skill command sync check =="
python3 scripts/sync_skill_commands.py --check

echo "== [2/7] Full test suite =="
python3 -m pytest -q

echo "== [3/7] Build acceptance sandbox =="
ACPT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/beacon-preflight-XXXXXX")"
echo "ACPT_DIR=${ACPT_DIR}" | tee "${ARTIFACT_ROOT}/sandbox.txt"

echo "== [4/7] P0 gate consistency (workflow --auto -> strict release gate) =="
python3 -m beacon.main workflow start "Preflight Delivery" \
  --auto \
  --project "${ACPT_DIR}" \
  --version v1.1.0 \
  --implementation-command 'python3 -c "print(\"impl\")"' \
  --verify-scope unit \
  --verify-unit-command 'python3 -c "print(\"ok\")"' \
  | tee "${ARTIFACT_ROOT}/workflow.out"

grep -q "NEXT STEP SELECTOR" "${ARTIFACT_ROOT}/workflow.out"

python3 -m beacon.main gate check release \
  --mode strict \
  --json \
  --project-root "${ACPT_DIR}" \
  > "${ARTIFACT_ROOT}/gate-release.json"

python3 - "${ARTIFACT_ROOT}/gate-release.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
raw = path.read_text(encoding="utf-8")
payload = json.loads(raw[raw.find("{"):])
assert payload["status"] == "Pass", payload
assert payload["blocked_count"] == 0, payload
print("OK: strict release gate Pass")
PY

echo "== [5/7] P1 version/evolution governance =="
python3 -m beacon.main version create "Version Governance Check" \
  --project "${ACPT_DIR}" \
  --base-version v1.0.1 \
  --bump minor \
  | tee "${ARTIFACT_ROOT}/version-create.out"

test -f "${ACPT_DIR}/docs/beacon/v1.1.0/version/version-governance-check.md"
test -f "${ACPT_DIR}/.beacon/state/version-plans/v1.1.0/version-governance-check.json"

python3 -m beacon.main evolution-summary create v1.1.0 \
  --project "${ACPT_DIR}" \
  --previous v1.0.1 \
  | tee "${ARTIFACT_ROOT}/evolution-summary.out"

test -f "${ACPT_DIR}/docs/beacon/v1.1.0/SUMMARY.md"
test -f "${ACPT_DIR}/.beacon/state/evolution-summary/v1.1.0.json"
! grep -q "TBD" "${ACPT_DIR}/docs/beacon/v1.1.0/SUMMARY.md"

echo "== [6/7] P2 visual regression gate (pass then fail) =="
python3 - "${ACPT_DIR}" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
(root / "visual/baseline").mkdir(parents=True, exist_ok=True)
(root / "visual/current").mkdir(parents=True, exist_ok=True)
(root / "visual/baseline/home.png").write_bytes(b"same-image")
(root / "visual/current/home.png").write_bytes(b"same-image")
PY

python3 -m beacon.main auto-test create visual \
  --project "${ACPT_DIR}" \
  --visual-baseline-dir "${ACPT_DIR}/visual/baseline" \
  --visual-current-dir "${ACPT_DIR}/visual/current" \
  --visual-threshold 0 \
  > "${ARTIFACT_ROOT}/visual-pass.out"

python3 - "${ACPT_DIR}/.beacon/auto-test-status.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "passed", payload
print("OK: visual pass")
PY

python3 - "${ACPT_DIR}" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
(root / "visual/current/home.png").write_bytes(b"changed-image")
PY

python3 -m beacon.main auto-test create visual \
  --project "${ACPT_DIR}" \
  --visual-baseline-dir "${ACPT_DIR}/visual/baseline" \
  --visual-current-dir "${ACPT_DIR}/visual/current" \
  --visual-threshold 0 \
  > "${ARTIFACT_ROOT}/visual-fail.out"

python3 - "${ACPT_DIR}/.beacon/auto-test-status.json" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["status"] == "failed", payload
print("OK: visual fail on diff")
PY

echo "== [7/7] LLM real-mode fallback gate =="
BEACON_LLM_MODE=real python3 -m beacon.main run workflow \
  --project-root "${ACPT_DIR}" \
  --feature "LLM Fallback Check" \
  --version v1.1.0 \
  --json \
  > "${ARTIFACT_ROOT}/run-fallback.json"

python3 - "${ACPT_DIR}" "${ARTIFACT_ROOT}/run-fallback.json" <<'PY'
import json
import pathlib
import sys

acpt_dir = pathlib.Path(sys.argv[1])
run_payload = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
run_id = run_payload["run_id"]
state = json.loads((acpt_dir / ".beacon" / "runs" / run_id / "state.json").read_text(encoding="utf-8"))
trace = (state.get("llm_prompts") or [{}])[0]
assert trace.get("inference_mode") == "rule-fallback", trace
print("OK: llm fallback =", trace.get("inference_mode"))
PY

cp -R "${ACPT_DIR}" "${ARTIFACT_ROOT}/acceptance-sandbox"

echo "✅ Preflight gate passed"
echo "Artifacts: ${ARTIFACT_ROOT}"
