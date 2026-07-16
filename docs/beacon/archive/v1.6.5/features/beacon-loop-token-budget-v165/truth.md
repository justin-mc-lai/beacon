---
slug: beacon-loop-token-budget-v165
version: v1.6.5
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Loop token budget ledger and kill switch
canonical_refs:
  prd: docs/beacon/archive/v1.6.5/features/beacon-loop-token-budget-v165/truth.md
  user_story: docs/beacon/archive/v1.6.5/features/beacon-loop-token-budget-v165/truth.md
  test_case: docs/beacon/archive/v1.6.5/features/beacon-loop-token-budget-v165/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Loop Token Budget v1.6.5

## Overview

Beacon loops can run multiple rounds and consume significant tokens/time without a visible budget. Pattern registry provides per-pattern cost fields; this feature adds budget accounting, status reporting, and a kill switch.

## User Intent

Make loop cost visible and stop automated loop execution when budget or kill switch boundaries say to pause.

## User Intent Snapshot

- user_prompt: "loop token budget"
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/archive/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- depends_on: beacon-loop-pattern-registry-v165
- silent_scope_change_allowed: false

## User Decisions

| ID | Decision | Value |
|---|---|---|
| UD-001 | Ledger path | `.beacon/loop/budget-ledger.json` |
| UD-002 | Status command | `beacon status loop-budget` |
| UD-003 | Kill switch | `.beacon/loop/pause-all` blocks automated loop execution |
| UD-004 | Budget semantics | soft gate for humans, fail-closed for unattended automation |

## Problem Statement

1. Loop cost is not visible in a governed runtime ledger.
2. Pattern cost fields cannot be consumed without a budget utility.
3. There is no kill switch to pause all automated loop execution.

## Non-Goals

- Do not bill real money or call provider APIs.
- Do not infer exact token usage when unavailable; estimates are acceptable if marked.
- Do not block manual planner analysis.

## Affected Surfaces

- `docs/beacon/archive/v1.6.5/loop-patterns/registry.yaml`
- `.beacon/loop/budget-ledger.json`
- `beacon status loop-budget`
- loop execution preflight helper
- `tests/test_v165_loop_token_budget.py`

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | registry-fields | Pattern registry entries expose `token_cost` and `daily_cap` fields consumed by budget utilities. |
| AC-002 | ledger-record | Budget utility appends run records with pattern id, run id, estimated tokens, actual tokens when known, date, and source. |
| AC-003 | daily-total | Budget utility calculates daily totals per pattern and overall project. |
| AC-004 | status-command | `beacon status loop-budget --json` reports totals, caps, remaining budget, and blocked/ok state. |
| AC-005 | cap-block | Unattended loop preflight blocks when daily cap is exceeded with reason_code `loop_budget_exceeded`. |
| AC-006 | kill-switch | Presence of `.beacon/loop/pause-all` blocks automated loops with reason_code `loop_kill_switch_active`. |

## State Model

```text
budget ok -> run allowed -> ledger appended
budget exceeded -> blocked:loop_budget_exceeded
pause-all present -> blocked:loop_kill_switch_active
manual/status query -> report_only
```

## Deferral Ledger

Deferral ledger contains only accepted decisions.

## Downstream Routes

- `beacon-gen-implement`: add ledger, status command, budget preflight, tests.
- `beacon-eval-qa`: verify cap and kill switch behavior.
