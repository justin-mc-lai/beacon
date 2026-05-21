# PRD: Beacon v1.4.8 物料强 Gate 与人类面子 Skill 原子写回契约

**Feature**: `beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract`
**Version**: `v1.4.8`
**Date**: `2026-05-21`
**Status**: `frozen`
**Track**: `material-gate-hardening + human-subskill-atomic-writeback + fail-closed-governance`
**Scenario**: `beacon_must_not_continue_when_required_materials_or_skill_writebacks_are_missing`

## Context

- Global boundaries:
  - `docs/beacon/global-boundaries.md`
- Research closure:
  - `docs/beacon/v1.4.8/research/beacon-v1.4.8-execution-material-rigor-and-version-governance-analysis.md`
  - `docs/beacon/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`
  - `docs/beacon/v1.4.8/research/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- Source architecture:
  - `docs/beacon/v1.4.8/source-architecture/index.md`
- Runtime surfaces under study:
  - `beacon/utils/change_refreeze.py`
  - `beacon/utils/requirement_clarity.py`
  - `beacon/utils/artifact_update_obligations.py`
  - `beacon/utils/docs_structure_contract.py`
  - `beacon/utils/technical_review_contract.py`
  - `beacon/utils/implementation_plan.py`
  - `beacon/utils/branch_governance.py`
  - `beacon/commands/implement.py`
  - `beacon/commands/gate.py`
  - `beacon/commands/review.py`

## 1. 问题

Beacon 已经具备多处材料门禁能力，但 `v1.4.8` 调研确认当前仍存在两个不能继续容忍的缺口：

1. execution host truth 可能退化为碎片化 side dossiers，缺少固定 host 文件、固定字段和固定阻断规则。
2. 人类面子 skill 可能只产出 advisory output，而没有明确更新材料、打开 obligation 或 route back，导致下游执行继续 fail open。

本 feature 要冻结一个更强的契约：

> 任何进入主链的 Beacon 操作，都必须能证明它依赖的 Beacon 材料存在、字段显式、来源可审计，并且每个人类面 skill 调用都有闭合 material effect。

### 1.1 问题细分

### 1.1.1 execution host contract 可能退化

真实项目证据显示，旧版本中 `architecture-blueprint.md` 曾承载 delivery host 信息，但新版本可能只生成分散的 branch / revision dossiers。

这会导致：

- `execution/index.md` 缺失但流程继续
- `architecture-blueprint.md` 缺失或缺少 host section
- branch / service / worktree 事实只在 side document 中出现
- automation 和人类都无法依赖一个稳定的 execution host

### 1.1.2 默认 seed 被误当成冻结事实

当前实现中，部分 delivery-critical facts 可以由默认值或配置 seed：

- `target_branch`
- `service_directories`
- `writable_services`
- `worktree_root`
- `use_git_worktree`

这些默认值能让文件“看起来完整”，但不能证明事实真实。

### 1.1.3 support skill finding 没有统一采纳契约

`beacon-ceo-review`、`beacon-doubt-review`、`beacon-security-review`、`beacon-performance-review`、`beacon-source-driven` 等 support surfaces 可以发现重要问题。

但如果 finding 被接受后没有转成：

- truth update
- execution host update
- evidence update
- release blocker
- `artifact_update_obligation`

那它只是建议，不是闭环。

### 1.1.4 toolkit skill 改变项目事实时缺少原子写回边界

例如 `beacon-toolkit-branch-governance` 如果被用来更新交付服务、目标分支或 worktree 模式，就不能只输出 show / verify。

它必须写入 canonical surfaces：

- `git-workflow-<feature>.md/json`
- `technical-review-contract-<feature>.md/json`
- `architecture-blueprint.md`
- `service-slice-map.md`
- metadata contract

## 2. 目标

1. 冻结 execution host required surface contract。
2. 冻结 branch / service / worktree explicit-fact gate。
3. 冻结 per-subskill material effect registry。
4. 冻结 support finding adoption contract。
5. 冻结 branch governance canonical writeback contract。
6. 冻结 open `artifact_update_obligations` 阻断规则。
7. 冻结 no silent default seed rule。
8. 让 `implement / QA / release` 在缺失材料、默认 seed、open obligations 或 evidence gap 存在时 fail closed。

## 3. 设计原则

### 3.1 Missing material 不等于 not needed

如果某个 surface 被触发、被声明相关或被下游 gate 依赖，那么对应材料缺失必须阻断。

### 3.2 Default seed 不等于 approved fact

默认值只能作为 draft seed，不能作为进入 implement 的冻结事实。

### 3.3 Support report 不等于 truth writeback

support surface 可以 challenge 和 route，但不能直接成为 canonical truth。accepted finding 必须被采纳进正式 material effect。

### 3.4 Side dossier 不等于 canonical execution host

per-feature dossier 可以作为补充，但不能替代 `execution/index.md`、`architecture-blueprint.md` 和受控 execution host projection。

### 3.5 每个 skill 调用必须有 material effect

每个人类面 skill 调用必须明确落到：

- `writeback_completed`
- `writeback_required`
- `obligation_opened`
- `truth_reopen_required`
- `execution_host_update_required`
- `evidence_update_required`
- `read_only_route_only`

### 3.6 Gate 必须消费材料状态

门禁不能只检查“是否有文件”，还要检查：

- 是否显式 reviewed / accepted
- 是否来自 canonical surface
- 是否存在 open obligation
- 是否存在 default-seeded critical fact
- 是否与 execution host drift

### 3.7 分层 / Layering

- requirement layer 负责 PRD、user-story、test-case、requirement clarity 和 freeze。
- execution host layer 负责 branch、service、worktree、delivery baseline、git workflow 和 technical review contract。
- support/toolkit layer 只能产生 material effect、route 或 obligation；不得直接替代 truth/gate layer。
- QA/release layer 只消费已冻结 truth、已实现代码和可审计 evidence。

## 4. 范围

### In scope

- execution host required file / section contract
- `service-slice-map.md` 对 multi-service / takeover 的 hard gate 候选
- branch / service / worktree explicit facts
- per-subskill material closure registry
- support finding adoption obligation
- `beacon-toolkit-branch-governance` writeback target set
- implement preflight fail-closed consumption
- QA / release 对 writeback obligations 和 evidence chain 的阻断
- material audit 对 missing / default-seeded / drifted facts 的检查

### Out of scope

- 自动执行 implementation
- 自动执行 QA / release
- 自动把 support surface 升级为 truth writer
- 自动将 advisory finding 写入 canonical truth
- 直接提升 `v1.4.8` 为 runtime release

## 5. 功能需求

### FR-001 Beacon 必须恢复 execution host required surface contract

对 execution-bound feature，Beacon 至少必须能要求和校验：

- `docs/beacon/<version>/execution/index.md`
- `docs/beacon/<version>/execution/architecture-blueprint.md`
- `docs/beacon/<version>/.machine/execution/implementation-delivery-baseline-<feature>.json`
- `docs/beacon/<version>/.machine/execution/git-workflow-<feature>.json`
- `docs/beacon/<version>/.machine/execution/technical-review-contract-<feature>.json`

### FR-002 Beacon 必须阻断缺失或漂移的 architecture blueprint projection

如果 `architecture-blueprint.md` 缺失、managed projection 缺失、或 projection drift，`implement` 必须 fail closed。

### FR-003 Beacon 必须冻结 branch / service / worktree explicit-fact gate

下列字段不能仅依赖默认 seed 解锁 implement：

- `target_branch`
- `service_directories`
- `writable_services`
- `direct_delivery_services`
- `use_git_worktree`
- `worktree_root`
- `worktree_path`
- per-service branch mapping

### FR-004 Beacon 必须识别 weak fact source

以下来源不得单独解锁 implement：

- `source=version_default`
- `source=project_config_seed`
- blank `approved_by`
- blank `reviewed_at`
- missing managed projection block

### FR-005 Beacon 必须冻结 per-subskill material effect registry

每个人类面子 skill 必须声明：

- `surface`
- `feature`
- `version`
- `material_effect`
- `target_artifacts`
- `truth_bindings`
- `accepted_route`
- `open_obligations`
- `fail_closed_gate`

### FR-006 Beacon 必须让 support finding 进入采纳契约

当 support finding 被接受时，必须转成以下之一：

- `change` update
- `prd` update
- `user-story` update
- `test-case` update
- `prototype` update
- `execution-host` update
- `technical-review-contract` update
- `git-workflow` update
- `qa-evidence` update
- `release-blocker` update
- `artifact_update_obligation`

### FR-007 Beacon 必须让 branch governance 更新走 canonical writeback

当 `beacon-toolkit-branch-governance` 被用于更新交付服务、目标分支或 worktree 时，必须写回或要求：

- `execution/git-workflow-<feature>.md`
- `.machine/execution/git-workflow-<feature>.json`
- `execution/technical-review-contract-<feature>.md`
- `.machine/execution/technical-review-contract-<feature>.json`
- `execution/architecture-blueprint.md`
- `execution/service-slice-map.md`
- canonical metadata contract

### FR-008 Beacon 必须阻断 open artifact update obligations

当 `artifact_update_obligations` 中存在 blocking open items 时：

- review quality 必须阻断
- QA 必须阻断
- release 必须阻断
- implement 是否允许继续必须由 obligation 类型显式决定

### FR-009 Beacon 必须提供 no silent pass diagnostics

当 gate 阻断时，输出必须说明：

- 缺哪个 material surface
- 哪个字段是 default-seeded
- 哪个 support finding 未采纳
- 哪个 obligation 仍 open
- 推荐回到哪个 Beacon surface 修复

### FR-010 Beacon 必须保持 support surface 边界

即便 support finding 被采纳，support surface 仍不得：

- 直接写 canonical truth
- 直接给 release verdict
- 直接绕过 `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze`

## 6. 冻结交付物

- `docs/beacon/v1.4.8/research/beacon-v1.4.8-execution-material-rigor-and-version-governance-analysis.md`
- `docs/beacon/v1.4.8/research/beacon-v1.4.8-human-subskill-material-closure-and-gate-contract.md`
- `docs/beacon/v1.4.8/research/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/v1.4.8/source-architecture/index.md`
- `docs/beacon/v1.4.8/change/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/v1.4.8/prd/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/v1.4.8/user-story/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`
- `docs/beacon/v1.4.8/qa/test-cases/beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract.md`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| runtime 代码未实现但文档已存在 | 后续误以为 release-ready | release checklist 明确保持 `blocked_pending_implementation_and_qa` |
| support finding 被误当成 truth | 冻结材料漂移或绕过 change/refreeze | accepted finding 必须进入 truth update、execution update、evidence update 或 blocking obligation |
| 默认 seed 被误当成 approved fact | implement 从错误 branch/service/worktree 开始 | explicit-fact gate 阻断 `version_default`、`project_config_seed` 和未 review 字段 |
| side dossier 替代 canonical execution host | 人类和 agent 找不到稳定事实来源 | execution host surface 必须绑定 `execution/index.md`、`architecture-blueprint.md` 和机器 projection |
| 子 skill 只输出建议不写回材料 | gate 无法消费 finding | 每次调用必须产出 material effect 和 target artifact |

## 8. 验收标准

- AC-001 Beacon defines a required execution host surface contract for execution-bound features, including `execution/index.md`, `execution/architecture-blueprint.md`, delivery baseline, git workflow, and technical review contract.
- AC-002 Beacon blocks `implement` when architecture blueprint projection is missing, drifted, or not bound to the canonical execution host.
- AC-003 Beacon treats branch / service / worktree facts as explicit frozen facts, not as acceptable silent defaults.
- AC-004 Beacon marks `source=version_default`, `source=project_config_seed`, blank `approved_by`, blank `reviewed_at`, or missing managed projection as weak fact sources that cannot unlock implementation by themselves.
- AC-005 Beacon provides a per-subskill material effect registry covering host, truth, execution, gate, support, toolkit, compatibility, and project-local skills.
- AC-006 Beacon requires every human-facing subskill invocation to resolve to `writeback_completed`, `writeback_required`, `obligation_opened`, `truth_reopen_required`, `execution_host_update_required`, `evidence_update_required`, or `read_only_route_only`.
- AC-007 Beacon converts accepted support findings into explicit material updates, release blockers, or `artifact_update_obligations`.
- AC-008 Beacon keeps support surfaces advisory unless their findings are adopted through `change`, truth surfaces, execution host updates, evidence updates, or obligations.
- AC-009 Beacon makes `beacon-toolkit-branch-governance` write delivery service, branch, and worktree updates through canonical git workflow, technical review contract, execution host, service slice, and metadata surfaces.
- AC-010 Beacon blocks QA and release while blocking artifact update obligations remain open.
- AC-011 Beacon emits diagnostics that name the missing material, default-seeded field, unadopted support finding, open obligation, and recommended repair surface.
- AC-012 Beacon preserves the main lifecycle boundary and does not turn support or toolkit skills into truth sources, gate sources, or new lifecycle stages.
