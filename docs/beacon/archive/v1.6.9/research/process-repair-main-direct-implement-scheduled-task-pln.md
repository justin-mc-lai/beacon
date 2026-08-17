# Plan: 修复「main 直改 implement」过程违规（scheduled-task 双轨 worktree）

**Surface**: `$beacon-plan`  
**Status**: plan only — not implement / not freeze  
**Incident**: commit `2e5592c1` 在 **main checkout** 直接落地 `beacon task` 实现；双轨仅有 feature 文档包，**无** admitted worktree / goal admit 硬闸 / 并行 leaf。  
**Constraint**: `main...origin/main [ahead 1]`（截至 plan 时 **未 push**）→ 修复窗口仍宽。

---

## 0. plan_artifact.v1

| Field | Content |
|-------|---------|
| surface_ask | 怎么修复「不是正常双轨 worktree 并行 goal」的问题 |
| deep_want | **过程权威补齐**：让 scheduled-task 进入 pool/admit/leaf 叙事；防止再 main 直改；代码正确性可保留，但 **交付路径要合规** |
| non_goals | plan 不写业务新功能；不 force push 已公开历史（若已 push 则禁止 rewrite）；不 cherry-pick 当日常对齐主手段 |
| high_risk | 是 — git 历史 / 双轨合并 / 与已有 main tip 关系 |

---

## 1. 问题诊断（根因，不是症状）

| 缺失项 | 规范要求 | 事故表现 |
|--------|----------|----------|
| workspace admit | implement 前必 admit | 未调用 |
| real worktree | cwd = worktree_path | 在 main 树写代码 |
| 双 leaf | v1.6.9 + v2.0.0 各一轨 | 无 branch / 无 worktree |
| goal 状态机 | goal run + stage_trace | 聊天直改 |
| merge-main | leaf merge baseline | 单 commit 落 main |
| 双轨实现 | 可并行 | 仅 Python 一份 + v200 文档 parity |

**已合规部分（可保留）**  
- truth 包在 canonical 路径（双 docs 包）— 符合「truth on main」。  
- 单元测试与 CLI 行为基本可用。

**需修复部分**  
- implement 路径权威、pool 登记、goal 证据、后续变更门禁。

---

## 2. 修复策略对比

| 方案 | 做法 | 适用 | 优点 | 风险 |
|------|------|------|------|------|
| **A. 事后登记（Backfill admit）** | 从当前 main tip 建双 feature branch + worktree；`workspace admit`；在 leaf 上跑 precheck/qa；写 process_repair 证据；main 代码不动 | **已 commit、未/已 push 都可用** | 不改写历史；快 | 历史仍显示「曾在 main 直改」，靠 evidence 说明 |
| **B. 严格重放（Replay on leaf）** | main 回退到 `a5546167`，双 leaf 上重放 2e5592c1，再 merge 回 main | **仅未 push** 时推荐 | 历史干净，符合教科书流程 | 需 transient reset；协作中慎用 |
| **C. 仅文档认错** | 只写 incident note | 不可接受作唯一手段 | 零成本 | **不闭合** 硬闸/pool |
| **D. 拆 commit 重做** | 拆 truth vs code 两次合入 | 过度工程 | 更清晰 | 收益有限 |

### 推荐

| 条件 | 推荐 |
|------|------|
| **仍 ahead 1、未 push** | **B 优先**（严格重放），时间紧则 **A** |
| **已 push origin** | **只用 A**（禁止 rewrite main） |
| 长期防再发 | A/B 之后必做 **§5 复发防护** |

---

## 3. 方案 B — 严格重放（未 push 时）

> 目标：让 `git log` 呈现「truth@main → admit leaf → implement@leaf → merge main」。

### B0. 预备

```bash
# 确认未 push
git status -sb   # 应为 ahead N，无 behind
# 记下 tip
TIP=$(git rev-parse HEAD)          # 期望 2e5592c1
BASE=$(git rev-parse HEAD~1)       # 期望 a5546167
```

### B1. 保护 tip

```bash
git branch backup/scheduled-task-main-direct "$TIP"
```

### B2. main 回到实现前（软回退，工作区干净时）

```bash
git switch main
git reset --hard "$BASE"    # 丢弃 main 上 2e5592c1；代码在 backup 分支
```

### B3. 双轨 worktree materialize + admit

```bash
# v1.6.9 leaf
git branch beacon/v1.6.9/beacon-scheduled-task-agent-suspend-v169 "$BASE"
git worktree add \
  .beacon/worktrees/v1.6.9/beacon-scheduled-task-agent-suspend-v169 \
  beacon/v1.6.9/beacon-scheduled-task-agent-suspend-v169

beacon workspace admit -p . -v v1.6.9 \
  --feature beacon-scheduled-task-agent-suspend-v169 --json

# v2.0.0 leaf
git branch beacon/v2.0.0/loom-scheduled-task-agent-suspend-v200 "$BASE"
git worktree add \
  .beacon/worktrees/v2.0.0/loom-scheduled-task-agent-suspend-v200 \
  beacon/v2.0.0/loom-scheduled-task-agent-suspend-v200

beacon workspace admit -p . -v v2.0.0 \
  --feature loom-scheduled-task-agent-suspend-v200 --json
```

### B4. 在 **v169 leaf** 重放实现（代码权威轨）

```bash
WT169=.beacon/worktrees/v1.6.9/beacon-scheduled-task-agent-suspend-v169
git -C "$WT169" merge --ff-only "$TIP"   # 或 cherry-pick 2e5592c1 仅此修复例外
# 在 WT169 跑测
(cd "$WT169" && python3 -m pytest -q tests/test_v169_scheduled_task.py)
```

> 对齐主线用 **merge/ff**，不要用 cherry-pick 当日常。此处 tip 本身是单 commit，ff/merge 等价。

### B5. 在 **v200 leaf** 合入同一功能 + 确认 v200 文档包

```bash
WT200=.beacon/worktrees/v2.0.0/loom-scheduled-task-agent-suspend-v200
git -C "$WT200" merge --ff-only "$TIP"
# v200 侧重：truth 包已在 tip；可选 loom CLI 别名文档说明，不强制第二套 Python
(cd "$WT200" && python3 -m pytest -q tests/test_v169_scheduled_task.py)
```

### B6. 合回 main（主星）

```bash
git switch main
git merge --no-ff beacon/v1.6.9/beacon-scheduled-task-agent-suspend-v169 \
  -m "merge: scheduled-task v169 from admitted worktree"
# 若 v200 与 v169 同 tip 内容，再 merge v200 应 fast-forward/already up-to-date
git merge --no-ff beacon/v2.0.0/loom-scheduled-task-agent-suspend-v200 \
  -m "merge: scheduled-task v200 parity lane"
```

### B7. Goal 证据补记（推荐）

```bash
beacon goal run "process-repair scheduled-task dual worktree" -p . -v v1.6.9 --no-longrun --json
# status / heartbeat 注明：implement already on admitted leaf; process_repair
```

### B8. 清理

- 保留 backup 分支直至 push 后稳定。  
- `.beacon/tasks/` smoke 数据勿提交。

---

## 4. 方案 A — 事后登记（已 push 或要快）

> 目标：不 rewrite；**补齐 leaf + admit + pool + 证据**；后续变更必须在 leaf。

```bash
TIP=$(git rev-parse main)

# 双轨 branch = 当前 tip（已含实现）
git branch beacon/v1.6.9/beacon-scheduled-task-agent-suspend-v169 "$TIP"
git branch beacon/v2.0.0/loom-scheduled-task-agent-suspend-v200 "$TIP"

git worktree add \
  .beacon/worktrees/v1.6.9/beacon-scheduled-task-agent-suspend-v169 \
  beacon/v1.6.9/beacon-scheduled-task-agent-suspend-v169
git worktree add \
  .beacon/worktrees/v2.0.0/loom-scheduled-task-agent-suspend-v200 \
  beacon/v2.0.0/loom-scheduled-task-agent-suspend-v200

beacon workspace admit -p . -v v1.6.9 \
  --feature beacon-scheduled-task-agent-suspend-v169 --json
beacon workspace admit -p . -v v2.0.0 \
  --feature loom-scheduled-task-agent-suspend-v200 --json

# 在 leaf cwd 重跑测试 = QA 证据
(cd .beacon/worktrees/v1.6.9/beacon-scheduled-task-agent-suspend-v169 && \
  python3 -m pytest -q tests/test_v169_scheduled_task.py)
```

**必须补写**（main 上 truth 允许）：

`docs/beacon/archive/v1.6.9/features/beacon-scheduled-task-agent-suspend-v169/evidence.md`  
增加 section：

```markdown
## Process repair
- incident: main-direct implement (2e5592c1)
- repair: backfill worktree + workspace admit YYYY-MM-DD
- lanes: beacon/v1.6.9/...  & beacon/v2.0.0/...
- policy: subsequent code changes only on admitted worktrees
```

v200 evidence 同步一行。

**后续任何代码改动**：只在 worktree 改 → merge main；**禁止**再 main 直改。

---

## 5. 复发防护（P0，与 A/B 捆绑）

| 措施 | 说明 |
|------|------|
| P-1 goal 入口检查清单 | `$beacon-goal` implement 前强制打印 admit JSON 路径 |
| P-2 人工习惯 | feature 实现前先 `workspace admit --dry-run` |
| P-3 doctor 可选 | `beacon doctor` 警告：main 上出现业务实现 commit 且无对应 pool 登记（后置湖） |
| P-4 本会话 | Codex/agent **默认** 不在 main 改 `beacon/**` 业务代码，除非 truth-only |

**不在本修复 plan 实现 P-3 代码**（另开湖）；P-1/P-2 立即执行。

---

## 6. 双轨「并行」在修复中的含义

| 轨 | 修复动作 |
|----|----------|
| v1.6.9 | **实现权威轨**：Python `beacon task` + tests 在此 leaf 验证 |
| v2.0.0 | **合同/parity 轨**：同一代码合并 + loom 文档包；后续 Rust 再演进 |

并行 ≠ 两套重复实现；并行 = **两 admit leaf 同时存在、各自 merge main、各自证据**。  
与 `main_star_satellite_pool` 一致：主星 main，卫星两 leaf。

---

## 7. 验收（修复完成定义）

| AC-PR | 断言 |
|-------|------|
| AC-PR-001 | 存在 real worktree 目录：`…/v1.6.9/beacon-scheduled-task-…` 与 `…/v2.0.0/loom-scheduled-task-…` |
| AC-PR-002 | 两 branch 存在且 `git worktree list` 可见 |
| AC-PR-003 | `beacon workspace admit` 对两 feature 均 pass（或 switched） |
| AC-PR-004 | 在 **worktree cwd** pytest 绿 |
| AC-PR-005 | evidence 含 process_repair 记录 |
| AC-PR-006 | 无新业务功能混入；仅过程修复 |
| AC-PR-007 | 若走 B：main 历史含 merge from leaf；若走 A：pool/worktree 已登记且后续只在 leaf 改 |

---

## 8. recommended_next

1. 用户二选一：**B（未 push 严格）** 或 **A（快速 backfill）**。  
2. `$beacon-goal` 执行修复步骤（process-repair，非新功能）。  
3. 通过 AC-PR-* 后，再 `git push origin main`（若尚未 push）。  
4. 正式 release 仍人工门。

---

## 9. 一句话

**修复 = 把已经写在 main 上的实现「收编」进双轨 admitted worktree 权威路径（重放或事后登记），并写 process_repair 证据；不是再改一遍业务功能。**
