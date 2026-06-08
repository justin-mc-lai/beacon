# Architecture Blueprint v1.6.0

- status: planning
- project_mode: greenfield
- feature: `beacon-skill-harness-taxonomy-v160`

## Scope

- host-visible skill taxonomy
- shared skill preamble generation
- planner/generator/evaluator/governor hard gates
- old-to-new skill migration
- package-authoritative truth preservation

## Service Map

- `skills/beacon/`: packaged host-visible skills.
- `.agents/skills/`: project-local Codex agent skill surface.
- `beacon/command_catalog.py`: CLI command layer catalog.
- `beacon/cli_factory.py`: CLI registration surface.
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/`: authoritative requirement package.

## No-Expand Guardrails

- Do not reintroduce `prd`, `user-story`, or `test-case` as v1.6.0 primary skill categories.
- Do not keep old host-visible skill aliases in the v1.6.0 package.
- Do not allow support/planner surfaces to write implementation, frozen truth, QA verdicts, or release verdicts.
- Do not allow generator surfaces to claim completion without evaluator evidence.
