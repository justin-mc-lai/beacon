# Beacon v1.3.1 总览

**主题**：人机共创中的心智包袱减重  
**状态**：accepted supplement line  
**日期**：2026-04-14

---

## 一句话总结

`v1.3.1` 已通过 formal release check，但仍然是 supplement line，不替代当前 runtime release line。

这条线的目标不是增加更多可见命令，而是把 Beacon 对人类暴露的心智面继续收窄：

1. 人类只关注有限闭环：`prd -> user-story -> test-case -> implement -> qa -> release`
2. `brainstorm` 持续嵌入 `prd -> user-story` 探索，不再要求人类单独维护复杂前置脑图
3. `implement` / `qa` 对人类保持单入口，对机器内部允许 team / learning / auto research 自由协作
4. 旧文档物料必须支持按文档版本一键更新对齐
5. 需求文档中遗漏点、问号点、未澄清点必须先经审核收口；未收口的 `prd/user-story` 不得冻结
6. 每个版本必须有技术评审给出确定性实现面：git 分支、worktree 隔离、服务目录与 monorepo 多服务映射
7. 探索 Beacon 的极简命令行，让“人类主线”与“机器协作入口”明确分层
8. 把极简人类面落成 Codex / Claude 可发现的 host skill pack，而不只是停留在文档建议
9. 同一个 `docs version` 必须允许多个并行 feature package 共存，而不是默认一个版本只服务一份 PRD
10. 交付后必须有独立 `change` 文档，以及版本级新增 / 删除 / 修复演进图

## 为什么要做这条线

`v1.3.0` 解决了：

- bounded team runtime
- implement-team / qa-team
- versioned git workflow contract
- 对旧项目 machine materials 的同步入口

但现在暴露出的新摩擦点不是“能力缺失”，而是“能力太多时，人类不知道自己到底该关注什么”。

对于真实项目操作者，人类的心智应只承受：

- 当前业务要解决什么
- 当前用户故事是否清晰
- 当前测试用例是否覆盖
- 当前实现是否交付
- 当前 QA 是否发现新问题
- 当前 release 是否可放行

而不应该被迫持续理解：

- team runtime 内部角色拆解
- learning / auto research 何时穿插
- 机器之间如何分工与回合协作
- 子代理 lane 的显式调度细节

## 这条线的核心变化

1. 把 Beacon 人类主面收敛为六段闭环。
2. 把 `brainstorm` 从“额外命令负担”转为 `prd/user-story` 探索中的持续能力。
3. 把 `implement` 与 `qa` 保持为人类单入口，team 协作退到机器内部执行面。
4. 把 learning / auto research 固化为 QA 中围绕冻结用户故事的覆盖增强机制。
5. 把旧版本物料升级收敛成按 `docs version` 指定的一键同步能力。
6. 把“需求澄清不足不得冻结”提升为正式前置门。
7. 把“每个版本必须先有技术评审确定实现面”提升为正式前置门。
8. 探索极简 CLI，不再要求人类记住过多细分命令。
9. 把“一个版本下多个 feature 并行包”固化为正式 contract，而不是隐式约定。
10. 把版本变更摘要沉淀成独立 `change` 文档与版本演进蓝图。

## 范围

### In scope

- 人类可见命令面的收敛
- `brainstorm` 与 `prd/user-story` 的耦合关系
- `implement` / `qa` 的 hidden team orchestration 模型
- learning / auto research 在 QA 中的边界与目的
- 旧版本文档物料按版本对齐升级
- 需求澄清审核与冻结前阻塞规则
- 技术评审对实现面、git/worktree/service scope 的确定性要求
- 极简 CLI 的人类主线设计
- Codex / Claude host skill pack 设计与安装约定
- 同一版本下多个 feature package 的并行治理与一对一文档链约束
- 独立 change 文档与版本演进图产出

### Out of scope

- 把所有底层命令删除
- 限制机器协作内部必须采用单一编排模型
- 重新定义 `v1.3.0` 已经落地的 bounded team runtime contract
- 让人类直接操作所有 machine lane

## 推荐阅读顺序

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `./execution/human-minimal-usage-guide.md`
4. `./execution/host-skill-pack-blueprint.md`
5. `./execution/parallel-feature-package-contract.md`
6. `./execution/change-document-contract.md`
7. `./execution/version-evolution-blueprint.md`
8. `./execution/boundaries.md`
9. `./execution/deterministic-implementation-contract-blueprint.md`
10. `./think/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
11. `./user-story/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
12. `./prd/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
13. `./qa/test-cases/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
14. `./change/v1.3.1.md`
15. `./release/v1.3.1.md`
