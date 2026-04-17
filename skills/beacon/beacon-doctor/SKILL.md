---
name: beacon-doctor
description: Use when the user needs Beacon to repair context, sync materials, diagnose environment or package drift, or restore the workflow to a usable state through the minimal v1.3.3 human surface.
---

# Beacon Doctor

This skill routes repair and diagnostics through Beacon's `doctor` surface.

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
