# Beacon v1.1.10 Source Architecture Sync Contract

## 目标

把源码架构文档更新从“可选补充项”变成正式交付项。

## 必须同步更新文档的变更类型

以下任一变化发生时，都必须检查并更新 `source-architecture/`：

1. 新增或重构 CLI 子命令
2. 命令注册方式或命令分层变化
3. story/revision/workflow memory/runtime state 结构变化
4. `.machine` 工件格式或路径变化
5. `.beacon` 运行态目录结构变化
6. skill/profile/orchestration 结构变化
7. browser session/auth persistence 结构变化
8. QA / implement / release / learning loop 的回流路径变化

## 最小更新要求

至少同步：

- `source-architecture/index.md`
- 受影响主题文档
- 对应 feature 的 release/test feedback 说明

如果变化较大，还应同步：

- 并行 requirement materials
- machine material regression tests

## 检查问题

每次结构性变更后至少回答：

1. 入口变了吗
2. 状态变了吗
3. 工件流变了吗
4. 项目 workflow / skill 面变了吗
5. QA -> implement -> feedback 闭环变了吗

有任一回答是“变了”，就不应跳过文档同步。

## 反例

以下做法不合格：

- “代码先上，文档以后补”
- 只更新 README，不更新源码架构目录
- 只更新 requirement docs，不更新 source-architecture
- 引入新的 state/artifact path，但文档仍写旧路径

## 结论

从 `v1.1.10` 开始，源码架构文档应被视为 Beacon 开发流程的一部分，而不是开发结束后的装饰。

In other words:

> structural code changes must update source architecture docs.
