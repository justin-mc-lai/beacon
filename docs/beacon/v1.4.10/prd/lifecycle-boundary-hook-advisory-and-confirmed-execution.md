# PRD: Lifecycle Boundary Hook Advisory And Confirmed Execution

**Feature**: `lifecycle-boundary-hook-advisory-and-confirmed-execution`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## Overview

Project lifecycle hooks are already governed as project-level contracts. This feature adds a bounded advisory layer at lifecycle boundaries so Beacon can tell operators which hook follow-up is available after a stage reaches the appropriate state, without hiding side-effect execution or turning hook evidence into lifecycle truth.

## Context

This requirement extends `project-lifecycle-hook-skill-toolkit-contract`. The earlier contract intentionally shipped a manual toolkit. This change keeps that safety model while adding lifecycle-boundary discovery, planning, and recommendation so operators do not lose project follow-up after release readiness passes.

## 1. 问题

The Beacon source release flow now has a governed `post_release` hook for local install and agent surface verification. The hook works when manually invoked, but the release surface does not make the next action obvious after `release check` passes.

This creates two failure modes:

1. Operators may miss required project follow-up because the hook command is not surfaced at the lifecycle boundary.
2. A naive fix could silently execute side-effect hooks after release and undermine Beacon's unique truth chain.

Beacon needs automatic hook advice, not hidden side-effect automation.

## 2. 目标

- AC-001: At lifecycle boundaries, Beacon discovers applicable enabled project hooks from `docs/beacon/hooks/<hook-id>.md`.
- AC-002: When release readiness passes, Beacon surfaces applicable `post_release` hook plans and a confirmed-run recommended command.
- AC-003: Beacon may automatically plan hooks and may dry-run hooks only when no side-effect execution occurs.
- AC-004: `manual_confirmed` hooks without `--confirm` remain blocked with an explicit reason code.
- AC-005: Hook evidence is recorded as support/runtime evidence and cannot produce or alter QA, release, gate, freeze, PRD, user-story, or test-case truth.
- AC-006: Help/status surfaces can display hook recommendations and latest evidence without creating a new lifecycle stage.
- AC-007: Hidden side-effect auto-run fails closed.

## 3. 设计原则

### 3.1 Advisory Before Execution

Beacon may automatically discover and explain hook follow-up. It must not silently execute side-effect actions.

### 3.2 Confirmation For Side Effects

Any hook that changes local installation, external environments, UAT pipelines, notifications, data, or agent surfaces must require explicit operator confirmation.

### 3.3 Evidence Is Support, Not Truth

Hook evidence can help operators understand follow-up status, but only the existing Beacon truth, QA, release, and gate surfaces decide lifecycle closure.

### 3.4 Project-Level Contract Stays Project-Level

Hook truth remains under `docs/beacon/hooks/`. Versioned docs freeze the requirement for advisory behavior, not duplicate hook contracts.

## 4. 范围

### In Scope

- Hook discovery by lifecycle boundary.
- Release check advisory for `post_release` hooks when release readiness passes.
- Recommended command generation for confirmed hook execution.
- Help/status projection of hook advisory and latest hook evidence.
- No-side-effect planning/dry-run behavior.
- Regression tests for release advisory, hidden auto-run blocking, confirmed execution, and evidence authority boundaries.

### Out Of Scope

- Automatic side-effect execution.
- Lifecycle auto-advance based on hook result.
- Hook-created release or QA verdicts.
- Arbitrary command execution from Markdown hook templates.
- Making fixture hooks global defaults for every project.

## 5. 功能需求

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must provide a utility that selects enabled hook contracts for a requested finite hook code. |
| FR-002 | AC-002 | `release check` must include a release follow-up advisory when release readiness passes and an applicable `post_release` hook exists. |
| FR-003 | AC-002 | The advisory must include hook id, hook code, trigger policy, plan status, blocked state, evidence paths, and a recommended confirmed-run command. |
| FR-004 | AC-003 | Automatic planning must not execute side effects and must mark `side_effect_executed` as false. |
| FR-005 | AC-003 | Automatic dry-run may write runtime hook evidence only when `dry_run` is true and must not run side-effect follow-up. |
| FR-006 | AC-004 | Running a `manual_confirmed` hook without `--confirm` must remain blocked with `manual_confirmation_required`. |
| FR-007 | AC-005 | Hook advisory and evidence must be marked `truth_authority: false` and `runtime_evidence_only: true`. |
| FR-008 | AC-006 | Help/status surfaces may display hook advisory data but must not expose it as a lifecycle stage or verdict. |
| FR-009 | AC-007 | Hidden side-effect auto-run attempts must fail closed with `hidden_auto_run_not_allowed` or `manual_confirmation_required`. |

## 6. 边界、分层、恢复

### 边界

Hook advisory is a support surface. It can recommend and evidence follow-up but cannot become PRD truth, user-story truth, test-case truth, QA verdict, release verdict, gate verdict, or freeze state.

### 分层

The lifecycle remains `change -> PRD -> user-story -> test-case -> implement -> QA -> release`. Hook advisory attaches at boundary points as support evidence and does not add a required lifecycle stage.

### 恢复

If hook admission fails, Beacon must report a hook-specific reason and route to the hook failure route. If release readiness fails, Beacon must not surface a confirmed post-release execution recommendation as if release passed.

## 7. Success Metrics

- Release output tells the operator exactly which confirmed hook command to run after release readiness passes.
- No release, QA, or gate verdict changes when hook evidence is created.
- A confirmed hook run can install/verify Beacon source follow-up.
- The same hook without confirmation remains blocked.
- Help/status summarize hook follow-up as support evidence only.

## 8. 验收标准

- Release-ready output includes a `post_release` hook advisory for `beacon-post-release-local-install`.
- The advisory includes a confirmed-run command and does not execute installation by itself.
- Running the hook without `--confirm` blocks with `manual_confirmation_required`.
- Running the hook with `--confirm` writes evidence and performs the restricted follow-up.
- Hook evidence is marked as support/runtime evidence and does not change release readiness, QA verdict, gate verdict, or freeze truth.

## 9. 风险与缓解

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Hook advisory is mistaken for release closure | False completion signal | Label advisory as support evidence only and keep release verdict unchanged. |
| Side-effect hook runs silently | Local or external environment damage | Require explicit `--confirm`; hidden auto-run fails closed. |
| Hook becomes a new lifecycle stage | Beacon lifecycle sprawl | Keep hooks at finite boundaries and never advance stages from hook result. |
| Project-specific hook becomes global default | Cross-project breakage | Discover only project-local `docs/beacon/hooks` contracts. |
