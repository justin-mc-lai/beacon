---
slug: beacon-protected-path-denylist-v165
version: v1.6.5
status: frozen
revision_id: R1
language: zh
change_reason: R1 - Cross-version protected path denylist
canonical_refs:
  prd: docs/beacon/archive/v1.6.5/features/beacon-protected-path-denylist-v165/truth.md
  user_story: docs/beacon/archive/v1.6.5/features/beacon-protected-path-denylist-v165/truth.md
  test_case: docs/beacon/archive/v1.6.5/features/beacon-protected-path-denylist-v165/tests.md
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Requirement Truth: Protected Path Denylist v1.6.5

## Overview

Beacon has fail-closed gates, but no explicit cross-version list of paths that automatic write surfaces must not edit without human routing. The user accepted making this a `global-boundaries` principle.

## User Intent

Protect sensitive and high-risk paths from automatic Beacon writes by making a global denylist principle and enforcing it in write surfaces.

## User Intent Snapshot

- user_prompt: "protected path denylist 进入 global-boundaries 作为跨版本原则"
- lake_or_ocean: 湖
- scope_mode: full_parity
- program_ref: docs/beacon/archive/v1.6.5/programs/beacon-oss-borrow-hardening-v165/feature-graph.md
- cross_version_surface: docs/beacon/global-boundaries.md
- silent_scope_change_allowed: false

## User Decisions

| ID | Decision | Value |
|---|---|---|
| UD-001 | Landing surface | `docs/beacon/global-boundaries.md` |
| UD-002 | Enforcement | fail-closed for write surfaces; advisory for planner surfaces |
| UD-003 | Reason code | `protected_path_denylist` |

## Problem Statement

1. Agents may touch secrets, credentials, auth, payment, migration, or environment files during broad fixes.
2. Beacon skills mention safety generally but lack a machine-checkable protected path matcher.
3. Hooks and admission guards cannot currently distinguish protected path attempts from ordinary writes.

## Non-Goals

- Do not block human-authored changes.
- Do not replace repository-specific security review.
- Do not hard-code customer-specific private paths beyond stable risky path patterns.

## Protected Path Classes

| Class | Examples |
|---|---|
| environment | `.env`, `.env.*` |
| secrets | `secrets/**`, `credentials/**`, `*.pem`, `*.key`, `*_key*` |
| auth | `auth/**`, `oauth/**`, `sso/**` |
| payments | `payments/**`, `billing/**`, `stripe/**` |
| migrations | `migrations/**`, `schema_migrations/**` |

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | global-boundary | `global-boundaries.md` contains the protected path denylist principle and states planner advisory vs write-surface fail-closed behavior. |
| AC-002 | matcher | Runtime matcher detects exact path, glob, extension, and path-segment denylist patterns. |
| AC-003 | write-block | Write guard returns blocked payload with reason_code `protected_path_denylist` for protected paths. |
| AC-004 | planner-advisory | Planner surfaces can report protected path risk without blocking read-only analysis. |
| AC-005 | override-route | Payload includes an explicit human route recommendation instead of silently allowing automatic edits. |

## Deferral Ledger

Deferral ledger contains only accepted decisions.

## Downstream Routes

- `beacon-gen-implement`: add global-boundaries text, matcher, write guard integration, tests.
- `beacon-eval-qa`: verify protected path blocks and advisory behavior.
