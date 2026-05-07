# Beacon Skill Example

This example focuses on the **Beacon CLI v1.4.0 line** (verify with `beacon --version`) and its lightweight main workflow:

1. read the current version package
2. use the **`beacon` CLI** from any project root (`pip`-installed Beacon does not require vendoring `skills/beacon/scripts/`)
3. generate PRD, user story, and test case materials
4. run implementation planning
5. inspect workflow status / next stage

Read first:

- [`../../../docs/beacon/v1.4.0/SUMMARY.md`](../../../docs/beacon/v1.4.0/SUMMARY.md)
- [`../../../docs/beacon/v1.4.0/execution/index.md`](../../../docs/beacon/v1.4.0/execution/index.md)
- [`../../../docs/beacon/v1.4.0/execution/project-skill-qa-evolution-blueprint.md`](../../../docs/beacon/v1.4.0/execution/project-skill-qa-evolution-blueprint.md)

Related focused examples:

- [`release-readiness.md`](./release-readiness.md)
- [`implementation-with-omx.md`](./implementation-with-omx.md)

```bash
# 0) Check Beacon CLI version
beacon --version

# 1) Generate the main-chain artifacts
beacon prd create \
  "Beacon v1.4.0 release line" \
  --project . \
  --version v1.4.0
beacon user-story create \
  "Beacon v1.4.0 release line" \
  --project . \
  --version v1.4.0
beacon test-case create \
  "Beacon v1.4.0 release line" \
  --project . \
  --version v1.4.0

# 2) Optional safe bootstrap for the same closed-loop materials (hidden command)
beacon prd-bootstrap run \
  "Beacon v1.4.0 release line" \
  --desc "闭环 PRD / user-story / test-case 材料" \
  --project-root . \
  --version v1.4.0 \
  --dry-run \
  --json

# 3) Compile implementation plan before coding
beacon implement plan \
  "Beacon v1.4.0 release line" \
  --project . \
  --version v1.4.0 \
  --json

# 4) Inspect status / next stage
beacon status --board --project-root . --version v1.4.0
beacon help --project-root . --version v1.4.0 --feature "Beacon v1.4.0 release line" --json
```
