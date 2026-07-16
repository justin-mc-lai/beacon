---
slug: beacon-loop-failure-mode-catalog-v165
version: v1.6.5
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Loop failure-mode catalog
canonical_refs:
  prd: docs/beacon/archive/v1.6.5/features/beacon-loop-failure-mode-catalog-v165/truth.md
  user_story: docs/beacon/archive/v1.6.5/features/beacon-loop-failure-mode-catalog-v165/truth.md
  test_case: docs/beacon/archive/v1.6.5/features/beacon-loop-failure-mode-catalog-v165/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Loop Failure-Mode Catalog v1.6.5

## Overview

Beacon has reason codes and QA repair routes, but known loop failures are not collected in one catalog that humans and tools can inspect. This feature adds a versioned catalog and validator.

## User Intent

Turn known loop failure modes into a governed catalog so audit and repair loops can explain symptoms, causes, mitigations, and routes.

## User Intent Snapshot

- user_prompt: "failure-mode catalog"
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/archive/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- depends_on: beacon-loop-pattern-registry-v165
- consumes: v1.6.4 defect repair taxonomy
- silent_scope_change_allowed: false

## User Decisions

| ID | Decision | Value |
|---|---|---|
| UD-001 | Catalog path | `docs/beacon/archive/v1.6.5/execution/loop-failure-modes.md` |
| UD-002 | Severity levels | S1 annoying, S2 harmful, S3 critical |
| UD-003 | Required fields | id, severity, symptom, cause, mitigation, route, evidence expectation |
| UD-004 | Audit consumption | loop-audit includes catalog readiness signal |

## Problem Statement

1. Reason codes are runtime classifications, not a curated system failure catalog.
2. Infinite repair loops, truth drift, stale evidence, and branch alignment failures lack a single explanatory surface.
3. Loop audit cannot check whether known failure modes are documented.

## Non-Goals

- Do not replace reason codes.
- Do not claim the catalog is exhaustive forever.
- Do not mark QA or release pass.

## Affected Surfaces

- `docs/beacon/archive/v1.6.5/execution/loop-failure-modes.md`
- new catalog validator utility
- `beacon doctor loop-audit` catalog signal
- `tests/test_v165_loop_failure_mode_catalog.py`

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | catalog-file | v1.6.5 includes `execution/loop-failure-modes.md` with S1/S2/S3 sections. |
| AC-002 | required-fields | Validator requires id, severity, symptom, cause, mitigation, route, and evidence expectation for each mode. |
| AC-003 | baseline-modes | Catalog includes truth drift, git alignment blocked, stale evidence manifest, infinite fix loop, and protected path attempt. |
| AC-004 | invalid-severity | Invalid severity fails validation with reason_code `loop_failure_mode_invalid_severity`. |
| AC-005 | audit-consumption | `doctor loop-audit` reports failure catalog status and findings. |

## Deferral Ledger

Deferral ledger contains only accepted decisions.

## Downstream Routes

- `beacon-gen-implement`: add catalog, parser/validator, audit integration.
- `beacon-eval-qa`: validate required fields, baseline modes, and audit signal.
