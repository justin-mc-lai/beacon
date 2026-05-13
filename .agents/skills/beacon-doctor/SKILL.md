---
name: beacon-doctor
description: Use when the user needs Beacon to repair context, sync materials, diagnose environment or package drift, or restore the workflow to a usable state through Beacon's current support surface.
---

# Beacon Doctor

This skill routes repair and diagnostics through Beacon's `doctor` surface.

The public command stays on Beacon's current support surface and uses the shared diagnostics read model.

## Use for

- context repair
- material sync
- environment diagnostics
- package / skill drift checks
- upgrade and recovery support

## Operator rule

Prefer:

- `beacon doctor ...`
- or `beacon doctor ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor ...`)

Use doctor only when blocked, misaligned, or repairing package integrity. It is a support surface, not part of the main 6-command delivery loop.

## Examples

- 适用例：
  - “Beacon 上下文好像漂了，先帮我诊断和修复。”
  - “版本、材料或 skill 包可能没同步，先看 doctor 怎么说。”
- 不适用例：
  - “我只是想知道主链下一步该做什么。” -> 应优先去 `beacon-help` 或 `beacon-status`
