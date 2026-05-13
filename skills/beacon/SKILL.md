---
name: beacon
description: Use when you need Beacon's evidence-first product workflow through its current human-facing surface. Beacon should act as the primary router for requirement truth, implementation, QA evidence, release decisions, and support guidance.
metadata:
  author: Beacon CLI
  version: "1.4.0"
  organization: Beacon
  date: April 2026
  abstract: Stable wrapper for Beacon's human-facing workflow surface, routing users into the right requirement, execution, verification, and support skills without exposing internal runtime detail by default.
---

# Beacon Skill

Beacon is an evidence-first product workflow for keeping requirement truth, implementation, QA evidence, and release decisions inside one versioned system.

This file is the stable human-facing wrapper for `skills/beacon/`. Its job is to define Beacon's default entry surface, route to the right skill, and hold the minimum boundaries that should remain stable even when runtime internals evolve.

Prefer the installed `beacon` CLI. Repo-local wrappers may exist in vendored setups, but they are compatibility detail, not the default human contract.

## What Beacon Is

Beacon's core promise is simple:

- keep requirement truth explicit
- keep execution routed through one public implementation surface
- keep QA and release evidence layered and auditable
- keep support surfaces available without turning them into parallel main stages

Beacon is not just a command catalog. It is a routing and evidence discipline.

## Human Surface

Humans should primarily remember the 7+3 surface.

Primary workflow:

- `prd`
- `user-story`
- `test-case`
- `prototype`
- `implement`
- `qa`
- `release`

Support and guidance:

- `help`
- `status`
- `doctor`
- `archive`

Optional support surfaces stay opt-in:

- `brainstorm`
- `deep`
- `learn`
- `ceo-review`
- `design-review`
- `prd-bootstrap`
- `toolkit-lighthouse`
- `toolkit-metadata`
- `toolkit-branch-governance`
- `friction-intake`
- `real-project-validation`

## Host and Dependency Defaults

Beacon should be judged inside the current host context only.

- Do not turn host/runtime selection into a default human decision.
- Do not require external skill repos, external plugins, or external runtimes as Beacon's default prerequisite.
- External capabilities may exist, but they are compatibility planes, not Beacon's default dependency plane.
- Do not expose internal team/subagent/runtime lanes unless the user explicitly asks for internals.

## Human vs Machine Output

Human-facing output should stay concise and action-oriented:

- current status
- blocking reason
- recommended next step
- fallback or repair route when relevant

Machine-facing and audit-facing output should remain complete:

- reason codes
- evidence refs
- diagnostics
- artifact paths
- runtime or transaction metadata

Beacon should absorb complexity into machine-readable surfaces first, then project only the minimum useful action layer to humans.

## Public Skill Routing

Route by decision surface, not by internal mechanism.

- Requirement definition, ambiguity, or promised surface: `beacon-prd`
- Story compilation and acceptance truth: `beacon-user-story`
- Coverage truth and verifiable scenarios: `beacon-test-case`
- Conditional UX/UI handoff before implementation: `beacon-prototype`
- Frozen truth revision or supplement after freeze: `beacon-change`
- Implementation execution: `beacon-implement`
- Verification and evidence closure: `beacon-qa`
- Release go/no-go judgment: `beacon-release`
- Blocked or unsure next step: `beacon-help` or `beacon-status`
- Context drift, package drift, or environment repair: `beacon-doctor`
- Historical truth isolation: `beacon-archive`

Use support surfaces when the user needs challenge, convergence, analysis, or governance without silently entering the main workflow.

## Current Version Anchors

Keep only the minimum current anchors here:

- current package version: `1.4.3`
- current release/docs line: `docs/beacon/v1.4.3/`
- if a project pins `docs/beacon/VERSION`, follow that pinned docs line for local truth

More detailed runtime architecture, release-note history, and migration context belong in versioned docs, not in this wrapper.

## Deep References

When deeper context is needed, start here:

1. [`docs/beacon/v1.4.3/SUMMARY.md`](../../docs/beacon/v1.4.3/SUMMARY.md)
2. [`docs/beacon/v1.4.3/execution/index.md`](../../docs/beacon/v1.4.3/execution/index.md)
3. [`docs/beacon/v1.4.3/release/v1.4.3.md`](../../docs/beacon/v1.4.3/release/v1.4.3.md)

Do not treat this wrapper as the full runtime manual or release note.

## Examples

- 适用例：
  - “我想用 Beacon 作为主工作流入口，但还不知道应该先进哪条 surface。”
  - “我需要一个稳定的总入口，把 requirement、implementation、qa、release 和 support surface 路由清楚。”
- 不适用例：
  - “我现在已经明确知道要去哪条具体 skill，而且只想看那条 skill 的边界。” -> 应直接进入对应子 skill

## Cold-start anchors

- Beacon 的主 skill 主要卖一个 promise: 帮宿主进入正确 surface，而不是解释全部 runtime 历史。
- 主 `beacon` skill 不是总 runbook、总 release note，也不是完整 operator manual。
- 当主 skill 开始承载过多版本叙事、命令矩阵或内部运行细节时，应把这些内容下沉到版本化 docs 或具体子 skill。
