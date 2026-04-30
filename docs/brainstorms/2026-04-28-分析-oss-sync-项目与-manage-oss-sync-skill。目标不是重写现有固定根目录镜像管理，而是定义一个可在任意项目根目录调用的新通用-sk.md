# Beacon Brainstorm

## prompt_summary
分析 oss-sync 项目与 manage-oss-sync skill。目标不是重写现有固定根目录镜像管理，而是定义一个可在任意项目根目录调用的新通用 skill 能力：1) 接收 GitHub 开源仓库 URL；2) 自动下载到当前项目内约定目录；3) 自动分类归档；4) 生成索引；5) 对仓库做初步分析、提取 README/结构/技术栈/入口文件；6) 生成学习材料或中文 usage 文档；7) 尽量复用 manage-oss-sync 的现有索引/去重/同步思路，但去掉对 /Users/apple/Developer/Personal/oss-sync 的硬编码依赖。请输出 requirement convergence，说明当前项目现状、缺口、建议能力边界、最小可行架构、哪些应保留为 oss-sync 专用、哪些应抽象为通用 skill。

- version: `v1.3.8`
- mode: `requirement-convergence`
- feature: ``

## version_material_refs
- `docs/beacon/global-boundaries.md` (present, required)
- `docs/beacon/v1.3.8/SUMMARY.md` (present, optional)
- `docs/beacon/v1.3.8/execution/index.md` (present, optional)
- `docs/beacon/v1.3.8/execution/architecture-blueprint.md` (present, optional)
- `docs/beacon/v1.3.8/prd/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md` (present, optional)
- `docs/beacon/v1.3.8/prd/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace.md` (present, optional)
- `docs/beacon/v1.3.8/prd/beacon-v1.3.8-prd-executable-diagram-truth-layer.md` (present, optional)
- `docs/beacon/v1.3.8/prd/beacon-v1.3.8-truth-lifecycle-governance.md` (present, optional)
- `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md` (present, optional)
- `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace.md` (present, optional)
- `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-prd-executable-diagram-truth-layer.md` (present, optional)
- `docs/beacon/v1.3.8/user-story/beacon-v1.3.8-truth-lifecycle-governance.md` (present, optional)
- `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-archive-governance-and-historical-requirement-isolation.md` (present, optional)
- `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace.md` (present, optional)
- `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-prd-executable-diagram-truth-layer.md` (present, optional)
- `docs/beacon/v1.3.8/qa/test-cases/beacon-v1.3.8-truth-lifecycle-governance.md` (present, optional)
- `docs/beacon/v1.3.8/qa/test-cases/index.md` (present, optional)

## confirmed_facts
- Beacon version material root is docs/beacon/v1.3.8.
- This sidecar is read-only against Beacon requirement truth.
- Frozen PRD, user-story, test-case, prototype, and .machine artifacts are not rewritten by brainstorm.

## assumptions_under_test
- The prompt may represent a requirement gap, an evolution idea, or implementation-risk question until mapped to frozen evidence.
- Any accepted requirement change must be routed through the Beacon requirement/change loop before implementation.

## first_principles_breakdown
- 用户价值: identify the irreducible user outcome before proposing mechanism.
- 证据约束: every implementation idea must trace back to frozen PRD/user-story/test-case evidence.
- 闭环约束: if evidence is missing or changing, return to requirement/change routing instead of implementing.

## socratic_questions
- What exact user outcome would fail if this idea is not implemented?
- Which frozen acceptance criterion proves this idea is required?
- What evidence would falsify this proposed direction?
- If this is an evolution, what is the smallest safe requirement delta?

## redundancy_cuts
- Remove implementation mechanisms that cannot be tied to frozen acceptance evidence.
- Remove duplicate document-to-document reconciliation; use canonical Beacon truth or route a change.
- Remove broad roadmap speculation unless it produces a concrete next Beacon route.

## material_signals
- → implement
- - 它位于 `test-case` 与 `implement` 之间
- ### 4. `implement` 与 `qa` 仍是唯一执行入口
- - `implement` 仍是唯一实现入口
- - verifier / repair-handoff-writer / implementation-architect 等内部角色协作
- ### 6. 预检查必须内嵌到 `implement` / `qa`
- - `implement`
- - `implement / qa / release` 只能沿这条链闭环，不得反向改写 requirement truth

## converged_recommendation
Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.

## next_route
beacon-prd, beacon-user-story, beacon-test-case, or beacon-change
