# Execution Note: workflow memory lifecycle 对齐（v1.0.1）

## 本次文档补充项

1. 扩展 workflow 闭环阶段为 6 阶段（不含 release）
2. 新增 release 专用 memory 校验函数需求
3. 修复 `compute_memory_metrics` run_id 默认选择策略
4. 同步更新 workflow_memory / gate_memory_closure 相关 fixture 需求
5. 新增 lifecycle 进度解析与 `workflow continue` 自动续跑能力
6. 修正 `workflow start --auto=false` 行为，避免“未执行却写入 stage_started/context”的失真

## 目标结果

- memory 指标与真实 workflow run 对齐
- release 事件不再污染 workflow 闭环判定
- gate release 校验有专用 profile，减少误阻断与假通过
- 支持按 `version + feature (+ run_id)` 解析生命周期进度
- 可根据 `next_stage` 自动续跑单阶段或全链路补齐到 verify

## 关联文档

- `research/workflow-memory-stage-expansion-analysis.md`
- `prd/workflow-memory-lifecycle-alignment.md`
- `user-story/workflow-memory-lifecycle-alignment.md`
- `qa/test-cases/workflow-memory-lifecycle-alignment.md`
- `qa/test-cases/workflow-memory-lifecycle-alignment.ac-test-matrix.json`
- `tests/test_workflow_continue_progress.py`
