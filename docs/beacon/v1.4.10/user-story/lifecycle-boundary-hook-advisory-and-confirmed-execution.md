# User Story: Lifecycle Boundary Hook Advisory And Confirmed Execution

**Feature**: `lifecycle-boundary-hook-advisory-and-confirmed-execution`
**Version**: `v1.4.10`
**Status**: `refreeze-input`
**Date**: `2026-05-25`

## Story

As a Beacon operator finishing a lifecycle stage, I want Beacon to automatically surface applicable project hook follow-up and the exact confirmed command to run, so that project-specific follow-up is visible and evidenced without hidden side-effect execution or confusion with lifecycle verdicts.

## Acceptance Criteria

| AC ID | Name | Acceptance Criteria |
| --- | --- | --- |
| AC-001 | Boundary discovery | Given a lifecycle boundary such as `post_release`, Beacon discovers enabled project hooks from `docs/beacon/hooks/<hook-id>.md` whose hook code matches the boundary. |
| AC-002 | Release follow-up advisory | Given `release check` passes and an applicable `post_release` hook exists, the release output includes a hook advisory with hook id, plan status, trigger policy, evidence paths, and a recommended confirmed-run command. |
| AC-003 | Safe automatic planning | Automatic hook advisory may plan hooks and may dry-run no-side-effect checks, but it does not execute side-effect follow-up. |
| AC-004 | Manual confirmation guard | Given a `manual_confirmed` hook is run without `--confirm`, the run is blocked with `manual_confirmation_required` and `side_effect_executed` remains false. |
| AC-005 | Confirmed execution path | Given the operator runs the recommended command with `--confirm`, the hook executes its restricted follow-up and writes hook evidence. |
| AC-006 | Evidence authority boundary | Hook advisory and hook evidence are marked as support/runtime evidence only and cannot advance or rewrite QA, release, gate, freeze, PRD, user-story, or test-case truth. |
| AC-007 | Help/status visibility | Help/status surfaces can show applicable hook advisory and latest hook evidence without presenting hooks as a new lifecycle stage. |
| AC-008 | Hidden auto-run fail closed | Hidden side-effect auto-run attempts fail closed with explicit reason codes. |

## Negative Cases

- A release-ready result must not automatically install Beacon local tools unless the operator confirms the hook.
- A hook pass must not change `release_ready`, QA verdict, gate verdict, or requirement freeze status.
- A hook command template must not become arbitrary shell execution.
- A disabled or mismatched hook must not appear as an executable follow-up.

## Boundary Notes

This story extends hook discoverability and advisory behavior only. It does not change Beacon's completion definition: completion remains governed by requirement truth, implementation evidence, QA proof, and release gate status.
