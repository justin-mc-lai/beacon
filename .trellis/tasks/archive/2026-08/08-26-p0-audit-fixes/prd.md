# Fix P0 audit findings: unify lake keying, binding diagnostics, evidence closure

## Goal

修复 v1.6.12 全面审查确认的 4 个严重问题（S1-S4）。它们同属一类根因：
**键约定不一致 + 静默失败 + 交付事实与机器证据两张皮**，全部在自媒体项目实战中实证。
修完后 `program freeze/orchestrate/drive` 对任意合法命名约定都能正确工作，且绑定失败可诊断。

## Requirements

* **R1 (S1) 回执发现双路径**：`_lake_truth_promotion_complete`（program_freeze_gate.py:26）读回执时
  同时尝试 `lakes/<row-slug>/truth-promotion.json` 与 `lakes/<feature-slug>/truth-promotion.json`
  （row 的 feature_slug 字段，缺省=row slug），任一存在且 status=complete 即通过。写侧不变。
* **R2 (S2) 闭环判定统一用 feature_slug**：`build_program_orchestrator_state`
  （program_orchestrator.py:70-101）对每湖计算 impl/qa 闭包与 truth 冻结时，
  证据查找键 = `feature_slug(row.feature_slug or row.slug)`；行内展示仍保留原 slug。
  与 `resolve_program_lake_topology` 的语义对齐（它已双注册）。
* **R3 (S3) 绑定诊断**：goal facade 路径上 `_goal_program_slug` 返回空且
  `docs/beacon/<v>/programs/` 目录存在时，向 payload 附加
  `program_binding = {status:"unbound", reason_code, checked:[...], hint}`，
  reason_code ∈ {programs_dir_missing(不附), program_not_frozen, feature_not_in_graph,
  graph_invalid}。纯增量字段；已绑定时附 `{status:"bound", program_slug}`。
  不改变任何现有字段/路由行为。
* **R4 (S4) 完成即闭包**：goal run 标记 complete 且 verifier refs 在场时
  （complete 本就强制 verifier），若 `.machine/execution/implementation-summary-<slug>.json`
  缺失则物化之（status=passed，引用 run_id + verifier refs + 真实 evidence ref）；
  QA 同理：goal stages 里 qa verdict=pass 时若 qa-acceptance 文件缺失则镜像一份
  （引用 QA scorecard/evidence 路径）。所有物化必须引用真实产物路径，禁止无中生有；
  无法引用真实证据时跳过并记 history 事件 `closure_backfill_skipped:<reason>`。
* **R5 回归红线**：现有单湖 goal 行为、selfmedia 已落位的图/回执数据（两处目录并存）继续工作；
  新增测试全部通过；全量失败集不得超出 HEAD 基线。

## Acceptance Criteria

* [ ] 图行 slug≠feature 名时（如 slug=L1-x, feature_slug=x）：orchestrate 能读到按 feature 名存放的
      impl/qa/truth-promotion 证据并正确闭环（R1+R2 合并验证）
* [ ] 回执只存在于 lakes/<feature>/ 时 freeze 通过；只存在于 lakes/<row-slug>/ 时也通过
* [ ] 未冻结 program / feature 不在图中 / 图无效 三种场景下 goal payload 出现对应 reason_code 的
      program_binding 诊断；正常绑定显示 bound；无 programs 目录时不附加
* [ ] goal complete（带 verifier refs）后 implementation-summary 自动在场；
      无真实可引证据时跳过并留 history 事件，绝不伪造
* [ ] 单元测试覆盖以上全部 + selfmedia 双目录并存回归；pytest 目标文件绿，全量失败集 ≤ HEAD 基线
* [ ] lint/typecheck 等价验证（compileall + import 检查）

## Definition of Done

* 测试齐备且绿；CHANGELOG 1.6.12 Added/Fixed 补条目
* code-spec 更新（program-driver.md 或新条目记录 canonical key 约定）

## Out of Scope

* W 级警告项（CHANGELOG 排序、bak 清理、drive 字段 null、trace 加富等）
* LAKE_ORDER_V1611 等 v1611 专属流程的键迁移
* 并行湖执行

## Technical Notes

* S1 现场：plan_goal_task_closure.py:2106 写 lakes/<feature>/；program_freeze_gate.py:29 读 lakes/<lake-slug>/
* S2 现场：orchestrate 用 l0-monorepo-shell 查证据 → 全 False（本会话实证）
* S3 现场：pgr-*.json 全部 program_slug=None 无诊断（本会话实证）
* S4 现场：7 湖 release 合并完成但 .machine 证据缺失 → orchestrate 全红
