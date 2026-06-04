# PRD: Beacon Implement Branch Gate（v1.1.12）

## 1. Problem Statement

Beacon 已经有 `git-alignment` 规则，但当前规则主要服务于：

- `workflow` 生成 execution artifacts
- `doctor verify-git-alignment`
- `gate check release`

问题在于 `implement run` 本身没有前置门禁。

这会导致：

1. 用户或 AI agent 在 `main` 上直接开始编码
2. 版本资料位于 `docs/beacon/<version>/`，但实际改动不发生在 `beacon/<version>` 分支
3. release/gate 才发现分支漂移，代价已经过晚

## 2. Product Principles

1. implement gate must be live, not artifact-only
2. one git policy, many consumers
3. coding should stop before runner starts
4. repair actions must be explicit and reversible
5. evidence should be written even for blocked runs

## 3. Goals

1. 为 `implement run` 增加强制 branch preflight
2. 提供显式的 `implement check-branch` 命令
3. 保证 workflow/gate/doctor/implement 共用同一套 git alignment 逻辑
4. 把 branch preflight 写成 implementation evidence
5. 在需要时支持显式 auto-switch 修复

## 4. Non-goals

1. 不在 implement 阶段接受 tag-only 放行
2. 不做隐式静默切分支
3. 不引入第二套分支命名规范
4. 不替代更晚阶段的 release gate / doctor 审计

## 5. Functional Requirements

### FR-001 Shared Git Alignment Helper

抽出共享 helper，至少可供：

- workflow execution artifact generation
- implement branch preflight
- future doctor/gate live checks

共同消费。

### FR-002 Implement Branch Preflight

`beacon implement run` 在 runner 解析前执行 branch preflight，输出：

- `expected_branch`
- `current_branch`
- `current_tag`
- `reason_codes`
- `recommended_command`
- `blocked`

### FR-003 Exact Branch Requirement

对 implement 阶段：

- 目标分支固定为 `beacon/<version>`
- 要求 `current_branch == target_branch`
- `allow_tag=false`
- `require_exact_branch=true`

### FR-004 Explicit Repair Surface

新增：

```bash
beacon implement check-branch --project-root . --version v1.1.12
```

并支持：

```bash
beacon implement check-branch --auto-switch-branch
beacon implement run ... --auto-switch-branch
```

### FR-005 Safe Switch Policy

当分支不匹配且启用 `--auto-switch-branch`：

- 优先 `git switch beacon/<version>`
- 本地分支不存在时允许 `git switch -c beacon/<version>`
- dirty worktree 且需要切换时必须阻断

### FR-006 Preflight Artifact

每次 preflight 写出：

```text
.beacon/implement/<run_id>/branch-preflight.json
```

blocked 结果也必须持久化。

### FR-007 Block Before Runner

若 preflight blocked：

- 不得调用 `resolve_adapter` 之后的执行路径
- 不得启动任何 runner/native implementation
- 必须返回 `implement_branch_guard_blocked`

## 6. Suggested Output Contract

```json
{
  "schema_version": "1.0",
  "status": "blocked",
  "version": "v1.1.12",
  "expected_branch": "beacon/v1.1.12",
  "current_branch": "main",
  "reason_codes": [
    "git_branch_target_mismatch",
    "git_version_ref_not_satisfied",
    "git_exact_branch_required"
  ],
  "recommended_command": "git switch beacon/v1.1.12",
  "blocked": true
}
```

## 7. Success Standard

这条线完成时，Beacon 应能稳定做到：

1. 在 `main` 或错误分支上调用 `implement run` 会先被挡住
2. `implement` 失败信息能直接告诉使用者切到哪个分支
3. `workflow` 与 `implement` 不再出现分支规则漂移
4. blocked 和 pass 都会留下 branch preflight evidence
