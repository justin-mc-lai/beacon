# Installing Beacon Host Skills for Codex

Enable Beacon's `v1.3.3` minimal human surface in Codex through native skill discovery.

## Installed skill root

Beacon's canonical install root is:

- `~/.agents/skills/beacon` -> `/absolute/path/to/beacon/skills/beacon`

Do not also install Beacon under `~/.codex/skills/beacon`. That creates duplicate discovery and can make Codex restart back onto a stale Beacon root.

## Public host-visible skills

- umbrella:
  - `beacon`
  - `using-beacon`
- primary:
  - `beacon-prd`
  - `beacon-user-story`
  - `beacon-test-case`
  - `beacon-implement`
  - `beacon-qa`
  - `beacon-release`
- support:
  - `beacon-help`
  - `beacon-status`
  - `beacon-doctor`

## Optional supplemental skills

- `beacon-toolkit-lighthouse`
- `beacon-prd-bootstrap`
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

## Verify

```bash
find ~/.agents/skills/beacon -maxdepth 2 -name SKILL.md | sort
python3 scripts/check_skill_drift.py --project-root . --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.3 --json
```

## HUD hook recovery

Use the doctor-managed hook instead of ad hoc config edits:

```bash
beacon doctor setup-codex-hud-hook --project-root . --version v1.3.3 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.3 --json
```

## Notes

- `~/.agents/skills/beacon` is the canonical install root.
- `brainstorm`, `team`, `implement-team`, and `qa-team` remain hidden machine lanes, not public skills.
- The nested public skills exist to make the `v1.3.3` 6+3 human surface prompt-triggerable.
