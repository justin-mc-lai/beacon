# Installing Beacon Host Skills for Codex

Enable Beacon's Scheme A **1+6 public surface** in Codex through native skill discovery.

## Installed skill root (Scheme A)

Beacon source of truth remains the packaged tree:

- `/absolute/path/to/beacon/skills/beacon/{beacon-goal,...}`

Codex discovery root uses **flat first-level links only**:

- `~/.agents/skills/beacon-goal` → `…/skills/beacon/beacon-goal`
- `~/.agents/skills/beacon-plan`
- `~/.agents/skills/beacon-truth`
- `~/.agents/skills/beacon-design`
- `~/.agents/skills/beacon-implement`
- `~/.agents/skills/beacon-qa`
- `~/.agents/skills/beacon-release`

And Loom dual-track (same shape):

- `~/.agents/skills/loom-{goal,plan,truth,design,implement,qa,release}`

### Do **not** install package roots

These paths recursively re-expose progressive/internal skills (`beacon-gov-*`, `beacon-pln-*`, …) into the Codex skill index:

- `~/.agents/skills/beacon` → full `skills/beacon` tree ❌
- `~/.agents/skills/loom` → full `skills/loom` tree ❌
- `~/.codex/skills/beacon` ❌
- backup symlinks such as `~/.codex/skills/beacon.bak-*` ❌

## Public host-visible skills (1+6)

| Public skill | Role |
|---|---|
| `beacon-goal` | Long-run transversal entry |
| `beacon-plan` | Plan harness (progressive: review/brainstorm/…) |
| `beacon-truth` | Truth freeze harness |
| `beacon-design` | Design harness |
| `beacon-implement` | Implement harness |
| `beacon-qa` | QA harness |
| `beacon-release` | Release harness |

Progressive/internal skills under `skills/beacon/beacon-{gov,pln,gen,eval}-*` remain in-repo for harness progressive load — they are **not** host-visible.

## Installation

Recommended (Python helper, dual-track):

```bash
python3 -c "from beacon.utils.agent_surface import install_global_agents_beacon_skills, verify_global_agents_beacon_skills; print(install_global_agents_beacon_skills(beacon_root='.')); print(verify_global_agents_beacon_skills())"
```

Or shell installer:

```bash
bash scripts/beacon-install.sh agents
bash scripts/install-loom-skills.sh agents
```

Unified:

```bash
bash scripts/install_all_agents.sh
```

Legacy full surface (not recommended for daily use):

```bash
INSTALL_ALL=1 bash scripts/beacon-install.sh agents
```

## Cleanup before reinstall

```bash
rm -rf ~/.codex/skills/beacon
rm -f ~/.codex/skills/beacon.bak-*
rm -f ~/.agents/skills/beacon ~/.agents/skills/loom
# then reinstall flat 1+6
bash scripts/beacon-install.sh agents
bash scripts/install-loom-skills.sh agents
```

## Verify

```bash
beacon --version
find ~/.agents/skills -maxdepth 1 \( -name 'beacon*' -o -name 'loom*' \) | sort
# package roots must be absent
test ! -e ~/.agents/skills/beacon
test ! -e ~/.agents/skills/loom
# exactly 7 beacon + 7 loom flat skills
find ~/.agents/skills -maxdepth 1 -name 'beacon-*' | wc -l   # 7
find ~/.agents/skills -maxdepth 1 -name 'loom-*' | wc -l     # 7
```

## Notes

- Progressive loads (gov/pln/gen/eval) are internal to harness shells — users only call `$beacon-goal` / `$beacon-plan` / …
- Restart Codex after reinstall so the skill index rebuilds.
