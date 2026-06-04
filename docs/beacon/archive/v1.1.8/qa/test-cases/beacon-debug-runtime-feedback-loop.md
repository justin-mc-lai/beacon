# Test Cases: Beacon Debug 运行时反馈闭环与版本迭代输入（v1.1.8）

**Feature**: beacon-debug-runtime-feedback-loop  
**Version**: v1.1.8

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备当前 debug 能力现状与用户修正后的目标）
- Gate1 冲突未决判定：Pass（目标聚焦在 runtime feedback/iteration input，而非泛化日志平台）
- Gate2 AC→TC 映射：Pass（覆盖目录、事件、聚合、生命周期绑定、产品规划输入）

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | 开启 debug 后在实践项目中执行 Beacon 生命周期 | 产生 runtime feedback，而不只是 prompt/router 事件 |
| TC-002 | contract | feedback 绑定 feature/run/stage | 每条反馈都能追溯到具体生命周期阶段 |
| TC-003 | contract | feedback 绑定 skill/profile | 每条反馈都有 skill_id / profile_id |
| TC-004 | contract | feedback 标记 feedback_target | 可区分 beacon-core / beacon-skill / project-skill / docs / runner |
| TC-005 | contract | 成功但高摩擦场景 | 可记录 `succeeded-with-friction` |
| TC-006 | contract | `.beacon/debug/` 目录输出 | 生成 runs/issues/ideas/index 等正式工件 |
| TC-007 | diagnosis | 高频同类 friction 聚合 | 可形成 issue 聚合对象 |
| TC-008 | planning | issue 升格为 idea | 可直接成为版本规划输入 |
| TC-009 | governance | debug 不退化为业务日志复制 | 输出聚焦 Beacon 使用摩擦 |
| TC-010 | integration | help / doctor / report 感知 debug 状态 | 能提示当前项目 Beacon friction 热点 |
| TC-011 | regression | 保持现有 prompt/run debug 兼容 | 不破坏已有 debug 基础能力 |
| TC-012 | scope | 当前 v1.1.8 仅为设计线 | 文档明确 design-only，不误报已实现 |

## 样板场景

### 场景 A：实现阶段高摩擦成功
- 用户通过 Beacon skill 完成 implement，但中途反复手工补上下文
- 预期：debug 记录为 `succeeded-with-friction`，并生成 Beacon 能力改进候选

### 场景 B：help/doctor 导航误导
- lifecycle 实际应进入 reopen/rewrite，但 help/doctor 仍建议继续 implement
- 预期：feedback_target=`workflow-docs` 或 `beacon-core`，并形成迭代 issue

### 场景 C：runner/skill 能力缺口
- 实践项目需要 QA/login-state/browser acceptance，但当前 skill 组合不够顺滑
- 预期：可归因到 `runner-adapter` / `beacon-skill`，而不是淹没在业务日志中

## 执行语义

- `Pass`：debug 被正式定义为实践反馈→产品迭代输入面
- `Fail`：仍然只是命令/路由调试，没有形成版本演进输入
- `Blocked`：debug 目录、事件 schema、聚合语义仍有关键冲突
