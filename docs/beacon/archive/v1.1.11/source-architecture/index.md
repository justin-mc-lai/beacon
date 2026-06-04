# Beacon v1.1.11 Source Architecture Index

## 目的

这组文档不是产品需求文档，也不是 API 参考手册。

它是 Beacon 当前源码架构的人类友好投影，回答：

- Beacon 代码主要分成哪些层
- 命令、状态、memory、skill、workflow、QA、implement、release 分别落在哪里
- 人在改代码时，应该同步更新哪些架构文档

## 适合谁读

- 新接手 Beacon 源码的开发者
- 需要让 Agent 在 Beacon 上继续演进的维护者
- 需要把产品 requirement 与源码结构对齐的负责人

## 推荐阅读顺序

1. `./overall-system-map.md`
2. `./command-surface-and-module-map.md`
3. `./lifecycle-memory-and-state.md`
4. `./skills-prompts-and-project-workflows.md`
5. `./workflow-and-artifact-flow.md`
6. `./qa-implement-release-feedback-loop.md`
7. `./sync-contract.md`

## 本目录与其它目录的关系

- `user-story / prd / qa/test-cases`：定义“为什么要有这组文档”
- `source-architecture/`：解释“Beacon 当前源码是怎么组织的”
- `.machine/`：Beacon workflow 机器侧正式工件
- `.beacon/`：运行态与证据链

## 约束

这组文档要做到：

- human-first
- source-anchored
- versioned
- continuously synced

做不到这些，就会再次退化成历史补充材料。
