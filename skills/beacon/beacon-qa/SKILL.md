---
name: beacon-qa
description: Use when the user wants to verify a Beacon feature, inspect new findings, improve coverage, or assess whether a feature is ready for release through the minimal v1.3.1 human surface.
---

# Beacon QA

This skill routes verification work through Beacon's `qa` surface.

## Use for

- feature verification
- new findings and repair handoff review
- coverage improvement
- release confidence and QA iteration

## Operator rule

Prefer:

- `beacon qa ...`
- or `bash skills/beacon/scripts/run_beacon.sh qa ...`

Keep `qa-team`, learning, and auto research hidden behind the public `qa` surface unless the user explicitly asks for internals.
