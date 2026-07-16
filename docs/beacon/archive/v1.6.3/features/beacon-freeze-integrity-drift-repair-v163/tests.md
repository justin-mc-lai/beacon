---
slug: beacon-freeze-integrity-drift-repair-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-freeze-integrity-drift-repair-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Freeze Integrity Drift Repair v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-FI-001 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_parser_contract_v2_accepted -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parser_contract=v2 的包通过 validation，无 parser_contract_mismatch |
| AC-001 | TC-FI-002 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_parser_contract_v1_still_accepted -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parser_contract=v1 的包仍通过 |
| AC-001 | TC-FI-003 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_unknown_contract_still_mismatch -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | parser_contract=beacon-feature-package-v9 仍报 parser_contract_mismatch |
| AC-002 | TC-FI-010 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_forbidden_field_substring_not_banned -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | evidence 含路径子串 gate-truth 不触发 evidence_forbidden_gate_truth_field |
| AC-002 | TC-FI-011 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_real_forbidden_authority_still_banned -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | authority=source_of_truth 仍报 evidence_invalid_authority |
| AC-003 | TC-FI-020 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_integration_pytest_not_soft -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Layer=integration + pytest command 行无 soft_test_assertion finding |
| AC-003 | TC-FI-021 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_hard_markers_regex_includes_pytest -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | _HARD_TEST_MARKERS_RE.search 含 pytest 的字符串命中 |
| AC-004 | TC-FI-030 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_authority_table_error_self_describing -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | evidence_authority_table_missing diagnostic 含 allowed_authorities 与 surface/authority 列提示 |
| AC-004 | TC-FI-031 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_invalid_authority_error_self_describing -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | evidence_invalid_authority diagnostic 含 allowed_authorities 列表 |
| AC-005 | TC-FI-040 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_v1_package_backward_compat -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.2 已冻结 feature 包修复后仍 pass validation |
| AC-006 | TC-FI-050 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_p03_package_no_regression -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | beacon-gate-truth-model-alignment-v163 包修复后仍 pass validation |
| AC-007 | TC-FI-060 | contract | `python3 -m pytest tests/test_v163_freeze_integrity_drift_repair.py::test_real_weak_assertion_still_blocked -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | Layer=integration 且无 hard command 的行仍被 soft_test_assertion 标记 |

## 验证说明

- TC 文件 `tests/test_v163_freeze_integrity_drift_repair.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- 所有 TC 为单元测试，直接调用 `beacon.utils.feature_package` 与 `beacon.utils.truth_integrity` 的校验函数，用 `tmp_path` 构造 feature 包。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
