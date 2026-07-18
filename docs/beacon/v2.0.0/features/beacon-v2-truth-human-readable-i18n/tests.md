---
slug: beacon-v2-truth-human-readable-i18n
version: v2.0.0
status: frozen
revision_id: R1
---

# Tests: beacon-v2-truth-human-readable-i18n

| AC ID | TC ID | Assertion |
|-------|-------|-----------|
| AC-V2-HR-001 | TC-V2-HR-001 | parity map v167 AC-HR present in upstream_ref package |
| AC-V2-HR-002 | TC-V2-HR-002 | self has ## 人话 |
| AC-V2-HR-003 | TC-V2-HR-003 | shared norms files exist |
| AC-V2-HR-004 | TC-V2-HR-004 | `beacon goal axis validate -v v2.0.0 --program beacon-v2-product-goal-parallel-v200` includes slug |
| AC-V2-HR-005 | TC-V2-HR-005 | reason_code string stable |
| AC-V2-HR-006 | TC-V2-HR-006 | no v2-only conflicting norms path required |

Commands: `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py -q`
