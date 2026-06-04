# 线框草图汇总：beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor

**Feature**: `beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor`
**Version**: `v1.3.5`
**Mode**: `wireframe`
**Generated At**: `2026-04-20T19:15:34Z`

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |
|---------|----------|------|--------|----------|
| `management-overview` | 管理总览 | Web, PC | P0 | 提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。 |
| `runtime-center` | 运行中心 | Web, PC | P1 | 只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。 |
| `material-viewer` | 项目物料查看器 | Web, PC | P1 | 按 version -> document type -> feature 提供只读 Markdown 浏览。 |
| `page-01-d1bbcc5c` | 不要求当前阶段生成好看的高保真页面 | Web, PC | P1 | 冻结 `不要求当前阶段生成好看的高保真页面` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `beacon-ui` | 不直接重构 Beacon UI 产品本身的页面字段 | Web, PC | P1 | 冻结 `不直接重构 Beacon UI 产品本身的页面字段` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-03-93da1608` | 页面清单 | Web, PC | P1 | 冻结 `页面清单` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-04-56a5749b` | 页面布局块 | Web, PC | P1 | 冻结 `页面布局块` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `demo` | 展示型 demo 页面 | Web, PC | P1 | 冻结 `展示型 demo 页面` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `human` | human 层可引用“业务页面名 | Web, PC | P1 | 冻结 `human 层可引用“业务页面名` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-07-d4c36c95` | 页面汇总文档规范 | Web, PC | P1 | 冻结 `页面汇总文档规范` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-08-4a2d79ff` | 页面名称 | Web, PC | P1 | 冻结 `页面名称` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-09-ece61c61` | 页面入口 | Web, PC | P1 | 冻结 `页面入口` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-10-107f06b4` | 页面出口 | Web, PC | P1 | 冻结 `页面出口` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `prd` | 该页面来自哪条 PRD 承诺 | Web, PC | P1 | 冻结 `该页面来自哪条 PRD 承诺` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `user-story` | 该页面承载哪些 user story | Web, PC | P1 | 冻结 `该页面承载哪些 user story` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-13-1c4ec680` | 页面结构 | Web, PC | P1 | 冻结 `页面结构` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-specs-json` | page-specs/*.json | Web, PC | P1 | 冻结 `page-specs/*.json` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `contract` | 更适合实现侧消费的页面草图 contract | Web, PC | P1 | 冻结 `更适合实现侧消费的页面草图 contract` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-spec` | 结构化 page spec | Web, PC | P1 | 冻结 `结构化 page spec` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `page-17-860d61fc` | 页面草图 | Web, PC | P1 | 冻结 `页面草图` 的页面结构、关键动作和状态说明，确保与 requirement 材料一致。 |
| `material-document-detail` | 物料文档详情 | Web, PC | P2 | 冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。 |

## 跳转关系图

```text
[prd] -- 点击跳转 --> [user-story]
[page-03-93da1608] -- 点击跳转 --> [prd]
[material-viewer] -- 点击文档列表项 --> [material-document-detail]
[material-document-detail] -- 点击返回 --> [material-viewer]
```

## 冻结检查点
- [ ] 页面清单完整
- [ ] 跳转逻辑完整
- [ ] 单页线框可读
- [ ] 关联 requirement 可追踪
- [ ] 仅保留 wireframe freeze 语义
