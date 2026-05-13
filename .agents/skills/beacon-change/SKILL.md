---
name: beacon-change
description: Use when the user wants to adjust a frozen Beacon feature, reopen its revision, refresh requirement materials, and return to implementation/QA/release through the existing mainline.
---

# Beacon Change

## Overview

`beacon-change` is the host-visible router for post-freeze requirement revisions.

It does not create a new primary stage. It reopens frozen truth in a governed way, refreshes the requirement package, and routes the work back into the existing mainline.

## When to Use

- frozen feature scope must change
- a hotfix or repair needs requirement truth updated before implementation continues
- requirement supplement is needed after freeze
- a support surface concluded that accepted scope, promise, or coverage must change

## Boundary

- `beacon-change` is not a parallel workflow
- it does not bypass `prd -> user-story -> test-case`
- it does not directly claim implementation, QA, or release completion

## Workflow / Decision Loop

- confirm that current truth is already frozen enough to require a change loop
- reopen the affected requirement truth and revision context
- refresh `prd`, `user-story`, and `test-case` as needed
- re-freeze before returning to `implement`, `qa`, or `release`

## Common Rationalizations

- “只是一个小修，不用回 formal truth。” -> 不允许；如果改 promise/acceptance，就必须进 `change`
- “support surface 已经下结论，可以直接改实现。” -> 不允许；support surface 只能 route，不直接写 truth
- “先修代码，最后再补文档。” -> 不允许；`change` 先于实现修改

## Red Flags

- frozen truth 已经漂移，但还试图直接进入 `implement`
- 把 `change` 当成内部脚本步骤，而不是 requirement reopen surface
- 修改 acceptance 或 scope，却没有显式 re-freeze 意图

## Verification

- 修改目标确实属于 frozen truth revision，而不是未冻结的 requirement clarification
- 变更会回写到正式 requirement package，而不是只停留在分析或实现面
- 后续路由会回到 `implement`、`qa` 或 `release`，而不是停在 reopen 中间态

## Evidence Produced

- change intent and reopen rationale
- affected requirement surfaces
- re-freeze expectation and downstream route

## State Updated

- revision/reopen state
- requirement package status for the affected feature

## Gate Impact

- blocks `implement` / `qa` / `release` from trusting stale frozen truth
- re-enables execution only after requirement truth is refreshed and re-frozen

## Operator rule

Prefer:

- `beacon change ...`

Treat `beacon-change` as a router, not a new public Beacon stage.
Do not introduce a new Beacon primary command such as `change`, `revision`, or `hotfix`.

## Examples

- 适用例：
  - “这条 feature 已经 freeze 了，但 scope 现在必须改。”
  - “这是 hotfix，但在动实现前必须先更新 requirement truth。”
- 不适用例：
  - “我还没冻结，只是在继续澄清需求。” -> 应先去 requirement surfaces
