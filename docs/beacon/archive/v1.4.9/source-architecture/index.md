# Beacon v1.4.9 Source Architecture

## Scope

本版本 source architecture 描述三条正式子线的结构边界：

- `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`
- `read-only-support-research-write-topology-gate-contract`

## Source Modules Under Review

- `beacon/commands/prototype.py`
- `beacon/utils/prototype_utils.py`
- `beacon/utils/prototype_support.py`
- `beacon/utils/design_review_surface.py`
- `beacon/utils/diagram_truth.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/cli_factory.py`
- `beacon/command_catalog.py`
- `skills/beacon/beacon-prototype/SKILL.md`
- `skills/beacon/beacon-design-review/SKILL.md`
- `/Users/apple/Developer/Personal/products/justin-mc-lai-skills/skills/ui-ux-dev/SKILL.md`
- `beacon/utils/brainstorm.py`
- `beacon/utils/support_surface_transactions.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/design_review_surface.py`
- `beacon/utils/deep_loop.py`
- `beacon/utils/learn_surface.py`
- `beacon/utils/material_gate_contract.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/utils/material_audit.py`
- `beacon/commands/gate.py`

## Architecture Position

Beacon v1.4.9 不新增 UI/UX execution engine。

目标架构是：

```text
ui-ux-dev
-> UI/UX execution output
-> Beacon design-result adapter
-> PRD / user-story / test-case truth bindings
-> requirement clarity
-> freeze / implement
```

## Gate Boundary

- Missing adapter truth bindings must block implementation.
- Missing version visualization truth bindings must block requirement clarity when visualization is required.
- Historical prototype bundles remain readable but cannot define new v1.4.9 UI/UX execution ownership.
- Explicit version+feature read-only support output must pass the support topology pre-write gate before persistence.
- Ordinary support reviews must upsert `research/<feature>.md`; `beacon-deep` writes detailed artifacts to `deep/<feature>/`; `beacon-learn` writes to `learning/<feature>.md` or transaction.
- `docs/brainstorms/` is not a fallback for governed Beacon feature research writes.
