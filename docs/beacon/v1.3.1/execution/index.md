# 执行索引（v1.3.1）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `./boundaries.md`
4. `./deterministic-implementation-contract-blueprint.md`
5. `../think/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
6. `../user-story/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
7. `../prd/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
8. `../qa/test-cases/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
9. `../release/v1.3.1.md`

## 说明

- `v1.3.1` 当前是规划线，不是 current runtime release line。
- 这条线的重点不是新增更多能力，而是收窄人类主界面。
- 对人类暴露的主闭环应收敛为：
  - `prd`
  - `user-story`
  - `test-case`
  - `implement`
  - `qa`
  - `release`
- `brainstorm` 不应继续作为额外心智负担存在，而应嵌入 `prd -> user-story` 探索链。
- 需求文档中的遗漏点、不清晰点、问号点、未澄清点必须先被显式审核；否则 `prd` / `user-story` 不得 freeze。
- `./boundaries.md` 明确人类主命令、辅助命令、隐藏机器命令以及 freeze / implement 阻塞边界。
- `implement-team`、`qa-team`、learning、auto research 等 machine lanes 仍允许存在，但不应成为人类主操作入口。
- 每个版本的需求技术评审必须先给出确定性实现面：
  - 目标 git 分支
  - 是否使用 worktree
  - 隔离开发环境
  - monorepo / multi-service 下的具体服务目录与责任边界
- `./deterministic-implementation-contract-blueprint.md` 定义技术评审输出应如何 materialize 成实现前 contract。
- 旧项目在 Beacon runtime 升级后，应允许按文档版本一键同步 machine materials：
  - `beacon doctor sync-materials --project-root <root> --version <docs-version> --all-features`
