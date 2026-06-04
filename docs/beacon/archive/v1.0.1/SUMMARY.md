# Beacon v1.0.1 版本摘要

## 版本目标

v1.0.1 聚焦**测试可信性增强**：

1. 降低 UI 自动化“假通过”概率
2. 提升关键动作（login/register/browse/submit-form）证据可信度
3. 让 AC→TC→Evidence 链路更可审计
4. 校准 workflow memory 生命周期，降低 metrics/gate 判定失真
5. 基于 memory lifecycle 自动识别 next_stage 并续跑工作流

## 本版本新增文档

- `research/ui-test-false-pass-and-coverage-research.md`
- `research/workflow-memory-stage-expansion-analysis.md`
- `user-story/ui-test-false-pass-hardening.md`
- `user-story/workflow-memory-lifecycle-alignment.md`
- `prd/ui-test-false-pass-hardening.md`
- `prd/workflow-memory-lifecycle-alignment.md`
- `qa/test-cases/ui-test-false-pass-hardening.md`
- `qa/test-cases/ui-test-false-pass-hardening.ac-test-matrix.json`
- `qa/test-cases/workflow-memory-lifecycle-alignment.md`
- `qa/test-cases/workflow-memory-lifecycle-alignment.ac-test-matrix.json`
- `execution/workflow-memory-lifecycle-adjustment.md`
- `execution/gate-rules-memory-lifecycle-v101.json`

## 状态

- 文档状态：Draft
- 预研更新时间：2026-03-03
