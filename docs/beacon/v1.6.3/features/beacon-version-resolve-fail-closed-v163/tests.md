---
slug: beacon-version-resolve-fail-closed-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Version Resolve Fail-Closed v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-VR-001 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_no_hardcoded_v161_fallback -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | project_hooks.py:543 区域无 v1.6.1 硬编码字面量作 fallback |
| AC-002 | TC-VR-002 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_eval_version_resolves_docs_version -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | version=auto/空时 eval_version 解析为 docs 实际版本而非 v1.6.1 |
| AC-003 | TC-VR-003 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_hook_payload_has_drift_fields -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | post-release hook payload 含 runtime_version/docs_version/drift 字段 |
| AC-004 | TC-VR-004 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_resolve_failure_fail_closed -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | resolve_target_version 抛异常时 hook block 且 reason_code 含 version_resolve_failed |
| AC-005 | TC-VR-005 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_agent_eval_uses_resolved_version -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | is_live_runner_admitted 运行时用 resolve 版本，不依赖硬编码默认 |
| AC-006 | TC-VR-006 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_no_regression_normal_scenario -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime==docs 正常场景 hook 不误 block |
| AC-007 | TC-VR-007 | contract | `python3 -m pytest tests/test_v163_version_resolve_fail_closed.py::test_drift_legitimate_not_blocked -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | runtime≠docs 时 drift=true 但 status 不因 drift 而 block |

## 验证说明

- TC 文件 `tests/test_v163_version_resolve_fail_closed.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001/005 用源码 inspection（grep/AST）断言硬编码消除；TC-002..004/006/007 用 `tmp_path` 构造项目 + monkeypatch 验证 hook 行为。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
