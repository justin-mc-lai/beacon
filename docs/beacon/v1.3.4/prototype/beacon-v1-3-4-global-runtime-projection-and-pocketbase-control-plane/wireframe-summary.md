# 线框草图汇总：beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane

**Feature**: `beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane`
**Version**: `v1.3.4`
**Mode**: `wireframe`
**Generated At**: `2026-04-20T07:49:04Z`

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |
|---------|----------|------|--------|----------|
| `home` | 首页 | Web, PC | P0 | 先回答经营判断，展示项目数、阻塞数、当前交付和介入点。 |
| `management-overview` | 管理总览 | Web, PC | P0 | 提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。 |
| `project-detail` | 项目详情 | Web, PC, App | P0 | 成为接力页，展示版本线、主 PRD、并行 PRD、需求闭环和推荐动作。 |
| `runtime-center` | 运行中心 | Web, PC | P1 | 只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。 |
| `recovery-diagnostics` | 恢复诊断 | Web, PC | P2 | 解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。 |

## 跳转关系图

```text
[home] -- 点击项目组合入口 --> [management-overview]
[home] -- 点击重点项目卡片 --> [project-detail]
[management-overview] -- 点击项目行/卡片 --> [project-detail]
[management-overview] -- 点击首页导航 --> [home]
[project-detail] -- 点击运行态摘要 --> [runtime-center]
[project-detail] -- 点击恢复诊断入口 --> [recovery-diagnostics]
[project-detail] -- 点击返回 --> [management-overview]
[runtime-center] -- 点击返回 --> [project-detail]
[recovery-diagnostics] -- 点击返回 --> [project-detail]
```

## 冻结检查点
- [ ] 页面清单完整
- [ ] 跳转逻辑完整
- [ ] 单页线框可读
- [ ] 关联 requirement 可追踪
- [ ] 仅保留 wireframe freeze 语义
