# Beacon Skill Example: Release Readiness

This example focuses on **verification and release evidence** for Beacon v1.1.12.

Read first:

- [`../../../docs/beacon/v1.1.12/SUMMARY.md`](../../../docs/beacon/v1.1.12/SUMMARY.md)
- [`../../../docs/beacon/v1.1.12/execution/index.md`](../../../docs/beacon/v1.1.12/execution/index.md)

```bash
# 1) Inspect current package state
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.1.12

# 2) Verify materials and delivery
bash skills/beacon/scripts/run_beacon.sh doctor verify-materials \
  --project-root . \
  --version v1.1.12 \
  --json
bash skills/beacon/scripts/run_beacon.sh doctor verify-delivery \
  --project-root . \
  --version v1.1.12 \
  --json

# 3) Repair old package layout if needed
bash skills/beacon/scripts/run_beacon.sh doctor repair-package \
  --project-root . \
  --version v1.1.12 \
  --json
bash skills/beacon/scripts/run_beacon.sh doctor upgrade-package \
  --project-root . \
  --version v1.1.12 \
  --json

# 4) Ensure current feature has an implementation plan before release gate
bash skills/beacon/scripts/run_beacon.sh implement plan \
  "Beacon v1.1.12 release line" \
  --project . \
  --version v1.1.12 \
  --json

# 5) Run release gate and release readiness checks
bash skills/beacon/scripts/run_beacon.sh gate check release \
  --project-root . \
  --version v1.1.12 \
  --json
bash skills/beacon/scripts/run_beacon.sh release check v1.1.12 --project .

# 6) Optional: generate acceptance audit artifacts
bash skills/beacon/scripts/run_beacon.sh report latest acceptance-audit \
  --project-root . \
  --version v1.1.12 \
  --feature beacon-prd-us-to-plan-implementation-progress-closure \
  --write
```
