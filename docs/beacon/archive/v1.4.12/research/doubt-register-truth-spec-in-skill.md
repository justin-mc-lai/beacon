# Doubt Register: truth-spec-in-skill

- version: `v1.4.12`
- feature: `version-material-file-map-contract` + `unified-truth-template-cli-contract`
- status: `converged`
- date: `2026-05-31`

## Doubt Challenge

**核心怀疑**: v1.4.12 的两项 truth 规范 feature 只改造了 CLI 和校验层，但没有改造 skill 层。LLM 在执行 `beacon-prd`/`beacon-user-story`/`beacon-test-case` 时，仍然没有任何固化格式边界的认知输入，会继续自由发挥 section 命名和结构。

## 最强主张

v1.4.12 固定英文模板 + truth verify CLI 足以约束 truth 格式——skill 层无调整必要，因为 CLI 模板是唯一的 truth 入口。

## 最弱证据

| 证据 | 缺口 |
|------|------|
| `_render_prd` (prd.py:1298) 仍是中英混合、编号不统一的硬编码 | CLI 模板 (`truth_template.py`) 是新建的，但旧入口 `beacon prd create` 仍走 `_render_prd`，没有调用新模板 |
| skill `beacon-prd` 无任何格式规范引用 | LLM 读到 skill 后不知道 section 必须无编号、必须英文、必须从白名单选取 |
| skill `beacon-user-story` 无格式规范引用 | 同上 |
| skill `beacon-test-case` 无格式规范引用 | 同上 |
| `requirement-closure-checklist.md` 只检查闭合链链路，不检查格式 | 闭合检查不覆盖 section 命名、编号、列名规范 |
| `freeze-readiness-checklist.md` 不检查格式 | 同上 |
| `_sections.md` 只管 skill 文档的 section 顺序，不管 truth 文档 | 两套 section 规范完全不同 |
| `prd_bootstrap.py` 的模板函数 (`_minimal_prd_from_downstream`) 使用编号 section | Bootstrap 入口生成的模板不符合 v1.4.12 规范 |

## Doubt 结论

**主张不成立**: CLI 模板不足以约束 truth 格式，因为 LLM 有三个入口可以绕过新模板：

1. `beacon prd create` 仍走 `_render_prd` 老代码，生成的 section 有编号、中英混合
2. skill `beacon-prd`/`beacon-user-story`/`beacon-test-case` 没有将 v1.4.12 格式规范注入 LLM prompt
3. `prd_bootstrap.py` 的 `_minimal_prd_from_downstream` 仍生成编号 section

**真实风险**: 如果只改 CLI 新入口不改 skill 和旧入口，LLM 执行 truth 任务时仍然会产出编号不统一、中英混合的文档——v1.4.12 格式规范只作用于 `beacon truth init` 这一条路径，其他所有路径都在规范之外。

## 收敛方向

需要在三个层面调整 skill 内容：

### 1. Skill 引用 truth-spec 规范

在 `beacon-prd`、`beacon-user-story`、`beacon-test-case` 三个 skill 中新增一个规范引用段，让 LLM 在执行 truth 任务时能够快速认知固化的内容边界：

```markdown
## Truth Format Specification (v1.4.12+)

When writing or editing truth documents for v1.4.12+, follow these format rules:

### PRD Format
- Section titles: plain English names, no numbering (## Problem, not ## 1. Problem)
- Mandatory sections (in order): Overview, Problem, Goals, Scope, Functional Requirements, Acceptance Criteria, Non-Goals, Success Metrics
- Optional sections (insertable): Context, Design Principles, Source Contract, State Axes, Runtime Behavior Contract, Evidence Contract, Diagram Truth Layer
- Front matter: Feature, Version, Status, Date, Language
- Scope subsections: only ### In Scope / ### Out of Scope
- Table columns: FR ID | Related AC | Requirement; Axis | States | Meaning

### User Story Format
- Sections: Story, Acceptance Criteria, Test Story Map, References
- Front matter: Feature, Version, Status, Date, Language
- AC table columns: AC ID | Theme | Description
- Test Story Map columns: Test ID | Covers | Scenario

### Test Cases Format
- Sections: Coverage Matrix, Explicit Non Coverage
- Front matter: Feature, Version, Status, Date, Language
- Coverage Matrix columns: AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path

### Universal Rules
- Content language must match **Language** field (en or zh)
- Section titles and table column names are always English
- No numbering prefixes on section titles
- No extra sections outside the white list
- **Status** != "template" means no FILL placeholders allowed
```

### 2. Skill 级 truth-spec snippet 文件

在 `skills/beacon/references/` 下新增 `truth-format-spec.md`，作为三个 skill 共用的格式规范文件。各 skill 通过相对路径引用，而不是各自重复。

### 3. 旧入口适配

`beacon prd create` 和 `prd_bootstrap.py._minimal_prd_from_downstream` 需要在 v1.4.12+ 强制调用 `truth_template.py` 的渲染函数，生成无编号英文模板。

## 路由

- skill 引用 truth-spec → `beacon-change` (scope 变更)
- 旧入口适配 → 归入 `unified-truth-template-cli-contract` 源码改造清单
- truth-format-spec.md → 归入 `version-material-file-map-contract` (manifest 路径注册)
