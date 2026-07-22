---
slug: truth-humanizer-runtime-v1610
version: v1.6.10
revision_id: R2
materials_status: current
---

| TC ID | AC | Command | Assertion |
|-------|-----|---------|-----------|
| TC-HUM-002 | AC-HUM-002 | `test -f /Users/apple/Developer/Personal/oss-sync/core-skills/Humanizer-zh/SKILL.md` | exit 0 |
| TC-HUM-003 | AC-HUM-003 | `test -f /Users/apple/Developer/Personal/oss-sync/core-skills/humanizer/SKILL.md` | exit 0 |
| TC-HUM-005 | AC-HUM-005 | `rg -n "速查|非权威" skills/beacon/references/truth-humanizer/truth_prose.zh.md` | 标注 |
| TC-HUM-011 | AC-HUM-011 | `rg -n "Humanizing|两引擎|humanizer" docs/beacon/v1.6.10/SUMMARY.md docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md` | 引擎定位 |
| TC-HUM-001 | AC-HUM-001 | `rg -n "default_language|profiles" docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md` | schema |

| TC-HUM-004 | AC-HUM-004 | `rg -n "preserve_machine|AC/FSM|机器字段" docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md` | preserve |
| TC-HUM-006 | AC-HUM-006 | `rg -n "global|project|merge" docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md` | merge |
| TC-HUM-007 | AC-HUM-007 | `rg -n "bilingual" docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md` | bilingual |
| TC-HUM-008 | AC-HUM-008 | `rg -n "require_on_truth_write|humanizer_skill_path_missing" docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md beacon/utils/humanizer_config.py` | fail path |
| TC-HUM-009 | AC-HUM-009 | `rg -n "全文|fulltext|SKILL" docs/beacon/v1.6.10/features/truth-humanizer-runtime-v1610/truth.md` | fulltext |
| TC-HUM-010 | AC-HUM-010 | `rg -n "truth_human_readable|prose-check" beacon/commands/truth.py` | L0 parallel |
