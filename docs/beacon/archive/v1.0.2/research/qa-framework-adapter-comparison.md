# QA 框架接入对比（v1.0.2）

## 结论（面向 AI Agent 集成）

在 **AI Agent 原生集成能力** 维度，`browser-use` 为首选。

但在 **release gate 可重复性** 维度，建议采用混合架构：
- `browser-use`：用于智能探索、任务驱动 E2E、自动生成候选用例/步骤
- `Playwright/Cypress`：用于稳定回归与严格放行证据

## 对比矩阵

| 框架 | AI Agent 集成 | 稳定性/可重复 | 适配建议 |
|---|---|---|---|
| browser-use | 原生 Agent 任务驱动，支持 LLM 编排 | 中（受模型与页面波动影响） | AI 驱动主入口 |
| Playwright | 非 Agent 原生，但有完善自动化与 MCP/Agent 文档 | 高 | Gate 主证据执行器（优先） |
| Cypress | 强测试生态，非 Agent 原生 | 高（Web 回归成熟） | 现有项目回归执行器（可选） |
| agent-browser | 命令级浏览器控制，适合工具化编排 | 中高（取决于脚本纪律） | 作为 Beacon 工具通道与应急回退 |

## 接入定位

### 1) browser-use（AI-first）
- 适合：自然语言任务、未知页面探索、多步骤流程（如表单/预订/复杂后台）
- 产出：
  - 任务执行轨迹
  - 关键页面状态
  - 候选断言与步骤（可转为 Playwright/Cypress 脚本）

### 2) Playwright（Deterministic-first）
- 适合：多浏览器兼容矩阵、trace/video/screenshot 证据、CI 稳定回归
- 产出：结构化报告与可重复证据，适合作为 strict gate 放行依据

### 3) Cypress（Regression-first）
- 适合：已有 Cypress 生态团队、快速 Web 回归套件
- 产出：成熟回归结果与开发者友好调试体验

### 4) agent-browser（Tool-first）
- 适合：Beacon 命令层调用、脚本化操作、轻量自动化探测
- 产出：统一 CLI 操作记录，便于串联 workflow 证据

## Beacon v1.0.2 建议策略

- `qa_strategy.runner_policy` 默认：
  - `functional`: `browser-use`（生成/探索） + `playwright`（固化/放行）
  - `compatibility`: `playwright`
  - `regression`: `playwright` 或 `cypress`（按项目已有资产）
- `gate strict` 只认可可重复报告层（Playwright/Cypress）作为 release 主证据；
  `browser-use` 证据用于补充解释与发现缺陷。

## 风险提示

- 仅依赖 browser-use 直接放行存在波动风险（模型推理与页面动态变化）
- 仅依赖 Playwright/Cypress 又会损失 AI 探索效率
- 最优路径：**AI 发现 + 确定性回归放行**
