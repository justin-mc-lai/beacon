# PRD: Beacon Prototype v2 升级为 Story-driven 高保真实现参考包（v1.1.11）

## 1. Problem Statement

### Background

`v1.1.10` 让 Beacon prototype 正式具备了 route closure contract 语义，但当前产品仍然存在一个更基础的交付缺口：

1. prototype 的输入仍然过于扁平，无法稳定表达复杂 feature 的 page inventory / state / baseline / route closure
2. prototype 的渲染单位仍然是 archetype shell，而不是 required page
3. prototype review 仍然偏向字符串存在性检查，无法阻断“看上去像原型、实际上无法实现”的假通过
4. 复杂 takeover 项目需要的是“高保真实现参考包”，而不是单页 demo

### Why this matters now

`slow_uni_bmtop` 暴露出的核心问题不是“页面不够好看”，而是：

- 文档要求 38 页全高保真
- 原型资产仍保留 `compact coverage`
- baseline protected 页面无法被生成器保护
- review 还能给出错误的 pass 语义

这说明 Prototype 的主问题不是样式，而是产品模型。

## 2. First-principles Requirements

Beacon prototype 必须先回答 6 个问题，才有资格生成高保真原型：

1. 当前 feature 的目标用户和主任务链是什么
2. 需要落哪些页面，哪些页面必须高保真
3. 每个页面要表达哪些信息结构、状态和主 CTA
4. 哪些 CTA/tab/page 跳转会产出路由，它们的上下文和 fallback 是什么
5. 哪些既有页面表达已经被验证有效，不能退化
6. 哪些 artifact 会被 implementation / QA / gate 消费

如果这 6 个问题没有先被编译成结构化合同，那么 HTML 再漂亮也只是 demo，不是 reference pack。

## 3. Goals

1. 将 prototype 升级为 `reference-pack-v2`，输出 page-level 高保真实现参考包
2. 将输入源从扁平字段升级为 contract compiler
3. 将 review/gate/freeze 升级为 coverage- / state- / route- / baseline-aware
4. 让 implementation / test-case / gate 可稳定消费 prototype artifacts
5. 让复杂项目 fixture 可以 truthful 表达，而不被 archetype shell 降级

## 4. Non-goals

1. 不做 Figma / 设计师级画布编辑器
2. 不把 prototype 直接变成生产前端代码生成器
3. 不在本线引入 React/Vite 等新的默认构建栈
4. 不试图一次性解析所有框架的运行时细节
5. 不继续通过“更花的模板”掩盖 contract 缺失

## 5. Functional Requirements

### FR-001 新增 Prototype Plan 编译层

新增编译结果：

- `prototype-plan.json`

它必须聚合：

- user-story / prd structured blocks
- route sources
- optional code sources
- optional baseline-protection sources
- coverage mode
- required pages
- required states

### FR-002 输入解析器必须支持 CJK 标点与 block 合同

解析器必须正确消费：

- `；` / `：` / `，`
- 多行列表
- YAML-like blocks
- JSON sidecar blocks

不得再因为中英文标点混用导致 jump_map、states、sections 被截断。

### FR-003 页面 inventory 成为 reference pack 主单位

原型生成不再以 archetype 为主单位，而应先解析：

- `coverage_mode`
- `page_inventory`
- `required_pages`
- `baseline_protection`

archetype 只保留为页面布局默认风格，而不是全部产物的结构代理。

### FR-004 必须为每个 required page 生成 page-spec

新增工件：

- `page-specs/<page>.json`

每个 page-spec 至少包含：

- `page_id`
- `intent`
- `layout_type`
- `sections`
- `components`
- `primary_cta`
- `secondary_ctas`
- `states`
- `route_targets`
- `truth_notes`
- `baseline_guardrails`

### FR-005 必须输出多页面高保真 reference pack

新增输出形态：

- `index.html`
- `pages/<page>.html`
- `states/<page>--<state>.html`

当 contract 声明 `full-hi-fi` 时：

- required pages 必须全部有独立页面/画布
- 不允许回退 `compact coverage`
- 不允许用 coverage matrix 代替真实页面

### FR-006 共享视觉系统必须单源输出

新增或强化工件：

- `theme.json`
- `tokens.css`

必须显式声明：

- palette
- typography
- spacing
- radius
- shadow
- motion reduction
- component material rules

页面应消费共享 token，而不是 per-page 临时硬编码。

### FR-007 Baseline protection 必须进入 contract

新增 contract 语义：

- `baseline_protection`

允许为页面声明：

- 必须保留的信息层级
- 必须保留的交互方式
- 不可退化的状态表达

review 必须能检测这些基线是否被破坏。

### FR-008 Route closure 必须与 page/state/context 合同合并

`route-closure-contract.json` 与 `implementation-map.json` 必须不再只是附加件，而要消费：

- page-spec route targets
- CTA route semantics
- tab state transitions
- params/context requirements
- safe fallback behavior

### FR-009 `prototype review` 必须升级为严格判定

至少新增失败项：

- `prototype_page_inventory_missing`
- `prototype_required_page_missing`
- `prototype_required_state_missing`
- `prototype_compact_mode_detected`
- `prototype_baseline_regression`
- `prototype_artifact_inconsistent`
- `prototype_cjk_parse_failed`
- `prototype_stale`

### FR-010 `prototype freeze/status` 必须基于 artifact consistency

`freeze` 仅允许在以下条件成立时通过：

- review pass
- current source fingerprints 与 recorded source 一致
- manifest / freeze / review / coverage report 自洽
- required artifacts fingerprints 完整

`status` 不得只回显 manifest 中的人为标签，而要报告：

- draft / frozen / stale / inconsistent

### FR-011 Machine consumers 必须读取新的 artifact pack

`test-case`、`review`、`gate`、implementation binding 必须可消费：

- `prototype-plan.json`
- `page-specs/`
- `coverage-report.json`
- `route-closure-contract.json`
- `implementation-map.json`

### FR-012 Backward compatibility 保持

旧 feature 可以继续使用 minimal prototype mode。

但 minimal mode 必须显式表达：

- 不是 `reference-pack-v2`
- 不提供 all-page hi-fi guarantee
- 不保证 baseline protection / strict coverage enforcement

## 6. Command Surface

推荐命令面如下：

- `beacon prototype plan <feature>`
- `beacon prototype create <feature>`
- `beacon prototype review <feature>`
- `beacon prototype bind <feature>`
- `beacon prototype freeze <feature>`
- `beacon prototype status <feature>`
- `beacon prototype list`

### Command semantics

`plan`
- compile sources into a normalized prototype plan

`create`
- render reference pack from prototype plan, not raw markdown only

`review`
- evaluate coverage/state/route/baseline/artifact consistency

`bind`
- attach implementation-map to real code paths and route/runtime targets

`freeze`
- persist trusted source + artifact fingerprints only after strict review

## 7. Artifact Model

推荐目录结构：

```text
docs/beacon/<version>/prototype/<feature>/
  index.html
  prototype-plan.json
  prototype-brief.json
  theme.json
  tokens.css
  navigation-map.json
  interaction-map.json
  coverage-report.json
  route-closure-contract.json
  implementation-map.json
  prototype-review.json
  prototype-review.md
  pages/
    <page>.html
  states/
    <page>--<state>.html
  page-specs/
    <page>.json
```

## 8. Review And Gate Expectations

Review / gate 至少应覆盖：

1. required pages 全部存在
2. required states 全部存在
3. full-hi-fi feature 不含 compact-mode
4. baseline-protected pages 无退化
5. route closure 完整
6. token source 单一
7. stale 检测真实
8. manifest / freeze / review / coverage self-consistent

## 9. Implementation Shape

Prototype v2 的最短实现路径不是“继续补 archetype 模板”，而是：

```text
source readers
→ contract normalizer
→ page inventory resolver
→ page-spec compiler
→ high-fidelity renderer
→ strict reviewer
→ freeze/status controller
```

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| 继续在当前模板上打补丁 | 产物仍然像 demo | 强制引入 prototype plan 和 page-spec 层 |
| schema 过重导致没人会写 | adoption 下降 | 支持 route source / code source 自动补齐 page inventory |
| review 仍然只看字符串存在 | 假通过继续出现 | 新增 coverage / baseline / artifact consistency 检查 |
| complex fixture 仍然无法表达 | 真实项目不敢用 | 用 `slow_uni_bmtop` 做规划期 fixture 和实现期验收样例 |
| backward compatibility 被破坏 | 旧线回归 | 保留 minimal mode 并显式降级语义 |

## 11. Success Criteria

1. prototype 从 archetype demo 升级为 page-level reference pack
2. 复杂 feature 可以表达 all-page hi-fi coverage
3. review/gate 能阻断 compact drift、baseline regression、artifact inconsistency
4. implementation / test-case 可以稳定消费 prototype artifacts
5. `slow_uni_bmtop` 类 fixture 不再需要靠手工原型兜底来绕开 Beacon prototype

## 12. Delivery Note

`v1.1.11` 当前仍是 planning line。

本线的目标不是立刻宣称功能已实现，而是冻结一版正确的问题定义、合同模型和实现分期，避免继续在错误产品模型上迭代。
