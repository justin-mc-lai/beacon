# Freeze Readiness Checklist

This is a non-canonical support reference for humans.

Use it before treating a requirement package as stable enough for execution.

## Checklist

- `prd`, `user-story`, and `test-case` are present for the feature
- acceptance is concrete enough for execution and QA
- unresolved ambiguity no longer changes promised behavior
- required prototype handoff is present when real UX/UI handoff exists
- known risks are explained, not silently ignored
- route after freeze is clear: `implement` or `qa`, not open-ended brainstorming

## Route Hint

- freeze not ready because promise still moves -> `beacon-change` or requirement surfaces
- freeze ready, execution next -> `beacon-implement`
