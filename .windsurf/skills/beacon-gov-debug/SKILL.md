---
name: beacon-gov-debug
description: Beacon v1.6.0 governor skill migrated from `beacon-debug-recovery`. Use when the user wants Beacon to help diagnose a blocked implementation or verification path and recover the workflow without confusing repair support with requirement or release authority.
---

# Beacon Governor Debug Recovery

## Overview

This is a support surface for blocked-path diagnosis and recovery.

It helps identify why implementation, QA, or release is stuck, then routes the repair back to the correct surface. It does not become a hidden replacement for `change`, `implement`, `qa`, or `release`.

## When to Use

- the workflow is blocked and the user needs recovery, not just status
- implementation or QA failures are noisy and the actual repair route is unclear
- the user wants debug-focused support before returning to the mainline
- the current problem feels like mixed context, broken assumptions, or runtime confusion

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not silently repair canonical truth
- if frozen truth itself must change, route to `beacon-gen-change`

## Workflow / Decision Loop

- identify the actual blocker family: truth drift, execution gap, verification gap, environment issue, or mixed context
- reduce the failure to the smallest actionable repair path
- separate what is broken from what is merely noisy
- route the result back to `beacon-gen-change`, `beacon-gen-implement`, `beacon-eval-qa`, `beacon-eval-release`, or `beacon-gov-doctor`

## Common Rationalizations

- “先多试几次，说不定就好了。” -> 不允许；先找 blocker family
- “卡住就把一切都当成 doctor 问题。” -> 不允许；先分 truth / execution / qa / environment
- “debug recovery 已经看明白了，直接在这里结案。” -> 不允许；修复仍要回主链

## Red Flags

- blocker family 没分清，修复建议过宽
- 把环境/上下文噪声错当成产品结论
- 用 debug support 代替正式 QA 或 release verdict

## Verification

- 输出能明确指出 blocker family 和下一跳
- noisy symptoms 与真实 repair path 被分离
- 若卡住原因属于 truth drift，会显式 route back

## Evidence Produced

- blocker diagnosis
- repair route summary
- recovery recommendation

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can stop blind thrashing by reducing the failure to the right repair surface

## Examples

- 适用例：
  - “这轮实现/QA 卡住了，但我不确定该回改需求、修代码，还是修环境。”
  - “我想先把失败面诊断清楚，再回主链继续。”
- 不适用例：
  - “我要正式执行 doctor 修复环境。” -> 应去 `beacon-gov-doctor`
  - “我要正式给 release verdict。” -> 应去 `beacon-eval-release`

## Cold-start anchors

- `debug-recovery` 的职责是分诊和回路由，不是隐藏主流程。
- 修复路径要尽量小，不要把所有异常都糊成一个大问题。
- 看明白原因之后，仍然要回正确的主链 surface 处理。


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## GIT_ADMISSION (mandatory — Tier A/B when version+feature known)

Before ANY repo write or implement/qa/release route:
1. `beacon workspace admit --project-root . --version <v> --feature <slug> --json`
2. If status != pass → STOP; show reason_codes; do NOT edit files
3. Set cwd to worktree_path from payload
4. Do NOT git checkout elsewhere to "fix" branch
5. When admission is soft-skipped (`require_workspace_admission=false`), still verify `current_branch == resolved target_branch` before repo writes (R5 UD-024)

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-debug-recovery` -> `beacon-gov-debug`。
- 主要作用：阻断恢复。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-debug-recovery` -> `beacon-gov-debug`。
- 主要作用：阻断恢复。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
