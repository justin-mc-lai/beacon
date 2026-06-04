# 线框草图汇总：Beacon v1.3.10 prototype UX PRD closure and design-asset projection

**Feature**: `beacon-v1-3-10-prototype-ux-prd-closure-and-design-asset-projection`
**Version**: `v1.3.10`
**Mode**: `wireframe`
**Generated At**: `2026-05-01T02:43:14Z`

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |
|---------|----------|------|--------|----------|
| `home` | 首页 | Web, PC | P0 | 先回答经营判断，展示项目数、阻塞数、当前交付和介入点。 |
| `management-overview` | 管理总览 | Web, PC | P0 | 提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。 |
| `project-detail` | 项目详情 | Web, PC, App | P0 | 成为接力页，展示版本线、主 PRD、并行 PRD、需求闭环和推荐动作。 |
| `runtime-center` | 运行中心 | Web, PC | P1 | 只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。 |
| `recovery-diagnostics` | 恢复诊断 | Web, PC | P2 | 解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。 |
| `material-viewer` | 项目物料查看器 | Web, PC | P1 | 按 version -> document type -> feature 提供只读 Markdown 浏览。 |
| `material-document-detail` | 物料文档详情 | Web, PC | P2 | 冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。 |

## 跳转关系图

```text
[home] -- 点击项目组合入口 --> [management-overview]
[home] -- 点击重点项目卡片 --> [project-detail]
[management-overview] -- 点击项目行/卡片 --> [project-detail]
[management-overview] -- 点击首页导航 --> [home]
[project-detail] -- 点击运行态摘要 --> [runtime-center]
[project-detail] -- 点击恢复诊断入口 --> [recovery-diagnostics]
[project-detail] -- 点击文档查看入口 --> [material-viewer]
[project-detail] -- 点击返回 --> [management-overview]
[runtime-center] -- 点击返回 --> [project-detail]
[runtime-center] -- 点击面包屑 --> [management-overview]
[recovery-diagnostics] -- 点击返回 --> [project-detail]
[recovery-diagnostics] -- 点击运行态关联 --> [runtime-center]
[material-viewer] -- 点击返回 --> [project-detail]
[material-viewer] -- 点击文档列表项 --> [material-document-detail]
[material-document-detail] -- 点击返回 --> [material-viewer]
```

## 冻结检查点
- [ ] 页面清单完整
- [ ] 跳转逻辑完整
- [ ] 单页线框可读
- [ ] 关联 requirement 可追踪
- [ ] 仅保留 wireframe freeze 语义
