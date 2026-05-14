# Release Blocker Taxonomy

This is a non-canonical support reference for humans.

Use it to scan whether a blocker belongs to truth, execution, QA, or release governance.

## Common blocker classes

- truth blocker:
  - promise drift
  - acceptance ambiguity
  - missing requirement package piece
- execution blocker:
  - implementation incomplete
  - prototype handoff missing when required
  - source conflict unresolved
- QA blocker:
  - evidence missing
  - regression unresolved
  - `stop_for_repair`
- release blocker:
  - pass/fail ambiguity
  - unresolved high-severity finding
  - evidence chain incomplete

## Route Hint

- truth blocker -> `beacon-change` or requirement surfaces
- execution blocker -> `beacon-implement`
- QA blocker -> `beacon-qa`
- release blocker -> `beacon-release`
