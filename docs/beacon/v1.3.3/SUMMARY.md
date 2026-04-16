# Beacon v1.3.3 总览

**主题**：核心瘦身与外部 skill 降级  
**状态**：规划线  
**日期**：2026-04-16

---

## 一句话总结

`v1.3.3` 的目标不是继续往主链上加能力，而是把 Beacon 收回到更轻的核心：

```text
human minimal surface
→ host-native implement / qa
→ compatibility plane for external skills
```

也就是说：

- core 继续只教 `6+3`
- 宿主原生能力继续优先
- 外部 `skill / profile / orchestrate / bridge` 退到 compatibility plane

## 当前版本目标

1. 让 README、help、skills 和测试叙事重新对齐到 `6+3`。
2. 把外部 runner / orchestration 从 core narrative 中降级出去。
3. 让 `qa` 默认不再隐式执行外部 orchestration。
4. 保留真实项目需要的 contract/evidence gate，但与外部执行解耦。

## 为什么要做这条线

`v1.3.2` 已经把：

- `implement` 三模式
- 迭代浏览器 QA
- host-native subagent/team 路线
- `global-boundaries`

这些核心主线收紧了。

下一步的真正价值不是继续堆执行面，而是把仍残留在核心叙事里的重型兼容能力降级：

- `omx`
- `omc`
- `gstack`
- `skill/profile/orchestrate`
- `ralph-bridge`

## 当前范围

### In scope

- core vs compatibility 分层
- README / SKILL / help 文案收口
- `qa` 主路径去隐式外部依赖
- external adapters 叙事降级
- project contract 与 external execution 解耦

### Out of scope

- 删除所有 legacy 兼容代码
- 删除 project contract / required evidence 能力
- 改写 `v1.3.2` 已验收的实现闭环
- 引入新的公开 runtime / bridge 命令

## 推荐阅读顺序

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `../global-boundaries.md`
4. `./execution/boundaries.md`
5. `./prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
6. `./user-story/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
7. `./qa/test-cases/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`
8. `./execution/beacon-v1.3.3-core-slimming-and-external-skill-demotion-slimming-checklist.md`

## 当前版本包起点

当前 `v1.3.3` 先从一个单 feature 版本包起步：

- `beacon-v1.3.3-core-slimming-and-external-skill-demotion`

如果后续有新增版本范围，应继续保持：

- core 主面不扩张
- compatibility plane 单独叙事
- 正式 requirement 只回写到当前版本包
