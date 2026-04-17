# Beacon Skill Example: Compatibility Implementation

This example shows how `v1.3.3` treats external runners such as OMX: useful for compatibility, but not part of the default human main path.

Read first:

- [`../../../docs/beacon/v1.3.3/SUMMARY.md`](../../../docs/beacon/v1.3.3/SUMMARY.md)
- [`../../../docs/beacon/v1.3.3/execution/project-skill-qa-evolution-blueprint.md`](../../../docs/beacon/v1.3.3/execution/project-skill-qa-evolution-blueprint.md)
- [`../../../docs/beacon/v1.3.3/execution/boundaries.md`](../../../docs/beacon/v1.3.3/execution/boundaries.md)

```bash
# 1) Inspect optional adapters and preferred runner
bash skills/beacon/scripts/run_beacon.sh skill list
bash skills/beacon/scripts/run_beacon.sh skill detect --project-root . --json
bash skills/beacon/scripts/run_beacon.sh implement list-runners --json

# 2) Keep default implementation host-native unless compatibility is explicit
bash skills/beacon/scripts/run_beacon.sh implement plan \
  "Beacon v1.3.3 lightweight release line" \
  --project . \
  --version v1.3.3 \
  --json

# 3) Explicit compatibility-plane runner usage
bash skills/beacon/scripts/run_beacon.sh implement run \
  "Beacon v1.3.3 lightweight release line" \
  --project . \
  --version v1.3.3 \
  --runner omx \
  --dry-run \
  --json

# 4) Inspect implementation status / plan progress
bash skills/beacon/scripts/run_beacon.sh implement status \
  "Beacon v1.3.3 lightweight release line" \
  --project-root . \
  --version v1.3.3

# 5) After implementation, run QA and release checks through Beacon core
bash skills/beacon/scripts/run_beacon.sh qa run \
  "Beacon v1.3.3 lightweight release line" \
  --project . \
  --version v1.3.3 \
  --json
bash skills/beacon/scripts/run_beacon.sh gate check release \
  --project-root . \
  --version v1.3.3 \
  --json
```
