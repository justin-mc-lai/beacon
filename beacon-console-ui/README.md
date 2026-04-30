# Beacon 可视化管理端

Beacon v1.3.6 的受管项目组合前端。当前实现覆盖首页、管理总览、项目详情、执行中心、恢复诊断、项目物料查看器和物料文档详情 7 页，并以内置真实项目投影数据支撑 AC-001 到 AC-017 的结构验收。

## 快速开始

```bash
npm install
npm run dev
```

默认开发地址：`http://localhost:5173`

生产构建：

```bash
npm run build
npm run preview
```

## 当前实现边界

- 首页只展示管理判断，不暴露宿主交互洪流。
- 管理总览只收 Beacon 项目，不引入 `omc / omx` 等外部系统。
- 项目详情表达版本线、主/并行 PRD、需求闭环、最近交付与推荐动作。
- 执行中心下钻 `single / team / ralph`，并只展示有限会话元数据。
- 物料流按 `version -> document type -> feature` 组织，且只读。
- 每页都回链 v1.3.5 wireframe freeze 与 v1.3.6 page spec。

## 受管文档来源

- 开发与构建前会自动执行 `scripts/generate-material-catalog.mjs`。
- 文档目录只扫描 Beacon 仓内 `docs/beacon` 下已经归档的真实项目材料。
- `slow-uni-bmtop` 等项目的物料页读取生成后的 `src/data/generatedProjectMaterials.ts`，不直接扫描外部项目仓。
- 物料目录数据通过 `src/data/materialCatalog.ts` 按需加载，不进入首页主入口包。

## 技术栈

- React 19
- TypeScript 6
- Vite 8
- React Router 7
- Ant Design 5
- react-markdown + remark-gfm

## 目录

```text
src/
├── components/      # Layout、HealthTag、PageTrace 等共享组件
├── data/            # 项目投影数据、页面 trace 与受管物料目录
├── pages/           # 7 个管理端页面
├── router/          # RouterProvider 与页面路由
├── types/           # Project / Runtime / Material 类型
├── utils/           # 状态标签与映射函数
└── constants/       # 路由常量
```

## 对照文档

- [实现进度](./IMPLEMENTATION.md)
- [v1.3.6 PRD](../docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md)
- [v1.3.6 User Story](../docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md)
- [v1.3.6 QA Test Cases](../docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md)
- [v1.3.5 Wireframe Freeze](../docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/wireframe-summary.md)
