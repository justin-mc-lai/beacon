# Beacon 调研：人类面子 Skill 材料闭环与 Gate 契约

> 日期：2026-05-21
> 调研版本线：`v1.4.8`
> 状态：仅调研
> 范围：人类面 Beacon 子 skill 调用、必需材料写回、显式路由义务、fail-closed 门禁
> 来源引用：
> - `skills/beacon/SKILL.md`
> - `skills/beacon/using-beacon/SKILL.md`
> - `skills/beacon/beacon-*/SKILL.md`
> - `skills/beacon-iteration-governance/SKILL.md`
> - `skills/beacon-prototype-reconcile/SKILL.md`
> - `.agents/skills/runtime-skill-admission-smoke/SKILL.md`
> - `beacon/utils/docs_structure_contract.py`
> - `beacon/utils/artifact_update_obligations.py`
> - `beacon/utils/technical_review_contract.py`
> - `beacon/utils/implementation_plan.py`
> - `beacon/utils/branch_governance.py`
> - `beacon/commands/implement.py`
> - `beacon/commands/gate.py`
> - `beacon/commands/review.py`
> - `docs/beacon/v1.4.8/research/beacon-v1.4.8-execution-material-rigor-and-version-governance-analysis.md`
> - `docs/beacon/v1.4.8/research/beacon-vnext-business-flow-and-state-machine-document-design.md`

---

## 1. 调研目标

本文闭合 `v1.4.8` 的下一个调研缺口：

> 人类面的 Beacon 子 skill 调用，必须更新对应 Beacon 材料面、打开正式材料更新义务，或明确保持只读并给出 route-back decision。

目标失败模式是：

```text
support 或 toolkit skill 给出了看起来合理的建议，
但没有更新任何显式 Beacon 文档，
没有打开 obligation，
下游 implement / QA / release 仍然继续推进。
```

这必须被视为 Beacon harness failure。

本文不是 canonical truth。
它是后续 `beacon-change -> prd -> user-story -> test-case` transaction 的上游调研材料。

## 2. 当前状态的源码确认

### 2.1 Beacon 已经区分 surface family

`skills/beacon/SKILL.md` 定义了四类人类决策面：

- truth
- execution
- verification / gate
- support

主链保持紧凑：

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

`prototype` 是条件触发。
support surfaces 可以 challenge、diagnose、route，但它们不是 truth source、gate source，也不是 lifecycle stage。

### 2.2 当前 docs structure contract 对这个问题仍然过粗

`beacon/utils/docs_structure_contract.py` 只把一小组 surface 映射到 semantic layers：

- truth: `prd`, `user-story`, `test-case`, `change`
- guidance: `ceo-review`, `brainstorm`, `design-review`, `deep`
- delivery: `prototype`, `implement`
- evidence: `qa`, `release`

它还没有定义完整的 per-subskill material update matrix，尤其没有覆盖：

- `context-engineering`
- `source-driven`
- `doubt-review`
- `security-review`
- `performance-review`
- `documentation-adr`
- `debug-recovery`
- `doctor`
- `learn`
- `archive`
- `real-project-validation`
- `friction-intake`
- toolkit surfaces

所以 Beacon 已经有 semantic layer model，但还没有完整的人类面子 skill 闭环契约。

### 2.3 Artifact update obligations 已存在，但仍不够

`beacon/utils/artifact_update_obligations.py` 已经把开放写回义务形式化到：

```text
.beacon/state/artifact-update-obligations/<feature>.json
```

这些 obligations 已被 review / QA 类 gates 消费。
例如 `beacon/commands/review.py` 会在非 acceptance 类 artifact writeback obligations 仍然 open 时阻断 quality review。

这个方向是对的。
但它还小于 `v1.4.8` 需要的契约：

- 它主要面向 implement / review 后续补写
- 它是通用机制，不是 per-human-subskill 机制
- 它还没有强制每个 accepted support finding 进入命名 Beacon material surface
- 它还不能防止 branch / service / worktree facts 被 default seed 代替显式冻结事实

### 2.4 执行事实仍可能被过于安静地 seed

`technical_review_contract.py` 和 `implementation_plan.py` 可以 seed 关键交付事实：

- `target_branch`
- `service_directories`
- `writable_services`
- `worktree_root`
- `use_git_worktree`

这意味着文件可能存在，但事实来源仍然很弱。

对 `v1.4.8`，更强的规则应该是：

```text
delivery-critical facts 必须是 explicit frozen facts，
不能是只满足 schema presence 的 silent defaults。
```

## 3. 闭环原则

每个人类面的子 skill 调用，最终必须落到以下 material effects 之一：

1. `writeback_completed`
2. `writeback_required`
3. `obligation_opened`
4. `truth_reopen_required`
5. `execution_host_update_required`
6. `evidence_update_required`
7. `read_only_route_only`

输出必须声明：

- surface name
- feature 或 version scope
- material effect
- target artifact paths
- 相关 truth bindings
- next route
- 当目标材料缺失时的 fail-closed condition

如果某个 skill 不能命名自己的 material effect，它就不应该静默解锁下一条主链 surface。

## 4. Canonical Material Surfaces（权威材料面）

本调研中的最低材料面集合是：

```text
docs/beacon/<version>/
├── SUMMARY.md
├── research/
├── prd/
├── user-story/
├── qa/
│   └── test-cases/
├── change/
├── prototype/
├── execution/
│   ├── index.md
│   ├── architecture-blueprint.md
│   ├── current-state-service-map.md
│   ├── refactor-boundaries.md
│   ├── service-slice-map.md
│   ├── git-workflow-<feature>.md
│   ├── technical-review-contract-<feature>.md
│   └── branch-governance-<feature>.md
├── release/
└── .machine/
    ├── execution/
    │   ├── git-workflow-<feature>.json
    │   ├── implementation-plan-<feature>.json
    │   ├── implementation-delivery-baseline-<feature>.json
    │   └── technical-review-contract-<feature>.json
    ├── qa/
    └── release/
```

不是每个项目都需要每个文件。
但如果某个 feature、project type 或 subskill 声称某个 surface 相关，那么对应目标材料必须显式存在。

## 5. 人类面子 Skill 闭环矩阵

### 5.1 Host 与路由面

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon` | host route constitution | `read_only_route_only`，除非它接受了会改变 route 的决策 | 如果 route 改变 accepted scope，必须通过 `beacon-change` 打开 `truth_reopen_required` |
| `using-beacon` | host-native route router | `read_only_route_only` | 如果它识别出 material gap 但没有命名下一跳 surface，不得继续 |
| `beacon-help` | 下一步指引 | `read_only_route_only` | 如果 help 发现 truth drift，路由到 `beacon-change`；如果是 context drift，路由到 `beacon-doctor` |
| `beacon-status` | board / lifecycle 可见性 | `read_only_route_only` | status 不能满足 truth、implementation、QA 或 release gates |

### 5.2 Truth 面

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon-prd` | 问题、范围、promise | 更新 `docs/beacon/<version>/prd/`，复杂需求触发时还要更新相关 research inputs | 如果 PRD promise / scope 缺失或不稳定，user-story 必须阻断 |
| `beacon-user-story` | actor goals 与 acceptance criteria | 更新 `docs/beacon/<version>/user-story/` | 如果 ACs 无法投影成可验证场景，test-case 与 freeze 必须阻断 |
| `beacon-test-case` | coverage truth | 更新 `docs/beacon/<version>/qa/test-cases/` | 如果 AC projection、boundary/recovery coverage 缺失，freeze 与 implement 必须阻断 |
| `beacon-change` | frozen truth revision | 更新 `docs/beacon/<version>/change/`，并把改变的 surface 重新送回 PRD / story / test-case | 当 stale frozen truth 已 reopen 时，implement / QA / release 必须阻断 |
| `beacon-change-refreeze` | 人类面进入 governed refreeze 的 route | 打开或完成 `change -> prd -> user-story -> test-case -> requirement_clarity -> freeze` transaction | refreeze status partial 或 blocked 时，下游 surfaces 必须阻断 |
| `beacon-prd-bootstrap` | 安全创建第一套 package shell | 只有显式 apply 时才创建受保护的 PRD / story / test-case shells | bootstrap 输出不能在缺少 research 与 clarity closure 时算作 freeze-ready |

### 5.3 Execution 面

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon-prototype` | 条件触发的 requirement-to-screen handoff | 更新 `docs/beacon/<version>/prototype/`，并把 design intent 绑定回 PRD / story / test-case | 如果真实存在 UX/UI handoff，但 prototype contract 缺失或 not gate-ready，implement 必须阻断 |
| `beacon-implement` | implementation planning / execution | 更新 `.machine/execution/implementation-plan-<feature>.json`、`.machine/execution/implementation-delivery-baseline-<feature>.json`、`execution/architecture-blueprint.md` projection 和 implementation evidence | 必须在 stale truth、technical review contract 缺失、delivery baseline 缺失、git workflow 缺失、branch preflight failure、architecture blueprint projection drift 时阻断 |

### 5.4 Verification 与 release 面

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon-qa` | 分层 verification | 更新 QA evidence，并把 defects 路由到 `implement`、`test-case` 或 `change` | 如果 QA layers、runner admission、acceptance proof 或 writeback obligations 不完整，release 必须阻断 |
| `beacon-release` | go / no-go 判断 | 更新 `docs/beacon/<version>/release/` 下的 release scorecard / release proof summary，或 machine release evidence | ship 必须在 QA layers 缺失、version drift、open blockers 或 material audit failure 时阻断 |
| `beacon-real-project-validation` | 真实 repo 证明 | 产出 validation record，并区分 project-state blocker 与 Beacon defect | 如果 public real-project proof 无法证明当前 version surface，release claims 必须阻断 |

### 5.5 Support review 面

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon-brainstorm` | 只读收敛 | 当输出需要持久化时，只写 brainstorm / research artifact；accepted scope change 路由到 `beacon-change` | brainstorm 不能单独满足 PRD / story / test-case / freeze |
| `beacon-ceo-review` | founder-level scope 与 promise challenge | advisory report 加 route decision；accepted promise / scope change 打开 `truth_reopen_required` | 如果 verdict 是 `expand`、`reduce` 或 `reframe`，implement 不得继续，直到 change/refreeze 闭合 |
| `beacon-deep` | 结构分析、test deltas、risk closure | deep report / test delta / risk register；accepted deltas 打开 test-case 或 change obligations | deep 不能替代 QA 或 truth updates；accepted findings 必须变成 obligations |
| `beacon-design-review` | prototype entry / design mismatch review | design verdict 加 route 到 `prototype`、`change`、`user-story` 或 `test-case` | design review pass 不能当作 prototype freeze |
| `beacon-context-engineering` | working-context reduction | context pack recommendation，并附 canonical truth refs | 如果 context reduction 暴露 missing truth anchors，必须阻断并路由到 truth surface |
| `beacon-source-driven` | source-anchored review | source anchor summary 与 unsupported-claim warnings | 没有 source 支撑的 claims 不能被提升为 implementation 或 release closure |
| `beacon-doubt-review` | adversarial evidence-gap review | doubt register 与 route recommendation | weak proof 或 contradiction 必须打开 obligation 或 route back，之后才能继续 |
| `beacon-security-review` | security risk challenge | security risk summary；accepted risk 打开 change、implement、QA 或 release blocker obligation | security findings 只有在目标材料或 evidence 更新后才算 resolved |
| `beacon-performance-review` | performance 与 scale challenge | performance risk summary；accepted risk 打开 SLA truth、implement、QA 或 release blocker obligation | performance risk 不能静默 waive；waiver 必须进入显式 release / support evidence |
| `beacon-documentation-adr` | ADR 与 delivery rationale | 只有真正改善 decision clarity 时才写 ADR / support doc；truth drift 路由到 change | ADR 不能覆盖 canonical requirement truth |
| `beacon-debug-recovery` | blocked-path diagnosis | blocker family 与 repair route；可打开 doctor、implement、QA 或 change obligation | debug diagnosis 不能单独关闭 implementation、QA 或 release |

### 5.6 Governance、toolkit 与 maintenance 面

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon-doctor` | context / material / version 修复 | diagnostics 与 repair artifacts；sync commands 必须通过 canonical transaction paths 写入 | 当 context 或 version drift 未解决时，主链必须阻断 |
| `beacon-learn` | governed learning recall / audit | learning audit 或 prune record | learning 不能定义 truth 或 release verdict |
| `beacon-archive` | historical truth isolation | archive plan / apply / status / explain artifact | archived truth 不得污染 active version materials |
| `beacon-friction-intake` | friction queue capture | 在 global sqlite 与 project-local debug / memory / analysis artifacts 中写入 queue item | friction item 只有显式接受进入 change / PRD 后，才能成为 requirement truth |
| `beacon-toolkit-metadata` | project / version metadata CRUD | canonical metadata transaction write；禁止只手改单个 sink | metadata contract mismatch 时，runtime 与 validation 必须阻断 |
| `beacon-toolkit-branch-governance` | branch / worktree governance view 与 repair route | 默认 show / verify 只读；如果请求 update，必须更新 canonical branch / service / worktree material surfaces | 如果 delivery service、target branch 或 worktree mode 缺失、default-seeded，或脱离 execution host truth，implement 必须阻断 |
| `beacon-toolkit-automation` | scheduler queue / tooling governance | automation queue / scaffold / summary schema artifacts | queue contract 或 executor tier 无效时，scheduled implement / QA 必须阻断 |
| `beacon-toolkit-lighthouse` | 单页结构分析 | 一个 Markdown analysis artifact；Beacon source iterations 还要产出 versioned execution artifact | Lighthouse output 不能满足 PRD、execution plan、QA plan 或 freeze |

### 5.7 兼容与项目本地 skills

| Skill | 主要职责 | 必需材料效果 | fail-closed 条件 |
| --- | --- | --- | --- |
| `beacon-iteration-governance` | Beacon source iteration governance | 在 `.beacon/iteration-governance/` 下写 iteration summary；当代码变化时同步收敛 README、`SKILL.md`、`skills/beacon/`、docs 与 release checks | 如果 source changes 未收敛到当前 docs、skill surfaces 与 release evidence，Beacon release / readiness 应阻断 |
| `beacon-prototype-reconcile` | code-backed prototype / docs reconciliation | 产出 implementation truth、route closure audit、prototype gap list、prototype patch report 等 execution artifacts | 当 docs / prototype / code drift 仍未解决或未分类时，prototype / design / gate 必须阻断 |
| `runtime-skill-admission-smoke` | host runtime skill admission smoke | 仅产出 runtime admission evidence | 这个 smoke 不能满足 requirement、execution、QA、release 或 package closure；它只证明 host skill admission |

## 6. Branch Governance（分支治理）闭环契约

`beacon-toolkit-branch-governance` 是 `v1.4.8` 需要升级的最清晰例子。

当前它主要被定义为：

- show resolved governance
- verify branch contract
- review evidence requirements before implement

这种只读行为是合理的。
但当人类意图是更新 delivery service 或 branch truth 时，闭环契约必须变成 write-backed。

### 6.1 必需写回 surfaces

对于 feature-bound branch governance update，Beacon 应更新或要求：

- `docs/beacon/<version>/execution/git-workflow-<feature>.md`
- `docs/beacon/<version>/.machine/execution/git-workflow-<feature>.json`
- `docs/beacon/<version>/execution/technical-review-contract-<feature>.md`
- `docs/beacon/<version>/.machine/execution/technical-review-contract-<feature>.json`
- `docs/beacon/<version>/execution/architecture-blueprint.md`
- multi-service 或 takeover context 存在时的 `docs/beacon/<version>/execution/service-slice-map.md`
- 当 service binding 或 per-service branch mapping 改变时的 canonical metadata contract

per-feature branch dossiers 可以存在，但它们不能成为 branch / worktree truth 的唯一来源。

### 6.2 必需显式事实

governance material 必须显式声明：

- delivery services
- writable services
- reference-only services
- base branch
- target branch 或 per-service target branch
- branch strategy
- `use_git_worktree`
- worktree mode
- worktree root / path
- clean worktree requirement
- fact source 与 review status

### 6.3 fail-closed 规则

对于 execution-bound features：

```text
缺少显式 delivery service / branch / worktree facts，
或事实仅来自 version defaults，
必须阻断 implement。
```

可接受状态必须是显式 human/material statuses，例如：

- `review_status=approved`
- `review_status=accepted`
- `source=metadata_contract`
- `source=execution_host`
- `source=human_reviewed_writeback`

以下弱状态不应单独解锁 implementation：

- `source=version_default`
- `source=project_config_seed`
- blank `approved_by`
- blank `reviewed_at`
- missing managed projection block

## 7. Support Finding（支持面发现）采纳契约

Support surfaces 应继续保持 support surface。
缺失的是 adoption。

当一个 support finding 被接受后，Beacon 应把它转换成以下之一：

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

support report 本身不够。

示例：

```text
security-review finds missing authz boundary
-> if requirement promise changes: beacon-change
-> if implementation is incomplete: beacon-implement obligation
-> if verification evidence is missing: beacon-qa obligation
-> if release risk remains: release blocker / waiver material
```

## 8. Gate 完整性提案

### 8.1 Requirement gate

以下情况应阻断：

- PRD missing 或 unstable
- user-story ACs 不能投影进 tests
- test-case coverage 不完整
- complexity-triggered business flow / state-machine truth bindings 缺失
- frozen truth reopened 或 stale

### 8.2 Execution host gate

以下情况应阻断：

- `execution/index.md` 缺失
- `execution/architecture-blueprint.md` 缺失
- architecture blueprint managed projection 缺失或 drifted
- implementation delivery baseline 缺失
- technical review contract 缺失、未 approved，或 default-seeded
- git workflow contract 缺失、未 approved，或 default-seeded
- branch / worktree / service facts 不在 execution host 中
- takeover baseline docs 缺失
- multi-service projects 缺少 `service-slice-map.md`

### 8.3 Support adoption gate

以下情况应阻断：

- 存在 accepted support findings，但没有声明 material target
- 存在 open artifact update obligations
- advisory result 声明 `route_to_change`、`route_to_test_case`、`route_to_qa` 或 `route_to_release_blocker`，但目标 surface 未更新

### 8.4 Evidence 与 release gate

以下情况应阻断：

- QA layers 不完整
- runner admission blocked 但未记录
- real-project validation 不能证明 public surface
- release scorecard 依赖看起来绿色的状态，但没有 evidence chain
- version / package / runtime surfaces drift

## 9. No Silent Pass Rules（禁止静默放过规则）

这些规则应在后续 `v1.4.8` change 中显式化：

1. missing material surface 不等于 `not needed`
2. generated default 不等于 approved fact
3. support report 不等于 truth writeback
4. side dossier 不等于 canonical execution host
5. route recommendation 只有命名 next material target 才算完整
6. accepted finding 必须更新 canonical material surface 或打开 blocking obligation
7. implement 不能从 implicit service / branch / worktree assumptions 开始
8. QA 和 release 不能在 writeback obligations 仍 open 时通过

## 10. 推荐运行时形态

后续实现可以引入类似下面的结构化 contract：

```json
{
  "schema_version": "1.0",
  "surface": "beacon-toolkit-branch-governance",
  "feature": "<feature>",
  "version": "v1.4.8",
  "material_effect": "execution_host_update_required",
  "target_artifacts": [
    "docs/beacon/<version>/execution/git-workflow-<feature>.md",
    "docs/beacon/<version>/.machine/execution/git-workflow-<feature>.json",
    "docs/beacon/<version>/execution/architecture-blueprint.md"
  ],
  "truth_bindings": [],
  "accepted_route": "beacon-implement",
  "open_obligations": [
    "delivery_service_mapping",
    "target_branch",
    "worktree_mode"
  ],
  "fail_closed_gate": "implement_preflight"
}
```

它可以作为 per-surface material closure registry 实现，然后被以下入口消费：

- `doctor verify-context --strict`
- `implement` preflight
- `qa`
- `review quality`
- `release`
- material audit

## 11. 调研结论

最强结论是：

> Beacon 不应该让每个 support surface 都变成 truth writer，但每个人类面子 skill 都必须有闭合的 material effect。

这意味着：

- truth surfaces 写 truth
- execution surfaces 写 execution host 与 execution evidence
- gate surfaces 写 evidence 与 verdicts
- support surfaces 要么明确只读，要么打开正式 route / writeback obligations
- toolkit surfaces 在改变项目事实时必须通过 canonical metadata / execution transaction paths 写入

`v1.4.8` 的具体升级应聚焦：

- per-subskill material closure registry
- branch / service / worktree explicit-fact gate
- support finding adoption 进入 artifact update obligations
- branch governance 的 execution host canonical writeback
- implement / QA / release 前的 fail-closed material audit

## 12. 下一步路由

推荐下一跳：

1. `beacon-change`
2. 冻结 human-subskill material closure contract
3. 编译进入 PRD / user-story / test-case
4. 实现 registry 与 gate checks
5. 在曾经出现 execution host docs 漂移或碎片化的真实项目上验证
