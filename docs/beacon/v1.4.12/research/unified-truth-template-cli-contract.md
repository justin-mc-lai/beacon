# 调研闭环: unified-truth-template-cli-contract

- version: `v1.4.12`
- feature: `unified-truth-template-cli-contract`
- diagram_types: branch-flow, state-machine, decision-priority
- state_axes: template_state, format_compliance, content_language
- status: `source-driven-converged`
- date: `2026-05-30`
- ceo_review: `converged` -- 六轴挑战后收窄范围，格式迁移走 refreeze
- brainstorm_revision: `R3` -- 旧版本不做兼容，hash 变更走 refreeze 管线，**去掉一级编号**

## 核心约束变更 (R3)

> **旧版本视为已 release，不设格式兼容跳过。** v1.4.12+ 所有 truth 文档强制使用固定英文模板。旧版本文档保持原样，不迁移。如果需要将旧版本 truth 文档升级到新格式，必须走 `beacon change --refreeze-chain`，baseline hash 变更是合法的 refreeze 结果。

> **去掉一级编号。** PRD section 标题使用纯英文名（`## Problem`, `## Goals`, `## Scope`），不使用数字前缀（~~`## 1. Problem`~~）。与 User Story 和 Test Case 保持一致的命名风格。

R3 相对 R2 的增量变更：
- 去掉 PRD 模板中的 `N.` 数字前缀
- 校验规则从"检查编号+名称"简化为"检查 section name 是否在白名单且顺序合规"
- 新增 mandatory/optional section 分类
- 消除重编号级联问题

## 源码锚点

| 源码 | 行号 | 角色 |
|------|------|------|
| `docs/beacon/v1.4.11/prd/*.md` (13 个文件) | 全文 | 编号 section 名高度分化：30 种不同名称 |
| `docs/beacon/v1.4.11/user-story/*.md` | 全文 | 无编号 section (`## Story`, `## Acceptance Criteria`) |
| `docs/beacon/v1.4.11/qa/test-cases/*.md` | 全文 | 无编号 section (`## Coverage Matrix`, `## Explicit Non Coverage`) |
| `beacon/utils/prd_bootstrap.py` | 156-720 | `_minimal_prd_from_downstream`, `_render_prd`, `run_prd_bootstrap` |
| `beacon/commands/prd.py` | 1298-1575 | `_render_prd` -- 无模板约束 |

### Section 命名现状锚定

v1.4.11 PRD 编号 section 名统计（13 个文件）：

| section 名 (去编号前缀后) | 出现次数 | 性质 |
|---------------------------|---------|------|
| Problem | 12 | mandatory |
| Goals | 12 | mandatory |
| Functional Requirements | 12 | mandatory |
| Non Goals | 13 | mandatory |
| Success Metrics | 12 | mandatory |
| Design Principles | 6 | optional |
| Diagram Truth Layer | 6 | optional |
| Runtime Behavior Contract | 4 | optional |
| State Axes | 2 | optional |
| Evidence Contract | 2 | optional |
| 验收标准 / Acceptance Criteria | 1/1 | mandatory (R3 统一为 Acceptance Criteria) |
| Scope / 范围 | 1/1 | mandatory |
| Source Contract | 1 | optional |
| 其他 17 种特有 section | 1 each | optional |

User Story 和 Test Case 无编号，纯名 section 运行良好。

## 发现一: 编号制造的问题多于解决的问题

**编号解决了什么**：人工引用锚点（"见第 3 节"）和视觉排序。

**编号制造了什么**：
1. 重编号级联：插入或删除 section，其后所有编号必须重算。refreeze 时 diff 充满编号噪声。
2. 假序暗示：编号暗示线性阅读顺序，但 PRD 需要交叉引用而非线性叙事。
3. 校验脆弱：必须解析 `## N. Name` 并分别校验序号和命名。去掉 N 只需匹配 section name。
4. 二级编号禁令自证矛盾：R2 禁止 `2.1`，但一级编号本质相同——给 markdown section 加人工顺序号。
5. 未解决命名一致性：`## 1. 问题` proving 编号只约束了前缀格式，内容仍失控。

## 发现二: LLM 自由决定 Section 结构

`_render_prd` (`prd.py:1298`) 没有模板约束，LLM 在 prompt 中自行编排 section 顺序和命名。

## 发现三: 表格列名不统一

AC 表格列名和 Coverage Matrix 列名在不同 feature 间有变体。

## 核心设计 (R3)

### 结构层与内容层分离

| 层 | 语言 | 控制方 | 可变性 |
|---|------|--------|--------|
| Section 标题 | **纯英文，无编号** | CLI 模板函数 | 固定，不可变 |
| 表格列名 | **纯英文** | CLI 模板函数 | 固定，不可变 |
| Front matter 键名 | **英文** | CLI 模板函数 | 固定 |
| FILL 占位注释 | **英文** | CLI 模板函数 | 固定 |
| LLM 填空正文 | **默认英文，可配中文** | `--lang` 参数 | 显式配置 |

### Section 分类 (R3)

**Mandatory sections** (必须存在，顺序固定)：

```python
PRD_MANDATORY = [
    "Overview",
    "Problem",
    "Goals",
    "Scope",
    "Functional Requirements",
    "Acceptance Criteria",
    "Non-Goals",
    "Success Metrics",
]
```

**Optional sections** (可存在，位置在指定插入点之后)：

```python
PRD_OPTIONAL = [
    "Context",              # 插入点: Overview 之后
    "Design Principles",    # 插入点: Goals 之后
    "Source Contract",       # 插入点: Functional Requirements 之后
    "State Axes",            # 插入点: Functional Requirements 之后
    "Runtime Behavior Contract",  # 插入点: Functional Requirements 之后
    "Evidence Contract",     # 插入点: Acceptance Criteria 之前
    "Diagram Truth Layer",   # 插入点: Success Metrics 之后
]
```

**校验规则**：
- 所有 mandatory section 必须存在且顺序合规
- optional section 必须在白名单内，且插入位置合规
- 不允许白名单外的 section 名称
- 不允许编号前缀 (如 `1.`, `2.`, `2.1`)
- **Scope** 下的 `### In Scope` / `### Out of Scope` 是唯一允许的子标题

### `--lang` 参数

`beacon truth init` 支持 `--lang en|zh`:

- `--lang en` (默认): 正文内容预期英文
- `--lang zh`: 正文内容预期中文

此参数写入模板文件 front matter 的 `**Language**` 字段。

### 格式迁移策略 (R3 -- 走 refreeze 管线)

**删除** `beacon doctor migrate-truth-format` 独立命令。

格式统一通过以下路径实现：

1. **v1.4.12 新建 truth**: `beacon truth init` 生成固定英文模板（无编号 section），LLM 填空。从源头保证格式合规。
2. **旧版本 truth**: 保持原样不动。如需升级到 v1.4.12 格式，走 `beacon change --refreeze-chain`:
   - 读取旧格式 PRD/user-story/test-case
   - 按 v1.4.12 固定英文模板重写 section 标题（**去掉编号前缀**）和表格列名
   - 保留原有正文内容
   - 自动检测正文语言，写入 `**Language**` 字段
   - 重算 baseline hash，写入 `.machine/requirement/<slug>.freeze-state.json`
   - 走完 refreeze 管线，确保 gate 一致性

**hash 变更是合法的**: section 标题变了（包括去掉编号），baseline hash 必须重算。这不是"破坏"，而是 truth 自然演进。

## 三件套固定英文模板 (R3 -- 去掉编号)

### PRD 模板 (--lang en 默认)

```markdown
# PRD: <Human-Readable Name>

**Feature**: `<feature-slug>`
**Version**: `<version>`
**Status**: `frozen`
**Date**: `YYYY-MM-DD`
**Language**: `en`

## Overview
<!-- FILL: One paragraph describing the problem and expected outcome. -->

## Context
<!-- FILL: References to research docs, architecture docs, and global constraints. -->

## Problem
<!-- FILL: Specific problem in the current system, backed by source-anchored evidence. -->

## Goals
<!-- FILL: List of acceptance criteria. -->

## Design Principles
<!-- FILL: Design constraints and principles this feature must follow. -->

## Scope

### In Scope
<!-- FILL -->

### Out of Scope
<!-- FILL -->

## Functional Requirements

| FR ID | Related AC | Requirement |
|-------|-----------|-------------|
<!-- FILL: FR-001 | AC-001 | Description -->

## Source Contract
<!-- FILL: Affected source files with line numbers. -->

## State Axes

| Axis | States | Meaning |
|------|--------|---------|
<!-- FILL -->

## Acceptance Criteria
<!-- FILL: List all ACs with details. -->

## Non-Goals
<!-- FILL: Explicitly excluded items. -->

## Success Metrics
<!-- FILL: How to determine successful delivery. -->
```

**校验规则 (R3)**:
- mandatory section 8 个必须存在，顺序合规
- optional section 白名单内，插入位置合规
- 不允许编号前缀 (如 `1.`, `2.`, `2.1`)
- front matter 五字段: `**Feature**`, `**Version**`, `**Status**`, `**Date**`, `**Language**`
- `**Language**` 值必须为 `en` 或 `zh`
- Functional Requirements 表格列: `FR ID`, `Related AC`, `Requirement`
- State Axes 表格列: `Axis`, `States`, `Meaning`
- **Scope** 下的 `### In Scope` / `### Out of Scope` 是唯一允许的子标题
- `**Status**` != `template` 时不允许残留 `<!-- FILL: ... -->` 占位符

### User Story 模板 (--lang en 默认)

```markdown
# User Story: <Human-Readable Name>

**Feature**: `<feature-slug>`
**Version**: `<version>`
**Status**: `frozen`
**Date**: `YYYY-MM-DD`
**Language**: `en`

## Story
<!-- FILL: As a <role>, I want <goal>, so that <benefit>. -->

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
<!-- FILL: AC-001 | <theme> | <description> -->

## Test Story Map

| Test ID | Covers | Scenario |
|---------|--------|----------|
<!-- FILL: TC-001 | AC-001 | <scenario> -->

## References
- Research: `docs/beacon/<version>/research/<feature-slug>.md`
- PRD: `docs/beacon/<version>/prd/<feature-slug>.md`
- Test cases: `docs/beacon/<version>/qa/test-cases/<feature-slug>.md`
```

**校验规则**:
- front matter 五字段: `**Feature**`, `**Version**`, `**Status**`, `**Date**`, `**Language**`
- AC 表格三列: `AC ID`, `Theme`, `Description`
- Test Story Map 表格三列: `Test ID`, `Covers`, `Scenario`
- References 至少列出三条路径

### Test Cases 模板 (--lang en 默认)

```markdown
# Test Cases: <Human-Readable Name>

**Feature**: `<feature-slug>`
**Version**: `<version>`
**Status**: `frozen`
**Date**: `YYYY-MM-DD`
**Language**: `en`

## Coverage Matrix

| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |
|-------|-------|-------|-----------------|----------|---------------|
<!-- FILL: AC-001 | TC-001 | unit | <command> | <assertion> | <path> -->

## Explicit Non Coverage
<!-- FILL: Scenarios intentionally not covered and why. -->
```

**校验规则**:
- front matter 五字段: `**Feature**`, `**Version**`, `**Status**`, `**Date**`, `**Language**`
- Coverage Matrix 表格六列: `AC ID`, `TC ID`, `Layer`, `Planned Command`, `Assertion`, `Evidence Path`
- `Explicit Non Coverage` section 必须存在

## CLI 命令 (R3)

### `beacon truth init`

```
beacon truth init prd --version <v> --feature <slug> [--lang en|zh] [--force]
beacon truth init user-story --version <v> --feature <slug> [--lang en|zh] [--force]
beacon truth init test-case --version <v> --feature <slug> [--lang en|zh] [--force]
beacon truth init all --version <v> --feature <slug> [--lang en|zh] [--force]
  生成三件套 + 调用 beacon manifest add-feature 注册。
```

### `beacon truth verify`

```
beacon truth verify --version <v> --feature <slug> [--strict]
  校验三件套格式合规性。
  检查项:
    1. mandatory section 存在且顺序合规
    2. optional section 在白名单内且插入位置合规
    3. 不允许编号前缀
    4. 表格列名与模板一致
    5. front matter 五字段完整，Language 值为 en|zh
    6. Status != "template" 时无残留 FILL 注释
    7. Status != "template" 时内容语言与 Language 字段一致 (启发式)
  --strict: 任一不合规返回 exit 2 (blocked)。
  无版本跳过逻辑：v1.4.12+ 强制执行。
```

### `beacon truth show`

```
beacon truth show --version <v> --feature <slug> --kind prd|user-story|test-case [--lang en|zh]
  显示应然模板规范（不读文件，纯渲染）。
```

### ~~`beacon doctor migrate-truth-format`~~ (删除)

R3 删除此命令。格式迁移走 `beacon change --refreeze-chain`。

## 与 manifest 集成 (R3)

```
beacon truth init all --feature <slug> [--lang en|zh]
  -> 依次 init 三件套
  -> 调用 manifest add-feature 注册 (依赖 version-material-file-map-contract)
  -> manifest["features"] 新增 {slug, truth_paths, status: "template", language: <lang>}
  -> save_manifest()

beacon truth verify --feature <slug> --strict
  -> 从 manifest 获取路径 (依赖 version-material-file-map-contract)
  -> 逐文件校验 (结构 + 语言一致性)
  -> 任一 fail: exit 2, reason_code: truth_format_non_compliant

build_requirement_package_gate()
  -> 新增: feature status == frozen 且 truth_format 不合规 → blocked
  -> reason_code: truth_format_non_compliant
```

## 内容语言检测规则

`beacon truth verify` 内置启发式检测:

- 提取正文 (排除 section 标题、表格列名、代码块、URL、文件路径)
- 统计中文字符占比
- 中文字符 > 30% → 判定为 zh
- 中文字符 ≤ 30% → 判定为 en
- 判定结果与 `**Language**` 字段不一致 → warn (非 strict) 或 fail (strict)

## CEO Review 六轴收敛 (R3)

### too_smooth_path → Reduce

原方案假设"格式迁移是平滑的"。

R3 解法：不存在格式迁移的平滑性问题。v1.4.12 新建 truth 从模板生成，自然合规。旧版本 truth 保持不动。需升级时走 `beacon change --refreeze-chain`。去掉编号后，section 校验从正则提取 `N. Name` 简化为字符串白名单匹配，更鲁棒。

### buried_landmine → Eliminate

原方案的地雷是 `migrate-truth-format` 破坏 baseline hash。

R3 解法：**删除 `migrate-truth-format` 独立命令。** 格式升级走 `beacon change --refreeze-chain`，hash 变更是 refreeze 的合法结果。去掉编号后，refreeze diff 更干净（只有名称变更，没有重编号级联噪声）。

### truth_freeze_destabilization → Eliminate

原方案担心格式工具绕过 truth freeze 重写 frozen truth。

R3 解法：**格式变更走 `beacon change --refreeze-chain`。** 与 global-boundaries 第 4 条完全一致。

### stage_boundary_sprawl → Hold with explicit declaration

`beacon truth init` / `beacon truth verify` 是 truth surface 的格式校验辅助服务，不是新的 lifecycle stage。

### false_closure_signal → Hold with condition

gate 必须区分 `truth_format_compliant`（格式合规）和 `requirement_closure`（需求闭环）。前者是后者的必要条件，不能替代。

### operator_cost_underpricing → Reduce (R3)

去掉编号后：
- 校验逻辑更简单（字符串白名单匹配 vs 正则提取编号+名称）
- refreeze diff 更干净（无重编号级联噪声）
- 模板更易读（`## Problem` vs `## 1. Problem`）
- 三件套风格统一（PRD/User Story/Test Case 全部无编号）

## Brainstorm 收敛: 去掉一级编号 (R3)

### 问题

PRD 一级编号（`## 1. Problem`, `## 2. Goals` 等）是否必要？

### 分析

源码锚定证据：
- v1.4.11 PRD 有 30 种不同编号 section 名，编号只约束了前缀格式，内容仍高度分化
- User Story 和 Test Case 无编号，运行良好
- 编号制造重编号级联问题（插入/删除 section 引起后续全部重编号）
- 编号与二级编号禁令自证矛盾

### 结论

**去掉一级编号。** PRD 模板使用纯英文名 section 标题（`## Problem`, `## Goals`, `## Scope`），与 User Story 和 Test Case 保持一致的命名风格。

收益：
1. 校验简化：从正则提取 `N. Name` 简化为 section name 白名单匹配
2. refreeze diff 干净：无重编号级联噪声
3. 三件套风格一致：PRD/User Story/Test Case 全部无编号
4. 消除二级编号禁令的自证矛盾：无编号 = 无编号问题
5. 特有 section 可自然插入：`## Runtime Behavior Contract` 直接在白名单位置插入，无需考虑编号

## 状态轴 (R3)

```
template_state:
  absent -> template_created (init)
  template_created -> content_filled (LLM 填空, Status 改为 frozen)
  content_filled -> format_verified (verify 通过)

content_language:
  en (默认)
  zh (--lang zh)

format_compliance:
  unverified -> compliant
  unverified -> non_compliant (missing mandatory section, extra section, numbering prefix, table column mismatch, language mismatch, residual FILL)
```

~~migration_status~~: **删除**。不再有"旧版本迁移"概念。

## 决策优先级 (R3)

1. Section 标题: **纯英文，无编号**。CLI 模板函数固定，不可变。不存在 `## 1. Problem`，只有 `## Problem`。
2. 表格列名: 纯英文，CLI 模板函数固定，不可变。
3. Front matter 键名: 英文，机器解析依赖。
4. LLM 填空正文: 默认英文，`--lang zh` 切中文。Language 字段写入 front matter。
5. 格式校验对 v1.4.12+ 强制执行，无版本跳过。
6. 格式升级走 `beacon change --refreeze-chain`，baseline hash 变更是合法结果。
7. 旧版本 truth 保持原样不动。
8. mandatory section 必须存在且顺序合规，optional section 白名单内且位置合规。

## 源码改造清单 (R3)

| # | 模块 | 变更 |
|---|------|------|
| 1 | 新增 `beacon/commands/truth.py` | CLI: truth init / verify / show, --lang en\|zh |
| 2 | 新增 `beacon/utils/truth_template.py` | render_*_template(lang="en")，section 标题无编号，lang 仅影响 Language 字段 |
| 3 | 新增 `beacon/utils/truth_format.py` | 结构校验 (白名单匹配，无编号解析) + 语言一致性启发式检测 |
| 4 | `beacon/utils/material_audit.py` | build_requirement_package_gate 增加 truth_format_non_compliant |
| 5 | `beacon/commands/truth.py` | init all 集成 manifest add-feature (依赖 version-material-file-map-contract) |
| 6 | 新增 `tests/test_truth_template.py` | 模板结构不变性、Language 字段、无编号前缀 |
| 7 | 新增 `tests/test_truth_format.py` | mandatory/optional section 校验、编号前缀拒绝、表格列名校验、语言检测、FILL 残留检测 |

**删除项 (R3)**:
- ~~新增 `beacon/commands/doctor.py` migrate-truth-format~~ → 走 `beacon change --refreeze-chain`
- ~~版本跳过逻辑~~ → v1.4.12+ 无条件执行
- ~~`migration_status` 状态轴~~ → 删除
- ~~PRD 一级编号~~ → 去掉，section 标题使用纯英文名

## 验证标准 (R3)

1. `beacon truth init prd --feature test` 生成文件 section 标题全英文**无编号**（`## Problem` 而非 `## 1. Problem`），表格列名全英文，`**Language**: en`
2. `beacon truth init prd --feature test --lang zh` 生成文件 section 标题全英文无编号，表格列名全英文，`**Language**: zh`
3. `beacon truth verify --feature test --strict` 对合规文件 exit 0
4. 带编号前缀的 section（如 `## 1. Problem`）→ verify 报 `numbering_prefix_not_allowed` (strict 模式 fail)
5. 缺少 mandatory section → verify 报 `missing_mandatory_section` (strict 模式 fail)
6. en 模板填入中文正文 → verify 报 `language_mismatch`
7. zh 模板填入英文正文 → verify 报 `language_mismatch`
8. `beacon change --refreeze-chain` 中使用 v1.4.12 模板重写时，去掉编号前缀并重算 baseline hash
9. 无 `migrate-truth-format` 独立命令存在
10. 无版本跳过逻辑存在

## 已关闭的开放问题 (R3)

1. ~~格式迁移走独立 doctor 命令？~~ **关闭**: 走 `beacon change --refreeze-chain`，hash 变更是合法的 refreeze 结果。
2. ~~v1.4.11 及更早格式合规跳过？~~ **关闭**: v1.4.12+ 无条件执行，旧版本不动。
3. ~~语言检测 30% 阈值是否合理？~~ **保留**: 启发式检测覆盖 95%+ 场景，后续可配置化。
4. ~~PRD section 是否需要编号？~~ **关闭**: 去掉编号。与 User Story/Test Case 保持一致，消除重编号级联，简化校验。

## 路由

- 本 feature 依赖 `version-material-file-map-contract` (manifest 先行)
- 如 scope 变更，走 `beacon-change`
- 格式升级在任何版本中走 `beacon change --refreeze-chain`

## Skill 层调整需求 (Doubt Review R3)

### 问题

v1.4.12 的 truth template feature 只改造了 CLI 新入口 (`beacon truth init`)，但旧入口和 skill 层没有适配：

1. `beacon prd create` 仍走 `_render_prd` 老代码，生成编号 section
2. `prd_bootstrap.py._minimal_prd_from_downstream` 仍生成编号 section
3. skill `beacon-prd`/`beacon-user-story`/`beacon-test-case` 没有将 v1.4.12 格式规范注入 LLM prompt

### 调整项

1. **`beacon prd create` 适配**: v1.4.12+ 强制调用 `truth_template.py` 的 `render_prd_template()`，生成无编号英文模板。旧入口成为新模板的 wrapper。
2. **`prd_bootstrap.py._minimal_prd_from_downstream` 适配**: v1.4.12+ 使用新模板渲染函数，保持 bootstrap 逻辑但生成格式合规输出。
3. **Skill 规范引用**: 三个 skill 新增 `truth-format-spec.md` 引用段（归入 `version-material-file-map-contract` 管理）。

### 源码改造清单追加 (R3)

| # | 模块 | 变更 |
|---|------|------|
| 8 | `beacon/commands/prd.py` _render_prd | v1.4.12+ 调用 `truth_template.render_prd_template()` 替代硬编码 section |
| 9 | `beacon/utils/prd_bootstrap.py` _minimal_prd_from_downstream | v1.4.12+ 使用新模板渲染函数 |

### 路由

- 旧入口适配归入本 feature 源码改造清单
- Skill 规范引用归入 `version-material-file-map-contract`

## Diagram Truth 传播结构 (Doubt Review R3 扩展)

### 发现

Diagram truth layer 自 v1.3.8 引入后只停在 PRD 声明层，没有传播到 User Story 和 Test Case：

| 版本 | PRD 有 diagram section | US 有 diagram section | TC 有 diagram section |
|------|----------------------|---------------------|---------------------|
| v1.4.11 | 6/11 (55%) | 0/8 (0%) | 0/8 (0%) |

v1.3.8 AC-005 ("QA / test-case 能按 diagram 的 branch / transition 建立覆盖骨架") 未闭环。

### 追加模板结构

#### PRD: Diagram Truth Layer (optional — 已有，格式标准化)

去掉编号子标题，鼓励使用 mermaid 代码块：

```markdown
## Diagram Truth Layer

### Diagram Types
<!-- branch-flow, state-machine, decision-priority -->

### State Axes

| Axis | States | Meaning |
|------|--------|---------|

### Branch Flow
<!-- mermaid flowchart 或 stateDiagram-v2 代码块 -->

### Propagation Contract
- Diagram truth must stay explicit through freeze readiness, implementation planning, and QA coverage.
- State axes must not be silently compressed into one implicit status field.
- User-story AC must declare which state axis transitions they cover.
- Test-case coverage must declare which diagram branches they cover.
```

#### US: State Axis Coverage (optional — 新增)

```markdown
## State Axis Coverage

| AC ID | State Axis | Transition | Covered |
|-------|-----------|------------|---------|
```

#### TC: Branch Coverage Mapping (optional — 新增)

```markdown
## Branch Coverage Mapping

| TC ID | Diagram Branch | Transition | Covered |
|-------|----------------|------------|---------|
```

### 追加源码改造清单

| # | 模块 | 变更 |
|---|------|------|
| 10 | `beacon/utils/diagram_truth.py` render_diagram_truth_section | 去掉编号子标题，改用纯英文名；鼓励 mermaid 代码块 |
| 11 | `beacon/utils/diagram_truth.py` parse_diagram_truth | 支持解析 ` ```mermaid ` 代码块中的 node 和 transition |
| 12 | `beacon/utils/truth_template.py` | render_user_story_template 新增 State Axis Coverage optional section |
| 13 | `beacon/utils/truth_template.py` | render_test_case_template 新增 Branch Coverage Mapping optional section |
| 14 | `beacon/utils/truth_format.py` | verify 新增 diagram 传播完整性 check (warn, 非 strict fail) |

### 触发条件

Diagram Truth Layer、State Axis Coverage、Branch Coverage Mapping 仅在 `diagram_truth.required=True` 时触发。简单 feature 不需要这些 section。

详细调研见 `docs/beacon/v1.4.12/research/diagram-truth-triptych-closure.md`。
