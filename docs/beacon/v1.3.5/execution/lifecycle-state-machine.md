# Beacon Lifecycle State Machine (v1.3.5 Draft)

## Purpose

这份文档把 Beacon 的 requirement-driven lifecycle 明确成一个可审计的状态机，并补齐“冻结后需求调整再闭环”的正式状态。

它服务两个目标：

1. 保持人类只记住 `7+3`
2. 让冻结后 change loop 有正式 machine-readable / human-readable 语义

## Human Surface Mapping

人类主链不变：

```text
prd
→ user-story
→ test-case
→ prototype
→ implement
→ qa
→ release
```

辅助面不变：

```text
help / status / doctor
```

冻结后需求调整通过宿主子 skill 进入：

```text
beacon-change
```

规则：

> `beacon-change` 是路由入口，不是新的 Beacon 一级主阶段。

## Internal States

### A. 初始化与立项

1. `context_bootstrap`
2. `requirement_drafting`
3. `requirement_structuring`
4. `acceptance_structuring`
5. `freeze_ready`
6. `prototype_freeze`

### B. 交付主闭环

7. `implementation_ready`
8. `implementation_in_progress`
9. `qa_ready`
10. `qa_verified`
11. `release_ready`
12. `released`

### C. 冻结后变更回环

13. `change_requested`
14. `revision_reopened`
15. `delta_recompiled`
16. `re_freeze_ready`
17. `fix_in_progress`
18. `re_qa_verified`
19. `re_release_ready`

## Primary Flow

```text
context_bootstrap
→ requirement_drafting
→ requirement_structuring
→ acceptance_structuring
→ freeze_ready
→ prototype_freeze
→ implementation_ready
→ implementation_in_progress
→ qa_ready
→ qa_verified
→ release_ready
→ released
```

## Post-freeze Change Loop

```text
released / qa_verified / implementation_in_progress
→ change_requested
→ revision_reopened
→ delta_recompiled
→ re_freeze_ready
→ fix_in_progress
→ re_qa_verified
→ re_release_ready
→ released
```

## State Definitions

### `context_bootstrap`

- 建立上下文、版本与 takeover baseline。

### `requirement_drafting`

- 进入命令面：`prd`
- 产物：PRD draft

### `requirement_structuring`

- 进入命令面：`user-story`
- 产物：user story / acceptance criteria

### `acceptance_structuring`

- 进入命令面：`test-case`
- 产物：test cases / AC-to-TC mapping

### `freeze_ready`

- 条件：PRD / user-story / test-case 形成 requirement truth，clarity gate pass

### `prototype_freeze`

- 进入命令面：`prototype`
- 产物：wireframe freeze bundle

### `implementation_ready`

- 进入命令面：`implement`
- 前置：branch/service preflight、git workflow contract、runtime/delegation precheck

### `implementation_in_progress`

- 进入命令面：`implement`
- 产物：implementation summary / technical archive / evidence manifest

### `qa_ready`

- 进入命令面：`qa`
- 前置：冻结基线已存在、implementation handoff 完整

### `qa_verified`

- 产物：feature scorecard / closure judgment / repair handoff

### `release_ready`

- 进入命令面：`release`
- 前置：gate pass、traceability intact

### `released`

- 终态类型：
  - initial delivery
  - revised delivery
  - hotfix delivery

### `change_requested`

- 触发条件：冻结后新增需求、边界补充、范围删减、hotfix 前需求补齐
- 推荐入口：`beacon-change`

### `revision_reopened`

- 触发动作：`reopen`
- 核心要求：新 revision id 生成，旧 frozen baseline 不被覆盖

### `delta_recompiled`

- 必须覆盖：
  - `prd revise`
  - `user-story refresh`
  - `test-case refresh`
  - `prototype refresh`

### `re_freeze_ready`

- 条件：delta compile 完整、clarity gate pass

### `fix_in_progress`

- 进入命令面：`implement fix` / `implement hotfix`
- 要求：implement 绑定最新 revision baseline

### `re_qa_verified`

- 进入命令面：`qa delta-run` / `qa regression-run`

### `re_release_ready`

- 进入命令面：`release recheck`

## Transition Rules

### Rule 1: 主链 truth 不变

runtime mode 可以变化，但 requirement truth 只能来自：

- `prd`
- `user-story`
- `test-case`
- `prototype`

### Rule 2: 冻结后变更必须 reopen

任何已经 frozen 的 feature 发生 requirement-level 变化，都必须先进入：

```text
change_requested → revision_reopened
```

### Rule 3: Re-freeze 前必须 delta compile 完整

如果只改了 PRD，没有刷新 user-story / test-case / prototype，则不能进入 `re_freeze_ready`。

### Rule 4: QA 与 release 必须绑定最新 revision

一旦新的 frozen revision 生成：

- implement 默认指向最新 revision
- qa 默认指向最新 revision
- release gate 默认指向最新 revision

## Artifact Boundary

### Human-readable artifacts

- PRD
- user story
- test cases
- prototype summary
- lifecycle state machine doc

### Machine-readable artifacts

- revision state
- story state
- requirement clarity writeback
- QA matrix / scenario map

### Runtime projections

- SQLite / runtime board / projection store

规则：

> human / machine / runtime projection 可以分层，但必须共享同一 revision truth。

## Routing Guidance

当 `status/help` 检测到以下条件时：

- feature 已冻结
- 用户表达 change intent

应推荐：

```text
beacon-change
→ reopen
→ prd revise
→ user-story refresh
→ test-case refresh
→ prototype refresh
→ freeze
→ implement fix
→ qa delta-run
→ release recheck
```

## Open Follow-up

1. `qa` 需要把 branch/service contract 复核纳入 revised baseline 验收面。
2. `release` 需要把 delivery type 作为正式字段输出。
3. `using-beacon` 后续需要把 `beacon-change` 纳入公共路由说明。
