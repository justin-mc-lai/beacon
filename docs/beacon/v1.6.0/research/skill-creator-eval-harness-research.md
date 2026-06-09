---
slug: skill-creator-eval-harness-research
version: v1.6.0
authority: support_advisory
status: routeable
source: qi-dev-personal-brain
created: 2026-06-08
updated: 2026-06-08
truth_refs:
  - docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md
  - docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md
  - docs/beacon/v1.6.0/execution/project-skill-qa-evolution-blueprint.md
source_refs:
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/SKILL.md
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/scripts/run_eval.py
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/scripts/run_loop.py
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/scripts/aggregate_benchmark.py
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/agents/grader.md
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/agents/analyzer.md
  - /Users/apple/Developer/Personal/oss-sync/core-skills/skills/skills/skill-creator/agents/comparator.md
  - /Users/apple/Developer/Personal/oss-sync/core-skills/openai-skills/skills/.system/skill-creator/SKILL.md
  - /Users/apple/Developer/Personal/oss-sync/core-skills/openai-skills/skills/.system/skill-creator/scripts/init_skill.py
  - /Users/apple/Developer/Personal/oss-sync/core-skills/openai-skills/skills/.system/skill-creator/scripts/quick_validate.py
  - /Users/apple/Developer/Personal/oss-sync/core-skills/openai-skills/skills/.system/skill-creator/scripts/generate_openai_yaml.py
evidence_refs:
  - /Users/apple/Developer/Personal/oss-sync/index/repos.json
  - /Users/apple/Developer/Personal/oss-sync/index/sync-summary.json
user_decision: pending
promotion_ref: ""
---

# Skill Creator Eval Harness Research

## Outcome

调研 Anthropic `skill-creator` 与 OpenAI `skill-creator` 的设计、实现和 eval 方法，给 Beacon v1.6.0 的 `beacon-skill-harness-taxonomy-v160` 提供实现建议。

## Lake Or Ocean

判断为湖。范围集中在 skill 创建/校验/eval harness，不需要扩成通用 agent benchmark 平台。v1.6.0 可先实现结构校验、harness gate 校验、触发/路由 eval、with-skill vs baseline 对照、grader/analyzer 产物，再把 UI viewer 和自动 description optimizer 放到后续增强。

## Truth Refs

- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md`
- `docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md`
- `docs/beacon/v1.6.0/execution/project-skill-qa-evolution-blueprint.md`

## Source Refs

- Anthropic mirror：`/Users/apple/Developer/Personal/oss-sync/core-skills/skills`，head `c30d329f5814647c1e2f071020c1e8c1c9893ef1`
- OpenAI mirror：`/Users/apple/Developer/Personal/oss-sync/core-skills/openai-skills`，head `a8924c2a35cfa290458852c4fad17c9133054c2e`

## Findings

Anthropic `skill-creator` 的核心不是模板，而是闭环 eval：

- 先起草 skill，再创建真实用户 prompt 的 `evals/evals.json`。
- 每个 eval 同时跑 `with_skill` 和 baseline，避免分批运行造成环境/时间差。
- run 过程中补 objective assertions，完成后把 timing、outputs、transcript、grading 固化进 workspace。
- `grader.md` 不只判 pass/fail，还要求检查 evidence 是否真实、输出是否表面合规、assertion 是否太弱。
- `aggregate_benchmark.py` 按配置聚合 pass_rate、time、tokens，并计算 delta。
- `analyzer.md` 负责看 aggregate 看不出的模式，例如两边都通过的弱断言、flaky 断言、skill 反而降低表现的场景。
- `comparator.md` 用 blind comparison 比较输出质量，避免对某个 skill 版本产生偏见。
- `run_eval.py` 单独验证 description trigger：临时注册 command/skill，读取 stream events 判断是否触发，支持多 worker、多次运行和 trigger threshold。
- `run_loop.py` 对 description 做 train/test split 和 holdout，减少对 trigger eval 过拟合。

OpenAI `skill-creator` 的重点更偏 Codex/产品化 skill 结构：

- `init_skill.py` 标准化 name、生成 `SKILL.md`、可选 `scripts/references/assets`，并生成 `agents/openai.yaml`。
- `quick_validate.py` 校验 frontmatter schema、name 规则、description 长度和 allowed keys。
- `generate_openai_yaml.py` 生成 UI metadata，包括 display name、short description、icons、brand color、default prompt 等产品消费字段。
- 主文档强调 progressive disclosure：metadata 常驻，`SKILL.md` 触发后读取，scripts/references/assets 按需读取。

## Beacon v1.6.0 Implications

Beacon v1.6.0 不应只做 skill 改名生成。它需要把 OpenAI 的结构化 skill package 校验和 Anthropic 的 eval harness 组合起来：

- 生成层：中心模板生成 `beacon-<harness-code>-<function>`、中文 description、共享 preamble、harness-specific `HARD GATE`、`agents/openai.yaml`。
- 静态校验层：校验 frontmatter、目录名、description、旧 alias 缺失、preamble 位置、HARD GATE 位置和 harness 匹配。
- 行为 eval 层：用粗粒度 prompt 验证 planner/generator/evaluator/governor 是否按边界路由，而不是顺手越权。
- 对照层：关键 eval 同时跑新 v1.6.0 skill 与旧/无 skill baseline，比较 pass_rate、时间、token 和错误模式。
- 评分层：evaluator 不只判 AC/TC，还要批判 assertion 是否能排除 fake delivery、placeholder evidence、docs-only completion 和 zero assertions。

## Eval Research Plan

最小可用 eval harness 应覆盖三类用例：

1. Trigger/routing eval：输入“帮我分析这个 feature”“帮我实现这个 feature”“验收这个 feature”“修一下 context”等粗 prompt，期望输出包含 outcome、湖/海、truth/source/evidence refs、gap/risk、recommended_route，且 planner 不写 truth/implementation。
2. Boundary negative eval：要求 planner 顺手改代码、generator 自证完成、evaluator 顺手修实现、governor 给 release verdict；期望 HARD GATE 阻断并路由。
3. Package static eval：扫描 `.generated/skills/beacon/` 和 `.agents/skills/`，验证 `beacon-<harness-code>-<function>`、无旧 alias、中文 description、共享 preamble、HARD GATE、no-fake-delivery 文案、OpenAI metadata。

建议输出 schema：

- `eval_metadata.json`：eval id、prompt、target harness、truth refs、assertions。
- `grading.json`：expectations `{text, passed, evidence}`、summary、claims、eval_feedback。
- `benchmark.json`：每个配置的 pass_rate/time/tokens 均值、标准差、delta。
- `research/<feature>.md`：planner support_advisory 结论，只在用户接受后通过 truth/change/refreeze 晋升。

## Truth Gap

当前 v1.6.0 truth 已定义 taxonomy、preamble、HARD GATE 和验收标准，但还缺少明确的 runtime eval artifact schema 和命令入口命名。建议新增或补充 implementation tasks，而不是直接修改 frozen truth。

## Test Gap

`tests.md` 已有 AC/TC 映射，但 TC-006 到 TC-011、TC-017 需要落地成可运行 harness eval，而不是只靠文档扫描。尤其要加入 Anthropic grader 风格的 assertion critique，防止弱断言通过。

## Implementation Risk

- 只做静态扫描会漏掉 LLM 运行时越权行为。
- 只做 LLM 自评会产生 fake pass。
- 保留旧 alias 会让 v1.6.0 breaking taxonomy 失效。
- 没有 baseline 时无法证明 skill 真的提升 routing/gate 质量。

## Verification Risk

LLM eval 存在波动，至少要支持 runs_per_query、trigger_threshold、holdout 或重复运行。静态 gate 扫描必须是 deterministic，作为 release 前硬门禁；行为 eval 可作为 evidence，但不能替代 deterministic package verification。

## Recommended Route

`routeable`：建议进入 `beacon-gen-implement` 做 v1.6.0 skill harness eval 最小闭环实现，然后由 `beacon-eval-qa` 验证 TC-003 到 TC-017。若要改变 truth schema 或新增 AC，需要先走 `beacon-gen-change`。

## Promotion

待用户确认。当前 artifact 仅为 `support_advisory`，不能作为 requirement truth、implementation closure、QA pass 或 release verdict。
