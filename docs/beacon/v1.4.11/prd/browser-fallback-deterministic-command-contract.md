# PRD: Browser Fallback Deterministic Command Contract

**Feature**: `browser-fallback-deterministic-command-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

This feature freezes Phase 8 of the v1.4.11 legacy burden reduction plan.

Beacon must preserve deterministic project command execution while renaming and reclassifying the old browser `fallback` path so evidence cannot imply browser-agent success when no browser agent actually ran.

## 1. Problem

Browser adapter fallback wording is ambiguous.

When a browser agent is unavailable, Beacon can run a deterministic project command. That behavior is useful, but the label `fallback` hides what happened. It can make a successful deterministic command look like successful browser-agent execution.

This weakens QA and release auditability because browser evidence and deterministic command evidence are different evidence classes.

## 2. Goals

- AC-001: Browser adapter current syntax exposes a deterministic project command option named `--deterministic-command` or `--explicit-project-command`.
- AC-002: Legacy `--fallback-cmd` remains callable as a compatibility alias.
- AC-003: Deterministic project command execution records `execution_mode=deterministic_command`.
- AC-004: Evidence explicitly records browser agent availability separately from deterministic command execution.
- AC-005: Evidence never claims browser-agent success when only deterministic project command execution happened.
- AC-006: Use of `--fallback-cmd` records compatibility evidence bound to `browser-fallback-command-name`.
- AC-007: Generated current QA/browser adapter command templates prefer current deterministic command naming instead of legacy fallback naming.
- AC-008: Missing browser agent and missing deterministic command fail closed with a clear reason code.
- AC-009: Tests prove this slice does not change prototype/design, QA legacy mirror, PRD legacy mirror, implement package, memory, intent, or test marker behavior.
- AC-010: Help/status/report or evidence readout provides a repair route that distinguishes browser-agent setup from deterministic command setup.

## 3. Design Principles

### 3.1 Truthful evidence labels

Evidence should say what actually executed.

### 3.2 Compatibility without promotion

`--fallback-cmd` can remain callable, but it must not be promoted as the current recommended syntax.

### 3.3 Browser evidence stays distinct

Deterministic command evidence can support command-level verification. It must not satisfy browser-agent evidence by name.

### 3.4 Scope stays narrow

This feature is not the memory/intent boundary, prototype adapter rebuild, QA mirror policy, or test marker relayering feature.

## 4. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Browser adapters must accept a current deterministic command option such as `--deterministic-command` or `--explicit-project-command`. |
| FR-002 | AC-002 | Browser adapters must continue accepting `--fallback-cmd` as a compatibility alias during this slice. |
| FR-003 | AC-003 | Adapter evidence must write deterministic project command execution as `execution_mode=deterministic_command`. |
| FR-004 | AC-004 | Adapter evidence must include distinct fields for browser agent availability and deterministic command execution. |
| FR-005 | AC-005 | Adapter evidence must not mark browser-agent execution as successful unless the browser agent actually executed. |
| FR-006 | AC-006 | Legacy alias usage must emit compatibility evidence with registry binding to `browser-fallback-command-name`. |
| FR-007 | AC-007 | QA command generation must prefer current deterministic command syntax for new/current templates. |
| FR-008 | AC-008 | If neither browser agent execution nor deterministic command execution is available, the adapter must fail closed with a stable reason code. |
| FR-009 | AC-009 | Regression tests must prove unrelated prototype/design, QA, PRD, implement, memory, intent, and test marker behavior is preserved. |
| FR-010 | AC-010 | Human and machine readouts must provide repair guidance for browser setup versus deterministic command setup. |

## 5. Required Compatibility Binding

This feature must bind to registry entry:

- `browser-fallback-command-name`

The registry entry remains compatibility governance. It does not become a lifecycle stage, truth source, or gate source.

## 6. Evidence Contract

Deterministic command evidence must expose at least:

- `execution_mode`: `deterministic_command`
- `browser_agent_requested`
- `browser_agent_available`
- `browser_agent_executed`
- `deterministic_command_configured`
- `deterministic_command_executed`
- `compat_alias_used`
- `compat_id`
- `reason_code`

The field names may be adapted to local conventions, but tests must prove the semantic distinction.

## 7. Success Metrics

- Current deterministic command syntax exists.
- Legacy fallback alias still works.
- Evidence no longer uses `fallback` as the current execution mode for deterministic commands.
- Browser-agent success is never inferred from deterministic command success.
- Compatibility alias usage is auditable.
- Current command templates no longer promote `--fallback-cmd`.
- Missing runner/command conditions fail closed with repair guidance.

## 8. Non Goals

- No browser admission redesign.
- No real browser evidence requirement change.
- No prototype/design behavior change.
- No memory or intent behavior change.
- No QA/PRD mirror policy change.
- No implement package behavior change.
- No test marker relayering.
- No command removal.
- No release verdict change by itself.
