---
name: beacon-gov-lighthouse
description: Beacon v1.6.0 governor skill migrated from `beacon-toolkit-lighthouse`. Use when the user wants a fast, single-file analysis of a target project, open-source repo, third-party package, infra chain, or feature slice using Mermaid plus concise explanation, without entering Beacon's main workflow.
---

# Beacon Governor Lighthouse

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
  - `docs/beacon/<version>/execution/beacon-gov-lighthouse-<slug>.md`
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


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-lighthouse` -> `beacon-gov-lighthouse`。
- 主要作用：快速源码和仓库分析。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-lighthouse` -> `beacon-gov-lighthouse`。
- 主要作用：快速源码和仓库分析。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
