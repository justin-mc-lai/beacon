<!-- BEACON:START -->
<!-- BEACON:VERSION:v1.1.7 -->
# AGENTS.md

This file is Beacon-managed agent operation guidance.

## Agent behavior
- Keep scope tight and implement the smallest correct change.
- Verify diagnostics/tests before claiming completion.
- Preserve user-authored sections outside Beacon managed blocks.

## Beacon requirement-material usage
- Runtime target version: `v1.1.7`
- Use `docs/beacon/<version>/` as the canonical delivery tree.
- Prioritize `SUMMARY`, `execution`, `prd`, `user-story`, `qa/test-cases`, and `release` artifacts.
- Prefer `docs/beacon/<version>/` over `.beacon/` for current release truth.
- If context blocks are missing/corrupted, run:
  - `beacon doctor setup-context --project-root .`
  - `beacon doctor verify-context --project-root . --strict`
<!-- BEACON:END -->
