---
slug: beacon-v2-domain-fsm-qa-gate
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-qa-gate/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: v2 Domain FSM QA Gate

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-FQA-001 | TC-V2-FQA-001 | contract | `python3 -m pytest tests/test_v200_domain_fsm_qa.py::test_legal_walk_required -q` | 合法 walk 强制 |
| AC-V2-FQA-002 | TC-V2-FQA-002 | negative | `python3 -m pytest tests/test_v200_domain_fsm_qa.py::test_illegal_required -q` | 非法行强制 |
| AC-V2-FQA-003 | TC-V2-FQA-003 | negative | `python3 -m pytest tests/test_v200_domain_fsm_qa.py::test_missing_coverage_blocks_release -q` | 缺 coverage 阻断 |
| AC-V2-FQA-004 | TC-V2-FQA-004 | integration | `python3 -m pytest tests/test_v200_domain_fsm_qa.py::test_golden_negative_consumed -q` | 负例消费 |
