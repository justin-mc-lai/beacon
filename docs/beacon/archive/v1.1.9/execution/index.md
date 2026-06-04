# Execution Index (v1.1.9 implemented line)

## Human Primary Surface

- `../SUMMARY.md`
- `../version/beacon-v1.1.9-exhaustiveness-research.md`
- `../research/beacon-pua-exhaustiveness-layer-analysis.md`
- `../research/beacon-karpathy-autoresearch-evo-analysis.md`
- `../prd/beacon-closure-control-learning-overlay.md`
- `../user-story/beacon-closure-control-learning-overlay.md`
- `../qa/test-cases/beacon-closure-control-learning-overlay.md`
- `../release/v1.1.9.md`
- `./architecture-blueprint.md`
- `./closure-loop-blueprint.md`
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`

## 推荐阅读顺序（按角色）

### 产品 / 版本负责人
1. `../SUMMARY.md`
2. `../version/beacon-v1.1.9-exhaustiveness-research.md`
3. `../prd/beacon-closure-control-learning-overlay.md`
4. `./closure-loop-blueprint.md`
5. `../release/v1.1.9.md`

### 技术负责人 / 架构负责人
1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `../prd/beacon-closure-control-learning-overlay.md`
4. `../qa/test-cases/beacon-closure-control-learning-overlay.md`
5. `./closure-loop-blueprint.md`
6. 两份 research 输入

### 执行 Agent / 自动化消费者
1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `../user-story/beacon-closure-control-learning-overlay.md`
4. `../qa/test-cases/beacon-closure-control-learning-overlay.md`
5. `./closure-loop-blueprint.md`
6. `../version/beacon-v1.1.9-exhaustiveness-research.md`

## 本版核心结论

v1.1.9 不应新增一套与 v1.1.8 平行的生命周期；
而应作为 **v1.1.8 五线交付面的控制层与学习层增强**。

也就是：

```text
v1.1.8 = delivery kernel
v1.1.9 = control + recovery + learning overlay
```

补充现实判断：

- 当前正式交付主链已经较强闭环
- `qa run <feature>` / `qa evolve` / `story-exhaustive` / release scorecard / keep-discard 已落地
- 但全生命周期 + 全端口 anti-drift 仍未完全闭环
- calibrated confidence 与 QA precision learning 仍未落地

## 关键闭环地图

```text
workflow / implement / qa / review / gate
→ debug harvest / technical archive
→ version research / keep-discard
→ next requirements iteration
```

## Notes

- `v1.1.9` 现已作为 **已落地实现线** 维护。
- 当前 PyPI / package 版本口径仍可能保留在 `v1.1.8`，但能力与文档核验面已进入 `docs/beacon/archive/v1.1.9/`。
- 本目录重点回答：如何把已有 Beacon 功能编织成更强的闭环，而不是重复发明能力面。
