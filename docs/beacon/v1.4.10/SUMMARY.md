# Beacon v1.4.10 总览

## 版本状态

- `v1.4.10` 当前状态：`released`
- 当前已闭环主题：补齐 v1.4.9 后置的 QA 深挖、Better Harness Skill Eval Kit、项目级 lifecycle hook toolkit，以及 QA evo-deep 证据绑定 / AC 感知闭环。
- 本版本线已经完成 3 个正式 feature 的 change/refreeze、PRD、user-story、test-case、implement、QA、release 闭环；剩余 research input 继续作为后续 backlog 管理。

## 版本目标候选

`v1.4.10` 候选方向来自 v1.4.9 后置 research 和外部 harness / skill evolution 参考材料。发布后状态如下：

已闭环：

1. `qa-evo-deep-and-skill-eval-kit-v1410`
   - 合并承接早期 `qa-evo-deep-state-scenario-round-memory-contract` 与 `better-harness-skill-eval-kit-regression-core` 的 P0 主轴。
2. `project-lifecycle-hook-skill-toolkit-contract`
   - 作为 P1 独立 feature 完成 project-level hook contract 与 manual toolkit。
3. `qa-evo-deep-evidence-bound-ac-aware-closure`
   - 作为 QA evo-deep 后续补强 feature，完成 evidence-bound / AC-aware closure。

已冻结、待实现：

4. `implement-mode-human-playbooks-and-routing-contract`

仍保留为 backlog / research input：

5. `ralph-task-loop-checkpoint-recovery-contract`
6. `learn-context-to-project-skill-lifecycle-injection`

剩余 backlog 必须后续进入 `change/refreeze`、`prd`、`user-story`、`test-case` 后才能成为 frozen truth。

发布后推荐方向收敛为：

```text
Completed: qa-evo-deep + Skill Eval Kit / project lifecycle hooks / QA evo-deep evidence closure
Frozen next P1: implement mode playbooks
Later P1/P2: Ralph Task Loop / learn context-to-project-skill lifecycle injection
```

## CEO Review Challenge

`v1.4.10` research 包曾存在明显过载风险：五条候选方向都合理，但不能同时作为 P0 冻结和实现目标。

CEO review 建议将本版本 promise 收窄为一个可验收主轴：

> 让 Beacon 的“验收与人类面 skill 演进”变得可审计、可回归、可路由，而不是一次性补齐所有自动化执行能力。

实际已采纳的 P0 收口：

1. `qa-evo-deep-and-skill-eval-kit-v1410`
2. `qa-evo-deep-evidence-bound-ac-aware-closure`

实际已采纳的 P1 / 后置处理：

- `project-lifecycle-hook-skill-toolkit-contract`：已做 project-level Markdown hook contract + manual toolkit，不做自动触发。
- `implement-mode-human-playbooks-and-routing-contract`：保留 `beacon-implement` 唯一入口，只补 single / team / ralph mode playbook 和路由评测，推荐作为下一条独立 refreeze feature。
- `ralph-task-loop-checkpoint-recovery-contract`：先作为后续长任务控制 research，不进入同版 P0。
- `learn-context-to-project-skill-lifecycle-injection`：先只冻结 learning influence / candidate skill admission，不做自动注入。

因此后续 `change-refreeze` 不应把 Ralph、learn、implement mode 与已发布 QA / Skill Eval 主轴写成同等 P0。

## 当前需求包

- Research
  - `docs/beacon/v1.4.10/research/qa-evo-deep-and-skill-eval-kit-evolution.md`
  - `docs/beacon/v1.4.10/research/project-lifecycle-hook-skill-toolkit-contract.md`
  - `docs/beacon/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`
- Frozen / delivered feature packages
  - `docs/beacon/v1.4.10/change/qa-evo-deep-and-skill-eval-kit-v1410.md`
  - `docs/beacon/v1.4.10/change/project-lifecycle-hook-skill-toolkit-contract.md`
  - `docs/beacon/v1.4.10/change/qa-evo-deep-evidence-bound-ac-aware-closure.md`
  - `docs/beacon/v1.4.10/prd/`
  - `docs/beacon/v1.4.10/user-story/`
  - `docs/beacon/v1.4.10/qa/test-cases/`
  - `docs/beacon/v1.4.10/release/checklist-v1.4.10.md`
- Frozen / pending implementation
  - `docs/beacon/v1.4.10/change/implement-mode-human-playbooks-and-routing-contract.md`
  - `docs/beacon/v1.4.10/change/implement-mode-human-playbooks-and-routing-contract.refreeze-summary.md`
  - `docs/beacon/v1.4.10/prd/implement-mode-human-playbooks-and-routing-contract.md`
  - `docs/beacon/v1.4.10/user-story/implement-mode-human-playbooks-and-routing-contract.md`
  - `docs/beacon/v1.4.10/qa/test-cases/implement-mode-human-playbooks-and-routing-contract.md`

## 继承边界

本版本继承 v1.4.9 的 Markdown-first 和只读 support 写入拓扑：

- 普通 support review upsert 到 `docs/beacon/<version>/research/<feature>.md`。
- `beacon-deep` 详细材料进入 `docs/beacon/<version>/deep/<feature>/`，research 只保留索引。
- `beacon-learn` 进入 `docs/beacon/<version>/learning/<feature>.md` 或 transaction，research 只记录 learning influence 摘要。
- 显式 version + feature 的只读分析不得回退到 `docs/brainstorms/`。
- 机器面只保存运行证据、索引、trace、eval result，不作为 requirement truth。

## 当前不包括 / 仍未闭环

- 不新增主生命周期 stage。
- 不让 `qa-evo-deep`、`source-driven`、`learn` 或 skill eval 自动成为 gate verdict。
- 不让项目级 hook 成为新的 Beacon lifecycle stage。
- 不把 single / team / ralph 拆成三个新的 public implement skill。
- 不把 `.machine` 或 `.beacon/state` 评测结果当作需求真相。
- 不在已发布范围内实现 Ralph Task Loop checkpoint/recovery controller。
- 不在已发布范围内实现 learn context-to-project-skill lifecycle injection。
- 不把 implement mode playbook 写成新的 public skill；当前冻结范围只允许在 `beacon-implement` 下补 playbook、route explanation 和 eval cases。

## 下一步

推荐下一跳：

```bash
beacon implement "implement-mode-human-playbooks-and-routing-contract" --project . --version v1.4.10
```

实现时应继续遵守已冻结方向：保留 `beacon-implement` 唯一 public skill，只补 single / team / ralph mode playbook、help/status 解释和 Skill Eval route stability，不把 Ralph Task Loop 或 learn skill injection 并入同一 feature。
