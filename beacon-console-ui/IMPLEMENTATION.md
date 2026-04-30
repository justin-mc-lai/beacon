# Beacon 可视化管理端 - 实现进度

**项目**: `beacon-console-ui`
**技术栈**: React 19 + TypeScript 6 + Vite 8 + Ant Design 5
**开始时间**: `2026-04-21`
**当前状态**: `implement ready / build clean`

## 已完成

### 构建与依赖

- 修正 `package.json` 依赖声明，补齐 `antd`、`react-router-dom`、`react-markdown`、`remark-gfm`
- 移除过时的 TS `baseUrl` 配置，修复 Vite 8 `manualChunks` 类型问题
- 将页面路由改为懒加载，并将受管文档目录拆为独立数据包，避免首页入口包携带全量 Markdown 文档
- 通过 `npm run build`，构建输出稳定且无大包告警

### 数据与类型

- 扩展 `Project / Runtime / Material / Recovery / RequirementClosure` 类型
- 建立 4 个真实项目的本地投影数据：
  - `beacon`
  - `slow_uni_bmtop`
  - `rolo`
  - `shopxo_canada`
- 将 `single / team / ralph`、有限 session metadata、artifact refs、recovery issues、material docs 统一到同一数据面
- 新增 `scripts/generate-material-catalog.mjs`，只从 Beacon 仓内 `docs/beacon` 归档材料生成真实项目文档目录
- 新增 `src/data/materialCatalog.ts`，以按需加载方式为物料页提供受管文档目录

### 页面闭环

- `HomePage`
  - 生命周期优先的经营总览
  - 阻塞与介入区
  - 当前交付与下一步
- `ManagementOverviewPage`
  - 多项目密集注册表
  - 健康态 / 阶段筛选
  - debug 与推荐 skill 扫描
- `ProjectDetailPage`
  - 版本线、主/并行 PRD、需求闭环
  - 最近交付与推荐动作
  - runtime 摘要入口
- `RuntimeCenterPage`
  - `single / team / ralph` 模式切换
  - team agent 表与 session metadata 引用
  - ralph round/failure/blocker 展示
- `RecoveryDiagnosticsPage`
  - truth source 说明
  - degraded / rebuild / doctor 解释
  - 恢复步骤与风险提示
- `MaterialViewerPage`
  - `version -> document type -> feature` 树形浏览
  - Markdown 只读预览
  - 来源路径保留
  - 正式来源说明与空状态处理
- `MaterialDocumentDetailPage`
  - 文档详情阅读态
  - 同类文档切换
  - 只读约束说明
  - 完整 Markdown 结构样式支持

### AC 对齐

- AC-001 ~ AC-002：首页先展示经营判断，不暴露机器洪流
- AC-003：总览页稳定展示项目名、项目类型、版本、阶段、健康态、debug、下一步、推荐 skill
- AC-004 ~ AC-005：项目详情可接力并显式表达 requirement closure
- AC-006 ~ AC-007：物料页和文档详情支持只读 Markdown 浏览与来源路径
- AC-008 ~ AC-011：runtime 下钻只在运行中心，Team / Ralph 与有限 session metadata 可见
- AC-012：恢复诊断明确 truth 仍来自 `docs/beacon` 与 `.beacon`
- AC-013 ~ AC-014：默认只看 Beacon 项目，并覆盖四个真实项目
- AC-015：每页增加 v1.3.5 freeze 与 v1.3.6 page spec 回链卡
- AC-016 ~ AC-017：保留 `home -> management-overview -> project-detail -> runtime-center / recovery-diagnostics` 主轴，并接入物料流

## 当前缺口

- 真实后端投影仍未接入，当前为 release-facing fixture/read-model
- implement / qa evidence 仍需通过 Beacon CLI 生成正式归档
- feature revision 仍需 freeze，之后 QA 才能从 blocked 进入可验证状态

## 下一步

1. 冻结 `beacon-v1.3.6-visual-management-console-and-material-viewer` revision
2. 生成 `.beacon/implement` 证据并补实现归档
3. 重新运行 `beacon qa`，产出 `scorecard/status/ac-closure`
4. 如有需要，再把当前 fixture 数据替换为真实 PocketBase / SQLite 读模型

## 验证命令

```bash
npm install
npm run build
npm run dev -- --host 127.0.0.1 --port 4173
```

## 参考文档

- `../docs/beacon/v1.3.6/prd/beacon-v1-3-6-visual-management-console-and-material-viewer.md`
- `../docs/beacon/v1.3.6/user-story/beacon-v1.3.6-visual-management-console-and-material-viewer.md`
- `../docs/beacon/v1.3.6/qa/test-cases/beacon-v1.3.6-visual-management-console-and-material-viewer.md`
- `../docs/beacon/v1.3.5/prototype/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor/wireframe-summary.md`

**最后更新**: `2026-04-21`
