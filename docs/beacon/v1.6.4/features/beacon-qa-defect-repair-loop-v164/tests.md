---
slug: beacon-qa-defect-repair-loop-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.4/features/beacon-qa-defect-repair-loop-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：QA Defect Repair Loop v1.6.4

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-DR-001 | contract | `python3 -m pytest tests/test_v164_qa_defect_repair_loop.py::test_defect_classification -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | QA finding 复用 `ROUTE_RECOMMENDATIONS` 分类为 7 family 之一；分类失败（unknown family）→ block |
| AC-002 | TC-DR-002 | contract | `python3 -m pytest tests/test_v164_qa_defect_repair_loop.py::test_repair_route_field -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `qa_acceptance` 输出含 `repair_route`（目标 harness）+ `defect_classification`（family + reason_code）；projection 同步 |
| AC-003 | TC-DR-003 | contract | `python3 -m pytest tests/test_v164_qa_defect_repair_loop.py::test_route_rules_release_blocking -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 路由规则：implementation_gap→beacon-implement, truth_drift→beacon-change, coverage_gap→beacon-test-case, execution_lapse→beacon-qa；RELEASE_BLOCKING_FAMILIES（implementation_gap/truth_drift/coverage_gap）强制 block release |
| AC-004 | TC-DR-004 | contract | `python3 -m pytest tests/test_v164_qa_defect_repair_loop.py::test_regression_trigger -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | defect 修复后 `regression_required=True`；回归未跑 → release block（reason_code 含 `regression_skipped`） |
| AC-005 | TC-DR-005 | contract | `python3 -m pytest tests/test_v164_qa_defect_repair_loop.py::test_closure_evidence_chain -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 闭环 evidence 链：defect 发现 → 修复 → 回归三段串联；缺段 → block（reason_code `repair_chain_broken`）；evidence 不被记为 full pass |

## 验证说明

- TC 文件 `tests/test_v164_qa_defect_repair_loop.py` 由 implement 阶段创建；实现前 tasks 允许标注 `BLOCKED:implement`。
- TC-001..005 为 contract 层（构造 QA finding payload + 调用分类/路由/回归函数断言）。
- 复用既有 `ROUTE_RECOMMENDATIONS` / `RELEASE_BLOCKING_FAMILIES`（import 校验）。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..005 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
