# OpenAI Eval Skills 调研与 Beacon 接入方案

## Source

- Primary article:
  - OpenAI Developers, `Testing Agent Skills Systematically with Evals`, January 22, 2026
  - `https://developers.openai.com/blog/eval-skills`
- Supporting docs:
  - Codex skills docs: `https://developers.openai.com/codex/skills`
  - Codex CLI reference: `https://developers.openai.com/codex/cli/reference`

## Why This Matters For Beacon

Beacon `v1.3.6` 已经把公开人类主面收口到 `7+3`，并把宿主原生 LLM orchestration、delivery kernel、release gate 做成当前 runtime truth。

当前仍缺一块系统能力：

- 我们会验证 `beacon` 自己的 docs/gate/release contract。
- 但我们还没有稳定验证 `skills/beacon/` 这层“是否被正确触发、是否按预期执行、是否误触发”。

OpenAI 这篇文章正好补的是这块空白：把 skill 从“感觉可用”变成“可回放、可评分、可回归”的对象。

## Official Findings Distilled

以下是基于 OpenAI 官方原文的直接提炼。

### 1. 先定义 success，再写 skill

官方建议先把 skill success 写成可测量目标，而不是先写说明后靠体感判断。

建议至少拆成四类：

- Outcome goals: 任务是否完成，产物是否可运行
- Process goals: agent 是否真的调用了 skill、是否走了预期步骤
- Style goals: 结果是否符合约束和约定
- Efficiency goals: 是否发生 thrashing、无意义重试、token 膨胀

### 2. `SKILL.md` 的 `name` 和 `description` 是触发质量核心

官方 skills docs 明确写了，Codex 先看 metadata，再决定是否加载完整 `SKILL.md`。

这意味着 skill eval 不能只测“skill 执行后对不对”，还要测：

- 该触发时是否触发
- 不该触发时是否误触发

### 3. 先手动显式触发，暴露 hidden assumptions

官方建议先用显式 skill 调用做人工试跑，暴露：

- trigger 假设
- 环境假设
- 执行顺序假设

Beacon 侧可直接转化为：

- `$beacon` 或具体 host-visible skill 显式调用先过一轮
- 每次手工发现的新失败案例，都要沉淀进 prompt set

### 4. Prompt set 要小而准

官方建议一个 skill 先从 `10-20` 条 prompt 开始，并至少覆盖：

- explicit invocation
- implicit invocation
- contextual invocation
- negative control

这对 Beacon 很关键，因为 Beacon 的 skill surface 不是只有 `$beacon`，还包括：

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

### 5. 先做 deterministic graders，再做 rubric grading

官方文章给出的顺序很清楚：

1. 用 `codex exec --json` 捕获 JSONL trace
2. 先做 deterministic checks
3. 再对 style / convention / quality 做 rubric-based grading

官方 CLI docs同时确认了：

- `--json` 会输出 newline-delimited JSON events
- `--output-schema` 可以强制最终输出匹配给定 JSON Schema

### 6. 扩展方向应聚焦风险，不应一开始做成大而全

官方建议扩展 checks 时优先加这些高价值项：

- command count / thrashing
- token budget
- build checks
- runtime smoke checks
- repository cleanliness
- sandbox / permission regressions

这和 Beacon `v1.3.6` 的 minimal surface、release-gate consistency 完全兼容。

## Beacon-Specific Inference

下面这些不是 OpenAI 原文直接说的，而是基于 Beacon 当前架构做的接入推导。

### Inference 1

Beacon 不应该新增新的一级人类主命令来承载 skill eval。

理由：

- `v1.3.6` 已经把公开表面收口为 `7+3`
- skill eval 更像质量基础设施，而不是新的用户工作流入口

所以 skill eval 应落在：

- repo-local research + eval harness
- `qa` / `doctor` / `gate` 的兼容平面

而不是新增第 11 个公开主命令。

### Inference 2

Beacon skill eval 需要同时测三层，而不是只测 skill 触发。

三层分别是：

1. Trigger layer
   - 该 skill 是否被选中
2. Execution layer
   - 是否跑了预期 Beacon surface 或 artifact writeback
3. Contract layer
   - 输出是否满足 Beacon 的 version/evidence/gate 约束

### Inference 3

Beacon 的 deterministic graders 不应过度依赖“trace 里一定有 skill selected 事件”。

更稳妥的做法是双通道判断：

- Primary: 解析 trace 中的 structured events
- Fallback: 校验结果 artifact 是否符合指定 surface contract

这样即使宿主 trace 事件格式后续有变，Beacon 侧仍有稳定回归信号。

## Recommended Integration For Beacon v1.3.6

## 1. Keep It In The Compatibility Plane

接入位置建议保持在兼容平面，而不是扩张人类主面。

建议结构：

- Research:
  - `docs/beacon/v1.3.6/research/openai-eval-skills-beacon-integration.md`
- Eval prompts:
  - `evals/skills/beacon/prompts.csv`
- Deterministic checks:
  - `evals/skills/beacon/checks/`
- Rubric schemas:
  - `evals/skills/beacon/schema/`
- Runners:
  - `scripts/skill_evals/run_beacon_skill_evals.py`
  - 或 `evals/skills/beacon/run_beacon_skill_evals.mjs`
- Evidence sink:
  - `.beacon/evidence/skill-evals/<run_id>/`
- Status sink:
  - `.beacon/skill-evals/status.json`

## 2. Start With One Release-Critical Skill Group

第一阶段不要评估所有 skill。

先评估当前 release-critical 组：

- `beacon`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-doctor`

原因：

- 这组最接近 release closure
- 最容易把结果接进现有 gate
- 最能验证“minimal surface 是否真的稳定”

`beacon-prd` / `beacon-user-story` / `beacon-test-case` 可以作为第二阶段扩展。

## 3. Prompt Matrix Design

每个 skill 至少 4 类 prompt：

- Explicit:
  - 明确写 `$beacon` / `$beacon-qa`
- Implicit:
  - 只写场景，不提 skill 名
- Contextual:
  - 带 Beacon 版本、feature、release 场景噪音
- Negative:
  - 相邻但不该触发 Beacon skill 的请求

初始矩阵建议 12 条左右：

### `beacon`

- positive / explicit:
  - `Use $beacon to help me close Beacon v1.3.6 release readiness`
- positive / implicit:
  - `I need to route a feature through PRD, QA, and release evidence in Beacon`
- negative:
  - `Brainstorm three new product ideas for me`

### `beacon-qa`

- positive / explicit:
  - `Use $beacon-qa to verify whether this Beacon feature is release ready`
- positive / implicit:
  - `Inspect coverage, test evidence, and missing acceptance closure for this Beacon feature`
- negative:
  - `Implement the feature code changes now`

### `beacon-release`

- positive / explicit:
  - `Use $beacon-release to decide whether v1.3.6 can ship`
- contextual:
  - `We already have QA evidence, now judge release blockers for Beacon v1.3.6`
- negative:
  - `Generate wireframes for the next Beacon prototype`

## 4. Deterministic Checks Beacon Should Add

第一轮 deterministic checks 只保留最强信号。

建议 8 个：

- `skill_triggered_expected`
  - 正例时至少出现一次目标 skill 触发证据
- `skill_not_triggered_on_negative`
  - 负例时不应出现目标 skill 触发证据
- `surface_command_alignment`
  - 输出应落在 Beacon 允许 surface，而不是扩张新的主命令
- `artifact_writeback_expected`
  - 如果是 write flow，必须产出目标 docs 或 `.beacon` evidence
- `version_alignment`
  - 产物版本必须对齐 `v1.3.6`
- `no_scope_escape`
  - 不得写入无关目录
- `no_thrashing`
  - command count / retry count 不超过阈值
- `gate_safe`
  - 不得制造新的 evidence hash drift / coverage regression

### Trigger Evidence Strategy

优先顺序建议：

1. 直接读 trace 中的 skill selection / context injection 事件
2. 如果宿主事件不可用，则回退到 outcome heuristic：
   - 是否调用 `bash skills/beacon/scripts/run_beacon.sh`
   - 或是否生成了目标 Beacon artifact
   - 或最终输出是否遵守目标 skill 的 narrow contract

## 5. Rubric Grading Schema

第二层用 `--output-schema` 做 rubric grading。

建议 schema：

```json
{
  "type": "object",
  "properties": {
    "overall_pass": { "type": "boolean" },
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "pass": { "type": "boolean" },
          "notes": { "type": "string" }
        },
        "required": ["id", "pass", "notes"],
        "additionalProperties": false
      }
    }
  },
  "required": ["overall_pass", "score", "checks"],
  "additionalProperties": false
}
```

Beacon rubric check ids 建议：

- `routing`
- `surface-minimality`
- `version-truth`
- `artifact-discipline`
- `gate-awareness`
- `repair-guidance`

## 6. Runner Shape

推荐先做一个 repo-local runner，不直接绑进 CLI 主流程。

推荐流程：

1. 读取 `prompts.csv`
2. 对每条 prompt 执行：
   - `codex exec --json --full-auto "<prompt>"`
3. 保存 JSONL trace
4. 执行 deterministic checks
5. 对结果目录执行只读 rubric grading：
   - `codex exec --output-schema <schema> -o <rubric.json>`
6. 汇总出一份 Beacon skill eval summary
7. 写入 `.beacon/evidence/skill-evals/<run_id>/summary.json`
8. 更新 `.beacon/skill-evals/status.json`

## 7. Gate Integration Path

不要一步到位把 skill eval 变成硬阻塞。

建议三阶段：

### Phase 1: Research + Local Harness

- 产出 prompts / schema / runner
- 只生成 evidence
- 不进 gate

### Phase 2: QA Advisory

- `beacon qa` 或 `beacon doctor` 可读取 `.beacon/skill-evals/status.json`
- 只作为 warning surfaced

建议 reason code：

- `skill_eval_missing`
- `skill_eval_regression`
- `skill_eval_false_positive_risk`

### Phase 3: Release Gate For Current-Line Skills

仅对当前 release-critical skill group 开 strict gate。

建议 gating 条件：

- explicit 正例通过率 `100%`
- implicit/contextual 正例通过率 `>= 90%`
- negative false positive rate `<= 5%`
- deterministic critical checks 全通过
- rubric 均分 `>= 85`

## 8. Mapping To Beacon v1.3.6 Architecture

这套方案与 `v1.3.6` 当前架构的对齐点如下：

- 与 minimal surface 一致
  - skill eval 不扩张新的公开一级命令
- 与 host-native runtime 一致
  - runner 直接复用宿主 `codex exec`
- 与 delivery kernel 一致
  - 产物进入 `.beacon` evidence plane
- 与 release-gate consistency 一致
  - 后续可纳入现有 evidence / coverage / gate reason code 系统

## 9. Concrete Next Step For Beacon

如果按最小可落地路径推进，建议顺序：

1. 建立 `docs/beacon/v1.3.6/research/` 调研结论
2. 新建 `evals/skills/beacon/prompts.csv`
3. 新建 `evals/skills/beacon/schema/style-rubric.schema.json`
4. 实现 `scripts/skill_evals/run_beacon_skill_evals.py`
5. 先只覆盖：
   - `beacon`
   - `beacon-qa`
   - `beacon-release`
6. 让 runner 写入：
   - `.beacon/evidence/skill-evals/<run_id>/`
   - `.beacon/skill-evals/status.json`
7. 把 skill eval 结果作为 `doctor` / `qa` advisory surfaced
8. 稳定后再接入 `release` strict gate

## Bottom Line

OpenAI 这篇文章给 Beacon 的核心启发不是“再做一套大 eval 平台”，而是：

- 先把 skill 触发和执行变成可回放证据
- 先用小 prompt set 抓 regression
- 先用 deterministic checks 拿 explainable signals
- 再用 rubric grading 补足质量判断

对 Beacon `v1.3.6` 来说，最合适的接入方式不是新增主命令，而是把 skill eval 作为当前 compatibility plane 的质量基础设施，逐步接进 `.beacon` evidence、`qa` advisory 和 `release` gate。
