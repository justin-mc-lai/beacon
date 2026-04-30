# Beacon v1.3.9 总览

## 版本状态

- `v1.3.9` 是建立在已发布 `v1.3.8` runtime 之上的并行演进线。
- 当前版本不是单一需求闭环，而是 4 条并行冻结子线共同收口。
- 本版本主题是：`execution 收敛 + agents 健壮性 + skill admission 兼容性 + friction 治理闭环`。

## 版本目标

`v1.3.9` 聚焦解决 Beacon 在实现后半程暴露出的四类问题：

1. execution 目录模板文件过多，machine truth 与 human projection 不够收敛
2. agents 能力缺少显式 requirement truth，Codex / Claude runtime 兼容性不足
3. 第三方 skill 接入缺少 host runtime 可验证的 admission 机制
4. 项目摩擦、阻塞、bug、优化建议缺少统一 intake 入口与可治理队列

## 当前需求包

- PRD
  - `docs/beacon/v1.3.9/prd/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
  - `docs/beacon/v1.3.9/prd/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
  - `docs/beacon/v1.3.9/prd/beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
  - `docs/beacon/v1.3.9/prd/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- User Story
  - `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
  - `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
  - `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
  - `docs/beacon/v1.3.9/user-story/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`
- Test Cases
  - `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
  - `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
  - `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
  - `docs/beacon/v1.3.9/qa/test-cases/beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`

## 正式子线

- `beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write`
- `beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility`
- `beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility`
- `beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue`

## 冻结状态

- `Beacon v1.3.9 execution projection convergence and QA acceptance dual-write`: `frozen`
- `Beacon v1.3.9 agents robustness and host runtime compatibility`: `frozen`
- `Beacon v1.3.9 runtime skill admission and host-validated third-party skill compatibility`: `frozen`
- `Beacon v1.3.9 beacon-friction-intake and sqlite governance queue`: `frozen`

## 已完成闭环

- `execution projection convergence and qa acceptance dual-write`
  - 已形成 QA acceptance 双写闭环，收敛 execution human/machine 交付边界。
- `agents robustness and host runtime compatibility`
  - 已形成 Codex / Claude host runtime 兼容增强主线与验收闭环。
- `runtime skill admission and host-validated third-party skill compatibility`
  - 已形成第三方 skill admission / validation 主线与实现、QA 闭环。
- `beacon-friction-intake and sqlite governance queue`
  - 已把旧 `memory-friction-evolution` 主语义升级为 `beacon-friction-intake`，支持 `scan/capture` 双入口、全局 sqlite 治理队列与显式 accept 路由。

## 关键验收锚点

- `docs/beacon/v1.3.9/execution/qa-acceptance-beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write.md`
- `docs/beacon/v1.3.9/execution/qa-acceptance-beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility.md`
- `docs/beacon/v1.3.9/execution/qa-acceptance-beacon-v1.3.9-runtime-skill-admission-and-host-validated-third-party-skill-compatibility.md`
- `docs/beacon/v1.3.9/execution/qa-acceptance-beacon-v1.3.9-beacon-friction-intake-and-sqlite-governance-queue.md`

## 版本主题图

```text
execution projection convergence
-> qa acceptance dual-write
-> release / gate / support truth convergence
-> agents robustness
-> codex / claude host runtime compatibility
-> runtime skill admission
-> host-validated third-party skill compatibility
-> beacon-friction-intake
-> sqlite-backed governance queue
```
