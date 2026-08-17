---
name: beacon-gov-metadata
description: Beacon v1.6.0 governor skill migrated from `beacon-toolkit-metadata`. Use when the user wants deterministic project/version metadata inspection or CRUD operations through Beacon's metadata toolkit surface, without entering the main delivery workflow.
---

# Beacon Governor Metadata

This skill routes metadata work through Beacon's `doctor metadata` support surface.

## Use for

- inspect current resolved metadata view
- list project topology / service binding / version contract state
- create project-level or version-level metadata records
- update existing metadata truth
- delete service bindings or version contracts
- verify runtime state against metadata contract

## Operator rule

Keep metadata operations outside the main workflow by default.

Prefer:

- `beacon doctor metadata show ...`
- `beacon doctor metadata list ...`
- `beacon doctor metadata create ...`
- `beacon doctor metadata update ...`
- `beacon doctor metadata delete ...`
- `beacon doctor metadata verify ...`
- or `beacon doctor metadata ...` (optional vendored wrapper: `bash skills/beacon/scripts/run_beacon.sh doctor metadata ...`)

Default expectations:

- treat `doctor metadata` as the human-facing deterministic metadata toolkit
- keep writes on the canonical metadata transaction path
- let runtime/project validation consume the resolved metadata view
- do not patch only one sink by hand

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the metadata result into the main Beacon workflow.

## Examples

- 适用例：
  - “我想先看当前项目/版本元信息到底被解析成什么。”
  - “我要修 metadata contract，但不想直接进入 implement/qa/release。”
- 不适用例：
  - “我现在要推进 feature 实现或验收。” -> 元信息检查结束后应回主链 surface

## Cold-start anchors

- `doctor metadata` 是确定性元信息治理面，不是 delivery 主链。
- 元信息写入必须走 canonical transaction path，不应单点手改某个 sink。
- metadata 结果可以影响主链判断，但不自动等于进入主链。


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

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-metadata` -> `beacon-gov-metadata`。
- 主要作用：确定性 metadata 工具。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-toolkit-metadata` -> `beacon-gov-metadata`。
- 主要作用：确定性 metadata 工具。
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
