# PRD: Compatibility Registry and Command Catalog Contract

**Feature**: `compatibility-registry-and-command-catalog-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

This feature freezes the next low-risk v1.4.11 legacy burden reduction slice.

Beacon must introduce a governed compatibility registry and explicit command catalog layering before any hidden fallback, legacy mirror, deprecated command, or compatibility path is retired.

The feature is registration-first and validation-first. It must preserve current runtime behavior except for diagnostics, readout labels, and validation artifacts.

## 1. Problem

Beacon currently keeps compatibility behavior across commands, QA, PRD, prototype, browser runners, memory, intent routing, and implement packaging.

Those paths are useful for historical projects and old scripts, but they are scattered across source files. Without a registry, maintainers cannot reliably answer:

- why a compat path exists.
- which current surface replaces it.
- whether it is enabled by default.
- whether it requires explicit admission.
- what evidence proves it is still covered.
- when it can retire.

The command catalog has a similar issue: current, support, labs, compatibility, deprecated, and internal commands are mixed in code and tests. This makes the public mainline harder to reason about and makes it easy to accidentally recommend an old compatibility command as the next default route.

## 2. Goals

- AC-001: Beacon defines a compatibility registry schema with required fields for each compat, fallback, legacy, deprecated, or historical surface.
- AC-002: The registry covers all known surfaces from the v1.4.11 baseline inventory that are assigned to Phase 2 or later compatibility governance.
- AC-003: The registry records each entry's owner, surface category, reason, current replacement, default behavior, allowed version range, retirement route, and required evidence.
- AC-004: Command catalog entries are classified into explicit layers: current, support, advanced, labs, compat, deprecated, and internal.
- AC-005: Compatibility and deprecated commands remain callable according to existing runtime behavior during this slice.
- AC-006: Default help, status, or next-route output must not promote compat or deprecated commands as the normal current mainline route.
- AC-007: Unregistered compatibility, fallback, or deprecated command surfaces fail validation.
- AC-008: Tests prove this feature does not change QA legacy mirror, PRD legacy mirror, implement legacy loader, prototype legacy source, browser fallback, memory migration, or intent routing behavior.

## 3. Design Principles

### 3.1 Register before retire

Compatibility behavior must be visible and typed before Beacon changes defaults or removes paths.

### 3.2 Registry is governance, not a lifecycle stage

The compatibility registry is an internal governance artifact. It must not become a new human-facing mainline step.

### 3.3 Current mainline stays compact

The primary route remains:

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

Compatibility entries can be discoverable, but they must not expand the default route.

### 3.4 Behavior changes are deferred

This feature can add validation and diagnostics. It must not disable, remove, or alter existing compatibility behavior.

## 4. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon must provide a machine-readable compatibility registry or registry module. |
| FR-002 | AC-001 | Each registry entry must include `compat_id`, `surface`, `owner`, `reason`, `introduced_before`, `allowed_version_range`, `default_behavior`, `current_replacement`, `retirement_route`, and `evidence_required`. |
| FR-003 | AC-002 | Registry validation must compare known baseline inventory compat IDs against registry entries. |
| FR-004 | AC-003 | Registry entries must identify whether the entry is current-compatible, deprecated, explicit-admission-only, historical, or internal. |
| FR-005 | AC-004 | Command catalog validation must classify command names by layer. |
| FR-006 | AC-004 | Compat and deprecated command aliases must be represented in the registry or derived from it. |
| FR-007 | AC-005 | Existing compat and deprecated command behavior must remain available during this slice. |
| FR-008 | AC-006 | Help, status, and route readouts must preserve current mainline recommendations and avoid defaulting to compat/deprecated commands. |
| FR-009 | AC-007 | Validation must fail when a known compat, fallback, deprecated, or legacy surface lacks registry coverage. |
| FR-010 | AC-008 | Regression tests must prove no behavior-changing legacy retirement happens in this slice. |

## 5. Required Registry Coverage

The registry must cover at least:

- `command-catalog-compat-deprecated-aliases`
- `cli-factory-hidden-compat-registrations`
- `implement-legacy-cli-loader`
- `qa-auto-test-status-legacy-mirror`
- `prd-legacy-machine-mirror`
- `prototype-legacy-wireframe-source`
- `browser-fallback-command-name`
- `memory-legacy-projection`
- `intent-legacy-router`

Authority Phase 1 entries may remain in the baseline inventory, but this feature's registry obligation is focused on compatibility, fallback, deprecated, legacy, and historical behavior.

## 6. Command Layer Contract

Command catalog validation must recognize these layers:

| Layer | Meaning |
| --- | --- |
| `current` | Mainline lifecycle command or current public command. |
| `support` | Advisory, diagnostic, or recovery surface. |
| `advanced` | Explicit advanced capability plane. |
| `labs` | Experimental or ideation surface. |
| `compat` | Backward-compatible command or alias retained for older usage. |
| `deprecated` | Legacy command kept temporarily with replacement guidance. |
| `internal` | Internal command or hidden implementation surface. |

Compat and deprecated commands must have replacement guidance and evidence ownership.

## 7. Diagram Truth Layer

### 7.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 7.2 State Axes

- `compat_entry_status`
- `command_layer`
- `admission_requirement`

### 7.3 Propagation Contract

Registry entry status, command layer, and admission requirement must stay visible through implementation planning, QA coverage, status/help/report readouts, and later behavior-changing retirement features.

## 8. Success Metrics

- Registry exists and validates.
- All required compat IDs are covered.
- Command catalog layers are explicit and testable.
- Current mainline recommendations remain compact.
- Existing compatibility behavior remains available after this slice.
- Later v1.4.11 features can use registry data to safely change QA, PRD, implement, prototype, browser, memory, intent, or command behavior.

## 9. Non Goals

- No command removal.
- No hidden alias removal.
- No QA legacy mirror retirement.
- No PRD legacy mirror retirement.
- No implement legacy loader migration.
- No prototype legacy inspector split.
- No browser fallback rename.
- No memory or intent behavior change.
- No release verdict change.
