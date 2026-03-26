# Beacon Skill Example: Implementation with OMX

This example focuses on **adapter-driven implementation** using the Beacon skill wrapper and OMX.

Read first:

- [`../../../docs/beacon/v1.1.8/SUMMARY.md`](../../../docs/beacon/v1.1.8/SUMMARY.md)
- [`../../../docs/beacon/v1.1.8/execution/index.md`](../../../docs/beacon/v1.1.8/execution/index.md)

```bash
# 1) Inspect skill adapters and preferred runner
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh skill detect --project-root . --json
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json

# 2) Optionally set OMX as the preferred runner for this project
bash skills/beacon/scripts/run_beacon.sh skill prefer omx --project-root . --scope project

# 3) Run implementation through OMX (dry-run first)
bash skills/beacon/scripts/run_beacon.sh implement run \
  "Beacon v1.1.8 release line" \
  --project . \
  --version v1.1.8 \
  --runner omx \
  --dry-run \
  --json

# 4) Inspect implementation status
bash skills/beacon/scripts/run_beacon.sh implement status \
  --project-root . \
  --version v1.1.8

# 5) After implementation, run review and release checks
bash skills/beacon/scripts/run_beacon.sh review spec \
  "Beacon v1.1.8 release line" \
  --project . \
  --version v1.1.8 \
  --json
bash skills/beacon/scripts/run_beacon.sh review quality \
  "Beacon v1.1.8 release line" \
  --project . \
  --version v1.1.8 \
  --json
```
