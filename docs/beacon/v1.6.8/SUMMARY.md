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

- **truth**: frozen R1 (all 6 lakes)
- **implement**: landed on main (`e3d63efe` / merge `844739e4`)
- **QA**: all 6 lakes `beacon qa run` → **passed** / `release_ready=true` (2026-07-19)
- **release check**: `beacon release check v1.6.8` → **pass** / `release_ready=true`
- **human GO**: **GO / SHIPPED** — current_runtime_release_line=v1.6.8, global install done


## Philosophy (shared with Loom)

1. One GoalRun; hotfix/longrun are modes/profiles
2. Production baseline sacred; forward-port required
3. Gates repairable; no fake green
4. Durable by default; opt-out explicit
5. Beacon prod + Loom evolve in parallel; no default replace


## Program (hotfix follow-up): `beacon-friction-closeout-v168`

Friction closeout on the same GoalRun spine (2026-07-19 GO):

| Wave | Lake | Role |
|------|------|------|
| 0 | beacon-runtime-install-truth-v168 | install / version truth diagnose + pin |
| 1 | beacon-longrun-contract-align-v168 | longrun_default contract = code |
| 2 | beacon-release-profile-wiring-v168 | ReleaseProfile drives release check |
| 3 | beacon-fsm-implement-order-v168 | entity precedence gates implement |

- **graph**: `docs/beacon/v1.6.8/programs/beacon-friction-closeout-v168/feature-graph.json`
- **axis**: `docs/beacon/v1.6.8/programs/beacon-friction-closeout-v168/goalrun-main-axis.md`
- **status**: truth frozen R1; implement pending

