# beacon-implement-branch-gate 测试用例

**版本**: v1.1.12
**Feature**: `beacon-implement-branch-gate`
**状态**: Draft
**更新时间**: 2026-03-31

---

## 1. 目标

验证 Beacon 在 implement 入口提供类似 gate 的前置分支校验，确保编码动作只会在 `beacon/<version>` 上开始。

---

## 2. 测试分组

| 组别 | 目标 |
|---|---|
| BG-TC-001 ~ 004 | branch preflight live check |
| BG-TC-101 ~ 103 | auto-switch repair |
| BG-TC-201 ~ 203 | workflow / evidence integration |

---

## 3. Branch preflight

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| BG-TC-001 | 目标分支通过 | 当前分支为 `beacon/<version>` 运行 `implement check-branch` | 返回 pass | unit |
| BG-TC-002 | 非版本分支阻断 | 当前分支为 `main` 运行 `implement run` | 返回 `implement_branch_guard_blocked` 且 runner 不执行 | integration |
| BG-TC-003 | tag-only 不放行 | detached HEAD 且 tag 命中版本 | implement preflight 仍 blocked | unit |
| BG-TC-004 | 非 git repo 阻断 | 在非 git 目录执行 implement | 返回 blocked | unit |

---

## 4. Auto-switch repair

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| BG-TC-101 | 显式 auto-switch 到已有分支 | 当前分支为 `main`，执行 `check-branch --auto-switch-branch` | 自动切到 `beacon/<version>` 并 pass | integration |
| BG-TC-102 | 显式 auto-switch 创建缺失分支 | 本地没有 `beacon/<version>`，执行 auto-switch | 创建并切到目标分支 | integration |
| BG-TC-103 | dirty worktree 阻断切换 | 当前分支错误且 worktree dirty，执行 auto-switch | blocked，并给出 dirty worktree 原因 | integration |

---

## 5. Workflow / evidence integration

| TC ID | 场景 | 关键步骤 | 预期结果 | 执行方式 |
|---|---|---|---|---|
| BG-TC-201 | preflight artifact | 运行 implement | 生成 `.beacon/implement/<run_id>/branch-preflight.json` | integration |
| BG-TC-202 | workflow delegate 复用同一规则 | workflow auto 进入 implementation 阶段 | 与 implement run 保持同样 branch 语义 | regression |
| BG-TC-203 | summary/state traceability | implement blocked 或 pass 后查看 state/summary | 包含 branch preflight 引用或内容 | regression |
