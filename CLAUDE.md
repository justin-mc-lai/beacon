<!-- BEACON:START -->
<!-- BEACON:VERSION:v1.1.1 -->
# CLAUDE.md

This file is Beacon-managed runtime guidance.

## Beacon usage
- Use Beacon commands for product workflow execution.
- Keep outputs evidence-first and machine-readable when possible.
- Prefer `beacon <subcommand>` form for cross-environment stability.

## Key commands
- `beacon init --apply`
- `beacon doctor setup-context --project-root .`
- `beacon doctor verify-context --project-root . --strict`
- `beacon workflow start "<feature>" --version <version> --project-root .`
- `beacon workflow --help`
- `beacon status --verbose`

## Requirement materials and docs paths
- Runtime target version: `v1.1.1`
- `docs/beacon/<version>/` is the canonical source of truth.
- `docs/beacon/<version>/SUMMARY.md`
- `docs/beacon/<version>/prd/`
- `docs/beacon/<version>/user-story/`
- `docs/beacon/<version>/qa/test-cases/`
- `docs/beacon/<version>/execution/`
<!-- BEACON:END -->
