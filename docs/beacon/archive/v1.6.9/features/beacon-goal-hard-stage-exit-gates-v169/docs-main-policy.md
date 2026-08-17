# Main docs write policy (tight)

## Allowed on `main` / `master`
- `docs/beacon/**` — feature packages, programs, freeze/truth materials
- `skills/**`, `.agents/**`, `.claude/**`, `.codex/**` (tooling)
- top-level meta: `README.md`, `AGENTS.md`, `CLAUDE.md`, `pyproject.toml`, …

## Forbidden on main (reason `main_docs_policy_forbidden`)
- any other `docs/**` path (e.g. `docs/guide.md`, `docs/marketing/**`, `docs/architecture.md` outside beacon tree)

## Business code still forbidden (`main_implement_forbidden`)
- `beacon/`, `packages/`, `apps/`, `plugins/`, `src/`, `tests/test_*.py`

## Escape
- Admitted worktree leaf branch (preferred)
- Emergency: `BEACON_ALLOW_MAIN_IMPLEMENT=1` + `.beacon/evidence/main-implement-exception.json`
