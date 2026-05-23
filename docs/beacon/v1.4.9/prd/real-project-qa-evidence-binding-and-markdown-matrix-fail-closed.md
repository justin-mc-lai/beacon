# PRD: Real Project QA Evidence Binding and Markdown Matrix Fail-Closed

**Feature**: `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## Context

- Research: `docs/beacon/v1.4.9/research/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- Source architecture: `docs/beacon/v1.4.9/source-architecture/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- Upstream defect research: `docs/beacon/v1.4.9/research/qa-evo-deep-human-subskill-and-implementation-qa-closure-gap.md`
- Deferred harness research: `docs/beacon/v1.4.9/research/better-harness-skill-eval-kit-and-source-driven-regression-core.md`

## 1. 问题

Beacon v1.4.9 在真实 BMTOP 项目 QA 验收中暴露出 P0 可信度问题：实现已经存在，Markdown QA 也已经存在，但机器闭环没有正确绑定 implementation evidence，也没有把 Markdown QA 编译为真实 AC matrix。

如果不先修复这一层，后续新增 `qa-evo-deep` 或 Better Harness 都会变成更多解释层，不能阻止真实项目继续出现假稳定信号。

## 2. 目标

- AC-001: Implement 完成或受控导入后，必须写入 QA 可识别的 implementation evidence marker。
- AC-002: Markdown QA 已存在且可解析时，machine AC matrix 必须从 Markdown QA 编译，不得静默 fallback 到占位 AC。
- AC-003: QA runner 必须支持项目级 runner profile，首批至少覆盖 Go + UniApp 命令矩阵。
- AC-004: QA outcome 必须区分 product/test failure 与 runner/environment/auth/evidence admission blocker。
- AC-005: BMTOP `rules-encyclopedia-admin-closure` case 必须进入 regression fixture，防止同类闭环退化。

## 3. 设计原则

### 3.1 Markdown QA truth first

Markdown QA 表格是冻结需求材料的一部分。机器矩阵只能投影它，不能在投影失败时静默生成占位用例。

### 3.2 Evidence binding before QA

QA 不能基于“看起来实现过”进入验收。它必须读取 implementation marker、summary、changed files 或受控 import evidence。

### 3.3 Project runner before generic fallback

真实项目有明确技术栈和命令矩阵时，项目 runner profile 必须优先于 generic fallback。

### 3.4 Admission blocker is not product failure

环境、认证、runner admission、evidence binding 缺口必须明确分类，不得折叠成产品失败。

### 3.5 P0 before harness expansion

Better Harness Skill Eval Kit 和 `qa-evo-deep` 是后续能力，不能替代 P0 runtime 修复。

## 4. 范围

### In Scope

- `beacon implement` 写入 implementation evidence marker。
- `beacon implement import-evidence <feature>` 受控导入外部实现证据。
- Markdown QA table parser 到 `.machine/qa/*.ac-test-matrix.json`。
- parser failure fail-closed diagnostics。
- Go + UniApp project runner profile。
- QA blocker taxonomy。
- BMTOP regression fixture。

### Out of Scope

- Better Harness Skill Eval Kit 的完整实现。
- 新增 `qa-evo-deep` 主能力实现。
- 新增 lifecycle stage。
- release waiver 自动化。
- 自动判断所有历史人工实现是否可信。

## 5. 功能需求

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Implement run 完成时必须写入 QA 可读取的 evidence marker。 |
| FR-002 | AC-001 | 提供 `import-evidence` 受控导入路径，记录 source refs、changed files、summary ref、approved_by。 |
| FR-003 | AC-002 | Markdown QA table 可解析时，machine AC matrix 必须保留原 AC ID、TC ID、command、assertion、evidence path。 |
| FR-004 | AC-002 | Markdown QA parser 失败时必须 fail closed，并输出 parser diagnostics，不得使用占位 fallback。 |
| FR-005 | AC-003 | QA 支持 project runner profile，首批覆盖 Go + UniApp 命令矩阵。 |
| FR-006 | AC-004 | QA outcome taxonomy 必须区分 product_failed、test_failed、runner_admission_blocked、environment_blocked、auth_session_blocked、evidence_binding_missing、coverage_gap、truth_projection_gap。 |
| FR-007 | AC-005 | BMTOP case 必须固化为 regression fixture，验证 implementation marker、Markdown matrix、runner profile、environment blocker 分类。 |

## 6. Diagram Truth Layer

### 6.1 Diagram Types

- `branch-flow`
- `state-machine`
- `decision-priority`

### 6.2 State Axes

- `implementation_evidence`
- `markdown_matrix`
- `runner_profile`
- `qa_outcome`
- `admission_blocker`

### 6.3 Propagation Contract

- Diagram truth must stay explicit through freeze readiness, implementation planning, and QA coverage.
- State axes must not be silently compressed into one implicit status field.

## 7. 冻结交付物

- `docs/beacon/v1.4.9/research/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/v1.4.9/source-architecture/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/v1.4.9/change/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/v1.4.9/prd/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/v1.4.9/user-story/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/v1.4.9/qa/test-cases/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`

## 8. 风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| import-evidence 被滥用伪造实现 | QA 信任错误证据 | 必须记录 source refs、approved_by、changed files，并允许 QA 阻断 |
| Markdown parser 过宽导致误读 | 机器矩阵失真 | parser diagnostics + regression fixture |
| project runner profile 过度定制 | 增加维护成本 | 先覆盖 Go + UniApp 最小命令矩阵 |
| admission blocker 分类过细 | 操作复杂 | 首批只冻结 8 类稳定 taxonomy |

## 9. 成功指标

- BMTOP fixture 不再出现 `implementation_run_not_found` 阻断真实 QA。
- Markdown QA 已存在时，machine AC matrix 不再出现占位验收 fallback。
- Go + UniApp 项目生成真实命令矩阵。
- Docker/testcontainers blocker 被分类为 environment / runner admission blocker。

## 10. 与 Better Harness 的关系

Better Harness 的方向保持有效，但本 P0 change 只吸收其中一条原则：真实失败 trace 必须变成 regression fixture。

完整 Skill Eval Kit、support-skill regression core、trace candidate extraction 留给后续 change。
