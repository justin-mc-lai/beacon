---
slug: beacon-product-goal-runtime-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Product Goal Runtime v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-PGR-001 | TC-PGR-001 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_state_schema -q` | state schema |
| AC-PGR-002 | TC-PGR-002 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_cli_surface -q` | CLI 合同 |
| AC-PGR-004 | TC-PGR-003 | negative | `python3 -m pytest tests/test_v167_product_goal.py::test_complete_requires_verifier -q` | 无 verifier 不可 complete |
| AC-PGR-005 | TC-PGR-004 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_blocked_requires_three_turns -q` | blocked≥3 |
| AC-PGR-006 | TC-PGR-005 | contract | `python3 -m pytest tests/test_v167_product_goal.py::test_stage_pointer_spans_lifecycle -q` | 阶段指针跨生命周期 |

## Verification Notes

- Contract tests may land under `tests/test_v167_product_goal_domain.py` (or per-feature modules).
- Negative fixtures must fail closed (freeze or QA).
