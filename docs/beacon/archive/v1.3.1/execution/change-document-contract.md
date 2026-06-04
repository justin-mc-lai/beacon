# Beacon v1.3.1 Change Document Contract

## Purpose

`implementation-summary` 偏执行摘要。

`technical-implementation` 偏技术归档。

但 release / 交付负责人真正需要的是：

> 本次版本新增了什么、删除了什么、修复了什么、哪些 feature package landed。

因此 `v1.3.1` 要求独立的 `change` 文档面。

## Minimal artifact set

### Feature-level change document

```text
docs/beacon/<version>/change/<feature-slug>.md
```

### Version-level aggregate change document

```text
docs/beacon/<version>/change/<version>.md
```

可选机器镜像：

```text
docs/beacon/<version>/.machine/change/<feature-slug>.json
docs/beacon/<version>/.machine/change/<version>.json
```

## Source-of-truth inputs

`change` 文档不应手写瞎编。

它至少应由这些现有材料归并：

- `execution/implementation-summary-<feature>.md`
- `execution/technical-implementation-<feature>.md`
- `.machine/execution/technical-implementation-<feature>.json`
- `execution/change-impact.json`
- QA scorecard / release readiness 材料

## Required sections

每个 change 文档至少应包含：

1. scope
2. added
3. removed / reduced
4. fixed
5. implementation impact
6. verification status
7. traceability refs

## Classification rule

### Added

- 新增能力
- 新增约束
- 新增交付物

### Removed / reduced

- 删除的入口
- 收窄的公开心智面
- 被废弃的旧假设

### Fixed

- 被纠正的治理漏洞
- 被补齐的交付缺口
- 被阻断的错误流程

## Relationship to version evolution

`change` 文档回答：

- 这次版本具体交付了什么

`version-evolution-blueprint` 回答：

- 这个版本相对上一条线如何演进

两者互补，不互相替代。

## Release rule

进入 release 前，版本级 change 文档必须能回答：

- 本版本包含哪些 feature package
- 哪些 feature package 被推迟
- 哪些 feature package 只完成文档，不进入 release
- 新增 / 删除 / 修复分别是什么

## Minimal implementation guidance

`v1.3.1` 不需要先发明一套新的巨大 writeback 体系。

最小可行做法是：

1. 继续复用当前 `technical-implementation` 的结构化信息
2. 为 feature 和 version 各补一层更轻的 `change` 聚合视图
3. 让 release 真相引用 `change` 文档，而不是要求人类自己读完整技术归档
