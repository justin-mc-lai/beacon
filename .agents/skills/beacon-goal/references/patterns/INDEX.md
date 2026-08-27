# Beacon Goal 交互模式目录（LoopX 蒸馏）

> 来源：`oss-sync/automation/autoresearch/loopx/docs/concepts/interaction-pattern-catalog.md`
> 每条模式必须配 canary 测试；模式编号稳定，只增不改。

## IP-001 Bounded Delivery（有界交付）

- 触发：配额 eligible 且无硬门禁阻断。
- 行为：选择一段有界工作 → 交付或阻塞 → 聚焦校验 → 持久 writeback → 只 spend 一次。
- canary_test：`tests/test_v1612_goal_budget.py`、`tests/test_v1612_goal_quota.py`

## IP-002 Blocked Priority With Safe Fallback（优先级阻塞 + 安全回退）

- 触发：主交付面被高优先级门禁阻塞，但存在经过审计的有界恢复动作。
- 行为：`should_run=false` 与 `recovery_action=true` 分开表达，执行器走恢复分支而不是安静跳过。
- canary_test：`tests/test_v1612_goal_quota.py::test_focus_wait_does_not_spend_and_recovery_is_separate_boolean`

## IP-003 Scoped Gate With Safe Fallback（带安全回退的作用域门禁）

- 触发：一条 lane 被 user gate 阻塞。
- 行为：gate 只阻塞对应 lane；独立的恢复动作不得绕过 gate。
- canary_test：`tests/test_v1612_goal_gates.py::test_unresolved_gate_blocks_next_stage`

## IP-013 Advisory Dreaming vs Autonomous Replan（建议性设想 vs 自主改计划）

- 触发：planner/检查输出低置信或退化（fallback）。
- 行为：低置信/无 diff 范围的检查结果降级为 advisory（不阻断、并入下一回合）；
  只有经过 review/freeze 门禁的意图才允许自主 replan。
- canary_test：`tests/test_v1612_goal_gates.py`（gate 卡片 + 决策缓存）

## IP-016 Task Lease Claim（任务租约认领）

- 触发：多 agent 对等协作。
- 行为：todo 认领绑定 owner + lease；重复认领被拒；supersede 保留历史；
  未认领不执行。
- canary_test：`tests/test_v1612_goal_todos.py`

## 维护规则

- 新增模式必须同时新增 canary 测试与 `tests.md` TC 行。
- 模式引用 LoopX 原编号以保持可追溯；蒸馏语义以本目录为准。
