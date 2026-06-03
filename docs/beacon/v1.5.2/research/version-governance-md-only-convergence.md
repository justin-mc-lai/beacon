# Brainstorm Convergence: v1.5.2 版本级元信息治理 MD 唯一真源设计

- version: `v1.5.2`
- date: 2026-06-03
- source_skill: `beacon-brainstorm`
- mode: `requirement-convergence`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`

> 输入文档：
> - `docs/beacon/v1.5.2/research/explicit-version-canonical-branch-worktree-preflight-gate.md`
> - `docs/beacon/v1.5.2/research/version-governance-git-branch-closure.md`

## 1. 问题还原

用户 prompt 的核心问题：

> beacon 版本级元信息治理唯一 MD 真源需要如何设计？

拆解为三个子问题：

1. **为什么当前不是唯一真源？** — 诊断现状
2. **唯一 MD 真源应该是什么形态？** — 目标设计
3. **从现状到目标需要什么？** — 路由与 AC 种子

---

## 2. 两份文档的共识与分歧

### 2.1 共识（已确认，无需再争论）

| 共识点 | 证据 |
|--------|------|
| v1.5.2 完成了 feature package 的 MD-first 切主源 | `SUMMARY.md` + `truth_map.py` `FEATURE_SURFACES` |
| 版本/拓扑/Git 分支治理仍以 JSON 为权威 | `.beacon/metadata/project-version-metadata.json` (511 行，~20 版本条目) |
| `load_execution_branch_contract()` 仍可覆盖 metadata | `commands.py:2244-2267` 确认：execution 先写，metadata 后补 |
| 目标应是单一 MD 真源，读写同源 | 两份文档一致 |
| 应退役 execution 三联 (`branch-governance-*`, `git-workflow-*`, `deterministic-implementation-contract-*`) | 两份文档一致 |
| 路由应为 `beacon-change`，不应直接改 v1.5.2 frozen truth | 两份文档一致 |

### 2.2 分歧 / 未决问题

| 维度 | 文档 1 (preflight-gate) | 文档 2 (branch-closure) | 需收敛 |
|------|------------------------|------------------------|--------|
| MD 路径 | 未指定 | `docs/beacon/governance/project-version-governance.md` (versionless) | **关键设计决策** |
| JSON 立场 | 未明确 | 硬约束"零 JSON"（§11） | 需评估可行性 |
| 迁移策略 | 未讨论 | G-06: JSON→MD→删 JSON | 需细化 |
| Parser contract | 未讨论 | 提及"与 feature-package-v2 同构"但无规格 | 必须定义 |
| 双 skill 统一 | 未讨论 | metadata + branch-governance → 同一 MD transaction | 需明确写路径 |

---

## 3. 现状诊断：为什么 JSON 仍是事实权威

### 3.1 写路径是 JSON-first

`project_metadata.py` 的 `_commit_payload` 先写 JSON，再 `_render_human` 生成 `.md` 投影。人类可读面是**写入投影**，不参与 load。

### 3.2 读路径只读 JSON

`load_project_metadata()` 只解析 JSON。`.md` 投影不被任何消费者读取。

### 3.3 合并顺序不是"metadata 绝对优先"

`_branch_guard_inputs()` (commands.py:2239-2318) 实际顺序：

```
git_workflow contract (seed)
  → execution_contract OVERRIDE (lines 2245-2267, 字段级覆盖)
    → metadata_view PARTIAL PATCH (lines 2293-2318, 仅 expected_branch/git_roots/participating/branch_governance)
```

execution_contract 的 `service_branch_map` 若未在 metadata 中显式覆盖，**可残留**。这与 toolkit 文案"let implement consume the same projected contract"的意图冲突。

### 3.4 truth-map 分类确认了"非权威"状态

`truth_map.py:57-61` 将 `project_version_metadata` 归入 `GENERATED_GOVERNANCE_SURFACES`（`generated_governance_state_not_truth`），`is_truth=False`。这承认 JSON 不是 truth，但**没有提供替代 truth surface**——版本治理 truth 在 truth-map 中处于"悬空"状态。

### 3.5 与 global-boundaries.md 的冲突

`global-boundaries.md` §4 明确规定：

> canonical source 是唯一提交源，不允许多源并写。
> 同一批次跨表面写入必须具备可审计事务元数据，并能检查 drift。

当前 execution_contract + metadata 双源合并模式直接违背了这条原则。

---

## 4. 目标设计：唯一 MD 真源的形态

### 4.1 核心设计决策

**决策 1：MD 路径 — 推荐 versionless，但需 governance 子目录**

文档 2 提议 `docs/beacon/governance/project-version-governance.md`。挑战：

- **Pro versionless**：拓扑 (topology_kind, service_bindings) 是跨版本的全局事实；per-service canonical branch 本身是"每个 version 在哪个分支"的映射，这份映射的**权威登记表**应该是一份文档，不是每个版本一份（避免版本间 drift）。
- **Con versionless**：Beacon 的 docs 组织是 `docs/beacon/<version>/` 为中心，versionless 文档打破了这一模式。但 `global-boundaries.md` 已经是 versionless 的先例——它是跨版本原则边界。

**推荐**：`docs/beacon/governance/project-version-governance.md`

理由：
- 拓扑是跨版本事实，不应每版复制
- `global-boundaries.md` 已是 versionless 先例
- 与 `GENERATED_GOVERNANCE_SURFACES` 中"治理状态非 truth"的定位一致：治理 truth 应是 versionless 原则 + 版本映射表的结合
- 若未来需要版本级覆盖，可在 versioned docs 中设投影/补充，但主源仍为 versionless

**决策 2：JSON 角色 — "零 JSON"需分阶段，不能一步到位**

文档 2 的硬约束"零 JSON"在目标态是正确的，但实操中：
- `.beacon/` 下的 JSON 是 runtime 的快速查询缓存，删除它意味着每次 implement/qa/release 都要 parse MD——性能可接受（feature-package-v2 parser 已证明 MD parse 可行）
- sqlite ledger 存 governance payload_json → 应改为存 MD hash
- **关键是先建立 MD 为主源，JSON 降级为 generated cache**（与 feature package 的 `.machine/` JSON 同哲学），验证闭环后再删 JSON 缓存

**推荐**：分两阶段
- Phase 1 (change + implement)：MD 成为 load 主源 → JSON 降级为 generated cache（`GENERATED_GOVERNANCE_STATE_ROLE` 语义不变，但写方向反转：MD→JSON 而非 JSON→MD）
- Phase 2 (后续 change)：验证 JSON 无消费者后删除

**决策 3：Parser contract 规格**

必须定义 governance MD 的 parser contract（类比 `beacon-feature-package-v2`）：

```text
contract: beacon-project-governance-v1

sections:
  - global_topology (required)
  - service_bindings[] (required)
  - version_contracts/<version> (repeatable)
    - participating_services[]
    - per_service_canonical_branch: {<service>: <branch>}
    - branch_guard_mode
    - branch_governance (optional)
```

MD 结构应同时满足：
- 人类可读（比 JSON 更易理解）
- 机器可解析（结构化 frontmatter / section markers）
- 事务可审计（transaction metadata 嵌入 MD frontmatter，与现有 transaction 模型对齐）

### 4.2 架构原则（从 global-boundaries.md §4 推导）

| 原则 | 当前 JSON 模式 | 目标 MD 模式 |
|------|---------------|-------------|
| 单真值 | ❌ JSON + execution 三联双源 | ✅ 唯一 MD |
| 单向投影 | ❌ `.md` 从 JSON 生成但不参与读 | ✅ JSON 从 MD 生成(cache only) |
| 事务一致 | ⚠️ JSON 有 transaction 但 execution 覆盖破坏一致性 | ✅ MD transaction → 所有消费者同一 resolver |
| 读写同源 | ❌ metadata toolkit→JSON, branch-governance→metadata view | ✅ 双 skill → 同一 MD → 同一 resolver |

### 4.3 消费者统一

```text
写入（唯一入口）:
  beacon-toolkit-metadata ──┐
  beacon-toolkit-branch-governance ──┼──> governance MD (唯一真源)
                                    │
读取（所有消费者同一 resolver）:
  truth-map resolve_project_governance(version)
    → parse governance MD
    → return GovernanceContract { topology, service_bindings, version_contract, branch_governance }
    → 消费者: implement._branch_guard_inputs / qa.verify / release.verify / doctor / gate

禁止:
  load_execution_branch_contract() 在 governance MD 存在时 merge（fail-closed）
  execution 三联新增（archive 旧文件）
```

---

## 5. 差距清单与 AC 种子

### 5.1 关键差距（从源码验证）

| ID | 差距 | 严重度 | 源码证据 |
|----|------|--------|----------|
| G-01 | `load_project_metadata()` 只读 JSON，忽略 MD | **critical** | `project_metadata.py` | 
| G-02 | `_commit_payload` JSON-first 写方向 | **critical** | `project_metadata.py` |
| G-03 | `load_execution_branch_contract()` 在 metadata 完整时仍合并 | **critical** | `commands.py:2244-2267` |
| G-04 | truth-map `VERSION_GOVERNANCE_SURFACES` 不含治理 MD | **high** | `truth_map.py:39-50` |
| G-05 | truth-map 无 `resolve_project_governance` 入口 | **high** | `truth_map.py` |
| G-06 | `service_branch_map` 可残留 execution 值 | **high** | `commands.py:2261` 加入 contract，2293+ 未覆盖 |
| G-07 | toolkit metadata / branch-governance 写路径分裂 | **medium** | 两个独立 skill，各自写不同 sink |
| G-08 | 无 governance MD parser contract 定义 | **blocking** | 全新需求 |
| G-09 | 无 JSON→MD 迁移工具 | **blocking** | 全新需求 |

### 5.2 AC 种子（beacon-change 输入）

| AC | 描述 | 覆盖的 G |
|----|------|---------|
| AC-G01 | `load_project_metadata()` 改为：若 governance MD 存在则 parse MD；缺失时 fallback JSON + warn | G-01 |
| AC-G02 | `_commit_payload` 改为：parse MD → validate → write MD → project JSON/sqlite (cache only) | G-02 |
| AC-G03 | `load_execution_branch_contract()` 在 governance MD 存在且 metadata 完整时 **fail-closed**（拒绝 merge execution 三联） | G-03 |
| AC-G04 | `VERSION_GOVERNANCE_SURFACES` 新增 `project_governance: "docs/beacon/governance/project-version-governance.md"`，role=`version_governance_truth` | G-04 |
| AC-G05 | truth-map 新增 `resolve_project_governance(version)` → `GovernanceContract` | G-05 |
| AC-G06 | `_branch_guard_inputs()` 中 `service_branch_map` 从 governance resolver 获取，不受 execution contract 污染 | G-06 |
| AC-G07 | metadata / branch-governance toolkit 命令只写 governance MD（经同一 transaction） | G-07 |
| AC-G08 | 定义 `beacon-project-governance-v1` parser contract（section schema + frontmatter spec） | G-08 |
| AC-G09 | `beacon doctor metadata migrate-to-md` 将现有 JSON → governance MD，保留 JSON 备份 | G-09 |
| AC-G10 | `material_gate_contract` 从 governance MD 解析，不依赖 JSON 路径 | 补充 |
| AC-G11 | 测试：governance MD 存在时 execution 三联触发 fail-closed | G-03 |
| AC-G12 | 测试：monorepo `service_bindings` + `per_service_canonical_branch` 从 MD 正确解析 | G-05 |

---

## 6. 推荐路由

```
beacon-brainstorm (本文档)
  └── 路由: beacon-change
        ├── feature slug: "markdown-only-project-version-governance"
        ├── 版本线: v1.5.3 (或下一个未冻结版本)
        ├── 输入: 本文档 §5 的 AC 种子 + 两份 research 文档作为 support evidence
        └── 后续: truth.define → truth.acceptance → truth.coverage → implement
```

### 6.1 不推荐的路由

| 路由 | 为什么不推荐 |
|------|-------------|
| 直接改 v1.5.2 frozen package truth | v1.5.2 scope 是 feature-package 切主源，版本治理是独立 concern |
| 直接进 implement | 没有 frozen AC，实现会偏离设计意图 |
| 只修 Rolo 实例不修 Beacon | 只解决一个实例，JSON-first 问题持续扩散到所有 Beacon 宿主项目 |
| 保留 JSON 为主源、只禁 execution 三联 | 仍然是双源（JSON + MD 投影），不符合 global-boundaries.md §4 单真值原则 |

### 6.2 为 Rolo 等下游项目提供的临时缓解

在 change 冻结和实现完成前：

1. 确保 `.beacon/metadata/project-version-metadata.json` 完整（topology + service_bindings + per_service_canonical_branch）
2. **删除** `docs/beacon/<version>/execution/branch-governance-*.md` 等 execution 三联（避免 implement 双源）
3. 在 Rolo workspace root 执行 `beacon doctor metadata verify --version <version>` 确认单源闭环

---

## 7. 开放问题（进入 change 前需回答）

1. **governance MD 是否需要按版本分文件？** 当前推荐 versionless 单文件，但若未来单个文件过大（>50 版本条目），是否需要 `governance/project-version-governance-<version>.md` 的分片策略？

2. **`doctor metadata verify` 的对比基准**：改为 MD 后，verify 是"当前 git branch vs MD 声明"还是"MD vs MD 投影的 JSON cache"？

3. **存量 JSON 的处理时序**：Phase 1 中 JSON 降级为 cache，那"cache 与 MD 不一致"应视为 error 还是 silent regenerate？

4. **execution 三联的 archive 策略**：是 `.archive/` 子目录、改扩展名 (`.md.archived`)、还是直接删除？

5. **beacon-toolkit-metadata 和 beacon-toolkit-branch-governance 是否应合并为一个 skill？** 还是保持两个 skill 但共享同一 MD transaction？

---

## 8. Verification

- [x] 输出明确指向 `beacon-change` 下一跳
- [x] 差距清单有源码证据支撑
- [x] AC 种子可追溯到具体差距
- [x] 未将 brainstorm 结果写成正式 requirement truth
- [x] 识别了两份文档间的分歧并给出收敛建议
- [x] 为 Rolo 等下游项目提供了临时缓解路径

---

## 9. Promotion Notes

- 本文档为 brainstorm convergence artifact，不修改 frozen truth。
- 采纳后应进入 `beacon-change` → feature `markdown-only-project-version-governance`。
- 两份输入 research 文档保留为 support evidence，在 change 的 `truth.md` 中引用。
- 关联：`docs/beacon/global-boundaries.md` §4（单真值原则）、`docs/beacon/v1.5.2/SUMMARY.md`（v1.5.2 scope 边界）、`docs/beacon/v1.5.2/execution/boundaries.md`（JSON 非 truth 声明）。
