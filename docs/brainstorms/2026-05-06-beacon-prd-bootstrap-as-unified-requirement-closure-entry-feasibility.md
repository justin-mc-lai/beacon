# Beacon PRD Bootstrap as Unified Requirement Closure Entry Feasibility

## 1. 问题重述

本次要分析的不是：

- `beacon-prd-bootstrap` 能不能生成三件套
- `beacon-prd-bootstrap` 能不能做最短补齐

而是更强的命题：

> 在 `v1.4.0` 中，是否可以把 `beacon-prd-bootstrap` 提升为 requirement closure 的统一入口，使其在以下任意不完整状态下都可接管，并通过上下文与提示词，把需求推进到“一键闭环冻结 / implementation-pending”：

- 只有 `prd`
- 只有 `user-story`
- 只有 `test-case`
- `prd + user-story`，缺 `test-case`
- `prd + test-case`，缺 `user-story`
- `user-story + test-case`，缺 `prd`
- 三件套都存在，但部分过旧/不完整/不一致

换句话说：

> `beacon-prd-bootstrap` 是否可以不再只是启动器，而是成为 requirement lifecycle 子 skill 的统一代理入口。

## 2. 先看与全局边界是否冲突

先看 `docs/beacon/global-boundaries.md`，高置信度结论是：

- 它**不禁止**内部把复杂度吸收到机器内部
- 它**禁止**扩张人类主流程
- 它**要求** requirement truth 仍然回到：
  - `prd -> user-story -> test-case -> acceptance`
- 它**不允许** runtime/局部状态绕过 requirement truth

因此：

> 只要 `beacon-prd-bootstrap` 仍然是 support surface，而不是新 public stage，那么它在内部代理 `prd / user-story / test-case` 是不违反全局边界的。

也就是说，从架构边界上：

- 不能把它说成“主流程替代”
- 但可以把它实现成“主流程编排代理”

## 3. 第一性原理判断

如果从用户视角看，用户真正要的不是：

- 分别记住 `prd`、`user-story`、`test-case` 三个命令

用户真正要的是：

- 给一个需求意图
- 系统自动识别当前 requirement package 缺什么
- 自动补齐缺失层
- 自动校验是否闭环
- 闭环后进入待实现

所以从产品一阶目标看，把 bootstrap 变成 unified requirement closure entry 是合理的。

问题只在于：

> 它能不能在不破坏 Beacon truth discipline 的情况下做到。

答案是：

> 可以，但前提不是“替代 requirement truth”，而是“统一代理 requirement compile and closure”。

## 4. 高置信度结论

高置信度结论如下：

1. `beacon-prd-bootstrap` 可以升级成 requirement closure 的统一入口。
2. 但它不能语义上“代替 requirement lifecycle”。
3. 它真正能代替的，是：
   - requirement 子 skill 的人工逐个调用动作
4. 它不能代替的，是：
   - PRD / User Story / Test Case 这三层 truth 本身
   - freeze judgement
   - gate judgement

所以最准确的表述不是：

> `prd-bootstrap` 代替其他 lifecycle 子 skill。

而是：

> `prd-bootstrap` 统一代理其他 requirement compile 子 skill，并在内部完成缺口识别、补齐编排、闭环判断与最短冻结推进。

## 5. 推荐定位修正

建议把 `beacon-prd-bootstrap` 的正式定位从：

- requirement draft initializer

升级为：

- unified requirement closure entry
- optional support orchestrator
- requirement compile proxy

但仍保留两个约束：

1. 它不是 public lifecycle stage
2. 它不是新的 truth root

## 6. 这件事为什么是可行的

因为从现有源码上看，`prd`、`user-story`、`test-case` 本身已经有明显的“可代理 compile”特征：

- `prd.py` 已具备更强的语义编译和上下文读取
- `user_story.py` 已支持从已有 requirement truth 反推 story payload
- `test_case.py` 已支持从 PRD / user-story / QA rows 扩展 coverage
- `prd_bootstrap.py` 已经有统一写入与安全防线

所以架构上欠缺的不是基础能力，而是：

1. partial package detection
2. per-layer gap inference
3. closure ordering
4. promotion verdict

也就是：

> 现在缺的是“requirement closure orchestrator”，不是缺生成器。

## 7. 需要支持的 7 类输入状态

如果要让 `beacon-prd-bootstrap` 成为 unified entry，它至少要显式支持 7 类状态：

### S1. Empty Package

- `prd` 不存在
- `user-story` 不存在
- `test-case` 不存在

动作：

- 从 intent 生成三件套
- 然后做 closure analysis

### S2. PRD Only

- `prd` 存在
- 其余不存在

动作：

- 从 PRD truth 编译 user-story
- 从 PRD + user-story 编译 test-case
- 再做 closure analysis

### S3. User Story Only

- `user-story` 存在
- 其余不存在

动作：

- 尝试从 story 反推最小 PRD shell
- 再从 PRD + story 生成 test-case
- 标记 `reverse-derived-prd`

这类风险高于 `PRD only`。

### S4. Test Case Only

- `test-case` 存在
- 其余不存在

动作：

- 反推最小 user-story
- 再反推最小 PRD shell
- 标记 `reverse-derived-truth`

这类风险更高，应默认更难直接 freeze-ready。

### S5. PRD + User Story

- 两者存在
- `test-case` 缺失

动作：

- 直接补 test-case
- 再做 AC/TC completeness closure

这是最适合一键闭环的类型之一。

### S6. PRD + Test Case

- `user-story` 缺失

动作：

- 用 PRD promised surfaces 与 test-case coverage 反编译 user-story
- 再检查 traceability

### S7. User Story + Test Case

- `prd` 缺失

动作：

- 反推最小 PRD shell
- 标记 derived-from-downstream

这类也能支持，但默认不应直接高置信度 freeze-ready，除非证据特别强。

## 8. 真正的难点

真正难点不是“生成哪份文件”，而是：

## 8.1 上游缺失时的 truth 逆推风险

Beacon 当前的真相链条是：

```text
prd -> user-story -> test-case
```

如果只给下游产物，让系统反推上游 truth，本质上是在做：

```text
test-case -> user-story -> prd
```

这是可做的，但必须显式标记：

- `derived_from_downstream`
- `needs_truth_review`

否则会破坏“上游定义承诺、下游定义验收”的秩序。

## 8.2 三件套存在但不一致时，谁说了算

如果三件套都存在但互相冲突：

- PRD scope A
- User Story scope A+B
- Test Case scope B+C

这时 unified entry 不能静默重写。

必须进入：

- drift digest
- repair route
- refreeze recommendation

也就是说：

> unified entry 可以编排修复，但不能静默裁决 truth。

## 8.3 “一键闭环”并不等于“无条件 freeze-ready”

一键闭环真正应该表示：

- 系统把缺失 requirement layers 都补齐
- 系统把 gap 和风险都显式化
- 系统做出 readiness verdict

而不是表示：

- 总能自动通过 freeze

## 9. 推荐协议：Unified Requirement Closure Orchestration

建议把 `beacon-prd-bootstrap` 升级为以下协议：

```text
detect current requirement package state
-> identify missing layers
-> compile missing layers in canonical order
-> if reverse-derivation is needed, mark it explicitly
-> run consistency + closure analysis
-> produce readiness verdict
-> route:
   - freeze-ready / implementation-pending
   - supplement-required
   - drift-repair-required
```

### 需要新增的 machine fields

```json
{
  "package_state": "prd_only",
  "missing_layers": ["user_story", "test_case"],
  "derived_layers": [
    {
      "layer": "user_story",
      "derived_from": ["prd"]
    }
  ],
  "reverse_derived_layers": [],
  "drift_digest": [],
  "closure_verdict": "freeze_ready",
  "readiness_verdict": "implementation_pending"
}
```

### package_state 建议枚举

- `empty`
- `prd_only`
- `user_story_only`
- `test_case_only`
- `prd_user_story`
- `prd_test_case`
- `user_story_test_case`
- `full_consistent`
- `full_inconsistent`

## 10. 对 requirement 子 skill 的影响

如果按这条路走，`prd`、`user-story`、`test-case` 子 skill 不会消失。

它们会变成：

- explicit fine-grained requirement editing surfaces

而 `prd-bootstrap` 变成：

- unified closure entry

类比来说：

- `prd / user-story / test-case` 是手工档位
- `prd-bootstrap` 是自动档位

但它们仍然产出同一个 truth tree。

## 11. 是否真的“代替其他需求生命周期子skill”

严格说，不应这样定义。

更准确的是：

### 可以代替的

- 人类手动依次调用 `prd`、`user-story`、`test-case`
- 人类自己判断当前缺哪层
- 人类手工做最短补齐编排

### 不能代替的

- requirement truth 的三层结构
- freeze judgment
- change/refreeze when drift exists
- downstream gate judgment

因此：

> 它可以代替“调用动作”，不能代替“truth structure”。

## 12. 推荐的 verdict ladder

建议 unified entry 最终只输出 5 种 verdict：

1. `draft_generated`
2. `supplement_required`
3. `drift_repair_required`
4. `freeze_ready`
5. `implementation_pending`

规则：

- `implementation_pending` 只能在 `freeze_ready` 之后
- `drift_repair_required` 高于 `supplement_required`
- `reverse-derived upstream truth` 默认不能直接给 `implementation_pending`，除非高置信度证据足够

## 13. 哪些场景最适合直接一键闭环

高适配场景：

1. `PRD only`
2. `PRD + user-story`
3. `full package but minor missing gaps`

中适配场景：

1. `PRD + test-case`
2. `user-story + test-case`

低适配场景：

1. `test-case only`
2. `full inconsistent`

这意味着 unified entry 可以覆盖所有状态，但不是所有状态都同等容易直接 freeze-ready。

## 14. 高置信度结论

高置信度结论如下：

1. `beacon-prd-bootstrap` 可以升级成 unified requirement closure entry。
2. 这不违反 `global-boundaries`，前提是它仍然是 support surface，而不是新 public stage。
3. 它不应被定义为“替代 requirement lifecycle”，而应定义为“统一代理 requirement compile and closure orchestration”。
4. 它可以在 `PRD only / PRD+story / partial package / inconsistent package` 等状态下工作。
5. 但它必须新增：
   - package state detection
   - missing layer compile
   - reverse-derived truth marking
   - drift digest
   - closure verdict
   - readiness verdict
6. 它确实可以在很多场景下做到“一键闭环冻结并进入待实现”，但前提是：
   - closure evidence 足够
   - 没有高风险 drift
   - 上游 truth 不是纯粹由下游硬反推出来

## 15. 建议下一步

如果要把这个方向正式纳入 `v1.4.x`，建议走 `beacon-change`，新增一条正式 feature：

- `beacon-prd-bootstrap-unified-requirement-closure-orchestration`

最小 requirement 只需冻结 5 个能力：

1. package state detection
2. missing-layer compile orchestration
3. reverse-derived truth labeling
4. drift repair routing
5. conditional promotion to `freeze_ready / implementation_pending`

这是目前最符合 Beacon 轻量内核、又最能降低 requirement 子 skill 操作摩擦的高价值方向。
