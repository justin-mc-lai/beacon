# Plan: Host Skill 简洁性 + Hotfix 主线热修 + 无版本默认（v1.6.9）

**Surface**: `$beacon-plan`  
**Status**: plan only — not frozen truth  
**Date**: 2026-07-21

## 0. plan_artifact.v1

| Field | Content |
|-------|---------|
| surface_ask | agent host skill 提示词如何足够简洁；hotfix 生产事故主分支热修但登记 hotfix 分支；提示词无版本时默认最新基线并 *.*.1 迭代 |
| deep_want | **低 token 稳定触发** + **两条清晰默认路径**（正常交付 vs 生产热修）+ **版本零摩擦**，框架自愈不塞进 skill 正文 |
| non_goals | plan 不改代码；不削弱 human release；不恢复 automation daemon |
| high_risk | 是 — 与「main 禁业务 commit / worktree admit」硬闸存在张力，需 UD 划例外 |

---

## 1. 第一性原理：host skill 为什么会膨胀

Host skill 的唯一工作是：

> **把用户意图路由到正确 harness，并给出最少不可协商约束。**

它**不是**手册、不是全部 CLI 百科、不是 history changelog。

| 原理 | 推论 |
|------|------|
| P1 认知负载 | skill 越长，agent 越容易忽略 HARD GATE |
| P2 单一职责 | 每个 public skill 只回答「何时用我 + 禁止什么 + 下一步一条命令」 |
| P3 渐进加载 | 细节放 `references/` / progressive_loads；默认不加载 |
| P4 运行时权威 | 版本解析、admit、自愈由 **CLI/runtime** 做，skill 只写「去调 CLI」 |
| P5 双场景分型 | **normal delivery** vs **prod hotfix** 两套默认，禁止第三套含糊流程 |

### 现状（简洁性债）

| Skill | 约行数 | 问题 |
|-------|--------|------|
| beacon-goal | ~250 | longrun/axis/fleet/hotfix/UD-ENF 全堆入口 |
| 其它 harness | ~50–80 | 尚可接受 |
| 用户负担 | 高 | 每次 $goal 吃满长文 |

**目标形态**：goal ≤ **80 行** 稳定；细则全部 progressive。

---

## 2. 简洁结构（推荐「三层洋葱」）

```text
L0  Host-visible SKILL.md（极薄）
    - 一句话职责
    - 触发词
    - 3 条 HARD GATE
    - 一条默认命令模板
    - 「细节 → references / CLI」

L1  references/*.md（按需）
    - git-worktree-execution-flow.md
    - hotfix-prod-incident.md
    - version-default.md

L2  Runtime（真相）
    - resolve_docs_version / resolve_runtime_version
    - build_hotfix_plan
    - implement_lane_enforcement + hotfix exception
    - progressive-map self_heal
```

### L0 模板（goal 示例，概念）

```markdown
# beacon-goal
一句话目标 → plan→truth→implement→qa→release（人工 release）

## 默认
beacon goal run "<目标>" -p . -v auto

## 两场景
1) 正常交付：admit worktree → leaf 实现 → merge main
2) 生产热修：见 references/hotfix-prod-incident.md（主线热修 + 登记 hotfix 分支）

## HARD
- 不自证 complete / 不 auto-release
- 无版本 → runtime 解析（见 version-default）
- 正常交付禁止 main 直写业务；热修走 hotfix 例外合同

## 细节
references/…  |  progressive_map
```

**Skill 正文禁止**：贴全文 version-truth、贴 7 层 CLI、贴历史 v1.6.x 变更表。

---

## 3. 场景 A — 发布后生产事故 Hotfix

### 3.1 用户意图（锁定）

> 生产出事 → **直接在主线热修**，**不进功能开发分支 / 常规 feature worktree 流**；  
> 但必须 **登记 hotfix 分支**（可追溯、可 forward-port、可回滚说明）。

### 3.2 与现状张力

| 现状合同 | 用户意图 |
|----------|----------|
| implement 默认 admitted leaf worktree | 热修在 **main 生产基线** 上修 |
| pre-commit 禁 main 业务 commit | 热修需要 **受控 main 写入** |
| hotfix 要求 forward_port + rollback_notes | 保留 |
| I-HF-003 禁止 next_feature 当第一生产落点 | **支持**用户：先打在生产基线 |

### 3.3 推荐流程（简洁、可写进 skill 四行）

```text
detect: 生产|线上|事故|hotfix|紧急回滚
  → mode = hotfix
  → baseline = current_runtime_release_line（或 --from-version）
  → branch = hotfix/<baseline>-<slug>   # 从生产 tag/baseline 拉出
  → 实现：在 hotfix 分支上改（可 worktree 指向该分支，cwd 可等于 main 检出的 hotfix 分支，
          或 short-lived worktree 绑定 hotfix/*，**不是** beacon/vX/feature 开发轨）
  → QA: release --profile hotfix（最小门）
  → 合入：生产主线 / release 分支（人工）
  → 登记：forward_port → 开发/规划线（main next / v2）
  → 永不 auto-release
```

**关键定义：什么叫「主分支热修」**

| 含义 | 推荐解释 |
|------|----------|
| ❌ 在脏 `main` 上直接 commit 无记录 | 禁止（与 UD-ENF 冲突且不可审计） |
| ✅ **生产基线（main/release tag）为起点**，立刻切 **`hotfix/*` 分支** 热修 | **采用** |
| ❌ 走 `beacon/v1.6.9/long-feature-slug` 开发 lake 流 | 热修 **不走** |

即：**语义上「贴着主线热修」；Git 上「hotfix 短分支登记」**，不是「无分支乱写 main」。

### 3.4 与 UD-ENF 的衔接（必须写进合同）

| 规则 | 内容 |
|------|------|
| UD-HF-MAIN-001 | hotfix 模式允许在 **hotfix/** 分支提交业务路径（pre-commit 放行 leaf 非 main 已满足；若 checkout 名是 main 则 **拒绝**，必须先 `git switch -c hotfix/...`） |
| UD-HF-MAIN-002 | **禁止** `mode=hotfix` 却在 `beacon/v*/feature-*` 开发 worktree 开工（防走偏） |
| UD-HF-MAIN-003 | 合并回生产线后，**必须**有 forward_port 任务到 next（开发线） |
| UD-HF-MAIN-004 | emergency 仅当无法建分支时用 `BEACON_ALLOW_MAIN_IMPLEMENT` + exception evidence（保留逃生） |

### 3.5 Skill 里只留 4 行

```text
生产事故 → --mode hotfix
baseline 默认 = current_runtime_release_line
分支 = hotfix/<baseline>-<slug>（从 baseline 创建，不进 feature 开发轨）
release = --profile hotfix + 人工确认 + 登记 forward-port
```

细节 → `skills/beacon/references/hotfix-prod-incident.md`。

---

## 4. 场景 B — 提示词没有版本

### 4.1 用户意图

> 默认 **当前最新版本基线**，并 **自动 *.*.1 patch 迭代**（或其它清晰规则）。

### 4.2 推荐默认（分模式）

#### Normal 交付（非热修）

| 步骤 | 规则 |
|------|------|
| 1 解析 docs 线 | 沿用 `resolve_docs_version(auto)`：onboarding → contract → **docs_default_line** → scan |
| 2 若落在 **已发布 runtime 线** 且意图是「新功能」 | **自动开 patch 迭代线**：`baseline = current_runtime_release_line`，`target = bump_patch(baseline)` → e.g. `v1.6.8` → **`v1.6.9`** |
| 3 若已存在更高 planning 线（如 docs 已有 v1.6.9） | **优先用已有 planning 线**，不再盲目 +1 |
| 4 双轨关键词 | 才拆 v1.6.x + v2.0.0；无关键词不自动 loom |

**「*.*.1」精确算法（推荐）**

```text
function default_target_version(project):
  runtime = current_runtime_release_line()     # e.g. v1.6.8
  planning = max(planning_lines ∪ scanned docs that > runtime)
  if planning exists and planning > runtime:
    return planning                            # e.g. already v1.6.9
  else:
    return bump_patch(runtime)                 # v1.6.8 → v1.6.9
  # NEVER bump minor/major silently
```

| 输入 | 输出示例（本仓当前 truth） |
|------|---------------------------|
| 无版本 + 新功能 | runtime v1.6.8，docs 已有 v1.6.9 planning → **v1.6.9** |
| 无版本 + 仅 runtime 线 | v1.6.8 → bump → **v1.6.9** |
| 无版本 + 「生产热修」 | **不** bump；baseline=**v1.6.8**（当前发布线） |
| 显式 v2.0.0 | 用 v2.0.0 |
| `v1.6.9\v2.0.0` | 双轨 |

#### Hotfix（生产事故）

| 规则 | 值 |
|------|-----|
| baseline 默认 | **`current_runtime_release_line`**（最新**已发布**生产基线） |
| **禁止** | 自动 bump 到未发布 planning 线当热修落点 |
| 文档/变更登记 | 可记在 `docs/beacon/<baseline>/change/hotfix-...` 或 patch 线说明，但 **代码以生产基线分支为准** |

### 4.3 与现网 `auto` 的差异（要产品化）

| 现网 | 用户要的 |
|------|----------|
| auto → docs_default（常是 runtime 线） | 新功能可 **自动 patch +1** 到下一迭代线 |
| hotfix 无默认 baseline | hotfix **默认 = 当前发布线** |
| skill 要写清 | **runtime 做**，skill 只写「无版本则 CLI auto/default-target」 |

---

## 5. 两场景对照表（agent 决策，可印在 L0 10 行内）

| 信号 | 模式 | 版本默认 | 分支/树 | release |
|------|------|----------|---------|---------|
| 生产/线上/事故/紧急 | **hotfix** | baseline=`current_runtime_release_line` | `hotfix/<baseline>-<slug>` 从 baseline 拉；**不进** feature 开发轨 | `--profile hotfix` + 人 |
| 普通需求/无版本 | **normal** | `default_target_version()`（已有 planning 优先，否则 patch+1） | admitted **feature worktree** | full + 人 |
| 双轨/并行 + 多版本 | dual | 解析 utterance 版本 | 各轨 leaf | 各轨 |

---

## 6. 简洁性落地清单（实现湖拆分，供后续 goal）

| Lake | 内容 |
|------|------|
| **L-skill-slim** | 压缩 beacon-goal/loom-goal 等到 ≤80 行；细则迁 references |
| **L-version-default** | `default_target_version()` + hotfix baseline 默认；CLI `-v auto` 行为对齐 |
| **L-hotfix-mainline** | hotfix 分支登记合同；与 UD-ENF 例外表；禁止 feature 开发轨 |
| **L-examples** | `hotfix-prod-30s.md` + `no-version-default-30s.md` |

**不在 skill 里实现逻辑** — 只在 skill 写默认与 HARD。

---

## 7. 推荐 UD（请确认后可 goal 冻结）

| ID | 推荐值 |
|----|--------|
| UD-SK-001 | Public skill L0 ≤80 行；细节 progressive only |
| UD-SK-002 | 框架自愈/doctor **永不**要求用户记 gov skill 名 |
| UD-HF-001 | 生产事故 = hotfix 模式；**从生产基线拉 `hotfix/*`，不进 feature 开发 worktree 流** |
| UD-HF-002 | 「主线热修」= 基线是 main/release；**Git 必须登记 hotfix 分支**（禁止无分支直写） |
| UD-HF-003 | hotfix 默认 baseline = `current_runtime_release_line` |
| UD-HF-004 | hotfix 仍要 forward_port + rollback_notes + human release |
| UD-VER-001 | 无版本 + normal → `default_target_version()`（planning 优先否则 patch +1） |
| UD-VER-002 | 无版本 + hotfix → **不 bump**，只用当前发布基线 |
| UD-VER-003 | 禁止无确认时 silent major/minor bump |
| UD-ENF-HF | pre-commit：`hotfix/*` 允许业务路径；`main` 仍禁（逼切换到 hotfix 分支） |

---

## 8. recommended_next

1. 确认 UD-SK / UD-HF / UD-VER（可「全接受推荐」）。  
2. `$beacon-goal` 开湖：优先 **L-version-default + L-hotfix-mainline**（行为），再 **L-skill-slim**（提示词）。  
3. 回归：无版本 normal、无版本 hotfix、显式双轨、main 直写仍被拒 / hotfix 分支可通过。

---

## 9. 一句话

**Skill 只留路由与两场景默认；版本与热修分支由 runtime 算死。**  
生产事故 = **贴生产基线的 `hotfix/*` 短分支**，不是 feature 开发轨，也不是无登记的裸 main。  
无版本 = **normal 走 patch 迭代线 / 已有 planning；hotfix 钉死当前发布线。**
