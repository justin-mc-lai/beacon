---
slug: beacon-domain-fsm-qa-gate-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-domain-fsm-qa-gate-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Domain FSM QA Gate v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-FQA-001 | TC-FQA-001 | contract | `python3 -m pytest tests/test_v167_domain_fsm_qa.py::test_matrix_requires_legal_walk -q` | 矩阵强制合法 walk |
| AC-FQA-002 | TC-FQA-002 | contract | `python3 -m pytest tests/test_v167_domain_fsm_qa.py::test_matrix_requires_illegal -q` | 矩阵强制非法用例 |
| AC-FQA-003 | TC-FQA-003 | negative | `python3 -m pytest tests/test_v167_domain_fsm_qa.py::test_missing_coverage_blocks_ready -q` | 缺覆盖阻断 ready |
| AC-FQA-004 | TC-FQA-004 | integration | `python3 -m pytest tests/test_v167_domain_fsm_qa.py::test_golden_negative_consumed -q` | golden 负例被消费 |

## Verification Notes

- Contract tests may land under `tests/test_v167_product_goal_domain.py` (or per-feature modules).
- Negative fixtures must fail closed (freeze or QA).
