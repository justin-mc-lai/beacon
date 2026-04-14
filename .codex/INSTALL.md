# Installing Beacon Host Skills for Codex

Enable Beacon's `v1.3.1` minimal human surface in Codex through native skill discovery.

## Installed skill root

Beacon's install root stays:

- `skills/beacon/`

This preserves the existing root `SKILL.md` and packaged metadata while adding nested host-visible subskills underneath the same root.

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
```

## Notes

- For Codex, `~/.agents/skills/beacon` is the canonical install root.
- Do not also install the same Beacon pack under `~/.codex/skills/beacon`; that creates duplicate skill discovery and repeated public skill entries like `beacon-doctor`.
- `brainstorm`, `team`, `implement-team`, and `qa-team` should remain hidden machine lanes, not public host-visible skills.
- The nested public skills exist to make the `v1.3.1` 6+3 human surface prompt-triggerable, not to mirror Beacon's full CLI catalog.
