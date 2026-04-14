---
name: beacon-release
description: Use when the user wants Beacon to judge release readiness, inspect final blocking conditions, or run the last release-facing checks through the minimal v1.3.1 human surface.
---

# Beacon Release

This skill routes final ship / release-readiness work through Beacon's `release` surface.

## Use for

- release readiness
- final go / no-go checks
- last-mile delivery confidence
- checking whether implementation and QA are sufficient to ship

## Operator rule

Prefer:

- `beacon release ...`
- or `bash skills/beacon/scripts/run_beacon.sh release ...`

If the user is still missing core evidence or next-step clarity, route to `beacon-help` or `beacon-qa` before pretending the work is in the release stage.
