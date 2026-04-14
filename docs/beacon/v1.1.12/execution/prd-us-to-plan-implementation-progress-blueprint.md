# PRD/US-to-Plan Implementation Progress Blueprint

## 1. Objective

将 `v1.1.12` 中 PRD / user story / test-case 到 implement 的过渡，收敛成可执行的运行时蓝图。

目标不是再加一个新的 workflow stage，而是把：

- 需求编译
- 计划校验
- 任务级进度
- writeback 回流
- status/help 解释

统一进一条正式闭环。

---

## 2. First-principles Order

实现顺序必须遵循：

```text
version truth
→ project mode
→ frozen revision / baseline truth
→ prd-us-to-plan compiler
→ implementation plan artifact
→ plan gate
→ implement execution
→ task progress writeback
→ status / help / review consumption
```

不是：

```text
user-story / prd path
→ 直接丢给 implement prompt
→ 跑完再临时拼 task progress
```

---

## 3. Target Runtime Architecture

```text
version truth state machine
→ project mode + profile gate
→ frozen revision / baseline gate
→ prd-us-to-plan compiler
   ├─ source refs collector
   ├─ task mapper
   ├─ AC / TEST traceability mapper
   └─ implementation-plan writer
→ plan gate
→ implement runner / adapter execution
→ task progress writeback
→ workflow / status / help / review consumption
```

核心原则：

1. 先确认这是不是可执行的需求基线
2. 再确认计划是否存在且已对齐
3. 再进入 runner / adapter 执行
4. 最后才把结果写回 story / revision / plan / status

---

## 4. Artifact Model

建议新增或正式化以下 machine-readable / human-readable artifacts：

```text
docs/beacon/<version>/execution/
  implementation-plan-<feature>.md

docs/beacon/<version>/.machine/execution/
  implementation-plan-<feature>.json
  implementation-plan-<feature>.progress.json

.beacon/implement/<run_id>/
  plan-preflight.json
  task-progress.json
  state.json
  summary.json
```

### 4.1 implementation-plan-<feature>.json

至少表达：

- `plan_id`
- `feature`
- `version`
- `revision_id`
- `baseline_hash`
- `plan_hash`
- `source_refs`
- `workstreams`
- `tasks`

### 4.2 task-progress.json

至少表达：

- `plan_id`
- `run_id`
- `feature`
- `version`
- `revision_id`
- `task_states`
- `counts`
- `blocked_task_ids`
- `next_task_id`
- `updated_at`

### 4.3 plan-preflight.json

至少表达：

- `status`
- `blocked`
- `reason_code`
- `expected_plan`
- `expected_revision_id`
- `baseline_hash`
- `current_version`
- `recommended_command`

---

## 5. Module Change Plan

## 5.1 `beacon/commands/implement.py`

目标：

- 在 runner 解析前加入 plan gate
- 在 implement 状态里写入 plan truth
- 在 status 视图中暴露 plan-level progress

最小改造：

- 在 `run_implement_stage()` 早期读取 implementation plan
- 若 plan 缺失 / baseline 不匹配 / revision 不匹配，直接 blocked
- 在成功执行后写入 task progress summary
- `status()` 读取 plan artifact 与 task progress artifact

产出：

- `plan_preflight`
- `plan_progress`
- `task_progress_path`

## 5.2 `beacon/utils/writeback.py`

目标：

- writeback 不只更新 story / revision
- 还要更新 plan task 状态

最小改造：

- `record_implementation_writeback()` 增加 plan progress 写回
- `record_verification_writeback()` 增加 task verify 回写
- `record_acceptance_writeback()` 保留 acceptance 语义，但不覆盖 plan truth

产出：

- `implementation_plan_progress`
- `task_evidence_refs`
- `task_changed_files`

## 5.3 `beacon/utils/workflow_memory.py`

目标：

- workflow 保留阶段级进度
- 但 implement 可见 task-level progress

最小改造：

- `compute_workflow_progress()` 继续负责 stage-level
- 新增 plan-aware progress 汇总读取
- `closure_complete` 不再伪装 task-level truth

产出：

- `workflow_stage_progress`
- `implementation_plan_progress_summary`

## 5.4 `beacon/utils/help_support.py`

目标：

- help/status 必须先解释“当前正在跑哪张 plan”
- 再解释“下一步该走哪个 task / stage”

最小改造：

- `_next_step()` 在 implement / verify / review 推荐前先看 plan truth
- `build_help_payload()` 增加：
  - `current_plan_id`
  - `plan_status`
  - `next_task`
  - `blocked_task_ids`
  - `task_progress_summary`

blocked reason 应新增：

- `implementation_plan_missing`
- `implementation_plan_revision_mismatch`
- `implementation_plan_baseline_mismatch`
- `implementation_task_blocked`

## 5.5 `beacon/utils/story_state.py`

目标：

- story / revision 仍是需求与修订真值
- 但不能再承担 plan 进度的唯一来源

最小改造：

- 保留 AC / TEST item 状态
- 增加 plan 绑定引用字段
- 避免 story item 状态与 plan task 状态互相覆盖

---

## 6. Execution Flow

### 6.1 Plan compile flow

```text
read user-story
read prd
read qa/test-cases
read frozen revision
read baseline hash
→ compile tasks
→ map AC / TEST refs
→ write implementation plan
```

### 6.2 Implement flow

```text
resolve version truth
→ resolve frozen baseline
→ load plan artifact
→ plan gate
→ resolve runner / adapter
→ execute implementation
→ write task progress
→ write run summary
```

### 6.3 Status/help flow

```text
resolve version truth
→ resolve project mode
→ resolve plan truth
→ resolve workflow stage truth
→ render next task / next stage / blocked reason
```

---

## 7. Runtime Guardrails

1. plan 缺失时不得进入真正 runner
2. baseline / revision 不匹配时不得伪装成“可实现”
3. task-level blocked 不得被 run-level success 覆盖
4. story/revision writeback 不得吞掉 plan truth
5. stage-level workflow 进度保留，但不能取代 plan-level 进度

---

## 8. Real closure questions

完成这条线后，Beacon 必须能回答：

1. 当前实现对应哪张 plan
2. plan 的来源是哪些 PRD / user-story / TEST
3. 当前卡在哪个 task
4. 哪个 task 对应哪个 AC / TEST
5. implement run 是在什么 baseline 上执行的
6. writeback 是否已经回流到 plan truth

---

## 9. Success Standard

这条线完成时，Beacon 应能稳定做到：

1. 在 implement 前把需求编译成 implementation plan
2. 在 runner 启动前阻断 plan 缺失或 baseline 不一致
3. 在实现过程中记录 task-level progress
4. 在 writeback 中回流 task / AC / TEST traceability
5. 在 status/help 中展示 plan truth，而不只是 run summary
6. 不破坏现有 implement / workflow / gate 语义

