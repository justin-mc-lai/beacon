---
slug: beacon-post-release-hook-agent-coverage-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Post-Release Hook Agent Coverage v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-HK-001 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_hook_covers_5_agents -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | hook agent 循环含 trae/claude/codex/cursor/windsurf 全 5 个 |
| AC-002 | TC-HK-002 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_all_agents_setup_verify_in_payload -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | agent_surfaces payload 含 5 agent 的 setup_status + verify_status |
| AC-003 | TC-HK-003 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_drift_blocks_hook -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 任一 agent drift 时 hook block 且 reason_code 含 verify_failed |
| AC-004 | TC-HK-004 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_claude_global_preserved -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | hook 仍调 install_global_claude_beacon_skills + verify |
| AC-005 | TC-HK-005 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_no_regression_codex_claude -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | codex/claude 仍 force=True + strict=True |
| AC-006 | TC-HK-006 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_no_regression_block_reasons -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | setup_failed/verify_failed reason_code 语义不变 |
| AC-007 | TC-HK-007 | contract | `python3 -m pytest tests/test_v163_post_release_hook_agent_coverage.py::test_agent_constant_reused -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 循环复用 agent_surface 全 agent 常量，无新硬编码 |

## 验证说明

- TC 文件 `tests/test_v163_post_release_hook_agent_coverage.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001/007 用源码 inspection 断言；TC-002..006 用 monkeypatch stub hook 内部重操作（run_agent_surface_setup/verify/install_global）测 payload + block 行为。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
