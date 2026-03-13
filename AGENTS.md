<!-- BEACON:START -->
<!-- BEACON:VERSION:v1.1.1 -->
# AGENTS.md

This file is Beacon-managed agent operation guidance.

## Agent behavior
- Keep scope tight and implement the smallest correct change.
- Verify diagnostics/tests before claiming completion.
- Preserve user-authored sections outside Beacon managed blocks.

## Beacon requirement-material usage
- Runtime target version: `v1.1.1`
- Use `docs/beacon/<version>/` as the canonical delivery tree.
- Treat `docs/product/<version>/` as a compatibility mirror.
- Keep canonical + compatibility artifacts aligned when mirror output is generated.
- Prioritize `prd`, `user-story`, `qa/test-cases`, and `execution` artifacts.
- If context blocks are missing/corrupted, run:
  - `beacon doctor setup-context --project-root .`
  - `beacon doctor verify-context --project-root . --strict`
<!-- BEACON:END -->
