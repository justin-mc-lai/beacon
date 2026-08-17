---
slug: beacon-domain-fsm-authority-v167
version: v1.6.7
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.7/features/beacon-domain-fsm-authority-v167/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: Domain FSM Authority v1.6.7

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-DFSM-001 | TC-DFSM-001 | contract | `python3 -m pytest tests/test_v167_domain_fsm.py::test_schema_contract -q` | schema 字段齐全 |
| AC-DFSM-002 | TC-DFSM-006 | contract | `python3 -m pytest tests/test_v167_domain_fsm.py::test_truth_section_resolver_readable -q` | Domain Model/FSM 可解析 |
| AC-DFSM-003 | TC-DFSM-002 | negative | `python3 -m pytest tests/test_v167_domain_fsm.py::test_freeze_blocks_missing_fsm -q` | 缺 FSM freeze blocked |
| AC-DFSM-004 | TC-DFSM-003 | negative | `python3 -m pytest tests/test_v167_domain_fsm.py::test_clarity_fail_closed -q` | clarity fail-closed |
| AC-DFSM-005 | TC-DFSM-004 | contract | `python3 -m pytest tests/test_v167_domain_fsm.py::test_orphan_ac_detected -q` | 孤儿 AC 被检出 |
| AC-DFSM-006 | TC-DFSM-005 | contract | `python3 -m pytest tests/test_v167_domain_fsm.py::test_illegal_transition_slot_required -q` | 非法转移槽位必填 |
| AC-DFSM-007 | TC-DFSM-007 | contract | `python3 -m pytest tests/test_v167_domain_fsm.py::test_checklist_is_noncanonical -q` | checklist 非权威 |

## Verification Notes

- Contract tests under `tests/test_v167_domain_fsm.py`.
- Negative fixtures must fail closed (freeze or QA).
