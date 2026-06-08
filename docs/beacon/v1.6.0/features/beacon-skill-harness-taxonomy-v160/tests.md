# 测试：Beacon Skill Harness Taxonomy v1.6.0

## 覆盖矩阵

| AC ID | TC ID | Layer | Assertion |
|-------|-------|-------|-----------|
| AC-001 | TC-001 | docs | v1.6.0 文档使用 `plan -> truth -> generate -> evaluate -> release` 作为用户可见生命周期。 |
| AC-002 | TC-002 | contract | `beacon truth-map resolve` 为 v1.6.0 选择 `features/<slug>/{truth,tests,tasks,evidence}.md` 作为 authority。 |
| AC-003 | TC-003 | contract | 每个 v1.6.0 host-visible skill 名称都匹配 `beacon-(planner|generator|evaluator|governor)-<function>`。 |
| AC-004 | TC-004 | negative | v1.6.0 skill package 中不存在旧 host-visible skill aliases。 |
| AC-005 | TC-005 | contract | 每个 v1.6.0 host-visible skill 都包含共享生成 preamble。 |
| AC-006 | TC-006 | negative | Planner skills 不能写 implementation、frozen truth、QA verdicts 或 release verdicts。 |
| AC-007 | TC-007 | negative | Generator skills 不能在缺少 evaluator evidence 或 fake delivery 检查时声称完成。 |
| AC-008 | TC-008 | negative | Evaluator skills 不能在生成 verdict 的同时改写 truth 或修复 implementation。 |
| AC-009 | TC-009 | contract | Governor skills 被分类为 support/governance surfaces，不能成为 human mainline stages。 |
| AC-010 | TC-010 | integration | Rough prompt routing 输出 outcome、source/truth/evidence refs、湖/海分类、gaps、risks 和 harness route。 |
| AC-011 | TC-011 | negative | Placeholder implementation、docs-only completion、fake runner evidence、zero assertions 和 placeholder evidence 都会被拒绝为 closure。 |
| AC-012 | TC-012 | docs | Migration docs 包含 old-to-new mapping、old alias removal、CLI compatibility boundary 和 operator next steps。 |
| AC-013 | TC-013 | docs | v1.6.0 canonical requirement truth、AC、测试断言、任务台账、迁移说明和 skill preamble 默认以中文为主语言；英文只作为稳定术语或路径标识保留。 |
| AC-014 | TC-014 | contract | `research/<feature-slug>.md` 被识别为 planner `support_advisory` artifact，并包含 outcome、湖/海、truth/source/evidence refs、gaps、risks、recommended_route、user_decision 和 promotion_ref。 |
| AC-015 | TC-015 | negative | 没有 `user_decision=accepted/promoted` 和 `promotion_ref` 的 research artifact 不能写入 package truth，也不能作为 implementation、QA 或 release closure。 |
| AC-016 | TC-016 | contract | v1.6.0 host-visible skill 迁移产物必须只有 `beacon-<harness>-<function>` 新名，且 `SKILL.md` frontmatter/name/description/preamble/boundary 与 Rename Matrix 对齐。 |
| AC-017 | TC-017 | contract | 扫描所有 v1.6.0 host-visible `SKILL.md`，验证共享 preamble 后存在匹配 harness 的 `HARD GATE`，并覆盖禁止跨 harness 调用、越权 truth/implementation/QA/release 动作、假交付闭环和唯一允许产物；缺失或不匹配时 agent-surface verify 必须失败。 |
| AC-018 | TC-018 | behavior | `beacon skill eval-kit benchmark --version v1.6.0` 输出 `eval_metadata/`、`grading/`、`benchmark/`、`analysis/` 四类 runtime evidence artifact，且标记 `runtime_evidence_only=true`、`requirement_truth=false`。 |
| AC-019 | TC-019 | behavior | Benchmark 覆盖 TC-006 到 TC-011、TC-017，把 planner/generator/evaluator/governor 边界、rough routing、no-fake-delivery 和 hard-gate injection 从静态/replay 证明升级为行为证据。 |
| AC-020 | TC-020 | behavior | Benchmark 每个关键 case 同时记录 `with_skill` 与 `baseline` 配置，并聚合 pass rate、boundary violation、fake delivery block 和 delta；baseline 只能作为对照证据，不能替代 gate。 |
| AC-021 | TC-021 | behavior | Grading artifact 必须包含 assertion evidence、reason codes、fake-delivery critique 和 weak-assertion critique；弱断言或假证据不能被记为 release-ready。 |
| AC-022 | TC-022 | behavior | Analysis artifact 必须产出跨 case failure patterns、covered AC/TC、static-only AC/TC、recommended route，并说明 benchmark evidence 不能替代 formal evaluator/release verdict。 |

## 验证说明

v1.6.0 的 coverage truth 位于本 package。Generated QA matrices 和 runtime JSON 可以从它投影，但它们不是 requirement authority。
