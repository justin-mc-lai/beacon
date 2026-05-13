---
name: beacon-toolkit-metadata
description: Use when the user wants deterministic project/version metadata inspection or CRUD operations through Beacon's metadata toolkit surface, without entering the main delivery workflow.
---

# Beacon Toolkit Metadata

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
