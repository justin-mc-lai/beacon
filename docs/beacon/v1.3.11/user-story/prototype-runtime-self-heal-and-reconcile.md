# User Story: prototype-runtime-self-heal-and-reconcile

## Story Boundary

- version: `v1.3.11`
- feature: `prototype-runtime-self-heal-and-reconcile`
- status: `draft`
- upstream_prd: `docs/beacon/v1.3.11/prd/prototype-runtime-self-heal-and-reconcile.md`
- related_prd:
  - `docs/beacon/v1.3.11/prd/prototype-design-intelligence-and-governed-rendering-separation.md`
  - `docs/beacon/v1.3.11/prd/beacon-execution-runtime-kernel.md`
- current_revision: `R1`
- source_revision: `R1`

本故事线覆盖 Beacon 在 `v1.3.11` 中把 prototype runtime 从“create 后人工 patch 再 freeze”的脆弱链路，收口为正式的 canonical truth、reconcile、nondestructive refresh 与 drift repair contract。它冻结的是原型运行时 repair 模型，不是页面视觉改版。

## Story 1: prototype 必须只有一个 canonical truth source

作为 Beacon prototype maintainer，我希望 runtime 对 prototype bundle 只有一个正式真相源，这样 review、freeze、status 就不会再各自读取不同文件导致漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | canonical-truth-source | prototype runtime 明确单一 canonical truth source，`prototype-plan / manifest / canonical-envelope / freeze` 都只允许从该真相单向投影。 |
| AC-002 | no-multi-truth-read | `review / freeze / status / gate` 不得再各自选择不同 sink 作为真相源。 |
| AC-003 | sink-drift-detection | 当 `plan / manifest / canonical-envelope / freeze` 任一 sink 与 canonical truth 不一致时，系统必须标记 drift。 |
| AC-004 | truth-traceability | canonical truth 与各 sink 都保留 `feature / version / source_hash / transaction_id-or-equivalent` 追溯字段。 |

## Story 2: prototype 必须提供正式 reconcile surface

作为 Beacon requirement owner，我希望 prototype 有正式 reconcile surface，把 canonical truth 重投影回 machine sinks，这样不再需要手工 patch 多个 JSON 才能恢复 bundle。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | reconcile-surface | Beacon 提供正式 `prototype reconcile` 或等价内部 surface。 |
| AC-102 | sink-reprojection | reconcile 至少能重投影 `prototype-plan.json / manifest.json / canonical-envelope.json / freeze metadata`。 |
| AC-103 | fingerprint-refresh | reconcile 会同步更新 `source_fingerprints / sink fingerprints / transaction headers`。 |
| AC-104 | no-requirement-writeback | reconcile 只修复 prototype bundle，不反向改写 `prd / user-story / test-case`。 |

## Story 3: nondestructive refresh 必须保护 human narrowing

作为真实项目 operator，我希望 bundle refresh 默认不覆盖已经收窄的人类页面与 production-visible copy，这样 prototype repair 不会把交付内容刷回旧骨架。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | pages-protected | nondestructive refresh 默认不覆盖 `pages/*.md`。 |
| AC-202 | preview-protected | nondestructive refresh 默认不覆盖已有 `preview.html / preview-dark.html`。 |
| AC-203 | production-copy-protected | 已冻结的 production-visible copy 不得被 machine repair 默认改写。 |
| AC-204 | machine-sink-only | nondestructive refresh 只更新结构化 machine sink 与必要 metadata。 |

## Story 4: freeze 必须先分类 drift，再决定 repair 还是 recreate

作为 Beacon runtime operator，我希望 freeze 不再把所有 bundle 问题都简化成“regenerate and review before freeze”，而是先判断 drift 类型，再走正式 repair path。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | drift-types | 系统至少区分 `source-drift / metadata-only-drift / sink-drift / transaction-header-drift / canonical-truth-missing / destructive-recreate-required`。 |
| AC-302 | repair-first | 当 drift 属于 `metadata-only-drift` 或 `transaction-header-drift` 时，freeze 必须先走 repair/reconcile，再继续 freeze。 |
| AC-303 | reprojection-before-review | 当 drift 属于 `sink-drift` 时，系统先重投影 machine sink，再重跑 review。 |
| AC-304 | recreate-explicit | 仅当属于 `destructive-recreate-required` 时，系统才允许 operator 重新 create，并明确说明覆盖范围。 |

## Story 5: reason code、diagnosis、repair path 必须跨 surface 共享

作为 Beacon governance owner，我希望 prototype drift 的异常语义在 review、freeze、status、gate、implement-readiness、real-project-validation 之间保持一致，这样不会再出现同一 bundle 不同入口给出不同判断。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | shared-reason-codes | `review / freeze / status / gate / implement-readiness / real-project-validation` 共享同一套 prototype drift `reason_code`。 |
| AC-402 | shared-diagnosis | 对同一 drift，相关 surface 返回一致 `diagnosis / next_action / repair_path`。 |
| AC-403 | no-surface-local-drift-copy | 不允许不同 surface 各自产生一套 prototype drift 解释话术。 |
| AC-404 | audit-ready | reason code 命中结果可进入 audit / board / status read model，作为正式机器证据。 |

## Story 6: runtime 必须消除 host LLM repair friction

作为 Beacon 使用者，我希望 prototype bundle 进入可修复 drift 状态时，runtime 直接给出正式动作，而不是逼 host LLM 输出“先不要重跑 create、先补几个字段”的人工分析。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | host-friction-elimination | 对可 repair drift，runtime 必须直接返回正式 repair action，而不是依赖 host 生成分析型操作建议。 |
| AC-502 | no-manual-json-playbook | runtime 不再把手工 patch `plan / manifest / canonical-envelope / transaction header` 作为默认操作路径。 |
| AC-503 | executable-next-action | 对每种 drift，next action 必须可直接映射到 `reconcile / repair / review / freeze / recreate` 之一。 |
| AC-504 | real-project-closure | 在真实项目 prototype refresh 中，可 repair drift 能通过正式 runtime 闭环收口，不需要额外人工经验。 |

## Delivery Notes

- 本故事线是 `prototype-design-intelligence-and-governed-rendering-separation` 的 runtime 修复补线。
- 它同时依赖 `beacon-execution-runtime-kernel` 的 shared reason code 与 repair contract 思路。
- 下一阶段应从本 story 继续进入 test-case，把 canonical truth、reconcile、nondestructive refresh、freeze repair、shared reason code 全部编译为 AC matrix。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 8 |
| Status | draft-runtime-repair-r1 |
| Created | 2026-05-04 |
| Change Scope | canonical-truth-contract / reconcile-surface / nondestructive-refresh / freeze-drift-classification / shared-reason-codes / host-friction-elimination |
