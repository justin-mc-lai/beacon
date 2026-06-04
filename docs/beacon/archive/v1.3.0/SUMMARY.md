# Beacon v1.3.0 总览

**主题**：在不把 Beacon 扩成通用多代理 runtime 的前提下，引入简化版 Codex 原生子代理能力，并同步收口版本语义与中英双面文档契约  
**状态**：规划线  
**日期**：2026-04-10

---

## 一句话总结

`v1.3.0` 的目标不是“让 Beacon 变成另一个 agent 平台”，而是：

1. 让部分阶段能显式使用受约束的 Codex 原生子代理
2. 先在 `implement run` 上证明多代理闭环，再扩到其他阶段
3. 把版本语义统一冻结
4. 把人类主读材料默认切成中文，同时保留机器面默认英文
5. 稳定新增 `team` surface，明确 implement-team 与 qa-team 的触发与隔离规则

## 为什么要做这条线

`v1.2.0` 已经把主链与 project-skill workflow 收得更稳。

`v1.2.1` 补上了 Codex prompt ingress visibility。

现在暴露出的下一步摩擦点是：

1. `ask` 能识别意图，但还不能稳定表达“下一版本能力演进 + 子代理规划”。
2. `implement run` 已有 `native-single` / `native-team`，但这还是 Beacon 自己的 runner，不是共享的 Codex-native 子代理契约。
3. `think / user-story / prd / test-case / qa` 仍以单阶段单面生成为主。
4. 版本语义虽然已有 machine-readable source，但缺更强的人类解释入口与后续源码统一归口约束。
5. `v1.3.0` 的人类主读材料仍有较多英文残留，不利于后续中文优先协作。
6. 当前还缺稳定的 team surface 定义，无法明确回答“何时进入 implement-team、何时进入 qa-team”。

## 这条线的核心变化

1. 增加简化版 `subagent_mode` 契约。
2. 子代理默认关闭、显式启用、受阶段边界约束。
3. 采用 `implement-first` 路径，优先在 `implement run` 上验证。
4. 把版本语义冻结为统一 contract，不允许命令面各自解释。
5. 明确区分：
   - 人类主读材料：默认中文
   - 机器可读工件：默认英文/机器友好结构
6. 把 `version-semantics` 做成“一体两面”：
   - JSON 机器真相
   - Markdown 中文镜像
7. 把 `artifact-language-policy` 做成统一“中人 / 英机”规范。
8. 把 `team` 正式提升为稳定 surface，而不是只停留在隐式 team-mode 提法。
9. 为 `implement` 补一条面向 frozen baseline 的 `dev-run` 开发入口，允许只在安全前置 gate 范围内自动准备执行面。
10. 把实现期 git workflow 从全局配置偏好，收敛成 versioned execution material 中的显式 contract（分支 / worktree / 服务目录）。
11. 提供 `implement sync-git-workflow`，把 config seed 显式固化到当前版本物料。

## 范围

### In scope

- `ask` / `prompt` 对下一版本子代理演进的规划路由
- `implement run` 的 Codex-native 多代理集成
- `implement dev-run` 的安全自动前置 gate 处理
- `think / user-story / prd / test-case / qa` 的后续扩面蓝图
- 版本语义 contract
- 中文人类面与英文机器面的双轨治理
- versioned git workflow contract（branch / worktree / service directories）

### Out of scope

- 通用多代理操作系统
- 任意 shell DAG 编排
- 不带 evidence writeback 的后台隐式委托
- 用中文替换所有机器主键

## 推荐阅读顺序

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `./execution/artifact-language-contract.md`
4. `./execution/version-semantics-contract.md`
5. `./execution/codex-native-subagent-implementation-blueprint.md`
6. `./user-story/beacon-v1.3.0-simplified-codex-native-subagents.md`
7. `./prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
8. `./qa/test-cases/beacon-v1.3.0-simplified-codex-native-subagents.md`
9. `./release/v1.3.0.md`
