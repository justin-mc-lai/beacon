# Prototype Design Governance Blueprint

## 1. Core principle

Prototype 设计治理必须按如下顺序工作：

```text
resolve version truth
→ resolve project mode + execution surface
→ confirm bounded learning surfaces
→ collect requirement sources
→ bounded autoresearch divergence
→ converge design brief
→ normalize design-system contract
→ render reference pack
→ audit against web-interface rules
→ produce design review outcome
→ keep/discard next iteration inputs
```

不是：

```text
render first
→ subjective visual opinion later
```

也不是：

```text
help/navigator 先默认 native implementation
→ 之后再补 project boundary / takeover baseline
```

## 2. Compiler stages

### Stage 0: Version truth + project boundary gate

进入 prototype / implement / review 前先确认：

- current runtime line vs planning line
- project mode (`greenfield` / `takeover` / `project-profiled`)
- stage-local execution surface
- learning-plane subject surfaces
- takeover baseline gate

### Stage A: Requirement + research readers

输入至少包括：

- user-story
- prd
- optional research docs
- project profile / service-slice / boundary docs as read-only contract inputs
- prototype plan inputs

### Stage B: Design brief compiler

归一化：

- audience
- tone
- visual direction
- typography intent
- palette intent
- motion intent
- differentiator

### Stage C: Design-system normalizer

输出：

- font families
- token palette
- spacing / radius / shadow / motion rules
- anti-generic restrictions

### Stage D: Renderer handoff

将 design-system contract 与 prototype plan 一起交给 reference-pack renderer。

同时要求 renderer 负责：

- 统一目录页
- `ui-style-analysis` 工件
- page/state 跳转闭环

### Stage E: Guideline auditor

拉取最新 web guideline 规则并输出 findings artifact。

### Stage E1: Design security review

`review design` 在 Beacon 中承担 cso-inspired 的软件设计安全审查。

它不是新的顶级安全平台，而是 review 阶段的附加判断面。

### Stage F: Iteration governor

根据 findings 与 benchmark 决定：

- keep
- review
- discard
- next iteration input

## 3. Real closure questions

设计治理完成后，Beacon 必须能回答：

1. 当前版本真相是什么，当前任务在哪个 execution surface 上运行
2. 为什么这个原型长成这样
3. 哪些视觉规则是共享 contract
4. 哪些规则是硬违规
5. 哪些 finding 必须在下一轮修复
6. 哪些策略改动值得 keep/discard
