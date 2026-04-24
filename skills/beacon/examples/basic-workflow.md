# Beacon Skill Example

This example focuses on the **Beacon v1.3.7 release line** and its lightweight main workflow:

1. read the current version package
2. use the wrapper script
3. generate PRD, user story, and test case materials
4. run implementation planning
5. inspect workflow status / next stage

Read first:

- [`../../../docs/beacon/v1.3.7/SUMMARY.md`](../../../docs/beacon/v1.3.7/SUMMARY.md)
- [`../../../docs/beacon/v1.3.7/execution/index.md`](../../../docs/beacon/v1.3.7/execution/index.md)
- [`../../../docs/beacon/v1.3.7/execution/project-skill-qa-evolution-blueprint.md`](../../../docs/beacon/v1.3.7/execution/project-skill-qa-evolution-blueprint.md)

Related focused examples:

- [`release-readiness.md`](./release-readiness.md)
- [`implementation-with-omx.md`](./implementation-with-omx.md)

```bash
# 0) Check Beacon version through the skill wrapper
bash skills/beacon/scripts/run_beacon.sh --version

# 1) Generate the main-chain artifacts
bash skills/beacon/scripts/run_beacon.sh prd create \
  "Beacon v1.3.7 runtime release line" \
  --project . \
  --version v1.3.7
bash skills/beacon/scripts/run_beacon.sh user-story create \
  "Beacon v1.3.7 runtime release line" \
  --project . \
  --version v1.3.7
bash skills/beacon/scripts/run_beacon.sh test-case create \
  "Beacon v1.3.7 runtime release line" \
  --project . \
  --version v1.3.7

# 2) Optional safe bootstrap for the same closed-loop materials
bash skills/beacon/scripts/run_beacon.sh prd bootstrap \
  "Beacon v1.3.7 runtime release line" \
  --project-root . \
  --version v1.3.7 \
  --dry-run \
  --json

# 3) Compile implementation plan before coding
bash skills/beacon/scripts/run_beacon.sh implement plan \
  "Beacon v1.3.7 runtime release line" \
  --project . \
  --version v1.3.7 \
  --json

# 4) Inspect status / next stage
bash skills/beacon/scripts/run_beacon.sh status --board --project-root . --version v1.3.7
bash skills/beacon/scripts/run_beacon.sh help --project-root . --version v1.3.7 --feature "Beacon v1.3.7 runtime release line" --json
```
