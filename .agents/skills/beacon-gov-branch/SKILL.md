---
name: beacon-gov-branch
description: Beacon v1.6.0 governor skill migrated from `beacon-toolkit-branch-governance`. Use when the user wants a human-readable git branch/worktree governance view or verification through Beacon's doctor support surface.
---

# Beacon Governor Branch

This skill routes branch-governance inspection through Beacon's `doctor branch-governance` support surface.

## Use for

- inspect the resolved branch-governance template for a version
- show the branch flow diagram, current position, and recommended next action
- verify whether the governance contract is currently blocked
- review evidence-contract requirements before entering `implement`

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon doctor branch-governance show ...`
- `beacon doctor branch-governance verify ...`
- or `beacon doctor branch-governance ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor branch-governance ...`)

Default expectations:

- treat `doctor branch-governance` as the human-facing deterministic git governance surface
- keep project-level writes on the canonical metadata transaction path
- let `implement` consume the same projected contract instead of maintaining a second truth

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the governance result into the main Beacon workflow.

## Examples

- 适用例：
  - “我想知道当前 branch/worktree 治理位置和下一步 git 动作建议。”
  - “进入 implement 前，先确认 branch governance 有没有阻断。”
- 不适用例：
  - “我现在已经明确要开始实现功能本身。” -> branch 检查结束后应回 `beacon-gen-implement`

## Cold-start anchors

- `branch-governance` 解决的是 git/worktree 治理可见性，不是 feature 执行本身。
- 它应和 `implement` 共享同一投影契约，而不是维护第二套真相。
- 这个 surface 可以阻断进入执行，但不能替代执行入口。


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## GIT_ADMISSION (mandatory — Tier A/B when version+feature known)

Before ANY repo write or implement/qa/release route:
1. `beacon workspace admit --project-root . --version <v> --feature <slug> --json`
2. If status != pass → STOP; show reason_codes; do NOT edit files
3. Set cwd to worktree_path from payload
4. Do NOT git checkout elsewhere to "fix" branch
5. When admission is soft-skipped (`require_workspace_admission=false`), still verify `current_branch == resolved target_branch` before repo writes (R5 UD-024)

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-branch-governance` -> `beacon-gov-branch`。
- 主要作用：分支和工作区治理。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-branch-governance` -> `beacon-gov-branch`。
- 主要作用：分支和工作区治理。
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
