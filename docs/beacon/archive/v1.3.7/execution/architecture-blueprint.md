# Beacon v1.3.7 Architecture Blueprint

## Blueprint Goal

`v1.3.7` 是 Beacon 的 current runtime promotion 线，它在 `v1.3.6` host-native kernel 之上完成公开 runtime line 提升。

这条线做三件事：

1. 把 implementation delivery baseline envelope 提升为实现投影的唯一真相。
2. 把 `beacon-brainstorm` 纳入 Beacon 内置 sidecar，用于继续头暴、收敛缺口、支持后续演进思考，但不直接改写 frozen truth。
3. 把仓库公开 runtime line、技能包装、managed context、release docs 一起提升到 `v1.3.7`。

## Runtime Position

- runtime line: `v1.3.7`
- delivery docs line: `v1.3.7`
- canonical delivery tree: `docs/beacon/archive/v1.3.7/`

因此，`v1.3.7` 的职责是把当前公开 runtime 面、版本文档树、技能包装和 release/governance 证据统一到同一条 current release line。

## System Boundary

```text
docs/beacon/global-boundaries.md
-> docs/beacon/archive/v1.3.7/{prd,user-story,qa/test-cases,prototype,.machine}
-> canonical implementation delivery baseline envelope
-> projected implementation artifacts
-> implement / qa / gate / release execution
-> release decision and acceptance evidence

beacon-brainstorm
-> reads frozen truth and version materials
-> writes standalone brainstorming markdown
-> feeds change / clarification / future evolution decisions
-> must not overwrite frozen truth directly
```

- `docs/beacon/global-boundaries.md` 提供全局约束。
- `docs/beacon/archive/v1.3.7/` 提供这条线的正式 requirement truth 与 execution evidence。
- canonical baseline envelope 是 implementation projection 的唯一源。
- gate 校验的是 projection 与 canonical 的一致性，而不是多个文档彼此“对表”。
- `beacon-brainstorm` 是读真相、产思考、促收敛的 sidecar，不进入主生命周期真相链。

## Layered Architecture

### 1. Frozen Truth Layer

这一层定义“需求冻结后的正式真相”：

- `prd/`
- `user-story/`
- `qa/test-cases/`
- `prototype/`
- `.machine/` 中由正式物料投影出的机器侧 requirement artifacts

职责：

- 提供 feature scope、acceptance criteria、test intent、freeze boundary。
- 为 implement / qa / release 提供可追溯的 requirement baseline。
- 明确什么属于 requirement change，什么只是 implementation clarification。

### 2. Canonical Baseline Layer

这一层定义实现交付的唯一投影源，而不是又一份平行真相。

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.3.7-beacon-v1.3.7-beacon-brainstorm-built-in-convergence-and-evolution-thinking-R1`
- transaction_id: `tx-c6f061f467aedd1fe`
- source_hash: `sha256:0248ff09f1b95295914f152b2460ae7928cd5dbc296c48398a2c63cfda69e6bf`
- projection_seq: `1`
- version: `v1.3.7`
- feature: `Beacon v1.3.7 beacon-brainstorm built-in convergence and evolution thinking`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.3.7`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:END -->

职责：

- 固定 delivery scope、branch/worktree strategy、projection metadata。
- 为 deterministic implementation contract、git workflow contract、implementation plan 提供单向投影源。
- 让 gate 可以校验“projection 是否偏离 canonical”，而不是让 projection 之间彼此兜底。

### 3. Projection Layer

这一层包含从 canonical baseline 单向投影出的实现文档与机器工件：

- `deterministic-implementation-contract-*.md/.json`
- `git-workflow-*.md/.json`
- `implementation-plan-*.md/.json`
- `implementation-summary-*.md/.json`
- `technical-implementation-*.md/.json`

职责：

- 把 canonical baseline 转成不同执行视角可消费的文档。
- 保持 metadata 对齐：`baseline_id`、`transaction_id`、`source_hash`、`projection_seq`。
- 一旦 metadata 漂移，必须阻断并回到 canonical 修复。

### 4. Execution Layer

这一层是实际交付执行面：

- `implement`
- `qa`
- `gate`
- `release`

职责：

- `implement` 只能对照 frozen requirement truth 做实现，不得隐式修改 PRD / user-story / test-case。
- 当 prompt 指向新增需求、用户故事扩充或 acceptance 变化时，必须改走 `change` / refreeze 路径。
- `qa` 依据 feature-specific matrix 与 execution evidence 验证实现，不以口头对齐代替证据。
- `release` 基于 gate、qa、change docs、evidence manifest 做最终 readiness 判断。

### 5. Verification And Release Governance Layer

这一层负责“是否闭环”的判断：

- `docs/beacon/archive/v1.3.7/SUMMARY.md`
- `docs/beacon/archive/v1.3.7/execution/boundaries.md`
- `docs/beacon/archive/v1.3.7/release/v1.3.7.md`
- `.beacon/gate-report.json`
- `.beacon/evidence-manifest.json`
- `docs/beacon/archive/v1.3.7/.machine/execution/terminal.json`

职责：

- 确认 feature execution 已经通过 plan -> implement -> qa -> release check。
- 确认 change docs、machine payload、evidence manifest、gate report 互相可追溯。
- 明确这条线同时是“delivery release line”和“public runtime release line”。

### 6. Brainstorm Sidecar Layer

这一层由 `beacon-brainstorm` 负责。

职责：

- 基于版本文档继续头暴、补齐缺口、做演进思考。
- 使用第一性原理、苏格拉底提问、奥卡姆剃刀追根溯源、剔除冗余。
- 产出 markdown 型分析结论，供 requirement clarification、change decision、future evolution 使用。

硬边界：

- 不改写 frozen PRD / user-story / test-case。
- 不作为 release truth。
- 不绕过 canonical baseline 和主链 gate。

## End-To-End Flow

```text
frozen requirement truth
-> canonical implementation delivery baseline envelope
-> projected implementation contracts and plan
-> implement execution against frozen truth
-> qa evidence and acceptance closure
-> release gate and release decision

brainstorm sidecar
-> reads the same version truth
-> outputs convergence/evolution notes
-> routes to clarify/change when truth must move
```

## Anti-Drift Contract

1. frozen requirement truth is authoritative once accepted.
2. canonical implementation delivery baseline envelope is the only implementation projection truth.
3. projection docs are disposable views; canonical metadata drift is a blocking defect.
4. gate validates projection-to-canonical consistency, not projection-to-projection consensus.
5. brainstorm output is advisory only; if truth changes, reopen through formal change flow.
6. `v1.3.7` docs, package truth, managed context, and public runtime surface must converge to the same release line.

## Out Of Scope

- 把 `beacon-brainstorm` 升格为新的主生命周期 stage。
- 允许 implement 根据提示词直接改写已冻结 requirement truth。
- 允许 architecture blueprint、implementation plan、git workflow contract 各自独立成为真相。
- 允许 implement 根据提示词绕过 promoted runtime contract 直接改写 frozen truth。
