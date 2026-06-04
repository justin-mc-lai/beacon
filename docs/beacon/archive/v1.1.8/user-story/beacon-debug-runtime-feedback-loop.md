# User Story: Beacon Debug 运行时反馈闭环与版本迭代输入（v1.1.8）

**Feature**: beacon-debug-runtime-feedback-loop  
**Version**: v1.1.8

**As a** 在真实项目中深度使用 Beacon skill 生命周期的使用者 / 维护者 / Beacon 自身迭代负责人  
**I want** 开启 Beacon debug 后，实践项目中的真实使用摩擦能被实时反馈到 Beacon 本体能力改进面，并沉淀到 debug 目录  
**So that** 后续可以直接从 debug 目录提取 Beacon 的版本迭代思路，而不是依赖事后回忆。

## Story Slices

### US-001: Debug 支持实践项目实时反馈
作为 Beacon 使用者，我希望在真实项目生命周期中开启 debug 后能持续记录结构化反馈，以便真实问题不丢失。

### US-002: Debug 反馈与 skill/profile/stage 绑定
作为 Beacon 使用者，我希望每条 feedback 都知道来自哪个 skill/profile/stage，以便能定位 Beacon 该补哪一层。

### US-003: Debug 支持高摩擦成功场景
作为 Beacon 使用者，我希望“成功但很痛苦”的使用过程也能被采集，以便 Beacon 迭代的不只是修 bug，还能优化体验。

### US-004: Debug 目录能直接服务版本规划
作为 Beacon 维护者，我希望 debug 目录中能聚合 issue 和 idea，以便直接成为后续 PRD / user-story 输入。

### US-005: Debug 与 help/doctor/report 联动
作为 Beacon 使用者，我希望 help/doctor/report 都能感知 debug 状态和高频摩擦，以便形成更闭环的治理面。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Runtime Feedback | Debug 支持实践项目中的实时 feedback，而不是只记录 prompt/router 事件 |
| AC-002 | Stage Binding | 每条 feedback 都能绑定 feature / run / lifecycle stage |
| AC-003 | Skill Binding | 每条 feedback 都能绑定 skill_id / profile_id |
| AC-004 | Feedback Target | feedback 必须区分 beacon-core / beacon-skill / project-skill / workflow-docs / runner-adapter |
| AC-005 | Friction Success | Debug 支持 failed 之外的 `succeeded-with-friction` 场景 |
| AC-006 | Debug Directory | `.beacon/debug/` 成为正式反馈目录 |
| AC-007 | Event Schema | Debug event 至少包含 expected / actual / friction_summary / workaround / suggested_capability |
| AC-008 | Aggregation | Debug 事件可聚合为 issue / idea |
| AC-009 | Planning Input | issue / idea 可直接作为后续版本规划输入 |
| AC-010 | Non-Business Logging | Debug 采集不退化为业务日志全量复制 |
| AC-011 | Help/Doctor | help / doctor / report 可感知 debug 状态与高频摩擦 |
| AC-012 | Design Scope | v1.1.8 当前先冻结 debug 反馈闭环设计，不宣称功能已实现 |

## 风险与提醒

- 若只保留 `.beacon/state/debug-feedback`，后续仍难直接作为产品规划输入
- 若 feedback 不绑定 stage/skill/profile，仍然很难知道 Beacon 要补哪一层
- 若只记录失败，不记录高摩擦成功，Beacon 会错过大量真实体验问题
