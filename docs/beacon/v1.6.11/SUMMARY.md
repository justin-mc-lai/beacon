# Beacon v1.6.11 — Plan/Goal Task Closure

## 定位

`v1.6.11` 是 planning-only 交付线，运行时仍为 `v1.6.10`。本版本把“口头大目标”从计划建议升级为可追溯、可委派、真实 worktree 隔离、可人工纠偏、可取消重排、可验证收敛的 Program。

## Program

- slug: `beacon-plan-goal-task-closure-v1611`
- status: `program_frozen`
- baseline commit: `30b9adffc8ec5442a7691a88faf64a251d97b98f`
- truth canonical: `main`
- lakes: L0–L8
- freeze result: 九个湖均通过 Truth Review Gate 并冻结为 `R1`；Program freeze gate 已通过

## 核心结果

1. 大目标先绑定主分支代码、冻结 Truth、测试与历史 Change 基线。
2. 意图递归拆全，再生成 Before→After Change 与状态机差异。
3. Journey/AC/状态差异编译成可承载 100+ 节点的原子任务 DAG；任务数量不是 KPI。
4. 每条任务路径持续聚合进度、反馈、阻塞、取消、替代与剩余工作。
5. 注水或偏差进入人工门禁；人工可继续、改写、拆分、替换或取消。
6. 取消任务后重算 ready set；必要依赖无替代时阻断路径。
7. Goal 仅在全部意图、路径、AC、状态、任务和证据闭环后完成。
8. 子代理只产出 finding/patch/evidence，主代理保留状态转换与 Goal 完成权；无宿主并行能力时诚实降级。
9. Truth 只在 `main` 冻结；direct/goal/team/ralph 的实现任务统一经过真实 git worktree admission。
10. 内部任务、偏差和重排状态不扩张 1+6 公共生命周期，关键出口统一写 `agent_trace.v1`。
11. 旧 package/ledger 不兼容读取；保留旧冻结真相作为 lineage，并通过新 revision 重新冻结向前迁移。

## 入口

- Program manifest: `docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/program-manifest.md`
- Feature graph: `docs/beacon/v1.6.11/programs/beacon-plan-goal-task-closure-v1611/feature-graph.json`
- Change: `docs/beacon/v1.6.11/change/beacon-plan-goal-task-closure-v1611.md`
