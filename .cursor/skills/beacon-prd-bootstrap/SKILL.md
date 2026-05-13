---
name: beacon-prd-bootstrap
description: Use when the user wants one-click requirement bootstrap (prd + user-story + test-case) with safe defaults (dry-run, strict context verify, no-overwrite).
---

# Beacon PRD Bootstrap

This optional skill reduces requirement startup friction while keeping Beacon safe-by-default.

## Use for

- one-click requirement bootstrap
- creating `prd + user-story + test-case` docs in one run
- low-risk initialization with strict guardrails

## Safety defaults

- strict context verify (`doctor verify-context --strict`)
- dry-run unless explicitly `--apply`
- no-overwrite by default
- lock + state artifact + rollback manifest

## Operator rule

Prefer the installed CLI (hidden command surface):

- `beacon prd-bootstrap run "<feature>" --desc "<需求描述>" --version <version> --dry-run --json`
- `beacon prd-bootstrap run "<feature>" --desc "<需求描述>" --version <version> --apply --allow-overwrite`

Optional repo-local shell wrappers under `skills/beacon/scripts/` remain supported only when that skill pack is vendored into the repo.

Do not treat this as Beacon mainline replacement.

## Examples

- 适用例：
  - “这个项目还没有 requirement 材料，我想先安全地 bootstrap 一套初始 PRD/user-story/test-case。”
  - “我要先 dry-run 看看 Beacon 会生成什么，再决定是否 apply。”
- 不适用例：
  - “这条 feature 已经有冻结 truth，只是要修改它。” -> 应优先去 `beacon-change`

## Cold-start anchors

- `prd-bootstrap` 解决的是 requirement 冷启动，不是主链替代。
- 默认应先安全、可验证、可回滚，再考虑 apply。
- 一旦项目已经进入正式 truth 演化，后续应回到 `prd / user-story / test-case / change` 主链。
