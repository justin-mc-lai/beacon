# Change: Version Aggregate Projection Guard Contract

**Feature**: `version-aggregate-projection-guard-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`  
**Date**: `2026-05-27`

## 1. Change Reason

`beacon-design-human-subskills-closure-contract` 完成 QA 后，版本 release check 曾因为版本聚合投影漏记 current feature 而 blocked。

这暴露出一个生命周期绑定缺口：QA acceptance、feature change projection、version aggregate projection、test-contract-index、release check 之间没有形成稳定的内部闭环。

本 change 接受 brainstorm 结论：不要新增 `aggregate-sync` 生命周期，而是把版本聚合投影守卫收回现有 QA / release / doctor surface。

## 2. Accepted Change

冻结一个 runtime / gate / projection feature：

```text
version-aggregate-projection-guard-contract
```

要求 Beacon：

1. 将 feature-level change projection 作为 QA accepted feature 的 release-facing 投影输入。
2. 将 version-level aggregate projection 作为 release create / release check 的确定性 read model。
3. 在 release check 中 fail-closed 校验 current QA accepted feature 已进入版本聚合。
4. 提供 doctor repair-only 路径重建 feature projection、version aggregate projection、test-contract-index。
5. 明确 aggregate projection 不是 truth source、不是 lifecycle stage、不是新的人工主流程。

## 3. Scope

### In Scope

- `beacon/commands/release.py`
- release scorecard / change document aggregation helpers
- QA acceptance writeback 后置 projection 校验或写回
- doctor repair-only projection rebuild / verify 路径
- test-contract-index refresh / verify 绑定
- regression tests for projection inclusion and fail-closed behavior
- docs wording that distinguishes truth from projection

### Out Of Scope

- No new lifecycle stage.
- No new required human-facing lifecycle command.
- No release publish execution.
- No post-release local install execution.
- No mutation of requirement truth after QA.
- No promotion of `.machine` aggregate projection to truth.

## 4. Source Evidence

- Brainstorm: `docs/brainstorms/2026-05-27-beacon-brainstorm-v1.4.11-aggregate-truth-lifecycle-gap.md`
- Previous blocked release check: current feature missing from version aggregate projection.
- Corrected aggregate state: `docs/beacon/archive/v1.4.11/.machine/change/v1.4.11.json`
- QA acceptance evidence: `docs/beacon/archive/v1.4.11/.machine/execution/qa-acceptance-beacon-design-human-subskills-closure-contract.json`

## 5. Route Decision

This is a post-QA release preflight guard improvement for v1.4.11.

It must enter the governed chain:

```text
change -> prd -> user-story -> test-case -> requirement_clarity -> freeze
```

After freeze, implementation may update runtime projection helpers and release/doctor tests.

## 6. Freeze Deliverables

- `docs/beacon/archive/v1.4.11/research/version-aggregate-projection-guard-contract.md`
- `docs/beacon/archive/v1.4.11/change/version-aggregate-projection-guard-contract.md`
- `docs/beacon/archive/v1.4.11/prd/version-aggregate-projection-guard-contract.md`
- `docs/beacon/archive/v1.4.11/user-story/version-aggregate-projection-guard-contract.md`
- `docs/beacon/archive/v1.4.11/qa/test-cases/version-aggregate-projection-guard-contract.md`

## 7. Boundary

This change freezes projection guard requirements only.

It does not redefine the Beacon lifecycle and does not make aggregate projection a requirement truth source.
