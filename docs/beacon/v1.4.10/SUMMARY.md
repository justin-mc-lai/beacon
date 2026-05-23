# Beacon v1.4.10 总览

## 版本状态

- `v1.4.10` 当前状态：`research_open`
- 当前主题：补齐 v1.4.9 后置的 QA 深挖、Better Harness Skill Eval Kit、Ralph 长任务闭环、以及 `beacon learn` 项目级 skill 演进能力。
- 本版本线当前只建立人类面调研入口，不代表 requirement frozen。

## 版本目标候选

`v1.4.10` 当前候选方向来自 v1.4.9 后置 research 和外部 harness / skill evolution 参考材料：

P0 推荐冻结：

1. `qa-evo-deep-state-scenario-round-memory-contract`
2. `better-harness-skill-eval-kit-regression-core`

P1/P2 research input：

3. `ralph-task-loop-checkpoint-recovery-contract`
4. `project-lifecycle-hook-skill-toolkit-contract`
5. `implement-mode-human-playbooks-and-routing-contract`
6. `learn-context-to-project-skill-lifecycle-injection`

这些候选方向必须后续进入 `change/refreeze`、`prd`、`user-story`、`test-case` 后才能成为 frozen truth。

当前推荐方向已经收敛为：

```text
P0: qa-evo-deep + Skill Eval Kit
P1: Ralph Task Loop / project lifecycle hooks / implement mode playbooks
P2: learn context-to-project-skill lifecycle injection
```

## CEO Review Challenge

`v1.4.10` 当前 research 包存在明显过载风险：五条候选方向都合理，但不能同时作为 P0 冻结和实现目标。

CEO review 建议将本版本 promise 收窄为一个可验收主轴：

> 让 Beacon 的“验收与人类面 skill 演进”变得可审计、可回归、可路由，而不是一次性补齐所有自动化执行能力。

建议 P0 只冻结：

1. `qa-evo-deep-state-scenario-round-memory-contract`
2. `better-harness-skill-eval-kit-regression-core`

建议 P1/P2 后置：

- `project-lifecycle-hook-skill-toolkit-contract`：先做 project-level Markdown hook contract + manual toolkit，不做自动触发。
- `implement-mode-human-playbooks-and-routing-contract`：保留 `beacon-implement` 唯一入口，只补 single / team / ralph mode playbook 和路由评测。
- `ralph-task-loop-checkpoint-recovery-contract`：先作为后续长任务控制 research，不进入同版 P0。
- `learn-context-to-project-skill-lifecycle-injection`：先只冻结 learning influence / candidate skill admission，不做自动注入。

因此下一次 `change-refreeze` 不应把 hook、Ralph、learn、implement mode 与 QA / Skill Eval 写成同等 P0。

## 当前需求包

- Research
  - `docs/beacon/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-evolution.md`
  - `docs/beacon/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
  - `docs/beacon/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`

## 继承边界

本版本继承 v1.4.9 的 Markdown-first 和只读 support 写入拓扑：

- 普通 support review upsert 到 `docs/beacon/<version>/research/<feature>.md`。
- `beacon-deep` 详细材料进入 `docs/beacon/<version>/deep/<feature>/`，research 只保留索引。
- `beacon-learn` 进入 `docs/beacon/<version>/learning/<feature>.md` 或 transaction，research 只记录 learning influence 摘要。
- 显式 version + feature 的只读分析不得回退到 `docs/brainstorms/`。
- 机器面只保存运行证据、索引、trace、eval result，不作为 requirement truth。

## 当前不包括

- 不冻结 PRD / user-story / test-case。
- 不新增主生命周期 stage。
- 不让 `qa-evo-deep`、`source-driven`、`learn` 或 skill eval 自动成为 gate verdict。
- 不让项目级 hook 成为新的 Beacon lifecycle stage。
- 不把 single / team / ralph 拆成三个新的 public implement skill。
- 不把 `.machine` 或 `.beacon/state` 评测结果当作需求真相。
- 不直接实现 v1.4.10 runtime。

## 下一步

推荐下一跳：

```bash
beacon change-refreeze run "qa-evo-deep-and-skill-eval-kit-v1410" --project . --version v1.4.10
```

冻结时应先按 CEO review 收窄正式 feature 切分、P0/P1 范围和验收顺序，避免把 project hook、Ralph Task Loop、learn skill injection 一次性并入 P0。
