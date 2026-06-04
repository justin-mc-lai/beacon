# Beacon v1.3.9 Execution 导航

## 这个目录是做什么的

`execution/` 是 `v1.3.9` 的人类面执行目录，用来承接实现、验收、发布前检查、运行说明与关键闭环证据。

当前 `v1.3.9` 已完成 release 收口，可把这里视为“最终执行归档 + 验收索引”。

这里不承担 machine canonical truth 的唯一职责。机器权威面仍在：

- `docs/beacon/archive/v1.3.9/.machine/execution/`
- `.beacon/qa/features/`
- `.beacon/state/`

## 推荐阅读顺序

1. `docs/beacon/archive/v1.3.9/SUMMARY.md`
2. `docs/beacon/archive/v1.3.9/change/v1.3.9.md`
3. `docs/beacon/archive/v1.3.9/release/v1.3.9.md`
4. 当前 feature 对应的 `implementation-summary-*.md`
5. 当前 feature 对应的 `qa-acceptance-*.md`

## 本目录主要内容

### 1. 实现摘要

用于快速理解某条 feature line 最终落地了什么：

- `implementation-summary-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `implementation-summary-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- `implementation-summary-beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
- `implementation-summary-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`

### 2. QA 验收闭环

用于查看每条子线的验收结果与 acceptance dual-write 产物：

- `qa-acceptance-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `qa-acceptance-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- `qa-acceptance-beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
- `qa-acceptance-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`

### 3. 设计 / 约束 / 过程文档

这类文档用于解释某次实现轮次中的约束、过程或特定专题：

- `technical-implementation-*.md`
- `implementation-plan-*.md`
- `requirement-clarity-*.md`
- `revision-delta-*.md`
- `ralph-summary-*.md`
- `ralph-round-*.md`

### 4. 子代理运行记录

如果某条实现使用了 codex subagents，运行记录在：

- `execution/codex-subagents/`

这些记录用于追溯，不是最终的人类主交付面。

## 与 machine 面的边界

- `execution/*.md`：给人看，强调摘要、说明、证据索引、下一步
- `.machine/execution/*.json`：给系统消费，承接 canonical envelope、writeback、projection
- `.beacon/`：运行时内部状态，不作为长期人类主阅读面

## v1.3.9 重点看哪些文件

如果只想快速理解本版本，优先看：

- `docs/beacon/archive/v1.3.9/change/v1.3.9.md`
- `docs/beacon/archive/v1.3.9/release/v1.3.9.md`
- `qa-acceptance-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `qa-acceptance-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- `qa-acceptance-beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
- `qa-acceptance-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`

## 本轮最终状态

- `gate check release`: `Pass`
- `release check`: `Pass`
- `release scorecard`: `ready`
- `version coverage`: `story 4/4, ac 26/26, tc 67/67`

## 相关补充

- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`

这两份属于历史演进/评分契约补充，不是本版本最优先的阅读入口。
