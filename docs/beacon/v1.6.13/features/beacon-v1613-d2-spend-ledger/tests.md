---
slug: beacon-v1613-d2-spend-ledger
version: v1.6.13
materials_status: current
---

# Tests: beacon-v1613-d2-spend-ledger

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `python3 -m pytest tests/test_v1613_spend_ledger.py -k persisted_ledger -q --tb=short` | exit 0：ledger 落盘后重读，字段完整 |
| TC-002 | AC-002 | `python3 -m pytest tests/test_v1613_spend_ledger.py -k no_spend_without_writeback -q --tb=short` | exit 0：writeback 未验证 → spend 拒绝（`spend_without_writeback`） |
| TC-003 | AC-003 | `python3 -m pytest tests/test_v1613_spend_ledger.py -k quiet_skip_no_spend -q --tb=short` | exit 0：quiet skip/dry-run 后 spent 计数不变 |
| TC-004 | AC-004 | `python3 -m pytest tests/test_v1613_spend_ledger.py -k idempotent_replay -q --tb=short` | exit 0：同 index 重放不重复扣（CAS conflict） |
| TC-005 | AC-005 | `python3 -m pytest tests/test_v1613_spend_ledger.py -k halt_on_exhaust -q --tb=short` | exit 0：配额耗尽 → halt_budget + `program_drive_budget_exhausted` |
| TC-006 | AC-006 | `python3 -m pytest tests/test_v1613_spend_ledger.py -k handoff_budget -q --tb=short` | exit 0：交接文本超 16 行/1800 字符被拦（回归） |
| TC-EXEC | AC-001..005 | `python3 -m pytest tests/test_v1613_spend_ledger.py -q --tb=short` | exit 0：全套 spend ledger 断言通过 |
| TC-ILLEGAL | AC-002,AC-003,AC-004 | `rg -n "writeback\(未验证\) → spend|spend 重放 → 重复扣|quiet skip → spend" docs/beacon/v1.6.13/features/beacon-v1613-d2-spend-ledger/truth.md` | illegal（未验证/重放/skip 均不可 spend） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + business domain exec-layer（pytest 真实断言，非 print(0)）。
