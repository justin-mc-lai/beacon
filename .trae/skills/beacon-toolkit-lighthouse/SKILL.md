---
name: beacon-toolkit-lighthouse
description: Use when the user wants a fast, single-file analysis of a target project, open-source repo, third-party package, infra chain, or feature slice using Mermaid plus concise explanation, without entering Beacon's main workflow.
---

# Beacon Toolkit Lighthouse

This skill routes analysis work through Beacon's optional `Toolkit Lighthouse` surface.
It is diagram-first and one-page by default.

## Use for

- fast repo ramp-up
- open-source library analysis
- third-party package decomposition
- infrastructure chain mapping
- feature slice breakdown
- single-file system maps similar to `system-architecture-map`

## Operator rule

Keep Toolkit Lighthouse outside the main workflow by default.

Prefer:

- produce exactly one Markdown artifact
- default output to `.beacon/analysis/<slug>.md`
- for Beacon source iterations, also produce a versioned deliverable:
  - `docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md`
- use Mermaid first, then concise explanation
- keep the explanation short and decision-oriented
- distinguish `Confirmed Facts` from `Inferred Structure`
- include key source refs and key files
- keep recommendations minimal and actionable

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`

unless the user explicitly asks to continue into the main Beacon workflow.

## Hard Constraints

- One page only.
- No requirement drafting.
- No implementation plan.
- No QA plan.
- No automatic freeze or writeback.
- No broad essaying.
- No hidden second artifact.
- No more than 3 Mermaid diagrams.
- Prefer flowcharts and state machines over prose.
- Keep `Confirmed Facts` and `Inferred Structure` strictly separated.

## Recommended Output Shape

```markdown
# <Target> Lighthouse Map

## 1. Summary
## 2. Scope
## 3. Mermaid Maps
## 4. Key Entry Points
## 5. Key Modules / Subsystems
## 6. Dependencies / Infra Chain
## 7. Confirmed Facts
## 8. Inferred Structure
## 9. Open Questions / Risks
## 10. Recommended Next Steps
```

## Writing Rules

- Use short sections and short bullets.
- Keep narrative to a minimum.
- State the main conclusion early.
- If the analysis expands toward PRD, user-story, test-case, or implementation work, stop and hand off conceptually instead of widening the report.
- For Beacon source iterations, always include the versioned artifact path in the final output.

## Examples

- 适用例：
  - “先给我一页图，把这个 repo / 包 / 基础设施链路讲清楚。”
  - “我现在不要 PRD，只要一个单页结构图和关键入口说明。”
- 不适用例：
  - “我要正式进入 requirement freeze 或 implementation plan。” -> 应转入主工作流 surface

## Cold-start anchors

- `Toolkit Lighthouse` 是单页分析面，不是 requirement 或 execution surface。
- 目标是快速建立结构理解，而不是产出完整方案包。
- 一旦问题开始要求正式 truth、测试闭环或执行计划，就应停止扩写并路由回主链。
