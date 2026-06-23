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

