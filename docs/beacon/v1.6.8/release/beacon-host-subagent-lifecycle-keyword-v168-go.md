# Release GO note — host subagent keyword + v1.6.8 line

- **date**: 2026-07-20
- **authority**: `beacon-eval-release` (human confirmation still required for product ship messaging)
- **release check**: `beacon release check v1.6.8` → **pass** / `release_ready=true`
- **artifact**: `docs/beacon/v1.6.8/release/release-check-v1.6.8-host-subagent-latest.json`
- **current feature driving scorecard**: `beacon-worktree-progressive-skill-flow-v168` (revision latest)
- **companion delivered feature**: `beacon-host-subagent-lifecycle-keyword-v168` (contract suite 17 passed; pack install)

## Hooks installed

| Hook | Result |
|------|--------|
| Codex fixed HUD (`doctor setup-codex-hud-hook --apply`) | applied; verify **WARN** on non-required freshness/version match (restart Codex session recommended) |
| `beacon-post-release-local-install` | **ran with --confirm** run-id `run-20260720T053345Z-b45d` |

Post-release follow-up confirmed:

- legacy skill cleanup
- Claude global skill install/verify
- Codex + Claude agent surface setup/verify
- context setup/verify
- global CLI launchers → **Beacon CLI v1.6.8**
- agent eval live release_hook regression-core

## Operator next

1. Restart Codex session so HUD hook activation is fresh.
2. Optional: reinstall host subagent packs in projects that need them:
   `beacon doctor install-subagent-pack -p . --host-runtime codex --pack minimal`
3. Product ship / tag / publish remains **human GO** beyond release-check pass.
