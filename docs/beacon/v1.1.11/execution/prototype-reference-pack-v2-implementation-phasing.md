# Prototype Reference Pack v2 Implementation Phasing

## Phase 0: Parser hardening

目标：

- 修复 flat parser 对中文标点、多行 block、结构化列表的脆弱性
- 建立 `prototype-plan.json` 的最小 schema

完成标准：

- `jump_map` / `states` / `sections` 不再因 `；：，` 混用而退化

## Phase 1: Prototype plan + page inventory

目标：

- 新增 prototype plan 编译层
- 解析 `coverage_mode`
- 解析 required page inventory
- 输出 baseline protection 语义

完成标准：

- Beacon 能回答“需要哪些页面 / 哪些页面必须 full-hi-fi”

## Phase 2: Page-spec compiler + multi-page renderer

目标：

- 生成 `page-specs/`
- 渲染 `pages/*.html`
- 渲染关键状态页面
- 输出共享 `tokens.css`

完成标准：

- required pages 全部拥有独立页面级输出

## Phase 3: Strict review / freeze / status

目标：

- review 检查 page/state coverage
- review 检查 compact drift / baseline regression / artifact inconsistency
- freeze 受 review/stale/self-consistency 约束

完成标准：

- 明显不 truthful 的 prototype 不能再得到假 pass

## Phase 4: QA / gate / implementation consumers

目标：

- `test-case` 消费 page-spec / coverage report / route closure
- gate 消费新的 reason codes
- implementation-map 与 page specs 联动

完成标准：

- prototype artifacts 成为实现和 QA 的正式输入，而不是旁路说明材料

## Phase 5: Real fixture validation

目标：

- 以 `slow_uni_bmtop` 这类复杂 fixture 做 acceptance proof

完成标准：

- all-page hi-fi intent、baseline protection、route closure 三者能同时被 truthful 表达
