---
slug: beacon-gate-truth-model-alignment-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-gate-truth-model-alignment-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Gate Truth Model Alignment v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-GT-001 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_semver_fork_v162_no_legacy_top_dirs_required -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 版本 issues 中无 `formal_package_closure_missing` 因 prd/user-story/qa/test-cases 缺失 |
| AC-002 | TC-GT-002 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_feature_package_closure_satisfied -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 版本有 features/<slug>/{truth,tests}.md 时 issues 为空 |
| AC-003 | TC-GT-003 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_legacy_v1410_keeps_top_dir_contract -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | <v1.5.2 版本缺 prd/user-story/qa/test-cases 仍报 `formal_package_closure_missing` |
| AC-004 | TC-GT-004 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_version_line_materials_still_checked -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 版本缺 SUMMARY/execution/boundaries 仍 critical block |
| AC-005 | TC-GT-005 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_missing_feature_package_blocks -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 版本无任何 feature 包 → reason_code `feature_package_closure_missing`，message 不含 prd/user-story/qa/test-cases |
| AC-006 | TC-GT-006 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_regression_v162_no_top_dir_block -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 对本项目 v1.6.2 跑 check_formal_version_package_closure，issues 中无 missing prd/user-story/qa/test-cases |
| AC-007 | TC-GT-007 | contract | `python3 -m pytest tests/test_v163_gate_model_alignment.py::test_empty_dir_no_bypass -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 版本仅有空 prd/ 目录无 feature 包 → 仍 block，空目录不绕过 |

## 验证说明

- TC 文件 `tests/test_v163_gate_model_alignment.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- 所有 TC 为单元测试，直接调用 `beacon.commands.gate.check_formal_version_package_closure`，用 `tmp_path` 构造版本目录树，避免依赖真实 docs。
- AC-006 为契约回归，对本项目真实 v1.6.2 docs 目录断言。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
