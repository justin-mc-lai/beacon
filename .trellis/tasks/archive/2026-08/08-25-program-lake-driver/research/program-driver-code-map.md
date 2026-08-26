# Program driver code map（已核实的代码事实）

> 本文件是 2026-08-25 会话内对 beacon 代码库的实地分析结论，供 implement/check sub-agent 直接引用。
> 所有路径均 repo-root 相对，行号以当日 HEAD（bd4d1be5）为准。

## 1. 路由源（已存在，勿重写）

`beacon/utils/program_orchestrator.py`

* `build_program_orchestrator_state(project_root, *, version, program_slug) -> dict`（L32）
  * 读 `docs/beacon/<v>/programs/<slug>/feature-graph.json` 的 `lakes[]` 行
    （`_lake_rows`，program_admission.py，读 `slug/feature_slug/depends_on/status/truth_status`）。
  * 每湖判定：truth frozen（`TRUTH_DONE = {frozen, accepted, closed, complete, completed, release_accepted}`，L16）
    → deps 闭合（`_implementation_closed` + `_qa_closed`）→ impl closed → qa closed → release/complete。
  * 输出字段：`current_lake / current_stage / passed_lakes / blocked_lakes / next_lake /
    resume_action / sea_completion_status / next_action / recommended_command / lakes[]`。
  * `resume_action ∈ {prepare_next_lake_truth, run_lake_implementation, run_lake_qa, await_human_gate, program_complete}`。
  * blocked 仅当 `reason_code == await_upstream_lake_closure`（L175-177）。
* `write_program_orchestrator_state` → `docs/beacon/<v>/programs/<slug>/program-run-state.json`（L28）。

## 2. 绑定链（goal ↔ program）

`beacon/utils/product_goal_runtime.py`

* `_goal_program_slug(root, payload)`（L756）：payload 显式 `program_slug` 优先，
  否则 `resolve_program_lake_topology`（beacon/utils/program_admission.py:100）按 feature 反查。
  * 反查硬条件：resolved version 下存在 programs 目录 + feature 在 graph/freeze 的 lakes 行里 +
    `_is_program_frozen`（freeze `status=frozen` 或 manifest/graph `program_plan_frozen=true`
    或 `lake_package_truth_frozen=true`）。任一不满足 → 返回空 → goal 不挂编排器。
* `sync_program_orchestrator_route`（L767）：把编排状态附到 goal payload
  （`program_orchestrator/resume_action/next_action/recommended_command/current_lake`）并持久化 run-state。
* `run_goal_facade`（L1352）：唯一调用 `create_goal_run` 处（L1396）；末尾调
  sync_program_orchestrator_route。**全库无任何消费者读 next_lake 开新 run —— 这就是要补的缺口。**
* `goal_continue_run`（L806）：刷新路由后 tick 一步。

## 3. 可复用的单 run longrun driver 原语

`beacon/utils/goal_agent_driver.py`

* 状态/锁：`driver_state_path`（L122）/`driver_lock_path`（L126）/`acquire_driver_lock`（L173,
  含 pid 存活检测 `_pid_alive` L220）/`release_driver_lock`（L204）。均为 run_id 键控——program 版需换成 program_slug 键控。
* 预算：`default_budget`（L115）/`_env_int`（L105）。
* 派发：`resolve_bridge_command`（L230）/`render_turn_prompt`（L281）/`write_turn_prompt`（L331）/
  `_default_spawn`（subprocess，L349）/`spawn_fn` 注入点。
* 循环：`is_goal_terminal`（L338）/`driver_run_once`（L522，prompt→spawn→end→requeue/halt，"Never completes/releases"）/
  `driver_run_loop`（L832）/`driver_start|status|stop`（L360/471/486）。
* 策略断言：`assert_no_auto_release_policy`（L929）/`assert_complete_requires_verifier_policy`（L934）。
* attach 入口：`attach_longrun_to_goal_run`（product_goal_runtime.py 调用，L1440）。

## 4. CLI 面

* `beacon program` app：beacon/commands/program.py —— 已有 `validate-graph`(L27) /
  `guard-sea-single-lake`(L57) / `freeze`(L85) / `orchestrate`(L165)。新 `drive` 子命令加在这里。
* `beacon goal` app：beacon/commands/goal.py —— `run`(L63)/`continue`(L211)/`driver`(L420) 等。
  goal 终止接管提示改在 run_goal_facade 终止路径 / recommended_next 组装处。
* stage→skill 映射参考 loop-goal.md Skill Routing Matrix：
  truth→beacon-gen-truth、implement→beacon-gen-implement、qa→beacon-eval-qa、release→人工门。

## 5. 测试布局

* 单 run driver 参考：tests/test_v167_goal_agent_driver.py、tests/test_v200_goal_durable_longrun.py
* program 相关：tests/test_program_plan_cli.py、tests/test_program_plan_state_contract.py、
  tests/test_v161_program_plan_release_gate.py
* 新测试建议命名：tests/test_v1612_program_lake_driver.py（跟随 v1612 前缀惯例）

## 6. 自媒体项目实证（缺口现场，非本仓库）

`.beacon/state/product-goal/pgr-*.json` 4 个 run 全部 `program_slug=None/orchestrator=None/scope.mode=lake`；
其 feature-graph.json 是极简结构（无 lakes 字段）、manifest 未冻结 —— 绑定前置不满足的实例。

## 7. 约束红线

* release 永远人工门（HARD GATE）；P0/user_decision_required 必停。
* governor/driver 不自证交付：只派发 harness，不自写 truth/QA verdict。
* 停止契约对齐 AC-039：每次停止必发 reason_code + resume_action。
