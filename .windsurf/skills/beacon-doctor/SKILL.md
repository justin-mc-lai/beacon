---
name: beacon-doctor
description: Use when the user needs Beacon to repair context, sync materials, diagnose environment or package drift, or restore the workflow to a usable state through Beacon's current support surface.
---

# Beacon Doctor

## Overview

This skill routes repair and diagnostics through Beacon's `doctor` support surface.

It diagnoses context, package, version, and environment drift, then routes recovery back to the usable workflow. It does not become part of the default mainline.

## When to Use

- context repair
- material sync
- environment diagnostics
- package / skill drift checks
- upgrade and recovery support

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not substitute for requirement or release surfaces once the environment is healthy

## Workflow / Decision Loop

- diagnose context, package, runtime, or version drift
- identify repair route and required commands
- restore the project to a state where truth/execution/gate surfaces can run normally

## Common Rationalizations

- “doctor 都能修，那就不用看 requirement/gate 了。” -> 不允许；doctor 只修运行条件
- “材料有点漂，先忽略继续做。” -> 不允许；doctor 应先修正上下文真相
- “既然是诊断面，可以顺手改正式 requirement。” -> 不允许；diagnostics 不改 canonical truth

## Red Flags

- context/material drift 已知存在，却继续执行主链
- package/version drift 没有显式 reason code
- `doctor` 被当成常驻主流程步骤

## Verification

- repair output explains the drift source and recovery route
- workflow can re-enter the proper truth/execution/gate surface after repair
- doctor actions remain support-only and do not mutate requirement truth semantics

## Evidence Produced

- diagnostics payload
- repair recommendation
- package/version/context drift findings

## State Updated

- diagnostic state and repair artifacts

## Gate Impact

- no direct product gate verdict
- may block workflow entry until context or version integrity is restored

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
