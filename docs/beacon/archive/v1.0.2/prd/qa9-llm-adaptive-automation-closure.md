# PRD: QA9 LLM 自适应测试闭环（v1.0.2）

## 1. 背景

Beacon 已具备 QA9 命令与 gate 基线能力，但对“不同项目自动选测什么、如何真实执行、如何自动回填与放行”仍需进一步产品化，尤其 AI Agent Skill 场景。

## 2. 目标

1. 建立项目感知型 QA 策略（LLM + 规则）
2. 建立 QA9 从生成到执行到放行的自动闭环
3. 建立 Cypress/Playwright 证据级强验收

## 3. 范围

### 3.1 In Scope

- think 输出 `qa_strategy`
- test-case 生成增强版 QA9 matrix
- auto-test 执行与结果回填
- test-progress 自动同步
- gate strict 强校验（防假证据）

### 3.2 Out of Scope（v1.0.2）

- 全量跨设备云真机兼容性平台接入
- 非 Web 场景的视觉回归体系化平台

## 4. 角色与场景

- PM/Tech Lead：定义 feature，查看 QA 策略与放行状态
- QA：审阅自动生成用例，处理异常与 waiver
- Dev：执行 workflow，一次性产出可审计测试结果

## 5. 详细需求

### 5.1 QA 策略生成

- 输入：项目目录、技术栈、是否 Web UI、API/Contract 线索
- 输出：`qa_strategy`（project_type、qa_applicability、runner_policy、commands）
- 规则优先级：安全规则 > 项目硬约束 > LLM 建议

### 5.2 QA9 用例生成

- 产物：`*.qa9-matrix.json`
- 必备字段：`qa_requirements`、`entries`、`llm_plan`、`compatibility_matrix`
- 生成策略：每个 AC 至少映射 1 个可执行 TC；required 类型必须覆盖

### 5.3 自动化执行与回填

- scope=qa9 执行所有 required auto/hybrid 用例
- 回填：TC status、exit_code、assertion_count、junit_valid、evidence_ref
- 汇总：passed/failed/blocked、pass_rate、automation_rate、flaky_rate

### 5.4 Runner 策略

- functional：Cypress 或 Playwright（按 qa_strategy）
- compatibility：优先 Playwright 多浏览器 project
- 探索/补充：agent-browser（非 release 主证据）

### 5.5 Gate 强验收

- 关键 reason_code（qa9/证据/报告一致性）默认 blocked
- 通过条件：
  - required type 全覆盖
  - required auto case 全执行
  - assertion_count > 0
  - junit 有效
  - evidence 新鲜且 run_id 一致
  - auto-test 汇总与层结果一致

## 6. 数据与产物

- `docs/beacon/{version}/execution/v1.0.2-requirements.md`
- `docs/beacon/{version}/user-story/qa9-llm-adaptive-automation-closure.md`
- `docs/beacon/{version}/prd/qa9-llm-adaptive-automation-closure.md`
- `docs/beacon/{version}/qa/test-cases/*.qa9-matrix.json`
- `.beacon/auto-test-status.json`
- `.beacon/test-progress.json`

## 7. 里程碑

- M1（P0）：QA strategy + QA9 matrix 闭环
- M2（P1）：Cypress/Playwright 混合执行 + 回填统计
- M3（P2）：Gate 报告一致性与反假证据强化

## 8. 验收

- AC 全部通过
- release gate strict 可稳定阻断假通过
- 关键指标达标：automation_rate >= 0.85，pass_rate 可追溯

## 9. 框架接入决策（v1.0.2）

- AI Agent 集成首选：`browser-use`
- Gate 主证据执行首选：`Playwright`（兼容性矩阵与可重复报告）
- 已有团队资产可选：`Cypress`（回归层）
- 命令通道与应急回退：`agent-browser`

详见：`../research/qa-framework-adapter-comparison.md`
