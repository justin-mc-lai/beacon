# Change: ui-ux-externalization-prototype-adapter-and-version-visualization-contract

**Version**: `v1.4.9`
**Status**: `frozen`
**Generated**: `2026-05-21`

## Why This Change Exists

Beacon 已经具备较重的 internal `prototype` 和 design 相关能力，但这些能力与 `ui-ux-dev` 的独立 UI/UX intent router 重叠，而且并不是 Beacon 的核心价值。

该 change 的目的，是把 vNext 头暴收敛正式冻结为 v1.4.9 requirement package：

- UI/UX execution 统一外部化到 `ui-ux-dev`
- Beacon `prototype` 降级为 design-result adapter
- `beacon-design-review` 降级为 route / governance support
- 版本级 business flow / state-machine / three-piece map 投影进入冻结契约
- 每个投影必须具备 truth bindings

## Delta

- Remove Beacon ownership of UI/UX execution from the future contract.
- Add `ui-ux-dev` as the required UI/UX execution route.
- Redefine `prototype` as adapter, not design generator.
- Redefine `design-review` as route / governance support.
- Add version-level business flow projection.
- Add version-level state-machine projection.
- Add version-level PRD / user-story / test-case map.
- Add truth binding requirement for every projection.
- Add compatibility boundary for historical prototype bundles.

## Freeze Intent

本次冻结只冻结 requirement truth。

本次不直接执行：

- code removal
- implementation
- QA
- release
- runtime promotion

## Traceability

- `docs/beacon/archive/v1.4.9/research/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- `docs/beacon/archive/v1.4.9/source-architecture/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- `docs/beacon/archive/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- `docs/beacon/archive/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
- `docs/beacon/archive/v1.4.9/qa/test-cases/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
