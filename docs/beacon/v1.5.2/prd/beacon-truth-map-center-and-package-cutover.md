# PRD: Beacon Feature Package Authoritative Cutover

- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`

## Goal

Complete the cutover so feature-package Markdown becomes Beacon's normal canonical truth source.

## Canonical Chain

```text
truth-map resolver
  -> features/<slug>/truth.md
  -> features/<slug>/tests.md
  -> features/<slug>/tasks.md
  -> features/<slug>/evidence.md
  -> gate / QA / release consumers
```

## Deprecated Normal Chain

```text
prd -> user-story -> qa/test-cases
```

The deprecated chain is not removed from disk by force, but it is no longer a normal truth source.

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

