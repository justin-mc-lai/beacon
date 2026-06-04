# Beacon v1.3.1 Parallel Feature Package Contract

## Purpose

`v1.3.1` 正式定义：

> 同一个版本不是一份 PRD。  
> 同一个版本是多个并行 feature package 的容器。

Beacon 当前实现已经按 `feature slug` 将 `prd`、`user-story`、`test-case`、`technical-implementation`
平铺写入同一个版本目录。

`v1.3.1` 要做的不是再发明一层复杂结构，而是把这件事明确成正式 contract。

## 做减法后的最小模型

保留当前目录模型，不新增公开命令，不新增额外目录心智。

版本目录仍然长这样：

```text
docs/beacon/<version>/
  prd/<feature-slug>.md
  user-story/<feature-slug>.md
  qa/test-cases/<feature-slug>.md
  execution/technical-implementation-<feature-slug>.md
  execution/implementation-summary-<feature-slug>.md
```

机器镜像继续按同一个 `feature slug` 存放：

```text
docs/beacon/<version>/.machine/
  user-story/<feature-slug>.json
  qa/<feature-slug>.ac-test-matrix.json
  qa/<feature-slug>.qa9-matrix.json
  execution/technical-implementation-<feature-slug>.json
  execution/implementation-summary-<feature-slug>.json
```

## Identity rule

并行 feature package 的绑定键只有一个：

- `feature slug`

这意味着：

- 一份 `prd/<slug>.md`
- 对应一份 `user-story/<slug>.md`
- 对应一份 `qa/test-cases/<slug>.md`

如果 `slug` 不同，就视为不同 feature package。

## One-to-one rule

在同一个版本中，必须满足：

1. 一个 `prd` 只能映射自己的 `user-story`
2. 一个 `user-story` 只能映射自己的 `test-case`
3. 一个 feature package 不得借用另一个 feature package 的冻结真相
4. 一个 feature package 的 implementation / QA / acceptance writeback 只能回写自己的 slug

## Parallelism rule

同一个版本可以同时存在：

- `feature-a`
- `feature-b`
- `feature-c`

这些 feature package 可以并行推进：

- 需求澄清
- 冻结
- 实现
- QA

但 release 仍是版本级聚合动作。

## Human-facing interpretation

对人类而言，不新增新的主命令。

主链仍然只有：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

变化只在于：

- 每次沿着主链处理一个 feature package
- 到 release 时再看版本级汇总

## Release aggregation rule

版本 release 至少要聚合这些信息：

- 哪些 feature package 已完成
- 哪些 feature package 被推迟
- 哪些 feature package 被删除 / 收敛
- 当前版本的 `change` 文档覆盖了哪些 package

## Forbidden patterns

以下做法在 `v1.3.1` 中应视为错误：

- 默认一个版本只能有一份 PRD
- 不同 feature 共享一份 user-story 或 test-case
- 一个 feature 的实现结果回写到另一个 feature 的 revision / QA 状态
- release 时无法说明本次版本到底包含哪些 feature package

## Why this is the smallest correct step

因为 Beacon 现有实现已经做到了：

- 同版本目录下按 feature 写文件
- `implement` 输出 `implementation-summary-<slug>` 与 `technical-implementation-<slug>`
- `review` / `qa` 也按 feature slug 消费材料

所以 `v1.3.1` 不需要先改成更重的 package tree。

先把隐式能力升格成显式 contract，才是更小也更稳的一步。
