# Beacon v1.4.6 Runtime Promotion Changelog

## Status

- Promotion completed.
- `v1.4.6` is now the current Beacon runtime release line.

## Version Truth

- `beacon/__init__.py`
  - `__version__ == "1.4.6"`
  - `__toolkit_version__ == "v1.4.6"`
- `pyproject.toml`
  - `[project].version == "1.4.6"`
- `beacon/version-truth.json`
  - `package_version == "1.4.6"`
  - `runtime_version == "v1.4.6"`
  - `docs_default_line == "v1.4.6"`
  - `current_runtime_release_line == "v1.4.6"`
  - `lines.v1.4.6.status == "current_runtime_release"`
  - `lines.v1.4.5.status == "historical_release"`

## What Changed

1. Runtime/default docs truth moved from `v1.4.5` to `v1.4.6`
   - package version, toolkit version, docs default line, and current runtime release line now point at `v1.4.6`.

2. Managed context moved to `v1.4.6`
   - `AGENTS.md`, `CLAUDE.md`, onboarding state, and agent-surface state were refreshed to the promoted line.

3. Release-facing docs were rewritten to release phrasing
   - `docs/beacon/archive/v1.4.6/` now describes `v1.4.6` as the current runtime line rather than a candidate line.

4. Local agent surfaces were refreshed
   - Codex / Claude / Cursor / Trae / Windsurf local skill surfaces now point at the promoted runtime/docs line.

5. Promotion evidence was rebuilt and revalidated
   - version-surface verification, managed context verification, release gate, release scorecard, and release check were refreshed after promotion.
   - final authoritative QA/release proof uses run `run-20260514T002632744979`.

## Promotion Validation

```bash
python3 -m beacon.main doctor sync-version-surfaces --project-root . --json
python3 -m beacon.main doctor setup-context --project-root . --version v1.4.6 --sync-materials --all-features --json
python3 -m beacon.main doctor verify-version-surfaces --project-root . --strict --json
python3 -m beacon.main doctor verify-context --project-root . --strict --json
python3 -m beacon.main gate check release --project-root . --version v1.4.6 --mode strict --json
python3 -m beacon.main release scorecard v1.4.6 --project . --json
python3 -m beacon.main release check v1.4.6 --project . --json
python3 -m pytest -q tests/test_v120_runtime_release_alignment.py
```

## Done Definition

Promotion is considered complete when:

- version-truth files all point to `1.4.6 / v1.4.6`
- docs and skill packaging describe `v1.4.6` as current
- managed context is anchored to `v1.4.6`
- promotion regression and version-alignment checks pass
- strict release gate and release check pass for `v1.4.6`
