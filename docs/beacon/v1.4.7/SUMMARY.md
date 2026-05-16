# Beacon v1.4.7 总览

## 版本状态

- `v1.4.7` 当前主题是：`meta-protocol hardening and horizontal engineering support surfaces`
- 当前版本状态：`current_runtime_release`
- 当前版本已经是 runtime release line；当前 runtime/default docs 已切到 `v1.4.7`
- `v1.4.7` 站在 `v1.4.6` 的 anti-drift contract 基线上，继续增强 Beacon 的公共入口协议、support skill 宽度与人类可读性，并把这些能力收成新的 active runtime context

## 版本目标

`v1.4.7` 聚焦一条主线：

> 在不削弱 Beacon truth / evidence / gate kernel 的前提下，把 Beacon 主 skill 收敛成更明确的元协议，补齐第一批横向工程 support skills 与轻量 references，让 Beacon 更像一个完整的工程 operating kit，而不是只像强治理内核。

## 当前需求包

- Research
  - `docs/beacon/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`
- PRD
  - `docs/beacon/v1.4.7/prd/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
  - `docs/beacon/v1.4.7/prd/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
  - `docs/beacon/v1.4.7/prd/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- User Story
  - `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
  - `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
  - `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- Test Cases
  - `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
  - `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
  - `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- Change
  - `docs/beacon/v1.4.7/change/v1.4.7.md`
  - `docs/beacon/v1.4.7/change/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
  - `docs/beacon/v1.4.7/change/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
  - `docs/beacon/v1.4.7/change/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- Release
  - `docs/beacon/v1.4.7/release/v1.4.7.md`
  - `docs/beacon/v1.4.7/release/checklist-v1.4.7.md`

## 正式子线

- `beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces`
- `beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract`

## 新增规划子线

- `beacon-v1.4.7-bounded-automation-closure-state-kernel`
  - 当前状态：`promoted-to-runtime-release`
  - 目标：把 automation 从 QA feedback helper 推进到 bounded closure-state runtime kernel
  - 边界：只做 `closure-state envelope + active issue register + QA/implement bounded loop + queue safety primitives`
  - 明确不承诺：`deep/refreeze/release` end-to-end automation 或 full autonomous closure-loop
  - 当前需求链：
    - `prd` 已冻结
    - `user-story` 已冻结
    - `test-case` 已冻结
    - `change` 已接入
    - `qa` 已完成 planning-line 验收
    - `release` 尚未接入

- `beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract`
  - 当前状态：`promoted-to-runtime-release`
  - 目标：把 automation 的 support-review / truth-refreeze / scenario-discovery / promotion-proof 缺口正式收成 runtime-facing second slice
  - 边界：只做 route / block / proof contract，不做自动 deep、自动 refreeze、自动 truth 写入
  - 当前需求链：
    - `prd` 已冻结
    - `user-story` 已冻结
    - `test-case` 已冻结
    - `change` 已接入
    - `qa` 尚未开始

## First Slice Freeze

`v1.4.7` 当前先正式冻结 first slice：

1. `skills/beacon/SKILL.md` 收敛成 meta-protocol
2. `skills/beacon/using-beacon/SKILL.md` 收敛成 host route constitution
3. 引入首批三条横向工程 support skills
   - `beacon-context-engineering`
   - `beacon-source-driven`
   - `beacon-doubt-review`
4. 补齐服务上述入口和路由判断的第一批 lightweight references

研究中其余 support skill 家族与 packaging 扩展保留为同主题 roadmap，不计入 first-slice 交付闭环。

## Next Slice

`v1.4.7` 当前下一轮已收紧到 second slice：

1. `beacon-security-review`
2. `beacon-performance-review`
3. `beacon-documentation-adr`
4. `beacon-debug-recovery`
5. `research-closure-checklist.md`
6. `business-flow-checklist.md`
7. `state-machine-checklist.md`

这一轮仍属于 support-surface 与 reference-layer 增强，不涉及 runtime promotion。

## 当前边界判断

- `v1.4.7` 不新增公开一级主命令，也不新增新的公开 lifecycle stage。
- `beacon` 主 skill 要更像元协议，而不是 wrapper/manual/version note 的混合体。
- `using-beacon` 要成为更稳定的 host-native route constitution，明确 truth、execution、verification、gate、support 的分工与回路。
- 新增横向工程 skill 只能是 support surface，不得成为 truth source、gate source 或新的 stage。
- lightweight references 只做人类判断支架，不得成为 canonical truth，也不得反向驱动 machine truth。
- `agent-skills` 与 `gstack` 只作为研究与映射输入；Beacon 吸收它们的 anatomy、discipline、specialist packaging 与 host readability，但不引入外部仓库为运行时依赖。
- 当前版本已经提升为 active docs/runtime line，但仍需保持 `v1.4.6` 项目上的向后兼容读取能力。
- automation 方向当前只允许推进 bounded runtime kernel；不允许把 research north-star 误写成近线产品承诺。

## 与 v1.4.6 的关系

`v1.4.6` 已经冻结：

- anti-drift skill contracts
- support-surface constitution
- implementation-first reconciliation governance
- project-local automation feedback loop

`v1.4.7` 继续往前推进的不是更强的 gate，而是更好的入口组织与工程可用宽度：

```text
anti-drift contract exists
-> mainline and support boundaries are already sharper
-> main beacon wrapper still carries too much mixed responsibility
-> host route readability is still not crisp enough
-> horizontal engineering support family is still too thin
-> human-readable references are still not enough
```

## 关键验收锚点

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.6/SUMMARY.md`
- `docs/beacon/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`
- `docs/beacon/v1.4.7/prd/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
- `docs/beacon/v1.4.7/prd/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
- `docs/beacon/v1.4.7/prd/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
- `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
- `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-meta-protocol-and-horizontal-engineering-support-surfaces.md`
- `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-bounded-automation-closure-state-kernel.md`
- `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-automation-support-review-truth-refreeze-and-promotion-contract.md`
- `docs/beacon/v1.4.7/qa/acceptance-summary.md`

## 当前 QA 状态

- `v1.4.7` 已完成已接受 slices 的 runtime-promotion QA
- 当前 QA verdict：`pass_for_runtime_release`
- 已验证范围：
  - main `beacon` meta-protocol
  - `using-beacon` host route constitution
  - first-wave support skills
  - first-wave lightweight references
  - second-wave support skills
  - second-wave lightweight references
  - `prd / implement / qa / release` 对 lightweight references 的显式消费接线
  - bounded automation closure-state kernel
  - active issue register inheritance
  - queue revision / stale-writer rejection
  - feature execution lease / single-flight
- 当前不代表：
  - 全量 roadmap closure
  - autonomous `deep/refreeze/release` 闭环
  - 所有真实项目都已 release-ready

## 当前 Release 状态

- `v1.4.7` 已补齐 runtime release materials
- 当前 release verdict：`current_runtime_release`
- 当前 promotion decision：`approved`
- active runtime/docs line 已切换为：`v1.4.7`

## 外部映射定位

- `agent-skills` 更像 engineering skill library
- `gstack` 更像 specialist software factory
- Beacon 仍定位为 truth / evidence / governance kernel

`v1.4.7` 的目标不是复制它们，而是吸收它们的强项后，让 Beacon 的入口协议、support family 与 operator readability 更完整。
