<!-- BEACON:START -->
<!-- BEACON:VERSION:v1.4.0 -->
<!-- BEACON:DOCS_VERSION:v1.4.0 -->
# AGENTS.md

This file is Beacon-managed agent operation guidance.

## Agent behavior
- Keep scope tight and implement the smallest correct change.
- Verify diagnostics/tests before claiming completion.
- Preserve user-authored sections outside Beacon managed blocks.

## Beacon requirement-material usage
- Runtime target version: `v1.4.0`
- Docs target version: `v1.4.0`
- Use `docs/beacon/global-boundaries.md` as the canonical Beacon-wide global constraint source.
- Use `docs/beacon/<version>/` as the canonical delivery tree.
- Read progressively in this order:
  1. `docs/beacon/global-boundaries.md`
  2. `docs/beacon/<version>/SUMMARY.md`
  3. `docs/beacon/<version>/execution/index.md`
  4. `docs/beacon/<version>/execution/architecture-blueprint.md`
  5. `docs/beacon/<version>/prd/`, `user-story/`, `qa/test-cases/`
  6. `docs/beacon/<version>/.machine/`
- For greenfield projects: start with architecture blueprint, then enter think → user-story → prd.
- For takeover projects: document current-state architecture, service map, constraints, and version timeline before new implementation.
- If context blocks are missing/corrupted, run:
  - `beacon doctor setup-context --project-root .`
  - `beacon doctor verify-context --project-root . --strict`
- After runtime/version upgrades on a real project, sync machine requirement materials before QA:
  - `beacon doctor sync-materials --project-root . --version <version> --all-features`

## Version Governance & Manifest Truth
- `beacon/version-truth.json` is the **single source of truth** for all versioned strings in this repository.
- DO NOT manually edit version strings in:
  - `beacon/__init__.py`
  - `SKILL.md` (root and skill-specific)
  - `metadata.json`
  - `.trae/rules/project_rules.md`
- To update versions:
  1. Modify `beacon/version-truth.json`.
  2. Run `beacon doctor sync-version-surfaces --project-root .`.
  3. Verify with `beacon doctor verify-version-surfaces --project-root . --strict`.
- Any drift will block `release` and `gate` flows with reason code `version_surface_governance_drift`.
<!-- BEACON:END -->






