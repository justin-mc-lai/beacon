# Beacon Revision Delta

- feature: `Beacon v1.3.10 project topology and version-branch metadata transaction governance`
- version: `v1.3.10`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `5`
- added_requirement_count: `36`

## Removed Requirement Surfaces
- `AC-005` Beacon 能为每个参与 service 保存该版本线对应的 canonical branch contract。
- `AC-014` 该 skill 的宿主命令面固定收口到 `beacon doctor metadata show/create/update/delete/list/verify`，不新增一级公开命令。
- `AC-010` 当 metadata 已存在时，prompt 层把项目拓扑、service repo、canonical branch 当作固定输入，而不是重新推断。
- `AC-006` Beacon 能表达 protected branch 禁写、可写分支约束与违例处理策略。
- `AC-013` Beacon 提供确定性的人类面元信息子 skill，名称固定为 `beacon:beacon-project-metadata`。

## Added Requirement Surfaces
- `AC-042` human/json 输出都能标识 human artifact、machine artifact、capture evidence 的绝对路径。
- `AC-044` 版本到 per-service allowed working branch 的治理问题能命中 `branch-governance` domain 规则。
- `AC-034` `implementation`、`qa acceptance`、`release closure` 的人类文档形态必须优先输出 brief / summary，而不是把 changed files、implemented item ids、round refs 大段直出。
- `AC-027` `doctor sync-materials` 只作为 repair/rebuild/drift recovery surface 保留，不再是正常 `beacon-change` 闭环的必经步骤。
- `AC-028` 若 human docs 与 `.machine` requirement materials 存在未同步缺口，`freeze`、`implement`、`qa`、`release` 必须明确阻断。
- `AC-025` `freeze` 成功时，不仅 revision/story state 冻结，当前 feature 的 `.machine` requirement package 也已与 human docs 对齐。
- `AC-050` Cross-project reporting is unambiguous
- `AC-047` Cross-project 输出无歧义
- `AC-048` 元信息类 friction 不再误分到 `prompt`
- `AC-049` 分支与仓绑定违例时硬阻断
- `AC-039` 人类提示中的“落盘位置”至少在 cross-project 模式下打印绝对路径。
- `AC-029` human execution 固定收口为 `index.md`、`architecture-blueprint.md`、`implementation-brief-<feature>.md`、`qa-acceptance-brief-<feature>.md`、`release-closure-brief-<feature>.md` 或版本级 release summary。
- `AC-040` `friction-intake` 的 human-readable 输出显式包含绝对 `project_root`。
- `AC-041` `friction-intake` 的 json 输出显式包含绝对 `project_root`。
- `AC-038` `latest.json` 这类 machine pointer 除相对路径外，还会补充 `project_root` 与绝对 artifact path。
- `AC-033` 现有 `.machine/execution/*` 继续保留确定性 envelope / contract / transaction truth，不因人类面瘦身而丢失。
- `AC-032` 上述运行痕迹若需要保留，必须下沉到 `.machine/trace/` 或 `.beacon/`，而不是继续出现在 `docs/beacon/<version>/execution/`。
- `AC-006` Beacon 只表达最小 working-branch guard 与违例处理策略，不扩张为完整项目 Git workflow。
- `AC-022` Beacon 核心 metadata 只覆盖 topology、service binding、participating services、per-service allowed working branch。
- `AC-019` 该 support surface 的宿主命令面固定收口到 `beacon doctor metadata show/create/update/delete/list/verify`，不新增一级公开命令。
- `AC-043` monorepo 拓扑绑定问题能命中 `monorepo` domain 规则。
- `AC-011` 正常 `beacon-change / reopen / freeze` 闭环结束时，human requirement docs 与 `.machine` requirement materials 已经同事务对齐，不再要求后置人工执行 `doctor sync-materials`。
- `AC-023` Beacon 核心 metadata 不内建 integration branch、testing branch、uat branch、merge flow graph 等项目级 workflow 结构。
- `AC-046` 以上问题在已满足证据条件时，不会被静默回退分类为 `prompt`。
- `AC-016` 提示层不得绕过 Beacon 运行层重新推断项目拓扑、service repo 或版本分支事实。
- `AC-031` `ralph/*`、`qa-team/*`、`codex-subagents/*`、`semantic/*.json` 不再落到 human execution 面。
- `AC-024` 若项目需要更复杂协作规则，应通过项目内 skill / policy 扩展，而不是挤入 Beacon 核心 metadata schema。
- `AC-012` 当 metadata 已存在时，prompt 层把项目拓扑、service repo、allowed working branch 当作固定输入，而不是重新推断。
- `AC-026` `reopen` 生成新 revision 后，machine 侧会同步切到可继续编辑/校验的 active projection，而不是只改 revision 编号。
- `AC-045` `project_root -> service repo root` 绑定问题能命中 `repo-binding` domain 规则。
- `AC-030` human execution 文档以 LLM 总结后的结论为主，默认正文不再以 run/transaction/round 字段为主体。
- `AC-017` `friction-intake`、`brainstorm`、`change` 等 Beacon 相关 support skill 在显式带版本调用时，也只能消费同一 resolved metadata view。
- `AC-018` Beacon 提供确定性的人类面元信息 support surface，固定收口到 `beacon doctor metadata ...`。
- `AC-007` Beacon 明确把 metadata 拆成“全局项目级元信息”和“版本级元信息”两层，而不是把所有字段混成单层模型。
- `AC-015` 当用户以 `beacon:子skill + vX.Y.Z` 或显式 `--version vX.Y.Z` 调用 Beacon 子 skill 时，运行层会先解析“全局项目级元信息 + 对应版本级元信息”，并返回 resolved metadata view 给提示层消费。
- `AC-005` Beacon 能为每个参与 service 保存该版本线对应的 allowed working branch contract。
