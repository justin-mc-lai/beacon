# Beacon Skill Example: Compatibility Implementation

This example shows how `v1.3.8` treats external runners such as OMX: useful for compatibility, but not part of the default human main path.

Read first:

- [`../../../docs/beacon/v1.3.8/SUMMARY.md`](../../../docs/beacon/v1.3.8/SUMMARY.md)
- [`../../../docs/beacon/v1.3.8/execution/project-skill-qa-evolution-blueprint.md`](../../../docs/beacon/v1.3.8/execution/project-skill-qa-evolution-blueprint.md)
- [`../../../docs/beacon/v1.3.8/execution/boundaries.md`](../../../docs/beacon/v1.3.8/execution/boundaries.md)

```bash
# 1) Inspect optional adapters and preferred runner
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh skill detect --project-root . --json
# skill prefer omx only when compatibility is explicit
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json

# 2) Keep default implementation host-native unless compatibility is explicit
bash skills/beacon/scripts/run_beacon.sh implement plan \
  "Beacon v1.3.8 runtime release line" \
  --project . \
  --version v1.3.8 \
  --json

# 3) Explicit compatibility-plane runner usage
bash skills/beacon/scripts/run_beacon.sh implement run \
  "Beacon v1.3.8 runtime release line" \
  --project . \
  --version v1.3.8 \
  --runner omx \
  --dry-run \
  --json

# 4) Inspect implementation status / plan progress
# review spec before escalating to compatibility-plane execution
bash skills/beacon/scripts/run_beacon.sh implement status \
  "Beacon v1.3.8 runtime release line" \
  --project-root . \
  --version v1.3.8

# 5) After implementation, run QA and release checks through Beacon core
bash skills/beacon/scripts/run_beacon.sh qa run \
  "Beacon v1.3.8 runtime release line" \
  --project . \
  --version v1.3.8 \
  --json
bash skills/beacon/scripts/run_beacon.sh gate check release \
  --project-root . \
  --version v1.3.8 \
  --json
```
