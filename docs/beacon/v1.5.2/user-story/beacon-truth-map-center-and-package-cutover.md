# User Story: Feature Package Authoritative Cutover

- version: `v1.5.2`
- feature: `beacon-truth-map-center-and-package-cutover`
- status: `frozen`

## Story

As a Beacon operator, I want Beacon to use feature-package Markdown as the only normal truth source, so future truth-source changes happen through the truth-map resolver instead of scattered legacy document chains.

## Acceptance Criteria

| AC ID | Theme | Description |
|---|---|---|
| AC-001 | package-authoritative | `features/<slug>/*.md` is authoritative for normal production and consumption. |
| AC-002 | resolver-required | Commands and skills must call truth-map resolver before reading truth. |
| AC-003 | legacy-not-canonical | Legacy triptych is not a canonical source in v1.5.2. |
| AC-004 | doctor-rebuild | `doctor` can rebuild legacy triptych from package truth. |
| AC-005 | change-absorb | `change` can absorb legacy triptych into package truth. |
| AC-006 | no-json-twin-requirement | Missing JSON twins do not block Markdown truth validity. |
| AC-007 | gate-consumption | QA/release/gate use resolver and parser outputs from package truth. |
| AC-008 | drift-fail-closed | Drift against package truth is reported; package truth remains authority. |

