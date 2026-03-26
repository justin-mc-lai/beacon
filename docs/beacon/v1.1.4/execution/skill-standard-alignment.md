# Beacon Skill Standard Alignment (v1.1.4)

## Problem statement

Before this alignment pass, Beacon had:

- a root-level `SKILL.md`
- a root-level `scripts/sync_skill_commands.py`
- no populated `skills/beacon/` package

That meant Beacon was *usable* as a skill, but it did **not** visibly satisfy the standard `skills/<name>/SKILL.md + references/ + scripts/` layout described in:

- `docs/skill-development-standards.md`

## Root cause

Beacon historically optimized for:

1. CLI-first execution
2. installed-skill compatibility (`~/.agents`, `~/.codex`, `~/.claude`)
3. root-level diagnostics that read `SKILL.md`

So the implementation path became:

- root `SKILL.md` first
- standard `skills/beacon/` package later

## v1.1.4 alignment decision

Beacon now adopts a two-layer model:

### Layer A — canonical standard skill package

- `skills/beacon/SKILL.md`
- `skills/beacon/references/`
- `skills/beacon/scripts/`
- `skills/beacon/examples/`
- `skills/beacon/metadata.json`

### Layer B — compatibility entry

- root `SKILL.md`

## Why not replace root SKILL.md immediately

Because current Beacon runtime/diagnostics/tests still rely on it:

- version consistency checks
- installed-skill copy drift checks
- command table sync checks
- current repo compatibility expectations

Therefore v1.1.4 uses:

- `skills/beacon/` as standard package
- root `SKILL.md` as compatibility mirror

## Script trigger model

To satisfy “skills + scripts” entry expectations, Beacon adds:

- `skills/beacon/scripts/run_beacon.sh`

This wrapper delegates to:

```bash
python3 -m beacon.main "$@"
```

So Beacon remains CLI-native, but is now also packaged as a standard script-backed skill.

## Acceptance outcome

This alignment is considered complete for v1.1.4 when:

1. the standard skill package exists
2. the wrapper script can invoke Beacon
3. root compatibility remains intact
4. docs/release materials explicitly describe the transition
