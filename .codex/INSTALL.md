# Installing Beacon Host Skills for Codex

Enable Beacon's `v1.3.8` host-visible workflow pack in Codex through native skill discovery.

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

- umbrella:
  - `beacon`
  - `using-beacon`
- primary:
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
  - `beacon-prototype`
  - `beacon-implement`
  - `beacon-qa`
  - `beacon-release`
- support:
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`
  - `beacon-archive`

## Optional supplemental skills

- `beacon-toolkit-lighthouse`
- `beacon-prd-bootstrap`
- `beacon-brainstorm`
- `beacon-real-project-validation`

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
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.8 --json
```

Expected:

- exactly one Codex Beacon root at `~/.agents/skills/beacon`
- no `~/.codex/skills/beacon`
- `beacon --version` prints `v1.3.8`
- `beacon --help` does not expose a `change` subcommand

## HUD hook recovery

Use the doctor-managed hook instead of ad hoc config edits:

```bash
beacon doctor setup-codex-hud-hook --project-root . --version v1.3.8 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.8 --json
```

## Notes

- `~/.agents/skills/beacon` is the canonical install root.
- `~/.codex/skills/beacon` is not a supported install location.
- `brainstorm`, `team`, `implement-team`, and `qa-team` remain hidden machine lanes, not public skills.
- The nested public skills exist to make the `v1.3.8` host-visible surface prompt-triggerable.
- `beacon-change` is a host skill route, not a `beacon change` CLI subcommand. The CLI change-loop entry remains `beacon reopen ...`.
