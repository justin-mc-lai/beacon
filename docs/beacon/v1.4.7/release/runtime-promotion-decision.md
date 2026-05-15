# Beacon v1.4.7 Runtime Promotion Decision

## Current Decision

- decision: `approved`
- current runtime/default docs line: `v1.4.7`
- reviewed_at: `2026-05-16`
- scope: `runtime promotion decision`

## What Is Already True

`v1.4.7` currently has:

- frozen requirement packages
- accepted change surfaces
- implemented support-surface slices
- implemented bounded automation closure-state kernel slice
- implemented automation support-review / truth-refreeze / promotion-proof second slice
- planning-line QA evidence for all accepted feature packages
- planning-line release materials

## Why Promotion Is Approved

Promotion is approved because five conditions are now satisfied:

1. accepted runtime-facing slices are implemented
2. targeted QA for the promoted scope is passing
3. required active-line execution docs now exist under `docs/beacon/v1.4.7/execution/`
4. version truth, package exports, managed context, and core host skill anchors are aligned to `v1.4.7`
5. real-project validation confirms Beacon behaves correctly on a nontrivial project and can close a repaired feature through `qa -> release -> gate`

## Promotion Entry Criteria

Promotion to current runtime release should require all of the following:

1. accepted `v1.4.7` runtime-facing slices remain fully implemented
2. targeted QA remains passing after promotion edits
3. release-facing proof stays refreshed after active-line updates
4. version-surface governance checks pass
5. managed context sync and verification pass for `v1.4.7`
6. future runtime-facing expansion continues to respect bounded automation authority

## Expected Promotion Validation

At minimum, promotion review should be prepared to run:

```bash
python3 -m beacon.main doctor sync-version-surfaces --project-root . --json
python3 -m beacon.main doctor setup-context --project-root . --version v1.4.7 --sync-materials --all-features --json
python3 -m beacon.main doctor verify-version-surfaces --project-root . --strict --json
python3 -m beacon.main doctor verify-context --project-root . --strict --json
python3 -m beacon.main release check v1.4.7 --project . --json
python3 -m pytest -q tests/test_v147_bounded_automation_closure_state_kernel.py tests/test_v147_automation_support_review_and_promotion_contract.py
```

Additional promotion-grade QA commands should be appended when later runtime-facing slices land.

## Latest Real-Project Proof

The strongest currently recorded real-project proof is:

- project: `shopxo_canada`
- docs target: `v1.0.0`
- feature: `admin-merchandising-analytics`
- QA run id: `run-20260516T004007963577`
- result:
  - `qa status = passed`
  - `ac_accepted = 8/8`
  - `release_ready = true`
  - `release check = pass`
  - `gate check release = Pass`

Reference:

- `docs/beacon/v1.4.7/release/shopxo-canada-real-project-proof-2026-05-16.md`

## Executive Read

`v1.4.7` is now strong enough to be:

- current Beacon runtime release line
- current docs default line
- the bounded automation and host-meta-protocol baseline

## Recommended Next Move

- keep `v1.4.7` as the active runtime/docs line
- continue later runtime-facing slices under later version lines
- use real-project validation to distinguish Beacon runtime safety from project-local release blockers
