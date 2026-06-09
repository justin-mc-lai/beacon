---
name: beacon-pln-deep
description: Beacon v1.6.0 planner skill migrated from `beacon-deep`. Use when Beacon should run deep analysis as a support surface for complex business risk, test-delta derivation, cross-stage routing, and release supplement closure without adding a new lifecycle stage.
---

# Beacon Planner Deep Analysis

## Overview

This skill routes deep analysis work through Beacon's `deep` support surface.

`deep` analyzes frozen requirement truth, derives routeable findings and test deltas, and writes support evidence. It does not become a parallel truth or QA stage.
It is not a primary lifecycle stage.

## When to Use

- high-risk trigger and low-risk skip decisions
- state-machine, fact-source, invariant, and consistency-chain analysis
- deep test delta derivation before QA
- structural QA feedback review when P0/P1/P2 defects expose modeling gaps
- release supplement evidence for deep closure, waiver, backlog, or skip decisions

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen PRD, user-story, or test-case truth directly

## Workflow / Decision Loop

- analyze frozen truth and structural evidence
- derive findings, deltas, and route decisions
- route accepted requirement gaps to `beacon-gen-refreeze` for governed `change/refreeze`
- route acceptance gaps to `test-case`
- route implementation gaps to `implement`
- route QA evidence gaps to supplemental `qa`
- route release risks to closure, waiver, or backlog decision

## Common Rationalizations

- “deep 发现的问题可以直接写回 truth。” -> 不允许；只能 route
- “这已经相当于做完 QA 了。” -> 不允许；deep 不代替验证
- “既然是高风险分析，deep 自己可以下最终 gate verdict。” -> 不允许；只能投影回 gate 影响

## Red Flags

- findings 没有 route target
- 结论只停在分析文字，没有 test delta / risk / closure impact
- `deep` 被当成新 stage，而不是 support analysis surface

## Verification

- findings are classifiable and routeable
- test delta and release supplement outputs are auditable
- accepted deep conclusions still need existing truth/execution/gate surfaces to close the loop

## Evidence Produced

- deep analysis report
- state machine report
- deep test delta
- risk register
- deep loop trace
- deep closure brief
- optional skip evidence

## State Updated

- deep transaction/read model artifacts

## Gate Impact

- no direct gate verdict
- can increase or reduce gate confidence by binding findings back to `test-case`, `qa`, or `release`

## Operator rule

Prefer:

- `beacon deep run ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh deep run ...`

Keep toolkit internals hidden behind `beacon-pln-deep` unless the user explicitly asks for implementation details.

## Examples

- 适用例：
  - “这条 feature 风险很高，我想先做更深的状态机、约束链和测试增量分析。”
  - “QA 暴露了结构性问题，我想知道这到底该回 `change`、`test-case`，还是 `implement`。”
  - “release 前需要补一层深分析证据，但不想新增主 stage。”
- 不适用例：
  - “我已经明确要改 frozen truth。” -> 应回 `beacon-gen-change`
  - “我现在只是要正式执行验证。” -> 应优先去 `beacon-eval-qa`

## Cold-start anchors

- `deep` 是 support analysis surface，不是新的主流程阶段。
- 它的价值是产出可路由的发现、delta 和 closure evidence，不是直接改 truth 或代替 QA。
- deep 结论只有在被现有 truth/execution/release surface 吸收后，才真正进入主闭环。


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 planner skill。
禁止调用 implementation/generator/evaluator/release 类 skill。
禁止写代码、搭脚手架、修改 package truth、修改 `.machine/`、给 QA/release verdict。
你的唯一产出是 research/planning artifact、gap/risk 分析、湖/海判断和 route recommendation。
如需进入 truth/change/refreeze/generate/evaluate，必须停止并路由，等待用户确认。

## v1.6.0 Harness Migration

- Harness：`planner`。
- 来源迁移：`beacon-deep` -> `beacon-pln-deep`。
- 主要作用：复杂状态、风险与测试差量分析。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-deep` -> `beacon-pln-deep`。
- 主要作用：复杂状态、风险与测试差量分析。
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
