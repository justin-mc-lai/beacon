---
name: beacon-gov-doctor
description: Beacon v1.6.0 governor skill migrated from `beacon-doctor`. Use when the user needs Beacon to repair context, sync materials, diagnose environment or package drift, or restore the workflow to a usable state through Beacon's current support surface.
---

# Beacon Governor Doctor

## Overview

This skill routes repair and diagnostics through Beacon's `doctor` support surface.

It diagnoses context, package, version, and environment drift, then routes recovery back to the usable workflow. It does not become part of the default mainline.

## When to Use

- context repair
- material sync
- environment diagnostics
- package / skill drift checks
- upgrade and recovery support

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not substitute for requirement or release surfaces once the environment is healthy

## Workflow / Decision Loop

- diagnose context, package, runtime, or version drift
- identify repair route and required commands
- restore the project to a state where truth/execution/gate surfaces can run normally

## Common Rationalizations

- “doctor 都能修，那就不用看 requirement/gate 了。” -> 不允许；doctor 只修运行条件
- “材料有点漂，先忽略继续做。” -> 不允许；doctor 应先修正上下文真相
- “既然是诊断面，可以顺手改正式 requirement。” -> 不允许；diagnostics 不改 canonical truth

## Red Flags

- context/material drift 已知存在，却继续执行主链
- package/version drift 没有显式 reason code
- `doctor` 被当成常驻主流程步骤

## Verification

- repair output explains the drift source and recovery route
- workflow can re-enter the proper truth/execution/gate surface after repair
- doctor actions remain support-only and do not mutate requirement truth semantics

## Evidence Produced

- diagnostics payload
- repair recommendation
- package/version/context drift findings

## State Updated

- diagnostic state and repair artifacts

## Gate Impact

- no direct product gate verdict
- may block workflow entry until context or version integrity is restored

## Operator rule

Prefer:

- `beacon doctor ...`
- or `beacon doctor ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor ...`)

Use doctor only when blocked, misaligned, or repairing package integrity. It is a support surface, not part of the main 6-command delivery loop.

## Examples

- 适用例：
  - “Beacon 上下文好像漂了，先帮我诊断和修复。”
  - “版本、材料或 skill 包可能没同步，先看 doctor 怎么说。”
- 不适用例：
  - “我只是想知道主链下一步该做什么。” -> 应优先去 `beacon-gov-help` 或 `beacon-gov-status`


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
6. (implement only) Before writing implementation, merge `truth_canonical` into the development branch so implementation bases on canonical frozen truth

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-doctor` -> `beacon-gov-doctor`。
- 主要作用：上下文和环境修复。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-doctor` -> `beacon-gov-doctor`。
- 主要作用：上下文和环境修复。
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
