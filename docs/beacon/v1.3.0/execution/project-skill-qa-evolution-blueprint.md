# Beacon v1.3.0 Project Skill / QA Evolution Blueprint

## Goal

Keep project adaptation and QA evolution aligned with the `v1.3.0` implement-first subagent line:

```text
project binding
→ requirement package
→ implement-team evidence
→ qa-team isolation
→ review / gate / release
```

This blueprint exists so `v1.3.0` does not overfit to implement-team only and forget how project skill binding and QA evidence still enter the same mainline.

---

## 1. Project-skill boundary in v1.3.0

`beacon skill discover` remains a bounded onboarding surface.

It still follows:

```text
detect
→ recommend
→ preview
→ apply
```

`v1.3.0` does not replace this with subagents.
Instead, the project-skill layer should determine whether the target project is ready to use:

- `implement-team`
- `qa-team`
- bounded delegated evidence paths

without moving project-private execution logic into Beacon core.

## 2. QA evolution boundary in v1.3.0

QA evolution also stays bounded.

Allowed:

- generate AC/TC/scenario baselines
- materialize `ac-test-matrix` / `story-scenario-map` / `qa9-matrix`
- compute rerun plans
- record repair handoff and human audit truth

Not allowed:

- inherit implement private context directly
- override release verdict by raw worker transcript
- skip machine-readable coverage artifacts

## 3. Shared operator contract

The recommended operator path is:

```text
skill discover / profile binding
→ requirement freeze
→ implement plan / implement team-run
→ qa team-plan / qa team-run
→ review / gate
```

`help` and `doctor` should keep recommending this same route rather than inventing a second delegated workflow tree.

## 4. Artifact contract

### Human docs

- `docs/beacon/v1.3.0/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.3.0/execution/codex-native-subagent-implementation-blueprint.md`
- `docs/beacon/v1.3.0/execution/version-semantics-contract.md`
- `docs/beacon/v1.3.0/execution/artifact-language-contract.md`

### Machine/runtime artifacts

- `.beacon/state/skill-discovery/...`
- `docs/beacon/v1.3.0/.machine/user-story/...`
- `docs/beacon/v1.3.0/.machine/qa/*.ac-test-matrix.json`
- `docs/beacon/v1.3.0/.machine/qa/*.story-scenario-map.json`
- `docs/beacon/v1.3.0/.machine/qa/*.qa9-matrix.json`
- `.beacon/handoffs/implement-to-qa/...`

## 5. Source touchpoints

- `beacon/commands/skill.py`
- `beacon/utils/project_skills.py`
- `beacon/commands/help.py`
- `beacon/utils/help_support.py`
- `beacon/commands/qa.py`
- `beacon/utils/team_surface.py`
- `beacon/utils/implementation_plan.py`
- `beacon/utils/versioning.py`

## 6. Freeze criteria for this workstream

This workstream is package-complete when:

1. project-skill discovery remains preview-first and bounded
2. implement-team and qa-team are linked to the same package evidence model
3. machine QA matrices exist for the frozen `v1.3.0` feature line
4. help/review/gate can read the resulting package without semantic drift

## 7. Boundary note

`v1.3.0` may validate delegated implement/qa evidence, but it still must not become a generic project analyzer or a generic autonomous QA platform.
