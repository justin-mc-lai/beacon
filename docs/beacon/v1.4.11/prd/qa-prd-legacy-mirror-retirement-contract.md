# PRD: QA and PRD Legacy Mirror Retirement Contract

**Feature**: `qa-prd-legacy-mirror-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## Overview

This feature freezes the next v1.4.11 legacy burden reduction slice after compatibility registry and command catalog validation.

Beacon must stop treating QA and PRD legacy mirrors as current authority by default while preserving their value as explicitly admitted compatibility evidence.

The feature is policy-first. It changes authority and gate semantics for two registered legacy mirror surfaces, but it must not delete historical artifacts or retire unrelated compatibility behavior.

## 1. Problem

Beacon still carries legacy mirrors close to critical decision points:

- `.beacon/auto-test-status.json` can mirror QA status for old flows.
- `.beacon/prd/<feature>.json` can mirror PRD machine state for old flows.

These artifacts are useful for old projects and scripts, but they are dangerous when current Beacon treats them as equivalent to canonical QA status or Markdown PRD truth.

The failure mode is false closure:

- legacy-only QA status appears green enough for release.
- stale legacy PRD mirror appears as current truth drift.
- operators cannot tell current projection gaps from compatibility mirror drift.

## 2. Goals

- AC-001: Canonical QA status is the default current QA authority for v1.4.11+ flows.
- AC-002: Legacy QA status can be read only through explicit compatibility admission and must be labeled as historical evidence.
- AC-003: Release checks and scorecards cannot pass from legacy-only QA status.
- AC-004: Markdown PRD remains requirement truth and legacy PRD mirror cannot override it.
- AC-005: Current PRD projection drift remains blocking when the current projection is stale or inconsistent.
- AC-006: Legacy PRD mirror mismatch is downgraded to compatibility warning by default.
- AC-007: QA and PRD legacy mirror policies are bound to compatibility registry entries.
- AC-008: This slice does not delete legacy files or change implement, prototype, browser, memory, intent, or command behavior.

## 3. Design Principles

### 3.1 Current authority first

Current flow must read canonical status and current projections first. Compatibility mirrors are not authority by default.

### 3.2 Compatibility remains explicit

Historical projects can still use legacy mirrors, but only through explicit admission that writes evidence.

### 3.3 Fail closed on legacy-only pass

If the only proof of QA success is legacy status, current release must block.

### 3.4 Warn, do not block, for stale compatibility mirrors

Stale legacy PRD mirror data should be reported as compatibility drift, not as current Markdown truth drift.

## 4. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | QA status read helpers must default to canonical/current QA status. |
| FR-002 | AC-001 | Current QA flows must not silently fall back to legacy auto-test status. |
| FR-003 | AC-002 | Legacy QA status reads must require an explicit admission flag or equivalent compatibility mode. |
| FR-004 | AC-002 | Explicit legacy QA admission must write machine-readable compatibility evidence. |
| FR-005 | AC-003 | Release scorecard and release check must block legacy-only QA pass authority. |
| FR-006 | AC-004 | Material audit must classify Markdown PRD as requirement truth. |
| FR-007 | AC-005 | Current projection mismatch or stale current projection must remain blocking. |
| FR-008 | AC-006 | Legacy `.beacon/prd/<feature>.json` mismatch must become a compatibility warning by default. |
| FR-009 | AC-007 | QA and PRD mirror policy code paths must reference registered compat IDs or registry validation. |
| FR-010 | AC-008 | Regression tests must prove no deletion or unrelated retirement happens in this slice. |

## 5. Required Policy Coverage

The feature must cover at least:

- `qa-auto-test-status-legacy-mirror`
- `prd-legacy-machine-mirror`

These IDs must remain in the compatibility registry and must have retirement route `qa-prd-legacy-mirror-retirement-contract` or an equivalent current policy route.

## 6. Runtime Behavior Contract

### 6.1 QA status

Default behavior:

```text
load canonical QA status
  -> if missing, current QA is incomplete/blocked
  -> do not silently treat legacy status as pass
```

Explicit compatibility behavior:

```text
allow_legacy/admission enabled
  -> read legacy status as historical evidence
  -> mark source as compatibility mirror
  -> write admission evidence
  -> do not convert evidence into release pass by itself
```

### 6.2 PRD material audit

Default behavior:

```text
Markdown PRD truth
  -> current projection audit
  -> legacy mirror audit as compatibility warning only
```

Blocking behavior:

```text
current projection stale/inconsistent -> block
legacy mirror stale/inconsistent -> warn, unless explicit historical mode requires blocking
```

## 7. Success Metrics

- Legacy-only QA status cannot pass current QA or release.
- Explicit legacy QA admission is visible as compatibility evidence.
- Markdown PRD remains the only PRD requirement truth.
- Current PRD projection drift still blocks.
- Legacy PRD mirror drift is reported separately as compatibility warning.
- Compatibility registry remains the source of mirror retirement ownership.
- No unrelated legacy behavior is deleted or changed.

## 8. Diagram Truth Layer

### 8.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 8.2 State Axes

- `qa_status_source`: `canonical`, `legacy_admitted`, `legacy_only_blocked`
- `prd_material_role`: `markdown_truth`, `current_projection`, `compat_mirror`
- `legacy_admission_state`: `not_allowed`, `explicitly_admitted`, `historical_evidence_only`
- `release_authority_state`: `current_evidence_ready`, `legacy_only_blocked`, `compat_warning_present`

### 8.3 Branch Flow

```text
current QA / PRD decision
  -> canonical QA status and Markdown PRD truth present
    -> current flow may continue
  -> canonical QA status missing but legacy QA status present
    -> block current QA / release unless explicit compatibility admission is requested
  -> Markdown PRD present but legacy PRD mirror differs
    -> classify as compatibility warning by default
  -> current projection differs from Markdown truth
    -> block as current projection drift
```

### 8.4 State Machine

```text
mirror_registered
  -> current_only_default
  -> explicit_compat_admission_optional
  -> historical_evidence_recorded
  -> release_authority_checked
```

Terminal states:

- `current_evidence_ready`: canonical/current evidence supports downstream QA or release.
- `legacy_only_blocked`: only legacy mirror evidence exists, so current QA or release must fail closed.
- `compat_warning_present`: legacy mirror drift exists but does not override current truth.

### 8.5 Decision Priority

```text
Markdown PRD truth
  > current machine projection
  > canonical QA runtime status
  > explicitly admitted compatibility evidence
  > legacy mirror files without admission
```

Legacy mirror files without admission cannot outrank current truth, current projection, canonical QA status, QA gate, or release gate.

## 9. Non Goals

- No deletion of `.beacon/auto-test-status.json`.
- No deletion of `.beacon/prd/<feature>.json`.
- No implement package migration.
- No prototype legacy inspector split.
- No browser fallback rename.
- No memory migration policy change.
- No intent router policy change.
- No command removal.
- No new lifecycle stage.
