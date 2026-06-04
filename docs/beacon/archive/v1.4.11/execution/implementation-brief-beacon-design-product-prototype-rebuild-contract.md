# Implementation Brief: beacon-design-product-prototype-rebuild-contract

## Status

- Version: `v1.4.11`
- Feature: `beacon-design-product-prototype-rebuild-contract`
- Implementation status: complete
- Scope: design support surface, design truth contract, prototype adapter boundary, design subskill admission

## Implemented Changes

This implementation rebuilds Beacon design/prototype capability around a support-only design contract.

- Added deterministic design contract utilities in `beacon/utils/design_contract.py`.
- Exposed `beacon design` as a visible support command in `beacon/cli_factory.py`.
- Moved `design` from labs to support command catalog classification in `beacon/command_catalog.py`.
- Reworked `beacon/commands/design.py` to support:
  - `design contract`
  - `design truth`
  - `design route`
  - `design plan`
  - `design bootstrap`
  - legacy `design create/list` compatibility.
- Added Beacon design child skill documents:
  - `skills/beacon/beacon-design/SKILL.md`
  - `.agents/skills/beacon-design/SKILL.md`
- Updated prototype status handling in `beacon/commands/prototype.py`:
  - default current status remains `design-result-adapter`
  - legacy wireframe/prototype details require explicit `--include-legacy`
  - legacy evidence is marked as migration input, not current closure.
- Added focused validation in `tests/test_v1411_beacon_design_product_prototype_rebuild.py`.

## Preserved Upstream Capability Routes

Beacon design now has explicit support-only routes for the upstream capabilities distilled from `ui-ux-dev`:

| Beacon route | Upstream capability | Boundary |
| --- | --- | --- |
| `explore` | `vibe-to-ui` | execution-capable support |
| `extract` | `vibe-to-ui` | execution-capable support |
| `system` | `ui-ux-pro-max` | execution-capable support |
| `review` | `impeccable` | execution-capable support |
| `polish` | `impeccable` | execution-capable support |
| `library` | `awesome-design-md` | reference-only |
| `bootstrap` | upstream compatibility checks | capability admission only |

## Truth Boundary

The implementation keeps design as a support surface only.

- `PRODUCT.md` and `DESIGN.md` are project-level truth candidates.
- `docs/beacon/<version>/design/style.md`, `component-system.md`, `interaction-contract.md`, and `state-matrix.md` are version-wide design truth surfaces.
- `docs/beacon/<version>/.machine/design` remains projection-only.
- Accepted UI/UX facts that change truth must route through `beacon-change-refreeze`.
- `beacon-design` does not become a gate source, release verdict source, or lifecycle stage.

## Verification

Focused feature validation:

```bash
rtk python3 -m pytest -q tests/test_v1411_beacon_design_product_prototype_rebuild.py
```

Result observed during implementation:

```text
21 passed
```

Related design/prototype regression was also checked. Existing unrelated failures remain in `tests/test_skill_standard_layout.py` because older root skill examples still reference previous Beacon version paths.
