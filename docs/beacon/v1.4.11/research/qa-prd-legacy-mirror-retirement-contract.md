# Research Closure: QA and PRD Legacy Mirror Retirement Contract

**Feature**: `qa-prd-legacy-mirror-retirement-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-26`

## 1. Purpose

This research closure promotes Phase 4 and Phase 5 of the v1.4.11 legacy burden reduction plan into requirement truth.

The slice covers:

- Phase 4: QA legacy mirror policy.
- Phase 5: PRD legacy mirror policy.

The goal is to keep historical compatibility evidence readable while preventing legacy mirrors from acting as current requirement truth, current QA authority, or release pass authority.

This feature depends on the prior compatibility registry slice. The QA and PRD legacy mirror surfaces must remain registered compatibility surfaces while this feature changes their default authority and gate behavior.

## 2. Architecture

The architecture is:

```text
Markdown requirement truth
  -> current machine projection / canonical runtime state
  -> compatibility mirror, only by explicit admission
  -> release gate rejects legacy-only pass authority
```

For QA:

```text
canonical QA status
  -> current QA read model
  -> release scorecard
```

Legacy `auto-test-status` may remain as historical evidence, but it must not be enough to pass current QA or release without explicit compatibility admission.

For PRD:

```text
Markdown PRD truth
  -> .machine PRD projection
  -> material audit
```

Legacy `.beacon/prd/<feature>.json` may remain as a compatibility mirror, but stale legacy mirror content must not be classified as current truth drift by default.

## 3. Business Flow

The maintainer flow is:

```text
registry identifies QA and PRD legacy mirrors
  -> freeze mirror authority policy
  -> implement current-only defaults
  -> preserve explicit compatibility admission
  -> QA proves legacy-only status cannot pass release
```

This feature answers:

- which QA status source has current authority.
- when legacy QA status may be read.
- how legacy QA admission is evidenced.
- which PRD material remains truth.
- how stale PRD legacy mirrors are reported.
- why release cannot pass from legacy-only evidence.

This feature does not delete legacy files or remove historical evidence.

## 4. State Machine

```text
legacy_mirror_registered
  -> current_only_default_required
  -> explicit_compat_admission_available
  -> legacy_only_pass_authority_blocked
  -> mirror_policy_release_ready
```

Allowed transitions:

- `legacy_mirror_registered -> current_only_default_required`: accepted by the v1.4.11 Phase 4 and Phase 5 scope decision.
- `current_only_default_required -> explicit_compat_admission_available`: implementation may preserve historical project support through explicit admission.
- `explicit_compat_admission_available -> legacy_only_pass_authority_blocked`: QA and release checks prove legacy-only status cannot pass.
- `legacy_only_pass_authority_blocked -> mirror_policy_release_ready`: all current authority and compatibility evidence paths are auditable.

Blocked transitions:

- `legacy_mirror_registered -> legacy_file_deletion`: blocked because this slice is policy-first, not deletion-first.
- `legacy_mirror_registered -> implement_loader_migration`: blocked because implement package migration is a later feature.
- `legacy_mirror_registered -> prototype_or_browser_policy_change`: blocked because prototype, browser, memory, and intent are later features.
- `legacy_only_pass_authority_blocked -> release_ready`: blocked unless implementation, QA, and release evidence close normally.

## 5. Decision Priority

When decisions conflict, use this priority:

1. Markdown PRD, user-story, and test-case remain requirement truth.
2. Canonical QA status and current `.machine` projection remain current authority surfaces.
3. Legacy mirrors may remain compatibility evidence only.
4. Legacy-only evidence must fail closed for current QA and release.
5. Explicit compatibility admission must leave machine-readable evidence.
6. No legacy file deletion or unrelated behavior retirement belongs in this slice.

## 6. Source Architecture Notes

Source-backed inputs:

- `beacon/utils/qa_runtime.py`: canonical QA status read/write and legacy auto-test status mirror.
- `.beacon/auto-test-status.json`: legacy QA mirror runtime artifact.
- `.beacon/qa/status.json`: canonical QA status runtime artifact.
- `beacon/commands/release.py`: release scorecard and legacy-only release pass prevention.
- `beacon/utils/material_audit.py`: PRD material audit and legacy mirror drift classification.
- `.beacon/prd/<feature>.json`: legacy PRD compatibility mirror.
- `docs/beacon/<version>/prd/<feature>.md`: Markdown PRD truth.
- `docs/beacon/<version>/.machine/prd/`: current projection surface when present.
- `beacon/compatibility/registry.py`: registered `qa-auto-test-status-legacy-mirror` and `prd-legacy-machine-mirror` entries.

## 7. Closure Decision

Freeze the QA and PRD legacy mirror retirement policy requirement package.

This package must require current-only defaults, explicit compatibility admission for historical mirrors, and release failure for legacy-only pass authority.

Do not include implement legacy loader migration, prototype legacy inspector split, browser fallback rename, memory migration changes, intent router behavior changes, command removal, or deletion of existing legacy artifacts.

## 8. Projection Truth Binding

### 8.1 prd_refs

- `docs/beacon/v1.4.11/prd/qa-prd-legacy-mirror-retirement-contract.md`

### 8.2 user_story_refs

- `docs/beacon/v1.4.11/user-story/qa-prd-legacy-mirror-retirement-contract.md`

### 8.3 test_case_refs

- `docs/beacon/v1.4.11/qa/test-cases/qa-prd-legacy-mirror-retirement-contract.md`

### 8.4 coverage_notes

- AC-001 through AC-003 cover QA canonical status authority, explicit legacy admission, and legacy-only release blocking.
- AC-004 through AC-006 cover PRD Markdown truth, projection blocking, and legacy mirror warning downgrade.
- AC-007 covers compatibility registry binding for both mirror surfaces.
- AC-008 covers no unrelated retirement.

### 8.5 out_of_scope_notes

- Legacy QA and PRD files are not deleted.
- Implement package migration is out of scope.
- Prototype, browser, memory, and intent behavior changes are out of scope.
- Command removal is out of scope.
- This feature does not create a new lifecycle stage.
