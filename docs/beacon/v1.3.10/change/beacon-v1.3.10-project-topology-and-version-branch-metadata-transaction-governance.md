# Beacon Feature Change Document

- feature: `Beacon v1.3.10 project topology and version-branch metadata transaction governance`
- feature_slug: `beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance`
- version: `v1.3.10`
- status: `freeze_ready`

## Change Intent

- 将 `rolo` 暴露的 monorepo / branch 漂移问题，从 friction 表象收口为项目版本元信息治理问题。
- 在不新增 Beacon 一级公开主命令的前提下，给出确定性的人类面元信息 skill 与宿主 support surface。
- 将该变更固定为可继续 freeze / implement 的 requirement truth，而不是停留在 brainstorm 或开放命名阶段。

## Scope Delta

- 新增 `project-version metadata governance` 能力线
- 新增确定性人类面 skill：`beacon:beacon-project-metadata`
- 将宿主命令面固定收口到 `beacon doctor metadata ...`
- 将 CRUD + verify 能力写入 PRD / user-story / test-case
- 将 `friction-intake` 的绝对 `project_root` / 绝对 artifact path / latest pointer contract 纳入 requirement truth
- 将 domain classifier 的 `monorepo / branch-governance / repo-binding` 规则纳入 requirement truth
- 将“提示层必须按版本从运行层读取 resolved metadata view”纳入 requirement truth

## Added

- 新增 `v1.3.10` PRD：
  - `docs/beacon/v1.3.10/prd/beacon-v1-3-10-project-topology-and-version-branch-metadata-transaction-governance.md`
- 新增 `v1.3.10` User Story：
  - `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- 新增 `v1.3.10` Test Cases：
  - `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- 新增 machine coverage：
  - `.machine/user-story/...`
  - `.machine/qa/...ac-test-matrix.json`
  - `.machine/qa/...story-scenario-map.json`

## Fixed / Clarified

- 不再把“人类面元信息 support surface”保留为开放命名问题。
- 明确 skill 名称固定为 `beacon:beacon-project-metadata`。
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

## Not Added

- 未新增新的一级公开命令，例如 `metadata`、`change`、`revision`。
- 未把 sqlite 升级为唯一 truth source。
- 未扩张为完整项目编排系统。

## Readiness

- requirement clarity：已收口
- freeze readiness：已补齐
- 当前状态：可再次 freeze；冻结后进入实现补丁与 QA delta-run

## Traceability Refs

- `docs/beacon/v1.3.10/prd/beacon-v1-3-10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- `docs/beacon/v1.3.10/.machine/prd/beacon-v1-3-10-project-topology-and-version-branch-metadata-transaction-governance.canonical.json`
- `docs/beacon/v1.3.10/.machine/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.json`
- `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.ac-test-matrix.json`
