# Tests: code2truth-project-intake

## Coverage Matrix

| AC ID | TC ID | Layer | Assertion |
|-------|-------|-------|-----------|
| AC-001 | TC-001 | integration | Intake builds a source inventory from code, docs, skills, tests, CLI behavior, Beacon source maps, and available provider artifacts. |
| AC-002 | TC-002 | contract | Provider artifacts from `qi-dev-understand-anything` / Understand-Anything are recorded as evidence refs and cannot be marked as requirement authority. |
| AC-003 | TC-003 | contract | Candidate truth output includes source refs, confidence, and ambiguity markers for material claims. |
| AC-004 | TC-004 | integration | Candidate truth is not promoted to package truth until user confirmation and governed truth/change routing occur. |
| AC-005 | TC-005 | integration | `beacon truth-map resolve` selects `features/<slug>/{truth,tests,tasks,evidence}.md` as authority and generated JSON/provider graphs cannot override it. |
| AC-006 | TC-006 | integration | Implement admission can close with no source diff when frozen ACs are satisfied by existing behavior and evidence. |
| AC-007 | TC-007 | contract | `tasks.md` records existing-code satisfaction and evidence refs without pretending task checkboxes are implementation, QA, or release gates. |
| AC-008 | TC-008 | integration | QA validates package coverage, evidence refs, provider boundary, governance/doctor verification, and current behavior satisfaction. |
| AC-009 | TC-009 | negative | Ambiguous, stale, conflicting, low-confidence, or unproven behavior is excluded, questioned, or routed to change instead of frozen as truth. |
| AC-010 | TC-010 | pilot | A bounded existing-project pilot, such as one `justin-mc-lai-skills` skill pack, can be analyzed without whole-repo forced adoption. |

## Validation Note

Coverage truth lives in this package for v1.5.2. Generated QA matrices and runtime JSON may project from it, but they are not requirement authority.
