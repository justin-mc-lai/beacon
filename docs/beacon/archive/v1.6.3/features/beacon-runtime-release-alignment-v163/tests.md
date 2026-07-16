---
slug: beacon-runtime-release-alignment-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Runtime Release Alignment v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-RA-001 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_release_gate_blocks_drift -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | release stage runtime≠docs → critical block `runtime_docs_release_drift` |
| AC-002 | TC-RA-002 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_release_gate_pass_when_aligned -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime==docs 时 release gate 不因 drift block |
| AC-003 | TC-RA-003 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_hook_runtime_alignment_field -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | hook payload 含 runtime_alignment 字段（runtime_version/docs_version/aligned/recommended_command） |
| AC-004 | TC-RA-004 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_hook_routes_sync_version_surfaces -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime≠docs 时 recommended_command 含 `beacon doctor sync-version-surfaces` |
| AC-005 | TC-RA-005 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_dev_stages_no_block -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | plan/qa stage 不因 runtime≠docs block |
| AC-006 | TC-RA-006 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_no_auto_pip_install -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | hook 不执行 pip install（源码无 pip install 调用） |
| AC-007 | TC-RA-007 | contract | `python3 -m pytest tests/test_v163_runtime_release_alignment.py::test_no_regression_p01 -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | _resolve_eval_version + resolve failure fail-closed 仍生效 |

## 验证说明

- TC 文件 `tests/test_v163_runtime_release_alignment.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001/002/005 用 tmp_path + monkeypatch 测 gate 各 stage 行为；TC-003/004/006 stub hook 重操作测 payload；TC-007 测 P0-1 守卫仍生效。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
