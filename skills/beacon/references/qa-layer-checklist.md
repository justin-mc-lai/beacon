# QA Layer Checklist

This is a non-canonical support reference for humans.

Use it to quickly distinguish implementation progress from actual verification closure.

## Checklist

- test scenarios map back to frozen acceptance
- evidence exists for the current pass/fail claim
- blockers are classified, not hand-waved
- `stop_for_repair` is treated as a real stop
- support commentary is not being confused with QA verdict
- release-facing judgment is kept for `beacon-release`

## Route Hint

- evidence still weak -> `beacon-qa`
- QA passed but release judgment still needed -> `beacon-release`
