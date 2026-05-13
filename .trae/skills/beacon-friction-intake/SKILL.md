---
name: beacon-friction-intake
description: Use when the user wants Beacon to scan project friction or capture a manual friction note, then persist it into the global sqlite governance queue without entering the main 6+3 workflow surface.
---

# Beacon Friction Intake

This skill routes optional friction governance work through Beacon's `friction-intake` support surface.
It is the primary `scan/capture` entry for Beacon friction governance.

## Use for

- scan Beacon source project friction, blockers, and bugs
- capture a manual friction note inside a target project
- classify friction into governance-ready queue items
- persist dual-write evidence into project-local artifacts and global sqlite
- decide whether a friction item should stay queue-only or be explicitly accepted for requirement/change

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon friction-intake run ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh friction-intake run ...`

Default expectations:

- `scan` mode is for Beacon source-project friction discovery
- `capture` mode is for manual friction logging in a target project
- both modes write queue items into the global runtime-ledger sqlite
- project-local truth stays in `.beacon/debug/`, `.beacon/memory/`, `.beacon/analysis/`
- requirement/change routing stays explicit and opt-in

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly accepts the item for requirement/change routing.

## Recommended command shapes

```bash
beacon friction-intake run \
  --project-root . \
  --version v1.4.3 \
  --mode scan \
  --json
```

```bash
beacon friction-intake run \
  --project-root . \
  --version v1.4.3 \
  --mode capture \
  --note "QA run is blocked because acceptance dual-write did not materialize" \
  --json
```

## Examples

- 适用例：
  - “先把这个阻塞记成 friction，不要立刻升级成需求或变更。”
  - “我想扫描 Beacon 源码仓最近有哪些摩擦点值得进治理队列。”
- 不适用例：
  - “我已经决定把这个问题正式纳入 requirement/change。” -> 应显式路由进相应主链 surface

## Cold-start anchors

- `friction-intake` 先做 capture 和 queue governance，不默认升级成正式 truth。
- 它的价值是让摩擦显性化、可排队、可筛选，而不是立即进入主工作流。
- 只有当用户明确接受 requirement/change routing 时，才应继续进入主链。
