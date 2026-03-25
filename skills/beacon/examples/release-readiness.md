# Beacon Skill Example: Release Readiness

This example focuses on **verification and release evidence** for Beacon v1.1.6.

Read first:

- [`../../../docs/beacon/v1.1.6/COMMANDS.md`](../../../docs/beacon/v1.1.6/COMMANDS.md)
- [`../../../docs/beacon/v1.1.6/execution/scenario-quick-reference.md`](../../../docs/beacon/v1.1.6/execution/scenario-quick-reference.md)

```bash
# 1) Inspect current package state
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.1.6

# 2) Verify materials and delivery
bash skills/beacon/scripts/run_beacon.sh doctor verify-materials \
  --project-root . \
  --version v1.1.6 \
  --json
bash skills/beacon/scripts/run_beacon.sh doctor verify-delivery \
  --project-root . \
  --version v1.1.6 \
  --json

# 3) Repair old package layout if needed
bash skills/beacon/scripts/run_beacon.sh doctor repair-package \
  --project-root . \
  --version v1.1.6 \
  --json

# 4) Run release gate and release readiness checks
bash skills/beacon/scripts/run_beacon.sh gate check release \
  --project-root . \
  --version v1.1.6 \
  --json
bash skills/beacon/scripts/run_beacon.sh release check v1.1.6 --project .

# 5) Optional: generate acceptance audit artifacts
bash skills/beacon/scripts/run_beacon.sh report latest acceptance-audit \
  --project-root . \
  --version v1.1.6 \
  --feature beacon-human-machine-artifact-layering \
  --write
```
