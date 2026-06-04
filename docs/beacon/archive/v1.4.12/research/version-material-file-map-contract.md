# 调研闭环: version-material-file-map-contract

- version: `v1.4.12`
- feature: `version-material-file-map-contract`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: manifest_state, feature_discovery_mode, path_resolution
- status: `source-driven-converged`
- date: `2026-05-30`
- ceo_review: `converged` -- 六轴挑战后收窄范围，旧版本不做兼容
- brainstorm_revision: `R2` -- 旧版本视为已 release，不设 compat glob fallback

## 核心约束变更 (R2)

> **旧版本不做格式兼容。** v1.4.11 及更早视为已 release 状态，其 truth 文档保持原样不动。v1.4.12+ 强制 manifest + 确定性路径，不存在 compat glob fallback。

这一约束消除以下原方案中的设计噪声：

- 不需要 `_build_legacy_manifest_from_glob` 回退路径
- 不需要 `manifest sync` 的"自动检测 + 强警告"模式
- 旧版本的 glob 消费者在 v1.4.12 分支中直接替换，不保留旧路径
- 格式迁移不属于本 feature 范围（归 `unified-truth-template-cli-contract`）

## 源码锚点

以下每一条结论都锚定到实际源码。

| 源码 | 行号 | 角色 |
|--------|-------|------|
| `beacon/utils/material_sync.py` | 18-22 | `_discover_features` -- 扫描 user-story/*.md |
| `beacon/utils/material_audit.py` | 77-85 | `_feature_names` -- 扫描 prd/user-story/test-case 三个目录 |
| `beacon/utils/material_audit.py` | 201-250 | `build_material_audit` -- 扫描 research/release/execution |
| `beacon/utils/material_audit.py` | 570 | 扫描 release_dir/*.md |
| `beacon/utils/material_audit.py` | 736 | 扫描 implementation-plan-*.json |
| `beacon/utils/material_audit.py` | 849-920 | `build_requirement_package_gate` |
| `beacon/utils/docs_structure_contract.py` | 110-117 | 扫描 release_root |
| `beacon/commands/release.py` | 244, 261 | 扫描 *.json, 扫描 technical-implementation-*.json |
| `beacon/commands/implement/commands.py` | 4836 | 扫描 */state.json |
| `beacon/commands/design.py` | 256 | 扫描 *.md |
| `beacon/utils/design_contract.py` | 130-165 | `design_truth_paths` -- 完全确定性路径 |
| `beacon/utils/artifact_paths.py` | 1-220 | 所有路径基于 slug 计算，确定性 |

## 发现一: Feature 发现依赖目录扫描，而非 Manifest

**主张**: Beacon 没有版本级的 canonical feature 列表。每个需要知道"这个版本有哪些 feature"的模块各自独立扫描目录。

**源码证据**:

1. `_discover_features` (`material_sync.py:18-22`): Feature 列表来自扫描 `user-story/*.md`。
2. `_feature_names` (`material_audit.py:77-85`): 独立扫描三个目录取并集。

**后果**: 不同模块可能看到不同的 feature 集合。

## 发现二: 执行/交付文档靠 Pattern 查找

**主张**: Release、execution、delivery 文档通过 glob pattern 发现，而非确定性路径查找。

**源码证据**:

1. `docs_structure_contract.py:110-117`: 扫描整个 release_root。
2. `release.py:261`: `glob("technical-implementation-*.json")`。
3. `material_audit.py:736`: `glob("implementation-plan-*.json")`。

## 发现三: 正面案例 -- 已实现确定性的路径

| 模块 | 机制 | 状态 |
|--------|-----------|------|
| `artifact_paths.py`（整个文件） | 所有路径由 version + slug + kind 计算 | 已固定 |
| `design_contract.py:design_truth_paths` | 完整 dict of 固定路径 | 已固定 |
| `implement_adapters.py:build_default_task_prompt` | PRODUCT.md/DESIGN.md 按固定文件名 | 已固定 |

## 架构 (R2 -- 无 compat fallback)

```
目标 (v1.4.12+):
  beacon manifest show --version v1.4.12
    -> 读取 .machine/manifest/version-features.json
    -> 返回完整 manifest (features + paths + status)

  beacon manifest add-feature --version v1.4.12 --feature <slug>
    -> compute_feature_paths(project_root, version, slug)
    -> 写入 manifest 条目
    -> 写入事务记录 .beacon/transactions/manifest-<txid>.json

  beacon manifest verify --version v1.4.12 --strict
    -> 逐 path 检查磁盘存在
    -> 逐 truth 文件检查 manifest 引用完整性
    -> 任一缺失: exit 2

  所有消费者 (_discover_features, _feature_names, build_material_audit, release.py, design.py, implement/commands.py):
    -> load_manifest() 替代 glob
    -> v1.4.11 及更早版本不再被 v1.4.12+ 代码路径服务
```

### Manifest Schema

```json
{
  "schema_version": "1.0",
  "version": "v1.4.12",
  "generated_at": "ISO-8601",
  "features": [
    {
      "slug": "<feature-slug>",
      "status": "template | frozen | released",
      "language": "en | zh",
      "truth_paths": {
        "prd": "docs/beacon/archive/v1.4.12/prd/<slug>.md",
        "user_story": "docs/beacon/archive/v1.4.12/user-story/<slug>.md",
        "test_case": "docs/beacon/archive/v1.4.12/qa/test-cases/<slug>.md"
      },
      "evidence_paths": {
        "qa_matrix": ".machine/qa/<slug>.evidence-contract.json",
        "freeze_state": ".machine/requirement/<slug>.freeze-state.json"
      }
    }
  ],
  "version_level_paths": {
    "research_dir": "docs/beacon/archive/v1.4.12/research/",
    "execution_dir": "docs/beacon/archive/v1.4.12/execution/",
    "release_dir": "docs/beacon/archive/v1.4.12/release/",
    "change_dir": "docs/beacon/archive/v1.4.12/change/",
    "design_dir": "docs/beacon/archive/v1.4.12/design/"
  }
}
```

### 真相三件套 MD 格式规范 (本 feature 只管路径，不管格式)

本 feature 只负责 manifest 路径注册和 feature 发现。格式规范归 `unified-truth-template-cli-contract`。

### CLI 命令

```
beacon manifest show --version <v> [--json]
beacon manifest features --version <v>
beacon manifest add-feature --version <v> --feature <slug>
beacon manifest remove-feature --version <v> --feature <slug>
beacon manifest verify --version <v> [--strict]
beacon manifest paths --version <v> --feature <slug> [--kind prd|user-story|test-case]
beacon manifest sync --version <v>
  扫描磁盘文件重建 manifest (仅用于首次初始化或紧急修复)。
  v1.4.12+ 不设 compat glob fallback。
```

### `beacon doctor verify-truth-format`

此命令归 `unified-truth-template-cli-contract`。本 feature 不包含格式校验。

## CEO Review 六轴收敛 (R2)

### too_smooth_path → Reduce

原假设"glob → manifest 是平滑替换"不准确。

R2 解法：消除 compat fallback 后，实际路径更简单：
- v1.4.12+ 所有消费者直接读 manifest，manifest 不存在则 fail (不是 fallback)
- 不存在 `_build_legacy_manifest_from_glob` 函数
- `beacon manifest sync` 仅用于初始化或紧急修复，不是常规 compat 路径
- 并发写入：manifest 修改通过单线程 CLI 命令完成，不需要文件锁

### buried_landmine → Eliminate (R2)

原方案担心 format 迁移破坏 baseline hash。

R2 解法：**旧版本已 release，不动旧版本 truth 文档。** v1.4.12 新建的 truth 文档从一开始就使用新模板，baseline hash 自然正确。不存在"迁移破坏 hash"的地雷。

### truth_freeze_destabilization → Eliminate (R2)

原方案担心 `migrate-truth-format` 重写 frozen truth。

R2 解法：**本 feature 不包含格式迁移命令。** `migrate-truth-format` 归 `unified-truth-template-cli-contract`，且作为 `beacon change --refreeze-chain` 的一部分执行，不是独立 doctor 命令。

### stage_boundary_sprawl → Hold with explicit declaration

`beacon manifest` 必须显式声明：这不是新的 lifecycle stage，是 truth surface 的确定性索引服务。manifest 是 truth 文档的注册表，不是 truth 本身。

### false_closure_signal → Hold with condition

`beacon manifest verify` 只检查"路径存在"，不检查"内容正确"或"需求闭环"。gate 必须区分 `manifest_path_exists` 和 `requirement_closure`。`manifest_truth_file_missing` 是阻断条件，但 `manifest_path_exists` 不等价于 acceptance closure。

### operator_cost_underpricing → Reduce (R2)

消除 compat fallback 后，实施更简单：
- 阶段 A: `utils/manifest.py` -- 核心数据层
- 阶段 B: `commands/manifest.py` -- CLI 面
- 阶段 C: 迁移所有消费者，消除 glob (无 compat fallback)
- 阶段 D: 测试回归

无阶段 E (没有 compat 修复脚本需要)。

## 源码改造清单 (R2)

| # | 模块 | 当前 | 目标 |
|---|------|------|------|
| 1 | `material_sync.py:_discover_features` | glob user-story/*.md | `load_manifest()[features]` |
| 2 | `material_audit.py:_feature_names` | glob 三目录 | `load_manifest()[features]` |
| 3 | `material_audit.py:build_material_audit` | glob research/release/execution | 读 manifest paths |
| 4 | `docs_structure_contract.py` | glob release_root | `manifest[version_level_paths]` |
| 5 | `release.py` L244/L261 | glob patterns | manifest paths |
| 6 | `implement/commands.py` L4836 | glob */state.json | manifest + feature status |
| 7 | `design.py` L256 | glob *.md | manifest design paths |
| 8 | `branch_governance.py` | fnmatch rule | manifest-based config |
| 9 | 新增 `commands/manifest.py` | -- | CLI 模块 |
| 10 | 新增 `utils/manifest.py` | -- | load/save/validate/compute_paths |
| 11 | 新增 `tests/test_manifest.py` | -- | manifest CRUD, path 计算, verify |

## 实施顺序 (R2)

1. **阶段 A**: `utils/manifest.py` -- 核心数据层 (manifest schema, load/save, compute_feature_paths)
2. **阶段 B**: `commands/manifest.py` -- CLI 面 (show, features, add-feature, remove-feature, verify, paths, sync)
3. **阶段 C**: 迁移所有消费者，消除 glob (直接替换，无 compat fallback)
4. **阶段 D**: 测试回归 + `beacon manifest verify --strict` 全路径覆盖

## 验证标准 (R2)

1. `beacon manifest verify --strict` 检查每个 path 在磁盘上存在
2. `beacon doctor verify-materials --strict` 零次 glob 调用 (所有 feature 发现走 manifest)
3. 删除 truth 文件后 `build_requirement_package_gate` 返回 `blocked`，reason code: `manifest_truth_file_missing`
4. 空版本 `beacon manifest add-feature` 生成含单 feature 的有效 manifest
5. `beacon manifest paths --kind prd` 返回正确固定路径
6. v1.4.12+ 无 `_build_legacy_manifest_from_glob` 函数存在

## 已关闭的开放问题 (R2)

1. ~~`sync` 应自动检测还是要求显式迁移？~~ **关闭**: `sync` 仅用于初始化和紧急修复，无 compat 需求。
2. ~~v1.4.11 及更早版本过渡？~~ **关闭**: 旧版本视为已 release，v1.4.12+ 不服务旧版本目录。
3. 格式校验归 `unified-truth-template-cli-contract`，不归本 feature。

## 路由

- 本 feature 是 `unified-truth-template-cli-contract` 的前置依赖
- manifest 完成后，truth init 才能通过 manifest 注册 feature
- 如 scope 变更，走 `beacon-change`

## Skill 层调整需求 (Doubt Review R3)

### 问题

v1.4.12 的 manifest feature 只改造了 CLI 和数据层，没有改造 skill 层。LLM 在执行 truth 任务时不知道 v1.4.12 的目录-文档规范地图。

### 调整项

1. **新增 `skills/beacon/references/truth-format-spec.md`**: 三件套格式规范速查文件，作为三个 skill 共用的规范引用。
2. **`beacon-prd` skill**: 新增规范引用段，指向 `truth-format-spec.md`，让 LLM 知道 PRD section 必须无编号、英文、从白名单选取。
3. **`beacon-user-story` skill**: 同上，引用 User Story 格式规范。
4. **`beacon-test-case` skill**: 同上，引用 Test Cases 格式规范。
5. **`requirement-closure-checklist.md`**: 新增格式闭合检查项（section 白名单合规、编号前缀拒绝、Language 字段一致）。
6. **`freeze-readiness-checklist.md`**: 新增格式就绪检查项（`beacon truth verify --strict` 通过）。

### 路由

- skill 引用 truth-spec → 归入本 feature 的源码改造清单
- truth-format-spec.md → 注册到 manifest 的 version_level_paths
