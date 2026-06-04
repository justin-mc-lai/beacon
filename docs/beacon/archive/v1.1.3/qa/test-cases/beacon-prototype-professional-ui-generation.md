# Test Cases: beacon-prototype-professional-ui-generation

## Overview

**Feature**: beacon-prototype-professional-ui-generation  
**Version**: v1.1.3  
**Source**: `docs/beacon/archive/v1.1.3/user-story/beacon-prototype-professional-ui-generation.md`  
**AC Matrix JSON**: `docs/beacon/archive/v1.1.3/qa/test-cases/beacon-prototype-professional-ui-generation.ac-test-matrix.json`

---

## AC → TC Mapping

| AC ID | TC ID | Layer | Scenario | Expected |
|------|------|-------|----------|----------|
| AC-001 | TC-001 | contract | `prototype create` 读取结构化 Prototype Contract，而不是只读文本 preview | 输入语义升级 |
| AC-002 | TC-002 | exception | 缺少关键 contract 时 create 直接失败 | fail-fast 生效 |
| AC-003 | TC-003 | contract | PRD/US 覆盖 archetype / theme / IA / CTA / jump / state contract | 输入字段齐全 |
| AC-004 | TC-004 | visual-contract | 输出页面体现专业 UI 气质，不是 generic shell | 页面表达与需求一致 |
| AC-005 | TC-005 | contract | archetype 覆盖 dashboard/list-detail/form-wizard/marketing-page/admin-workbench/mobile-task-flow | archetype 模型齐全 |
| AC-006 | TC-006 | contract | `theme.json` 存在并包含主题/排版/spacing/radius/shadow/motion | 主题契约齐全 |
| AC-007 | TC-007 | contract | `navigation-map.json` 存在并记录节点、跳转目标和说明 | 导航契约齐全 |
| AC-008 | TC-008 | contract | `interaction-map.json` 存在并记录 CTA/modal/drawer/tab/form/state | 交互契约齐全 |
| AC-009 | TC-009 | contract | `prototype-brief.json` 记录 archetype/target_user/primary_flow/design_intent | 原型摘要齐全 |
| AC-010 | TC-010 | command-contract | `prototype review` 子命令存在 | review 阶段建立 |
| AC-011 | TC-011 | contract | `prototype-review.json` 与 `prototype-review.md` 落盘 | review 输出齐全 |
| AC-012 | TC-012 | workflow-contract | UI 需求 workflow prototype 阶段要求 create + review + freeze | workflow 集成完整 |
| AC-013 | TC-013 | gate-contract | gate 校验 theme/navigation/interaction/review 产物 | gate 消费新 contract |
| AC-014 | TC-014 | test-contract | `test-case create` 能消费 navigation / interaction map | 原型与测试打通 |
| AC-015 | TC-015 | accessibility-contract | 原型继续满足语义结构、focus、aria-label、label、reduced-motion | a11y 约束保留 |
| AC-016 | TC-016 | draft-contract | 文档明确当前 v1.1.3 为需求草稿阶段，未实现正常 | 阶段语义清晰 |

---

## 执行检查清单

- [ ] 检查 `prototype create` 是否被定义为 contract-driven
- [ ] 检查缺失 contract 时是否明确 fail-fast
- [ ] 检查是否新增 `prototype review`
- [ ] 检查是否新增 `prototype-brief / theme / navigation-map / interaction-map`
- [ ] 检查 workflow 是否要求 create + review + freeze
- [ ] 检查 gate 是否消费 review/theme/navigation/interaction 产物
- [ ] 检查 test-case 是否计划消费 navigation / interaction contract
- [ ] 检查文档是否明确当前仍属 requirement draft

---

## 建议验证命令（文档期）

| TC ID | 建议命令 | 备注 |
|------|----------|------|
| TC-001 | `rg -n "Prototype Contract|contract-driven|结构化 Prototype Contract" docs/beacon/archive/v1.1.3/{prd,user-story}/*.md -S` | 输入语义检查 |
| TC-002 | `rg -n "fail-fast|直接失败|不允许退化|不允许模糊猜测" docs/beacon/archive/v1.1.3/prd/beacon-prototype-professional-ui-generation.md -S` | 失败策略检查 |
| TC-006 | `rg -n "theme.json|spacing|radius|shadow|motion" docs/beacon/archive/v1.1.3/{prd,user-story}/*.md -S` | 主题契约检查 |
| TC-007 | `rg -n "navigation-map.json|jump rationale|navigation nodes" docs/beacon/archive/v1.1.3/{prd,user-story}/*.md -S` | 导航契约检查 |
| TC-008 | `rg -n "interaction-map.json|CTA|modal|drawer|tabs|toast|state transitions" docs/beacon/archive/v1.1.3/{prd,user-story}/*.md -S` | 交互契约检查 |
| TC-010 | `rg -n "prototype review" docs/beacon/archive/v1.1.3/{prd,user-story}/*.md -S` | review 子命令检查 |
| TC-012 | `rg -n "create \+ review \+ freeze|workflow" docs/beacon/archive/v1.1.3/prd/beacon-prototype-professional-ui-generation.md -S` | workflow 集成检查 |
| TC-013 | `rg -n "theme.json|navigation-map.json|interaction-map.json|prototype-review" docs/beacon/archive/v1.1.3/prd/beacon-prototype-professional-ui-generation.md -S` | gate 集成检查 |
| TC-014 | `rg -n "test-case create|CTA 跳转|状态覆盖|UI smoke" docs/beacon/archive/v1.1.3/prd/beacon-prototype-professional-ui-generation.md -S` | test-case 集成检查 |
| TC-016 | `rg -n "requirement materials draft|未实现.*正常|草稿阶段" docs/beacon/archive/v1.1.3/{prd,user-story}/*.md -S` | 草稿阶段语义检查 |

---

## 建议 reason codes

- `prototype_contract_missing`
- `prototype_contract_incomplete`
- `prototype_theme_contract_missing`
- `prototype_navigation_contract_missing`
- `prototype_interaction_contract_missing`
- `prototype_review_missing`
- `prototype_review_failed`
- `prototype_generic_shell_detected`
- `prototype_test_contract_unlinked`
