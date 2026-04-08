# Beacon Skill Example: Implementation with OMX

This example focuses on **adapter-driven implementation** using the Beacon skill wrapper and OMX.

Read first:

- [`../../../docs/beacon/v1.2.0/SUMMARY.md`](../../../docs/beacon/v1.2.0/SUMMARY.md)
- [`../../../docs/beacon/v1.2.0/execution/index.md`](../../../docs/beacon/v1.2.0/execution/index.md)

```bash
# 1) Inspect skill adapters and preferred runner
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh skill detect --project-root . --json
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json

# 2) Optionally set OMX as the preferred runner for this project
bash skills/beacon/scripts/run_beacon.sh skill prefer omx --project-root . --scope project

# 3) Run implementation through OMX (dry-run first)
bash skills/beacon/scripts/run_beacon.sh implement plan \
  "Beacon v1.2.0 release line" \
  --project . \
  --version v1.2.0 \
  --json

# 4) Run implementation through OMX (dry-run first)
bash skills/beacon/scripts/run_beacon.sh implement run \
  "Beacon v1.2.0 release line" \
  --project . \
  --version v1.2.0 \
  --runner omx \
  --dry-run \
  --json

# 5) Inspect implementation status / plan progress
bash skills/beacon/scripts/run_beacon.sh implement status \
  "Beacon v1.2.0 release line" \
  --project-root . \
  --version v1.2.0

# 6) After implementation, run review and release checks
bash skills/beacon/scripts/run_beacon.sh review spec \
  "Beacon v1.2.0 release line" \
  --project . \
  --version v1.2.0 \
  --json
bash skills/beacon/scripts/run_beacon.sh review quality \
  "Beacon v1.2.0 release line" \
  --project . \
  --version v1.2.0 \
  --json
```
