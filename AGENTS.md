<!-- BEACON:START -->
<!-- BEACON:VERSION:v1.1.11 -->
# AGENTS.md

This file is Beacon-managed agent operation guidance.

## Agent behavior
- Keep scope tight and implement the smallest correct change.
- Verify diagnostics/tests before claiming completion.
- Preserve user-authored sections outside Beacon managed blocks.

## Beacon requirement-material usage
- Runtime target version: `v1.1.11`
- Latest accepted docs line in this repo: `v1.1.12`
- Keep runtime version and docs version separate:
  - runtime guidance follows the Beacon CLI/runtime line
  - feature delivery and acceptance follow the explicit `docs/beacon/<version>/` line you are working against
- Use `docs/beacon/<version>/` as the canonical delivery tree.
- Read progressively in this order:
  1. `docs/beacon/<version>/SUMMARY.md`
  2. `docs/beacon/<version>/execution/index.md`
  3. `docs/beacon/<version>/execution/architecture-blueprint.md`
  4. `docs/beacon/<version>/prd/`, `user-story/`, `qa/test-cases/`
  5. `docs/beacon/<version>/.machine/`
- For the latest accepted prototype reference-pack line, prefer:
  - `docs/beacon/v1.1.12/SUMMARY.md`
  - `docs/beacon/v1.1.12/execution/index.md`
  - `docs/beacon/v1.1.12/execution/architecture-blueprint.md`
  - `docs/beacon/v1.1.12/release/v1.1.12.md`
- For greenfield projects: start with architecture blueprint, then enter think → user-story → prd.
- For takeover projects: document current-state architecture, service map, constraints, and version timeline before new implementation.
- If context blocks are missing/corrupted, run:
  - `beacon doctor setup-context --project-root .`
  - `beacon doctor verify-context --project-root . --strict`
<!-- BEACON:END -->
