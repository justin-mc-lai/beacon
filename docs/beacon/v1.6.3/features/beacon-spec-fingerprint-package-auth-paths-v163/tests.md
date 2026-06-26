---
slug: beacon-spec-fingerprint-package-auth-paths-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Spec Fingerprint Package-Auth Paths v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-SF-001 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_user_story_layer_package_auth -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 包 fingerprint user_story 层 count>0 |
| AC-002 | TC-SF-002 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_prd_layer_package_auth -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | ≥v1.5.2 包 fingerprint prd 层 count>0 |
| AC-003 | TC-SF-003 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_truth_change_detected -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 改 truth.md 后 fingerprint hash 改变 |
| AC-004 | TC-SF-004 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_legacy_find_layer_files_unchanged -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | <v1.5.2 _find_layer_files 行为不变 |
| AC-005 | TC-SF-005 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_case_layer_preserved -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | test_case 层仍扫 .machine/qa/*.ac-test-matrix.json |
| AC-006 | TC-SF-006 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_no_regression_v163_release -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.3 release gate 重生成 fingerprint 后仍 pass |
| AC-007 | TC-SF-007 | contract | `python3 -m pytest tests/test_v163_spec_fingerprint_package_auth_paths.py::test_no_regression_v162 -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.2 fingerprint 行为不变 |

## 验证说明

- TC 文件 `tests/test_v163_spec_fingerprint_package_auth_paths.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001..005 用 tmp_path 构造版本目录树测 _find_layer_files/generate_spec_fingerprint；TC-006/007 对真实包断言。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
