# Change: Lifecycle Boundary Hook Advisory And Confirmed Execution

**Feature**: `lifecycle-boundary-hook-advisory-and-confirmed-execution`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## 1. Change Reason

Beacon v1.4.10 introduced project-level lifecycle hook contracts and a manual toolkit. Real use of the Beacon source release showed a gap: after release readiness passes, operators expect Beacon to surface the post-release local install follow-up without having to remember the hook id or command.

The accepted change is not hidden automatic execution. It is lifecycle-boundary advisory: Beacon may discover applicable hooks, plan them, dry-run safe checks when there is no side effect, recommend the next confirmed command, and record hook evidence. Side-effect hook execution remains explicitly confirmed by the operator.

## 2. Accepted Change

Freeze a narrow extension to the existing project hook contract:

- Beacon may automatically discover project hooks at finite lifecycle boundaries.
- Beacon may automatically build hook plans and support read models.
- Beacon may automatically perform no-side-effect dry-run checks where the hook policy allows it.
- Beacon must surface a recommended command when a side-effect hook is applicable.
- Side-effect hooks still require explicit confirmation and must block without `--confirm`.
- Hook evidence remains support/runtime evidence only and cannot advance, pass, or rewrite implement, QA, release, gate, freeze, PRD, user-story, or test-case truth.

## 3. Scope

### In Scope

- Release-facing advisory for applicable `post_release` hooks after release readiness passes.
- Help/status visibility for lifecycle boundary hook recommendations and latest hook evidence.
- Hook plan and dry-run support that does not execute side effects.
- Explicit recommended command output for confirmed side-effect follow-up.
- Regression coverage for hidden auto-run prevention and support-evidence authority boundary.

### Out Of Scope

- Hidden side-effect hook execution.
- Making hooks a new lifecycle stage.
- Letting hook success become QA, release, gate, freeze, or requirement truth.
- Automatically advancing the Beacon lifecycle based on hook results.
- Arbitrary shell execution from hook Markdown.
- Project-specific global defaults for downstream projects.

## 4. Route Decision

This is a post-freeze semantic extension to `project-lifecycle-hook-skill-toolkit-contract`. It must pass through the governed change/refreeze chain before implementation.

Implementation may proceed only after PRD, user-story, test-case, requirement clarity, and freeze are closed for this feature.

## 5. Freeze Deliverables

- `docs/beacon/v1.4.10/change/lifecycle-boundary-hook-advisory-and-confirmed-execution.md`
- `docs/beacon/v1.4.10/prd/lifecycle-boundary-hook-advisory-and-confirmed-execution.md`
- `docs/beacon/v1.4.10/user-story/lifecycle-boundary-hook-advisory-and-confirmed-execution.md`
- `docs/beacon/v1.4.10/qa/test-cases/lifecycle-boundary-hook-advisory-and-confirmed-execution.md`

## 6. Boundary

This change freezes advisory and confirmed-execution semantics only. It does not install tools, deploy UAT, run Debug Lab, pass release, or execute side-effect hooks without explicit confirmation.
