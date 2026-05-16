---
name: beacon-change-refreeze
description: Use when the user asks for change 一键冻结, change refreeze, 重新冻结, refreeze-chain, or post-freeze requirement closure through the existing governed Beacon change refreeze transaction.
---

# Beacon Change Refreeze

## Overview

`beacon-change-refreeze` is the stable human-facing route for accepted post-freeze requirement refreeze intent.

It is a narrow change-family support skill. It makes one-shot refreeze discoverable for natural language requests, then routes to the existing governed machine path:

```bash
beacon change ... --refreeze-chain
```

It does not create a second refreeze implementation.

## When to Use

- change 一键冻结
- change refreeze
- 重新冻结
- refreeze-chain
- post-freeze requirement closure
- a `deep` or support-surface finding has been accepted and must enter governed change/refreeze closure

## Boundary

- not a lifecycle stage
- not a truth source
- not a gate source
- does not write canonical PRD, user-story, or test-case truth directly
- does not execute implementation, QA, release, or direct canonical truth writes
- does not replace `beacon-change`; it routes into the existing `beacon change ... --refreeze-chain` transaction

## Workflow / Decision Loop

- confirm the intent is accepted post-freeze refreeze closure, not early requirement drafting
- route the operator to `beacon change ... --refreeze-chain`
- keep the closure chain explicit: `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`
- fail closed back to `beacon-change` when required truth surfaces are missing or clarity blocks
- route onward only after the refreeze transaction reports complete

## Common Rationalizations

- “有了 `beacon-change-refreeze`，它就是一个新的 stage。” -> 不允许；它只是 change-family route surface.
- “skill 已命中，可以直接写 truth。” -> 不允许；truth still belongs to PRD, user-story, test-case, requirement clarity, and freeze.
- “refreeze 完就可以自动 implement / QA / release。” -> 不允许；it only unlocks the safe next route after the transaction completes.

## Red Flags

- operator wants to change accepted scope but no PRD/user-story/test-case refresh exists
- refreeze intent is used to bypass requirement clarity
- support findings are treated as canonical truth before adoption
- implementation resumes while `refreeze_status` is blocked

## Verification

- the requested route maps to `beacon change ... --refreeze-chain`
- the chain remains `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`
- any blocked transaction stays in `beacon-change`
- no implementation, QA, release, or direct truth write is claimed by this skill

## Evidence Produced

- route explanation for the operator
- expected refreeze command
- pointer to the change refreeze transaction artifacts produced by the CLI

## State Updated

- no state is updated by the skill itself
- state changes only occur through `beacon change ... --refreeze-chain`

## Gate Impact

- no direct gate verdict
- can unblock downstream `implement`, `qa`, or `release` only after the existing refreeze transaction completes
- blocked or partial refreeze remains a `beacon-change` problem

## Operator Rule

Prefer:

```bash
beacon change "<feature>" --project . --version v1.4.7 --reason "<accepted change>" --refreeze-chain
```

If the feature is already reopened, use the same route. The transaction must close the active refreshed requirement package before execution resumes.

## Examples

- 适用例：
  - “change 后帮我一键重新冻结。”
  - “deep 的这个 finding 已经接受，走 change/refreeze 闭环。”
  - “这个 feature 的 PRD/user-story/test-case 都改好了，现在 refreeze。”
- 不适用例：
  - “我还在想需求怎么写。” -> 应先去 `beacon-prd` / `beacon-user-story` / `beacon-test-case`
  - “我想直接跑实现。” -> 应先确认 refreeze transaction 已 complete，再去 `beacon-implement`

## Cold-start Anchors

- `beacon-change-refreeze` 是稳定人类入口，不是新主链段。
- 唯一机器执行路径是 `beacon change ... --refreeze-chain`。
- refreeze 只重新闭合 requirement truth；不执行 implement、QA 或 release。
