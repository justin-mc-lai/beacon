# Beacon Skill Example: Release Readiness

This example focuses on **v1.3.3 release evidence and gate consistency**.

Read first:

- [`../../../docs/beacon/v1.3.3/SUMMARY.md`](../../../docs/beacon/v1.3.3/SUMMARY.md)
- [`../../../docs/beacon/v1.3.3/execution/index.md`](../../../docs/beacon/v1.3.3/execution/index.md)
- [`../../../docs/beacon/v1.3.3/release/v1.3.3.md`](../../../docs/beacon/v1.3.3/release/v1.3.3.md)

```bash
# 1) Inspect current package state
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.3.3

# 2) Verify context and sync machine materials after runtime upgrades
bash skills/beacon/scripts/run_beacon.sh doctor verify-context \
  --project-root . \
  --strict \
  --json
bash skills/beacon/scripts/run_beacon.sh doctor sync-materials \
  --project-root . \
  --version v1.3.3 \
  --all-features \
  --json

# 3) Ensure current feature has implementation-plan truth before release gate
bash skills/beacon/scripts/run_beacon.sh implement plan \
  "Beacon v1.3.3 lightweight release line" \
  --project . \
  --version v1.3.3 \
  --json

# 4) Run release gate and release readiness checks
bash skills/beacon/scripts/run_beacon.sh gate check release \
  --project-root . \
  --version v1.3.3 \
  --json
bash skills/beacon/scripts/run_beacon.sh release check v1.3.3 --project .

# 5) Confirm the fixed HUD hook can inject context into Codex
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续 Beacon v1.3.3 release"}' \
  | bash skills/beacon/scripts/run_beacon.sh debug codex-fixed-hud --project-root . --version v1.3.3 --json
```
