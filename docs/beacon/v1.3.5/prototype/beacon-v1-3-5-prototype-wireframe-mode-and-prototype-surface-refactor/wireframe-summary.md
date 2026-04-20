# 线框草图汇总：beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor

**Feature**: `beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor`
**Version**: `v1.3.5`
**Mode**: `wireframe`
**Generated At**: `2026-04-20T09:56:31Z`

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |
|---------|----------|------|--------|----------|
| `management-overview` | 管理总览 | Web, PC | P0 | 提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。 |
| `runtime-center` | 运行中心 | Web, PC | P1 | 只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。 |
| `material-viewer` | 项目物料查看器 | Web, PC | P1 | 按 version -> document type -> feature 提供只读 Markdown 浏览。 |
| `material-document-detail` | 物料文档详情 | Web, PC | P2 | 冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。 |

## 跳转关系图

```text
[material-viewer] -- 点击文档列表项 --> [material-document-detail]
[material-document-detail] -- 点击返回 --> [material-viewer]
```

## 冻结检查点
- [ ] 页面清单完整
- [ ] 跳转逻辑完整
- [ ] 单页线框可读
- [ ] 关联 requirement 可追踪
- [ ] 仅保留 wireframe freeze 语义
