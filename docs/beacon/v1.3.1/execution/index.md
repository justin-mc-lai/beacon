# 执行索引（v1.3.1）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `./human-minimal-usage-guide.md`
4. `./host-skill-pack-blueprint.md`
5. `./parallel-feature-package-contract.md`
6. `./change-document-contract.md`
7. `./version-evolution-blueprint.md`
8. `./boundaries.md`
9. `./deterministic-implementation-contract-blueprint.md`
10. `../think/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
11. `../user-story/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
12. `../prd/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
13. `../qa/test-cases/beacon-v1.3.1-human-ai-cocreation-cognitive-load-reduction.md`
14. `../change/v1.3.1.md`
15. `../release/v1.3.1.md`

## 说明

- `v1.3.1` 当前已通过 release check，作为 accepted supplement line 存在。
- `v1.3.1` 仍不是 current runtime release line；当前 runtime release line 仍是 `v1.3.0`。
- 这条线的重点不是新增更多能力，而是收窄人类主界面。
- 这条线还要求把极简人类面落成可被 Codex / Claude 自动发现的 host-visible skills。
- 对人类暴露的主闭环应收敛为：
  - `prd`
  - `user-story`
  - `test-case`
  - `implement`
  - `qa`
  - `release`
- `brainstorm` 不应继续作为额外心智负担存在，而应嵌入 `prd -> user-story` 探索链。
- `./human-minimal-usage-guide.md` 是当前最适合人类操作者直接使用的极简人类面手册。
- `./host-skill-pack-blueprint.md` 定义 `using-beacon + 9 public subskills` 的 host packaging 与 prompt-trigger 约定。
- `./parallel-feature-package-contract.md` 把“同一版本支持多个并行 PRD / user-story / test-case 包”正式写成 contract。
- `./change-document-contract.md` 规定每个交付包与每个版本都应产出独立 change 文档。
- `./version-evolution-blueprint.md` 给出版本路线演进图以及新增 / 删除 / 修复分类。
- 需求文档中的遗漏点、不清晰点、问号点、未澄清点必须先被显式审核；否则 `prd` / `user-story` 不得 freeze。
- `./boundaries.md` 明确人类主命令、辅助命令、隐藏机器命令以及 freeze / implement 阻塞边界。
- `implement-team`、`qa-team`、learning、auto research 等 machine lanes 仍允许存在，但不应成为人类主操作入口。
- 每个版本的需求技术评审必须先给出确定性实现面：
  - 目标 git 分支
  - 是否使用 worktree
  - 隔离开发环境
  - monorepo / multi-service 下的具体服务目录与责任边界
- `./deterministic-implementation-contract-blueprint.md` 定义技术评审输出应如何 materialize 成实现前 contract。
- 现有 Beacon 实现已经通过 `feature slug` 把 `prd / user-story / test-case / technical-implementation` 按 feature 平铺到同一版本目录中；`v1.3.1` 只是把这件事显式化并要求 release / change 也遵守同一 identity。
- 旧项目在 Beacon runtime 升级后，应允许按文档版本一键同步 machine materials：
  - `beacon doctor sync-materials --project-root <root> --version <docs-version> --all-features`
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`
