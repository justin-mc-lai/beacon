# Beacon v1.3.12 Requirement Convergence Contract

## 目标

定义 `prd / user-story / test-case / brainstorm / change / help` 之间的统一收敛编排 contract。

它不新增公开 stage，不改写 frozen truth，只定义：

- 需要哪些字段
- 谁产生这些字段
- 谁消费这些字段
- 什么时候路由到 `brainstorm`
- 什么时候路由到 `change`
- 什么时候回到 `user-story / test-case`
- 什么时候允许 re-freeze / revalidate

## Contract 字段

### 1. `requirement_gap_digest`

由 `prd` 或 `help` 产出。

最小字段：

- `feature`
- `version`
- `revision_id`
- `source_truth_ref`
- `gap_id`
- `gap_type`
- `gap_severity`
- `gap_summary`
- `gap_dimensions`
- `missing_dimensions`
- `blocked_subgates`
- `candidate_targets`
- `human_followup_needed`
- `recommended_route`

### 2. `brainstorm_hint`

由 `help` 基于 `requirement_completeness` 和 `change_loop` 产出。

最小字段：

- `feature`
- `version`
- `trigger_reason`
- `focus_areas`
- `open_questions`
- `recommended_mode`
- `recommended_output`
- `recommended_route`

### 3. `supplement_task`

由 `brainstorm` 或 `help` 路由给 `user-story / test-case`。

最小字段：

- `feature`
- `version`
- `target_artifact`
- `writeback_target`
- `candidate_kind`
- `candidate_payload`
- `source_truth_ref`
- `rationale`
- `confidence`
- `human_decision`
- `audit_trail_required`

### 4. `change_loop`

由 `help` 产出，专门处理 frozen truth 变化。

最小字段：

- `intent`
- `recommended`
- `route`
- `reason`
- `ladder`
- `project_metadata_context`
- `reopen_command`
- `metadata_verify_command`
- `metadata_update_command`

### 5. `re_freeze_transaction`

由 `user-story / test-case` 接受补料后进入。

最小字段：

- `feature`
- `version`
- `revision_id`
- `accepted_candidates`
- `rejected_candidates`
- `deferred_candidates`
- `writeback_targets`
- `machine_mirror_paths`
- `refreeze_required`
- `revalidate_required`

## 路由规则

### Rule 1: PRD 缺口优先进入 `brainstorm`

如果 gap 主要表现为：

- 角色差异不完整
- 状态机不完整
- 边界 / 异常 / 恢复路径不完整
- 风险与覆盖族群不完整

则 `help` 应推荐：

- `beacon-brainstorm`

而不是直接进入 `change`。

### Rule 2: frozen truth 变化必须进入 `change`

如果 gap 会改变：

- PRD promised surface
- story boundary
- test-case coverage ownership
- revision / freeze baseline

则 `help` 应推荐：

- `beacon-change`

### Rule 3: coverage gap 进入 `user-story / test-case`

如果 gap 只是：

- 需要补故事
- 需要补测试族群
- 需要补 human decision trail

则 `help` 应推荐：

- `beacon-user-story`
- `beacon-test-case`

### Rule 4: human supplement 后必须 re-freeze

接受候选后必须进入：

- `decision log`
- `writeback projection`
- `truth refreeze`
- `revalidate`

不能只改 markdown。

### Rule 5: delivery 只能读取 completeness

`prototype / implement / qa / release` 只能读取：

- `requirement_completeness`
- `human_loop_handoff`
- `change_loop`

不能反向改写 requirement truth。

## 责任边界

- `prd`: 定义 truth anchor 和 gap 约束
- `brainstorm`: 生成 gap 候选和收敛建议
- `help`: 决定下一跳路由
- `change`: 处理 frozen truth 变更
- `user-story`: 补齐 story gap
- `test-case`: 补齐 coverage gap

## 统一闭环

```text
PRD
-> requirement_gap_digest
-> help
-> brainstorm or change or supplement task
-> user-story / test-case writeback
-> re-freeze
-> revalidate
-> help/status/board visibility
```

## 冻结约束

- 该 contract 只定义编排规则，不新增 public stage。
- 该 contract 只约束路由和字段，不改写 PRD / story / test-case frozen truth。
- 若任一环节缺失 machine-readable trail，则必须 fail-closed。

