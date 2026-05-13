---
name: beacon-change
description: Use when the user wants to adjust a frozen Beacon feature, reopen its revision, refresh requirement materials, and return to implementation/QA/release through the existing mainline.
---

# Beacon Change

This skill is the host-visible router for post-freeze requirement change loops.

It does not create a new Beacon primary stage.
It routes the user back into the existing requirement truth and delivery chain.

## Use for

- frozen feature scope change
- requirement supplement after freeze
- reopen + requirement revise + re-freeze
- fix / hotfix that must first update requirement truth
- revised delivery and release recheck preparation

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
