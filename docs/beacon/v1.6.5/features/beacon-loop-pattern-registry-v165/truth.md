---
slug: beacon-loop-pattern-registry-v165
version: v1.6.5
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Machine-readable loop pattern registry
canonical_refs:
  prd: docs/beacon/v1.6.5/features/beacon-loop-pattern-registry-v165/truth.md
  user_story: docs/beacon/v1.6.5/features/beacon-loop-pattern-registry-v165/truth.md
  test_case: docs/beacon/v1.6.5/features/beacon-loop-pattern-registry-v165/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Loop Pattern Registry v1.6.5

## Overview

Beacon loop patterns such as ralph, team, and automation are spread across skill prose and command behavior. Tools cannot validate or consume the pattern set because there is no machine-readable registry.

This feature adds a versioned registry and validator. The registry is a human-readable governed artifact, while machine consumers treat it as a read model for loop audit and budgeting.

## User Intent

Make Beacon loop patterns reusable and auditable by recording them in a machine-readable registry instead of prose-only skill text.

## User Intent Snapshot

- user_prompt: "loop pattern registry"
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- silent_scope_change_allowed: false

## User Decisions

| ID | Decision | Value |
|---|---|---|
| UD-001 | Registry path | `docs/beacon/v1.6.5/loop-patterns/registry.yaml` |
| UD-002 | Required fields | id, cadence, risk, harness_skills, state_surface, phases, human_gates, token_cost, daily_cap, safety |
| UD-003 | Consumer | `doctor loop-audit` reads registry when present |

## Problem Statement

1. Pattern definitions cannot be validated for duplicate ids or missing safety fields.
2. Loop audit cannot distinguish "registry absent" from "registry invalid".
3. Token budget and failure catalog phases need a stable pattern id surface.

## Non-Goals

- Do not make internal implementation lanes public lifecycle stages.
- Do not replace skill guidance.
- Do not require all future loop patterns to be implemented in v1.6.5.

## Affected Surfaces

- `docs/beacon/v1.6.5/loop-patterns/registry.yaml`
- new registry validator utility under `beacon/utils/`
- `beacon doctor loop-audit` registry signal
- `tests/test_v165_loop_pattern_registry.py`

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | registry-file | v1.6.5 includes `docs/beacon/v1.6.5/loop-patterns/registry.yaml` with at least ralph, team, and beacon-loop patterns. |
| AC-002 | schema-required | Validator requires id, cadence, risk, harness_skills, state_surface, phases, human_gates, token_cost, daily_cap, and safety fields. |
| AC-003 | duplicate-block | Duplicate pattern ids fail validation with reason_code `loop_pattern_duplicate_id`. |
| AC-004 | risk-values | Validator accepts only governed risk values `low`, `medium`, `high`, `critical`. |
| AC-005 | audit-consumption | `doctor loop-audit` reports registry status as pass/fail/missing and includes registry findings. |

## Deferral Ledger

Deferral ledger contains only accepted decisions.

## Downstream Routes

- `beacon-gen-implement`: add registry, parser, validator, audit integration.
- `beacon-eval-qa`: validate schema, duplicate ids, and audit consumption.
