# Beacon v1.2.0 Source Architecture Index

This source-architecture surface exists so the shipped v1.2.0 release line can point to the code it reshaped.

## Command surfaces

- `beacon/commands/skill.py` — adapter registry / bind / doctor entrypoint plus landed `skill discover` host surface
- `beacon/commands/help.py` — stage-aware next-step router that can recommend discovery when project binding is missing
- `beacon/commands/profile.py` — project profile create/show surface plus discovery-result inspection
- `beacon/commands/doctor.py` — material/package verification surface that should validate discovery-produced artifacts
- `beacon/commands/test_case.py` — current generator for AC matrix / QA9 matrix / story-scenario-map machine artifacts
- `beacon/commands/freeze.py` — frozen revision baseline command for the requirement package

## Shared kernel modules

- `beacon/utils/project_skills.py` — existing registry/profile/orchestration/evidence-gate kernel
- `beacon/utils/help_support.py` — profile-aware routing logic and blocking-reason computation
- `beacon/utils/implement_adapters.py` — current adapter discovery / default-runner detection
- `beacon/utils/story_state.py` — machine user-story state and frozen revision story baseline
- `beacon/utils/revision_state.py` — revision freeze / reopen state
- `beacon/utils/material_audit.py` — package completeness / delivery audit logic
- `beacon/utils/artifact_paths.py` — version-aware machine artifact path resolution

## Landed v1.2.0 additions

These files are now part of the bounded v1.2.0 split:

- `beacon/utils/project_analyzer.py` — static project feature detection
- `beacon/utils/skill_templates.py` — starter-pack/template loading and merge rules
- `beacon/utils/skill_discovery.py` — recommendation scoring, explanation payloads, preview/apply contract

## Boundary note

Even when these additions land, project-private execution logic remains outside Beacon core.
The source architecture must keep Beacon on the governance/configuration side of the adapter boundary.

## Imported pressure points from architecture deep analysis

The architecture deep analysis also identifies follow-on hot spots that inform, but do not redefine, v1.2.0:

- `beacon/utils/prototype_utils.py` remains a large multi-responsibility module
- `beacon/utils/learning_loop.py` still mixes several learning-plane concerns
- `beacon/utils/help_support.py` carries a large amount of routing logic
- explicit agent orchestration / observability remains a future surface
- testing visibility should improve, but is not required to expand the v1.2.0 product center

These are architecture follow-ons, not blockers for the shipped v1.2.0 release line.
