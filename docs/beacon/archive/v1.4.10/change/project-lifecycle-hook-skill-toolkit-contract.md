# Change: Project Lifecycle Hook Skill Toolkit Contract

**Feature**: `project-lifecycle-hook-skill-toolkit-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## 1. Change Reason

Beacon operators repeatedly need project-specific actions at stable lifecycle boundaries: Beacon itself needs local CLI and agent skill installation after release, Rolo needs UAT delivery after implementation, and Rolo QA may need Debug Lab diagnostics when validation is blocked.

Today those actions live in operator memory or project-specific manual skill calls. They are useful, but they are not governed by Beacon's lifecycle boundary, evidence model, or truth-authority rules.

This change freezes a project-level hook contract and manual toolkit boundary so project-specific delivery actions can be planned, dry-run, confirmed, evidenced, and routed without becoming a new Beacon lifecycle stage.

## 2. Accepted Change

Freeze `project-lifecycle-hook-skill-toolkit-contract` as an independent P1 feature:

- Hook definitions are project-level single Markdown files under `docs/beacon/hooks/<hook-id>.md`.
- Versioned docs may record research, requirements, and implementation evidence, but must not copy hook truth under `docs/beacon/<version>/hooks/`.
- Hook execution is limited to finite hook codes and explicit admission.
- The first frozen contract supports manual toolkit behavior only: list, plan, dry-run, confirmed run, status, and disable.
- Hook output is runtime/support evidence only; it cannot rewrite requirement truth, QA verdict, release verdict, or gate truth.

## 3. Scope

### In Scope

- Project-level hook Markdown contract shape.
- Finite hook code taxonomy.
- Manual confirmation and dry-run admission rules.
- Hook evidence paths and read-model boundaries.
- Human-facing toolkit behavior for `beacon-project-hooks` / `beacon hooks`.
- Fixture contracts for Beacon post-release local install, Rolo post-implement UAT delivery, and Rolo QA Debug Lab.
- Help/status/release support visibility for hook blocker and evidence summaries.

### Out Of Scope

- Hidden automatic hook execution.
- Arbitrary shell hooks or unbounded hook codes.
- Version-scoped hook truth under `docs/beacon/<version>/hooks/`.
- Hook-created PRD, user-story, test-case, QA verdict, release verdict, or freeze state.
- Making hooks a required lifecycle stage for all Beacon projects.
- Hard-coding Rolo or Beacon project commands into Beacon core defaults.
- Executing implementation, QA, release, UAT deployment, local installation, or Debug Lab as part of this refreeze.

## 4. Route Decision

- This accepted research enters v1.4.10 as a separate P1 feature.
- The first implementation must prioritize contract, parser/admission, dry-run planning, evidence projection, and fixture coverage.
- Runtime hook execution may exist only behind explicit `--confirm` / manual confirmation policy.
- Downstream implementation may start only after this refreeze transaction reports complete.

## 5. Freeze Deliverables

- `docs/beacon/archive/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/source-architecture/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/change/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/prd/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/user-story/project-lifecycle-hook-skill-toolkit-contract.md`
- `docs/beacon/archive/v1.4.10/qa/test-cases/project-lifecycle-hook-skill-toolkit-contract.md`

## 6. Boundary

This change freezes requirement truth only. It does not execute hooks, install global tools, deploy UAT services, run Debug Lab, implement runtime code, run QA, or pass release.
