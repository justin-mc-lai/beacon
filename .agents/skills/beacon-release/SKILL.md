---
name: beacon-release
description: Use when the user wants Beacon to judge release readiness, inspect final blocking conditions, or run the last release-facing checks through Beacon's current v1.4.0 runtime surface.
---

# Beacon Release

This skill routes final ship / release-readiness work through Beacon's `release` surface.

The public command stays on the current **`v1.4.0`** runtime line and uses the shared delivery kernel and release-scorecard behavior defined by the **`v1.4.0`** docs tree (`docs/beacon/v1.4.0/`), unless your project explicitly pins another docs version.
Compatibility wrappers may preserve older runtime aliases, but release truth, scorecards, and gate language should follow the `v1.4.0` docs line.

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

## Inputs Contract

- `project-root`
- `version`
- `feature` or version release target
- layered QA proof
- release gate status
- version surface governance status

## Decision Protocol

- Continue in `release` only when implementation and QA have already produced sufficient evidence.
- Block on missing QA layers, unresolved truth drift, version-surface drift, or unresolved release gate blockers.
- Prefer explicit no-go verdicts over soft optimism when evidence is incomplete.
- Treat `real-project-validation` as highest proof, but still require the other layers.

## Anti-Inertia Notes

- `release` is not a place to finish implementation or invent acceptance truth.
- A green-looking dashboard without evidence chain is not release closure.
- Version drift across docs, package, and runtime surfaces must block ship.
- `release` cannot rewrite frozen truth or override gate truth by itself.

## Learning Notes

- Reuse prior release blockers as warning signals for current no-go checks.
- Learning may influence inspection order, but it does not override gate verdicts.
- Stale release learning should trigger re-check, not silent acceptance.

## Backstop CLI

- `beacon release ...`
- `beacon qa ...` when proof is incomplete
- `beacon doctor verify-version-surfaces --project-root . --strict`
