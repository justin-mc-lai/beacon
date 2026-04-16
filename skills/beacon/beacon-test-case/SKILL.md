---
name: beacon-test-case
description: Use when the user wants to create, extend, or audit test cases and acceptance coverage for a Beacon feature through the minimal v1.3.2 human surface.
---

# Beacon Test Case

This skill routes acceptance coverage work through Beacon's `test-case` surface.

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
