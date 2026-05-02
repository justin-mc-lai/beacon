# DESIGN.md: beacon-operator-workbench-and-board-launcher

## Visual Theme
- Design Preset: `apple-inspired-design-md`
- Primary Accent: `#0071E3`
- Secondary Surface: `#F5F5F7`
- Atmosphere: quiet neutrals, restrained emphasis, dense but readable workbench hierarchy.

## Typography
- Bias toward SF Pro / system sans.
- Hero-scale text is disallowed in workbench pages unless a real first-screen signal demands it.

## Layout Principles
- Recommended Pattern: header -> primary judgment -> supporting context -> next action
- First screen answers the main question before secondary detail.
- Keep navigation low-noise and avoid decorative dashboard filler.

## Component Styling
- Compact toolbars, restrained cards, explicit empty/error/loading states.
- Buttons and controls should privilege recognition over recall.

## Do
- Show recovery actions when blocked, stale, or error states appear.
- Keep source paths and machine references in secondary disclosure zones only.

## Don't
- Do not produce a marketing hero dashboard.
- Do not surface transaction metadata in primary UI copy.
- Do not use a generic blue SaaS shell as the default design answer.

## Responsive
- Preserve hierarchy and next-action clarity on desktop-first workbench layouts.
- Collapse secondary detail before primary judgment content.

## Agent Prompt Guide
- Primary audience: Beacon 管理者 / 需求 owner / 实现协作者
- Preserve page intent contracts and state visibility contracts during implementation.
- Treat this file as projection from prototype truth, not an editable source of truth.
