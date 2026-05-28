---
name: beacon-design
description: Use when the user wants Beacon-owned support-only design exploration, design-system planning, UI/UX review, polish, screenshot/reference extraction, design reference lookup, or upstream design capability bootstrap while preserving Beacon truth binding.
---

# Beacon Design

## Overview

`beacon-design` is Beacon's support-only design route surface.

It preserves the useful intent split from `ui-ux-dev` while adding Beacon truth boundaries:

- `explore` and `extract` preserve `vibe-to-ui`.
- `system` preserves `ui-ux-pro-max`.
- `review` and `polish` preserve `impeccable`.
- `library` preserves `awesome-design-md` as reference-only.
- `bootstrap` checks upstream installed/mirror/bootstrap availability.

## When to Use

- UI direction is unclear and needs exploration.
- A screenshot or reference needs structure extraction.
- A version-wide component system or design baseline is needed.
- Existing UI needs UX review or ship-readiness polish.
- The operator needs curated design references.
- A machine needs design upstream capability admission checks.

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not replace `beacon-change`
- does not replace `beacon-prototype`
- does not treat upstream design skills as Beacon truth
- does not treat `awesome-design-md` as an execution skill

## Workflow / Decision Loop

- normalize the request into `explore`, `system`, `review`, `polish`, `extract`, `library`, or `bootstrap`
- use `beacon design route <intent> "<feature>" --project . --version auto --json` to resolve the deterministic contract
- draft design truth candidates under Beacon version-wide design surfaces when needed
- route accepted UI/UX facts to `beacon prototype adapt`
- route promise-changing design facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted design facts are truth-bound

## Common Rationalizations

- “design skill 输出了，所以就是 truth。” -> 不允许；accepted facts still need Beacon truth binding.
- “参考库里有案例，可以直接当项目设计规范。” -> 不允许；`awesome-design-md` is reference-only.
- “bootstrap 通过了，所以 release 可以过。” -> 不允许；bootstrap is capability admission only.
- “review/polish 是小建议，不用看 PRD/user-story/test-case。” -> 不允许；promise-changing facts route to change/refreeze.

## Red Flags

- accepted UI/UX facts exist but no prototype adapter binding exists
- `awesome-design-md` is used as an execution authority
- upstream skill output is copied into implementation without Beacon truth refs
- design support becomes a mandatory lifecycle stage for non-UI features

## Verification

- `beacon design contract --project . --version auto --json` lists all seven routes
- route outputs mark `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- `library` is reference-only
- `bootstrap` is capability-admission-only
- accepted design results can be bound through `beacon prototype adapt`

## Evidence Produced

- route contract payload
- version-wide design truth draft paths
- capability admission payload
- support-only design plan

## State Updated

- no lifecycle state directly
- optional version-wide design truth drafts when the CLI is explicitly called with `design truth --write`
- optional prototype adapter binding only through `beacon prototype adapt`

## Gate Impact

- no direct release gate verdict
- can block downstream execution only when accepted design facts remain unbound by Beacon truth

## Operator Rule

Prefer:

```bash
beacon design route review "<feature>" --project . --version auto --json
beacon design contract "<feature>" --project . --version auto --json
beacon design truth --project . --version auto --write --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```

## Examples

- 适用例：
  - “帮我给这个功能出 UI 方向，但要能进 Beacon truth。”
  - “这个界面做一次 UX review，结论如果接受要能写回。”
  - “检查一下 design 上游能力在这台机器是否可用。”
- 不适用例：
  - “我要直接发布。” -> 应去 `beacon-release`
  - “我要让参考库直接决定项目设计规范。” -> 不允许
