# Beacon 全量测试失败机器分类（2026-08-06）

> 数据来源：`pytest --lf --junitxml` 重跑缓存失败用例（703 failed + 1 error = 704）。pytest 缓存中的 745 条含 41 条失效条目（`--lf` 自动 deselected），实际可复现失败为 **704**。

## 总览

| 版本线 | 失败数 |
|---|---:|
| v1.0x | 1 |
| v1.1x | 127 |
| v1.2x | 4 |
| v1.3x | 177 |
| v1.4x | 228 |
| v1.5x | 34 |
| v1.6x | 93 |
| v2.x | 4 |
| other | 36 |

- 历史线（v1.0–v1.5）合计 **571**，占 **81%**；v1.6x 93（13%）；v2.x 4；通用/其他 36。
- 版本线解析按文件命名（v1611→v1.6.11、v1411→v1.4.11、v13010→v1.3.10），非按 4 位数字大小。

## 原因类别 × 处置

| 类别 | 数量 | 含义 | 建议处置 |
|---|---:|---|---|
| cli_exit_code_gate_blocked | 124 | CLI 退出码 2/1（原期望 0）——新 gate fail-closed（workspace admission / freeze 前置 / package 形状等） | 更新断言到现行规范 |
| missing_docs_material | 80 | 仓库 docs/beacon/<v>/ 下文件缺失——旧 split docs / machine 工件已删除或迁移 | 换现行 fixture；旧线可归档 |
| state_semantics_changed | 78 | 状态/原因码语义变化（assert 'X' == 'Y'） | 更新断言到现行规范 |
| legacy_cutover_required | 67 | legacy cutover preflight 阻断 v1.x 旧线 release/qa——新 runtime 要求先 truth-cutover | 更新断言到现行规范 |
| text_or_surface_drift | 50 | 命令输出 / skill 文本 / 状态面板文案断言过期 | 更新断言到现行规范 |
| missing_skill_file | 50 | 已删除的旧 skill 文件（using-beacon / change-refreeze / gen-truth / loop-goal / eval-qa 等） | 更新断言；若行为已废除则归档/删除 |
| prototype_requires_truth | 43 | prototype 冻结前必须已有 user-story/prd/test-case truth（新规则） | 更新断言到现行规范 |
| boolean_expectation_drift | 41 | 布尔断言（exists()/is_file()/flag）与现行行为不一致 | 更新断言到现行规范 |
| missing_file_boolean | 36 | exists()/is_file() 断言期望文件存在但已不存在 | 换现行 fixture；旧线可归档 |
| skill_surface_drift | 21 | skill 注册/安装面变化（Scheme A 1+6、installer 脚本、skill 清单） | 更新断言；若行为已废除则归档/删除 |
| count_or_field_drift | 16 | 计数/字段值变化（0 vs N、empty vs filled） | 更新断言到现行规范 |
| cascade_tmp_fixture_missing | 15 | tmp fixture 文件缺失——通常是上游 CLI 先被 gate 阻断的级联失败 | 先修上游 gate 导致的级联 |
| user_story_missing | 15 | 旧 split 路径 user story 缺失——新 package 形状不再写旧路径 | 换现行 feature-package fixture |
| surface_diff | 14 | 列表/集合/字典表面 diff（command surface、evidence 集合等） | 更新断言到现行规范 |
| authority_model_changed | 10 | 权威模型变化（feature_package_authoritative / authoritative_ready / reserved_fail_closed） | 更新断言到现行规范 |
| schema_key_removed | 9 | payload schema 字段被移除（machine_json_role、content_source_exists） | 更新断言到现行规范 |
| payload_surface_diff | 6 | JSON payload 整体 diff（多行断言消息） | 更新断言到现行规范 |
| version_pin_drift | 5 | 版本固定值过期（1.6.9→1.6.11、1.6.10→1.6.11 等） | 更新断言到现行规范 |
| sequence_missing | 5 | 序列迭代提前结束（上游写入缺失） | 先修上游 gate 导致的级联 |
| branch_name_drift | 4 | program/worktree 分支命名规则变化（beacon/v0.0.12 → beacon/v0.0.12/<slug>） | 更新断言到现行规范 |
| missing_mirror_doc | 3 | 旧版本执行文档镜像缺失（version-semantics / artifact-language contract） | 补齐现行线镜像，或把旧线标记为 frozen lineage 不再要求镜像 |
| dual_axis_guard_block | 3 | 本仓库新双轴守卫拦截（fixture 在外部项目上用了 docs==runtime） | fixture 改用产品线版本或 beacon_self 设置 |
| task_binding_shape_required | 3 | package 形状要求 task ac=/evidence= 绑定（v1.6.3+ 规则） | 换现行 feature-package fixture |
| test_harness_error | 2 | 测试自身收集/夹具问题（helper 被 pytest 收集、stderr 未捕获） | 修测试自身（重命名被收集的 helper / 修 stderr 捕获） |
| docs_current_drift | 2 | README/当前发布线文档断言过期 | 更新断言到现行规范 |
| output_format_drift | 1 | 输出格式细节变化（profile=full、推荐命令等） | 更新断言到现行规范 |
| legacy_behavior_removed | 1 | 旧路径/旧行为被显式移除（如 legacy split 路径不再写） | 更新断言；若行为已废除则归档/删除 |

## 建议处置汇总

| 处置 | 数量 |
|---|---:|
| 更新断言到现行规范 | 466 |
| 换现行 fixture；旧线可归档 | 103 |
| 更新断言；若行为已废除则归档/删除 | 72 |
| 换现行 feature-package fixture | 31 |
| 先修上游 gate 导致的级联 | 20 |
| v2 planning 线，暂缓或按新计划重查 | 4 |
| 补齐现行线镜像，或把旧线标记为 frozen lineage 不再要求镜像 | 3 |
| fixture 改用产品线版本或 beacon_self 设置 | 3 |
| 修测试自身（重命名被收集的 helper / 修 stderr 捕获） | 2 |

## 失败最集中的文件（Top 25）

| 文件 | 失败数 | 主要类别 |
|---|---:|---|
| tests/test_v131_cognitive_load_gates.py | 21 | cli_exit_code_gate_blocked(18), schema_key_removed(2) |
| tests/test_v135_prototype_projection_consistency.py | 20 | prototype_requires_truth(18), surface_diff(1) |
| tests/test_v112_implementation_plan_runtime.py | 19 | cli_exit_code_gate_blocked(19) |
| tests/test_v114_implement_command.py | 17 | legacy_cutover_required(17) |
| tests/test_v1411_beacon_design_human_subskills_closure.py | 15 | missing_file_boolean(14), text_or_surface_drift(1) |
| tests/test_v151_truth_map.py | 15 | state_semantics_changed(7), authority_model_changed(6) |
| tests/test_v142_test_contract_governance.py | 14 | count_or_field_drift(5), sequence_missing(3) |
| tests/test_v147_meta_protocol_and_support_surfaces.py | 13 | missing_skill_file(7), text_or_surface_drift(6) |
| tests/test_v110_runtime_closure.py | 11 | legacy_cutover_required(6), cli_exit_code_gate_blocked(4) |
| tests/test_v140_prd_bootstrap_unified_closure.py | 11 | cli_exit_code_gate_blocked(8), state_semantics_changed(2) |
| tests/test_v162_delivery_program_branch_r5.py | 11 | state_semantics_changed(5), branch_name_drift(4) |
| tests/test_v13010_requirement_package_gates.py | 10 | cli_exit_code_gate_blocked(10) |
| tests/test_v130_implement_team_surface.py | 10 | legacy_cutover_required(6), authority_model_changed(3) |
| tests/test_v1311_board_launcher.py | 10 | prototype_requires_truth(10) |
| tests/test_v147_change_refreeze_human_skill_route.py | 10 | missing_skill_file(7), skill_surface_drift(3) |
| tests/test_v112_prototype_feature_contract.py | 9 | missing_file_boolean(6), prototype_requires_truth(1) |
| tests/test_v140_branch_blocked_payload_consistency.py | 9 | legacy_cutover_required(4), state_semantics_changed(3) |
| tests/test_v167_goal_agent_driver.py | 9 | missing_docs_material(5), boolean_expectation_drift(3) |
| tests/test_v110_requirement_materials.py | 8 | missing_docs_material(5), missing_file_boolean(3) |
| tests/test_v119_feature_qa_closure.py | 8 | legacy_cutover_required(6), cli_exit_code_gate_blocked(2) |
| tests/test_v147_change_refreeze_one_shot.py | 8 | legacy_cutover_required(5), missing_skill_file(1) |
| tests/test_v115_materials_contract.py | 7 | missing_docs_material(6), missing_file_boolean(1) |
| tests/test_v136_delivery_kernel_read_model.py | 7 | text_or_surface_drift(3), schema_key_removed(3) |
| tests/test_v146_anti_drift_skill_contracts.py | 7 | missing_skill_file(6), count_or_field_drift(1) |
| tests/test_v150_feature_package.py | 7 | missing_docs_material(3), state_semantics_changed(2) |

## 需要特别注意的 4 组

1. **dual_axis_guard_block（3）**：`tests/test_v1611_plan_goal_task_closure.py` 的 CLI 用例在外部 tmp 项目上用 `docs/beacon/v1.6.11` + `--version v1.6.11`，被本次 #14 修复的新守卫正确拦截。它们原本就失败（HEAD 上原因不同），修复方式是把 fixture 改成产品线版本或 beacon_self 形态。
2. **test_harness_error（2）**：`beacon/utils/test_contract_governance.py::test_contract_index_path` 是 helper 函数因 `test_` 前缀被 pytest 收集（fixture 缺失）；另一个是 click stderr 未捕获。属真实测试缺陷，应立即修。
3. **missing_mirror_doc（3）**：v1.3.0/v1.4.11 的 version-semantics / artifact-language 镜像缺失。按“旧 docs 走新 runtime 重新梳理并冻结”决策，应明确旧线镜像策略（补齐或冻结免检）。
4. **v2.x（4）**：loom/skill-score 等 planning 线能力未落地，测试先行导致的失败，建议 defer。

## 使用方式

- 机器明细：`beacon-test-drift-classification-2026-08-06.csv`（704 行：nodeid / file / band / category / disposition / error_type / excerpt）。
- 结构化 JSON：`beacon-test-drift-classification-2026-08-06.json`。
- 迁移 feature 可直接按 `disposition` 分组：先处理 fix_harness / fix_fixture_dual_axis / sync_or_freeze_mirror，再按文件批量 migrate。
