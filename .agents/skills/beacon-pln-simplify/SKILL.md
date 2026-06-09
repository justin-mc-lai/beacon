---
name: beacon-pln-simplify
description: Beacon v1.6.0 planner skill migrated from `beacon-design-simplify`. Use when the user wants Beacon-owned support-only first-principles simplicity audit through the deterministic `beacon design route simplify` contract. Helps operators escape engineer-thinking, extract core user scenarios, detect abstraction-to-UI mapping drift, deduplicate information, and quantify complexity burden.
---

# Beacon Planner Design Simplify

## Overview

This is a host-visible child skill for the Beacon design `simplify` route.

It is Beacon-native (no external upstream dependency). It provides a first-principles simplicity audit that challenges whether a design is unnecessarily complex before entering explore, system, review, or polish routes.

## First Principles

Beacon design 的第一要义：为懒人简化。用户正是因为懒才用产品——想要最简单、最少的输入完成目标。复杂性是敌人。

## When to Use

- Before entering design exploration for a feature — ask "should this be simpler?"
- When a design feels over-engineered but each piece justifies itself in isolation
- When the same concept appears in multiple UI sections
- When data model structure leaks into the UI layer
- When you need a quantified complexity burden score

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design audit
- does not replace `beacon-gen-design`
- does not depend on any external upstream skill (Beacon-native)
- output is advisory — does not block implementation by itself

## Capabilities

| Capability | Description |
| --- | --- |
| `lazy_user_axiom` | Assert "users are lazy" as the first principle. Challenge any complexity that exceeds the minimum necessary input. |
| `core_scenario_extraction` | Strip feature packaging to extract the real core scenario (e.g., "10-second court-side fee split" vs "ball inventory management"). |
| `engineer_abstraction_detection` | Identify UI layers that directly mirror internal data models rather than user mental models. |
| `information_deduplication` | Detect the same concept appearing in multiple UI sections. |
| `complexity_burden_score` | Quantify screen count, input dimensions, and cognitive load. |

## Workflow / Decision Loop

- run `beacon design route simplify "<feature>" --project . --version auto --json`
- execute the five capability checks against the target feature
- produce `simplicity_audit_findings`, `reduction_recommendations`, `core_scenario_map`, and `complexity_burden_report`
- route accepted findings:
  - non-promise facts → `PRODUCT.md` / `DESIGN.md` truth binding
  - prototype input → `beacon prototype adapt`
  - promise-changing facts → `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Decision Priority

```text
1. Core scenario detection (highest)
   → If no core scenario defined → block audit
   → If feature deviates from core scenario → flag

2. Complexity burden scoring
   → If > 5 input dimensions or > 1.5 screens → flag complexity drift

3. Information deduplication
   → If same concept in ≥ 2 UI sections → flag duplication

4. Engineer abstraction detection
   → If UI layer mirrors internal data model → flag abstraction leak
```

## Acceptance Test

> 用户在核心场景下，能在 10 秒内完成目标操作吗？

Target: form ≤ 1.5 screens, core inputs ≤ 5 fields.

## Verification

- route payload reports `route=beacon-pln-simplify`, `intent=simplify`, and `upstream=beacon-native`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- route payload lists five capabilities
- no external upstream dependency

## Evidence Produced

- route contract payload
- simplicity audit findings
- reduction recommendations
- core scenario map
- complexity burden report

## Operator Rule

Prefer:

```bash
beacon design route simplify "<feature>" --project . --version auto --json
```

If audit findings are accepted and non-promise:

```bash
# bind to project design truth
```

If audit findings change product promise:

```bash
beacon change "<feature>" --project . --version auto --reason "simplify audit changed requirement promise" --refreeze-chain
```

## Examples

- 适用例:
  - "在进入设计探索之前，先对这个 feature 做一次简洁审计。"
  - "这个界面感觉过度设计了，但我说不清哪里不对——帮我量化一下。"
  - "我想知道核心场景到底是什么，以及当前设计偏离了多远。"
- 不适用例:
  - "我要正式做 UX review。" → 应去 `beacon-pln-design`
  - "我要生成 prototype。" → 应去 `beacon-gen-prototype`
  - "我要发布。" → 应去 `beacon-eval-release`


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 planner skill。
禁止调用 implementation/generator/evaluator/release 类 skill。
禁止写代码、搭脚手架、修改 package truth、修改 `.machine/`、给 QA/release verdict。
你的唯一产出是 research/planning artifact、gap/risk 分析、湖/海判断和 route recommendation。
如需进入 truth/change/refreeze/generate/evaluate，必须停止并路由，等待用户确认。

## v1.6.0 Harness Migration

- Harness：`planner`。
- 来源迁移：`beacon-design-simplify` -> `beacon-pln-simplify`。
- 主要作用：简化审计与范围收敛。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-design-simplify` -> `beacon-pln-simplify`。
- 主要作用：简化审计与范围收敛。
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
