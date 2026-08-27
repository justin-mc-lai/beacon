# Beacon Goal 事故档案（LoopX 蒸馏 + 本项目实例）

> 事故是证据，不是操作手册。每条含：现象、根因、修复契约。

## INC-001 outcome-floor 双布尔混淆

- 现象：`should_run=false` 与 `safe_bypass_allowed=true` 同在一个载荷，执行器走了 quiet skip。
- 根因：把“可否常规交付”与“是否有界恢复动作”混成一个布尔。
- 修复契约：`quota_should_run` 输出独立 `recovery_action`/`recovery_kind`（CAP-1）。

## INC-002 planner-review 退化假硬停

- 现象：无 diff 范围（base_ref 为空）的 fallback review 产出 P1 + user_decision_required，阻断整个流水线。
- 根因：低置信检查被当作自主 replan 级别，未降级为 advisory。
- 修复契约：低置信/退化检查降级为 advisory；阻断必须落成 gate 卡片（CAP-3、IP-013）。

## INC-003 monitor-only replan stall

- 现象：只监控不推进的回合导致循环假死。
- 根因：缺少“本次是否有界动作”的显式判断。
- 修复契约：quota should-run 顺序中 focus/evidence 等待显式返回 `decision=skip` + `recovery_action`（CAP-1）。

## INC-004 user-gate overreach

- 现象：agent 把局部决定扩成全局 user gate，或反之。
- 根因：gate 作用域未绑定 lane/todo。
- 修复契约：gate 卡片携带 decision_key 与作用域，per-todo capability gate 绑定现有 admission（CAP-2/3）。

## INC-005 standing-authorization reprompt

- 现象：长期授权被反复重新提问。
- 根因：决策未持久化缓存。
- 修复契约：decision_cache 按 decision_key 去重，同 key 不二次提问（CAP-3）。
