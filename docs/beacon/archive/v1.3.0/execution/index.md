# 执行索引（v1.3.0）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `./artifact-language-contract.md`
4. `./version-semantics-contract.md`
5. `./codex-native-subagent-implementation-blueprint.md`
6. `./codex-subagent-runtime-and-tmux-hud-blueprint.md`
7. `./team-runtime-usage-guide.md`
8. `../../research/beacon-codex-native-subagent-direction-gstack-superpowers.md`
9. `../think/beacon-v1.3.0-simplified-codex-native-subagents.md`
10. `../user-story/beacon-v1.3.0-simplified-codex-native-subagents.md`
11. `../prd/beacon-v1.3.0-simplified-codex-native-subagents.md`
12. `../qa/test-cases/beacon-v1.3.0-simplified-codex-native-subagents.md`
13. `../release/v1.3.0.md`

## 说明

- `v1.3.0` 已是当前 runtime release line。
- 这条线的重点是：在保持 Beacon 主链与 release truth 不变的前提下，引入受约束的 Codex 原生子代理能力。
- `implement run` 是第一条需要真正验证多代理闭环的执行面。
- `implement dev-run` 是 frozen revision 进入开发的推荐入口：它只自动处理安全前置 gate，不自动改写需求真相。
- `implement sync-git-workflow` 用来把 config seed 显式固化成当前版本线的 git workflow contract。
- “下一版本 + 子代理演进”类 prompt 应优先进入 `version` 规划面，再收敛到阶段实现。
- `./artifact-language-contract.md` 定义未来所有 artifact 类型的“中人 / 英机”统一规范。
- `./version-semantics-contract.md` 是 `beacon/version-semantics.json` 的中文镜像；两者必须视为同步的一体两面契约。
- `team` 在 `v1.3.0` 应作为稳定显性 surface 看待，而不仅是实现细节里的隐式模式。
- `implement-team` 已完成 tmux runtime + HUD 实机落地；`qa-team` 已接入同一 runtime/HUD contract。
- `implement-team` 的执行角色应补入实现期架构角色（`implementation-architect`），但该角色只允许写 execution-scoped artifacts。
- `implement` 的 git branch / worktree / service-directory 约束应优先来自 versioned execution materials，而不是只写在全局 `beacon.config`。
- Codex-native 子代理方向研究已提升到 `docs/beacon/research/` 全局目录；`v1.3.0` 只消费其结论，不再把该研究本体视为版本私有物料。
- `./codex-subagent-runtime-and-tmux-hud-blueprint.md` 说明下一步如何把 team mode 推进到真实 tmux / pane 级多角色执行。
- `./team-runtime-usage-guide.md` 是当前最适合操作者直接使用的 team runtime 手册。
- 对实际项目执行 Beacon runtime 升级后，应先同步 machine requirement materials，再进入 `qa team-plan` / `qa team-run`：
  - `beacon doctor sync-materials --project-root <root> --version <docs-version> --all-features`
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`
