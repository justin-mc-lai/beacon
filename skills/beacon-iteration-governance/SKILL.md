---
name: beacon-iteration-governance
description: Use when iterating Beacon itself and you need a fixed source-iteration to docs-convergence to release-verification workflow that keeps README, current release docs, skill surfaces, and release checks aligned.
metadata:
  author: Beacon CLI
  version: "1.3.6"
  organization: Beacon
  date: April 2026
  abstract: Repository-local governance skill for Beacon runtime promotion, documentation convergence, and release-readiness verification.
---

# Beacon Iteration Governance

## Overview

This skill is for developing Beacon itself.

It standardizes one loop:

`source changes -> current docs convergence -> delivery audit -> release verification`

Use it when a Beacon feature changes code, current-version docs, README, skill surfaces, or release evidence.

## When to Use

Use this skill when:

- Beacon source behavior changed and docs must converge before close-out
- README current sections might drift from the active release line
- you need to run current-contract, material, delivery, and release checks as one governed loop
- you want Beacon project profiles to call a repository-local governance script through `beacon skill` / `beacon verify` / `beacon orchestrate`

## Workflow

1. Confirm the active release line from `beacon/__init__.py`, `pyproject.toml`, and `docs/beacon/<version>/`.
2. Make the smallest implementation change.
3. Converge current-version docs:
- `README.md` current sections
- `SKILL.md`
- `skills/beacon/`
- `docs/beacon/<current>/`
4. Run the governance script:
- `quick` for docs + current-contract alignment
- `delivery` for delivery/release checks
- `full` for both
5. If Beacon is being driven through a project profile, bind the feature and run `beacon verify run ...` or `beacon orchestrate run ...`.

## Script Entry

```bash
bash skills/beacon-iteration-governance/scripts/run_iteration_governance.sh --help
bash skills/beacon-iteration-governance/scripts/run_iteration_governance.sh quick --project-root . --version v1.3.6
bash skills/beacon-iteration-governance/scripts/run_iteration_governance.sh delivery --project-root . --version v1.3.6
bash skills/beacon-iteration-governance/scripts/run_iteration_governance.sh full --project-root . --version v1.3.6
```

The script writes logs and a summary under:

`<project-root>/.beacon/iteration-governance/`

## Beacon Skill Integration

Use this skill through Beacon project skills when you want Beacon to own the loop:

1. Register the external skill in `project_skills.registry`.
2. Create a profile that uses it for `verify` and optional `delivery`.
3. Bind the feature with `beacon skill bind`.
4. Run:

```bash
beacon skill registry list --project-root <temp-or-project-root> --json
beacon skill bind "Beacon Iteration Governance" --profile beacon-iter-dev --project-root <root> --version v1.3.6
beacon verify run "Beacon Iteration Governance" --project-root <root> --version v1.3.6 --param repo_root=/abs/path/to/beacon --json
beacon orchestrate run "Beacon Iteration Governance" --project-root <root> --version v1.3.6 --stage delivery --param repo_root=/abs/path/to/beacon --dry-run --json
```

See the profile example in [examples/profile-integration.md](./examples/profile-integration.md).

## References

- [Governance workflow](./references/workflow.md)
- [Profile integration example](./examples/profile-integration.md)
- [Beacon v1.3.6 Summary](../../docs/beacon/v1.3.6/SUMMARY.md)
- [Beacon v1.3.6 Execution Index](../../docs/beacon/v1.3.6/execution/index.md)
- [Beacon v1.3.6 Release Notes](../../docs/beacon/v1.3.6/release/v1.3.6.md)
