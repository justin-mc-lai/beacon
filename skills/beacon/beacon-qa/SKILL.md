---
name: beacon-qa
description: Use when the user wants to verify a Beacon feature, inspect new findings, improve coverage, or assess whether a feature is ready for release through Beacon's current v1.3.12 runtime surface.
---

# Beacon QA

This skill routes verification work through Beacon's `qa` surface.

The public command stays on the `v1.3.9` runtime line while `v1.3.12` defines the shared delivery kernel, read model, and host-native QA contract.

`Beacon Acceptance Kit v1` is the shared QA verdict base. QA should read and project:

- `skill-contract`
- `scenario-suite`
- `trace-scorecard`
- `real-project-proof`

Use the layered verdicts as the release-facing truth, not a single score.

## Use for

- feature verification
- new findings and repair handoff review
- coverage improvement
- release confidence and QA iteration
- shared acceptance proof chain validation

## Operator rule

Prefer:

- `beacon qa ...`
- or `bash skills/beacon/scripts/run_beacon.sh qa ...`

Keep `qa-team`, learning, and auto research hidden behind the public `qa` surface unless the user explicitly asks for internals.
