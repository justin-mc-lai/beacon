---
name: beacon-release
description: Use when the user wants Beacon to judge release readiness, inspect final blocking conditions, or run the last release-facing checks through Beacon's current v1.4.0 runtime surface.
---

# Beacon Release

This skill routes final ship / release-readiness work through Beacon's `release` surface.

The public command stays on the current **`v1.4.0`** runtime line and uses the shared delivery kernel and release-scorecard behavior defined by the **`v1.4.0`** docs tree (`docs/beacon/v1.4.0/`), unless your project explicitly pins another docs version.

`Beacon Acceptance Kit v1` is the release-facing proof base. Release should treat these as required proof layers:

- `skill-contract`
- `scenario-suite`
- `trace-scorecard`
- `real-project-proof`

`real-project-validation` is the highest proof layer, but not the only one.

## Use for

- release readiness
- final go / no-go checks
- last-mile delivery confidence
- checking whether implementation and QA are sufficient to ship
- release proof chain validation

## Operator rule

Prefer:

- `beacon release ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh release ...`

If the user is still missing core evidence or next-step clarity, route to `beacon-help` or `beacon-qa` before pretending the work is in the release stage.
