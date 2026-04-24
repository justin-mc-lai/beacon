---
name: beacon-doctor
description: Use when the user needs Beacon to repair context, sync materials, diagnose environment or package drift, or restore the workflow to a usable state through Beacon's current v1.3.7 runtime surface.
---

# Beacon Doctor

This skill routes repair and diagnostics through Beacon's `doctor` surface.

The public command stays on the current `v1.3.7` runtime line and uses the shared read model and diagnostics behavior defined by the `v1.3.7` docs.

## Use for

- context repair
- material sync
- environment diagnostics
- package / skill drift checks
- upgrade and recovery support

## Operator rule

Prefer:

- `beacon doctor ...`
- or `bash skills/beacon/scripts/run_beacon.sh doctor ...`

Use doctor only when blocked, misaligned, or repairing package integrity. It is a support surface, not part of the main 6-command delivery loop.
