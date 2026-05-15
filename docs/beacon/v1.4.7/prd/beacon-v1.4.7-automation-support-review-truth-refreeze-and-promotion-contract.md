# PRD: Beacon v1.4.7 automation support-review, truth-refreeze, and promotion contract

**Feature**: `beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract`  
**Version**: `v1.4.7`  
**Date**: `2026-05-15`  
**Status**: `freeze-ready`  
**Track**: `automation-runtime-second-slice + support-review-routing + truth-refreeze-barrier + promotion-proof-hooks`  
**Scenario**: `runtime-facing_automation_needs_support_and_truth-pressure_contracts_before_more_autonomy`

## Context

- Global boundaries:
  - `docs/beacon/global-boundaries.md`
- Current runtime baseline:
  - `docs/beacon/v1.4.6/SUMMARY.md`
- Existing `v1.4.7` automation slice:
  - `docs/beacon/v1.4.7/prd/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
  - `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
  - `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
- Research closure:
  - `docs/beacon/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`
  - especially:
    - `11.2 Missing Runtime Contract`
    - `11.4 CEO Feasibility Verdict`
- Runtime implementation surfaces:
  - `beacon/utils/automation_runtime.py`
  - `beacon/utils/automation_feedback.py`
  - `beacon/commands/implement.py`

## 1. Overview

`v1.4.7` 的 first automation slice 已经把 Beacon automation 从 queue helper 推进到 bounded QA/implement closure kernel。

但真正阻止这条线继续落地的，不再是 queue safety，而是以下四类 runtime-facing 缺口：

1. repeated structural failure 还没有正式的 `support_review / deep` route contract
2. requirement meaning 受压后，还没有正式的 `truth_recompiled_pending` barrier
3. scenario discovery 还没有正式拆分成 `closure_supplement` 与 `promotion_candidate`
4. release/promotion readiness 还缺少可检查的 proof hooks

因此本次 `change` 需要冻结一个更窄但更硬的 second slice：

> 让 automation 能表达 support-review、truth pressure、scenario discovery 与 promotion proof，但仍然 fail-closed，不给 automation 真相写入主权。

## 2. 问题

### 2.1 repeated repair 一旦进入结构性问题，当前 runtime 只能停在人类经验层

当前 first slice 只能表达：

- QA -> implement
- implement -> QA
- human escalation
- release-ready

但当 QA 发现的问题更像：

- 需要 `deep` 进一步分析
- 多轮 repair 后仍不收敛
- 看起来像 requirement meaning pressure

runtime 还没有正式 contract 去表达：

- 为什么现在该走 `support_review`
- `deep` 出来的结论是实现修复，还是 truth refreeze
- 什么时候已经达到 repeat cap，需要停止夜间自迭代

### 2.2 requirement meaning 一旦变化，当前 runtime 还缺少 recompile barrier

如果 support-review / deep 发现：

- 当前缺口不是单纯实现 defect
- 而是 `prd / user-story / test-case / requirement_clarity / freeze` 这条链需要重新编译

Beacon 不能直接回 implement。

当前缺的是一个正式 barrier：

- `truth_recompiled_pending=true`
- 明确列出必须重新编译的 downstream truth package
- implement 在 barrier 清除前必须 fail-closed

### 2.3 scenario discovery 现在还没有 current-closure 与 future-promotion 的分流

automation 在真实项目里会不断发现新场景，但这些场景不全都属于同一类：

- 有些会改变当前 feature 的 closure 定义，属于 `closure_supplement`
- 有些只是值得沉淀为后续机会，属于 `promotion_candidate`

如果不正式拆分：

- 当前 closure 会被 promotion noise 污染
- 或者未来的高价值发现会被误判为当前必须阻断

### 2.4 没有 promotion-grade proof hooks，就很难判断“该不该升级成更正式的 change”

即便 scenario discovery 被正式分类，如果没有 proof hooks，系统仍然无法清楚表达：

- 这是一个只有局部 observation 的想法
- 还是一个已经具备 acceptance/real-project proof 支撑、值得升级成正式 `change` 的候选

Beacon 需要可见的 promotion proof 投影，但这类 proof 只能辅助 route，不能替代 truth gate。

## 3. 目标

1. 为 automation 加入正式的 `support_review` runtime route
2. 把 `deep` 的 bounded outcome 收成 machine-readable contract
3. 在 truth pressure 出现后，正式冻结 `truth_recompiled_pending` barrier
4. 把 scenario discovery 拆成 `closure_supplement` 与 `promotion_candidate`
5. 给 runtime 增加 promotion-grade proof hooks，辅助判断是否值得升级成正式 change
6. 让 `implement` 在 truth-refreeze / truth-recompile 未清理前 fail-closed

## 4. 设计原则

### 4.1 support-review 仍是 support surface，不是新 lifecycle stage

runtime 可以 route 到 `support_review`，但不能把它升格成新的主链 stage。

### 4.2 `deep` 只提供 bounded outcome，不直接写 canonical truth

`deep` 可以输出：

- `deep_exit_no_truth_delta`
- `support_review_deep_route_implement`
- `support_review_deep_route_truth_refreeze`
- `support_review_deep_repeat_cap_reached`

但它不能自动重写 `prd / user-story / test-case`。

### 4.3 truth pressure 必须通过 barrier 显式收口

只要发现 requirement meaning delta：

- 不得自动恢复 implement
- 不得把 local fix 当成 closure
- 必须先过 `truth_recompiled_pending` barrier

### 4.4 promotion candidate 只进非 canonical sink

`promotion_candidate` 是 future change 候选，不是当前 feature truth。

它必须进入非 canonical runtime sink，并通过 proof hooks 表达强弱，而不是直接写回 requirement truth。

### 4.5 proof hooks 只辅助 route，不定义 release verdict

promotion proof 可以说明：

- acceptance kit 是否存在
- all layers 是否通过
- real-project proof 是否存在

但 release verdict 仍属于正式 release gate。

## 5. 范围

### In scope

- `support_review` next-route taxonomy
- `deep` bounded exit contract
- `truth_recompiled_pending` barrier
- truth recompile target list
- scenario discovery classification sink
- promotion proof projection hooks
- implement preflight 对 `support_review / change_refreeze / truth_recompiled_pending` 的 fail-closed gating

### Out of scope

- 自动执行 `deep`
- 自动执行 `change/refreeze`
- 自动重写 requirement package
- 自动 promotion 到 canonical truth
- 自动 release orchestration

## 6. 功能需求

### FR-001 Beacon 必须冻结 `support_review` route contract

automation runtime 必须能正式表达：

- `next_route=support_review`
- `terminal_signal=qa_route_support_review`
- support-review executor metadata

至少要能绑定：

- `required`
- `executor`
- `reason`
- `repeat_count`

### FR-002 Beacon 必须冻结 `deep` bounded outcome contract

support-review / deep 的机器输出至少必须区分：

- `deep_exit_no_truth_delta`
- `support_review_deep_route_implement`
- `support_review_deep_route_truth_refreeze`
- `support_review_deep_repeat_cap_reached`

并据此路由到：

- `implement`
- `change_refreeze`
- `human`

### FR-003 Beacon 必须冻结 `truth_recompiled_pending` barrier

当 runtime 已判断 requirement meaning 受压，且 refreeze 后下游真相包尚未重新编译时，必须显式写入：

- `truth_recompiled_pending=true`
- `truth_recompile_gate.required=true`
- `truth_recompile_gate.targets`

默认 targets 至少包含：

- `user-story`
- `test-case`
- `requirement_clarity`
- `freeze`

### FR-004 Beacon 必须让 `implement` 对 truth barrier fail-closed

当 feature automation runtime 存在以下任一条件时，`implement` 不能继续执行：

- `next_route=support_review`
- `next_route=change_refreeze`
- `truth_recompiled_pending=true`

系统必须返回可解释的 blocked reason。

### FR-005 Beacon 必须冻结 scenario discovery classification sink

automation runtime 必须能把 scenario discovery 至少拆分为：

- `closure_supplement`
- `promotion_candidate`

并显式记录：

- `requirement_meaning_delta`
- `finding_count`
- `evidence_refs`
- `requires_truth_reopen`

### FR-006 Beacon 必须在 closure supplement 与 promotion candidate 之间 fail-closed 分流

当 scenario discovery 属于：

- `closure_supplement`
- 或 `requirement_meaning_delta=true`

runtime 必须 route 到 `change_refreeze`。

当 scenario discovery 仅属于：

- `promotion_candidate`
- 且 `requirement_meaning_delta=false`

runtime 不得自动污染当前 canonical truth，可保留当前 route，并把候选沉到 runtime sink。

### FR-007 Beacon 必须增加 promotion-grade proof hooks

runtime 必须能投影 promotion proof，至少说明：

- acceptance kit 是否存在
- acceptance layers 是否全部通过
- real-project proof 是否存在
- 当前缺失哪些 proof hooks

### FR-008 Beacon 必须保持 support plane 边界

即便 second slice 完成，automation 仍然只能：

- classify
- route
- explain
- block

它仍然不能：

- write canonical truth
- execute refreeze autonomously
- convert promotion candidate into current closure truth
- claim autonomous end-to-end lifecycle ownership

## 7. 验收标准

1. QA 可显式产出 `support_review` route
2. support-review outcome 可显式 route 到 `implement / change_refreeze / human`
3. truth recompile barrier 可正式写入并在 implement preflight 中阻断
4. promotion candidate 与 closure supplement 被清楚分流
5. promotion proof hooks 有明确 machine projection
6. 所有新增 contract 都仍满足 Beacon 的 truth / gate / support 边界
