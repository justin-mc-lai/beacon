---
artifact_type: planner_review
skill: beacon-pln-review
target_version: v1.6.8
loom_sync: v2.0.0
created_at: 2026-07-18
status: support_advisory
user_decision: GO_intent_all_gaps_in_v1.6.8
not: [implementation, qa_verdict, release_verdict, truth_write]
sources:
  - conversation: production hotfix + release fragility + longrun default + multi-version ops
  - docs/beacon/archive/v1.6.7/SUMMARY.md
  - docs/beacon/v2.0.0/SUMMARY.md
  - docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/goalrun-main-axis.md
  - beacon/utils/branch_governance.py (DUAL_VERSION_TEMPLATE)
  - skills/beacon/beacon-gen-change/SKILL.md
  - skills/beacon/beacon-goal/SKILL.md
---

# Planner Review: v1.6.8 生产运维硬化 + Loom 哲学同步

## intent_snapshot

用户 **认可** 交付视角全部缺口，要求在 **v1.6.8 一并完整修复**：

1. **热修主航线**（上线后 bug 的生产修复线路）
2. **发布门过重且易碎**（evidence-manifest / run_id / 工件链）
3. **长程默认不稳**（Driver/Supervise 仅 opt-in）
4. **多版本并存运营未产品化**（v1 维护 + v2/Loom 进化）

并要求：**工程哲学/治理同步到 v2 Loom**（非只修 Python 生产轨）。

**一句话 intent：**  
v1.6.8 把 Beacon 从「能正向交付」补成「上线后也能安全养」；同一套运维哲学挂进 Loom/v2 主轴，禁止 v2 另起一套互相矛盾的运维语义。

## scope_mode

`full_parity`（用户明确：以上所有问题一起在 v1.6.8 完整修复）  
**非 MVP 裁切**；允许 **分湖并行**，但 **program 一次立项、主轴一次挂载、done_when 统一**。

**Out of scope（本 program 不假装完成）：**

- 真实 K8s/云厂商部署引擎实现
- 替代用户 CD（GitHub Actions / 云效）本身
- Loom 品牌 CLI 全量（仍属 v2 Wave 0；本 program 只 **同步治理语义**）
- 把 BEACON_V2=1 默认打开（仍禁，直到 W4 人工 GO）

---

## 1. 问题 → 能力契约（煮干）

### 1.1 热修主航线（P0）

| 今日 | v1.6.8 Must |
|------|-------------|
| change 文案提 hotfix，无独立入口 | **HotfixLane** 一等：入口 + 状态机 + 证据 |
| dual-version 模板可选、默认空 | **默认可用** 的 hotfix 分支契约 + forward-port 门 |
| 小修走全量 release 门 | **hotfix-release profile**：最小门集 + 强制回归槽 |
| 无回滚笔记硬门 | **rollback_notes** 在 release_ready 必填（hotfix） |

**用户入口（推荐，不第二哲学入口）：**

```text
$beacon-goal --mode hotfix "生产：…现象…"
# 或
beacon goal run "…" --mode hotfix --from-version <tag|version>
```

语义仍挂在 **唯一公共 facade `beacon-goal`**；mode 是 GoalRun 子模式，不是第二 skill 入口。

### 1.2 发布门过重且易碎（P0）

| 今日 | v1.6.8 Must |
|------|-------------|
| evidence-manifest 手搓/易脏 | `beacon doctor repair-evidence-manifest` **一键重算** |
| run_id / signature chain 漂移 | **run_id 对齐器** + fail 时 reason 给修复命令 |
| 门禁检查 8–20 项同级 critical | **ReleaseProfile**：`full` / `hotfix` / `docs-only` |
| 修门像考古 | 每个 blocked reason → **单一 repair command**（已有雏形，扩到全表） |

### 1.3 长程默认不稳（P0）

| 今日 | v1.6.8 Must |
|------|-------------|
| durable + driver 默认 idle | **项目级默认** `goal.longrun_default=true`（可关） |
| 上下文满靠人打「继续」 | resume-pack + driver **默认 on**（项目 opt-out） |
| supervise 另记 | `goal run` 在 longrun 时 **自动 attach** supervise 心跳 |
| 无默认 trace | longrun 默认写 agent_trace 最小事件（对齐 Loom trace 合同） |

### 1.4 多版本并存运营（P0）

| 今日 | v1.6.8 Must |
|------|-------------|
| version-truth 有线，无运营 SOP | **VersionFleet** 读模型：current_prod / maint / next / planning |
| dual-version 需手配 | `beacon doctor init-dual-version` + verify fail-closed |
| 禁止 next→prod 修复 仅模板 | **release 门** enforce forbidden_directions |
| Loom 与 v1 叙事分裂 | **同一运维哲学**写入 v2 axis + loom skill 指针 |

---

## 2. 湖拆分（program 拓扑）

**Program 建议名：** `beacon-prod-ops-hardening-v168`

| # | Lake slug | 角色 | 优先级 | depends_on |
|---|-----------|------|--------|------------|
| 1 | `beacon-hotfix-lane-v168` | 热修入口/FSM/最小 QA/forward-port | P0 | — |
| 2 | `beacon-release-profile-selfheal-v168` | full/hotfix profile + evidence 自愈 | P0 | — |
| 3 | `beacon-goal-longrun-default-v168` | 项目默认 longrun + auto supervise | P0 | — |
| 4 | `beacon-version-fleet-ops-v168` | 多版本舰队读模型 + dual-version 产品化 | P0 | hotfix-lane |
| 5 | `beacon-v168-goalrun-axis-mount` | 主轴挂载 + UD-AXIS regenerate | P0 | 1–4 |
| 6 | `beacon-v2-loom-ops-philosophy-sync` | v2/Loom 合同镜像（parity） | P0 | 5 |

**海（明确 defer，写入 deferral_ledger，不假装 v1.6.8 完成）：**

| 海 | 原因 |
|----|------|
| 云 CD 编排器本体 | 超出 Beacon 内核；只要求证据槽 |
| 全自动生产回滚执行 | 需环境权限；本版只强制 **rollback plan 工件** |
| Loom CLI 全量双装 | 仍属 v2 Wave 0 implement；本版 **哲学+门语义** parity |

---

## 3. state_model（关键）

### 3.1 GoalRun 扩展（共享 v1.6.8 / v2）

```text
created → running → stage_active{plan|truth|design?|implement|qa|release}
         → hotfix_active   (mode=hotfix 时并行子路径，仍在 GoalRun 下)
         → host_interrupted ↻ resume-pack
         → awaiting_verifier → completed
         → release_pending → release_confirmed (human)
```

**HotfixLane 子机（不得 complete GoalRun）：**

```text
incident_captured → baseline_locked → change_refrozen
  → implement_minimal → qa_minimal → forward_port_planned
  → release_hotfix_profile → (human) release_confirmed
  → forward_port_merged | forward_port_blocked
```

Illegal:

| ID | 禁止 |
|----|------|
| I-HF-001 | hotfix 无 incident/baseline 引用 → implement |
| I-HF-002 | hotfix 无 forward_port 计划 → release_confirmed |
| I-HF-003 | next_feature 直接当 first_production_fix（forbidden_direction） |
| I-HF-004 | HotfixLane → GoalRun.completed 自证 |
| I-LR-001 | longrun_default on 但无 resume-pack 能力 → 宣称 durable |
| I-REL-001 | full profile 用 hotfix 最小门宣称 platform release |

### 3.2 ReleaseProfile 状态

```text
profile_selected{full|hotfix|docs_only}
  → preflight_selfheal (manifest/run_id)
  → gates_run
  → pass | blocked(repair_command)
```

---

## 4. 各湖验收标准草案（AC 纲要）

### 4.1 beacon-hotfix-lane-v168

| AC | Must |
|----|------|
| AC-HF-001 | `beacon goal run … --mode hotfix` 创建 GoalRun.mode=hotfix |
| AC-HF-002 | 强制 `from_version` 或 production tag 引用 |
| AC-HF-003 | change 包 delivery_type=hotfix；禁止 silent 扩 scope 无 UD |
| AC-HF-004 | 最小 QA：复现 TC + 烟测列表；全量矩阵可选 |
| AC-HF-005 | release 使用 hotfix profile |
| AC-HF-006 | forward-port 任务/PR 引用必填 |
| AC-HF-007 | rollback_notes 非空 |
| AC-HF-008 | examples：`skills/beacon/examples/hotfix-30s.md` |
| AC-HF-009 | 与 domain FSM：热修可声明 `domain_required` 继承生产包，不新建空 FSM |

### 4.2 beacon-release-profile-selfheal-v168

| AC | Must |
|----|------|
| AC-RP-001 | `ReleaseProfile.full` 兼容现网 full gate |
| AC-RP-002 | `ReleaseProfile.hotfix` 门集 ⊆ full，且含 HF 专属门 |
| AC-RP-003 | `beacon doctor repair-evidence-manifest` 重算 hash，缺文件 drop 或 report |
| AC-RP-004 | `beacon doctor align-run-id --run-id` 对齐 status/coverage/signature/manifest |
| AC-RP-005 | 每个 release blocked reason → `recommended_command` 非空 |
| AC-RP-006 | 负例：manifest 故意脏 → repair → gate pass |
| AC-RP-007 | 禁止把 repair 当 fake runner（仍要真 hash 一致） |

### 4.3 beacon-goal-longrun-default-v168

| AC | Must |
|----|------|
| AC-LR-001 | 项目 metadata `goal.longrun_default` 默认 **true**（新项目）；旧项目 migrate 提示 |
| AC-LR-002 | longrun_default 时 `goal run` 自动 attach Driver+supervise（等价今日 `--longrun`） |
| AC-LR-003 | 可项目级 `longrun_default=false` opt-out |
| AC-LR-004 | 上下文满 → resume-pack digest 为续跑权威 |
| AC-LR-005 | longrun 默认最小 agent_trace（tool_call+output/failure） |
| AC-LR-006 | 负例：opt-out 时行为与 v1.6.7 兼容 |
| AC-LR-007 | 文档 30s：`goal-longrun-default-30s.md` |

### 4.4 beacon-version-fleet-ops-v168

| AC | Must |
|----|------|
| AC-VF-001 | `beacon version fleet` 读模型：prod/maint/next/planning |
| AC-VF-002 | `doctor init-dual-version` 写入 hotfix 命名规则 + baselines |
| AC-VF-003 | `doctor verify-dual-version` fail-closed 缺字段 |
| AC-VF-004 | release 在 dual-version 启用时 enforce forbidden_directions |
| AC-VF-005 | forward-port 证据槽：source_commit, forward_port_commit |
| AC-VF-006 | 与 version-truth catalog 单向投影，禁止双写权威 |
| AC-VF-007 | 示例：维护 v1.6.7 + 开发 v2.0.0 的 30s SOP |

### 4.5 axis + Loom sync

| AC | Must |
|----|------|
| AC-AX-001 | v1.6.8 program 生成 goalrun-main-axis，挂载 1–4 湖 |
| AC-AX-002 | change 触达上述湖 → UD-AXIS regenerate |
| AC-LM-001 | v2 program 镜像湖：`beacon-v2-hotfix-lane` / `release-profile` / `longrun-default` / `version-fleet`（parity 表） |
| AC-LM-002 | Loom skill 文档声明：**运维哲学与 v1.6.8 同源**；禁止 Loom 私有矛盾门 |
| AC-LM-003 | 主轴 Wave 序：Fleet/Profile → Hotfix → Longrun default → Axis validate |

---

## 5. Wave（实现序，防空中阁楼）

```text
Wave 0  version-fleet 读模型 + dual-version init/verify（无运维地图，不先做热修）
Wave 1  release-profile + evidence self-heal（先让门可修、可分级）
Wave 2  hotfix-lane（依赖 profile + fleet 方向门）
Wave 3  longrun-default（独立，但与 hotfix 同 program 验收）
Wave 4  axis mount + examples + v2/Loom parity 合同冻结
Wave 5  QA：正负例矩阵（见下）→ human release v1.6.8
```

**第一性原理序：**  
先能 **看见版本舰队** → 再能 **修门** → 再能 **热修** → 再能 **默认长跑** → 再冻结哲学到 Loom。

---

## 6. 测试/负例矩阵（program 级）

| 场景 | 期望 |
|------|------|
| 正常 full release | profile=full 与 v1.6.7 行为兼容 |
| 脏 manifest | repair 后 pass；不 repair 则 mismatch |
| hotfix 无 from_version | blocked I-HF-001 |
| hotfix 无 forward_port | blocked I-HF-002 |
| next_feature 冒充 prod fix | forbidden_direction |
| longrun_default on 断会话 | resume-pack 可续，不丢 GoalRun |
| longrun_default off | 兼容 v1.6.7 opt-in |
| v2 合同-only 湖 | 不宣称 implement complete |
| 双轨：hotfix 合并后无 port 到 next | release/port 门 blocked |

---

## 7. parity_matrix：v1.6.8 ↔ v2 Loom

| 能力 | v1.6.8 生产轨 | v2 / Loom |
|------|---------------|-----------|
| HotfixLane | **实现 + CLI** | 合同镜像 + axis 挂载；实现可复用 Python 直至 Rust 接线 |
| ReleaseProfile | **实现** | 合同 + scorecard 字段同源 reason_code |
| Longrun default | **实现** | `beacon-v2-goal-durable-longrun` **升格默认策略**；与 driver 合同合并修订 |
| Version fleet | **实现** | version-truth + Loom 文档同一舰队模型 |
| 公共入口 | `$beacon-goal --mode` | `$loom-goal --mode` 语义对齐（品牌面仍 Wave 0） |
| 禁止 | 第二哲学入口 | 同：loop 仅 support |

---

## 8. findings

| ID | Sev | Finding | 处置 |
|----|-----|---------|------|
| F1 | P0 | 热修无产品入口，上线后只能野路 | 湖1 完整实现 |
| F2 | P0 | 发布门易碎导致「能交付却难重验」 | 湖2 self-heal + profile |
| F3 | P0 | 长程默认 off 违背「一句话跑到验收」 | 湖3 项目默认 on |
| F4 | P0 | 多版本运营未产品化，双轨模板休眠 | 湖4 |
| F5 | P0 | v2 合同不跟进会哲学分叉 | 湖6 parity |
| F6 | P1 | 门禁过重伤害 hotfix | profile 分级，非删 full 门 |
| F7 | P1 | SUMMARY 状态漂移 | axis/program 验收含 SUMMARY 同步检查 |
| F8 | info | CD 本体 out of scope | 证据槽即可 |

confidence：高（均有代码/合同锚点）；authority：user GO + support_advisory。

---

## 9. deferral_ledger

| 项 | 状态 | 说明 |
|----|------|------|
| 云上自动回滚执行 | **deferred** | 仅 rollback_notes + 人工确认 |
| Loom pip/CLI 全量 | **deferred to v2 Wave 0** | 本 program 只同步 ops 哲学 |
| BEACON_V2 默认 | **rejected** | 保持 W4 人工 GO |
| 删减 full release 安全门 | **rejected** | 用 profile，不阉割 full |
| 一次改写全部历史 truth L0 | **deferred** | 与 v168 正交；不阻塞 |

**无 MVP 静默裁切四 P0 能力**——用户要求 v1.6.8 完整修复。

---

## 10. 工程哲学（写入 v1.6.8 + Loom 共同边界）

1. **一条 GoalRun**：hotfix/longrun 是 mode/profile，不是第二入口。  
2. **生产基线神圣**：hotfix 从 tag/baseline 来，禁止 next 线直接顶生产修。  
3. **Forward-port 义务**：修了旧线必须计划合新线。  
4. **门可修**：blocked 必带 repair command；自愈不做假绿。  
5. **默认耐久**：长任务默认 durable；opt-out 显式。  
6. **双轨诚实**：Beacon 生产与 Loom 进化并行，互不默认覆盖。  
7. **子机不终裁**：Driver/Supervisor/HotfixLane 不得 completed/release。

---

## 11. recommended_route

| 步 | 动作 | Skill |
|----|------|-------|
| 1 | 用户确认本 review（已有 GO 意图） | — |
| 2 | 开版本线 `docs/beacon/v1.6.8/` + program 骨架 | `beacon-pln-program` 或 truth-init |
| 3 | **一次 change 冻 6 湖** + feature-graph + axis | **`beacon-gen-change` / gen-truth** |
| 4 | 按 Wave 0→4 implement | `beacon-goal` / gen-implement |
| 5 | QA 矩阵（§6） | `beacon-eval-qa` |
| 6 | 人工 release v1.6.8 | `beacon-eval-release` |
| 7 | v2/Loom 合同镜像同 PR 或紧随 PR | change on v2.0.0 |

**禁止本 review 直接 implement。**

### 建议用户确认的锁定决策（写入 change 前）

| ID | 建议默认 | 备选 |
|----|----------|------|
| UD-V168-001 | longrun_default=**true**（新项目） | false 兼容旧 |
| UD-V168-002 | hotfix 入口= **goal --mode hotfix** | 独立 skill（不推荐） |
| UD-V168-003 | hotfix profile **强制** forward-port 计划 | 仅 warn（拒绝） |
| UD-V168-004 | repair-evidence-manifest **可写** .beacon | dry-run 默认 |
| UD-V168-005 | v2 同步= **parity 合同+axis** 同里程碑 | 仅文档 |

若用户无反对，下一跳直接：

```text
$beacon-gen-change v1.6.8
program: beacon-prod-ops-hardening-v168
lakes: hotfix-lane, release-profile-selfheal, goal-longrun-default, version-fleet-ops, axis-mount, v2-loom-ops-sync
```

---

## 12. 完整修复定义（done_when for v1.6.8 program）

v1.6.8 **完整修复** 当且仅当：

1. 四 P0 湖 **truth frozen + implement + QA pass**  
2. `goal --mode hotfix` 端到端示例在 examples/ 可跟做  
3. 故意弄脏 manifest → 一键 repair → release check 恢复  
4. 新项目 longrun 默认开启；opt-out 测过  
5. dual-version init/verify + forbidden_direction 负例  
6. goalrun-main-axis v1.6.8 与 v2 镜像均 validate ok  
7. 人工 `beacon release check v1.6.8` release_ready  
8. Loom/v2 research+truth 写明 **同源运维哲学**（无第二套）

---

## 13. 大白话

v1.6.7 像 **能把新软件造出来并验收的灯塔**。  
v1.6.8 要补的是 **船上以后坏了怎么修、门坏了怎么修、跑长途怎么不熄火、几艘船（版本）怎么并排开**——并且 **Loom 这艘新船用同一套航海规矩**，不能各开各的。
