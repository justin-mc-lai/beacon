# Program-level lake driver: consume resume_action to auto-dispatch next lake (human release gate kept)

## Goal

Beacon 能计算海级（program）湖路由，但没有任何组件消费它——用户必须手动一个湖一个湖跑 goal。
本任务新增 **program-level driver 循环**：消费 `build_program_orchestrator_state` 的路由输出
（`current_lake / current_stage / resume_action`），自动派发下一湖的阶段工作
（truth → implement → qa），保留人工门（release 永远停；P0 review 阻断照旧）。

## Requirements

* R1 主入口：新模块 `beacon/utils/program_driver.py` + `beacon program drive <slug>` 子命令。
* R2 派发机制（方案 A）：每轮按 lake-stage 渲染 turn prompt（「当前湖+阶段→加载对应 skill」），
  经 bridge_cmd/spawn_fn 启动 host agent 执行；turn 结束从文件系统证据重算 orchestrator 路由再派下一轮。
* R3 证据驱动推进：只信 `_implementation_closed / _qa_closed / TRUTH_DONE` 等文件系统证据，
  不信任 driver 自身记忆；幂等可恢复，崩溃后重跑 drive 从当前证据状态继续。
* R4 停止条件：`await_human_gate`（release）、P0/user_decision_required、bridge/host 失败、
  `blocked_streak >= 3`、turn/budget 上限、feature-graph 无效或 lakes 缺失。停止时输出
  reason_code + recommended_command + resume_action（对齐 AC-039 resilient stop contract）。
* R5 次入口：goal run 终止时若 program 路由存在 next_lake，输出接管提示与 `beacon program drive`
  路由（提示级缝合，不在 goal 内部自动 spawn program driver）；`goal continue` 手动续跑行为不变。
* R6 依赖阻断：`await_upstream_lake_closure` 的下游湖不派发，按编排器现有顺序取第一个可动湖。
* R7 不改变现有单湖 goal 行为（回归红线）。

## Acceptance Criteria

* [ ] 多湖 fixture（A→B→C，B depends_on A）：lake1 truth→implement→qa closed 后自动进入 lake2 truth
* [ ] 到达 release 阶段即停，resume_action=await_human_gate，不自动放行（策略断言复用）
* [ ] B 的上游 A 未闭环时不派发 B（await_upstream_lake_closure）
* [ ] 中断后重新 drive 从当前证据状态恢复，不重做已闭环的湖/阶段
* [ ] blocked_streak≥3 或 budget 用尽 → 停止并输出 reason_code/resume_action
* [ ] goal run 终止且存在 next_lake 时输出接管提示；无 program 绑定时行为与现状一致
* [ ] 单元测试覆盖以上全部；lint + typecheck 通过

## Definition of Done

* 测试齐备（driver 推进/停止/依赖阻断/恢复/goal 提示钩子）
* lint + typecheck 绿
* CHANGELOG/docs 若有行为面变化则同步

## Technical Approach

* 复用原语：`goal_agent_driver.py` 的锁/budget/render_turn_prompt/resolve_bridge_command/spawn_fn/
  策略断言按 program 作用域适配（state/lock 以 program_slug 为键，不与 run_id 冲突）。
* 循环骨架：`program_drive_once()`（单 tick：算路由 → 渲染 prompt → spawn → 重算证据 → 更新状态）
  + `program_drive_loop()`（预算内循环），对齐 driver_run_once/driver_run_loop 形态。
* 状态落盘：`docs/beacon/<v>/programs/<slug>/program-drive-state.json`（orchestrate 已写
  program-run-state.json，drive 状态单独文件避免互踩）。
* stage→skill 映射：truth→beacon-gen-truth、implement→beacon-gen-implement、qa→beacon-eval-qa；
  release 阶段永不派发。

## Decision (ADR-lite)

**Context**: truth/implement/QA 都需要 AI agent 创作，纯 CLI 无法连续；需选派发机制与入口形态。
**Decision**: 方案 A（host-agent 轮转）+ 双入口（CLI `beacon program drive` 为主，
goal 终止接管提示为辅）+ MVP 含安全护栏（streak/budget）。
**Consequences**: 自动化程度最高；新增 program 级 driver 状态/锁/budget（复用单 run 原语）；
host agent 不可用时退化为停止并输出 recommended_command；并行多湖留待后续版本。

## Out of Scope

* 并行卫星多湖同时执行（main_star_satellite_pool 编排）——预留后续
* 自媒体项目侧材料补全（graph lakes 化 + program freeze）——另一个任务
* release 门自动化（永远不做）

## Technical Notes

* 关键文件：beacon/utils/program_orchestrator.py、beacon/utils/goal_agent_driver.py、
  beacon/utils/product_goal_runtime.py、beacon/commands/program.py、beacon/commands/goal.py
* 绑定前置：feature-graph.json 含 `lakes[]`+`depends_on` 且 program 已冻结（`_is_program_frozen`）
* 停止契约参考：loop-goal.md AC-039（reason_code + resume_action 必发）
