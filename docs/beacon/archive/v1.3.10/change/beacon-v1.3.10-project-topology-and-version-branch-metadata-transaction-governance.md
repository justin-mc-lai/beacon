# Beacon Feature Change Document

- feature: `Beacon v1.3.10 project topology and version-branch metadata transaction governance`
- feature_slug: `beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`
- version: `v1.3.10`
- status: `freeze_ready`

## Change Intent

- 将 `rolo` 暴露的 monorepo / branch 漂移问题，从 friction 表象收口为项目版本元信息治理问题。
- 在不新增 Beacon 一级公开主命令的前提下，给出确定性的人类面元信息 support surface。
- 将该变更固定为可继续 freeze / implement 的 requirement truth，而不是停留在 brainstorm 或开放命名阶段。
- 将需求边界进一步收口为“极简核心 metadata + 强门禁”，不把项目级 Git workflow 编进 Beacon 核心。

## Scope Delta

- 新增 `project-version metadata governance` 能力线
- 新增 `execution human surface slimming` 收敛线
- 将宿主命令面固定收口到 `beacon doctor metadata ...`
- 将 CRUD + verify 能力写入 PRD / user-story / test-case
- 将 `friction-intake` 的绝对 `project_root` / 绝对 artifact path / latest pointer contract 纳入 requirement truth
- 将 domain classifier 的 `monorepo / branch-governance / repo-binding` 规则纳入 requirement truth
- 将“提示层必须按版本从运行层读取 resolved metadata view”纳入 requirement truth
- 将字段语义从 `canonical branch` 收口为 `per-service allowed working branch`
- 明确复杂协作分支流程交给项目内 skill / policy，而不是 Beacon 核心 metadata
- 将 `beacon-change / reopen / freeze` 对 requirement package 的人机双写闭环纳入 requirement truth
- 将 `docs/beacon/<version>/execution/` 收口为人类结论层，不再承载运行轮次痕迹
- 将 `ralph/*`、`qa-team/*`、`codex-subagents/*`、`semantic/*.json` 下沉到 machine/runtime trace 面

## Added

- 新增 `v1.3.10` PRD：
  - `docs/beacon/archive/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- 新增 `v1.3.10` User Story：
  - `docs/beacon/archive/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- 新增 `v1.3.10` Test Cases：
  - `docs/beacon/archive/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- 新增 machine coverage：
  - `.machine/user-story/...`
  - `.machine/qa/...ac-test-matrix.json`
  - `.machine/qa/...story-scenario-map.json`

## Fixed / Clarified

- 不再把“人类面元信息 support surface”保留为开放命名问题。
- 明确宿主命令面固定为：
  - `beacon doctor metadata show`
  - `beacon doctor metadata create`
  - `beacon doctor metadata update`
  - `beacon doctor metadata delete`
  - `beacon doctor metadata list`
  - `beacon doctor metadata verify`
- 明确该 surface 必须支持增删改查与校验，并全部纳入 canonical transaction。
- 明确 `friction-intake` human/json 输出必须显式包含绝对 `project_root`。
- 明确 `latest.json` 除相对路径外必须补 `project_root` 与绝对 artifact path。
- 明确 cross-project 模式下“落盘位置”必须打印绝对路径。
- 明确元信息治理问题不得再默认误分类到 `prompt`。
- 明确 Beacon 核心 metadata 只表达最小防错真相：topology、repo binding、participating services、per-service allowed working branch。
- 明确 integration branch、testing branch、uat branch、merge flow graph 等项目级协作流程不进入 Beacon 核心 metadata。
- 明确此类复杂协作规则应由项目内 skill / policy 承载。
- 明确正常 `beacon-change` 闭环必须直接同步 human docs、`.machine` requirement materials、revision/story state。
- 明确 `doctor sync-materials` 退化为 repair / rebuild surface，而不是 change 正常路径的必经步骤。
- 明确 human execution contract 固定收口为：
  - `index.md`
  - `architecture-blueprint.md`
  - `implementation-brief-<feature>.md`
  - `qa-acceptance-brief-<feature>.md`
  - `release-closure-brief-<feature>.md` 或版本级 `release summary`
- 明确 `docs/beacon/<version>/execution/` 中的人类文档应以 LLM 归纳后的结论为主，而不是 run 轨迹或 agent 轮次回放。
- 明确 `.machine/execution/*` 继续承载确定性 envelope / contract / transaction 投影。
- 明确运行痕迹目录：
  - `ralph/*`
  - `qa-team/*`
  - `codex-subagents/*`
  - `semantic/*.json`
  必须退出 human execution 面；其中 machine trace 固化到 `.machine/trace/`，运行态细节留在 `.beacon/`。
- 明确 human execution 文档不得再默认暴露 `run_id`、`transaction_id`、`source_hash`、`projection_seq`、agent round refs 等机器审计字段作为正文主体。

## Not Added

- 未新增新的一级公开命令，例如 `metadata`、`change`、`revision`。
- 未把 sqlite 升级为唯一 truth source。
- 未扩张为完整项目编排系统。
- 未要求删除 machine trace，只要求从人类默认阅读面移出。

## Readiness

- requirement clarity：已收口
- freeze readiness：已补齐
- 当前状态：可再次 freeze；冻结后进入实现补丁与 QA delta-run

## Traceability Refs

- `docs/beacon/archive/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/archive/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/archive/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/archive/v1.3.10/.machine/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.canonical.json`
- `docs/beacon/archive/v1.3.10/.machine/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.json`
- `docs/beacon/archive/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.ac-test-matrix.json`
