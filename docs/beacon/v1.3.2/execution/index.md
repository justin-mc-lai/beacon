# 执行索引（v1.3.2）

## 推荐阅读顺序

1. `../SUMMARY.md`
2. `./architecture-blueprint.md`
3. `../research/beacon-v1.3.2-responsibility-optimization-analysis.md`
4. `./implement-execution-modes-blueprint.md`
5. `./implement-command-contract.md`
6. `./qa-iterative-browser-contract.md`
7. `./ralph-closure-state-machine.md`

## 说明

- `v1.3.2` 关注的是 `implement + qa` 执行面的收口，不是新一轮 requirements mainline 扩表面。
- 这条线要解决的问题是：让用户和源码都能明确回答“现在到底是在单进程执行、team 多代理执行，还是 Ralph 持续闭环执行”。
- `single`、`team`、`ralph` 应被理解为同一 execution family 下的三种模式，而不是三个互相独立的命令体系。
- `../research/beacon-v1.3.2-responsibility-optimization-analysis.md` 负责把 stage owner、execution runtime、Ralph closure controller 与 learning plane 的职责再切齐。
- 当前仓库里已经有稳定的 `implement-team` / `qa-team` runtime、tmux pane、HUD 和 role reports；`v1.3.2` 需要把它们重新讲清楚，而不是重新发明。
- 当前仓库里 `implement` 默认 runner 已偏向 `codex-subagents`；`v1.3.2` 需要把这个技术实现语义提升成明确的人类可理解模式：`team`。
- 当前仓库里 `qa` 已有 `run / team-run / evolve / status / session` 这些 surface；`v1.3.2` 需要把它们重新收成“浏览器原生、冻结材料驱动、逐轮 autoresearch 演进”的正式合同。
- `ralph` 在 `v1.3.2` 中不应再只是 bridge state；它应成为“持续穷尽到完整可交付”的正式闭环层。
- requirement truth、formal writeback、gate、release 仍由 Beacon stage owner 持有。
