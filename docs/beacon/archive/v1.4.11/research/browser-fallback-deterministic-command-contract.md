# Research Closure: Browser Fallback Deterministic Command Contract

**Feature**: `browser-fallback-deterministic-command-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Purpose

This research closure promotes Phase 8 of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers browser fallback naming and evidence semantics only:

- keep deterministic project command execution available.
- stop describing deterministic command execution as browser-agent fallback success.
- introduce a current name such as `deterministic_command` or `explicit_project_command`.
- keep `--fallback-cmd` as a compatibility alias with explicit compatibility evidence.
- preserve browser runner admission, QA, release, prototype, design, memory, intent, and test marker behavior outside this slice.

The immediately previous prototype/design rebuild has already moved current prototype semantics to `design-result-adapter`. This Phase 8 slice must not reopen prototype. It only handles browser adapter wording and command/evidence semantics.

## 2. Current Problem

Beacon browser adapter surfaces currently use the term `fallback` for deterministic project commands.

That wording is overloaded:

- it can mean browser agent is unavailable.
- it can mean a deterministic project command was executed.
- it can be misread as the browser agent executed successfully.

This creates evidence ambiguity. A QA or release reader may see a successful fallback command and incorrectly treat it as browser-agent proof.

## 3. Target Architecture

The target model is:

```text
browser agent requested
  -> browser agent available
  -> browser agent execution evidence

browser agent requested
  -> browser agent unavailable
  -> deterministic project command admitted explicitly
  -> execution_mode=deterministic_command
  -> compatibility evidence only if legacy --fallback-cmd was used
```

Deterministic project commands are valid execution evidence for their own command contract. They are not browser-agent execution evidence.

## 4. State Machine

```text
browser_agent_requested
  -> browser_agent_executed
  -> browser_agent_evidence_recorded

browser_agent_requested
  -> browser_agent_unavailable
  -> deterministic_command_admitted
  -> deterministic_command_executed
  -> deterministic_command_evidence_recorded

legacy_fallback_cmd_used
  -> compat_alias_admitted
  -> deterministic_command_executed
  -> compatibility_evidence_recorded
```

Blocked transitions:

- `deterministic_command_executed -> browser_agent_evidence_recorded`: blocked because deterministic command output cannot claim browser-agent execution.
- `legacy_fallback_cmd_used -> current_contract_default`: blocked because `--fallback-cmd` is compatibility syntax.
- `browser_agent_unavailable -> release_browser_pass`: blocked unless valid browser evidence exists or browser evidence is not required.

## 5. Decision Priority

When decisions conflict, use this priority:

1. Preserve deterministic project command execution.
2. Make evidence vocabulary truthful.
3. Keep `--fallback-cmd` callable as a compatibility alias.
4. Prefer `deterministic_command` / `explicit_project_command` in current contracts.
5. Emit compatibility evidence when legacy syntax is used.
6. Do not change prototype/design, memory, intent, QA mirror, PRD mirror, implement package, or test marker layering in this slice.

## 6. Source Architecture Notes

Source-backed inputs:

- `beacon/adapters/browser_runner_common.py`: likely shared browser runner command/evidence normalization.
- `beacon/adapters/browser_use_runner.py`: browser-use adapter command surface.
- `beacon/adapters/agent_browser_runner.py`: agent-browser adapter command surface.
- `beacon/utils/qa9.py`: generated QA command templates that may still use `--fallback-cmd`.
- `beacon/compatibility/registry.py`: registry entry `browser-fallback-command-name`.
- `docs/beacon/archive/v1.4.11/execution/legacy-burden-baseline-inventory.md`: baseline inventory row for browser fallback naming.

## 7. Closure Decision

Freeze the browser fallback deterministic command requirement package.

This package must require current naming and evidence semantics for deterministic project commands, while preserving `--fallback-cmd` as an explicit compatibility alias.

Do not include memory migration, intent routing, prototype changes, design changes, QA/PRD mirror changes, implement package changes, command removal, or test marker relayering.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/archive/v1.4.11/prd/browser-fallback-deterministic-command-contract.md`

### 8.2 user_story_refs

- `docs/beacon/archive/v1.4.11/user-story/browser-fallback-deterministic-command-contract.md`

### 8.3 test_case_refs

- `docs/beacon/archive/v1.4.11/qa/test-cases/browser-fallback-deterministic-command-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-004 cover current deterministic command naming and evidence semantics.
- AC-005 through AC-006 cover browser-agent success claim prevention and compatibility alias evidence.
- AC-007 through AC-010 cover generated command defaults, fail-closed behavior, out-of-scope preservation, and repair-route readout.

### 8.5 out_of_scope_notes

- Prototype/design rebuild is already handled by `beacon-design-product-prototype-rebuild-contract`.
- Memory and intent boundaries are Phase 9.
- Test marker relayering is Phase 10.
- Release verdict changes are out of scope.

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-26T15:18:45.015728+00:00`
- deep_artifact_root: `docs/beacon/archive/v1.4.11/deep/browser-fallback-deterministic-command-contract`
- machine_artifact_root: `docs/beacon/archive/v1.4.11/.machine/deep/browser-fallback-deterministic-command-contract`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/archive/v1.4.11/.machine/deep/browser-fallback-deterministic-command-contract/release-supplement.json`
- adoption_status: `route_only`
