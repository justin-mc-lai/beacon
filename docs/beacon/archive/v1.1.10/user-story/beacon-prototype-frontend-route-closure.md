# User Story: Beacon 原型到前端实现的路由闭环防漂移（v1.1.10）

**Feature**: beacon-prototype-frontend-route-closure  
**Version**: v1.1.10

**As a** 使用 Beacon 管理原型、前端实现与验收闭环的维护者 / 前端负责人 / QA owner  
**I want** Beacon 在 prototype、review、gate、test-case 主链中正式引入 route closure contract 与 implementation binding manifest  
**So that** 按钮跳转、页面跳转、tab 跳转、孤岛页面、legacy-only 入口、toast 假跳转等偏移能在 requirement/prototype 阶段被拦住，而不是等到真实项目验收时才暴露。

## Story Slices

### US-001: Prototype 工件新增 route closure contract
作为前端负责人，我希望 prototype 不只产出 `navigation-map.json` 与 `interaction-map.json`，还产出 `route-closure-contract.json`。

### US-002: Prototype 工件新增 implementation binding manifest
作为前端负责人，我希望 prototype 同时产出 `implementation-map.json`，用于把原型 surface/route case 绑定到真实实现。

### US-003: Beacon 能识别按钮/页面/tab 三类跳转闭环
作为 QA owner，我希望 Beacon 能区分 page jump、button jump、tab jump，并要求它们都有明确目标与回退。

### US-004: Beacon 能阻断孤岛页面与 legacy-only 入口
作为 release owner，我希望已实现但无真实入口、或只存在 legacy-only 入口的页面不能被误判为闭环。

### US-005: Beacon 能阻断 fake jump
作为 QA owner，我希望“可点击但只 toast、不真正跳转”的假闭环被正式识别并阻断。

### US-006: Prototype review 必须检查 route closure binding completeness
作为评审人，我希望 `prototype review` 在 route closure required 时，不只检查文件存在，还要检查 binding 是否完整。

### US-007: Gate 必须识别 route closure drift reason codes
作为 release owner，我希望 `gate prototype/release` 能抛出 `prototype_surface_unbound / prototype_route_closure_drift / prototype_fake_jump` 等原因码。

### US-008: Test-case 需要消费 route closure contract
作为 QA owner，我希望 `test-case create` 能把 route closure cases 编入 QA matrix，而不是只消费 navigation/interaction 的宽松骨架。

### US-009: 该解决方案要覆盖 shopxo_canada、milemon、slow_uni_bmtop 暴露出的共性问题
作为版本负责人，我希望新特性明确覆盖：
- utility/footer/mega-menu/mobile accordion 漏入口
- tab 不消费路由
- query/params 口径不统一
- fake jump / toast-only jump
- isolated / fragile / legacy-only 页面

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Route Closure Contract | `prototype create` 产出 `route-closure-contract.json` |
| AC-002 | Implementation Map | `prototype create` 产出 `implementation-map.json` |
| AC-003 | Route Closure Required | 当需求声明 `route_closure_required: true` 时，review/gate 必须检查 route closure 工件 |
| AC-004 | Binding Completeness | `prototype review` 对未绑定 case 抛出失败检查 |
| AC-005 | Drift Markers | `prototype review` / gate 可识别 `isolated / fragile / legacy-only / tab-route-drift / param-contract-mismatch / fake-jump` |
| AC-006 | Fake Jump Block | 已绑定但无真实 runtime target 或 tab state target 的 case 不能通过 review |
| AC-007 | Test Case Synthesis | `test-case create` 会把 `prototype:route-closure-contract` 编进 AC matrix |
| AC-008 | Backward Compatibility | 未声明 `route_closure_required` 的旧版本 prototype 流程不被破坏 |
| AC-009 | Shopxo Coverage | 解决方案覆盖 utility/footer/孤岛/legacy-only 页面类问题 |
| AC-010 | Milemon Coverage | 解决方案覆盖 mega-menu quick links / mobile accordion / dead-link 问题 |
| AC-011 | Miniapp Coverage | 解决方案覆盖 tab route、params/query、fake jump、safe fallback 问题 |

## Risks And Reminders

- 若没有 implementation binding manifest，原型再完整也无法约束真实前端实现
- 若 gate 只检查 prototype 文件存在，不检查 binding 完整性，前端偏移仍会漏过
- 若 QA matrix 不消费 route closure cases，验收仍会只测“页面能打开”，而不测“跳转是否确定性闭环”
