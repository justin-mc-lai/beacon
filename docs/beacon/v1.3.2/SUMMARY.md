# Beacon v1.3.2 总览

**主题**：implement / qa 三模式与 Ralph 持续交付闭环  
**状态**：规划线  
**日期**：2026-04-14

---

## 一句话总结

`v1.3.2` 的目标不是继续增加新的 runtime 名词，而是把 **`implement + qa`** 的执行面收敛成三种清晰模式：

1. `single`：单进程、单 owner、最小执行面
2. `team`：有界多代理、显式分工、可视执行
3. `ralph`：围绕 `implement + qa` 持续穷尽到完整可交付的闭环控制面

并且把这三种模式统一放回同一条 `implement + qa` 主链，而不是继续分散在 `native-single`、`codex-subagents`、`team-run`、`ralph-bridge` 等不同叙事里。

## 为什么要做这条线

`v1.3.0` 已经证明了：

- bounded team runtime 可行
- `implement-team` / `qa-team` 可用
- tmux / HUD / role reports 可以稳定落盘

`v1.3.1` 继续把人类主线收窄。

但现在新的摩擦点是：

1. `implement` 已默认偏向 `codex-subagents`，但这个名字容易让人误解为“已经是通用原生子代理平台”。
2. 当前 `team` 已经是稳定执行面，但在主叙事里仍不够清晰。
3. 用户仍然缺一个明确的“不要多代理，只要单进程最小执行面”的正式入口。
4. `ralph-bridge` 目前更像 bridge 状态记录，而不是“持续推进直到完整可交付”的正式执行模式。
5. 现有恢复/穷尽控制面已经存在，但还没有被统一提炼成 Ralph 的交付闭环合同。
6. QA 作为正式执行面，仍缺少一份明确口径来说明：
   - 它只围绕冻结的 `prd / user-story / test-case`
   - 它应启动目标项目浏览器环境
   - 它应按顺序、逐轮、带 autoresearch 增量地演进

## 这条线的核心变化

1. 把 `implement` 的执行模式正式定义为：`single` / `team` / `ralph`。
2. 明确这套模式只正式落在 `implement` 与 `qa`，而不是扩展到 requirement 阶段。
3. 把当前 `codex-subagents` 的实际语义正式收敛为 `team` 模式，而不是继续让 runner 名称承担产品叙事。
4. 明确 `team` 是 Beacon 自己掌控的 bounded multi-agent runtime，不是通用 agent platform。
5. 把 `qa` 定义为浏览器原生、冻结材料驱动、顺序可迭代、自带 autoresearch 增量的验收闭环。
6. 把 `ralph` 从 bridge 升级为执行闭环控制器：它驱动 `implement -> review -> qa -> gate -> repair`，直到达到明确终态。
7. `ralph` 不直接改写 requirement truth，只调度既有正式阶段。
8. 统一 HUD / status / checkpoint / exhaustion 口径，让三种模式共享可观测与恢复面。
9. 吸收 `oh-my-codex` 这类开源项目中真正有价值的契约：
   - 显式 teamwork mode
   - worktree / 隔离执行
   - 持续推进的 Ralph loop
   - durable status / HUD / resume
10. 不吸收 generic launcher shell、深层递归代理或第二套 truth plane。

## 范围

### In scope

- `implement` 三模式 contract
- `qa` 的浏览器驱动、自迭代 autoresearch contract
- `ralph` 的闭环终态与持续推进规则
- `single/team/ralph` 的统一命令语义
- HUD / status / control plane 的统一观测面
- team runtime 与 worktree/runtime 隔离的后续落点
- 对当前 `codex-subagents`、`native-single`、`team-run`、`ralph-bridge` 的兼容映射

### Out of scope

- 把 Beacon 改造成通用多代理操作系统
- 让 `think / user-story / prd / test-case` 默认进入多代理执行
- 让 worker 直接持有正式 writeback ownership
- 重写 `v1.3.0` 与 `v1.3.1` 已经成立的 requirement truth / gate / release 模型

## 推荐阅读顺序

1. `./execution/index.md`
2. `./execution/architecture-blueprint.md`
3. `./research/beacon-v1.3.2-responsibility-optimization-analysis.md`
4. `./execution/implement-execution-modes-blueprint.md`
5. `./execution/implement-command-contract.md`
6. `./execution/qa-iterative-browser-contract.md`
7. `./execution/ralph-closure-state-machine.md`
8. `./prd/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.md`
9. `./user-story/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.md`
10. `./qa/test-cases/beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa.md`
