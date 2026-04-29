# User Story: Beacon v1.3.10 project topology and version-branch metadata transaction governance

## Story Boundary

- version: `v1.3.10`
- feature: `beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`
- status: `freeze_ready`
- upstream_prd: `docs/beacon/v1.3.10/prd/beacon-v1-3-10-project-topology-and-version-branch-metadata-transaction-governance.md`

本故事线只覆盖 Beacon 的项目拓扑与版本分支元信息治理能力，不扩展成新的主生命周期 stage，也不让 sqlite 单独成为唯一 truth source。

## Story 1: 固化项目拓扑元信息

作为 Beacon 维护者，我希望 Beacon 能把目标项目显式识别并固化为 `single_repo` 或 `monorepo`，并保存 `project_root -> service repo roots` 的结构化契约，这样后续执行不再反复依赖临时推断。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | topology-kind | Beacon 能持久化项目拓扑类型，至少区分 `single_repo` 与 `monorepo`。 |
| AC-002 | service-bindings | 当项目为 monorepo 时，Beacon 能持久化 `project_root -> service repo roots`、service key、角色与可写性边界。 |
| AC-003 | deterministic-resolution | 当元信息已存在时，Beacon 执行前能直接确定目标 service repo，而不是重新探测。 |

## Story 2: 固化版本到服务与分支契约

作为 Beacon requirement owner，我希望 Beacon 能持久化 `version -> service set -> canonical branch` 契约，这样 implement/qa/release 都能读取同一份版本分支真相。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-101 | version-contract | Beacon 能为某个版本保存参与交付的 service set。 |
| AC-102 | canonical-branch | Beacon 能为每个参与 service 保存该版本线对应的 canonical branch contract。 |
| AC-103 | protected-branch-rules | Beacon 能表达 protected branch 禁写、可写分支约束与违例处理策略。 |
| AC-104 | two-layer-model | Beacon 明确把 metadata 拆成“全局项目级元信息”和“版本级元信息”两层，而不是把所有字段混成单层模型。 |

## Story 3: 元信息必须通过事务级多写投影

作为 Beacon runtime owner，我希望项目版本元信息遵循 canonical-first 的事务级多写，而不是由文档、sqlite、运行态各写一份，这样多面状态不会持续漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-201 | canonical-envelope | 任一元信息变更都先形成单一 canonical metadata envelope。 |
| AC-202 | three-sink-transaction | 同一笔元信息事务会共享一致 transaction metadata，并投影到 human sink、machine sink、sqlite sink。 |
| AC-203 | drift-detectable | status/doctor/gate/review 能检测元信息投影缺失、校验和漂移、失败事务或过期 sqlite projection。 |

## Story 4: Prompt 层与 runtime 层必须直接消费元信息

作为 Beacon 操作者，我希望提示层与运行层读取已经固化的元信息契约，而不是每次重新推断项目拓扑、服务映射与目标分支，这样错误分支开发风险能在执行前就被阻断。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-301 | prompt-consumption | 当 metadata 已存在时，prompt 层把项目拓扑、service repo、canonical branch 当作固定输入，而不是重新推断。 |
| AC-302 | runtime-consumption | runtime 层在 implement/qa/release 前直接读取 metadata contract 进行 repo/branch/worktree 校验。 |
| AC-303 | deterministic-block | 当前 service、branch 或 worktree 状态不满足 contract 时，Beacon 会确定性阻断并给出修复指引。 |
| AC-304 | version-bound-resolve | 当用户以 `beacon:子skill + vX.Y.Z` 或显式 `--version vX.Y.Z` 调用 Beacon 子 skill 时，运行层会先解析“全局项目级元信息 + 对应版本级元信息”，并返回 resolved metadata view 给提示层消费。 |
| AC-305 | no-prompt-reinference | 提示层不得绕过 Beacon 运行层重新推断项目拓扑、service repo 或版本分支事实。 |
| AC-306 | support-skill-consistency | `friction-intake`、`brainstorm`、`change` 等 Beacon 相关 support skill 在显式带版本调用时，也只能消费同一 resolved metadata view。 |

## Story 5: 需要新增确定性的人类面元信息子 skill / support surface

作为人类操作者，我希望 Beacon 提供确定性的人类面元信息子 skill 来管理这类元信息，并把宿主命令面收口到现有 support surface，而不是新增一级公开命令，这样增删改查与校验动作都能被事务化治理。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-401 | support-surface | Beacon 提供确定性的人类面元信息子 skill，名称固定为 `beacon:beacon-project-metadata`。 |
| AC-402 | minimal-human-surface | 该 skill 的宿主命令面固定收口到 `beacon doctor metadata show/create/update/delete/list/verify`，不新增一级公开命令。 |
| AC-403 | crud-verify-coverage | 该 surface 至少支持新增、查询、修改、删除、列表查看与显式校验 metadata contract。 |
| AC-404 | transaction-boundary | 该 surface 的增删改动作必须走 canonical transaction，而不是直接改某一个 sink。 |

## Story 6: Cross-project 报告必须无歧义

作为跨项目操作者，我希望 Beacon 在报告元信息产物和决策结果时显式显示绝对 `project_root`、service repo root 和关键 artifact path，这样我不会在 Beacon 仓与目标项目仓之间混淆路径。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-501 | absolute-root | 人类可见输出会显式显示绝对 `project_root`。 |
| AC-502 | artifact-clarity | 元信息相关的人类可见输出能清楚标识 human sink、machine sink 与 sqlite transaction 标识。 |
| AC-503 | cross-project-safety | 在 cross-project / monorepo 场景下，路径报告不会让操作者误判产物属于 Beacon 核心仓还是目标项目仓。 |
| AC-504 | latest-pointer-absolute-paths | `latest.json` 这类 machine pointer 除相对路径外，还会补充 `project_root` 与绝对 artifact path。 |
| AC-505 | human-drop-location-absolute | 人类提示中的“落盘位置”至少在 cross-project 模式下打印绝对路径。 |

## Story 7: friction-intake 输出必须带绝对项目根与工件定位

作为跨项目操作者，我希望 `friction-intake` 的 human/json 输出显式包含绝对 `project_root` 与绝对 artifact path，这样我不会把 Beacon 仓里的状态文件和目标项目里的产物混淆。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-601 | human-output-root | `friction-intake` 的 human-readable 输出显式包含绝对 `project_root`。 |
| AC-602 | json-output-root | `friction-intake` 的 json 输出显式包含绝对 `project_root`。 |
| AC-603 | absolute-artifact-paths | human/json 输出都能标识 human artifact、machine artifact、capture evidence 的绝对路径。 |

## Story 8: 元信息类 domain classifier 必须准确命中

作为 Beacon 治理者，我希望 monorepo、branch governance、repo binding 这类问题被稳定分类到元信息治理域，而不是被误打到 `prompt`，这样后续路由与治理线才不会漂移。

### Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-701 | monorepo-domain | monorepo 拓扑绑定问题能命中 `monorepo` domain 规则。 |
| AC-702 | branch-domain | 版本到 canonical branch 的治理问题能命中 `branch-governance` domain 规则。 |
| AC-703 | repo-binding-domain | `project_root -> service repo root` 绑定问题能命中 `repo-binding` domain 规则。 |
| AC-704 | no-prompt-fallback | 以上问题在已满足证据条件时，不会被静默回退分类为 `prompt`。 |
