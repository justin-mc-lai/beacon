# 任务：Beacon Skill Harness Taxonomy v1.6.0

## 任务台账

- [ ] TASK-001 更新 v1.6.0 lifecycle language 为 `plan -> truth -> generate -> evaluate -> release`。
- [ ] TASK-002 保持 v1.5.2+ feature package authority 作为 v1.6.0 truth 来源。
- [ ] TASK-003 生成或物化使用 `beacon-<harness>-<function>` 的 v1.6.0 host-visible skill names。
- [ ] TASK-004 从 v1.6.0 skill package 移除旧 host-visible skill aliases。
- [ ] TASK-005 把共享 v1.6.0 skill preamble 生成进所有 host-visible skills。
- [ ] TASK-006 增加 planner hard gates：只允许 research-only routing，禁止 implementation/truth/verdict writes。
- [ ] TASK-007 增加 generator hard gates：限定 authority 内 artifact generation，并禁止 self-certified completion。
- [ ] TASK-008 增加 evaluator hard gates：只做 evidence judgment，不改写 truth，不修复 implementation。
- [ ] TASK-009 增加 governor hard gates：只做 support/governance context、archive、memory、hooks、automation、metadata 和 status。
- [ ] TASK-010 实现或文档化 rough prompt routing，输出 outcome、refs、湖/海分类、gaps、risks 和 harness route。
- [ ] TASK-011 在 implementation、QA 和 release surfaces 强制 no-fake-delivery checks。
- [ ] TASK-012 编写 v1.6.0 migration docs，包含 old-to-new skill mapping 和 compatibility boundaries。
- [ ] TASK-013 把 v1.6.0 需求真相、AC、测试断言、任务台账、迁移说明和 skill preamble 默认中文主语言策略落入生成/校验规则。
- [ ] TASK-014 定义 planner research contract，把 `docs/beacon/<version>/research/<feature-slug>.md` 固定为 `support_advisory` artifact surface，并要求 outcome、湖/海、refs、gaps、risks、route、user_decision、promotion_ref。
- [ ] TASK-015 实现或文档化 research 到 truth/change/refreeze 的 promotion gate：没有用户确认和 promotion_ref 时，research 不得自动写 truth 或作为交付闭环。
- [ ] TASK-016 实现 skill rename rewrite contract：生成 `beacon-<harness>-<function>` 新 skill，更新 frontmatter/name/description/preamble/boundary，并移除旧 host-visible aliases。
- [ ] TASK-017 实现 harness-specific HARD GATE 模板注入和 agent-surface verify 扫描：planner/generator/evaluator/governor 各自生成禁止动作、唯一允许产物和跨 harness route 规则，缺失或不匹配时阻断 v1.6.0 skill package。

## 边界

Checkboxes 只是可读 task-ledger 输入。没有既有 gate validation 时，它们不能表示 implementation、QA 或 release 已完成。
