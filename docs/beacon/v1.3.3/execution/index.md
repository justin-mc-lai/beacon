# 执行索引（v1.3.3）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `../../global-boundaries.md`
4. `./boundaries.md`
5. `../prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
6. `../prd/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`
7. `../prd/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
8. `../user-story/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
9. `../user-story/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`
10. `../user-story/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
11. `../qa/test-cases/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
12. `../qa/test-cases/beacon-v1.3.3-minimal-hud-scenarios-and-implementation.md`
13. `../qa/test-cases/beacon-v1.3.3-memory-friction-evolution-toolkit.md`
14. `./beacon-v1.3.3-core-slimming-and-external-skill-demotion-slimming-checklist.md`

## 说明

- `v1.3.3` 的主题是 Beacon core slimming，而不是继续放大 workflow 面。
- 这条线只回答一个核心问题：
  - Beacon 哪些能力还属于 core，哪些必须退到 compatibility。
- 人类主流程仍固定为：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

- `skill / profile / orchestrate / external adapters` 的处理目标，不是删除一切，而是退出默认主叙事。
- `../../global-boundaries.md` 仍是高于所有版本线的唯一全局约束源。

## 这条线的输出目标

1. 讲清 v1.3.3 的 core/compatibility 分层。
2. 把瘦身目标落实到 README/help/skill/tests。
3. 通过并行 HUD PRD 锁定 S1-S6 极简场景与 1-3 行预算。
4. 通过并行 toolkit PRD 锁定 memory/friction 演进与 lighthouse 并行策略。
5. 给后续实际实现提供一份不扩张心智负担的执行蓝图。
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`
