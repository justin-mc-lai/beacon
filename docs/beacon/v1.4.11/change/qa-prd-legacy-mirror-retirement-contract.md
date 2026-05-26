# Change: QA and PRD Legacy Mirror Retirement Contract

**Feature**: `qa-prd-legacy-mirror-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Change Reason

v1.4.11 has already established Markdown-first authority vocabulary and a compatibility registry for known legacy, fallback, deprecated, and compatibility surfaces.

The next low-risk behavior-policy slice is to handle the two legacy mirrors closest to truth and gate decisions:

- QA legacy mirror: `.beacon/auto-test-status.json`
- PRD legacy mirror: `.beacon/prd/<feature>.json`

These mirrors may remain useful for historical projects, but they must stop acting as current QA authority, current PRD truth, or release pass authority by default.

## 2. Accepted Change

Freeze a requirement package that requires Beacon to:

1. Make canonical QA status the default current QA authority.
2. Require explicit compatibility admission before legacy QA status can be read as historical evidence.
3. Prevent release from passing from legacy-only QA status.
4. Keep Markdown PRD as requirement truth.
5. Keep current PRD projection drift blocking where applicable.
6. Downgrade stale legacy PRD mirror mismatch to compatibility warning by default.
7. Bind both mirror policies to the compatibility registry.
8. Preserve historical compatibility files without deleting unrelated legacy surfaces.

## 3. Scope

### In Scope

- QA status loading default policy.
- Explicit `allow_legacy` or equivalent compatibility admission for legacy QA status.
- Compatibility evidence when legacy QA status is admitted.
- Release scorecard or release check behavior proving legacy-only QA status cannot pass.
- PRD material audit classification for Markdown truth, current projection, and legacy mirror.
- Legacy PRD mirror stale classification as `compat_mirror_stale` or equivalent warning.
- Registry binding for:
  - `qa-auto-test-status-legacy-mirror`
  - `prd-legacy-machine-mirror`
- Deterministic tests for QA mirror and PRD mirror policy.

### Out Of Scope

- No deletion of `.beacon/auto-test-status.json`.
- No deletion of `.beacon/prd/<feature>.json`.
- No implement package migration or `_implement_legacy_cli` removal.
- No prototype legacy source behavior change.
- No browser fallback rename.
- No memory migration behavior change.
- No intent router behavior change.
- No command removal.
- No new public lifecycle stage.

## 4. Source Evidence

- Research: `docs/beacon/v1.4.11/research/markdown-first-projection-authority-and-legacy-retirement-contract.md`
- Action plan: `docs/beacon/v1.4.11/research/legacy-burden-reduction-auditable-action-plan.md`
- Baseline inventory: `docs/beacon/v1.4.11/execution/legacy-burden-baseline-inventory.md`
- Compatibility registry research: `docs/beacon/v1.4.11/research/compatibility-registry-and-command-catalog-contract.md`
- Compatibility registry tests: `tests/test_v1411_compatibility_registry_and_command_catalog.py`

## 5. Route Decision

This change accepts Phase 4 and Phase 5 from the v1.4.11 legacy burden reduction plan.

It is intentionally mirror-policy-first:

```text
registry -> QA mirror policy -> PRD mirror policy -> later loader/prototype/browser/memory/intent retirement
```

Downstream implementation may start only after PRD, user-story, test-case, requirement clarity, and freeze complete.

## 6. Freeze Deliverables

- `docs/beacon/v1.4.11/research/qa-prd-legacy-mirror-retirement-contract.md`
- `docs/beacon/v1.4.11/change/qa-prd-legacy-mirror-retirement-contract.md`
- `docs/beacon/v1.4.11/prd/qa-prd-legacy-mirror-retirement-contract.md`
- `docs/beacon/v1.4.11/user-story/qa-prd-legacy-mirror-retirement-contract.md`
- `docs/beacon/v1.4.11/qa/test-cases/qa-prd-legacy-mirror-retirement-contract.md`

## 7. Boundary

This feature freezes requirement truth for QA and PRD legacy mirror authority policy only.

It does not execute implementation, QA, release, legacy file deletion, implement package migration, prototype migration, browser rename, memory migration, intent routing changes, or command removal.
