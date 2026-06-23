---
slug: beacon-global-workspace-git-admission-v162
version: v1.6.2
status: frozen
revision_id: R3
language: zh
truth_ref: docs/beacon/v1.6.2/features/beacon-global-workspace-git-admission-v162/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Global Workspace Git Admission v1.6.2

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-WS-001 | integration | `mkdir -p .beacon/qa-tmp && beacon workspace admit --project-root . --version v1.6.2 --feature beacon-global-workspace-git-admission-v162 --json >.beacon/qa-tmp/TC-WS-001.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-WS-001.json')); assert d.get('status')=='pass' and 'worktree_path' in d"` | pass + worktree |
| AC-001 | TC-WS-002 | contract | `python3 -m pytest tests/test_v162_workspace_admit.py::test_admit_json_schema_no_expires_at -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 无 normative expires_at |
| AC-002 | TC-WS-010 | integration | `mkdir -p .beacon/qa-tmp && rm -f .beacon/state/workspace-admission/v1.6.2/beacon-global-workspace-git-admission-v162.json && python3 -m beacon implement run "beacon-global-workspace-git-admission-v162" --project-root . --version v1.6.2 --json >.beacon/qa-tmp/TC-WS-010.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-WS-010.json')); assert d.get('status')=='blocked'"` | fail-closed 无 artifact |
| AC-002 | TC-WS-011 | integration | `python3 -m pytest tests/test_v162_workspace_integration.py::test_qa_run_blocked_without_artifact -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | qa fail-closed（gate，避免嵌套 qa run 超时） |
| AC-003 | TC-WS-020 | contract | `rg -q 'GIT_ADMISSION' skills/beacon/SKILL.md && rg -q 'workspace admit' skills/beacon/SKILL.md` | umbrella preamble |
| AC-003 | TC-WS-021 | integration | `beacon doctor setup-agent-surface --project-root . --agent cursor --force && rg -q 'GIT_ADMISSION' .cursor/skills/beacon-gen-implement/SKILL.md` | 物化 Step 0 |
| AC-004 | TC-WS-030 | hook | `python3 -m pytest tests/test_v162_workspace_admission_hook.py::test_cursor_hook_denies_missing_artifact -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | deny 无 artifact |
| AC-004 | TC-WS-031 | hook | `python3 -m pytest tests/test_v162_workspace_admission_hook.py::test_cursor_hook_allows_valid_artifact -q` | allow valid |
| AC-004 | TC-WS-032 | hook | `python3 -m pytest tests/test_v162_workspace_admission_hook.py::test_hook_no_ttl_deny -q` | 时间 alone 不 deny |
| AC-005 | TC-WS-040 | hook | `python3 -m pytest tests/test_v162_workspace_admission_hook.py::test_claude_hook_parity -q` | Claude parity |
| AC-006 | TC-WS-050 | integration | `mkdir -p .beacon/qa-tmp && python3 -m beacon doctor verify-agent-surface --project-root . --agent cursor --strict --json >.beacon/qa-tmp/TC-WS-050.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-WS-050.json')); checks=(d.get('result') or {}).get('checks') or d.get('checks') or []; assert any(c.get('name')=='v160_shared_preamble_and_hard_gates' for c in checks)"` | preamble check |
| AC-006 | TC-WS-051 | integration | `beacon doctor verify-agent-surface --project-root . --agent cursor --strict --json >.beacon/qa-tmp/TC-WS-051.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-WS-051.json')); assert d.get('ok') is True or 'hook' in str(d).lower()"` | hook warn path |
| AC-007 | TC-WS-060 | hook | `TRELLIS_DISABLE_HOOKS=1 python3 -m pytest tests/test_v162_workspace_admission_hook.py::test_beacon_hook_independent_of_trellis -q` | Trellis 隔离 |
| AC-008 | TC-WS-070 | governance | `python3 -m pytest tests/test_v162_workspace_admit.py::test_governance_v162_dirty_only -q` | v1.6.2 MD block |
| AC-009 | TC-WS-080 | integration | `python3 -m pytest tests/test_v162_workspace_admit.py::test_dirty_invalidation_branch_change -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | exit 0 或 BLOCKED:Phase-A |
| AC-009 | TC-WS-082 | integration | `python3 -m pytest tests/test_v162_workspace_admit.py::test_no_ttl_still_valid -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | exit 0 或 BLOCKED:Phase-A |
| AC-010 | TC-WS-090 | integration | `mkdir -p .beacon/qa-tmp && beacon implement check-branch --project-root . --version v1.6.2 --feature beacon-global-workspace-git-admission-v162 --json >.beacon/qa-tmp/TC-WS-090.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-WS-090.json')); assert d.get('status')=='pass'"` | alias pass |
| AC-012 | TC-VL-001 | contract | `python3 -m pytest tests/test_v162_version_line_package_closure.py::test_upgrade_package_writes_release_stub -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | release stub |
| AC-013 | TC-VL-010 | contract | `python3 -m pytest tests/test_v162_version_line_package_closure.py::test_package_gate_routes_upgrade_package -q` | remediation_mode |
| AC-014 | TC-VL-011 | contract | `python3 -m pytest tests/test_v162_version_line_package_closure.py::test_package_gate_repair_commands -q` | repair_commands |
| AC-015 | TC-VL-020 | integration | `mkdir -p .beacon/qa-tmp && python3 -m beacon doctor upgrade-package --project-root . --version v1.6.2 --json >/dev/null && python3 -m beacon doctor verify-materials --project-root . --version v1.6.2 --strict --json >.beacon/qa-tmp/TC-VL-020.json 2>&1; python3 -c "import json; d=json.load(open('.beacon/qa-tmp/TC-VL-020.json')); ok=(d.get('result') or {}).get('ok'); assert ok is True or d.get('status') in ('PASS','pass')"` | strict pass |
| AC-011 | TC-WS-100 | integration | `python3 -m pytest tests/test_v162_agent_eval_admit.py::test_slash_skill_step0_admit -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | exit 0 或 BLOCKED:Phase-D |

## 验证说明

- Phase 实现前允许 tasks 标注 `BLOCKED:Phase-*`；command 列须含 `beacon` / `pytest` / `BLOCKED:`。
- **无 TTL TC**：不存在 expired-by-time 必 fail 用例（方案 A）。
- Hook TC（AC-004..007）为 **Should**；不挡 formal QA MVP。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..003, AC-008..015 |
| Should | AC-004..007 |

---

**Revision:** R3 adds version-line package operator closure (AC-012..015).
