# Installing Beacon Host Skills for Codex

Enable Beacon's `v1.6.0` harness-first host-visible workflow pack in Codex through native skill discovery.

## Installed skill root

Beacon's canonical install roots are:

- Beacon source of truth:
  - `/absolute/path/to/beacon/skills/beacon`
- Codex discovery root:
  - `~/.agents/skills/beacon` -> `/absolute/path/to/beacon/skills/beacon`

Do not also install Beacon under any of these paths:

- `~/.codex/skills/beacon`
- `~/.codex/skills/beacon/skills/beacon`
- backup symlinks such as `~/.codex/skills/beacon.bak-*`

Those paths create duplicate discovery and can make Codex restart onto a stale Beacon root.

## Public host-visible skills

Beacon v1.6.0 uses only harness-first skill names:

- `beacon-planner-*`
- `beacon-generator-*`
- `beacon-evaluator-*`
- `beacon-governor-*`

Old aliases such as `using-beacon`, `beacon-prd`, `beacon-user-story`, `beacon-test-case`, `beacon-implement`, `beacon-qa`, `beacon-release`, and `beacon-brainstorm` are intentionally not emitted in the packaged host-visible skill root.

## Installation

1. Clone this repository to a stable local path.
2. Link the packaged Beacon skill root into Codex's native discovery path:

```bash
mkdir -p ~/.agents/skills
ln -s /absolute/path/to/beacon/skills/beacon ~/.agents/skills/beacon
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\beacon" "C:\absolute\path\to\beacon\skills\beacon"
```

3. Restart Codex.

## Cleanup before reinstall

If Beacon was previously installed in multiple places, clean it first:

```bash
rm -rf ~/.codex/skills/beacon
rm -f ~/.codex/skills/beacon.bak-*
rm -f ~/.agents/skills/beacon
mkdir -p ~/.agents/skills
ln -sf /absolute/path/to/beacon/skills/beacon ~/.agents/skills/beacon
```

## Verify

```bash
beacon --version
beacon --help
find ~/.agents/skills/beacon -maxdepth 2 -name SKILL.md | sort
python3 scripts/check_skill_drift.py --project-root . --json
beacon skill package verify --project-root . --version v1.6.0 --package-root skills/beacon --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.6.0 --json
```

Expected:

- exactly one Codex Beacon root at `~/.agents/skills/beacon`
- no `~/.codex/skills/beacon`
- `beacon skill package verify --package-root skills/beacon --version v1.6.0` passes
- no old host-visible aliases exist under `skills/beacon`

## HUD hook recovery

Use the doctor-managed hook instead of ad hoc config edits:

```bash
beacon doctor setup-codex-hud-hook --project-root . --version v1.6.0 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.6.0 --json
```

## Notes

- `~/.agents/skills/beacon` is the canonical install root.
- `~/.codex/skills/beacon` is not a supported install location.
- `brainstorm`, `team`, `implement-team`, and `qa-team` remain hidden machine lanes, not public skills.
- The nested public skills exist to make the `v1.6.0` harness-first surface prompt-triggerable.
- CLI compatibility may keep legacy commands, but old names must not reappear as host-visible skill directories in `skills/beacon`.
