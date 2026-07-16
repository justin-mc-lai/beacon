# 任务：Beacon Skill Harness Taxonomy v1.6.0

## 任务台账

> Ledger sync 2026-06-10：implementation + formal QA 已通过（`qa-acceptance-beacon-skill-harness-taxonomy-v160.json`，verdict: passed）。下列勾选表示任务 intent 已 closure，非 release runtime switch。

- [x] TASK-001 更新 v1.6.0 lifecycle language 为 `plan -> truth -> generate -> evaluate -> release`。
- [x] TASK-002 保持 v1.5.2+ feature package authority 作为 v1.6.0 truth 来源。
- [x] TASK-003 生成或物化使用 `beacon-<harness-code>-<function-code>` 的 v1.6.0 compact host-visible skill names，其中 code 只能是 `pln/gen/eval/gov`。
- [x] TASK-004 从 v1.6.0 skill package 移除旧 host-visible skill aliases。
- [x] TASK-005 把共享 v1.6.0 skill preamble 生成进所有 host-visible skills。
- [x] TASK-006 增加 planner hard gates：只允许 research-only routing，禁止 implementation/truth/verdict writes。
- [x] TASK-007 增加 generator hard gates：限定 authority 内 artifact generation，并禁止 self-certified completion。
- [x] TASK-008 增加 evaluator hard gates：只做 evidence judgment，不改写 truth，不修复 implementation。
- [x] TASK-009 增加 governor hard gates：只做 support/governance context、archive、memory、hooks、automation、metadata 和 status。
- [x] TASK-010 实现或文档化 rough prompt routing，输出 outcome、refs、湖/海分类、gaps、risks 和 harness route。
- [x] TASK-011 在 implementation、QA 和 release surfaces 强制 no-fake-delivery checks。
- [x] TASK-012 编写 v1.6.0 migration docs，包含 old-to-new skill mapping 和 compatibility boundaries。
- [x] TASK-013 把 v1.6.0 需求真相、AC、测试断言、任务台账、迁移说明和 skill preamble 默认中文主语言策略落入生成/校验规则。
- [x] TASK-014 定义 planner research contract，把 `docs/beacon/<version>/research/<feature-slug>.md` 固定为 `support_advisory` artifact surface，并要求 outcome、湖/海、refs、gaps、risks、route、user_decision、promotion_ref。
- [x] TASK-015 实现或文档化 research 到 truth/change/refreeze 的 promotion gate：没有用户确认和 promotion_ref 时，research 不得自动写 truth 或作为交付闭环。
- [x] TASK-016 实现 skill rename rewrite contract：生成 `beacon-<harness-code>-<function-code>` compact 新 skill，更新 frontmatter/name/description/preamble/boundary，并移除旧 host-visible aliases 和第一版完整 harness 长名 aliases。
- [x] TASK-017 实现 harness-specific HARD GATE 模板注入和 agent-surface verify 扫描：planner/generator/evaluator/governor 各自生成禁止动作、唯一允许产物和跨 harness route 规则，缺失或不匹配时阻断 v1.6.0 skill package。
- [x] TASK-018 实现 `beacon skill eval-kit benchmark --version v1.6.0`，输出 `eval_metadata/`、`grading/`、`benchmark/`、`analysis/` runtime evidence。
- [x] TASK-019 将 TC-006 到 TC-011、TC-017 纳入 benchmark 行为 case，覆盖 harness 越权阻断、rough routing、no-fake-delivery 和 HARD GATE 注入。
- [x] TASK-020 为 benchmark 增加 `with_skill` 与 `baseline` 对照聚合，输出 pass rate、boundary violation、fake delivery block 和 delta。
- [x] TASK-021 为 grading 增加 fake-delivery critique 与 weak-assertion critique，阻断假证据或弱断言被当成 release-ready。
- [x] TASK-022 为 analysis 增加跨 case failure patterns、covered AC/TC、static-only AC/TC 和 recommended route。

## 边界

Checkboxes 只是可读 task-ledger 输入。Formal QA acceptance（2026-06-09）已 closure 本 feature；v1.6.0 runtime promotion 仍受版本级 release gate 约束。
