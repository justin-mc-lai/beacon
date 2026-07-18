---
slug: beacon-v2-parallel-cli-skill-naming
version: v2.0.0
status: support_advisory
authority: beacon-pln-review
kind: planner_review
date: 2026-07-18
user_intent: "v2 能否重新定义进化版 CLI/skill 名称，后续允许并行安装并验收"
related_truth:
  - docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md
  - docs/plans/beacon-v2-redesign.md
locked_upstream:
  - UD-V2-PGO-004 single public facade beacon-goal
  - AC-V2-PGO-006 Python CLI 入口保持 beacon goal
  - AC-V2-PGO-007 用户主路径仅 beacon-goal
  - DEF-SE-004 / AC-V2-PGO-011 reject early BEACON_V2=1 until W4
---

# Planner Review: v2 并行安装下的 CLI / Skill 命名

## intent_snapshot

| 字段 | 内容 |
|------|------|
| 用户原话 | v2 能否重新定义进化版 CLI/skill 名称，后续允许并行安装，进行验收 |
| 真实意图 | 在 **不打断 v1.6.7 生产可用** 的前提下，让 v2 有可安装、可验收的独立入口；避免“同名覆盖导致只能二选一” |
| 非意图 | 立刻砍掉 `$beacon-goal`；W4 前默认全站切 v2；第三套并列主编排 skill |

## scope_mode

- **scope**: 命名 / 安装 / 验收拓扑（CLI 包名、二进制名、host skill 名、环境开关）
- **lake_or_ocean**: **湖**（安装面命名策略），但触达 **海级** 产品入口一致性 → 必须与 product-goal 合同交叉
- **silent_scope_change_allowed**: false

## 现状（权威约束）

| 约束 | 来源 | 含义 |
|------|------|------|
| 唯一公共 facade | UD-V2-PGO-004 / AC-V2-PGO-007 | 用户主路径语义仍是 **goal 一句话交付**，不是 loop |
| CLI 兼容 | AC-V2-PGO-006 | **至少** 保留 `beacon goal` 形状 |
| 不提前默认 | DEF-SE-004 | W4 前不得默认 `BEACON_V2=1` |
| 规划已写并行包 | `docs/plans/beacon-v2-redesign.md` | 已有 `pip install beacon-v2`、PyO3 轮子、P4 并行期共存 |
| 当前 skill 文案 | `beacon-goal` SKILL | v2 docs 线与 v1.6.7 **共用** `$beacon-goal` + `--version` |

## Options（命名 / 安装拓扑）

### Option A — 同名单入口（现状）

| 面 | 名称 |
|----|------|
| pip | `beacon` only |
| CLI | `beacon` / `beacon goal` |
| skill | `$beacon-goal` |
| 切换 | `--version v2.0.0` 或以后 `BEACON_V2=1` |

- **优点**: 用户心智最简单；不破坏“唯一入口”
- **缺点**: **不能真正并行装两套 runtime**；升级即覆盖；v2 验收易污染 v1 生产
- **验收**: 难做“本机同时绿 v1 + v2”

### Option B — 并行包 + 显式进化名（推荐）

| 面 | v1.6.7（稳定） | v2（进化 / 验收轨） |
|----|----------------|---------------------|
| pip | `beacon` | **`beacon-v2`**（或 `beacon2`） |
| CLI 二进制 | `beacon` | **`beacon2`** 或 `beacon-v2` |
| skill 公共入口 | `$beacon-goal` | **`$beacon-goal-v2`**（或 `$beacon2-goal`） |
| skill support | `$beacon-loop-goal` | **`$beacon-loop-goal-v2`**（仅 support） |
| 内部子 skill | `beacon-gen-*` 等 | 初期 **复用同一仓库 skills** 或 `beacon2-gen-*` 镜像（二选一，见下） |

行为合同：

1. **语义同构**：v2 入口仍是“一句话 → 验收”，不是第二套产品哲学  
2. **安装正交**：`pip install beacon` 与 `pip install beacon-v2` **可同机共存**  
3. **PATH 不互相覆盖**：二进制名必须不同  
4. **验收独立**：`beacon2 release check v2.0.0` / 独立 scorecard 根  
5. **默认仍是 v1**：未装 v2 或未点 v2 入口时，行为与今天一致  
6. **W4 后可选**：`beacon` 主二进制内部切 spine，或 `beacon` 成为 `beacon2` 的 alias（人工 GO）

- **优点**: 真并行；真可验收；不违反“单一产品入口语义”（每轨各一个 goal skill）  
- **缺点**: 两套名字要教用户；文档要写清“生产用 goal / 验收用 goal-v2”  
- **与冻结 AC**: 用 **clarification** 解释 AC-V2-PGO-006：  
  - **Must 保留** `beacon goal` 兼容形状（shim 或 alias）  
  - **允许额外** `beacon2 goal` 作为 v2 显式轨  
  - 非“第二产品入口哲学”，而是 **第二安装轨**

### Option C — 仅环境开关、不改名（弱并行）

| 面 | 名称 |
|----|------|
| 同包 | `beacon` |
| 切换 | `BEACON_V2=1` / `BEACON_RUNTIME=v2` |

- **优点**: 实现便宜  
- **缺点**: 仍是单安装；验收与生产抢同一 `~/.local/bin/beacon`；与“并行安装”意图不符  
- **判定**: **不满足**用户“并行安装”主意图

### Option D — 全量 skill 改名前缀（重）

33 个 skill 全部 `beacon2-*`  
- **优点**: 最干净隔离  
- **缺点**: agent 面爆炸；与 redesign“33 skill 目录不变”冲突；成本高  
- **判定**: **P2+**，仅当 host skill 解析无法按 package 隔离时再上

## 推荐冻结决策（待用户 GO）

### GO 推荐：**Option B（并行包 + 显式进化名）**

| ID | 建议锁定 | 值 |
|----|----------|-----|
| UD-V2-NAM-001 | 并行安装 | **允许** v1 `beacon` 与 v2 `beacon-v2` 同机 |
| UD-V2-NAM-002 | v2 CLI 名 | **`beacon2`**（短）或 **`beacon-v2`**（显式）；推荐 **`beacon2`** 输入成本更低 |
| UD-V2-NAM-003 | v2 公共 skill | **`$beacon-goal-v2`**（唯一 v2 用户入口） |
| UD-V2-NAM-004 | v1 入口 | **保留** `$beacon-goal` / `beacon goal` 不变 |
| UD-V2-NAM-005 | 子 skill | **Phase-1 共享** `skills/beacon/*` 内容；CLI 调度进 v2 runtime；Phase-2 若冲突再镜像 `skills/beacon2/` |
| UD-V2-NAM-006 | 验收命令 | `beacon2 goal run ...` + `beacon2 release check v2.0.0` |
| UD-V2-NAM-007 | 默认 | 安装 `beacon-v2` **不** 改写 `beacon`；W4 前 **不** 默认 alias |
| UD-V2-NAM-008 | 与 AC 关系 | AC-V2-PGO-006/007 解释为 **语义单入口**；**安装轨可双轨** |

### 不推荐

| 方案 | 原因 |
|------|------|
| 只改 skill 名不改 CLI | agent 调 skill 与用户终端不一致 |
| 只改 CLI 不改 skill | host 仍可能加载 v1 skill 文案 |
| 默认装 v2 覆盖 `beacon` | 破坏生产；违反 DEF-SE-004 |
| 第三公共入口（如 `beacon-loop-v2` 并列 goal） | 重开 dual-entry 债 |

## 并行安装 / 验收拓扑（目标态）

```text
本机:
  ~/.local/bin/beacon      → package beacon==1.6.7     生产
  ~/.local/bin/beacon2     → package beacon-v2==0.x    验收/进化

Agent skills:
  $beacon-goal             → 生产轨（v1.6.7）
  $beacon-goal-v2          → 验收轨（v2 spine / docs v2.0.0）

状态/数据（建议）:
  v1: 项目 .beacon/ + 既有约定
  v2: 全局 ~/.beacon/beacon.db（plan）+ 可选 BEACON2_STATE_DIR
  禁止两轨静默写同一权威库而不标注 runtime
```

### 验收矩阵（并行安装后）

| 检查 | v1 | v2 |
|------|----|----|
| which CLI | `beacon --version` → 1.6.7 | `beacon2 --version` → 2.x/0.x |
| skill 加载 | goal 不要求 v2 | goal-v2 指向 v2 路由 |
| 一句话 goal | `beacon goal run` | `beacon2 goal run` |
| release | `beacon release check v1.6.7` | `beacon2 release check v2.0.0` |
| 互不覆盖 | 卸 v2 不影响 v1 | 卸 v1 不影响 v2（理想） |

## Findings

| ID | Sev | Finding |
|----|-----|---------|
| F-01 | P0 | **可以**重新定义 v2 进化名，且 **应该** 为“并行安装+验收”服务；否则 v2 只能 docs-line 或覆盖装 |
| F-02 | P0 | 与冻结 AC **不冲突**，若采用 **语义单入口 + 安装双轨** 解释；需用户 GO 写进 change/truth |
| F-03 | P0 | 仅 `BEACON_V2=1` **不满足**“并行安装” |
| F-04 | P1 | redesign 已预留 `beacon-v2` pip 名；应与 skill `$beacon-goal-v2` **成对**，避免 CLI/skill 分叉 |
| F-05 | P1 | Phase-1 不必 fork 33 skill 目录；先 **双二进制 + 双 facade skill** 即可验收 |
| F-06 | P1 | 状态目录必须轨隔离，否则并行验收会污染生产 goal run |
| F-07 | P2 | W4 后“`beacon` alias 到 v2”是可选迁移，不是 Day-1 |

## deferral_ledger

| 项 | 决定 | 理由 |
|----|------|------|
| 33 skill 全量 `beacon2-*` 前缀 | **延后** | 成本高；Phase-1 不必要 |
| W4 前 `beacon` 默认指向 v2 | **拒绝** | DEF-SE-004 |
| 废弃 `$beacon-goal` | **拒绝** | 生产连续性 |
| v2 专用状态根 `~/.beacon-v2` 或 env | **建议采纳**（实现阶段） | 并行验收隔离 |

## state_model（安装面）

| 状态 | 含义 |
|------|------|
| v1_only | 仅 beacon 包 |
| dual_installed | beacon + beacon-v2 同机 |
| v2_default_alias | W4+ 可选：`beacon`→v2（人工 GO） |
| v1_removed | 仅 v2（远期） |

非法：`dual_installed` 但两轨写同一未标注权威库；`v2_default_alias` 在 W4 前。

## recommended_route

```text
User GO on UD-V2-NAM-001..008
  → beacon-gen-change v2.0.0
     lake: beacon-v2-parallel-install-surface（新湖）或并入 beacon-v2-product-goal-orchestrator R4
  → freeze 命名合同 + 并行验收矩阵
  → implement: packaging (beacon-v2 wheel) + beacon2 CLI + skill beacon-goal-v2
  → eval-qa: dual-install matrix
  → release: human gate（docs + optional preview wheel；不默认替换 beacon）
```

## 大白话结论

1. **能改名吗？** 能，而且 **为了并行安装，应该给 v2 单独名字**。  
2. **推荐叫啥？**  
   - 包：`beacon-v2`  
   - 命令：`beacon2`  
   - 用户 skill：`$beacon-goal-v2`  
   - 生产继续：`beacon` + `$beacon-goal`  
3. **算不算两个入口？** 算两个 **安装轨**，不是两套产品哲学；每轨各自仍是“唯一 goal 入口”。  
4. **和现有 v2 合同？** 不推翻；要 **change/refreeze** 写清“兼容保留 + 显式进化轨”。  
5. **下一步**：你确认 GO 后走 `beacon-gen-change`，不要直接改代码。

## User decisions needed（请选）

1. v2 CLI 名：`beacon2`（短） vs `beacon-v2`（显式）  
2. v2 skill 名：`beacon-goal-v2` vs `beacon2-goal`  
3. 子 skill：Phase-1 共享 vs 立即全镜像  
4. 是否新建湖 `beacon-v2-parallel-install-surface` vs 并入 orchestrator R4  

**Planner 默认推荐**：`beacon2` + `$beacon-goal-v2` + Phase-1 共享子 skill + **新湖**（安装面独立验收，不绑架 orchestrator 语义）。
