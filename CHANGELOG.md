## [1.6.7] — 2026-07-16 · version-surface + catalog cutover

### Fixed
- Promote package/runtime/docs default line to **v1.6.7** via `beacon/version-truth.json` and `beacon doctor sync-version-surfaces`
- Align public entry surfaces (README current-line claims, root `SKILL.md`, host skill metadata) with package truth
- Advance version-truth-catalog active window to `v1.6.5 / v1.6.6 / v1.6.7` (archive older delivery roots)

### Notes
- Feature program `beacon-unified-topology-loop-goal-v167` remains the v1.6.7 capability delivery (GitScopeGraph + loop-goal R7)
- This entry closes the release-entry consistency gap called out after comprehensive project diagnosis

## [1.6.1] — 2026-06-23 · fix/p0-p1-p2 (P0/P1/P2 fix batch)

### Added (P1)
- `scripts/beacon-install.sh` — idempotent symlink installer for all 10 host surfaces (agents, codex, cursor, trae, windsurf, opencode, pi, qoder, trellis, reasonix); guards against duplicate real-directory installs; supports `DRY_RUN=true`
- `scripts/generate-host-surfaces.py` — single-spec host surface generator driven by `beacon/version-truth.json`; supports `--check` (CI) and `--dry-run` (preview) modes; replaces manual maintenance of 10+ host directories
- `.github/workflows/version-gate.yml` — CI gate that fails the build when `pyproject.toml`, `README.md`, or `SKILL.md` diverge from `beacon/version-truth.json`; triggered on every push to main/pre-main/beacon/v*/fix/*/feat/* and every PR targeting main

### Fixed (P0)
- `.gitignore` — added rules to stop tracking Python build artifacts (`__pycache__/`, `*.egg-info/`, `dist/`, `build/`), Node artifacts (`node_modules/`, `packages/*/dist/`, `*.tsbuildinfo`), Beacon runtime state (`test-results/`, `.beacon/state/`, `.reasonix/truncated-results/`, `.omc/sessions/`), and IDE/OS noise (`.DS_Store`, `.idea/`)

### Pending (requires local git CLI — cannot be done via web editor)
- Remove already-tracked generated artifacts: `git rm -r --cached test-results/ beacon.egg-info/ .reasonix/truncated-results/ .omc/sessions/`
- Fix README.md version references: `sed -i 's/v1\.6\.0/v1\.6\.1/g' README.md && git commit -m "docs(p0): update README version v1.6.0 -> v1.6.1"`
## [1.6.12] — 2026-08-17 · main delivery-surface recovery + goal LoopX acceptance closure

### Added
- Program-level lake driver: `beacon/utils/program_driver.py` + `beacon program drive <slug>` CLI. Consumes `build_program_orchestrator_state` routes and dispatches one lake-stage per turn (truth → implement → qa) to the host agent; release is never dispatched (human gate). Stops emit `reason_code` + `resume_action` (+ `recommended_command`) per AC-039, with blocked-streak (≥3) / turn-budget guards and filesystem-evidence crash resume. Drive state lives at `docs/beacon/<v>/programs/<slug>/program-drive-state.json`; lock at `.beacon/state/program-drive/<slug>.lock`.
- Goal run terminal takeover hint (`program_takeover` in facade payload + `recommended_next.program`): when the program route has a pending next lake, goal output points to `beacon program drive`; prompt-level only, goal never auto-spawns the driver.

### Fixed
- Restore deleted `pyproject.toml`, `tests/` tree (484 files incl. 25 v1.6.12 goal canaries), and `scripts/` from the pre-checkpoint snapshot; main is installable and testable again.
- Track the canonical `skills/beacon/` package (1+6 public surface + patterns/incidents) in git; remove implicit untracked symlink dependency.
- Close the v1.6.12 goal feature acceptance: 26 canary + 16 life-cycle guardrail tests green on main, implement/QA evidence recorded, feature-graph + authenticated program freeze pass, program state aligned (`program_frozen`/all-lakes-complete).
- Rebuild `test-contract-index` from frozen truth; fix TC-007 to reference the real tracked legacy state bundle.
- Align version surfaces: onboarding/python/README to v1.6.12, catalog active window converged to v1.6.10/11/12, stale top-level delivery roots relocated to `docs/beacon/archive/`.
- Add ignore rules for `packages/**` build artifacts and `*.egg-info/`; untrack generated backups and egg-info metadata.

### Notes
- Release gate: still awaits human confirmation on v1.6.12 (loop-goal release is human-gated).

## [1.6.7] — 2026-07-16 · version-surface + catalog cutover
