# 执行索引（v1.3.3）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `../../global-boundaries.md`
4. `./boundaries.md`
5. `../prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
6. `../user-story/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
7. `../qa/test-cases/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
8. `./beacon-v1.3.3-core-slimming-and-external-skill-demotion-slimming-checklist.md`

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
3. 给后续实际实现提供一份不扩张心智负担的执行蓝图。
