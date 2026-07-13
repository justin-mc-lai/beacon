---
slug: beacon-loop-readiness-audit-v165
version: v1.6.5
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Loop readiness audit score
canonical_refs:
  prd: docs/beacon/v1.6.5/features/beacon-loop-readiness-audit-v165/truth.md
  user_story: docs/beacon/v1.6.5/features/beacon-loop-readiness-audit-v165/truth.md
  test_case: docs/beacon/v1.6.5/features/beacon-loop-readiness-audit-v165/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Loop Readiness Audit v1.6.5

## Overview

Beacon has many gate and diagnostic surfaces, but no single loop-readiness signal. Operators need one report that says whether a project can safely run assisted or unattended loops, which signals are missing, and what to repair first.

## User Intent

Expose loop readiness as one deterministic score and level so users and CI can see whether Beacon loops are safe to run.

## User Intent Snapshot

- user_prompt: "loop readiness audit"
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- silent_scope_change_allowed: false

## User Decisions

| ID | Decision | Value |
|---|---|---|
| UD-001 | Score range | 0-100 |
| UD-002 | Levels | L0 draft, L1 report-only, L2 assisted, L3 unattended |
| UD-003 | Strict behavior | below threshold exits code 2 and emits repair suggestions |
| UD-004 | Default behavior | report-only unless strict mode is passed |

## Problem Statement

1. Gate results are fragmented across doctor, QA, release, workspace, and feature package surfaces.
2. Users cannot quickly tell which missing signal makes loop execution unsafe.
3. CI cannot block on a single readiness threshold.

## Non-Goals

- Do not replace existing gates.
- Do not make readiness score a release verdict.
- Do not require Phase 3 registry before Phase 2 can produce a score.

## Affected Surfaces

- `beacon/commands/doctor.py`
- new readiness utility under `beacon/utils/`
- `tests/test_v165_loop_readiness_audit.py`

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | cli-surface | `beacon doctor loop-audit --project-root . --version <v> --json` returns schema version, score, level, signals, findings, and repair suggestions. |
| AC-002 | score-levels | Scores map to L0/L1/L2/L3 with deterministic thresholds: L0 `<40`, L1 `40-59`, L2 `60-79`, L3 `>=80`. |
| AC-003 | signal-inventory | Audit reports at least these signals: version governance, global boundaries, feature packages, workspace admission, QA status, release status, pattern registry, token budget, run log, failure catalog. |
| AC-004 | strict-exit | Strict mode exits with code 2 when score is below the configured threshold and includes `loop_readiness_below_threshold`. |
| AC-005 | suggest | `--suggest` or JSON default includes ordered repair commands or routes for failed signals. |
| AC-006 | no-gate-authority | Payload labels readiness as advisory/report-only unless strict mode explicitly blocks. |

## State Model

```text
signals collected -> score calculated -> level assigned
level below threshold + strict -> blocked
level below threshold + non-strict -> report_only
level meets threshold -> pass
```

## Deferral Ledger

Deferral ledger contains only accepted decisions.

## Downstream Routes

- `beacon-gen-implement`: add CLI and scoring utility.
- `beacon-eval-qa`: validate score calculation, strict exit, and suggestions.
- `beacon-eval-release`: verify readiness audit does not masquerade as release pass.
