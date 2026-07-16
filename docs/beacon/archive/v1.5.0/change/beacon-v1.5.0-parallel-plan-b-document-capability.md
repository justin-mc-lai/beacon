# Change: Beacon v1.5.0 Parallel Plan B Document Capability

- version: `v1.5.0`
- feature: `beacon-v1.5.0-parallel-plan-b-document-capability`
- reason: `中文需求重冻结：确认 v1.5.0 feature package 与 OpenSpec bounded subset 对齐`
- status: `draft`
- language: `zh`

## Summary

本次 change 不扩大 v1.5.0 范围，只把已接受的 v1.5.0 边界用中文重新表述并冻结。v1.5.0 交付新的整体文档能力，但旧 triptych 和 `.machine` 继续作为 canonical truth / gate 基线。

## Accepted Boundary

- v1.5.0 可以实现 `features/<slug>/{truth,tests,tasks,evidence}.md`。
- v1.5.0 必须保留现有 `prd -> user-story -> test-case -> requirement_clarity -> freeze` truth 链路。
- v1.5.0 不删除旧 CLI、旧 skill、`.machine` 或 release / QA authority surfaces。
- Deep、CEO review 仍是 support advisory，不能因为进入 `evidence.md` 索引就变成 gate truth。
- QA verdict 和 release readiness 仍由现有 QA / release 表面决定。

## Accepted OpenSpec Boundary Addendum

- `features/<slug>/truth.md` 必须包含 YAML frontmatter，但 v1.5.0 中该 frontmatter 只是并行/read-model metadata，不替代 `.machine`。
- `features/<slug>/tasks.md` 必须包含 checkbox task ledger，但 checkbox 只能作为可读执行视图或显式 opt-in 输入，不能绕过 implement 或 QA gate。
- CLI 必须提供确定性 parser/validator，读取 frontmatter、AC 表、checkbox rows、evidence authority labels。
- LLM 可以写 markdown 正文和 checklist rows，但 lifecycle state advancement 必须由 CLI 校验后完成。
- `features/<slug>/evidence.md` 继续是 index/read model，不承载 gate truth。
- 相关 skill 必须提供 LLM 可阅读的快速模板示例，帮助生成 parser-compatible 的 `truth.md`、`tests.md`、`tasks.md`、`evidence.md`。

## Implementation Alignment

当前实现提供：

- `beacon materialize-feature-package <feature> --version v1.5.0`
- `beacon validate-feature-package <feature> --version v1.5.0`
- `docs/beacon/archive/v1.5.0/.machine/requirement/feature-package-validation.json`

实现要求保持：

- `gate_authority = canonical_surfaces_preserved`
- `checkbox_gate_bypass = false`
- `evidence_gate_truth = false`
