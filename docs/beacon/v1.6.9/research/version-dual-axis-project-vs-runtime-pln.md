# Plan: 版本双轴 — Beacon Runtime vs 项目交付线（纠正 default_target 误用）

**Surface**: `$beacon-plan`  
**Status**: plan only — 纠正既有 UD-VER 在「外项目」上的误读  
**Date**: 2026-07-21

## 0. 你的质疑（成立）

> Beacon 既自驱迭代自身，也服务**其他项目**。其他新项目默认应从 **v0.0.1** 起，  
> 怎么会是「normal → planning/docs 高于 runtime → 本仓 v1.6.9」？

**结论：当前 `default_target_version()` 把「Beacon 工具仓的 docs 线」误当成了「业务项目交付版本」。这在 monorepo 自驱时碰巧像对，在外项目上是错的。**

---

## 1. 第一性原理：必须拆成两条轴

| 轴 | 名字 | 是什么 | 典型值 | 权威来源 |
|----|------|--------|--------|----------|
| **A. Beacon Runtime** | 工具运行时 / CLI 能力线 | 安装的 Beacon/Loom 包版本，决定 CLI 行为、技能合同能力 | `v1.6.8`、`1.6.8` | `beacon --version` / `__toolkit_version__` / `version-truth.runtime_version` |
| **B. Project docs / 交付线** | **项目产品版本线** | 该仓库正在交付的产品版本目录 `docs/beacon/<ver>/` | 外项目：`v0.0.1`；Beacon 自仓：`v1.6.9` | 项目 onboarding / project-metadata / `docs/beacon/*` / 用户显式 `-v` |

**二者独立：**

```text
外项目：
  runtime = v1.6.8   （本机装的 Beacon）
  docs/project = v0.0.1 或 v0.1.0  （产品自己的线）

Beacon 自仓：
  runtime = v1.6.8
  docs/project = v1.6.9（planning）/ v2.0.0（loom 线）
```

**禁止**：用「Beacon 安装版本 + patch」去当外项目的默认产品版本。  
**禁止**：用「Beacon monorepo 扫出来的 v1.6.9」去当任意 cwd 项目的 default_target。

---

## 2. 项目形态三分（默认策略不同）

| 形态 | 如何判定（推荐） | 无版本时 project docs 默认 | hotfix baseline |
|------|------------------|----------------------------|-----------------|
| **P1 外项目 greenfield** | `project_mode=greenfield` 或尚无 `docs/beacon/v*` 产品历史 / metadata 声明 | **`v0.0.1`**（首发）或已有 onboarding 的 docs_version | 产品**已发布线**（若无发布则无 hotfix 或等同首发） |
| **P2 外项目 takeover / 演进** | 已有 `docs/beacon/vX` 或 contract | **项目内**最大交付线 或 patch+1（相对**项目**当前发布线，不是 beacon runtime） | 项目 `current_release` / tag |
| **P3 Beacon/Loom 自驱 monorepo** | `package_name=beacon` 或 repo 含 `skills/beacon`+`beacon/version-truth.json` 自指 | 可用 monorepo 规则：planning > runtime 或 monorepo patch | `current_runtime_release_line` |

**关键：patch+1 的基数永远是「项目交付基线」，不是「Beacon runtime」。**

---

## 3. 当前实现错在哪

```text
default_target_version(project_root):
  runtime = Beacon toolkit v1.6.8
  higher = 扫 project_root 的 docs/beacon → 发现 v1.6.9, v2.0.0
  return v1.6.9
```

| 在 Beacon 自仓 | 在外项目（空/新） |
|----------------|-------------------|
| 扫到自己的 docs → 像「下个规划线」 | 若误用 monorepo 规则 / 或把 runtime 当基数 | 
| 尚可讨论 monorepo 专用 | **错误**：新项目应 **v0.0.1**，与工具是 v1.6.8 无关 |

`resolve_docs_version(auto)` 也会在 monorepo 上扫出最大 docs（甚至 v2.0.0），**不能**原样当作「任意项目的产品版本」。

---

## 4. 纠正后的默认算法（推荐 UD）

### 4.1 先分类

```text
context = classify_project(project_root)
  → beacon_self | external_greenfield | external_existing
```

### 4.2 Project docs 版本（goal `-v auto` 应解析这个）

```text
resolve_project_docs_version(auto):
  1. 显式 -v / utterance 中的 vX.Y.Z
  2. onboarding_docs_version / project-metadata.active_docs_version
  3. 若 external_greenfield 且无 docs 线:
       return v0.0.1          # UD-VER-EXT-001
  4. 若 external_existing:
       release = project_current_release or max(docs/beacon/*)
       if intent=new_feature: return bump_patch(release)   # 项目内 *.*.+1
       else: return release
  5. 若 beacon_self:
       # monorepo 专用（原逻辑可保留，但必须打标 source=beacon_self）
       if planning_or_docs > runtime: return min(higher)  # 可选
       else: return bump_patch(runtime_release)  # 工具自身迭代
```

### 4.3 Beacon Runtime 版本（始终另一路）

```text
resolve_runtime_version(auto):
  toolkit / version-truth.runtime_version
  # 只影响 CLI 能力与 managed context，不写入「产品 v0.0.1」语义
```

### 4.4 Hotfix

```text
hotfix baseline:
  external → 项目生产基线（tag / project release line），不是 beacon runtime
  beacon_self → current_runtime_release_line
  仍：登记 hotfix/*，不进 feature 开发轨，不 bare main
```

---

## 5. 对照表（纠正后）

| 场景 | Runtime（工具） | Project docs（交付） |
|------|-----------------|----------------------|
| 新外项目 `beacon init` | auto → 本机 v1.6.8 | **v0.0.1**（或用户 `--version`） |
| 外项目已有 v0.2.3，无版本新功能 | v1.6.8 | **v0.2.4**（项目 patch+1） |
| 外项目生产热修 | v1.6.8 | baseline **v0.2.3**（钉死，不 bump） |
| Beacon 仓自驱下一版本 | v1.6.8 | **v1.6.9** 或 monorepo 规划线 |
| Beacon 仓热修 | v1.6.8 | baseline **v1.6.8** |

**「planning/docs 高于 runtime → v1.6.9」仅适用于 P3 beacon_self，且应在 payload 标明 `project_kind=beacon_self`。**

---

## 6. Skill / 提示词应怎么写（简洁）

L0 只写：

```text
版本有两轴：
- runtime：装的 Beacon 几（CLI 自动）
- 项目交付线：产品版本（-v / auto）
  · 新项目默认 v0.0.1
  · 已有项目 patch+1 基于项目发布线
  · 热修钉项目生产基线，不 bump
```

**不要**写「取 monorepo 的 v1.6.9」这类本仓特例当全局默认。

---

## 7. 对已合并实现的影响（诚实）

| 组件 | 状态 |
|------|------|
| `default_target_version()` | **需改**：加 project_kind 分支；外项目 greenfield → v0.0.1 |
| goal `version_resolve` | **需改**：区分 runtime_meta vs project_docs_version |
| skill-slim 文案 | **需改**：删「planning 高于 runtime → 本仓 v1.6.9」全局表述 |
| hotfix 钉 runtime | **仅 beacon_self 正确**；外项目应钉**项目**发布线 |
| 测试 | 需加：tmp_path 空项目 → v0.0.1；monorepo → 自驱规则 |

---

## 8. 推荐 UD（替换/收窄原 UD-VER）

| ID | 值 |
|----|-----|
| UD-VER-AXIS-001 | 强制双轴：`runtime_version` ≠ `project_docs_version` |
| UD-VER-EXT-001 | 外项目 greenfield 无版本 → **v0.0.1** |
| UD-VER-EXT-002 | 外项目已有线无版本新功能 → **相对项目基线 patch+1** |
| UD-VER-SELF-001 | 仅 beacon_self 可用「相对 toolkit release 的 monorepo 规划/patch」 |
| UD-VER-HF-001 | hotfix baseline = **该项目生产基线**（self 则 runtime release line） |
| UD-VER-003 | 禁止 silent major/minor（保留） |

原「无版本 normal = planning 优先否则 patch+1（相对 beacon runtime）」→ **废止为全局规则**，降级为 **self 特例**。

---

## 9. recommended_next

1. 确认本 plan 的双轴 + 外项目 v0.0.1。  
2. `$beacon-goal` 开修复湖：`fix-version-defaults-dual-axis-v169`（改 version_defaults + skill 文案 + 测试）。  
3. 回归：空目录 / init greenfield / beacon monorepo / hotfix 外项目。

---

## 10. 一句话

**Beacon runtime 是螺丝刀型号；项目 docs 版本是工件编号。**  
新项目工件从 **v0.0.1** 起号；不能拿螺丝刀的 v1.6.8/v1.6.9 去当客户产品的版本默认。  
先前「planning > runtime → v1.6.9」只是 **Beacon 自仓** 的巧合，不是全局真理。
