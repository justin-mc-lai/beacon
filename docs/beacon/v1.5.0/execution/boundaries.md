# Execution Boundaries (v1.5.0)

## Version Position

`v1.5.0` 上线新的 feature-centric 整体文档能力，但不退役既有 Beacon 主链。

Beacon canonical 主链继续保持：

```text
prd -> user-story -> test-case -> implement -> qa -> release
```

新增的 `features/<slug>/{truth,tests,tasks,evidence}.md` 是并行 read-model package，不是新的 lifecycle stage，也不是 `.machine` 的替代提交面。

## Canonical Authority Boundary

- `prd/`、`user-story/`、`qa/test-cases/`、`execution/`、`.machine/` 继续是 v1.5.0 的 canonical stable chain。
- `features/<slug>/truth.md` frontmatter 是 parallel metadata，不替代 revision state、requirement freeze state、QA matrices 或 release readiness。
- `features/<slug>/tasks.md` checkbox 是 task ledger/read model，不能绕过 implement、QA 或 release gate。
- `features/<slug>/evidence.md` 是 evidence index/read model，不承载 gate truth、QA verdict 或 release readiness。
- Deep、CEO review、brainstorm 等 support surfaces 可被索引为 `support_advisory`，但不能替代 truth、QA 或 release gate。

## CLI Parser Boundary

CLI 在 v1.5.0 中必须以确定性方式解析和校验：

- `truth.md` YAML frontmatter。
- `truth.md` Acceptance Criteria table。
- `tasks.md` checkbox rows。
- `evidence.md` authority labels。

LLM 可以写 markdown 正文、AC rows、task checklist 和 evidence index rows；生命周期状态推进必须由 CLI validation 和现有 gate surfaces 完成。

## Migration Boundary

旧体系退役不属于 v1.5.0。任何迁移或替换 canonical triptych / `.machine` 的决策必须推迟到 v1.6+，并基于真实项目验证证据重新冻结。

## Delivery Boundary

Implementation and QA may proceed only when:

- frozen PRD / user-story / test-case 主链可读；
- v1.4.12+ manifest 能识别当前 feature 的 truth paths；
- feature package validation pass；
- formal requirement materials include summary, boundaries, source architecture, skill/QA blueprint, and release placeholders；
- QA/release verdicts 仍来自 canonical surfaces。
