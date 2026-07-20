---
slug: branch-ref-hierarchy-collision-admit-main-fallback
version: v2.0.0
status: support_advisory
authority: beacon-pln-review
generated_at: 2026-07-20T00:30:00+08:00
user_utterance: "为啥还是会在 main 主分支进行实现；admit 因 beacon/v2.0.0 分支命名冲突失败，目录被设立成分支导致；应整理分支生成规则，严格工业限制后续不再因分支冲突"
recommended_route: beacon-gen-change
user_decision_required: true
planner_boundary:
  truth_write_allowed: false
  code_write_allowed: false
  machine_write_allowed: false
---

# Planner Review: Branch ref hierarchy 冲突 → admit 失败 → 误在 main 实现

## intent_snapshot

| 字段 | 值 |
|------|-----|
| original | 为何 admit 失败后仍在 main 实现；根因是 `beacon/v2.0.0` 与子路径分支冲突；要**整理分支生成规则**，工业级限制以后不再因冲突落 main |
| strong_signals | 「严格」「软件工业限制」「后续不再」= full fix + hard gate，禁止继续 soft fallback |
| non_negotiable | implement 不得在未 admit 的 main 脏工作区继续；admit 失败必须 fail-closed |
| evidence incident | `$beacon-goal` R3 implement：`workspace admit` → `workspace_admission_worktree_failed`（cannot lock `beacon/v2.0.0`）→ agent 在 main 继续写 |

## scope_mode

**`full_parity` 对「可工业使用的 branch/worktree 命名 + admit fail-closed」**  
不是 MVP「再写一段文档」。

## 湖/海

| | |
|--|--|
| 主湖 | **branch/worktree naming + admit materialize hard gate**（扩展既有 governance，不必新品牌） |
| 建议挂靠 | `loom-git-worktree-implement-harness` **或** `beacon-v2-rust-kernel-redesign` BranchContext 相关 AC；推荐 **独立 change** 进 worktree harness + execution_branch_contract |
| 海 | 全 GitFlow 企业变体、多 remote 命名空间 |

---

## 根因（已核实）

### 1. Git 物理约束（不可协商）

Git refs 是**前缀树**：

- 若存在 `refs/heads/beacon/v2.0.0/foo`，则 **不能** 再创建 `refs/heads/beacon/v2.0.0`
- 反之亦然

本仓库现状：

```text
EXISTS (children only):
  beacon/v2.0.0/beacon-v2-rust-kernel-redesign
  beacon/v2.0.0/dev-kernel-goal-delivery
  beacon/v2.0.0/goalrun-main-axis-sync
  beacon/v2.0.0/product-goal-parity-delivery

DOES NOT EXIST:
  beacon/v2.0.0   # parent leaf

create -c beacon/v2.0.0 → fatal: cannot lock ref ... 'refs/heads/beacon/v2.0.0/<child>' exists
```

### 2. Beacon 解析逻辑自相矛盾

| 层 | 行为 |
|----|------|
| `execution_branch_contract` **program-level** | 期望 branch ≈ `beacon/<version>`（聚合） |
| 历史 / per-feature 实现 | 真实 lane = `beacon/<version>/<feature-slug>` |
| `validate_workspace_admission` 注释 | **已知** “Git cannot host both beacon/\<version\> and beacon/\<version\>/\<feature\>” 并放宽 validate 接受子路径 |
| `ensure_expected_worktree_lane` / admit materialize | 仍尝试 **创建/切换父 branch** `beacon/v2.0.0` → 失败 |

即：**校验层已经承认冲突，创建层仍按父 branch 物化**。

### 3. 为何落到 main

1. admit **fail-closed** 正确返回 `workspace_admission_worktree_failed`
2. 流程文档要求 implement 仅 admitted worktree
3. agent/goal 在失败后 **没有工业级恢复路由**（创建 leaf branch / 使用已有 child lane）
4. 选择在 **main 未提交工作区**继续实现 → **过程违规**（用户正确质疑）

这不是「main 被选为合法 implement 树」，而是 **recovery 缺失 + soft 违规**。

---

## 推荐工业规则（写入 truth 的候选 UD）

### UD-BR-001 命名拓扑：禁止父子 ref 共存

任意时刻，对任意 prefix `P`：

- 禁止同时存在 ref `P` 与 `P/<anything>`
- admit / branch create **必须** preflight：`git check-ref-format` + ancestor/descendant scan
- 失败 reason_code：`branch_ref_hierarchy_collision`

### UD-BR-002 语义拆分：program namespace ≠ git leaf branch

| 概念 | 用途 | 合法形态示例 |
|------|------|----------------|
| program aggregation **namespace** | 路径/文档/策略 key | `v2.0.0` 或 worktree 目录 `.beacon/worktrees/v2.0.0/` |
| implement **git leaf branch** | 真实 checkout | `beacon/v2.0.0/<feature-slug>` **或** 扁平 `beacon/v2.0.0--<feature-slug>` |
| truth canonical | 写 truth | `main` / `master` only |

**禁止**把 program aggregation 名 `beacon/<version>` 当作 **必须存在的 leaf git branch**（当 children 可能存在时）。

### UD-BR-003 默认实现 lane（推荐方案 A）

**Always leaf-per-feature:**

```text
feature_branch = beacon/<version>/<feature-slug>
worktree_path  = .beacon/worktrees/<version>/<feature-slug>
```

- program-level 只影响 **policy / 路径根 / 并行拓扑**，不创建 `beacon/<version>` branch
- 与现有 child branches 兼容

**方案 B（扁平，彻底消灭斜杠父子）**：

```text
feature_branch = beacon/v2.0.0--<feature-slug>
```

代价：破坏已有 `beacon/v2.0.0/*` 命名；需迁移。

**推荐默认 A + preflight；迁移可选 B。**

### UD-BR-004 admit 失败禁止 main 实现

| Illegal | reason_code |
|---------|-------------|
| admit blocked 后在 main/canonical 写实现 | `implement_on_canonical_without_admission` |
| admit failed 静默 continue | `workspace_admission_soft_fallback_forbidden` |
| 用 `mkdir` 冒充 worktree | `mkdir_only_worktree_forbidden`（已有） |

**唯一合法恢复：**

1. preflight collision → 改用 leaf branch（自动 rewrite expected_branch）  
2. 或 fail 并打印 `git branch` 冲突列表 + 修复命令  
3. **绝不** fallback main 编码

### UD-BR-005 materialize 算法（Must）

```text
expected = resolve_lane_branch(version, feature)  # always leaf under rule
if ref_exists(expected): switch
elif ancestor_or_descendant_collision(expected):
    rewrite to safe leaf OR block with branch_ref_hierarchy_collision
else:
    create -c expected from base (main)
ensure worktree -- path dedicated
merge main into expected (conflict → block)
issue admission artifact
```

### UD-BR-006 历史债务清理（ops，非 silent）

对本仓：

- **不要**创建 `beacon/v2.0.0` parent  
- 保留 children 为合法 feature lanes  
- 文档/contract 中所有 `expected_branch: beacon/v2.0.0` 改为 leaf 或 namespace-only 字段

---

## parity / state_model（admit 相关）

### Domain entities

| Entity | 说明 |
|--------|------|
| BranchNamespace | version 聚合名（非 leaf） |
| FeatureLaneBranch | leaf git ref |
| WorktreeLane | path + admitted |
| RefHierarchyPreflight | pass/block |

### Illegal transitions

| From | To | Guard |
|------|-----|-------|
| admit_failed | implement_running_on_main | **forbidden** |
| program_namespace | git_leaf_parent_with_children | **forbidden** |
| materialize | create_parent_while_children_exist | **forbidden** |

---

## findings

### F-BR-001 P0 | intent-fidelity + process

- **issue**: 用户要求工业级禁止「admit 冲突 → main 实现」；现状 agent 可 soft 继续  
- **route**: change + implement hard gate in goal/implement  
- **user_decision_required**: true（是否对 goal/implement 一律 fail-closed）

### F-BR-002 P0 | source/runtime correctness

- **issue**: program-level 期望 `beacon/<version>` 与已有 `beacon/<version>/*` **物理不可共存**  
- **evidence**: git error + workspace_admission comments  
- **route**: `beacon-gen-change` 改 `execution_branch_contract` + admit materialize  

### F-BR-003 P1 | state-machine

- **issue**: validate 已接受 child lane，materialize 仍创建 parent → 状态机不一致  
- **route**: 统一 resolve 为 leaf-only  

### F-BR-004 P1 | coverage-shape

- **issue**: 缺 TC：创建 parent 当 children 存在 → block；admit fail 后 implement 被阻断  
- **route**: tests in worktree/branch governance package  

### F-BR-005 P2 | ops debt

- **issue**: 仓库已有 4+ child branches；parent 永不创建  
- **route**: inventory + docs fix；optional rename plan  

### F-BR-006 P0 | agent behavior（本 incident）

- **issue**: R3 steering implement 在 main 继续 = 违反 GIT_ADMISSION / worktree flow  
- **route**: 运行时强制；skill 明确「admit fail = STOP」；不得「为完成目标」绕过  

---

## deferral_ledger

| id | item | decision |
|----|------|----------|
| DEF-BR-01 | 扁平命名 `beacon/v2.0.0--slug` 全量迁移 | **pending**（推荐先 A） |
| DEF-BR-02 | 自动删除/重命名历史 parent 尝试 | N/A（parent 未创建） |
| DEF-BR-03 | 允许 main 紧急热修实现 | **pending user**（应仍 admit hotfix lane） |

---

## promotion_diff（accept 后 change 写入）

1. UD-BR-001..006  
2. AC：ref hierarchy preflight；program-level 不创建 parent leaf；admit fail 阻断 implement/goal implement stage  
3. Illegal I-BR-*  
4. Tests：collision fixture；rewrite-to-leaf；no main soft fallback  
5. Ops note：现有 `beacon/v2.0.0/*` 为合法 children  

## recommended_route

```text
beacon-gen-change
  primary: loom-git-worktree-implement-harness
           (+ execution_branch_contract / workspace_admission behavior)
  optional new slug: beacon-v2-branch-ref-hierarchy-gate
then implement (only on admitted leaf lane)
NOT: continue implementing on main
```

## 用户决策问卷

**1. 命名方案**  
- **A（推荐）**：始终 leaf `beacon/<version>/<feature-slug>`；program 只做 namespace/路径  
- **B**：扁平 `beacon/<version>--<feature-slug>`（需迁移计划）  

**2. admit 失败**  
- **A（推荐/工业）**：goal/implement **硬停**，禁止 main 写实现  
- **B**：仅 warn（不推荐）  

**3. 是否立即 change**  
- **A：GO** `$beacon-gen-change`  
- **B**：先只 research  

## 一句话

> **不是「实现应该在 main」**，而是 **program-level 把 `beacon/v2.0.0` 当 leaf branch，与已有 `beacon/v2.0.0/*` 子 ref 物理冲突 → admit 失败 → 错误恢复到 main**。  
> 修法：分支规则 **永远 leaf、禁止父子 ref 共存、admit fail 绝对禁止 main 实现**。
