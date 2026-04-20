# User Story: beacon-v1.3.5-prototype-wireframe-mode-and-prototype-surface-refactor

## Story

**As a** Beacon 产品负责人与实现负责人,  
**I want** `prototype` 阶段只输出 requirement-driven wireframe 冻结包，并且跨 human/machine/sqlite 多写入点保持一致,  
**So that** 我可以在 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 主链中稳定冻结需求、避免信息漂移、并将结果可靠交接到 `v1.3.6` 实现线。

## Acceptance Criteria

- [ ] AC-001 `prototype` 默认与唯一正式模式是 `wireframe`，不再以 HTML 高保真原型作为交付语义。
- [ ] AC-005 Beacon 人类主链明确包含 `prototype` 阶段，且其职责固定为 wireframe freeze（位于 test-case 与 implement 之间）。
- [ ] AC-006 `beacon-prototype` 成为唯一 host-visible 原型子 skill，默认解释为 requirement-driven wireframe freeze。
- [ ] AC-007 `wireframe.py` 退出正式流程，不再作为平行入口与 `prototype` 竞争语义。
- [ ] AC-002 wireframe 包可独立冻结页面清单、页面职责、路由关系、状态说明，不依赖 HTML 页面。
- [ ] AC-003 每个页面都可追溯到 PRD 承诺、user story 与 test-case 场景，满足 requirement-driven 闭环。
- [ ] AC-004 `v1.3.5` 输出只负责结构冻结，不反向篡改 `v1.3.6` 产品定义，且可被下游直接消费。
- [ ] AC-008 `state-flow-map` 可验证关键状态迁移、异常回退与 test-case 映射；缺失时 `prototype review` 必须阻断。
- [ ] AC-009 `component-catalog` 能建立组件职责/动作/状态与 AC/TC 映射；缺失时 `prototype freeze` 必须失败。
- [ ] AC-010 human/machine/sqlite 三写入点共享 `source_hash`、`projection_seq`、`transaction_id`；任一不一致必须标记 `drift` 并阻断 release pass。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 8 |
| Status | frozen-pending-implementation |
| Created | 2026-04-20T17:28:21.671716 |
| Updated | 2026-04-20T17:33:00+08:00 |
| Memory Context | N/A |
