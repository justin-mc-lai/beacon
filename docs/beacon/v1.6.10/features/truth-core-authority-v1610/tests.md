---
slug: truth-core-authority-v1610
version: v1.6.10
revision_id: R3
materials_status: current
---

# Tests R3

| TC ID | AC | Command | Assertion |
|-------|-----|---------|-----------|
| TC-TRG-001 | AC-TRG-001 | `rg -n "Mandatory Review Gate|强制.*审查|Truth Review Gate" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 强制门成文 |
| TC-TRG-002 | AC-TRG-002 | `rg -n "3-Step|Draft|Check A|Check B|Check C" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 三步管线 |
| TC-TRG-003 | AC-TRG-003 | `rg -n "Intent Coverage Matrix|intent_id|landing" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 矩阵 |
| TC-TRG-004 | AC-TRG-004 | `rg -n "悬空|非终态|转出 Event" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 悬空规则 |
| TC-TRG-005 | AC-TRG-005 | `rg -n "每 AC|≥ 1 TC|Command" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | AC→TC |
| TC-TRG-006 | AC-TRG-006 | `rg -n "Humanizer.*pass|A/B/C pass 后" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 润色序 |
| TC-TRG-007 | AC-TRG-007 | `rg -n "review_gate_pass" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | freeze 前置 |
| TC-TRG-008 | AC-TRG-008 | `rg -n "beacon truth review" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 命令合同 |
| TC-TRG-009 | AC-TRG-009 | `rg -n "truth_review_gate_failed" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | reason_code |
| TC-TRG-010 | AC-TRG-010 | `rg -n "refreeze 前重跑|重跑 Gate" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | refreeze 重跑 |
| TC-TRG-011 | AC-TRG-011 | `rg -n "不得单独授权 freeze|不能.*授权 freeze" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | plan 边界 |
| TC-TRG-012 | AC-TRG-012 | `rg -n "FP-008|级联" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 级联成本 |
| TC-TCA-003 | AC-TCA-003 | `rg -n "reopen|verify-materials" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | 变更链 |
| TC-TCA-007 | AC-TCA-007 | `test -f docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md && test -f docs/beacon/v1.6.10/features/truth-core-authority-v1610/tests.md && test -f docs/beacon/v1.6.10/features/truth-core-authority-v1610/tasks.md && test -f docs/beacon/v1.6.10/features/truth-core-authority-v1610/evidence.md` | 四件套 |
| TC-TCA-020 | illegal | `rg -n "without review_gate_pass|draft → frozen" docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md` | illegal freeze |
