# Mode: pln-friction

> Archived from `beacon-pln-friction` during 1+6 merge. This is progressive disclosure content for `beacon-plan`.

# Beacon Planner Friction Intake

This skill routes optional friction governance work through Beacon's `friction-intake` support surface.
It is the primary `scan/capture` entry for Beacon friction governance.

## Use for

- scan Beacon source project friction, blockers, and bugs
- capture a manual friction note inside a target project
- classify friction into governance-ready queue items
- persist dual-write evidence into project-local artifacts and global sqlite
- decide whether a friction item should stay queue-only or be explicitly accepted for requirement/change

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon friction-intake run ...`
- optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh friction-intake run ...`

Default expectations:

- `scan` mode is for Beacon source-project friction discovery
- `capture` mode is for manual friction logging in a target project
- both modes write queue items into the global runtime-ledger sqlite
- project-local truth stays in `.beacon/debug/`, `.beacon/memory/`, `.beacon/analysis/`
- requirement/change routing stays explicit and opt-in

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly accepts the item for requirement/change routing.

## Recommended command shapes

```bash
beacon friction-intake run \
  --project-root . \
  --version v1.4.3 \
  --mode scan \
  --json
```

```bash
beacon friction-intake run \
  --project-root . \
  --version v1.4.3 \
  --mode capture \
  --note "QA run is blocked because acceptance dual-write did not materialize" \
  --json
```

## Examples

- 适用例：
  - “先把这个阻塞记成 friction，不要立刻升级成需求或变更。”
  - “我想扫描 Beacon 源码仓最近有哪些摩擦点值得进治理队列。”
- 不适用例：
  - “我已经决定把这个问题正式纳入 requirement/change。” -> 应显式路由进相应主链 surface

## Cold-start anchors

- `friction-intake` 先做 capture 和 queue governance，不默认升级成正式 truth。
- 它的价值是让摩擦显性化、可排队、可筛选，而不是立即进入主工作流。
- 只有当用户明确接受 requirement/change routing 时，才应继续进入主链。


> 共享守则（preamble / HARD GATE / GIT_ADMISSION）见 `skills/beacon/references/shared-preamble.md`
## GIT_ADMISSION (mandatory — Tier A/B when version+feature known)

Before ANY repo write or implement/qa/release route:
1. `beacon workspace admit --project-root . --version <v> --feature <slug> --json`
2. If status != pass → STOP; show reason_codes; do NOT edit files
3. Set cwd to worktree_path from payload
4. Do NOT git checkout elsewhere to "fix" branch
5. When admission is soft-skipped (`require_workspace_admission=false`), still verify `current_branch == resolved target_branch` before repo writes (R5 UD-024)
6. (implement only) Before writing implementation, merge `truth_canonical` into the development branch so implementation bases on canonical frozen truth

## v1.6.0 Harness Migration

- Harness：`planner`。
- 来源迁移：`beacon-friction-intake` -> `beacon-pln-friction`。
- 主要作用：摩擦记录、排队与只读治理。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-friction-intake` -> `beacon-pln-friction`。
- 主要作用：摩擦记录、排队与只读治理。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
