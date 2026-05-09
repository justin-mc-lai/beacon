---
name: beacon-toolkit-branch-governance
description: Use when the user wants a human-readable git branch/worktree governance view or verification through Beacon's doctor support surface.
---

# Beacon Toolkit Branch Governance

This skill routes branch-governance inspection through Beacon's `doctor branch-governance` support surface.

## Use for

- inspect the resolved branch-governance template for a version
- show the branch flow diagram, current position, and recommended next action
- verify whether the governance contract is currently blocked
- review evidence-contract requirements before entering `implement`

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon doctor branch-governance show ...`
- `beacon doctor branch-governance verify ...`
- or `beacon doctor branch-governance ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor branch-governance ...`)

Default expectations:

- treat `doctor branch-governance` as the human-facing deterministic git governance surface
- keep project-level writes on the canonical metadata transaction path
- let `implement` consume the same projected contract instead of maintaining a second truth

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the governance result into the main Beacon workflow.
