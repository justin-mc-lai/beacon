# Source Architecture Index v1.6.0

## Feature

- `beacon-skill-harness-taxonomy-v160`

## Source Surfaces

- `skills/beacon/**/SKILL.md`
- `.agents/skills/**/SKILL.md`
- `beacon/command_catalog.py`
- `beacon/cli_factory.py`
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/`
- `docs/beacon/v1.6.0/execution/project-skill-qa-evolution-blueprint.md`

## Architectural Constraint

The v1.6.0 skill migration is a host-visible taxonomy change. It must preserve package-authoritative truth while replacing old skill names with harness-prefixed names.

## Implementation Notes

Implementation must update source, packaged skills, project-local agent surfaces, command docs, and tests together. Generated docs should be preferred for shared preamble propagation to avoid drift.
