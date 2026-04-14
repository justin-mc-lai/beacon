# Think：Beacon v1.3.1 人机共创心智包袱减重

**Feature**: `beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction`  
**Version**: `v1.3.1`  
**Date**: `2026-04-12`  
**Status**: `accepted supplement line`

## 问题框定

Beacon 目前的问题不只是“功能够不够”，而是“人类是否需要理解太多命令与内部执行细节”。

对于真实项目操作者，人类的心智是有限的。

如果 Beacon 继续把：

- `brainstorm`
- `team`
- `implement-team`
- `qa-team`
- learning
- auto research
- doctor repair / sync

都暴露成需要长期记忆的操作面，那么即使底层能力变强，人类的主体验也会更重。

## 想要的结果

让 Beacon 对人类看起来像一个有限、稳定、闭环的交付系统：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

同时，让机器内部继续拥有高自由度：

- `brainstorm` 深挖需求
- team runtime 快速实现
- qa team 做验证和 handoff
- learning / auto research 持续补 coverage

但这些内部动作都由 Beacon 自由决定，而不是持续要求人类操控。

## 核心判断

Beacon 下一条线应优先优化：

1. 人类主面极简化
2. 机器内部 lane 隐藏化
3. QA 回合必须带来新发现、新边界、新覆盖
4. 旧项目升级后的物料同步自动化

## 约束

1. 不得破坏 `v1.3.0` 已落地的 team runtime 能力。
2. 不得让机器 lane 偏离冻结用户故事。
3. 不得让人类继续背负越来越多的子命令。
4. 不得把“极简”做成“能力削弱”。

## 结论

`v1.3.1` 已验证为一条“交互收口 + 执行隐藏 + 同步增强”的 accepted supplement line。
