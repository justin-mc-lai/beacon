# Beacon Open-Source Reference Source Map

**Date**: 2026-04-15  
**Purpose**: 为 Beacon 研究与版本演进冻结一份“外部开源参考项目 -> `oss-sync` 本地源码目录”的 source map，避免后续只看到 GitHub 链接，却不知道本机应从哪个目录开始读源码。  
**Canonical mirror root**: `/Users/apple/Developer/Personal/oss-sync`  
**Canonical mirror indexes**:

- `/Users/apple/Developer/Personal/oss-sync/index/repos.json`
- `/Users/apple/Developer/Personal/oss-sync/index/repos.md`

**Verification note**: 本文内容基于 2026-04-15 重新生成的 `oss-sync` index，当前 `repo_count = 75`。

---

## 1. How to use this map

当 Beacon 文档引用外部开源项目时，按下面顺序处理：

1. 先查这份 source map。
2. 如果 `oss-sync status = canonical`，优先读本地镜像目录，不要先去猜旧的 `.research/` 路径。
3. 如果 `oss-sync status = missing`，说明当前本机没有 canonical mirror：
   - 先使用上游 GitHub 资料
   - 若该项目会持续进入 Beacon 版本演进，请先镜像到 `oss-sync`，再回填本文
4. 当版本线需要引用外部项目时，`SUMMARY.md` / `execution/index.md` 只负责引用研究结论；源码定位统一回到本文。

---

## 2. Verified canonical mirrors relevant to Beacon research

| Project | oss-sync status | oss-sync relative path | Upstream | Main Beacon docs |
| --- | --- | --- | --- | --- |
| `gstack` | `canonical` | `agents/agent-skills/gstack` | `https://github.com/garrytan/gstack.git` | `docs/beacon/research/beacon-codex-native-subagent-direction-gstack-superpowers.md`, `docs/beacon/v1.1.8/research/gstack-gap-analysis.md`, `docs/beacon/v1.1.6/research/gstack/README.md` |
| `superpowers` | `canonical` | `agents/agent-skills/superpowers` | `git@github.com:obra/superpowers.git` | `docs/beacon/research/beacon-codex-native-subagent-direction-gstack-superpowers.md` |
| `codex-turbo` | `canonical` | `agents/agent-skills/codex-turbo` | `https://github.com/atticus98/codex-turbo.git` | `docs/beacon/research/beacon-codex-native-subagent-direction-gstack-superpowers.md` |
| `awesome-codex-subagents` | `canonical` | `agents/agent-skills/awesome-codex-subagents` | `https://github.com/VoltAgent/awesome-codex-subagents.git` | `docs/beacon/research/beacon-codex-native-subagent-direction-gstack-superpowers.md` |
| `ralph` | `canonical` | `ralph/agent-skills/ralph` | `https://github.com/snarktank/ralph` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `ralph-orchestrator` | `canonical` | `ralph/agent-skills/ralph-orchestrator` | `https://github.com/mikeyobrien/ralph-orchestrator` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `ralphex` | `canonical` | `ralph/agent-skills/ralphex` | `https://github.com/umputun/ralphex` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `ralph-loop-agent` | `canonical` | `ralph/agent-skills/ralph-loop-agent` | `https://github.com/vercel-labs/ralph-loop-agent` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `ralph-claude-code` | `canonical` | `ralph/agent-skills/ralph-claude-code` | `https://github.com/frankbria/ralph-claude-code` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `ralphy` | `canonical` | `ralph/agent-skills/ralphy` | `https://github.com/michaelshimeles/ralphy` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `ralph-tui` | `canonical` | `ralph/agent-skills/ralph-tui` | `https://github.com/subsy/ralph-tui` | `docs/beacon/research/beacon-ralph-subagent-long-task-delivery-brainstorm.md` |
| `deer-flow` | `canonical` | `agents/agent-skills/deer-flow` | `git@github.com:bytedance/deer-flow.git` | `docs/beacon/v1.1.6/research/deer-flow/README.md`, `docs/beacon/v1.1.6/research/README.md` |
| `openspec` | `canonical` | `automation/autoresearch/openspec` | `https://github.com/Fission-AI/OpenSpec.git` | `docs/beacon/v1.1.6/research/openspec/README.md`, `docs/beacon/v1.1.6/research/README.md` |
| `gsd-2` | `canonical` | `automation/autoresearch/gsd-2` | `https://github.com/gsd-build/gsd-2.git` | `docs/beacon/v1.1.6/research/gsd-2/README.md`, `docs/beacon/v1.1.6/research/README.md` |
| `bmad-method` | `canonical` | `automation/autoresearch/bmad-method` | `https://github.com/bmad-code-org/BMAD-METHOD.git` | `docs/beacon/v1.1.6/research/bmad-method/README.md`, `docs/beacon/v1.1.6/research/README.md` |
| `karpathy-autoresearch` | `canonical` | `automation/autoresearch/karpathy-autoresearch` | `https://github.com/karpathy/autoresearch.git` | `docs/beacon/v1.1.6/research/autoresearch/README.md`, `docs/beacon/v1.1.6/research/README.md` |
| `memevolve` | `canonical` | `automation/autoresearch/memevolve` | `https://github.com/bingreeky/MemEvolve.git` | `docs/beacon/v1.1.6/research/memevolve/README.md`, `docs/beacon/v1.1.6/research/README.md` |
| `autoagent` | `canonical` | `automation/autoresearch/autoagent` | `https://github.com/HKUDS/AutoAgent.git` | `docs/beacon/research/beacon-self-iteration-and-story-qa-coverage-study-awesome-design-md-autoagent.md` |
| `statsclaw` | `canonical` | `automation/autoresearch/statsclaw` | `https://github.com/statsclaw/statsclaw.git` | `docs/beacon/v1.1.12/research/beacon-external-reference-study-statsclaw-awesome-design-md.md` |
| `awesome-design-md` | `canonical` | `core-skills/awesome-design-md` | `https://github.com/VoltAgent/awesome-design-md.git` | `docs/beacon/research/beacon-self-iteration-and-story-qa-coverage-study-awesome-design-md-autoagent.md`, `docs/beacon/v1.1.12/research/beacon-external-reference-study-statsclaw-awesome-design-md.md` |
| `mempalace` | `canonical` | `memory/memory-systems/mempalace` | `https://github.com/mempalace/mempalace.git` | `docs/beacon/research/beacon-memory-asset-eval-plane-study-mempalace.md` |

Absolute path rule:

```text
/Users/apple/Developer/Personal/oss-sync/<oss-sync relative path>
```

例如：

- `gstack` absolute path:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack`
- `superpowers` absolute path:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/superpowers`
- `ralph` absolute path:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralph`

---

## 3. Key source entrypoints for the main active references

### `gstack`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack`
- Start here:
  - `README.md`
  - `ARCHITECTURE.md`
  - `qa/SKILL.md`
  - `qa-only/SKILL.md`
  - `scripts/gen-skill-docs.ts`

### `superpowers`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/superpowers`
- Start here:
  - `README.md`
  - `docs/README.codex.md`
  - `skills/brainstorming/SKILL.md`
  - `skills/writing-plans/SKILL.md`
  - `skills/subagent-driven-development/SKILL.md`
  - `skills/using-git-worktrees/SKILL.md`

### `codex-turbo`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/codex-turbo`
- Start here:
  - `README.md`
  - `README.en.md`
  - `templates/cn/`
  - `templates/en/`
  - `docs/manual-merge.md`

### `awesome-codex-subagents`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/awesome-codex-subagents`
- Start here:
  - `README.md`
  - `CONTRIBUTING.md`
  - `categories/04-quality-security/`
  - `categories/09-meta-orchestration/`
  - `categories/10-research-analysis/`

### `ralph`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralph`
- Start here:
  - `README.md`
  - `ralph.sh`
  - `prompt.md`
  - `CLAUDE.md`
  - `skills/prd/`
  - `skills/ralph/`

### `ralph-orchestrator`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralph-orchestrator`
- Start here:
  - `README.md`
  - `docs/getting-started/`
  - `docs/concepts/`
  - `crates/ralph-cli/`
  - `crates/ralph-core/`
  - `.ralph/`

### `ralphex`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralphex`
- Start here:
  - `README.md`
  - `cmd/ralphex/`
  - `pkg/plan/`
  - `pkg/processor/`
  - `pkg/executor/`
  - `pkg/config/`

### `ralph-loop-agent`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralph-loop-agent`
- Start here:
  - `README.md`
  - `packages/ralph-loop-agent/`
  - `examples/cli/`

### `ralph-claude-code`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralph-claude-code`
- Start here:
  - `README.md`
  - `install.sh`
  - `lib/response_analyzer.sh`
  - `lib/circuit_breaker.sh`
  - `lib/enable_core.sh`
  - `docs/user-guide/`

### `ralphy`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralphy`
- Start here:
  - `README.md`
  - `ralphy.sh`
  - `cli/README.md`
  - `cli/src/`
  - `example-prd.md`
  - `example-prd.yaml`

### `ralph-tui`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/ralph/agent-skills/ralph-tui`
- Start here:
  - `README.md`
  - `src/cli.tsx`
  - `src/engine/`
  - `src/tui/`
  - `src/plugins/`
  - `skills/ralph-tui-prd/`
  - `docs/plans/`

### `deer-flow`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/deer-flow`
- Start here:
  - `README.md`
  - `backend/docs/ARCHITECTURE.md`
  - `backend/docs/HARNESS_APP_SPLIT.md`
  - `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  - `backend/packages/harness/deerflow/subagents/executor.py`

### `openspec`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/openspec`
- Start here:
  - `README.md`
  - `docs/commands.md`
  - `docs/supported-tools.md`
  - `src/core/init.ts`
  - `src/core/profiles.ts`

### `gsd-2`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/gsd-2`
- Start here:
  - `docs/architecture.md`
  - `docs/auto-mode.md`
  - `docs/commands.md`
  - `src/resources/extensions/gsd/custom-workflow-engine.ts`
  - `src/resources/extensions/gsd/run-manager.ts`
  - `src/worktree-cli.ts`

### `bmad-method`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/bmad-method`
- Start here:
  - `README.md`
  - `docs/index.md`
  - `docs/reference/agents.md`
  - `docs/reference/workflow-map.md`
  - `src/core-skills/`

### `karpathy-autoresearch`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/karpathy-autoresearch`
- Start here:
  - `README.md`
  - `program.md`
  - `prepare.py`
  - `train.py`

### `memevolve`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/memevolve`
- Start here:
  - `Flash-Searcher-main/EvolveLab/memory_types.py`
  - `Flash-Searcher-main/EvolveLab/config.py`
  - `Flash-Searcher-main/evolve_cli.py`
  - `Flash-Searcher-main/run_flash_searcher_mm_gaia.py`

### `autoagent`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/autoagent`
- Start here:
  - `README.md`
  - `docs/README.md`
  - `evaluation/README.md`
  - `autoagent/cli.py`
  - `autoagent/workflows/`

### `statsclaw`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/statsclaw`
- Start here:
  - `README.md`
  - `agents/`
  - `profiles/`
  - `skills/`
  - `templates/`

### `awesome-design-md`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md`
- Start here:
  - `README.md`
  - `CONTRIBUTING.md`
  - `.github/ISSUE_TEMPLATE/design-md-request.yml`
  - `design-md/`
  - `design-md/voltagent/`

### `mempalace`

- Root:
  `/Users/apple/Developer/Personal/oss-sync/memory/memory-systems/mempalace`
- Start here:
  - `README.md`
  - `benchmarks/README.md`
  - `mempalace/README.md`
  - `docs/schema.sql`
  - `.codex-plugin/README.md`

---

## 4. Current gap status

当前 Beacon 高优先级研究里显式点名的开源参考项目，已经全部有 `oss-sync` canonical mirrors。

补充说明：

1. Ralph 相关参考项目现在统一归到 `oss-sync/ralph/agent-skills/`
2. 若后续版本线继续细化 Ralph / loop / closure controller 研究，优先从这组 canonical mirrors 开始，而不是重新搜索零散学习副本

后续规则保持不变：

1. 新增外部参考前，先查 `oss-sync/index/repos.json`
2. 若无 canonical mirror，再决定是否导入
3. 不要在新版本研究里再写 `.research/...` 形式的伪本地路径

---

## 5. Maintenance rule

以后只要 Beacon 研究文档新增了外部开源参考，必须同步做下面两件事：

1. 在文档中写清楚：
   - 上游仓库
   - 本地 `oss-sync` 目录，或明确写 `missing`
2. 更新本文：
   - 新增该项目的 source map entry
   - 如果已有 mirror，写出关键入口文件
   - 如果没有 mirror，写出推荐 canonical path

这样后续版本演进阅读研究文档时，才能真正做到“从研究结论直接落到本地源码目录”。
