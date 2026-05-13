---
name: beacon-toolkit-branch-governance
description: Use when the user wants a human-readable git branch/worktree governance view or verification through Beacon's doctor support surface.
---

# Beacon Toolkit Branch Governance

This skill routes branch-governance inspection through Beacon's `doctor branch-governance` support surface.

## Use for

- inspect the resolved branch-governance template for a version
- show the branch flow diagram, current position, and recommended next action
- verify whether the governance contract is currently blocked
- review evidence-contract requirements before entering `implement`

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon doctor branch-governance show ...`
- `beacon doctor branch-governance verify ...`
- or `beacon doctor branch-governance ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor branch-governance ...`)

Default expectations:

- treat `doctor branch-governance` as the human-facing deterministic git governance surface
- keep project-level writes on the canonical metadata transaction path
- let `implement` consume the same projected contract instead of maintaining a second truth

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the governance result into the main Beacon workflow.

## Examples

- 适用例：
  - “我想知道当前 branch/worktree 治理位置和下一步 git 动作建议。”
  - “进入 implement 前，先确认 branch governance 有没有阻断。”
- 不适用例：
  - “我现在已经明确要开始实现功能本身。” -> branch 检查结束后应回 `beacon-implement`

## Cold-start anchors

- `branch-governance` 解决的是 git/worktree 治理可见性，不是 feature 执行本身。
- 它应和 `implement` 共享同一投影契约，而不是维护第二套真相。
- 这个 surface 可以阻断进入执行，但不能替代执行入口。
