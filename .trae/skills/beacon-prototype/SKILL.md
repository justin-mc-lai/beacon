---
name: beacon-prototype
description: Use when the user wants to generate, review, freeze, or inspect Beacon requirement-driven wireframe + UX PRD closure bundles through the public `prototype` stage.
---

# Beacon Prototype

This skill routes prototype work through Beacon's `prototype` surface.

Prototype is a conditional requirement surface, not a parallel implementation lane.

## Use for

- requirement-driven wireframe freeze package generation
- UX PRD closure bundle generation
- design context / design reasoning / UX contract freezing
- page intent and state visibility contract freezing
- DESIGN.md / preview asset projection before implementation
- prototype review and freeze readiness
- requirement-to-screen-and-UX handoff before implementation

## Operator rule

Prefer:

- `beacon prototype ...`
- or `beacon prototype ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh prototype ...`)

Treat `prototype` as a conditional formal stage between `test-case` and `implement`.
Keep `prototype` inside the requirement stage:

- it remains `requirement-driven wireframe freeze`
- it is not final visual approval
- it is not production UI generation
- it is only required when the feature has real UX/UI surface or route/state/interaction handoff needs

Expected prototype truth should make screen intent, UX reasoning, and interaction/state handoff auditable.

Do not turn prototype into a generic design playground, a final visual approval layer, or a parallel frontend entrypoint.

## Examples

- 适用例：
  - “这个 feature 有真实页面、状态切换和交互 handoff，需要在实现前冻结 UX contract。”
  - “需求本身没变，但实现前需要把页面意图、状态可见性和 screen-level handoff 说清楚。”
- 不适用例：
  - “这是纯后端契约/治理 feature，没有真实 UX/UI surface。” -> 不应强行进入 `prototype`
  - “我想直接做最终高保真视觉稿或生产页面。” -> 这不是 `prototype` 的职责

## Cold-start anchors

- `prototype` 解决的是 requirement-to-screen handoff，不是最终视觉审批。
- 只有当 UX/UI surface 真实存在时才需要它。
- 一旦进入 `prototype`，重点是让交互、状态和页面意图可审计，而不是追求展示效果。
