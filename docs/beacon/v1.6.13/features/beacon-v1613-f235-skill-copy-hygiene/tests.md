---
slug: beacon-v1613-f235-skill-copy-hygiene
version: v1.6.13
materials_status: current
---

# Tests: beacon-v1613-f235-skill-copy-hygiene

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -c 'references/shared/|共享 Preamble' skills/beacon/beacon-{plan,truth,implement,qa,release,design,goal}/references/modes/*.md` | 引用方式存在（命中 ≥1/文件）且无整块复制（`rg -c 'Beacon v1.6.0 共享 Preamble' <mode>` 每文件 ≤1） |
| TC-002 | AC-002 | `rg -n 'beacon-gen-truth.*beacon-gen-truth.*beacon-gen-truth|旧版自指' skills/beacon/beacon-{plan,truth}/references/modes/*.md` | 无输出（复制 bug 已修） |
| TC-003 | AC-003 | `rg -n 'v1\.4\.|v1\.5\.' skills/beacon/beacon-{plan,truth,implement,qa,release,design,goal}/references/modes/*.md` | 无输出（无硬编码过期版本） |
| TC-004 | AC-004 | `rg -n 'eval-truth-review|truth-review' skills/beacon/beacon-truth/SKILL.md skills/beacon/beacon-truth/references/modes/*.md` | 命中 `eval-truth-review` 且 `truth-review` 仅作为 legacy alias 出现 |
| TC-EXEC | AC-001..004 | `python3 tests/test_v1613_skill_copy_hygiene.py` | exit 0（脚本断言共享引用/无复制 bug/无过期版本/前缀统一） |
| TC-ILLEGAL | AC-001,AC-003 | `rg -n "共享块仍多份复制且漂移|写死过期版本" docs/beacon/v1.6.13/features/beacon-v1613-f235-skill-copy-hygiene/truth.md` | illegal（复制残留/锚点漂移） |

## Validation Note

v1.6.10 TC layout for Truth Review Gate Check C + exec-layer（`tests/test_v1613_skill_copy_hygiene.py` 为真实断言）。
