# User Story: Version Aggregate Projection Guard Contract

**Feature**: `version-aggregate-projection-guard-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## Story

As a Beacon operator, I want QA accepted features to be reflected in the version aggregate projection automatically or through a clear repair-only route, so release check can verify the actual version scope without adding another lifecycle step.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | wording | Beacon uses `version aggregate projection` wording and does not call aggregate change payloads requirement truth. |
| AC-002 | feature projection | A QA accepted current feature has a deterministic feature change projection input or a repairable missing-projection finding. |
| AC-003 | release create | `release create` rebuilds version aggregate projection from feature change projections and preserves explicit feature dependency order. |
| AC-004 | fail closed | `release check` fails closed when the current QA accepted feature is missing from version aggregate projection. |
| AC-005 | inclusion pass | `release check` passes aggregate inclusion when the current QA accepted feature is included in version aggregate projection. |
| AC-006 | doctor repair | Doctor exposes repair-only projection rebuild / verify behavior for feature projection, version aggregate projection, and test-contract-index. |
| AC-007 | test index | test-contract-index refresh / verify is part of projection repair closure when stale index risk is reported. |
| AC-008 | no lifecycle stage | The guard does not add a new lifecycle stage, required human-facing command, release publish action, or post-release install action. |
| AC-009 | regression coverage | Tests cover missing projection, repaired projection, aggregate feature count/list, dependency order, and wording boundaries. |
| AC-010 | repair route | Blocked release output gives actionable repair guidance for projection inclusion failure. |

## Test Story Map

| Test ID | Covers | Scenario |
| --- | --- | --- |
| TEST-001 | AC-001 | Search release / docs output for projection wording and absence of machine-as-truth wording. |
| TEST-002 | AC-002 | Simulate or fixture a QA accepted feature missing `.machine/change/<feature>.json` and assert repairable finding. |
| TEST-003 | AC-003 | Build version change projection and assert feature list / count / explicit dependency waves. |
| TEST-004 | AC-004 | Run release scorecard/check fixture where current feature is absent from aggregate and assert blocked. |
| TEST-005 | AC-005 | Run release scorecard/check fixture where current feature is included and assert aggregate inclusion passes. |
| TEST-006 | AC-006 | Verify doctor repair-only route creates or validates projection artifacts without claiming truth authority. |
| TEST-007 | AC-007 | Verify stale test-contract-index risk is cleared by build + strict verify path. |
| TEST-008 | AC-008 | Assert no new lifecycle stage or new mandatory human-facing command is introduced. |
| TEST-009 | AC-009 | Regression suite covers projection guard behavior. |
| TEST-010 | AC-010 | Blocked release payload includes recommended repair route. |
