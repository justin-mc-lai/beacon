---
slug: legacy-project-v152-cutover
version: v1.5.2
status: draft
language: zh
canonical_refs:
  prd: docs/beacon/v1.5.2/features/legacy-project-v152-cutover/truth.md
  user_story: docs/beacon/v1.5.2/features/legacy-project-v152-cutover/truth.md
  test_case: docs/beacon/v1.5.2/features/legacy-project-v152-cutover/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Feature Truth: Legacy Project v1.5.2 Cutover

## Overview

旧 Beacon 项目从 legacy triptych 或 mixed truth state 切到 v1.5.2 时，Beacon 必须提供一个可发现、分阶段、fail-closed 的 cutover transaction。目标是让操作者不用手动拼接 `materialize-feature-package`、`validate-feature-package`、`truth-map verify`、`doctor metadata verify` 和 agent-surface refresh，也不会在旧 truth authority 下误以为 refreeze 已经完成 v1.5.2 迁移。

## Problem

`beacon-change-refreeze` 只负责 accepted post-freeze refreeze closure。对旧项目来说，用户实际意图经常是“把项目切到 v1.5.2 的 feature package 和 project governance 能力后继续 refreeze”。如果 skill 直接路由 `beacon change ... --refreeze-chain`，旧 triptych 可能继续工作，但 v1.5.2 的 package authority、governance MD 和 agent guidance 没有闭合。

## Goal

提供 legacy/mixed project cutover 入口，使 Beacon 在 refreeze、freeze、implement 前能识别旧真相源和治理面缺口，给出一键分阶段迁移路线，并在迁移成功后恢复原始操作者意图。

## Non-Goals

| Item | Rationale |
|---|---|
| 删除 legacy triptych | 旧文件可作为 absorb/rebuild/archive evidence；删除会增加迁移风险 |
| 让 brainstorm 成为 truth | Research 只作为 support evidence，正式承诺必须进入 feature package |
| 让 cutover 绕过 clarity/freeze | Cutover 只闭合真源和治理前置条件，不能替代 requirement clarity |
| 用 sqlite/JSON 写回治理 truth | v1.5.2 project governance MD 是 authority，sqlite/JSON 只是 projection/runtime state |

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | legacy-detection | Cutover preflight detects legacy or mixed truth state, including old `prd/`, `user-story/`, `qa/test-cases/` surfaces, missing feature package files, missing governance MD, missing projection, and stale agent-surface guidance. |
| AC-002 | refreeze-intercept | `beacon-change-refreeze` must detect legacy/mixed state before refreeze and route to cutover instead of presenting `beacon change ... --refreeze-chain` as sufficient. |
| AC-003 | phased-migration | Beacon exposes a human-facing one-command cutover wrapper that runs or reports phases: inventory, package materialize/validate, truth-map verify, governance verify/projection, agent-surface refresh, and resume. |
| AC-004 | package-authority | Requirement package cutover must validate `features/<slug>/{truth,tests,tasks,evidence}.md` as v1.5.2 package authority; legacy triptych can be absorb/rebuild/archive-only and cannot win authority. |
| AC-005 | governance-verify | Project governance cutover must verify `docs/beacon/governance/project-version-governance.md` and generated sqlite/runtime projection, failing closed on missing version contract or projection drift. |
| AC-006 | stale-skill-detection | Cutover must detect stale installed/project skills or agent rules that still present old triptych as normal v1.5.2 truth authority and route to `doctor setup-agent-surface` / verify. |
| AC-007 | fail-closed-mixed-authority | Freeze, refreeze, implement, QA, and release must fail closed while package authority, governance MD, or agent-surface verification is incomplete or contradictory. |
| AC-008 | resume-original-intent | After successful cutover, Beacon resumes the original operator intent, such as refreeze, without requiring the operator to rediscover the next command. |
| AC-009 | tasks-plan-alignment | For v1.5.2 package-authoritative features, `beacon implement plan` must consume `features/<slug>/tasks.md` as the requirement-owned task intent and may return a draft/skeleton plan even when execution admission is blocked; implementation progress must write to execution/progress artifacts, not mutate `tasks.md` checkbox state. |
| AC-010 | friction-routing-simplification | Beacon must close the four accepted friction findings with the lowest-cognitive-load route: keep `truth-cutover` as a CLI/machine repair transaction instead of adding a new default public skill, route existing human surfaces to it, add explicit `doctor truth-source-mismatch` diagnostics and repair commands, and regression-test the `technical_review_contract` root fix plus change CLI version stability. |

## Transaction Shape

```text
detect legacy/mixed truth state
  -> classify required migration phases
  -> materialize/validate feature package
  -> install v1.5.2 version governance materials
  -> verify resolver + doctor metadata
  -> refresh agent surfaces
  -> resume original refreeze/freeze/implement intent
```

## Task Ledger Boundary

`features/<slug>/tasks.md` is the requirement-owned task intent surface for v1.5.2 feature packages. `beacon implement plan` must read it through the resolver and expose task alignment before or alongside execution admission gates.

`tasks.md` is not the implementation progress store. Runtime completion, blocked task state, evidence refs, and execution handoff state must be written to implementation plan/progress artifacts. A missing technical review contract may block execution admission, but it must not hide whether the package task ledger was resolved and aligned.

## Friction Closure Model

The accepted friction analysis is requirement material for this cutover feature. Beacon should simplify user mental load by exposing fewer human concepts while keeping the machine transaction strong and explicit.

| Friction | Decision | Required closure |
|---|---|---|
| `beacon-truth-cutover skill` | Do not add a standalone default public skill when the existing CLI and existing skills can route the operator. | `truth-cutover` remains a CLI/machine repair transaction. `change-refreeze`, implement, QA, release, doctor, and help surfaces may recommend `beacon truth-cutover run ...` when legacy or mixed authority is detected. |
| `technical_review_contract` | Treat as a root normalization regression, not a new user-facing concept. | Contract lookup/build paths must resolve from the project root consistently, including relative `--project .`, and focused tests must prove the blocked implement plan still exposes task alignment. |
| `doctor truth-source-mismatch` | Accept as an open diagnostic gap. | Doctor must emit an explicit `truth_source_mismatch` reason when feature package frontmatter, truth-map projection, machine mirrors, legacy triptych, or governance authority disagree, and must print exact repair routes such as `truth-map verify`, `truth-map rebuild-machine`, `truth-cutover run`, and `validate-feature-package`. |
| `change CLI version drift` | Treat as a route/version normalization regression, not a new workflow. | `beacon change ... --project . --version v1.5.2` must preserve the requested version and recommended refreeze command after root resolution. |

The human-facing principle is: one repair command can exist, but every normal Beacon surface must explain why it is needed and where to resume. New public skills are only justified if an existing skill family cannot route the user without adding ambiguity.

## Authority

This feature package is the requirement authority. The upstream support research is `docs/beacon/v1.5.2/research/legacy-project-v152-cutover-convergence.md`.
