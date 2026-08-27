---
slug: beacon-v1613-d2-spend-ledger
version: v1.6.13
materials_status: current
---

# Tests: beacon-v1613-d2-spend-ledger

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k test_persisted_ledger --tb=short` | exit 0 + junit 断言 >0 |
| TC-002 | AC-002 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k "test_no_spend_without_writeback or test_spend_guard_contract" --tb=short` | exit 0 + junit 断言 >0 |
| TC-003 | AC-003 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k test_quiet_skip_no_spend --tb=short` | exit 0 + junit 断言 >0 |
| TC-004 | AC-004 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k test_idempotent_replay --tb=short` | exit 0 + junit 断言 >0 |
| TC-005 | AC-005 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k test_halt_on_exhaust --tb=short` | exit 0 + junit 断言 >0 |
| TC-006 | AC-006 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k test_handoff_budget --tb=short` | exit 0 + junit 断言 >0 |
| TC-FSM | AC-002..005 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py -k test_fsm_legal_walk --tb=short` | exit 0 + FSM 合法路径可达 halt |
| TC-EXEC | AC-001..005 | `python3 -m pytest -q --junitxml .beacon/junit.xml tests/test_v1613_spend_ledger.py --tb=short` | exit 0 + junit.xml 存在且断言数 ≥8 |
| TC-ILLEGAL | AC-002,AC-003,AC-004 | `rg -n "writeback\(未验证\) → spend|spend 重放 → 重复扣|quiet skip → spend" docs/beacon/v1.6.13/features/beacon-v1613-d2-spend-ledger/truth.md` | illegal（未验证/重放/skip 均不可 spend） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + business domain exec-layer（pytest junitxml 真实断言，含 FSM legal walk）。
