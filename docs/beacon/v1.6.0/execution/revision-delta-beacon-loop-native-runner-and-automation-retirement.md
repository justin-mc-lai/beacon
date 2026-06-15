# Beacon Revision Delta

- feature: `beacon-loop-native-runner-and-automation-retirement`
- version: `v1.6.0`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `True`
- removed_requirement_count: `14`
- added_requirement_count: `29`

## Removed Requirement Surfaces
- `AC-001` `beacon automation` 业务代码退役，不再作为 active command surface 暴露或执行旧 queue/job/launchd 业务。
- `AC-015` `beacon-loop doctor` 能检查 Beacon CLI 可用性、Node runtime、agent backend、git/worktree 能力和 evidence import prerequisites。
- `AC-003` `beacon-loop goal "<goal>"` 是唯一 goal entrypoint；不存在 `beacon-loop lfg` alias、deprecated alias、compatibility route 或 help hint。
- `AC-004` `beacon-loop goal` 启动前调用 `beacon truth-map resolve ... --json` 并记录 resolver refs。
- `AC-010` `beacon-loop import-evidence <run-id>` 调用 Beacon implementation evidence import，并把 runtime evidence candidate 接入 Beacon 可读实现证据面。
- `AC-009` `beacon-loop resume <run-id>` 从既有 run metadata、notes 和 branch/worktree 状态恢复，而不是创建无关新运行。
- `AC-011` Beacon QA/release 仍然是唯一 closure verdict；`beacon-loop` output 不得声明 QA pass、release ready 或 feature complete。
- `AC-012` docs、help、tests、command catalog 和 skill routing 全部使用 `goal` 命名，不出现 active `lfg` route。
- `AC-006` resolver pass 时，`beacon-loop` 创建 `.beacon/loop/runs/<run-id>/run-package.json`、`prompt.md`、`notes.md`、`output-schema.json`、iteration logs、`evidence.json` 和 `summary.md`。
- `AC-007` runner 默认使用 branch/worktree isolation，并在 dirty worktree 下 fail closed，除非显式 controlled mode 存在。
- `AC-014` runtime artifacts 明确标记为 runtime process record，不是 requirement truth，不写 `.machine` requirement projection。
- `AC-002` 仓库包含 `packages/beacon-loop`，并能独立构建出 `beacon-loop` CLI。
- `AC-008` 成功 iteration 自动 commit；失败 iteration rollback；commit failure 进入 repair state，且 resume 可继续。
- `AC-013` 旧 automation tests 被删除或重写为 retirement negative tests；新增 `beacon-loop` CLI/package/runner/evidence tests。

## Added Requirement Surfaces
- `AC-029` `resume` 继续下一轮 iteration 编号（N+1），复用同一 run-id 与 worktree/branch。
- `AC-001` TC-001, TC-002
- `AC-002` TC-003
- `AC-003` TC-004, TC-005
- `AC-004` TC-006, TC-007
- `AC-005` TC-008
- `AC-006` TC-009
- `AC-007` TC-010
- `AC-008` TC-011, TC-018
- `AC-009` TC-012
- `AC-010` TC-013
- `AC-011` TC-014
- `AC-012` TC-015
- `AC-013` TC-016
- `AC-014` TC-017
- `AC-015` TC-019
- `AC-017` TC-021
- `AC-018` TC-022
- `AC-016` TC-020
- `AC-019` TC-023
- `AC-020` TC-024, TC-025
- `AC-021` TC-026
- `AC-022` TC-027
- `AC-023` TC-028
- `AC-024` TC-029
- `AC-025` TC-030
- `AC-026` TC-031, TC-032
- `AC-027` TC-033
- `AC-030` Phase C 至少完成 claude 与 `acp:<target>` adapter，输出同一 structured schema。
