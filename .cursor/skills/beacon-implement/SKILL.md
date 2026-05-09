---
name: beacon-implement
description: Use when the user wants to plan or run implementation through Beacon's current v1.4.0 runtime surface. Keep `implement` as the only public implementation entrypoint; treat team runtime and subagent lanes as internal.
---

# Beacon Implement

This skill routes execution work through Beacon's `implement` surface.

The execution contract is aligned to the `v1.4.0` docs line and shared delivery kernel.
Compatibility wrappers may preserve older runtime aliases, but `implement` should read current truth from `docs/beacon/v1.4.0/`.

## Use for

- implementation planning
- implementation execution
- implementation progress / handoff checks
- implementation readiness after freeze and technical review
- requirement completeness checks before execution

## Operator rule

Prefer:

- `beacon implement ...`
- or `beacon implement ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh implement ...`)

Do not expose `implement-team`, planner/implementer/tester roles, or lane-level runtime details unless the user explicitly asks for internals.

## Inputs Contract

- `project-root`
- `version`
- `feature`
- frozen `prd / user-story / test-case`
- conditionally required `prototype` when the feature has real UX/UI handoff
- current gate / blocked reason / branch or execution governance context when present

## Decision Protocol

- Enter `implement` only after requirement truth is frozen enough for execution.
- Block when frozen truth requires `change`, when cutover guardrails fail, or when a conditionally triggered prototype is still missing.
- Keep `implement` as the only execution entry; `ask --execute` and support surfaces may route here but must not replace it.
- Prefer explanation and routing logic in skill surface; keep final schema, contract, and gate writes in Python guardrails.
- When dual-read or compatibility windows exist, fail closed on mismatch.

## Anti-Inertia Notes

- `implement` is not permission to rewrite requirement truth.
- `goal`, task ledgers, or partial execution progress do not define completion truth.
- If the feature needs UX/UI handoff and prototype is triggered, do not skip straight into coding.
- Team/runtime internals stay internal unless the user explicitly asks for them.
- `implement` cannot rewrite frozen truth or override gate truth by itself.

## Learning Notes

- Reuse implementation learning to avoid repeated blocked paths or flaky cutovers.
- Learning may shape route explanation and caution, but cannot override gate truth.
- Downgrade stale learning instead of silently trusting it.

## Backstop CLI

- `beacon implement ...`
- `beacon change ...` when truth must reopen
- `beacon qa ...` after implementation evidence is ready
