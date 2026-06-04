# PRD: Beacon 原型到前端实现的路由闭环防漂移（v1.1.10）

## 1. Background

在三个真实项目中，Beacon debug 都暴露了同一类问题：

1. `shopxo_canada`
   - 孤岛页面
   - fragile route
   - legacy-only 入口误判
2. `milemon`
   - utility/footer legal/mega-menu quick links/mobile accordion 漏进原型导航盘点
   - dead link / HTTP 404 / 装饰性跳转
3. `slow_uni_bmtop`
   - tab 不消费路由
   - query/params 口径不统一
   - fake jump（可点击但只 toast）

共同根因不是“页面没写”，而是：

> **Prototype 只有导航骨架，没有实现绑定骨架。**

## 2. First-principles problem

要杜绝前端实现落地偏移，至少要回答五个问题：

1. 哪个交互是 route-producing control
2. 它的目标页面/目标 tab/目标状态是什么
3. 它需要什么上下文参数
4. 它在真实实现里绑定到哪里
5. 当上下文缺失时如何安全回退

当前 Beacon 的 prototype 主链只较好地回答了 1 的一部分与 2 的一部分。

它没有正式回答 3、4、5。

## 3. Goals

1. 为 prototype 新增 route closure contract
2. 为 prototype 新增 implementation binding manifest
3. 让 review/gate 可以正式识别 route closure drift
4. 让 QA matrix 消费 route closure cases
5. 覆盖 shopxo_canada / milemon / slow_uni_bmtop 中暴露的共性问题

## 4. Non-goals

1. 不做全自动前端代码解析器
2. 不做视觉 diff 平台
3. 不承诺一次性覆盖所有框架细节
4. 不替代业务项目自己的前端测试框架

## 5. Functional requirements

### FR-001 `prototype create` must emit route closure contract

新增工件：

- `route-closure-contract.json`

至少包含：

- `required`
- `drift_guardrails`
- `surfaces`
- `closure_cases`

### FR-002 `prototype create` must emit implementation binding manifest

新增工件：

- `implementation-map.json`

至少包含：

- `surfaces`
- `closure_bindings`
- `binding_status`

### FR-003 `prototype review` must fail on unresolved route closure binding

当 `route_closure_required: true` 时：

- 未绑定 case 必须 fail
- `isolated / fragile / legacy-only / fake-jump / tab-route-drift / param-contract-mismatch` 必须 fail

### FR-004 `gate prototype/release` must surface route-closure reason codes

至少支持：

- `prototype_route_closure_contract_missing`
- `prototype_implementation_map_missing`
- `prototype_surface_unbound`
- `prototype_route_closure_drift`
- `prototype_fake_jump`

### FR-005 `test-case create` must synthesize route closure cases

`test-case create` 需要消费 `route-closure-contract.json`，并把这些 case 编进 AC matrix，source 标记为：

- `prototype:route-closure-contract`

### FR-006 Backward compatibility must hold

未声明 `route_closure_required: true` 的旧 prototype 流程不得被强制阻断。

## 6. Solution shape

```text
user-story / prd
→ route_closure_required: true
→ prototype create
  → navigation-map.json
  → interaction-map.json
  → route-closure-contract.json
  → implementation-map.json
→ prototype review
→ gate prototype / gate release
→ test-case create
```

## 7. Success criteria

- Beacon 能在 prototype/review/gate 阶段拦住前端路由漂移
- QA matrix 能覆盖按钮跳转、页面跳转、tab 跳转与孤岛页面场景
- 旧 prototype 功能不回归

## 8. Project evidence summary

### shopxo_canada
- 要点：`Isolated / Fragile / Legacy-only`

### milemon
- 要点：utility/footer/mega-menu/mobile accordion 入口盘点不完整

### slow_uni_bmtop
- 要点：tab route、params/query、fake jump、safe fallback

这些共性足以说明：

> Beacon 需要一个可审计的 route closure contract，而不只是“页面导航看起来像通了”。
