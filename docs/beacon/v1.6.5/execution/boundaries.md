# Execution Boundaries - v1.6.5

## Scope Boundary

v1.6.5 is a same-version, six-phase program. Phase boundaries are verification boundaries, not scope cuts.

## Truth Boundary

- Feature truth lives only under `docs/beacon/v1.6.5/features/<feature>/`.
- Program artifacts under `programs/beacon-oss-borrow-hardening-v165/` are advisory planning evidence.
- Old `prd/`, `user-story/`, and `qa/test-cases/` compatibility mirrors must not become independent truth.

## Implementation Boundary

- `beacon-workspace-pool-lease-v165` may change workspace admission, pool state, and workspace commands.
- `beacon-loop-readiness-audit-v165` may add doctor audit surfaces and scoring helpers.
- `beacon-loop-pattern-registry-v165` may add registry files, schema validation, and audit integration.
- `beacon-protected-path-denylist-v165` may change `global-boundaries`, protected path matching, and write-surface guards.
- `beacon-loop-token-budget-v165` may add budget ledger utilities, status reporting, and kill-switch checks.
- `beacon-loop-failure-mode-catalog-v165` may add failure catalog material and validators.

## Gate Boundary

- Planner and program artifacts do not imply freeze, QA, or release pass.
- Each phase requires independent truth integrity, requirement clarity, freeze preflight, implementation evidence, QA, and release checks.
- Docs-only, placeholder, fake runner, zero assertion, and placeholder evidence patterns are not closure.
