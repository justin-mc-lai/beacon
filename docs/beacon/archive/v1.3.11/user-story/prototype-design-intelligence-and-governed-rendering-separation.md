# User Story: prototype-design-intelligence-and-governed-rendering-separation

## Story Boundary

- version: `v1.3.11`
- feature: `prototype-design-intelligence-and-governed-rendering-separation`
- status: `reopened`
- upstream_prd: `docs/beacon/archive/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
- related_prd:
  - `docs/beacon/archive/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md`
  - `docs/beacon/archive/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- current_revision: `R2`
- source_revision: `R2`

本故事线覆盖 Beacon 在 `v1.3.11` 中把 prototype 与 implement 之间的设计推导链正式分层，阻断设计治理文案、审阅文案、解释性说明直接渲染到终态 UI。它冻结的是原型编译与受控渲染合同，不是视觉品牌重构项目。

## Story 1: prototype 必须先产出设计中间工件

作为 Beacon requirement owner，我希望 prototype 先把 requirement truth 编译成结构化设计工件，而不是直接写页面文案，这样 implement 才能消费稳定输入。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | design-intelligence-layer | prototype compiler 接收 `prd / user-story / test-case / prototype freeze context / software-semantic-profile` 作为正式输入。 |
| AC-002 | design-artifact-set | prototype compiler 至少产出 `design-context / surface-profile / layout-pattern / component-state-matrix / ui-copy-policy / style-preset / design-review` 七类结构化工件。 |
| AC-003 | artifact-traceability | 每类工件都记录 `source feature / source requirement refs / generated_at / source_hash / projection_role`。 |
| AC-004 | no-markdown-only-contract | implement 与 preview 不再以 ux-prd 解释段落作为唯一消费面。 |
| AC-005 | four-layer-artifact-topology | prototype bundle 必须显式区分 `authoring / review / projection / implementation` 四层 artifact topology，并保持单向投影关系。 |

## Story 2: design skill 必须只作为内部推导与治理输入

作为 Beacon 设计治理维护者，我希望 design skill 只参与推导、约束和审阅，而不是直接形成首屏文案，这样生成页面不会继续漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | ui-ux-pro-max-role | `ui-ux-pro-max-skill` 仅用于页面目标、布局模式、信息密度、组件组织推导。 |
| AC-102 | impeccable-role | `impeccable` 仅用于反模式识别、文案校验、交互与视觉治理。 |
| AC-103 | awesome-design-md-role | `awesome-design-md` 仅用于样式预设、设计语法、组件语义基线参考。 |
| AC-104 | no-direct-render-from-skill | 上述 design skill 的原始输出不得直接写入 `pages/*.md`、`page-specs/*.json`、`preview.html`、implement render 结果。 |

## Story 3: governed rendering 必须区分 internal copy 与 production copy

作为 Beacon operator，我希望页面只显示正式可见文案，不显示治理合同与解释文案，这样首屏才符合正式软件语义。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | rendering-contract | Beacon 建立正式 `governed-rendering-contract`，至少区分 `internal-governance-copy / review-visible-copy / production-visible-copy`。 |
| AC-202 | internal-copy-boundary | `internal-governance-copy` 仅允许出现在 `ux-prd / review material / gate evidence`。 |
| AC-203 | production-copy-boundary | `production-visible-copy` 才允许进入 `pages/*.md / page-specs/*.json / preview.html / implement render`。 |
| AC-204 | no-governance-leakage | 默认页面不再出现设计原因、审阅意见、资产目录说明、路径清单、历史噪声。 |
| AC-205 | review-only-human-materials | `ux-prd.md`、`DESIGN.md`、`prototype-review.md`、解释型页面 markdown 仅作为 review-only human-readable materials 保留，不再属于默认实现输入面。 |

## Story 4: 首屏投影必须服从正式语义合同

作为 Beacon 真实项目使用者，我希望页面首屏只显示页面目标、核心对象、主动作和必要状态反馈，这样原型与实现都不会变成解释页。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | production-ui-copy-profile | `page intent / state visibility / action hierarchy / recovery diagnostics` 到 UI 文案的投影必须经过 `production-ui-copy-profile`。 |
| AC-302 | single-semantic-target | 一句话只表达一个功能含义；标题只描述页面对象与页面动作。 |
| AC-303 | first-screen-suppression | `当前状态 / 下一步动作 / 恢复路径` 解释块、设计说明、路径列表、历史 run 噪声不得默认占据首屏。 |
| AC-304 | exception-surface | 仅当页面状态为 `blocked / failed / empty-risk` 时，允许显示恢复信息；恢复信息只包含 reason code、受影响对象、允许动作。 |

## Story 5: prototype review gate 必须 fail-closed

作为 Beacon 交付治理维护者，我希望 prototype gate 能稳定拦截解释上屏与语义漂移，这样 freeze 才有约束力。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | gate-reason-codes | prototype review gate 至少支持 `design_context_explicit_block / governance_copy_leak / review_copy_rendered_as_production_ui / semantic_profile_violation / first_screen_over_explanation`。 |
| AC-402 | fail-closed | 任一阻断项命中时，prototype 不得判定为可交付。 |
| AC-403 | shared-semantic-profile | prototype、preview、board、implement 共享同一 `software-semantic-profile`，术语、状态枚举、动词口径一致。 |
| AC-404 | auditability | gate 输出保留 reason code、命中对象、修复建议、对应 artifact ref。 |
| AC-405 | projection-gate-before-render | 未经 projection contract 允许的 artifact 不得进入 production render surface，不能只在输出后再做词面拦截。 |

## Story 6: implement 必须只消费受控设计工件

作为 Beacon implement maintainer，我希望 implement renderer 只消费结构化设计工件与正式可见文案，这样实现层不再重新解释需求。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | allowed-inputs | implement renderer 只允许消费 `surface-profile / layout-pattern / component-priority-map / production-ui-copy-profile / style-preset / design-lint-rules`。 |
| AC-502 | blocked-inputs | implement renderer 禁止直接消费 brainstorm 原文、review comments 原文、ux-prd 解释段落、gate 诊断原文。 |
| AC-503 | traceability | implement 输出可追溯到 requirement source ref、design artifact ref、projection contract ref、review gate verdict。 |
| AC-504 | closure | 在不读取设计解释原文的前提下，implement 仍可完成页面渲染与状态表达。 |
| AC-505 | default-consumption-entry | implement 默认且唯一允许读取 `machine-view/index.json`、`design-artifacts/`、`implementation-map.json`、`production-ui-copy-profile.json`、`design-lint-rules.json`。 |

## Delivery Notes

- 本故事线是 `beacon-operator-workbench-and-board-launcher` 的模型层补强。
- 它优先修复 prototype compiler、preview renderer、implement renderer 的输入输出合同。
- 下一阶段应进入 test-case，把 artifact、projection、gate、implement consumption 全部编译为可执行 AC matrix。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 8 |
| Status | reopened-model-line-r2 |
| Created | 2026-05-02 |
| Change Scope | design-intelligence-layer / design-artifact-contract / four-layer-artifact-topology / review-only-human-materials / design-skill-role-contract / governed-rendering-contract / production-ui-copy-profile / first-screen-projection / prototype-review-gate / implement-consumption-contract |
