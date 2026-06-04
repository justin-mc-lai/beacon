# 线框草图汇总：Beacon Operator Workbench And Board Launcher

**Feature**: `beacon-operator-workbench-and-board-launcher`
**Version**: `v1.3.11`
**Mode**: `wireframe`
**Generated At**: `2026-05-02T15:13:51Z`

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |
|---------|----------|------|--------|----------|
| `recovery-diagnostics` | 恢复诊断 | Web, PC | P2 | 解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。 |
| `portfolio-board` | 项目组合看板 | Web, PC | P1 | 汇总当前版本线的 feature 状态、阻塞分布与建议波次，支持先判断先处理哪一组事项。 |
| `execution-board` | 执行看板 | Web, PC | P0 | 先暴露当前运行状态、阻塞项与下一步动作，而不是先展示全量运行历史。 |
| `feature-detail` | 功能详情 | Web, PC | P1 | 聚合单个 feature 的基线、依赖、当前状态与建议动作，支持判断是否继续实现或先回修。 |
| `run-detail` | 运行详情 | Web, PC | P1 | 聚合单次运行的状态时间线、写入范围、证据与建议动作，避免操作者在散落材料中自行拼接上下文。 |
| `review-surface` | 验收面 | Web, PC | P1 | 集中展示差异入口、验收证据与发布提示，支持判断是否放行或回修。 |

## 跳转关系图

```text
[recovery-diagnostics] -- 点击跳转 --> [portfolio-board]
[portfolio-board] -- 点击跳转 --> [execution-board]
[execution-board] -- 点击跳转 --> [feature-detail]
[feature-detail] -- 点击跳转 --> [run-detail]
[run-detail] -- 点击跳转 --> [review-surface]
```

## 冻结检查点
- [ ] 页面清单完整
- [ ] 跳转逻辑完整
- [ ] 单页线框可读
- [ ] 关联 requirement 可追踪
- [ ] 仅保留 wireframe freeze 语义
