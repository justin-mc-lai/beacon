# P0 修复接缝图（已核实的精确位置）

> 2026-08-26 会话实证。行号基于 HEAD 2730678b。前序背景见
> `.trellis/tasks/archive/2026-08/08-25-program-lake-driver/research/program-driver-code-map.md`。

## S1 回执键位（读侧修复）

* 读：`beacon/utils/program_freeze_gate.py:26-45` `_lake_truth_promotion_complete(project_root, version, program_slug, lake_slug)`
  只查 `programs/<slug>/lakes/<lake_slug>/truth-promotion.json`。
* 调用方：同文件 `build_program_freeze_gate` L70-90（按 graph 行 slug 迭代）；
  `validate_authenticated_program_freeze`(L122+) 从 receipts 参数或 lakes 目录收集。
* 写：`beacon/utils/plan_goal_task_closure.py:2064-2130` `materialize_authenticated_lake_receipt`
  固定写 `lakes/<feature>/truth-promotion.json`（feature 键）。
* 修复方向：读侧同时接受 `<row-slug>` 与 `<row.feature_slug or row-slug>` 两个目录名。

## S2 闭环判定键（orchestrator）

* `beacon/utils/program_orchestrator.py:70-101`：
  `slug = feature_slug(row.slug or row.feature_slug)` 后用该 slug 查 `_implementation_closed/_qa_closed/_truth_frozen`。
* 对照组（已正确）：`beacon/utils/program_admission.py:100` `resolve_program_lake_topology`
  把 slug 和 feature_slug 都注册进 lake_by_slug。
* 实证：selfmedia 图行 slug=L0-monorepo-shell、feature_slug=monorepo-shell 时 orchestrate 全 False；
  slug 改为 feature 名后立即正确。证据查找键应为 `feature_slug(row.feature_slug or row.slug)`。

## S3 绑定诊断

* `beacon/utils/product_goal_runtime.py:756-765` `_goal_program_slug`：
  显式 program_slug → 否则 resolve_program_lake_topology；空串=未绑定，无任何输出。
* 附着点：`sync_program_orchestrator_route`（L767，run_goal_facade 尾部与 goal_continue_run 都会调）。
* 判定材料：programs 目录存在性、graph 是否有效（load_feature_graph errors）、
  行内是否有该 feature、`_is_program_frozen(program_admission.py:75)`。

## S4 完成即闭包

* complete 入口：`beacon/commands/goal.py:263` `complete` 命令 → runtime 的 complete 函数
  （grep `def .*complete|mark_complete` in beacon/utils/product_goal_runtime.py）；
  complete 已强制 verifier refs（`assert_complete_requires_verifier_policy`，goal_agent_driver.py:934）。
* 物化目标（缺失才写，全部引用真实路径）：
  * impl 标记候选位：`.machine/execution/implementation-summary-<slug>.json`
    （program_admission._implementation_closed 的第二候选）
  * qa 镜像：`.machine/execution/qa-acceptance-<slug>.json`
    （_qa_closed 第三类候选；verdict=passed 即认）
* QA verdict 在 goal stages 里可从 payload stages[qa].status/artifact 取。
* 禁止伪造：无 verifier refs / 无 scorecard 路径可引时跳过 + history 事件 `closure_backfill_skipped:<reason>`。

## 测试参考

* 新测试建议：tests/test_v1612_p0_audit_fixes.py
* 复用 fixture 风格：tests/test_v1612_program_lake_driver.py（spawn_fn 注入、临时项目树）
* 回归：test_v1612_program_lake_driver.py + test_program_plan_state_contract.py 必须保持绿
