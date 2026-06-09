# Ruff / Pylint CI Gate Context

**Version**: `v1.6.0`
**Artifact role**: planner support advisory
**Truth authority**: false

## Source Anchors

- `pyproject.toml` currently defines only `pytest` under `[project.optional-dependencies].dev`.
- `.github/workflows/beacon-release-gate.yml` installs `pip install -e .` and runs `bash scripts/ci/preflight_gate.sh`.
- Local tool probe on 2026-06-09: `ruff` missing, `pylint` missing.
- Current source scale: 229 Python files under `beacon/`; 41 modules exceed 800 lines.
- Current test scale: 348 test files and 1900+ test functions.

## Assessment

Add `ruff` first as the fast structural lint gate. Defer `pylint` as an advisory-only local/deep check until the high-churn legacy modules have an explicit suppression and ownership policy.

Do not turn all lint findings into release blockers in one step. The current codebase has large historical modules such as `beacon/utils/qa_feature.py`, `beacon/commands/gate.py`, and `beacon/commands/implement/commands.py`; a hard all-file lint gate would mostly expose backlog rather than protect active changes.

## Recommended Context Pack

Keep:

- `pyproject.toml`
- `.github/workflows/beacon-release-gate.yml`
- `scripts/ci/preflight_gate.sh`
- high-churn modules touched by the current change
- a small allowlist or baseline for known legacy lint debt

Discard from the first gate:

- full `pylint` score enforcement
- formatting rewrites across untouched historical modules
- unrelated import sorting churn outside changed files

## Phased Route

1. Add `ruff` to `dev` optional dependencies.
2. Add `[tool.ruff]` with Python 3.9 target and a conservative rule set.
3. Add `ruff check beacon tests` to preflight in advisory or changed-file mode first.
4. Promote to hard gate after one release line once baseline findings are either fixed or explicitly ignored.
5. Add `pylint` later for selected modules only, starting with new leaf modules such as `skill_eval_kit.py`, `version_surface.py`, and `project_hooks.py`.

## Route Recommendation

If accepted, route to `beacon-gen-implement` for a small CI implementation change. Do not modify requirement truth from this advisory alone.
