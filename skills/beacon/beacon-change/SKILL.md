---
name: beacon-change
description: Use when the user wants to adjust a frozen Beacon feature, reopen its revision, refresh requirement materials, and return to implementation/QA/release through the existing mainline.
---

# Beacon Change

This skill is the host-visible router for post-freeze requirement change loops.

It preserves the current `v1.3.7` public runtime surface while aligning change refresh work to the `v1.3.7` host-native runtime line.

It does not create a new Beacon primary stage.
It routes the user back into the existing requirement truth and delivery chain.

## Use for

- frozen feature scope change
- requirement supplement after freeze
- reopen + requirement revise + re-freeze
- fix / hotfix that must first update requirement truth
- revised delivery and release recheck preparation

## Operator rule

Prefer this flow:

- `beacon-change`
- `reopen`
- `prd revise`
- `user-story refresh`
- `test-case refresh`
- `prototype refresh`
- `freeze`
- `implement fix`
- `qa delta-run`
- `release recheck`

Treat `beacon-change` as a router, not a new public Beacon stage.
Do not introduce a new Beacon primary command such as `change`, `revision`, or `hotfix`.
