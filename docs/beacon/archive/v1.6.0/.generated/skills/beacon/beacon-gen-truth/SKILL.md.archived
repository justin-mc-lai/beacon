---
name: beacon-gen-truth
description: Beacon v1.6.0 generator skill migrated from `beacon-truth`. Use when the user wants Beacon's preferred v1.5.2+ truth umbrella for package-authoritative requirement definition, acceptance, coverage, or governed truth change routing.
---

# Beacon Generator Truth Package

## Overview

`beacon-gen-truth` is the preferred v1.5.2+ human-facing umbrella for Beacon feature truth work.

It is a routing and mode-selection surface, not a new authority. The authority remains the resolver-selected Markdown feature package:

- `features/<slug>/truth.md` for requirement definition and acceptance framing
- `features/<slug>/tests.md` for coverage truth
- `features/<slug>/tasks.md` for task ledger
- `features/<slug>/evidence.md` for evidence index

## Modes

- `truth.define`: define problem, scope, goals, boundaries, promised surface, and freeze readiness. Canonical v1.6.0 route: `beacon-gen-truth`.
- `truth.acceptance`: compile story intent and acceptance criteria into executable acceptance truth. Canonical v1.6.0 route: `beacon-gen-truth`.
- `truth.coverage`: compile acceptance criteria into verifiable coverage rows in `features/<slug>/tests.md`. Canonical v1.6.0 route: `beacon-gen-truth`.
- `truth.change`: route frozen truth changes through `beacon-gen-change` or accepted post-freeze closure through `beacon-gen-refreeze`.

These modes preserve distinct decision work. Do not flatten definition, acceptance, coverage, and change into one freeform truth surface.

## When To Use

- the user asks for the current Beacon truth surface under v1.5.2+
- the user is confused by old `prd`, `user-story`, or `test-case` names after package-authoritative cutover
- requirement work needs mode selection before implementation
- accepted support findings need routing back to truth or change

## Boundary

- not a truth authority
- not a truth source
- not a gate source
- not a new lifecycle stage
- not a lifecycle stage
- does not execute QA
- does not issue release verdicts
- does not make `brainstorm`, `change-refreeze`, QA, or release into truth authoring stages
- does not delete canonical v1.6.0 routees such as `beacon-gen-truth`

## Workflow / Decision Loop

1. Resolve the feature truth map before reading or writing requirement material:

```bash
beacon truth-map resolve <feature> --project . --version v1.5.2 --json
```

2. Choose the narrow mode:

```text
truth.define      -> features/<slug>/truth.md
truth.acceptance  -> features/<slug>/truth.md
truth.coverage    -> features/<slug>/tests.md
truth.change      -> beacon-gen-change / beacon-gen-refreeze
```

3. Route through the canonical v1.6.0 route when an existing skill is the more precise operator surface.
4. Preserve closure:

```text
support research
  -> truth.define
  -> truth.acceptance
  -> truth.coverage
  -> requirement_clarity
  -> freeze
  -> implement
  -> qa
  -> release
```

## Canonical v1.6.0 Routes

- `beacon-gen-truth` remains the canonical v1.6.0 route for `truth.define`.
- `beacon-gen-truth` remains the canonical v1.6.0 route for `truth.acceptance`.
- `beacon-gen-truth` remains the canonical v1.6.0 route for `truth.coverage`.
- `beacon-gen-change` remains the governed route for frozen truth changes.
- `beacon-gen-refreeze` remains the support route for accepted post-freeze refreeze closure.

Use the new mode names when explaining lifecycle shape. Use compact skill names for host-visible routing; use CLI commands only for stable compatibility command surfaces.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- resolver-selected `features/<slug>/truth.md`
- resolver-selected `features/<slug>/tests.md`
- resolver-selected `features/<slug>/tasks.md`
- resolver-selected `features/<slug>/evidence.md`
- support research when present

## Decision Protocol

- If problem, scope, goals, boundaries, or promised surface are open, choose `truth.define`.
- If acceptance criteria need to be compiled or sharpened, choose `truth.acceptance`.
- If coverage rows, negative paths, boundary cases, or regression proof are weak, choose `truth.coverage`.
- If frozen truth must change, choose `truth.change`.
- If the user only wants read-only challenge, route to `beacon-pln-brainstorm` and require promotion back to truth before freeze.
- If the user asks for implementation, QA, or release, leave `beacon-gen-truth` and route to `beacon-gen-implement`, `beacon-eval-qa`, or `beacon-eval-release`.

## Anti-Inertia Notes

- `beacon-gen-truth` is not permission to bypass resolver-first package truth.
- `truth.md` owns requirement and acceptance framing; it does not own executable coverage matrices.
- `features/<slug>/tests.md` owns coverage truth; generated QA JSON is projection state.
- Canonical v1.6.0 routes are stable public surfaces, not legacy authority.
- Support output must be adopted into the package before it becomes requirement truth.

## Backstop CLI

- `beacon truth-map resolve <feature> --project . --version v1.5.2 --json`
- `beacon prd ...` for `truth.define` compatibility
- `beacon user-story ...` for `truth.acceptance` compatibility
- `beacon test-case ...` for `truth.coverage` compatibility
- `beacon change ...` for `truth.change`

## Examples

- “这个 feature 的 scope/promise 还没清楚。” -> `truth.define` / `beacon-gen-truth`
- “我要把承诺面编译成 AC。” -> `truth.acceptance` / `beacon-gen-truth`
- “AC 有了，但测试覆盖不够。” -> `truth.coverage` / `beacon-gen-truth`
- “冻结后的承诺要变。” -> `truth.change` / `beacon-gen-change`
- “只是想先 challenge 一下，不想写 truth。” -> `beacon-pln-brainstorm`

## Cold-start Anchors

- v1.5.2+ preferred truth lifecycle is `truth.define -> truth.acceptance -> truth.coverage`.
- The Markdown feature package is the source of truth; `beacon-gen-truth` is a route umbrella.
- Old public skill names do not remain host-visible routees in v1.6.0; compact names are canonical.


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 generator skill。
禁止自证完成，禁止给 QA/release verdict，禁止把 placeholder/docs-only/fake-runner/zero-assertion/placeholder-evidence 当成交付闭环。
只能在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact。
如需判断是否通过，必须路由到 evaluator。

## v1.6.0 Harness Migration

- Harness：`generator`。
- 来源迁移：`beacon-truth` -> `beacon-gen-truth`。
- 主要作用：package-authoritative 需求真相总入口。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`generator`。
- 来源迁移：`beacon-truth` -> `beacon-gen-truth`。
- 主要作用：package-authoritative 需求真相总入口。
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
