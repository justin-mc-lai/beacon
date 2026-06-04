# Workflow Boundaries (v1.1.11)

**run_id**: `run-20260331T023659Z-291e`
**feature**: `beacon-prototype-reference-pack-v2`
**workflow_status**: `planned`

## 1. Intent Boundary

本线只解决一个问题：

> 让 `beacon prototype` 从 archetype demo generator 升级为 story-driven 高保真实现参考包生成器。

它不解决：

- 生产级前端代码输出
- 设计师画布编辑器
- 视觉 diff SaaS
- 任意框架的静态分析全覆盖

## 2. In-scope Control Surfaces

本线关注以下 surface：

- `prototype plan`
- `prototype create`
- `prototype review`
- `prototype freeze`
- `prototype status`
- `test-case` / `gate` 对 prototype artifacts 的消费

## 3. Artifact Boundary

本线要求的 prototype 主工件不是单个 `index.html`，而是 reference pack：

- `prototype-plan.json`
- `page-specs/`
- `pages/`
- `states/`
- `theme.json`
- `tokens.css`
- `coverage-report.json`
- `route-closure-contract.json`
- `implementation-map.json`
- `prototype-review.json`

## 4. Review Boundary

以下问题属于必须阻断项：

- required page 缺失
- required state 缺失
- `full-hi-fi` feature 仍产出 `compact coverage`
- baseline protected page 退化
- route closure 不完整
- source/artifact fingerprints 不一致
- stale source 未被识别

## 5. Real-project Evidence Boundary

规划与实现必须能覆盖下列真实现象：

- `slow_uni_bmtop` 这种 all-page hi-fi + baseline protection + route closure fixture
- 中文标点导致的 contract parsing 偏差
- 手工 polish 与 freeze/manifest/source drift 并存

## 6. Guardrail

workflow / review / gate 只能消费主链 requirement materials 与 prototype artifacts。

仓外聊天、一次性分析、临时截图可以作为研究输入，但不能替代正式工件。
