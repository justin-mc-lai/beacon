# User Story: Beacon v1.3.10 prototype UX PRD closure and design-asset projection

## Story Boundary

- version: `v1.3.10`
- feature: `beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection`
- status: `freeze_ready`
- upstream_prd: `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`

本故事线只覆盖 Beacon `prototype` 的 requirement-stage 语义升级：

- 它仍然属于 `requirement-driven wireframe freeze`
- 它不升级成高保真视觉稿审批
- 它不替代 `implement`

它解决的是：如何让 `prototype` 真正提供 UI/UX 类 PRD 能力，而不是只提供页面、路由、状态和组件说明。

## Story 1: Prototype 必须冻结显式设计上下文

作为使用 Beacon 协作需求与原型的产品负责人 / 设计协作者，我希望 prototype 在进入 freeze 前就冻结显式设计上下文，而不是默认依赖临场猜测，这样原型不会退化成 generic wireframe。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | design-context | prototype canonical truth 必须包含 `target_audience`、`primary_use_cases`、`operator_mental_state`、`usage_environment`、`brand_tone`、`density_preference`。 |
| AC-002 | no-hidden-inference | 缺少显式 design context 时，prototype 只能停留在结构 freeze candidate，不得被判定为 UX freeze ready。 |

## Story 2: Prototype 必须冻结设计推理，而不只冻结结构

作为前端负责人 / 需求 owner，我希望 prototype 不只冻结页面结构，还冻结设计推理和反模式约束，这样 implement 不会重新发明页面模式、布局策略和信息优先级。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | design-reasoning | prototype canonical truth 必须包含 `product_surface_type`、`interaction_model`、`recommended_layout_pattern`、`visual_priority_rules`、`anti_patterns`、`design_checklist`。 |
| AC-102 | external-signal-absorb | 设计推理层必须能吸收 `ui-ux-pro-max-skill` 的产品类型/布局模式/反模式约束，同时保持 Beacon requirement-derived compile。 |
| AC-103 | rationale-freeze | implement 可以改变代码实现方式，但不能绕过已经冻结的设计推理重新定义页面主判断与信息层级。 |

## Story 3: Prototype 必须升级成 UI/UX 类 PRD 编译器

作为产品负责人，我希望 prototype 从“线框清单”升级成“UI/UX 类 PRD 编译器”，把 `prd / user-story / test-case` 编译成正式 UX closure truth。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | ux-contract | prototype 必须新增正式 `ux_contract`，至少表达 `first_glance_question`、`primary_decision`、`action_hierarchy`、`recognition_over_recall_rules`、`error_recovery_policy`、`allowed_machine_noise`、`forbidden_machine_noise`。 |
| AC-202 | page-intent-contract | 每个页面都必须表达 `why_this_page_exists`、`decision_supported`、`must_show_first`、`must_not_show`、`entry_conditions`、`exit_actions`。 |
| AC-203 | state-visibility-contract | loading / empty / error / blocked / stale / success 等关键状态必须表达 `user_question`、`required_feedback`、`recovery_actions`、`forbidden_feedback`。 |
| AC-204 | ux-prd-artifact | prototype 必须产出人类可读的 `ux-prd.md`，收口 design context、design reasoning、page intent、state visibility 与 AC/TC traceability。 |

## Story 4: Prototype 必须产出 agent-friendly 设计资产

作为 AI coding agent / 人类评审者，我希望 prototype 输出可直接消费的设计资产，而不是只输出内部 JSON 和摘要，这样 implement 与 review 才有稳定设计基线。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | design-md | prototype 必须产出 `DESIGN.md`，覆盖 visual theme、palette、typography、components、layout、do/don't、responsive、agent prompt guide。 |
| AC-302 | preview-assets | prototype 必须产出 `preview.html` 与 `preview-dark.html`，作为 design asset catalog，而不是产品实现页。 |
| AC-303 | canonical-projection | `DESIGN.md` 与 preview assets 必须由 canonical truth 单向投影生成，不允许手工编辑文档再反驱 machine truth。 |
| AC-304 | awesome-design-md-shape | prototype 资产形态必须对齐 `awesome-design-md` 的人/agent 双消费模式，但语义仍然是 Beacon requirement compile 产物。 |

## Story 5: Beacon 必须提供稳定默认 design preset

作为 Beacon 项目 owner，我希望 Beacon 在未显式声明其他设计方向时，默认提供一套克制、低噪音、管理工作台友好的设计基线。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | default-preset | Beacon 默认 design preset 固定支持 `apple-inspired-design-md`。 |
| AC-402 | preset-semantics | 该 preset 至少约束 quiet neutral surfaces、restrained accent、system/SF Pro typography bias、content-first hierarchy、management/workbench-friendly density。 |
| AC-403 | override-explicit | 项目 requirement 可以显式覆盖默认 preset，但覆盖原因必须被记录，而不是静默漂移。 |

## Story 6: Prototype review / gate 必须正式阻断 generic wireframe

作为 QA owner / release owner，我希望 prototype review 和 freeze gate 能把 generic wireframe、静态说明文档、状态反馈缺失、设计资产缺失正式阻断，而不是让它们带着 pass 标记进入 implement。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | heuristic-review | prototype review 必须新增 UX/heuristic 检查，至少覆盖 system status、real-world match、user control、recognition over recall、minimalist discipline、error recovery clarity。 |
| AC-502 | generic-wireframe-block | 缺少 design context、design reasoning、page decision、state feedback 或 design assets 时，prototype review / freeze 必须 fail closed。 |
| AC-503 | static-explanation-block | 仅有结构化说明、没有正式 UX closure truth 的 prototype 不得通过 freeze。 |

## Story 7: Implement 与 QA 必须消费同一套 prototype UX closure truth

作为 release owner，我希望 implement 与 qa 读取同一套 prototype UX closure truth，这样需求、原型、实现和验收四者不会再次分离。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | implement-consumption | implement 至少能消费 `ux_contract`、`page_intent_contract`、`design_context`、`DESIGN.md`。 |
| AC-602 | qa-consumption | qa 至少能验证页面主判断、状态反馈、machine noise 边界与设计资产偏离。 |
| AC-603 | no-truth-split | runtime mode 或前端代码实现细节不得改变已经冻结的 UX closure truth。 |

## Story 8: Prototype 子 skill 与规则面必须完成语义升级

作为 Beacon 平台维护者，我希望 prototype 相关子 skill、prompt、rule surface 从“线框生成器”升级成“UX PRD closure compiler”，吸收优秀设计输入但不破坏 Beacon 生命周期边界。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | prototype-skill-upgrade | prototype 子 skill / prompt / rule 默认吸收 `impeccable` 的上下文要求、`ui-ux-pro-max-skill` 的设计推理约束、`awesome-design-md` 的设计资产投影形态。 |
| AC-702 | no-stage-expansion | 该升级不新增新的公开 lifecycle stage，仍然对人类表现为 `prototype`。 |
| AC-703 | transaction-consistency | 新增 `ux-prd.md`、`DESIGN.md`、preview assets 后，多写入点仍遵循同一 canonical transaction contract。 |

## Story 9: Component contract 必须升级为 state-aware UX truth

作为 implement / QA 协作者，我希望 prototype 不只告诉我页面有哪些 section，还要明确每个组件负责哪些状态反馈和 AC/TC，这样交付与验收才能按责任边界对齐。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-801 | component-state-contract | prototype canonical truth 必须把组件责任表达为 state-aware contract，而不是仅有 page-global section inventory。 |
| AC-802 | component-feedback-traceability | 每个关键状态反馈至少能追溯到一个负责呈现的 component contract，并绑定对应 AC/TC。 |
| AC-803 | implement-qa-component-alignment | implement 与 qa 至少能读取同一套 component-state contract，避免组件层的 UX 责任漂移。 |

## Story 10: Cross-page business transition 必须冻结为正式 contract

作为产品负责人 / QA owner，我希望 prototype 不只冻结页面跳转，还冻结跨页业务迁移的事件、守卫和回退链路，这样 checkout / retry / fallback 类流程不会在 implement 阶段重新猜。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-901 | cross-page-transition-contract | prototype canonical truth 必须显式表达关键跨页业务迁移的 `from_page/from_state -> to_page/to_state`、`event`、`guard`、`fallback`。 |
| AC-902 | evidence-bound-transition | 关键跨页业务迁移必须绑定 route 或 runtime evidence，而不是只借用目标页 `ready` 状态。 |
| AC-903 | transition-traceability | 跨页业务迁移必须具备 AC/TC traceability，并能被 prototype review / QA 正式消费。 |

## Story 11: Prototype 必须输出 automation priority matrix

作为 QA / release owner，我希望 prototype 在冻结 UX truth 的同时产出自动化优先级矩阵，这样我能立刻知道哪些页面、状态和迁移是 release blocker，哪些只需 smoke 或人工验证。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-1001 | automation-priority-matrix | prototype 必须产出正式 `automation-priority-matrix`，覆盖 page/state/transition/component 四类 target。 |
| AC-1002 | priority-classification | 该矩阵至少区分 `release-blocker`、`primary-automation`、`smoke-only`、`manual-acceptable`。 |
| AC-1003 | shared-priority-truth | implement / qa / release 必须消费同一套 automation priority truth，而不是各自临时判断。 |
