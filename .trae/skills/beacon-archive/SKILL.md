---
name: beacon-archive
description: Use when the user wants Beacon archive governance to plan/apply/status/explain historical requirement isolation without turning archive into a new lifecycle stage.
---

# Beacon Archive

This skill routes archive governance through Beacon's support-command surface.

Archive is not a new lifecycle stage. The lifecycle remains:

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

Use archive when historical requirement truth must stay traceable but stop contaminating the current delivery plane.

## Use for

- `beacon archive plan`
- `beacon archive apply`
- `beacon archive status`
- `beacon archive explain`
- Separating `active` truth from `archived-learnable` and `archived-reference-only`

## Operator rule

Prefer:

- `beacon archive ...`
- or `beacon archive ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh archive ...`)

Keep brainstorm read-only. If the task is still discussing archival strategy, stay on `beacon-brainstorm`. Once the user wants formal archive truth written, route to `beacon-archive`.

## Examples

- 适用例：
  - “这批旧 requirement 需要保留可追溯性，但不能继续污染当前交付面。”
  - “我想看 archive 现在的状态、计划或解释。”
- 不适用例：
  - “我还在讨论要不要归档、归档策略对不对。” -> 应先去 `beacon-brainstorm`
