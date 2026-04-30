# Test Cases: Beacon v1.3.10 project topology and version-branch metadata transaction governance

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 项目元信息能持久化 `single_repo` 与 `monorepo` 两种 topology_kind | unit | 拓扑类型被写入结构化 metadata schema |
| TC-002 | AC-002 | monorepo 项目能持久化 `project_root -> service repo roots`、service key、角色、可写边界 | integration | service binding 被写入 canonical metadata，并可被读取 |
| TC-003 | AC-003 | 已存在 metadata 时，运行前不再重复 repo 探测，而是直接按 contract 解析目标 service repo | integration | 目标 service repo 的解析结果稳定且可重复 |
| TC-004 | AC-101 | 某个 Beacon version 能绑定参与交付的 service set | unit | version contract 包含明确 service set |
| TC-005 | AC-102 | 每个参与 service 都能绑定 allowed working branch contract | unit | version -> service -> allowed working branch 映射可读取 |
| TC-006 | AC-103 | Beacon 只表达最小 working-branch guard，而不引入项目级 workflow 图 | unit | branch guard 规则保持最小边界 |
| TC-006A | AC-104 | metadata 明确拆成“全局项目级元信息 + 版本级元信息”两层 | unit | 两层字段边界明确，版本字段不污染全局项目事实 |
| TC-007 | AC-201 | 任一元信息变更先形成 canonical metadata envelope | integration | human/machine/sqlite 不会各自独立起写 |
| TC-008 | AC-202 | 同一笔元信息事务会双写或三写到 human sink、machine sink、sqlite sink | integration | 共享 transaction_id/source_hash/projection_seq/sink_checksums |
| TC-009 | AC-203 | status/doctor/gate/review 能发现 metadata sink 缺失、checksum drift、failed transaction | integration | drift 与 failed transaction 可报告且可阻断 |
| TC-009A | AC-204 | 正常 `beacon-change / reopen / freeze` 闭环后不再需要额外执行 `doctor sync-materials` | integration | human requirement docs 与 `.machine` requirement materials 已同步完成 |
| TC-010 | AC-301 | prompt 层读取固定 metadata，而不是重新推断 monorepo/service/working-branch | integration | 提示输入引用 metadata truth，而非再次决策事实 |
| TC-011 | AC-302 | runtime 层在 implement/qa/release 前读取 metadata contract 做 repo/branch/worktree 校验 | integration | 前置校验读取同一份 metadata truth |
| TC-012 | AC-303 | 当前 service、branch 或 worktree 不满足 contract 时确定性阻断 | integration | 停止执行并给出明确修复指引 |
| TC-012A | AC-304 | 当用户以 `beacon:子skill + vX.Y.Z` 或显式 `--version vX.Y.Z` 调用 Beacon 子 skill 时，运行层先解析全局项目级元信息与对应版本级元信息 | integration | 运行层返回 resolved metadata view，而不是把推断责任留给 prompt 层 |
| TC-012B | AC-305 | prompt 层不得绕过运行层再次推断 topology/service/branch 事实 | integration | prompt 输入只能消费运行层 resolved metadata view |
| TC-012C | AC-306 | `friction-intake`、`brainstorm`、`change` 等 support skill 带版本调用时复用同一 resolved metadata view | integration | support skill 不会各自重跑 monorepo/service/branch 推断 |
| TC-013 | AC-401 | Beacon 提供确定性人类面元信息 support surface，并固定收口到 `beacon doctor metadata ...` | unit | support surface 稳定，不新增一级公开命令 |
| TC-014 | AC-402 | 宿主命令面固定收口到 `beacon doctor metadata show/create/update/delete/list/verify` | unit | 不新增一级公开命令，同时命令集具备确定性 |
| TC-015 | AC-403 | 人类元信息 surface 支持新增 metadata contract | integration | create 动作进入 canonical metadata transaction |
| TC-016 | AC-403 | 人类元信息 surface 支持查询 / 列表 metadata contract | integration | read/list 动作返回当前 topology、service、version、branch 绑定 |
| TC-017 | AC-403 | 人类元信息 surface 支持修改或删除 metadata contract | integration | update/delete 动作留下可审计 transaction 轨迹并更新投影 |
| TC-018 | AC-403 | 人类元信息 surface 支持显式 verify 当前 runtime state 与 metadata contract 是否一致 | integration | verify 给出 pass / block 与具体 mismatch 原因 |
| TC-019 | AC-404 | 人类元信息 surface 的增删改不会直接手改单一 sink，而是走 canonical transaction | integration | 单点写入被禁止或会被 doctor/gate 识别为 drift |
| TC-020 | AC-501 | 元信息相关人类输出显式显示绝对 `project_root` | unit | cross-project 报告不再只有相对路径 |
| TC-021 | AC-502 | 元信息输出能标识 human sink、machine sink、sqlite transaction | integration | 操作者能定位三面产物与事务来源 |
| TC-022 | AC-503 | 在 Beacon 核心仓与目标项目仓并存时，路径报告不会混淆产物归属 | integration | 输出能明确区分 Beacon 仓与 target project 仓 |
| TC-023 | AC-504 | `latest.json` 同时包含相对路径、绝对路径与 `project_root` | unit | machine pointer 不再只有相对 artifact path |
| TC-024 | AC-505 | 人类提示里的“落盘位置”在 cross-project 模式下打印绝对路径 | integration | 操作者能直接定位目标项目产物 |
| TC-025 | AC-601 | `friction-intake` human 输出显式包含绝对 `project_root` | integration | human 输出不再省略绝对项目根 |
| TC-026 | AC-602 | `friction-intake` json 输出显式包含绝对 `project_root` | integration | json 输出包含可机读绝对项目根 |
| TC-027 | AC-603 | `friction-intake` human/json 输出包含绝对 artifact path | integration | human artifact、machine artifact、capture evidence 都可被直接定位 |
| TC-028 | AC-701 | monorepo 拓扑问题命中 `monorepo` domain 规则 | unit | 不再落到宽泛 `prompt` |
| TC-029 | AC-702 | 版本分支治理问题命中 `branch-governance` domain 规则 | unit | 分类结果进入元信息治理域 |
| TC-030 | AC-703 | `project_root -> service repo root` 绑定问题命中 `repo-binding` domain 规则 | unit | repo binding 问题被正确分类 |
| TC-031 | AC-704 | 满足证据条件的元信息治理问题不会静默回退为 `prompt` | integration | domain classifier 稳定保留 metadata governance 语义 |
| TC-032 | AC-801 | 核心 metadata 字段只覆盖 topology、service binding、participating services、per-service allowed working branch | unit | schema 不引入额外项目级 workflow 字段 |
| TC-033 | AC-802 | 核心 metadata 不内建 integration/testing/uat/merge-flow graph | unit | PRD 与 schema 边界保持极简 |
| TC-034 | AC-803 | 项目级复杂协作规则通过项目内 skill/policy 扩展 | review | 核心 requirement truth 显式声明扩展边界 |
| TC-035 | AC-901 | `freeze` 成功后，human docs、`.machine` requirement package、revision/story state 同时完成冻结对齐 | integration | 不存在“文档已变但机器面未刷新”的成功态 |
| TC-036 | AC-902 | `reopen` 生成新 revision 时，machine requirement projection 同步切换到新 active revision | integration | 新 revision 立即可继续编辑/校验 |
| TC-037 | AC-903 | 正常 change 闭环不依赖 `doctor sync-materials`，该命令仅用于 repair/rebuild | integration | 主路径不再包含额外机器面补齐步骤 |
| TC-038 | AC-904 | human docs 与 `.machine` requirement materials 不一致时，`freeze`/`implement`/`qa`/`release` 被阻断 | integration | material gap 被显式报告并 fail closed |

## Regression Focus

- monorepo 元信息不能退化回 prompt 期临时推断
- sqlite 不得单独成为唯一 truth source
- human sink 不得反向驱动 machine truth
- 元信息 CRUD 动作不得绕开 canonical transaction
- implement / qa / release 不得在 working-branch/service mismatch 时继续推进
- 正常 `beacon-change` 闭环不得再要求人工补跑 `.machine` materials sync
- 核心 metadata 不得膨胀成项目级 Git workflow engine
- `friction-intake` 输出不得再次退化为仅相对路径
- 元信息治理类 domain 不得被回退分类成 `prompt`

## Execution Notes

- version: `v1.3.10`
- upstream_prd: `docs/beacon/v1.3.10/prd/beacon-v1-3-10-project-topology-and-version-branch-metadata-transaction-governance.md`
- upstream_user_story: `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- machine_matrix: `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.ac-test-matrix.json`
- 本测试矩阵优先覆盖 topology metadata、version-scoped working-branch contract、事务级多写一致性、人类元信息 surface 的 CRUD + verify 闭环，以及 `friction-intake` 输出契约与 domain classifier 修正。
