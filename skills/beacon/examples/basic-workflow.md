# Beacon Skill Example

This example focuses on the **basic workflow path** in v1.1.7:

1. start from the command docs hub
2. use the wrapper script
3. start a workflow
4. generate the core workflow artifacts
5. inspect status / next stage

Read first:

- [`../../../docs/beacon/v1.1.7/COMMANDS.md`](../../../docs/beacon/v1.1.7/COMMANDS.md)
- [`../../../docs/beacon/v1.1.7/getting-started-10-minutes.md`](../../../docs/beacon/v1.1.7/getting-started-10-minutes.md)

Related focused examples:

- [`release-readiness.md`](./release-readiness.md)
- [`implementation-with-omx.md`](./implementation-with-omx.md)

```bash
# 0) Check Beacon version through the skill wrapper
bash skills/beacon/scripts/run_beacon.sh --version

# 1) Natural-language planning
bash skills/beacon/scripts/run_beacon.sh ask \
  "Create a release-ready requirement package for Beacon v1.1.7 layered delivery" \
  --project-root . \
  --version v1.1.7 \
  --plan-only --json

# 2) Start the workflow
bash skills/beacon/scripts/run_beacon.sh workflow start \
  "Beacon v1.1.7 layered delivery" \
  --project . \
  --version v1.1.7

# 3) Generate the main-chain artifacts
bash skills/beacon/scripts/run_beacon.sh think start \
  "Beacon v1.1.7 layered delivery" \
  --project . \
  --version v1.1.7
bash skills/beacon/scripts/run_beacon.sh user-story create \
  "Beacon v1.1.7 layered delivery" \
  --project . \
  --version v1.1.7
bash skills/beacon/scripts/run_beacon.sh prd create \
  "Beacon v1.1.7 layered delivery" \
  --project . \
  --version v1.1.7
bash skills/beacon/scripts/run_beacon.sh test-case create \
  "Beacon v1.1.7 layered delivery" \
  --project . \
  --version v1.1.7

# 4) Inspect status / next stage
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.1.7
bash skills/beacon/scripts/run_beacon.sh workflow status --project . --version v1.1.7
```
