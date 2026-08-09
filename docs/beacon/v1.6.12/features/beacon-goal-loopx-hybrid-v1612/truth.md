---
slug: beacon-goal-loopx-hybrid-v1612
version: v1.6.12
status: frozen
language: zh
package_maturity: filled
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.12/features/beacon-goal-loopx-hybrid-v1612/truth.md
  user_story: docs/beacon/v1.6.12/features/beacon-goal-loopx-hybrid-v1612/truth.md
  test_case: docs/beacon/v1.6.12/features/beacon-goal-loopx-hybrid-v1612/tests.md
humanizer_applied: true
---

# Requirement Truth: beacon-goal-loopx-hybrid-v1612

## 人话

把 LoopX 最有价值的 5 项能力接入 beacon goal：1）配额内核（该不该跑、跑完才记账、恢复路径独立）；2）todo 所有权（认领/租约/继承，防抢防漏）；3）具体问题卡片（阻断=一张可回答的卡片，同问题不重复问）；4）有界回合预算（一轮一结、交接限 16 行）；5）模式目录与事故档案（教训变制度 + ready-score）。全程不改变 beacon 生命周期门禁，默认关闭、状态向后兼容，验收=canary 测试全绿。

- 能做： （待补）
- 不能做： （待补）
- 怎样算完： （待补）

## User Intent Snapshot

```yaml
lake_or_ocean: 湖（单 feature 一次煮干）
scope: 5 capability groups (CAP-1..CAP-5)
source: oss-sync/automation/autoresearch/loopx (91d8ed0)
runtime: v1.6.12 goal 编排层，不触碰生命周期门禁
```

## 用户旅程

1. 配额内核：goal 长程 run 按 should-run 决策跑，spend-once 记账
1. todo 所有权：多 agent 认领/租约/继承，per-todo 门禁
1. 具体 user gate：阻断变成 gate 卡片，决策缓存去重
1. 有界回合预算：driver 一轮一结，交接限 16 行/1800 字符
1. 模式目录与事故档案：IP 模式 + canary + ready-score + incidents
1. 护栏验收：生命周期门禁测试全绿，默认 off，状态向后兼容

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-01 | user | must | AC-001 | covered |
| INT-02 | user | must | AC-002 | covered |
| INT-03 | user | must | AC-003 | covered |
| INT-04 | user | must | AC-004 | covered |
| INT-05 | user | must | AC-005 | covered |
| INT-06 | user | must | AC-006 | covered |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | GoalQuota.should_run 按 健康门禁→operator gate→证据等待→focus 等待→配额 顺序决策；focus/evidence 等待不 spend；恢复动作独立布尔；quota=0 时 visible 且不可跑 |
| AC-002 | GoalTodo 支持 claim/release/supersede/update；同一 todo 重复 claim 被拒；supersede 保留历史；未 claim 不得执行 |
| AC-003 | UserGateCard 输出 question/context/resume_action；决策缓存去重（同 decision_key 不二次提问）；resolve 后记录答案 |
| AC-004 | TurnBudget 契约包含 choose→deliver→validate→writeback→spend；交接文本超 16 行/1800 字符被截断并记录；无 writeback 不 spend |
| AC-005 | patterns/ 目录含 IP-001/002/003/013/016 模式且每条配 canary 测试；ready-score 对 未冻结/未 admission/无配额 返回 blocked 明细；incidents/ 档案收录本次 5 条教训 |
| AC-006 | 生命周期门禁相关测试（truth/freeze/implement/qa/release/admission/双轴）全绿；新模块默认关闭（env 开启）；旧 goal 状态文件可读（新增字段可选） |

## Domain Model

| Entity | Key fields | Meaning |
|--------|------------|---------|
| GoalQuota | compute, window_hours, slot_minutes, ledger | 长程 run 的自动计算配额与 spend 账本 |
| GoalTodo | id, owner, claim, lease, successor, capability_gate | 任务级所有权与认领状态 |
| UserGateCard | decision_key, question, context, resume_action | 需要人判断的具体问题卡片 |
| TurnBudget | choose, deliver, validate, writeback, spend | 有界回合契约与交接预算 |
| PatternCanary | pattern_id, canary_test, status | 模式目录与 canary 绑定 |

## Domain FSM GoalLoopxHybrid

| State | From | Guard |
|-------|------|-------|
| quota_eligible | — | health gates pass, quota > 0 |
| turning | quota_eligible | turn selected within bound |
| quota_spent | turning | validated writeback accepted |
| todo_open | — | unclaimed |
| todo_claimed | todo_open | claim valid, lease bound |
| todo_superseded | todo_claimed | successor valid, history kept |
| gate_open | — | decision_key unanswered |
| gate_resolved | gate_open | answer recorded in cache |
| pattern_ready | pattern_pending | canary test green |
| ready | loop_ready | ready-score all checks pass |
| blocked | any non-terminal | gate unresolved / no claim / quota zero |

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| quota_eligible | turn_selected | health_and_quota_ok | turning | choose bounded segment |
| turning | validated_writeback | writeback_accepted | quota_spent | record spend once |
| todo_open | claim | unclaimed | todo_claimed | bind owner+lease |
| todo_claimed | supersede | successor_valid | todo_superseded | keep history |
| gate_open | resolve | answer_recorded | gate_resolved | cache decision |
| pattern_pending | canary_pass | test_green | pattern_ready | mark catalog ok |
| loop_ready | ready_score | all_checks_pass | ready | allow longrun start |

### invalid / illegal

- todo_open -> executing without claim
- gate_open -> next_stage without resolve
- turning -> quota_spent without validated writeback
- quota_zero -> running
- lifecycle_gate_change without user decision

## Illegal transitions

- GoalLoopxHybrid.todo_open → executing 未经过 claim
- GoalLoopxHybrid.gate_open → next_stage 未 resolve
- GoalLoopxHybrid.turning → quota_spent 无 validated writeback
- GoalLoopxHybrid.quota_zero → running（配额为 0 仍自动跑）
- GoalLoopxHybrid.lifecycle_gate_change 未经用户决策修改生命周期门禁

## Non-goals

- 不实现事件溯源状态/多 agent 工作台/Capability 注册框架（Deferral）
- 不改 truth/freeze/implement/qa/release 生命周期门禁
- 不整体搬运 LoopX 代码，只做接口对齐或语义蒸馏
- 不做 release 判定
