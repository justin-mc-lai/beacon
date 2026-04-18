<!-- BEACON:START -->
<!-- BEACON:VERSION:v1.3.3 -->
# AGENTS.md

This file is Beacon-managed agent operation guidance.

## Agent behavior
- Keep scope tight and implement the smallest correct change.
- Verify diagnostics/tests before claiming completion.
- Preserve user-authored sections outside Beacon managed blocks.

## Beacon requirement-material usage
- Runtime target version: `v1.3.3`
- Use `docs/beacon/global-boundaries.md` as the canonical Beacon-wide global constraint source.
- Use `docs/beacon/<version>/` as the canonical delivery tree.
- Read progressively in this order:
  1. `docs/beacon/global-boundaries.md`
  2. `docs/beacon/<version>/SUMMARY.md`
  3. `docs/beacon/<version>/execution/index.md`
  4. `docs/beacon/<version>/execution/architecture-blueprint.md`
  5. `docs/beacon/<version>/prd/`, `user-story/`, `qa/test-cases/`
  6. `docs/beacon/<version>/.machine/`
- If context blocks are missing or corrupted, run:
  - `beacon doctor setup-context --project-root .`
  - `beacon doctor verify-context --project-root . --strict`
- After runtime or version upgrades on a real project, sync machine requirement materials before QA:
  - `beacon doctor sync-materials --project-root . --version <version> --all-features`
- For Codex HUD recovery, prefer:
  - `beacon doctor setup-codex-hud-hook --project-root . --version <version> --apply --json`
  - `beacon doctor verify-codex-hud-hook --project-root . --version <version> --json`
<!-- BEACON:END -->
