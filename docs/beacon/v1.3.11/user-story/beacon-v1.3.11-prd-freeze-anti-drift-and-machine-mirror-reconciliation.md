# User Story: Beacon v1.3.11 PRD freeze anti-drift and machine-mirror reconciliation

## Story Boundary

- version: `v1.3.11`
- feature: `beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation`
- status: `change_open`
- upstream_change: `docs/beacon/v1.3.11/change/beacon-v1.3.11-prd-freeze-anti-drift-and-machine-mirror-reconciliation.md`
- upstream_prd: `docs/beacon/v1.3.11/prd/beacon-v1-3-11-orchestration-runtime-and-long-running-execution-governance.md`

本故事线只覆盖 `PRD freeze anti-drift` 与 `machine mirror reconciliation` 的 requirement change 闭环，不扩展成新的一级公开命令，也不把 `doctor` repair surface 直接等同于正常 change path。

## Story 1: PRD Reconcile 必须成为正式 requirement surface

作为 Beacon requirement owner，我希望当 `PRD markdown` 已经发生正式修订时，系统能提供确定性的 `reconcile` 语义，把当前 human truth 重投影到 machine mirror，而不是依赖一次性脚本或人工 patch JSON。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | authoritative-markdown | 当人类明确编辑 `docs/beacon/<version>/prd/*.md` 后，Beacon 能把当前 markdown 视为可重投影的 authoritative truth，而不是强制要求重新从 skeleton 生成。 |
| AC-002 | reconcile-sinks | `prd reconcile` 或等价正式 surface 会同步更新至少三类 sink：`docs/beacon/<version>/prd/*.md`、`docs/beacon/<version>/.machine/prd/` 下的 canonical/compile 文件、以及 `.beacon/prd/*.json`。 |
| AC-003 | deterministic-projection | 同一份 markdown 在未变化时重复 reconcile，生成的 `source_hash / projection_seq / sink_checksums` 结果必须稳定可解释。 |
| AC-004 | no-manual-json-patch | 正常闭环下，操作者不需要手工 patch machine JSON 才能让 PRD 重回 audit-pass 状态。 |

## Story 2: PRD Audit 必须从 legacy compare 扩展成 full mirror audit

作为 Beacon 维护者，我希望 `audit` 不只检查 human markdown 与 `.beacon/prd` 的 legacy 对比，而是能覆盖 canonical/compile mirror，这样 freeze 漂移不会被半套审计掩盖。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | audit-legacy-and-machine | `prd audit` 至少同时检查 `docs/beacon/<version>/prd/*.md`、`.beacon/prd/*.json`、`docs/beacon/<version>/.machine/prd/*.canonical.json`、`docs/beacon/<version>/.machine/prd/*.compile.json`。 |
| AC-102 | mismatch-localization | 当任一 sink 漂移时，audit 输出必须指出是哪一类 sink 失配，而不是只给出笼统的 drift 结论。 |
| AC-103 | contract-vs-mirror-split | audit 输出必须能区分“markdown contract 无效”和“markdown contract 有效但 machine mirror stale”这两类问题。 |
| AC-104 | freeze-gate-usable | audit 结果必须能直接被后续 freeze / gate / doctor verify-materials 消费，而不是只作为一次性调试信息。 |

## Story 3: Transaction History 必须表达 latest pointer 与 supersedes 语义

作为 Beacon runtime owner，我希望 PRD transaction 历史不只是不断追加 json 文件，还要明确谁是当前最新冻结结果，这样多次 revise/reconcile 后不会再出现“多个 applied transaction 并存但没人知道该信哪一个”。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | latest-transaction-pointer | PRD transaction 面必须存在可确定解析的 latest pointer，能够指向当前 active transaction。 |
| AC-202 | supersedes-link | 新 transaction 生成后，系统能表达其与前一 transaction 的 supersedes 关系，而不是只靠时间排序猜测。 |
| AC-203 | revision-readable | 人类和 machine surface 都能判断某一 transaction 是 `pending / applied / superseded / stale` 中的哪一种。 |
| AC-204 | stale-history-safe | 历史 transaction 允许保留，但不得继续被 audit / doctor / release 错认成当前 truth。 |

## Story 4: Change Loop 必须能识别 stale mirror，而不是只看 doc freeze 状态

作为 post-freeze change operator，我希望 `beacon-change / reopen / freeze / material audit` 能识别“human docs 已变更，但 machine mirror 仍旧旧版本”的状态，并把它路由到 reconcile 或 repair，而不是误判为已经 freeze 完整。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | stale-mirror-detection | change-loop 至少能识别 `markdown_changed_but_machine_stale` 这一类 requirement package 状态。 |
| AC-302 | change-route-clarity | 当识别到 stale mirror 时，系统推荐动作必须明确指向 `beacon-change` 内的 reconcile/repair 路径，而不是继续放行 implement / qa / release。 |
| AC-303 | fail-closed | 对于已识别的 stale mirror，`freeze`、`implement`、`qa`、`release` 必须 fail-closed，而不是带着旧 machine truth 继续前进。 |
| AC-304 | status-help-surface | `status / help / doctor advise` 这类 support surface 必须能把 stale mirror 原因明确投影给操作者。 |

## Story 5: Repair Path 必须与正常 Reconcile Path 边界清晰

作为 Beacon 操作者，我希望系统清楚区分“正常 requirement refresh 后的 reconcile”与“材料损坏后的 doctor repair fallback”，这样不会把 repair surface 误当成常规 requirement path。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | reconcile-vs-repair | 系统明确区分正常 `reconcile` 与异常 `doctor sync-materials / repair-package` 的职责边界。 |
| AC-402 | doctor-fallback-only | `doctor` 相关 repair surface 仅在 machine sink 缺失、损坏或历史状态不可信时作为 fallback 推荐，而不是 PRD revise 后的默认下一步。 |
| AC-403 | recovery-instructions | 当进入 repair fallback 时，输出必须说明触发原因、恢复步骤、以及恢复后如何重新回到 change/freeze 主链。 |
| AC-404 | post-repair-reentry | repair 完成后，系统能重新回到可审计的 `validate -> audit -> freeze readiness` 路径，而不是停留在 repair-only 状态。 |

## Delivery Notes

- 本故事线是 `change-loop requirement refresh`，不是实现完成声明。
- 下一阶段应基于本 user-story 生成 test-case，随后再进入 `prd reconcile / extended audit / transaction pointer / stale mirror detection / doctor fallback` 的实现闭环。

## Metadata

| Field | Value |
| --- | --- |
| Priority | high |
| Story Points | 8 |
| Status | draft-change-open |
| Created | 2026-05-01 |
| Change Scope | prd / change-loop / machine-mirror / doctor-fallback |
