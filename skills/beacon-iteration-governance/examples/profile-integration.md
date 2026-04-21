# Profile Integration Example

Use this when you want Beacon to invoke the governance skill through `beacon verify` or `beacon orchestrate`.

```yaml
project_skills:
  registry:
    beacon-iteration-governance:
      id: beacon-iteration-governance
      kind: external
      entry: /abs/path/to/beacon/skills/beacon-iteration-governance/scripts/run_iteration_governance.sh
      capabilities:
        - verify
        - delivery
        - docs-governance
        - release-readiness
      supported_stages:
        - verify
        - delivery
      evidence_contract:
        - docs_current_contract
        - docs_material_audit
        - delivery_audit
        - release_readiness
  profiles:
    beacon-iter-dev:
      project: beacon
      profile_id: beacon-iter-dev
      description: Beacon source iteration with docs convergence and release verification.
      skills:
        verify: beacon-iteration-governance
        delivery: beacon-iteration-governance
      required_evidence:
        - docs_current_contract
        - docs_material_audit
      required_cases: []
      orchestration:
        nodes:
          -
            id: docs-contract
            stage: verify
            skill: beacon-iteration-governance
            command_template: "{skill_entry} quick --project-root {repo_root} --version {version}"
            produces_evidence:
              - docs_current_contract
              - docs_material_audit
          -
            id: delivery-audit
            stage: delivery
            skill: beacon-iteration-governance
            command_template: "{skill_entry} delivery --project-root {repo_root} --version {version}"
            produces_evidence:
              - delivery_audit
              - release_readiness
  default_profile: beacon-iter-dev
```

## Example Commands

```bash
beacon skill registry list --project-root <profile-root> --json
beacon skill bind "Beacon Iteration Governance" --profile beacon-iter-dev --project-root <profile-root> --version v1.3.6
beacon verify run "Beacon Iteration Governance" --project-root <profile-root> --version v1.3.6 --param repo_root=/abs/path/to/beacon --json
beacon orchestrate run "Beacon Iteration Governance" --project-root <profile-root> --version v1.3.6 --stage delivery --param repo_root=/abs/path/to/beacon --dry-run --json
```
