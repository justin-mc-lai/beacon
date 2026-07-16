---
slug: beacon-truth-map-center-and-package-cutover
version: v1.5.2
status: frozen
language: zh
canonical_refs:
  prd: docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/truth.md
  user_story: docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/truth.md
  test_case: docs/beacon/archive/v1.5.2/features/beacon-truth-map-center-and-package-cutover/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Feature Truth: Feature Package Authoritative Cutover

## Summary

v1.5.2 将 feature package Markdown 升级为 Beacon 正常生产/消费的唯一真相源。旧 triptych 只作为 doctor rebuild 和 change absorb 的目标存在。

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | package-authoritative | Feature package Markdown is the authoritative requirement/test/task/evidence truth package. |
| AC-002 | resolver-required | CLI and skill consumers must resolve feature truth through truth-map resolver. |
| AC-003 | legacy-not-canonical | PRD/user-story/test-case are rebuild/absorb artifacts only, not normal authority. |
| AC-004 | doctor-rebuild | Doctor can rebuild legacy surfaces from package truth. |
| AC-005 | change-absorb | Change can absorb legacy surfaces into package truth. |
| AC-006 | no-json-twin-requirement | Release and QA cannot require JSON twins for Markdown truth documents. |
| AC-007 | gate-consumption | Gate/QA/release consume package-derived truth through resolver/parser. |
| AC-008 | drift-fail-closed | If a legacy rebuild artifact conflicts with package truth, package truth wins and drift is reported. |

## Authority

Feature package Markdown is authority. Resolver code defines how consumers locate it. JSON projections are optional diagnostics only.

