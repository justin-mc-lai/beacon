---
slug: beacon-v1613-f4-plain-language-contract
version: v1.6.13
materials_status: current
---

# Tests: beacon-v1613-f4-plain-language-contract

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -l 'plain_language_delivery_summary' skills/beacon/beacon-{design,goal,implement,plan,qa,release,truth}/SKILL.md` | 输出包含全部 7 个 SKILL.md（7 行） |
| TC-002 | AC-002 | `rg -n 'plain_language_delivery_summary' skills/beacon/beacon-truth/SKILL.md` | 命中字段名 |
| TC-003 | AC-003 | `rg -c 'mode_id|Intent Coverage Matrix|AC-' skills/beacon/beacon-plan/SKILL.md` | 机器字段仍存在（计数 ≥3） |
| TC-004 | AC-004 | `rg -n 'truth_human_l0_missing|## 人话|## Plain language' skills/beacon/beacon-truth/references/modes/gen-truth.md` | 命中 fail-closed 约束与 L0 标题 |
| TC-EXEC | AC-001 | `python3 tests/test_v1613_plain_language_contract.py` | exit_code 0（脚本断言 7 个 SKILL.md 均含字段） |
| TC-ILLEGAL | AC-004 | `rg -n "frozen truth without L0 人话|truth_human_l0_missing" docs/beacon/v1.6.13/features/beacon-v1613-f4-plain-language-contract/truth.md` | illegal（L0 缺失 freeze 被拦） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + docs-layer exec TC（`tests/test_v1613_plain_language_contract.py` 为真实断言脚本，非 print(0)）。
