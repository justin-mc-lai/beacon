# User Story: Beacon implement 分支前置门禁（v1.1.12）

**Feature**: `beacon-implement-branch-gate`
**Version**: `v1.1.12`

## Story

**As a** 使用 Beacon skill/CLI 发起实现编码的开发者、AI coding agent、release owner
**I want** `beacon implement run` 在真正拉起 runner 之前先强制校验当前 git 分支是否命中 Beacon 版本分支
**So that** 实现动作不会在 `main`、错误 feature branch 或 detached HEAD 上开始，保证 Beacon 版本资料与实际编码分支一致

## Story Slices

### US-001: Implement 入口必须有 live branch preflight
作为 release owner，我希望 `implement` 入口实时检查 git 状态，而不是依赖旧的 execution artifact。

### US-002: Implement 阶段必须精确命中版本分支
作为 AI coding agent，我希望编码前必须位于 `beacon/<version>`，只满足 tag 或前缀不够。

### US-003: skill/wrapper 不得绕过门禁
作为 Beacon 维护者，我希望 `skills/beacon/scripts/run_beacon.sh`、`workflow` 委托、CLI 直调都经过同一套门禁。

### US-004: 失败时必须给出修复命令
作为使用者，我希望被拦截时能直接看到推荐切分支命令，而不是只收到模糊 blocked。

### US-005: 显式 auto-switch 可以作为修复动作
作为高级用户，我希望在明确指定时允许 Beacon 先切到目标分支，再继续实现。

### US-006: preflight 必须成为实现证据
作为审计方，我希望实现运行目录里保留 branch preflight 结果，后续 review/debug 可以回溯。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Live Check | `implement run` 进入 runner 解析前必须执行 live git branch preflight |
| AC-002 | Exact Branch | 对 `--version vX.Y.Z`，实现阶段必须要求 `current_branch == beacon/vX.Y.Z` |
| AC-003 | No Tag Shortcut | implement 阶段不得因为 exact tag 命中版本而放行 detached HEAD / tag-only 状态 |
| AC-004 | Unified Surface | `implement run`、`implement check-branch`、workflow implementation delegate 必须共用同一套分支判断逻辑 |
| AC-005 | Blocked Reason | 分支不匹配时返回结构化 blocked 结果，至少包含 `expected_branch/current_branch/reason_codes/recommended_command` |
| AC-006 | Preflight Artifact | 每次 implement preflight 都写出 `.beacon/implement/<run_id>/branch-preflight.json` |
| AC-007 | Runner Isolation | preflight blocked 时不得继续解析或执行 runner |
| AC-008 | Explicit Repair | `--auto-switch-branch` 仅在显式声明时允许切换/创建目标分支 |
| AC-009 | Safe Switch | worktree dirty 且需要切分支时，preflight 必须阻断并说明原因 |
| AC-010 | Compatibility | 现有 workflow git alignment / doctor / gate 语义保持一致，不产生第二套版本分支规则 |

## First-principles Loop

正确链路应是：

```text
resolve version
→ live branch preflight
→ [optional explicit auto-switch]
→ re-check branch alignment
→ resolve runner
→ implement execution
→ implementation evidence
```

而不是：

```text
resolve runner
→ start coding
→ release gate 才发现分支错了
```
