---
name: beacon-prototype
description: Use when the user wants to bind an accepted external UI/UX result into Beacon requirement truth through the public `prototype` adapter surface; legacy wireframe bundles remain readable for older versions.
---

# Beacon Prototype

This skill routes prototype work through Beacon's `prototype` surface.

For `v1.4.9+`, Prototype is a design-result adapter, not a UI/UX execution or design generation surface.
For `v1.4.8` and older versions, legacy requirement-driven wireframe freeze bundles may still be generated, reviewed, frozen, or inspected for compatibility.

## Use for

- accepted `ui-ux-dev` result intake
- design-result adapter binding
- PRD / user-story / test-case truth binding diagnostics
- page intent and state visibility contract freezing
- interaction handoff mapping before implementation
- historical prototype bundle status/archive/release compatibility
- legacy `design_context` / `design_reasoning` / `ux_contract` inspection when old materials exist
- legacy `DESIGN.md` / `preview-dark.html` preview asset inspection when old materials exist
- requirement-to-screen-and-UX handoff before implementation

## Operator rule

Prefer:

- `beacon prototype adapt ...` after an accepted `ui-ux-dev` result exists
- `beacon prototype status ...` to inspect adapter binding or legacy bundle status
- `ui-ux-dev` for exploration, system recommendation, review, polish, extract, and library lookup

For `v1.4.9+`, do not use Beacon prototype to generate wireframes or visual direction.
Route UI/UX execution to `ui-ux-dev`, then write the accepted result back through `beacon prototype adapt`.

Keep `prototype` inside the requirement governance boundary:

- it adapts accepted design output into Beacon truth bindings
- it is not final visual approval
- it is not production UI generation
- it is not a generic design playground
- it is required only when accepted UI/UX output affects screen intent, state visibility, interaction handoff, PRD promise, user-story acceptance, or test-case coverage

Expected adapter truth should make screen intent, state visibility, interaction handoff, and PRD/user-story/test-case bindings auditable.

Legacy design anchors that may still appear in historical requirement packs or compatibility tests:

- `apple-inspired-design-md`
- `ui-ux-pro-max-skill`
- `awesome-design-md`

## Examples

- 适用例：
  - “ui-ux-dev 的结果已经接受，需要把 screen intent、状态可见性和 handoff 绑定回 Beacon truth。”
  - “实现前需要证明这个设计结果映射到了 PRD、user-story、test-case。”
  - “我要检查旧版本 prototype bundle 的状态或 release history。”
- 不适用例：
  - “这是纯后端契约/治理 feature，没有真实 UX/UI surface。” -> 不应强行进入 `prototype`
  - “我想探索 UI 方向、做视觉 polish、找组件库。” -> 应去 `ui-ux-dev`
  - “我想直接做最终高保真视觉稿或生产页面。” -> 这不是 `prototype` 的职责

## Cold-start anchors

- `prototype` 在 `v1.4.9+` 解决的是 accepted design result 到 requirement truth 的绑定。
- UI/UX execution belongs to `ui-ux-dev`。
- 一旦进入 `prototype adapt`，重点是让交互、状态、页面意图和 truth bindings 可审计，而不是生成展示效果。
