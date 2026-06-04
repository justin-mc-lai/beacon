# Test Cases: Beacon 原型到前端实现的路由闭环防漂移（v1.1.10）

**Feature**: beacon-prototype-frontend-route-closure  
**Version**: v1.1.10

## 前置 Gate 结论

- Gate0 输入完整性：Pass
  已有三组真实项目 debug 证据
- Gate1 根因收敛：Pass
  问题被收敛为“原型缺 route closure contract 与 implementation binding manifest”
- Gate2 覆盖策略：Pass
  覆盖 prototype create / review / gate / test-case create 四个主链入口

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | `prototype create` 生成 route closure contract | 存在 `route-closure-contract.json` |
| TC-002 | contract | `prototype create` 生成 implementation binding manifest | 存在 `implementation-map.json` |
| TC-003 | review | route closure required 且 binding 未完成 | `prototype review` fail，出现 `route_closure_binding_complete` |
| TC-004 | gate | review 失败后执行 `gate prototype/release` | 出现 `prototype_surface_unbound` / `prototype_review_failed` |
| TC-005 | fake-jump | binding 标记已 bound 但没有 runtime target/state target | 识别为 fake jump，不可通过 |
| TC-006 | test-case | `test-case create` 消费 route closure contract | AC matrix 中出现 `prototype:route-closure-contract` |
| TC-007 | backward | 未声明 `route_closure_required` 的旧 prototype | 不被新 contract 强制阻断 |
| TC-008 | shopxo | 以孤岛/legacy-only 页面为 drift marker | 能通过 binding drift status 表达并阻断 |
| TC-009 | milemon | 以 quick links / mobile accordion / footer links 为 case | 能表达为 route closure cases，并进入 QA matrix |
| TC-010 | miniapp | 以 tab route / params-query mismatch / fake jump 为 case | review/gate 能阻断 |

## 样板场景

### 场景 A：utility/footer 链接未入原型 inventory

- 预期：route closure contract 必须收录这些入口，不允许只在实现中偷偷存在

### 场景 B：tab 跳转没有真正消费路由

- 预期：tab case 若无 `state_target` 或等价绑定，review fail

### 场景 C：页面已实现但无真实入口

- 预期：binding drift status 可表达 `isolated`，gate blocked

### 场景 D：点击只 toast 不跳转

- 预期：识别为 `fake-jump`，不可通过 review/gate
