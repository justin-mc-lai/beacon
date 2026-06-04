# 源码架构: unified-truth-template-cli-contract

- version: `v1.4.12`
- feature: `unified-truth-template-cli-contract`
- brainstorm_revision: `R3` -- 格式迁移走 refreeze，删除 migrate 命令，**去掉一级编号**

## 运行时布局

新增模块:

```
beacon/
├── commands/
│   └── truth.py                ← CLI: beacon truth init|verify|show, --lang en|zh
├── utils/
│   ├── truth_template.py       ← render_*_template(lang)，section 标题无编号纯英文，lang 仅影响 Language 字段
│   └── truth_format.py         ← 结构校验 (白名单匹配，无编号解析) + content_language 启发式检测
```

受影响的已有模块:

```
beacon/commands/
├── doctor.py                   ← verify-truth-format (新增子命令，无 migrate-truth-format)
beacon/utils/
├── material_audit.py           ← build_requirement_package_gate 增加 truth_format_non_compliant
```

## 写路径

### 模板生成 (--lang 仅影响 Language 字段和正文预期)

```
beacon truth init prd --feature <slug> [--lang en|zh]
  -> resolve_version >= v1.4.12
  -> lang = args.lang or "en" (默认)
  -> compute_path(project_root, version, slug, kind="prd")
  -> render_prd_template(feature_slug, version, lang)
     返回 markdown:
       section 标题: 无编号纯英文 (Overview, Problem, Goals, Scope, ...)
       表格列名: 无编号纯英文 (FR ID, Related AC, Requirement, ...)
       **Language** = lang
  -> 写入 prd/<slug>.md
  -> manifest add-feature 注册 (依赖 version-material-file-map-contract)
```

### 语言检测 (verify 时)

```
beacon truth verify --feature <slug> --strict
  -> 从 manifest 获取路径 (依赖 version-material-file-map-contract)
  -> 逐文件:
     -> 读取 **Language** 字段 (en|zh)
     -> 提取正文 (排除 section 标题、表格列名、代码块、URL、路径)
     -> 统计中文字符占比:
        占比 > 30% → detected = zh
        占比 ≤ 30% → detected = en
     -> detected != Language:
        strict 模式 → fail, reason: content_language_mismatch
        非 strict → warn
```

### 结构校验 (verify 时)

```python
# beacon/utils/truth_format.py

PRD_MANDATORY_SECTIONS = [
    "Overview", "Problem", "Goals", "Scope",
    "Functional Requirements", "Acceptance Criteria",
    "Non-Goals", "Success Metrics",
]

PRD_OPTIONAL_SECTIONS = {
    "Context": "after_overview",
    "Design Principles": "after_goals",
    "Source Contract": "after_functional_requirements",
    "State Axes": "after_functional_requirements",
    "Runtime Behavior Contract": "after_functional_requirements",
    "Evidence Contract": "before_acceptance_criteria",
    "Diagram Truth Layer": "after_success_metrics",
}

def validate_prd_format(content: str, *, strict: bool = False) -> dict:
    """校验 PRD 格式合规性。

    Returns:
        {status, mandatory_sections_ok, optional_sections_ok,
         no_numbering_prefixes, columns_ok, language_ok, issues: [...]}
    """
    ...
```

**校验逻辑**：
1. 提取所有 `## ` 开头的 section 标题
2. 拒绝含编号前缀的标题（`## 1.`, `## 2.`, `## 2.1` 等）
3. 检查所有 mandatory section 存在且顺序合规
4. 检查 optional section 在白名单内且插入位置合规
5. 检查 front matter 五字段完整
6. 检查表格列名合规
7. 检查 `**Status**` != `template` 时无 FILL 残留

### ~~格式迁移~~ (删除)

不设 `migrate-truth-format` 命令。格式升级走 `beacon change --refreeze-chain`，其中 change surface 使用 v1.4.12 无编号模板重写 section 标题，然后走完整 refreeze 管线。

## 读模型

### render 函数签名

```python
# beacon/utils/truth_template.py

PRD_MANDATORY_SECTIONS = [
    "Overview", "Problem", "Goals", "Scope",
    "Functional Requirements", "Acceptance Criteria",
    "Non-Goals", "Success Metrics",
]

PRD_OPTIONAL_SECTIONS = {
    "Context": "after_overview",
    "Design Principles": "after_goals",
    "Source Contract": "after_functional_requirements",
    "State Axes": "after_functional_requirements",
    "Runtime Behavior Contract": "after_functional_requirements",
    "Evidence Contract": "before_acceptance_criteria",
    "Diagram Truth Layer": "after_success_metrics",
}

def render_prd_template(*, feature_slug: str, version: str, lang: str = "en") -> str:
    """返回 PRD 固定模板。section 标题无编号纯英文，表格列名无编号纯英文。
       lang 仅控制 **Language** 字段值。"""
    ...

def render_user_story_template(*, feature_slug: str, version: str, lang: str = "en") -> str: ...
def render_test_case_template(*, feature_slug: str, version: str, lang: str = "en") -> str: ...
```

### validate 函数签名

```python
# beacon/utils/truth_format.py

def validate_prd_format(content: str, *, strict: bool = False) -> dict:
    """返回 {status, mandatory_sections_ok, optional_sections_ok,
       no_numbering_prefixes, columns_ok, language_ok, issues: [...]}"""
    ...

def validate_user_story_format(content: str, *, strict: bool = False) -> dict: ...
def validate_test_case_format(content: str, *, strict: bool = False) -> dict: ...

def detect_content_language(content: str) -> str:
    """启发式检测正文语言。返回 "en" 或 "zh"。"""
    ...
```

### load_manifest_or_fail (依赖 version-material-file-map-contract)

```python
# beacon/utils/manifest.py

def load_manifest_or_fail(project_root: Path, version: str) -> dict:
    """v1.4.12+ 强制 manifest，不存在则 fail。"""
    ...
```

## `--lang` 影响范围

| 元素 | --lang en (默认) | --lang zh |
|------|-----------------|-----------|
| Section 标题 | `## Overview`, `## Problem`, `## Goals` ... (无编号) | 同左 (固定英文，无编号) |
| 表格列名 | `FR ID`, `Related AC`, `Requirement` ... | 同左 (固定英文) |
| Front matter 键名 | `**Feature**`, `**Version**` ... | 同左 (固定英文) |
| `**Language**` 字段 | `en` | `zh` |
| FILL 注释 | `<!-- FILL: ... -->` | 同左 (固定英文) |
| 正文预期语言 | 英文 | 中文 |

## 合约边界 (R3)

### 范围内

- section 标题: 纯英文无编号，CLI 固定，不可变
- 正文语言: 默认英文，`--lang zh` 切中文，写入 `**Language**` 字段
- `beacon truth verify` 的语言一致性和结构合规检测
- mandatory/optional section 分类和白名单校验
- 编号前缀拒绝（`## 1.`, `## 2.` 等非法）
- manifest 集成 + gate 阻断 (依赖 version-material-file-map-contract)
- 格式升级走 `beacon change --refreeze-chain`

### 范围外

- 不改变旧版本文件 (不做迁移)
- 不改变 prd.py / prd_bootstrap.py 的旧生成逻辑 (旧流程自然淘汰)
- 不改变 PRODUCT.md / DESIGN.md / research / execution 文档格式
- 语言检测不追求 100% 精确，目标覆盖 95%+ 场景
- 不包含 `beacon doctor migrate-truth-format` 命令
- 不包含版本跳过逻辑

### 显式边界声明

`beacon truth init` / `beacon truth verify` 不是新的 lifecycle stage，是 truth surface 的格式校验辅助服务。格式合规是 truth 冻结的必要条件，不是充分条件。`truth_format_compliant` ≠ `requirement_closure`。

### baseline hash 变更声明

当 `beacon change --refreeze-chain` 使用 v1.4.12 无编号模板重写 section 标题时，truth 内容发生变化（去掉编号前缀），baseline hash 必须重算。这是 refreeze 的合法结果，不是 hash 破坏。此行为与 global-boundaries 第 4 条一致。

## Diagram Truth 传播结构 (D3)

### 运行时改造

#### diagram_truth.py

```python
# beacon/utils/diagram_truth.py 更新

# render_diagram_truth_section: 去掉编号子标题
def render_diagram_truth_section(*, include_diagrams: list[str], state_axes: list[str]) -> str:
    """返回无编号的 Diagram Truth Layer section。
       鼓励使用 mermaid 代码块呈现 branch-flow 和 state-machine。"""
    # 旧: ## 11. Diagram Truth Layer → 新: ## Diagram Truth Layer
    # 旧: ### 11.1 / 11.2 / 11.3 → 新: ### Diagram Types / ### State Axes / ### Branch Flow / ### Propagation Contract
    ...

# parse_diagram_truth: 支持 mermaid 代码块解析
def parse_diagram_truth(version, prd_text, user_story_text) -> dict:
    """新增: 解析 ```mermaid 代码块中的 node 和 transition 列表。"""
    ...
```

#### truth_template.py 新增 optional section

```python
# PRD: Diagram Truth Layer — 已有但格式标准化 (去编号 + mermaid)
PRD_OPTIONAL_SECTIONS["Diagram Truth Layer"] = "after_functional_requirements"

# US: State Axis Coverage — 新增
USER_STORY_OPTIONAL_SECTIONS["State Axis Coverage"] = "after_acceptance_criteria"

# TC: Branch Coverage Mapping — 新增
TEST_CASE_OPTIONAL_SECTIONS["Branch Coverage Mapping"] = "after_coverage_matrix"
```

#### truth_format.py 扩展 verify

当 feature 的 PRD 声明了 diagram truth (diagram_truth.required=True):

1. 校验 US 是否有 State Axis Coverage section 且每个 AC 声明了覆盖的 state transition — warn
2. 校验 TC 是否有 Branch Coverage Mapping section 且每个 diagram branch 有至少一个 TC 覆盖 — warn
3. 覆盖完整性是 warn，不是 strict fail

### baseline hash 变更声明 (D3)

Diagram Truth Layer section 格式变更（去编号 + mermaid 鼓励）和新增 US/TC optional section 不影响 mandatory section 列表，不触发已有 truth 的格式不合规。仅在 `beacon truth verify` 中以 warn 形式提示。
