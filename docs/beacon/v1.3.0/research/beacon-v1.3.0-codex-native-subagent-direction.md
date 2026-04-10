# Beacon v1.3.0 Research: Simplified Codex Native Subagent Direction

**Date**: 2026-04-10  
**Reference**: `https://github.com/atticus98/codex-turbo`

## Research question

What should Beacon borrow from `codex-turbo` if the goal is not "become another agent runtime", but "add a small, reliable Codex native subagent lane inside Beacon stages"?

## Observed signals from `codex-turbo`

From the project README and repo surface, three ideas stand out:

1. Native subagents are treated as a repo-local capability toggle, not a platform rewrite.
2. Role-specific instruction files matter as much as the launcher itself.
3. Delegation is selective and task-bounded, not a default answer for every prompt.

## What Beacon should borrow

### 1. Config-gated delegation

Beacon should not auto-spawn agents because a stage exists.

Instead, each stage should declare:

- whether `subagent_mode` is allowed
- which worker roles are valid
- what artifact the worker must return

### 2. Role contracts over free-form prompts

Beacon already has stage semantics.

So the right abstraction is not "spawn arbitrary agent", but:

- `think.researcher`
- `user-story.mapper`
- `prd.critic`
- `test-case.scenario-mapper`
- `qa.verifier`
- `implement.executor`

### 3. Repo truth stays in Beacon artifacts

Codex-native child agents may help produce results, but Beacon must still own:

- version truth
- docs/beacon materials
- gate contracts
- release evidence

The child agent output is input evidence, not a second source of truth.

## What Beacon should not borrow

1. Broad runtime mutation of the user's Codex environment
2. Open-ended "delegate everything" behavior
3. A separate agent memory plane that bypasses Beacon writeback
4. Any design that forces `think / story / prd / qa` to depend on tmux or external shells

## Recommended direction

Use a two-layer design:

1. `subagent plan`
   - Beacon decides whether a stage may delegate.
   - Beacon writes a stage-local plan with worker role, scope, inputs, and expected outputs.
2. `subagent evidence`
   - worker result is written under `.beacon/subagents/<feature>/<run>/`
   - stage command compiles the result back into canonical Beacon artifacts

## Why this is the right cut

This keeps the mainline intact:

`ask/think -> user-story -> prd -> test-case -> qa -> implement -> gate`

but allows hard parts to be split into bounded worker lanes where it actually helps.
