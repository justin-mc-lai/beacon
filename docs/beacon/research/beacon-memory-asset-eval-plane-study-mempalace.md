# Research: Beacon memory and knowledge-plane study from `mempalace`

**Date**: 2026-04-08  
**Intent**: extract the parts of `mempalace` that matter for Beacon's long-term memory, compiled knowledge, and self-iteration support.

**Beacon first principle reminder**:

> Beacon 的长期记忆设计不能脱离它的主链。  
> 主链仍然是 `PRD → user-story → QA`。  
> memory / knowledge plane 的职责，是帮助这条链更可追溯、更不漂移，而不是取代这条链。

**Source directories**:

- canonical source map:
  [`./beacon-open-source-reference-source-map.md`](./beacon-open-source-reference-source-map.md)
- `mempalace`:
  `/Users/apple/Developer/Personal/oss-sync/memory/memory-systems/mempalace`
- adjacent local memory-system mirrors now live under:
  `/Users/apple/Developer/Personal/oss-sync/memory/memory-systems/`

---

## 1. Executive summary

`mempalace` 对 Beacon 最有价值的启发，不在它的“记忆宫殿”命名，而在三个更底层的判断：

1. **不要先让 AI 决定什么值得记忆**
2. **优先保留原始上下文，再建立可导航结构**
3. **记忆系统的价值来自可找回、可定位、可组合，而不只是摘要**

对 Beacon 的翻译是：

> Beacon 不应该只积累“结论摘要”或“阶段状态”，还应该逐步形成一个带结构的 compiled knowledge plane，让 requirement materials、research、review、implementation evidence 在长期上可找回、可导航、可比较。

更准确地说，这个 compiled knowledge plane 最该服务的是：

```text
PRD
→ story
→ QA
→ review / gate / implementation evidence
```

---

## 2. What `mempalace` is

`mempalace` 把自己定义成：

- 本地运行
- 存全部对话原文
- 再通过结构和检索让其可找回

核心叙事非常鲜明：

- “store everything, then make it findable”
- 不是先做摘要，再丢掉原文
- 不是先让 AI 过滤“什么值得记住”

它的仓库同时暴露了三类信号：

1. **CLI**
   - `mempalace init`
   - `mempalace mine`
   - `mempalace search`
   - `mempalace status`
2. **MCP**
   - 直接给外部 agent 使用
3. **Benchmarks**
   - LongMemEval、Locomo、MemBench、ConvoMem

也就是说，它不是只讲概念，而是把：

- memory model
- command surface
- benchmark proof

三者同时放出来了。

---

## 3. The most important design choice

### 3.1 Raw verbatim first

`mempalace` 的关键判断是：

> memory 默认应保留 verbatim raw exchanges，而不是先做 extraction/summarization。

它甚至明确批评了其他系统常见的做法：

- 提取 `"user prefers Postgres"`
- 却丢掉“为什么偏好它”的完整上下文

### 3.2 Why this matters for Beacon

Beacon 当前很强的是：

- requirement materials
- machine state
- stage closure
- evidence contracts

但长期上仍有一个风险：

- 很多关键 reasoning 只留在对话里
- 最终只剩下摘要化的 docs
- 上下文为什么变成这样，过一段时间就找不回来了

`mempalace` 提醒 Beacon：

> “structured memory” 不应只等于“更好的摘要”；它也可以意味着“保留足够原始上下文，再在上面建立结构和索引”。

但 Beacon 这里要再加一层收束：

- Beacon 不需要保存“所有上下文”
- Beacon 最该保存的是与 `PRD/story/QA` 演化有关的关键 reasoning

---

## 4. Structure over flat retrieval

`mempalace` 的 memory palace 结构大致是：

- wings
- halls
- rooms
- closets
- drawers

不管这套命名是否最终适合 Beacon，它表达了一个很重要的设计点：

### 4.1 retrieval should be structured

系统不是把所有内容丢进一个大向量池里等搜，而是先给内容分层：

- 所属对象
- 所属主题
- 所属记忆类型
- 原文出处

### 4.2 Beacon translation

Beacon 不一定要用 `wings / rooms / closets` 这套词，但应该明确区分：

1. **project / version / feature**
2. **material type**
   - prd
   - user-story
   - qa/test-case
   - execution
   - release
   - research
3. **memory type**
   - decision
   - contradiction
   - failure
   - evidence
   - lesson
4. **raw source vs compiled layer**

这和 `LLM Wiki` 模式非常一致：

- raw sources
- compiled knowledge
- schema/governance

只是 `mempalace` 给了更强的“导航结构”信号。

而 Beacon 的导航顺序应继续围绕主链：

```text
PRD first
→ story
→ QA / evidence
→ supporting research / memory
```

---

## 5. The benchmark lesson

`mempalace` 最强的外部信号之一是：它不只讲架构，还讲 benchmark。

README 明确围绕：

- `LongMemEval`
- raw mode score
- AAAK mode tradeoff
- honest benchmark caveats

甚至专门写了一个 “What we got wrong / What's still true” 的纠错说明。

### 5.1 Why this matters for Beacon

Beacon 如果未来要做自迭代、自优化，必须走类似路径：

- 不只给 narrative
- 要给 benchmark
- 而且要把“什么模式下得分高”说清楚

### 5.2 Beacon-specific translation

对于 Beacon，自迭代 benchmark 最值得围绕：

1. PRD-to-story traceability
2. story coverage
3. AC coverage
4. scenario family coverage
5. evidence closure rate
6. false-complete rate

换句话说：

> `mempalace` 告诉 Beacon：一个长期知识/记忆层如果没有 benchmark，只会停在哲学；一旦要进入产品内核，就必须把效果变成可重复测量的东西。

---

## 6. Honest mode separation

`mempalace` README 有一个非常值得 Beacon 学的地方：

- 它明确区分 raw mode
- AAAK compression mode
- rooms/metadata filtering mode

并坦白说：

- headline score 来自 raw mode
- AAAK 目前会回归
- 某些 README claim 过去表达得不够准确

### 6.1 Beacon should copy the honesty, not the branding

Beacon 后续如果做：

- memory plane
- QA baseline packs
- eval plane
- self-iteration

也应该严格区分：

- 哪个模式是 production truth
- 哪个模式是 experimental
- 哪个 score 来自哪个 mode

不要把实验层的结果直接写成主产品 truth。

---

## 7. What Beacon should learn

## 7.1 Add a raw memory layer, not just summaries

Beacon 未来的长期记忆不应只保留：

- stage markers
- summarized feedback
- compacted lessons

还应考虑：

- 保留关键原始 reasoning sources
- 并建立检索/索引层来找回它们

尤其是：

- PRD tradeoff debate
- architecture tradeoffs
- story decomposition reasoning
- why a release was blocked
- why a review rejected something

这些是最不该被压扁成一句摘要的内容。

## 7.2 Add a structured knowledge plane

建议 Beacon 长期把 knowledge plane 分成：

- `project`
- `version`
- `feature`
- `material_type`
- `memory_type`

而不是把记忆全塞到一个平面 JSON 里。

## 7.3 Add benchmarked memory/eval separation

建议明确分成：

### production memory mode

- 面向可靠 recall
- 强调原始证据可找回

### experimental compression / rewrite mode

- 面向 token density 或更低 operator load
- 但必须接受 benchmark 检验

## 7.4 Keep “searchability” as the real value

`mempalace` 真正强调的不是“记得更多”，而是“找得到”。

对 Beacon 来说，长期也一样：

- 不是存更多 docs 就赢
- 而是关键问题能否在正确时刻找回正确材料和上下文

---

## 8. Concrete Beacon design suggestion

结合 `LLM Wiki`、`autoagent`、`awesome-design-md` 和 `mempalace`，Beacon 可形成如下结构：

### 8.1 Memory / Knowledge plane

保留：

- PRD-origin reasoning
- story decomposition reasoning
- QA/gate blockage reasoning
- raw reasoning artifacts
- compiled knowledge pages
- machine-readable indices

### 8.2 Asset plane

把高价值 bundle 固定化：

- story QA baseline packs
- design governance packs
- scorecards
- distilled lessons

### 8.3 Eval plane

只允许少数 policy surfaces 自迭代：

- PRD-to-story rewrite fidelity
- story scenario expansion
- coverage thresholds
- review severity mapping
- rewrite policy

### 8.4 Benchmark plane

明确用哪些 corpus / stories / ACs / scenarios 来评估：

- PRD-to-story traceability
- coverage gain
- false-complete reduction
- evidence closure gain

---

## 9. Final recommendation

`mempalace` 给 Beacon 的最终建议可以压缩成一句话：

> Beacon 的长期记忆不该只是“更聪明地摘要过去”，而应是“围绕 `PRD/story/QA` 主链保留关键原始上下文，建立结构化导航层，并通过 benchmark 证明这种记忆真的能提升 story-native QA 与长期演进能力”。

所以 Beacon 后续若继续推进：

1. 先定义 raw-vs-compiled memory boundary
2. 再定义 structured knowledge plane
3. 再定义 story/AC-driven benchmark
4. 最后才做自迭代和压缩层

不要反过来先做“会变的 memory magic”。
