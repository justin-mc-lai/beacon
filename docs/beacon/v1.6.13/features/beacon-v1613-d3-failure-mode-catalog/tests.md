---
slug: beacon-v1613-d3-failure-mode-catalog
version: v1.6.13
materials_status: current
---

# Tests: beacon-v1613-d3-failure-mode-catalog

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -c '^## FM-|^### 模式' skills/beacon/beacon-qa/references/failure-mode-catalog.md` | 目录条目 ≥ 5 |
| TC-002 | AC-002 | `rg -c 'rubric|判定标准' skills/beacon/beacon-qa/references/failure-mode-catalog.md` | 每条含 rubric（命中数 ≥ 条目数） |
| TC-003 | AC-003 | `python3 -m pytest tests/test_v1613_failure_mode_catalog.py -q --tb=short` | exit 0：用例断言可独立执行 |
| TC-004 | AC-004 | `rg -n 'failure-mode-catalog|失败模式目录' skills/beacon/beacon-qa/references/modes/eval-qa.md skills/beacon/beacon-qa/references/modes/eval-qa-deep.md` | 审查模式引用目录 |
| TC-005 | AC-005 | `rg -n 'user decides|人裁决|不自动判' skills/beacon/beacon-qa/references/failure-mode-catalog.md` | 明确批判式意见边界 |
| TC-EXEC | AC-001,AC-003 | `python3 -m pytest tests/test_v1613_failure_mode_catalog.py -q --tb=short` | exit 0：目录存在 + 条目/rubric/引用断言通过 |
| TC-ILLEGAL | AC-005 | `rg -n "目录自动判 pass|未引用目录仍声称" docs/beacon/v1.6.13/features/beacon-v1613-d3-failure-mode-catalog/truth.md` | illegal（越权裁决/advisory 缺失） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（pytest 断言目录/rubric/gate 引用）。
