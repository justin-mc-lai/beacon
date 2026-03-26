# Test Cases: Beacon 原型基线、实现绑定与防漂移 Debug 闭环（v1.1.8）

**Feature**: beacon-prototype-baseline  
**Version**: v1.1.8

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备 prototype 当前能力、milemon 真实案例与目标设计）
- Gate1 冲突未决判定：Pass（问题已明确聚焦在 baseline/binding/verify/debug，而非泛化到所有前端生成）
- Gate2 AC→TC 映射：Pass（覆盖 baseline、binding、verify、debug、lifecycle、milemon 样板）

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | 从已 freeze 的 prototype 生成 baseline manifest | 产出 `baseline.json`，且包含 surface/state/breakpoint/token/effect |
| TC-002 | exception | baseline 缺少关键 surface/state/token | `prototype baseline` fail-fast，给出缺失字段 |
| TC-003 | contract | 为 feature 生成 implementation binding manifest | 产出 `implementation-map.json`，可绑定 route/url/code path/selectors |
| TC-004 | contract | 使用 WordPress adapter 绑定 Milemon 首页/详情页 | baseline surface 正确映射到 `front-page.php` / `header.php` / `woocommerce/*` |
| TC-005 | contract | 使用非 WordPress adapter | schema 仍成立，不出现 WordPress 专属硬编码字段依赖 |
| TC-006 | token | prototype theme token 映射到实现 token | 产出 `token-map.json`，主色/辅色/间距/字体/阴影/圆角/动效映射清晰 |
| TC-007 | integration | 运行 `prototype verify-impl` | 产出 `verify-implementation.json / .md` |
| TC-008 | diagnosis | 视觉结构与 baseline 不一致 | 输出 `prototype_visual_drift` |
| TC-009 | diagnosis | 标题/语义结构/required selector 缺失 | 输出 `prototype_semantic_drift` |
| TC-010 | diagnosis | CTA / jump / modal / state 无法触发 | 输出 `prototype_interaction_drift` |
| TC-011 | diagnosis | 主题色/设计 token 与 baseline 映射不符 | 输出 `prototype_token_unmapped` 或等价 drift reason |
| TC-012 | diagnosis | hover/focus/motion/effect 未按 baseline 落地 | 输出 `prototype_effect_drift` |
| TC-013 | exception | surface 未绑定就执行 verify-impl | `overall_status=blocked`，reason=`prototype_surface_unbound` |
| TC-014 | gate | 启用 prototype baseline 治理时未做 verify-impl | `review quality` / `review accept` blocked |
| TC-015 | gate | baseline stale / binding stale | gate blocked，需 reopen/rebind/rerun |
| TC-016 | debug | 开启 `prototype debug --watch` | 持续输出 mismatch queue、severity、建议修复范围 |
| TC-017 | debug | 修复后 rerun verify-impl | report 更新，已解决项关闭，未解决项保留 |
| TC-018 | lifecycle | baseline 在 Verified 后被重写 | 旧 revision 标记 superseded，新 revision 重新 Reviewed/Frozen/Bound/Verify |
| TC-019 | milemon | Milemon `site-visual-system` 可绑定全站 token 与关键模板 | 能表达 theme token → `design-tokens.css` / `style.css` 的关系 |
| TC-020 | milemon | Milemon 首页 hero / 顶栏 / 业务闭环卡片与 baseline 对比 | 差异可在 surface 级被报告 |
| TC-021 | regression | 非 UI / 非 baseline 治理 feature | 不被强制绑定 prototype baseline，旧流程不回归 |
| TC-022 | scope | v1.1.8 当前仅为设计方案 | 文档明确 planned/design-only，不误报已实现 |
| TC-023 | audit | 基于 `frontend-design` 审计当前 prototype generator | 能明确指出字体、构图、CTA、背景/层级的 generic 风险 |
| TC-024 | audit | 基于 `web-design-guidelines` 审计当前 prototype shell | 能明确指出 skip link、icon aria、tab semantics、表单语义等基线缺口 |
| TC-025 | contract | baseline manifest 包含 aesthetic baseline pack | 至少包含 design_direction/font_pair/palette_hierarchy/surface_density/cta_tone |
| TC-026 | review | finalized review 可识别 generic CTA 与模板化 card shell 退化 | 输出 `prototype_aesthetic_regression` 或 `prototype_ui_guideline_gap` |

## Milemon 样板场景

### 场景 A：主题 token 绑定
- prototype `theme.json.primary = #F26522`
- 实现 `assets/css/design-tokens.css` 中 `--color-primary = #F26522`
- 预期：Beacon 能识别为 token mapping pass，而不是只把 `theme.json` 存档不消费

### 场景 B：全局头部与首页 CTA 漂移
- prototype baseline 要求首页 hero + quote/catalog CTA + 顶栏 secondary nav
- 实现若缺失某个 CTA 或 header 结构变化
- 预期：输出 surface 级 drift，不能被“页面大体差不多”掩盖

### 场景 C：WooCommerce 页面绑定
- `catalog` 绑定 `woocommerce/archive-product.php`
- `product-detail` 绑定 `woocommerce/single-product.php`
- 预期：Beacon 能在 verify-impl 中按绑定结果做对比，而不是只看首页

### 场景 D：开发期 debug 闭环
- verify-impl 发现 `prototype_effect_drift`
- 开启 debug watch，输出受影响 surface、selector、code path 与 rerun command
- 预期：开发者修复后可立即 rerun，并更新 diff report

### 场景 E：原型自身审美退化
- generator 输出仍使用过于 generic 的字体、CTA fallback、重复 card/table/list shell
- 预期：review/audit 不能只给 pass，而应明确提示需要补齐 aesthetic baseline

## 执行语义

- `Pass`：baseline / binding / verify / debug / lifecycle / milemon 样板设计都能自洽闭环
- `Fail`：仍无法确定 prototype 如何约束真实实现，或 debug/gate 语义缺失
- `Blocked`：baseline schema、binding schema、verify layer 或 lifecycle 仍存在关键冲突
