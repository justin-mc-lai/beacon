---
name: beacon-gov-hooks
description: Beacon v1.6.0 governor skill migrated from `beacon-project-hooks`. Use when the user wants to inspect, plan, dry-run, manually run, disable, or explain project-level Beacon lifecycle hooks under docs/beacon/hooks.
---

# Beacon Governor Hooks

## Overview

This skill routes project-specific lifecycle hook work through Beacon's governed `hooks` toolkit.

Project hooks are project-level extensions opened at finite Beacon lifecycle boundaries. They are not lifecycle stages, not requirement truth, and not QA or release verdicts.

## When to Use

- inspect project hook contracts
- plan a hook before a lifecycle boundary
- dry-run a hook without side effects
- manually confirm a side-effect hook
- disable a hook contract
- inspect latest hook evidence or blocker status

## Boundary

- hook truth lives only in `docs/beacon/hooks/<hook-id>.md`
- do not create canonical hook truth under `docs/beacon/<version>/hooks/`
- do not run arbitrary shell hooks
- do not allow hidden auto-run for side-effect hooks
- do not rewrite PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict

## Command

List hooks:

```bash
beacon hooks list --project .
```

Plan a hook:

```bash
beacon hooks plan "<hook-id>" --project . --version <version> --feature "<feature>"
```

Dry-run a hook:

```bash
beacon hooks run "<hook-id>" --project . --version <version> --feature "<feature>" --dry-run
```

Manually confirm a hook:

```bash
beacon hooks run "<hook-id>" --project . --version <version> --feature "<feature>" --confirm
```

Disable a hook:

```bash
beacon hooks disable "<hook-id>" --project .
```

Inspect status:

```bash
beacon hooks status "<hook-id>" --project . --feature "<feature>"
```

## Write Topology

- project hook truth: `docs/beacon/hooks/<hook-id>.md`
- runtime evidence: `.beacon/state/hooks/<hook-id>/<run-id>.json`
- latest read model: `docs/beacon/.machine/hooks/<hook-id>.latest.json`

The runtime evidence and latest read model are evidence only.

## Allowed Hook Codes

- `post_implement_pre_qa`
- `qa_diagnostics`
- `post_qa_pre_release`
- `post_release`

## Common Rationalizations

- “hook 成功了，所以 QA 通过。” -> 不允许；正式 QA 仍归 `beacon qa`。
- “release 后项目总是要安装，所以自动后台跑。” -> 不允许；高副作用 hook 必须手动确认。
- “这个 hook 只在 v1.4.10 用，所以放进 version 目录。” -> 不允许；hook contract 是项目级 truth。

## Verification

- `beacon hooks list` reads `docs/beacon/hooks`
- `beacon hooks plan` fails closed on invalid hook code or missing evidence declaration
- `beacon hooks run --dry-run` writes evidence without side effects
- `beacon hooks run --confirm` is required for side-effect hooks
- `beacon hooks status` never reports requirement, QA, release, gate, or freeze authority

## Cold-start Anchors

- Project hooks are governed project extensions, not lifecycle stages.
- Hook execution evidence is not requirement truth.
- Side-effect hooks require explicit operator confirmation.


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
- 来源迁移：`beacon-project-hooks` -> `beacon-gov-hooks`。
- 主要作用：生命周期 hook 合约。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-project-hooks` -> `beacon-gov-hooks`。
- 主要作用：生命周期 hook 合约。
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
