# Governance Workflow

## Goal

Keep Beacon source changes and current-version docs aligned.

## Canonical Loop

1. Change Beacon source in `beacon/`.
2. Converge current-version docs and skill surfaces:
- `README.md`
- `SKILL.md`
- `skills/beacon/`
- `docs/beacon/<current>/`
3. Run current-contract checks.
4. Run material and delivery audits.
5. Run release gate / release readiness checks when the change is intended to be release-grade.

## Command Bundles

### Quick

- `python3 -m pytest -q tests/test_docs_current_contract.py tests/test_skill_standard_layout.py tests/test_v110_docs_examples_contract.py`
- `python3 -m beacon.main doctor verify-materials --project-root <root> --version <version> --json`

### Delivery

- `python3 -m beacon.main doctor verify-delivery --project-root <root> --version <version> --json`
- `python3 -m beacon.main gate check release --project-root <root> --version <version> --json`
- `python3 -m beacon.main release check <version> --project <root>`

## Expected Behavior

- `quick` should pass before closing a docs-convergence task.
- `delivery` may fail during active iteration; use failures as current blockers, not as reasons to skip the checks.
- The governance script should be the smallest reproducible path for Beacon self-iteration.
