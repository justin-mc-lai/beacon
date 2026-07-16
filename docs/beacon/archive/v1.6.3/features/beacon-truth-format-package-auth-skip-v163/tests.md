---
slug: beacon-truth-format-package-auth-skip-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Truth Format Package-Auth Skip v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-TF-001 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_feature_paths_package_auth -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | compute_feature_paths 对 ≥v1.5.2 返回 features/<slug>/truth.md 路径 |
| AC-002 | TC-TF-002 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_manifest_status_from_frontmatter -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | package-auth frozen 包 manifest status=frozen |
| AC-003 | TC-TF-003 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_truth_format_skip_package_auth -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | build_requirement_package_gate 对 ≥v1.5.2 不报 truth_format_non_compliant |
| AC-004 | TC-TF-004 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_legacy_truth_format_preserved -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | <v1.5.2 truth_format 校验行为不变 |
| AC-005 | TC-TF-005 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_implement_unblocked_format -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.3 frozen 包 implement run 不因 truth_format blocked |
| AC-006 | TC-TF-006 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_no_regression_v162 -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.2 包 build_requirement_package_gate 仍 pass |
| AC-007 | TC-TF-007 | contract | `python3 -m pytest tests/test_v163_truth_format_package_auth_skip.py::test_feature_package_validate_still_runs -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | package-auth 包仍经 feature_package.validate 校验 |

## 验证说明

- TC 文件 `tests/test_v163_truth_format_package_auth_skip.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001/002/004 用 tmp_path 构造版本目录树；TC-003/005/006 对真实包断言；TC-007 验证 feature_package.validate 仍调用。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
