# Prototype Reference Pack v2 Blueprint

## 1. Core principle

Prototype v2 应按如下顺序工作：

```text
collect sources
→ normalize contract
→ resolve page inventory
→ compile page specs
→ render high-fidelity pack
→ review coverage / route / baseline / consistency
→ freeze if trusted
```

不是：

```text
choose archetype
→ fill generic HTML shell
```

## 2. Compiler stages

### Stage A: Source readers

输入源至少包括：

- user-story markdown
- prd markdown
- route sources
- optional code sources
- optional baseline reference sources

### Stage B: Contract normalizer

归一化以下信息：

- coverage mode
- page inventory
- page groups / priorities
- required states
- CTA / tab / route targets
- baseline protection
- token / theme expectations

### Stage C: Inventory resolver

输出：

- required pages
- optional pages
- pages that must be full-hi-fi
- pages protected by baseline rules

### Stage D: Page-spec compiler

每页编译出：

- intent
- layout type
- sections
- components
- state variants
- CTA semantics
- route closure hooks
- truth notes
- baseline guardrails

### Stage E: Renderer

输出：

- overview index
- one page file per required page
- one state file per required page-state pair when required
- shared `theme.json + tokens.css`

### Stage F: Reviewer

严格检查：

- page coverage
- state coverage
- route closure
- baseline regression
- artifact consistency
- stale source

## 3. Data model expectations

Prototype v2 至少需要这些数据结构：

- `prototype-plan.json`
- `coverage-report.json`
- `page-specs/*.json`
- `route-closure-contract.json`
- `implementation-map.json`

其中 `page-spec` 是渲染和 QA 的主消费单元。

## 4. Review contract

Review 必须能回答这些问题：

1. 哪些页面必须存在
2. 哪些状态必须存在
3. 哪些页面绝不能 compact 化
4. 哪些 CTA/tab/page jumps 未闭环
5. 哪些 baseline expressions 被退化
6. manifest / freeze / source / review 是否自洽

## 5. Real-project proof target

规划线实现完成时，至少要能对一个真实复杂 fixture 给出 truthful 输出。

推荐 fixture：

- `slow_uni_bmtop`

目标不是“一次生成完美设计稿”，而是“生成不会违背 requirement materials 的高保真实现参考包”。
