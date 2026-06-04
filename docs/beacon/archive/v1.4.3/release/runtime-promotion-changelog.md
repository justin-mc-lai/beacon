# Beacon v1.4.3 Runtime Promotion Changelog

## Status

- Promotion completed.
- `v1.4.3` is now the current Beacon runtime release line.

## Version Truth

- `beacon/__init__.py`
  - `__version__ == "1.4.3"`
  - `__toolkit_version__ == "v1.4.3"`
- `pyproject.toml`
  - `[project].version == "1.4.3"`
- `beacon/version-truth.json`
  - `package_version == "1.4.3"`
  - `runtime_version == "v1.4.3"`
  - `docs_default_line == "v1.4.3"`
  - `current_runtime_release_line == "v1.4.3"`
  - `lines.v1.4.3.status == "current_runtime_release"`
  - `lines.v1.4.2.status == "historical_release"`
  - `planning_lines == ["v1.3.5"]`

## What Changed

1. Runtime/default docs truth moved from `v1.4.2` to `v1.4.3`
   - root package version, toolkit version, default docs line, and current runtime release line now point at `v1.4.3`.

2. Managed context moved to `v1.4.3`
   - `AGENTS.md`, `CLAUDE.md`, onboarding state, and agent-surface state were refreshed to the promoted line.

3. Release-facing docs were rewritten to release phrasing
   - `docs/beacon/archive/v1.4.3/` now describes `v1.4.3` as the current runtime line rather than a planning-only line.

4. Aggregation-contract release semantics were preserved
   - the umbrella feature remains a version-line aggregation contract and is still exempt from standalone umbrella `prototype`, `technical review`, `implementation plan`, and browser-lane requirements.

5. Promotion evidence was rebuilt and revalidated
   - test-contract index, QA evidence, gate report, release scorecard, and version/context verification were refreshed after promotion.

## Promotion Validation

```bash
rtk python3 -m beacon doctor sync-version-surfaces --project-root . --json
rtk python3 -m beacon doctor setup-context --project-root . --version v1.4.3 --sync-materials --all-features --json
rtk python3 -m beacon doctor verify-version-surfaces --project-root . --strict --json
rtk python3 -m beacon doctor verify-context --project-root . --strict --json
rtk python3 -m beacon doctor build-test-contract-index "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation" --project-root . --version v1.4.3 --json
rtk python3 -m beacon qa run "beacon-v1.4.3-evidence-first-decision-surfaces-and-governed-learning-activation" --project . --version v1.4.3 --json
rtk python3 -m beacon gate check release --project-root . --version v1.4.3 --strict --json
rtk python3 -m beacon release check v1.4.3 --project-root . --json
rtk python3 -m pytest -q tests/test_v120_runtime_release_alignment.py
```

## Done Definition

Promotion is considered complete when:

- version-truth files all point to `1.4.3 / v1.4.3`
- docs and skill packaging describe `v1.4.3` as current
- managed context is anchored to `v1.4.3`
- promotion regression and version-alignment tests pass
- strict release gate and release check pass for `v1.4.3`
