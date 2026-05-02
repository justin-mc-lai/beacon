---
name: beacon-test-case
description: Use when the user wants to create, extend, or audit test cases and acceptance coverage for a Beacon feature through Beacon's current v1.3.9 runtime surface.
---

# Beacon Test Case

This skill routes acceptance coverage work through Beacon's `test-case` surface.

The public command stays on the current `v1.3.9` runtime line and uses the host-native requirement runtime defined by the `v1.3.9` docs.
Default host execution now enters the requirement bridge family before compatibility fallback.

## Use for

- test-case generation
- acceptance coverage expansion
- boundary and regression coverage review
- QA preparation before implementation or verification
- truth-projected case generation from frozen `user-story / prd / qa/test-cases` materials

## Operator rule

Prefer:

- `beacon test-case ...`
- or `bash skills/beacon/scripts/run_beacon.sh test-case ...`

The public goal is coverage readiness, not exposing internal QA lanes yet.
When host-native runtime is available, `test-case` should first use the wrapper-provided bridge and project from requirement truth or existing QA rows instead of emitting a generic placeholder matrix.
