# Beacon Support Surface Next Route Rendering

## Scope

- version: `v1.4.3`
- status: `implementation-spec-ready`

## Goal

Make every support-surface result end in an explicit next action rather than a vague summary.

## Required Next Route Fields

- `command`
- `why`
- `target_surface`
- `priority`
- `prerequisites`

## Allowed Target Surfaces

- `beacon-change`
- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-prototype`
- `beacon-help`

## Rendering Examples

### CEO Review

```json
{
  "command": "beacon change \"v1.4.3\"",
  "why": "Requirement direction must be reframed before freeze remains valid.",
  "target_surface": "beacon-change",
  "priority": "high",
  "prerequisites": ["accepted ceo-review decision"]
}
```

### Design Review

```json
{
  "command": "beacon prototype \"beacon-v1.4.3-design-review-surface-and-prototype-governance\"",
  "why": "UI surface exists and design-review cleared prototype entry.",
  "target_surface": "beacon-prototype",
  "priority": "medium",
  "prerequisites": ["design_verdict=ready_for_prototype"]
}
```

### Learn

```json
{
  "command": "beacon help",
  "why": "Learning affects route choice and should be exposed in operator guidance.",
  "target_surface": "beacon-help",
  "priority": "medium",
  "prerequisites": ["route influence summary available"]
}
```

## Boundary Rule

If no valid next route exists, Beacon must emit:

- `blocked: true`
- primary reason code
- `next_route.command = beacon-help`

This prevents orphaned support-surface outcomes.
