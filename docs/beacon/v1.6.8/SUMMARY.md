# Beacon v1.6.8 — Production Ops Hardening

## Scope

Program **`beacon-prod-ops-hardening-v168`**: production hotfix lane, release self-heal profiles,
longrun default, version fleet ops; engineering philosophy synced to v2/Loom.

Promotion: `docs/beacon/v1.6.7/research/beacon-v168-prod-ops-hardening-pln-review.md`

## Public entry

- `$beacon-goal` / `beacon goal run` only
- Hotfix: `beacon goal run "…" --mode hotfix --from-version <tag>`
- Longrun: project `goal.longrun_default` (default true for new projects)

## Lakes (Wave order)

| Wave | Lake | Role |
|------|------|------|
| 0 | beacon-version-fleet-ops-v168 | version fleet + dual-version productization |
| 1 | beacon-release-profile-selfheal-v168 | full/hotfix profile + evidence repair |
| 2 | beacon-hotfix-lane-v168 | hotfix mode + forward-port + rollback |
| 3 | beacon-goal-longrun-default-v168 | longrun default + auto driver |
| 4 | beacon-v168-goalrun-axis-mount | main axis mount |
| 4 | beacon-v2-loom-ops-philosophy-sync | v2/Loom parity contracts |

## Status

- **truth**: frozen R1 (all lakes)
- **implement**: in progress
- **release**: pending human after QA

## Philosophy (shared with Loom)

1. One GoalRun; hotfix/longrun are modes/profiles
2. Production baseline sacred; forward-port required
3. Gates repairable; no fake green
4. Durable by default; opt-out explicit
5. Beacon prod + Loom evolve in parallel; no default replace
