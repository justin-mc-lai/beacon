# 测试：Beacon Truth Integrity Gates v1.6.0

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-TIG-001 | TC-TIG-001 | integration | `beacon doctor verify-truth-integrity beacon-truth-integrity-gates-v160 --project-root . --version v1.6.0 --mode block --json` | `blocked=false` 且 `status=pass` 于本包 draft 通过后 |
| AC-TIG-002 | TC-TIG-002 | unit | `python -m pytest tests/test_truth_integrity.py -q` | 坏 fixture 触发 `placeholder_ac_language` / `soft_test_assertion` / `deferral_pending` |
| AC-TIG-003 | TC-TIG-003 | contract | `beacon skill package verify-closure --feature beacon-truth-integrity-gates-v160 --project-root . --version v1.6.0 --json` | `closure_allowed=true` 与 TIG `fake_delivery.closure_allowed` 一致 |
| AC-TIG-004 | TC-TIG-004 | unit | `python -m pytest tests/test_truth_integrity.py::test_prose_ac_validation_passes -q` | prose AC 包不报 `acceptance_criteria_table_missing` |
| AC-TIG-005 | TC-TIG-005 | integration | `beacon doctor verify-truth-integrity beacon-v2-rust-kernel-redesign --project-root . --version v2.0.0 --mode audit --json` | frozen v2 r4 包 `status=pass` 或 `audit_only` 且无 block |

## 验证说明

Canonical coverage 在本 package；runtime JSON 为投影，不是 requirement authority。
