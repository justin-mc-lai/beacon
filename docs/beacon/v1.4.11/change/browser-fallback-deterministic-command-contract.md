# Change: Browser Fallback Deterministic Command Contract

**Feature**: `browser-fallback-deterministic-command-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

v1.4.11 has already registered browser fallback command naming as a compatibility surface.

The next reduction slice is to rename the current browser adapter fallback semantics so deterministic project commands are not mistaken for successful browser-agent execution.

The previous design/prototype rebuild already converted current prototype behavior into `design-result-adapter`. This change must not reopen prototype. It only addresses browser adapter command naming and evidence vocabulary.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Introduce current terminology for deterministic project command execution: `deterministic_command` or `explicit_project_command`.
2. Keep `--fallback-cmd` as a compatibility alias.
3. Ensure evidence records deterministic command execution as `execution_mode=deterministic_command`.
4. Ensure evidence distinguishes browser agent unavailable from deterministic command executed.
5. Prevent deterministic command success from claiming browser-agent success.
6. Emit compatibility evidence when legacy `--fallback-cmd` syntax is used.
7. Bind the change to compatibility registry entry `browser-fallback-command-name`.
8. Preserve prototype/design, QA, PRD, implement package, memory, intent, test marker, and command removal behavior outside this slice.

## 3. Scope

### In Scope

- Browser adapter command-line naming.
- Evidence vocabulary for deterministic project commands.
- Compatibility handling for `--fallback-cmd`.
- QA command template updates that currently emit browser adapter fallback syntax.
- Tests for adapter evidence snapshots and compat alias behavior.

### Out Of Scope

- No browser runner admission redesign.
- No real browser evidence policy change.
- No prototype or design behavior change.
- No memory migration behavior change.
- No intent router behavior change.
- No QA legacy mirror or PRD legacy mirror change.
- No implement package change.
- No test marker relayering.
- No command removal.

## 4. Source Evidence

- Research: `docs/beacon/v1.4.11/research/browser-fallback-deterministic-command-contract.md`
- Action plan: `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Baseline inventory: `docs/beacon/v1.4.11/execution/legacy-burden-baseline-inventory.md`
- Compatibility registry: `beacon/compatibility/registry.py`
- Browser adapters: `beacon/adapters/browser_runner_common.py`, `beacon/adapters/browser_use_runner.py`, `beacon/adapters/agent_browser_runner.py`
- QA9 command templates: `beacon/utils/qa9.py`

## 5. Route Decision

This change accepts Phase 8 from the v1.4.11 legacy burden reduction plan.

It is intentionally browser-adapter-only:

```text
registry -> prototype/design rebuild -> browser fallback rename -> later memory/intent boundary -> later test marker relayering
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/v1.4.11/research/browser-fallback-deterministic-command-contract.md`
- `docs/beacon/v1.4.11/change/browser-fallback-deterministic-command-contract.md`
- `docs/beacon/v1.4.11/prd/browser-fallback-deterministic-command-contract.md`
- `docs/beacon/v1.4.11/user-story/browser-fallback-deterministic-command-contract.md`
- `docs/beacon/v1.4.11/qa/test-cases/browser-fallback-deterministic-command-contract.md`

## 7. Boundary

This feature freezes requirement truth for browser fallback deterministic command naming only.

It does not execute implementation, QA, release, prototype migration, design changes, memory migration, intent routing changes, test marker relayering, or command removal.
