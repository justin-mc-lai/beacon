# Test Cases: Beacon v1.3.10 prototype UX PRD closure and design-asset projection

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | prototype canonical truth 写入完整 design context 字段 | unit | `design_context` 字段齐全且可读取 |
| TC-002 | AC-002 | design context 缺失时，prototype 不能进入 UX freeze ready | integration | review / freeze 给出 fail-closed verdict |
| TC-003 | AC-101 | prototype canonical truth 写入 design reasoning 字段 | unit | `design_reasoning` 字段齐全且可读取 |
| TC-004 | AC-102 | 设计推理层能表达产品表面类型、布局模式、反模式约束 | review | 输出内容不只停留在页面 inventory |
| TC-005 | AC-103 | implement 消费 prototype truth 时不得重新定义页面主判断与优先级 | integration | 实现输入能读取冻结后的 design reasoning |
| TC-006 | AC-201 | prototype 产出正式 `ux_contract` | unit | 包含 first glance、primary decision、action hierarchy、noise rules |
| TC-007 | AC-202 | 每个页面都产出 `page_intent_contract` | unit | 页面都有 decision_supported 与 must_show_first |
| TC-008 | AC-203 | 关键状态都产出 `state_visibility_contract` | unit | loading/empty/error/blocked/stale/success 都具备反馈与恢复规则 |
| TC-009 | AC-204 | prototype 产出 `ux-prd.md` | integration | 人类可读文档收口 design context、reasoning、page intent、state visibility |
| TC-010 | AC-301 | prototype 产出 `DESIGN.md` | integration | 设计资产存在且包含规范章节 |
| TC-011 | AC-302 | prototype 产出 `preview.html` 与 `preview-dark.html` | integration | 两个 preview 资产存在并被索引 |
| TC-012 | AC-303 | `DESIGN.md` 与 preview 由 canonical truth 单向投影生成 | integration | asset sink 共享 transaction metadata |
| TC-013 | AC-304 | design asset 形态对齐 `awesome-design-md` 的人/agent 双消费面 | review | `DESIGN.md + previews` 结构可直接给 agent/human 使用 |
| TC-014 | AC-401 | Beacon 默认 design preset 为 `apple-inspired-design-md` | unit | 默认 preset 字段稳定可见 |
| TC-015 | AC-402 | 默认 preset 至少表达安静中性色、克制强调、内容优先层级 | review | 默认设计说明不再是 generic SaaS 蓝色模板 |
| TC-016 | AC-403 | 项目 requirement 显式覆盖 preset 时会记录 override reason | integration | override 不再静默发生 |
| TC-017 | AC-501 | prototype review 执行 UX/heuristic 检查 | integration | 产出 machine-readable heuristic review 结果 |
| TC-018 | AC-502 | design context / reasoning / page decision / state feedback / assets 缺失时阻断 | integration | review / freeze 返回 block 或 fail |
| TC-019 | AC-503 | 只有结构说明、没有 UX closure truth 的 prototype 不得 freeze pass | integration | static explanation only 被识别并阻断 |
| TC-020 | AC-601 | implement 至少消费 `ux_contract`、`page_intent_contract`、`design_context`、`DESIGN.md` | integration | implement 输入侧可见同一套 prototype truth |
| TC-021 | AC-602 | qa 至少验证页面主判断、状态反馈、machine noise 边界与设计偏离 | integration | qa verdict 能覆盖 UX closure surfaces |
| TC-022 | AC-603 | implement / qa / release 不得因为 runtime mode 切换而改变 UX truth | integration | same feature 在不同 runtime lane 下仍绑定同一 UX closure truth |
| TC-023 | AC-701 | prototype 子 skill / prompt / rule surface 吸收三类参考能力 | review | 规则面明确存在 context、reasoning、asset projection 三层 |
| TC-024 | AC-702 | prototype 语义升级不新增新的公开 lifecycle stage | review | 人类命令面仍只表现为 `prototype` |
| TC-025 | AC-703 | 新增 UX PRD 与设计资产 sink 后仍保持 transaction consistency | integration | `source_hash / projection_seq / transaction_id / sink_checksums` 一致可审计 |
| TC-026 | AC-801 | component catalog 升级为 state-aware contract | unit | component truth 至少包含状态反馈责任与 AC/TC 绑定 |
| TC-027 | AC-802 | 关键状态反馈可追溯到负责组件 | integration | page/state/component 三层责任链完整 |
| TC-028 | AC-803 | implement / qa 消费同一套 component-state contract | integration | 组件级 UX 责任不会在实现/验收之间漂移 |
| TC-029 | AC-901 | prototype 冻结关键跨页业务迁移 contract | unit | from/to page+state、event、guard、fallback 字段完整 |
| TC-030 | AC-902 | 跨页业务迁移绑定 route 或 runtime evidence | integration | 迁移 contract 不再只借用目标页 ready 状态 |
| TC-031 | AC-903 | 跨页业务迁移具备 AC/TC traceability | integration | QA 能读取 transition-level trace refs |
| TC-032 | AC-1001 | prototype 产出 automation priority matrix | integration | 存在 machine-readable 与 human-readable priority 资产 |
| TC-033 | AC-1002 | automation priority matrix 正确区分四类优先级 | review | release-blocker / primary-automation / smoke-only / manual-acceptable 全部可见 |
| TC-034 | AC-1003 | implement / qa / release 消费同一套 automation priority truth | integration | 不同执行 lane 不会重新定义自动化优先级 |

## Regression Focus

- prototype 不得再次退化成 generic wireframe
- prototype 不得只输出结构化说明而缺少 UX closure truth
- design context 不得再次被静默省略
- implement 不得重新发明页面主判断和关键信息优先级
- QA 不得只验证结构文件存在，而不验证 UX closure surfaces
- `DESIGN.md` 不得退化成手工文档或孤立资产
- preview assets 不得脱离 canonical transaction 单独生成
- 默认 design preset 不得回退成通用蓝色 SaaS 模板
- component contract 不得继续停留在 page-global section inventory
- cross-page business transition 不得继续依赖 ready-to-ready 启发式跳转
- QA 不得缺少 automation priority truth

## Execution Notes

- version: `v1.3.10`
- upstream_prd: `docs/beacon/v1.3.10/prd/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- upstream_user_story: `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.md`
- machine_matrix: `docs/beacon/v1.3.10/.machine/qa/beacon-v1.3.10-prototype-ux-prd-closure-and-design-asset-projection.ac-test-matrix.json`
- 本测试矩阵优先覆盖 design context、design reasoning、UX contract、page/state intent、design asset projection、heuristic review、component-state contract、cross-page transitions 与 multi-sink consistency。
