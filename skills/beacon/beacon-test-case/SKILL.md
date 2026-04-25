---
name: beacon-test-case
description: Use when the user wants to create, extend, or audit test cases and acceptance coverage for a Beacon feature through Beacon's current v1.3.8 runtime surface.
---

# Beacon Test Case

This skill routes acceptance coverage work through Beacon's `test-case` surface.

The public command stays on the current `v1.3.8` runtime line and uses the host-native requirement runtime defined by the `v1.3.8` docs.

## Use for

- test-case generation
- acceptance coverage expansion
- boundary and regression coverage review
- QA preparation before implementation or verification

## Operator rule

Prefer:

- `beacon test-case ...`
- or `bash skills/beacon/scripts/run_beacon.sh test-case ...`

The public goal is coverage readiness, not exposing internal QA lanes yet.
