---
slug: beacon-v2-domain-fsm-authority
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-domain-fsm-authority/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: v2 Domain FSM Authority

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-DFSM-001 | TC-V2-DFSM-001 | contract | `python3 -m pytest tests/test_v200_domain_fsm.py::test_schema_contract -q` | schema 字段齐全 |
| AC-V2-DFSM-003 | TC-V2-DFSM-002 | negative | `python3 -m pytest tests/test_v200_domain_fsm.py::test_missing_fsm_blocks_freeze -q` | 缺 FSM freeze blocked |
| AC-V2-DFSM-006 | TC-V2-DFSM-003 | contract | `python3 -m pytest tests/test_v200_domain_fsm.py::test_illegal_slot_required -q` | 非法转移槽位 |
| AC-V2-DFSM-007 | TC-V2-DFSM-004 | parity | `python3 -m pytest tests/test_v200_domain_fsm.py::test_v167_fixture_parity -q` | v167 夹具等价语义 |
