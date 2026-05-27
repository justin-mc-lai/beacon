# Research: Version Aggregate Projection Guard Contract

**Feature**: `version-aggregate-projection-guard-contract`  
**Version**: `v1.4.11`  
**Status**: `research-closed`  
**Date**: `2026-05-27`

## 1. 背景

v1.4.11 在 `beacon-design-human-subskills-closure-contract` 完成 implement / QA 后，release check 一度被挡住。

根因不是 feature 没做完，而是版本聚合投影漏账：

- feature requirement 已冻结。
- implementation evidence 已写入。
- QA acceptance 已通过。
- 但 `docs/beacon/v1.4.11/.machine/change/<feature>.json` 缺失。
- `release create` 只读取已有 feature change projection，所以版本 change 聚合仍然只有 8 条。
- `release check` 发现 current QA accepted feature 没进版本 change，于是 fail-closed。

这说明 Beacon 当前缺少一个内置守卫：当 QA 已经 accepted 一个 feature 时，release-facing version aggregate projection 必须同步可见。

## 2. 大白话问题

单条 feature 做完了，但版本总账没有记上。

这不是需求真相缺失，也不是新增生命周期。它是投影 / read model 缺失。

如果每次都靠人手动补：

- 容易漏。
- 容易把 `.machine` 误叫成 truth。
- release 前才爆雷。
- 还会让用户误以为 `qa` 和 `release` 中间多了一个新阶段。

## 3. 关键边界

本 feature 不新增 lifecycle。

主链仍然是：

```text
change/refreeze -> implement -> qa -> release check
```

版本聚合投影只是现有 surface 的内部写回和校验：

```text
qa acceptance writeback
  -> feature change projection writeback
  -> version aggregate projection refresh
  -> test-contract-index refresh / verify

release check
  -> aggregate inclusion gate
```

## 4. 收敛结论

冻结 `version-aggregate-projection-guard-contract`，要求 Beacon 把版本聚合投影守卫收进现有 QA / release / doctor 面：

1. QA acceptance 成功后，必须能生成或校验 feature-level change projection。
2. `release create` 必须重建 version-level change markdown / machine payload，并能发现 QA accepted 但缺 projection 的 feature。
3. `release check` 必须 fail-closed 校验 current QA accepted feature 已进入 version aggregate projection。
4. `doctor` 必须提供 repair-only 路径，用于重建 feature projection、version aggregate projection、test-contract-index。
5. 文案必须明确 aggregate projection 不是 truth source、不是 gate source、不是 lifecycle stage。

## 5. 设计原则

- Markdown PRD / user-story / test-cases 仍是 requirement truth。
- `.machine/change/<feature>.json` 是 release-facing projection input。
- `change/<version>.md` 和 `.machine/change/<version>.json` 是 version aggregate projection。
- QA pass 不直接等于 release ready；release 还要校验 projection inclusion。
- projection 刷新可以自动发生，但不能让用户多走一个人工 lifecycle step。

## 6. 验收重点

验收必须证明：

- 缺 feature change projection 时，release check 能明确指出 current feature 未进入版本聚合。
- QA accepted feature 的 projection 修复后，version change 聚合包含该 feature。
- version aggregate feature count 与 feature list 可审计。
- test-contract-index 会在修复路径中刷新并验证。
- 所有输出都避免把 aggregate projection 称为 truth。

## 7. 不做什么

本 feature 不做：

- 不新增 `aggregate-sync` lifecycle stage。
- 不新增用户面主命令作为必经步骤。
- 不让 aggregate projection 变成 requirement truth。
- 不改变 release 发布动作。
- 不自动执行 post-release install hook。
- 不重写已完成 feature 的需求真相。

## 8. 推荐下一跳

进入 `beacon-change-refreeze`，冻结：

```text
version-aggregate-projection-guard-contract
```

实现时应优先修改 deterministic runtime / tests，而不是继续加厚 skill 文案。

## Deep Summary

- source_skill: `beacon-deep`
- updated_at: `2026-05-27T03:22:26.372141+00:00`
- deep_artifact_root: `docs/beacon/v1.4.11/deep/version-aggregate-projection-guard-contract`
- machine_artifact_root: `docs/beacon/v1.4.11/.machine/deep/version-aggregate-projection-guard-contract`
- deep_requirement_state: `required`
- status: `closed`
- route_decision: `closed`
- release_supplement_ref: `docs/beacon/v1.4.11/.machine/deep/version-aggregate-projection-guard-contract/release-supplement.json`
- adoption_status: `route_only`
