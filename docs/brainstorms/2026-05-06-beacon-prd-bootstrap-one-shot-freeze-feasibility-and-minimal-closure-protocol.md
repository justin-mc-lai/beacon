# Beacon PRD Bootstrap One-Shot Freeze Feasibility and Minimal Closure Protocol

## 1. 问题

当前问题不是：

> `beacon-prd-bootstrap` 能不能一键生成三件套。

这个已经能做。

真正的问题是：

> `beacon-prd-bootstrap` 是否应该根据上下文和提示词，直接把需求一键补齐到“冻结闭环 + 待实现”状态？

以及：

> 当 LLM 无法确认信息已闭环时，最短应该补到什么状态，才既不阻断效率，又不破坏 Beacon 的 frozen truth discipline？

## 2. 第一性原理

从第一性原理看，Beacon 的 requirement freeze 不是“文件存在”就成立，而是至少要同时满足三件事：

1. 有结构化 truth
2. 有 closure judgement
3. 有 downstream readiness

`prd-bootstrap` 当前只天然擅长第 1 件事的一部分：

- 能快速生成结构化 draft package

它天然不擅长，或者说不能无条件假设第 2、第 3 件事已经成立：

- 信息是否真的闭环
- 边界是否真的清楚
- AC/TC 是否真的足够
- 是否已经满足 implement readiness

所以高置信度结论是：

> `prd-bootstrap` 可以一键推进到“最短冻结闭环入口”，但不能无条件一键宣称“冻结完成并待实现”。

除非系统能证明闭环信息已经充分。

## 3. 可行性判断

## 3.1 完全自动一键冻结：不可默认成立

默认不可成立，原因有四个：

1. 用户提示词常常只提供意图，不提供约束、边界、异常、角色、依赖、验收口径
2. 当前 bootstrap 实现偏模板生成，不具备强闭环判断能力
3. `freeze-ready` 是一种治理判断，不只是文档写满
4. 如果把“文档生成成功”误当作“需求冻结成功”，会直接破坏 Beacon 的 truth discipline

所以：

> “生成成功 = freeze-ready” 不能默认成立。

## 3.2 条件式一键冻结：可行

如果改成条件式判断，则可行。

也就是：

- 先尝试自动补齐
- 再做闭环判定
- 只有在证据足够时，才直接进入 `implementation-pending`

这本质上不是“一步生成”，而是：

```text
intent
-> draft package generation
-> closure analysis
-> pass: freeze-ready + implementation-pending
-> fail: supplement-required + shortest missing package
```

这条路是可行的。

## 3.3 最短补齐协议：强可行

最可行的不是追求“总能一步冻结”，而是定义：

> 当信息不够时，bootstrap 至少要把需求推进到哪个最短稳定状态。

这个状态必须：

- 比 today 的模板 draft 更强
- 比 formal freeze-ready 更弱
- 但足够让人类或后续 LLM 以最低成本继续补齐

这个方向非常可行，而且最符合 Beacon 轻量内核原则。

## 4. 建议的闭环分层

建议把 `beacon-prd-bootstrap` 的输出状态正式分成 4 层，而不是 2 层。

### Layer A: Intent Draft

输入只有：

- feature name
- 简短描述
- 稀疏提示词

输出：

- 最小 draft 三件套

状态：

- `bootstrap-generated`
- `insufficient-for-freeze`

这层不允许进入 implement。

### Layer B: Minimal Closure Draft

输入除了 intent 之外，还能从上下文里推断出：

- 用户目标
- 主流程
- 最小角色
- 最小异常面
- 最小验收口径

输出：

- 最短可补齐版 PRD / user-story / test-case
- 明确 gap digest
- supplement task 列表

状态：

- `bootstrap-generated`
- `supplement-required`
- `closure-partial`

这层仍不能直接进入 implement，但已经是很好的冻结前入口。

### Layer C: Freeze-Ready Draft

系统通过上下文和 LLM 分析，能够高置信度确认：

- 主流程完整
- 范围清楚
- 关键边界清楚
- AC 足够支撑 TC
- TC 足够支撑 implement/qa 起步
- 没有明显高风险未知项

输出：

- freeze-ready 三件套
- 进入 `implementation-pending` 的正式建议

状态：

- `bootstrap-generated`
- `review-complete-or-review-not-needed`
- `freeze-ready`
- `implementation-pending`

这层才允许直接进入待实现。

### Layer D: Implement-Ready Confirmed

这层比 `freeze-ready` 再多一步：

- execution handoff 已经可读
- 后续 implement 不需要先回头补 requirement 主干

这层可以直接触发：

- `prototype`
- 或 `implement`

但它不是 bootstrap 的默认目标，只应在高置信度场景触发。

## 5. 需要新增的核心判断

如果要支持“条件式一键补齐到待实现”，`prd-bootstrap` 至少要新增一个显式 closure analyzer，而不是只靠模板渲染。

建议新增 3 类判断：

## 5.1 Requirement Closure Score

至少判断：

- 目标是否明确
- 用户对象是否明确
- 主流程是否明确
- 边界是否明确
- 异常/失败路径是否最小覆盖
- AC 是否足够
- TC 是否映射完整
- 是否存在阻断级未知项

输出不要只给分数，还要给：

- `closure_pass`
- `closure_partial`
- `closure_blocked`

## 5.2 Gap Digest

当不能 freeze-ready 时，不要只说“信息不足”，而必须给最短缺口摘要：

- 缺哪个信息
- 缺失影响什么
- 不补会阻断哪一步
- 推荐最短补问

这相当于把 Bootstrap 输出从“文档生成器”升级成“冻结前补齐路由器”。

## 5.3 Readiness Verdict

最终必须有正式 verdict：

- `draft_only`
- `supplement_required`
- `freeze_ready`
- `implementation_pending`

而不是当前较粗的：

- dry-run / applied / blocked

## 6. 最短补齐版本应该长什么样

高置信度建议：

> 当闭环信息不足时，bootstrap 不应继续输出完整但空心的大文档，而应输出“最短闭环版本需求文件”。

它的形式应该是：

### PRD 最短版

只保留：

- 目标
- 范围
- 非目标
- 主流程
- 关键约束
- 已知风险
- 缺口摘要

### User Story 最短版

只保留：

- 角色
- 主目标
- 关键场景
- 当前 AC
- 未闭环问题

### Test Case 最短版

只保留：

- 已有 AC 对应 TC
- 明确缺失覆盖位
- 哪些 TC 需要补料后再生成

关键不是把文档写短，而是：

> 只保留对进入下一步 freeze 补齐真正必要的信息。

这比生成一大份模板化长文更符合 Occam。

## 7. 推荐协议：Bootstrap Closure Protocol

建议 `v1.4.x` 给 `beacon-prd-bootstrap` 增加以下协议：

```text
input
-> context verify
-> draft generation
-> closure analysis
-> gap digest
-> readiness verdict
-> route:
   - draft_only
   - supplement_required
   - freeze_ready
   - implementation_pending
```

### 推荐 machine fields

至少新增：

```json
{
  "closure_verdict": "supplement_required",
  "closure_score": 0.62,
  "gap_digest": [
    {
      "gap_id": "GAP-001",
      "theme": "missing-boundary",
      "question": "该需求的失败回退策略是什么",
      "blocks": ["freeze_ready", "test_case_completeness"]
    }
  ],
  "supplement_tasks": [
    {
      "task_id": "SUP-001",
      "target_doc": "prd",
      "action": "clarify-boundary"
    }
  ],
  "readiness_verdict": "supplement_required"
}
```

## 8. 与现有 Beacon 边界的兼容性

这个方案与 Beacon 当前边界是兼容的。

原因：

1. 不新增新的主 lifecycle stage
2. 不新增新的 truth root
3. 不让 bootstrap 直接越权宣称 release/qa/implement complete
4. 只是把 bootstrap 从“生成 draft”增强成“生成 + 分析 + 最短补齐路由”

它与 `global-boundaries` 也兼容，因为：

- 人类主流程仍然是
  - `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- bootstrap 仍然只是 support surface
- 真正冻结仍然发生在 canonical docs tree

## 9. 风险

## 9.1 最大风险：把 LLM 推断误当成闭环事实

这是最大风险。

缓解方式：

- 必须把“LLM 推断补齐”与“明确上下文证据”分开
- 必须保留 closure verdict
- 高风险缺口不能自动盖过

## 9.2 第二风险：bootstrap 变得过重

如果把它做成 mini-agent pipeline，可能再次变重。

缓解方式：

- 只做最短闭环分析
- 不引入多余 agent 面
- 不引入新的长期状态面
- 复用现有 story/test-case traceability 和 support verdict 机制

## 9.3 第三风险：support skill 污染主心智

如果默认把 bootstrap 叙述成“一键完成需求”，会污染主流程心智。

缓解方式：

- 始终强调 optional support
- 输出永远要显式显示：
  - 当前处于哪一层
  - 是否真的 freeze-ready

## 10. 高置信度结论

高置信度结论如下：

1. `beacon-prd-bootstrap` 不应默认“一键补齐到冻结待实现”，否则会破坏 Beacon 的 truth discipline。
2. `beacon-prd-bootstrap` 可以做成“条件式一键闭环”：
   - 仅当上下文和 LLM 分析足以证明闭环时，才进入 `freeze-ready / implementation-pending`。
3. 当闭环证据不足时，最优策略不是停在粗糙 draft，而是进入：
   - `minimal closure draft`
   - `supplement required`
   - `shortest missing package`
4. 最值得实现的增强，不是更强模板，而是：
   - closure analyzer
   - gap digest
   - readiness verdict
   - shortest supplement routing
5. 这条路线与 Beacon `v1.4.0` 的轻量内核方向一致，而且可行性高。

## 11. 建议下一步

如果要把本头暴转成正式 requirement，建议进入 `beacon-change`，新增一条 `v1.4.x` feature：

- `beacon-prd-bootstrap-closure-analyzer-and-minimal-supplement-routing`

核心新增 requirement 只需要四项：

1. bootstrap closure verdict
2. gap digest and supplement tasks
3. shortest closure draft mode
4. conditional promotion to `freeze-ready / implementation-pending`

这样可以在不扩张主流程的前提下，把 `beacon-prd-bootstrap` 从“安全 draft 生成器”升级成“安全的最短闭环引导器”。
