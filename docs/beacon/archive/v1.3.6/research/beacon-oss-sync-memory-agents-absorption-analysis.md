# OSS-Sync Memory Agents Lighthouse Map

## 1. Summary

这次分析的结论很明确：

- `MemPalace` 最值得 Beacon 吸收的是 `verbatim-first + structured navigation + layered recall`。
- `gBrain` 最值得 Beacon 吸收的是 `knowledge plane + hybrid retrieval + deterministic background work`。
- `Evolver` 最值得 Beacon 吸收的是 `signal suppression + empty-cycle detection + evolution control plane`。
- `Hermes Agent` 更像 host agent，不是 Beacon 当前最需要吸收的 memory kernel。

Beacon 现在已经有 memory/debug/workflow-memory 闭环，但它更像：

- `workflow memory`
- `debug candidate memory`
- `release evidence memory`

它还不是：

- `raw-evidence memory`
- `navigable knowledge plane`
- `graph-backed recall system`

所以 Beacon 不该“重做一个 mempalace/gbrain”，而应该在现有 `.beacon/memory + .beacon/debug + workflow_memory` 上，补出一层更强的 evidence/knowledge projection。

## 2. Scope

本次分析基于：

- `oss-sync/CLAUDE.md`
- `memory-agents/mempalace`
- `memory-agents/gbrain`
- `memory-agents/evolver`
- `memory-agents/hermes-agent`
- Beacon 当前实现：
  - `beacon/utils/memory.py`
  - `beacon/utils/workflow_memory.py`
  - `beacon/utils/memory_friction_evolution.py`
  - `.beacon/memory/*`
  - `.beacon/debug/*`

## 3. Mermaid Maps

```mermaid
flowchart LR
  A[Beacon Current]
  A --> A1[typed memory items]
  A --> A2[workflow lifecycle events]
  A --> A3[debug issues -> friction candidates]

  B[MemPalace]
  B --> B1[verbatim drawers]
  B --> B2[closet pointer index]
  B --> B3[layered wake-up]
  B --> B4[temporal KG]

  C[gBrain]
  C --> C1[brain pages]
  C --> C2[hybrid search + backlinks]
  C --> C3[auto-link + timeline]
  C --> C4[minions queue]

  D[Evolver]
  D --> D1[signal extraction]
  D --> D2[repair-loop suppression]
  D --> D3[empty-cycle detection]

  A -. should absorb .-> B1
  A -. should absorb .-> B2
  A -. should absorb .-> B3
  A -. should absorb selectively .-> C2
  A -. should absorb selectively .-> C3
  A -. should absorb selectively .-> D1
  A -. should absorb selectively .-> D2
  A -. should absorb selectively .-> D3
```

```mermaid
flowchart TD
  U[Beacon main chain]
  U --> S1[PRD]
  U --> S2[user-story]
  U --> S3[test-case]
  U --> S4[implement]
  U --> S5[qa/release]

  E[New evidence layer]
  E --> E1[raw evidence excerpts]
  E --> E2[artifact links]
  E --> E3[stage context packs]
  E --> E4[friction signals]

  K[Knowledge projection]
  K --> K1[feature/artifact graph]
  K --> K2[hybrid recall]
  K --> K3[debug recurrence analysis]

  S1 --> E
  S2 --> E
  S3 --> E
  S4 --> E
  S5 --> E
  E --> K
  K --> U
```

## 4. Key Entry Points

### 4.1 Beacon current memory surface

- `beacon/utils/memory.py`
  - typed memory storage: `insight / decision / vocabulary / feedback`
  - single-file canonical store: `memory-v1.json`
  - legacy projection compatibility
- `beacon/utils/workflow_memory.py`
  - workflow event memory for `think -> user-story -> prd -> ... -> gate`
  - run/stage/attempt/evidence traceability
- `beacon/utils/memory_friction_evolution.py`
  - collects memory/debug evidence
  - ranks top candidates
  - optional writeback into feedback memory

### 4.2 Memory-agent projects

- `memory-agents/mempalace`
  - strongest raw-memory architecture
- `memory-agents/gbrain`
  - strongest knowledge-plane architecture
- `memory-agents/evolver`
  - strongest evolution-control architecture
- `memory-agents/hermes-agent`
  - strongest host-agent packaging, but not strongest memory kernel

## 5. Key Modules / Subsystems

### 5.1 MemPalace

#### Confirmed facts

- MemPalace explicitly defines itself as `verbatim always / incremental only / entity-first / local-first / background everything` in [`oss-sync/memory-agents/mempalace/CLAUDE.md`](../../../../../oss-sync/memory-agents/mempalace/CLAUDE.md).
- It separates `drawers` and `closets`; closets are a pointer/index layer, not the truth layer. See [`oss-sync/memory-agents/mempalace/mempalace/palace.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/palace.py).
- Search keeps direct drawer search as the floor and uses closet hits only as a ranking signal, never as a gate. See [`oss-sync/memory-agents/mempalace/mempalace/searcher.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/searcher.py).
- It has a local temporal knowledge graph backed by SQLite with `valid_from / valid_to` and provenance fields. See [`oss-sync/memory-agents/mempalace/mempalace/knowledge_graph.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/knowledge_graph.py).
- It has layered recall: L0 identity, L1 essential story, L2 filtered retrieval, L3 deep search. See [`oss-sync/memory-agents/mempalace/mempalace/layers.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/layers.py).

#### Why it matters

MemPalace solves a problem Beacon still only partially solves:

- Beacon stores memory summaries.
- MemPalace stores raw memory, then projects structure on top.

For Beacon, the important lesson is not “copy wings/rooms/drawers naming”, but:

- keep raw decisive evidence
- add deterministic addressing
- load context in layers instead of dumping everything or only keeping summaries

### 5.2 gBrain

#### Confirmed facts

- gBrain is contract-first: CLI and MCP share the same operation definitions. See [`oss-sync/memory-agents/gbrain/CLAUDE.md`](../../../../../oss-sync/memory-agents/gbrain/CLAUDE.md) and [`oss-sync/memory-agents/gbrain/src/core/operations.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/operations.ts).
- It has a hard trust boundary between local and remote callers using `OperationContext.remote`; remote callers default to stricter behavior. See [`oss-sync/memory-agents/gbrain/src/core/operations.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/operations.ts).
- It supports pluggable engines with both embedded `PGLite` and external `Postgres + pgvector`. See [`oss-sync/memory-agents/gbrain/src/core/engine.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/engine.ts).
- It has a serious hybrid retrieval stack: keyword + vector + RRF + cosine rescoring + backlink boost + dedup. See [`oss-sync/memory-agents/gbrain/src/core/search/hybrid.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/search/hybrid.ts).
- It turns brain pages into a graph and timeline system through auto-link and auto-timeline extraction. See [`oss-sync/memory-agents/gbrain/src/core/operations.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/operations.ts).
- It includes `Minions`, a Postgres-native durable job queue for deterministic background work. See [`oss-sync/memory-agents/gbrain/src/core/minions/queue.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/minions/queue.ts).

#### Why it matters

gBrain is not “a memory feature”. It is a full knowledge operating system.

For Beacon, the most useful parts are:

- graph/timeline projection from artifacts
- retrieval ranking discipline
- deterministic background execution for maintenance jobs

The least useful parts for Beacon right now are:

- person/company enrichment
- full brain repo architecture
- Postgres-first infra expansion

### 5.3 Evolver

#### Confirmed facts

- Evolver positions itself as a GEP-based self-evolution engine that scans `memory/` for signals and emits auditable evolution prompts. See [`oss-sync/memory-agents/evolver/README.md`](../../../../../oss-sync/memory-agents/evolver/README.md).
- Its signal layer explicitly tracks recurring errors, stagnation, empty cycles, repair loops, and opportunity classes. See [`oss-sync/memory-agents/evolver/src/gep/signals.js`](../../../../../oss-sync/memory-agents/evolver/src/gep/signals.js).

#### Why it matters

Beacon already has debug feedback and memory-friction-evolution, but its control logic is still simple:

- memory candidates = confidence/reason-codes projection
- friction candidates = debug issue count/sample projection
- convergence = trim low-score tail

Evolver suggests a more mature control plane:

- suppress over-processed signals
- detect repeated empty cycles
- measure recent failure ratio
- distinguish repair mode from innovation mode

Beacon should absorb this logic into its debug/release governance, not into its main memory storage.

### 5.4 Hermes Agent

#### Confirmed facts

- Hermes is a self-improving host agent with cross-session search, skill creation, periodic nudges, and pluggable memory integrations. See [`oss-sync/memory-agents/hermes-agent/README.md`](../../../../../oss-sync/memory-agents/hermes-agent/README.md).

#### Why it matters

Hermes proves that memory can stay behind the agent surface and still feel native, but its value to Beacon is mostly packaging and UX, not memory architecture. Beacon today needs stronger memory primitives first, not a multi-platform host runtime.

## 6. Beacon Current Baseline

### 6.1 Confirmed facts

- Beacon canonical memory is a typed append/upsert envelope in `.beacon/memory/memory-v1.json`, with legacy projections still maintained. See [`beacon/utils/memory.py`](../../../../beacon/utils/memory.py).
- Beacon recall is not true semantic retrieval yet. Its `semantic` mode is only term-overlap ratio over `content/source/tags`, and `hybrid` is direct-match-or-overlap. See [`beacon/utils/memory.py`](../../../../beacon/utils/memory.py).
- Beacon workflow memory is strong: it tracks `run_id / stage / event / attempt_seq / supersedes_event_id / evidence_ref`. See [`beacon/utils/workflow_memory.py`](../../../../beacon/utils/workflow_memory.py).
- Beacon memory-friction-evolution is a thin orchestration layer over existing memory/debug inputs, and its writeback compresses candidates into one-line feedback strings with recommendation and command. See [`beacon/utils/memory_friction_evolution.py`](../../../../beacon/utils/memory_friction_evolution.py) and [`.beacon/memory/feedback.json`](../../../../.beacon/memory/feedback.json).

### 6.2 Inferred structure

Beacon currently optimizes for:

- lifecycle traceability
- evidence closure
- release/debug governance

not for:

- raw conversational recall
- graph traversal across artifacts
- compiled knowledge reuse across many versions

That is the right product boundary. The gap is not “memory exists or not”; the gap is “memory is still mostly flattened into summary items”.

## 7. Memory Implementation Approaches

### 7.1 MemPalace implementation pattern

MemPalace is the clearest `verbatim-first` memory implementation in this set.

Its core design is:

- `drawers` store the original chunked memory as the truth layer
- `closets` store compact topic/entity pointer lines as the searchable index layer
- direct drawer search is always the floor
- closet hits only act as a ranking signal, never as a gate

That means its retrieval discipline is:

- preserve raw recall first
- project navigation structure second
- never let indexing heuristics hide the original memory

It then adds two higher-order structures:

- a local temporal knowledge graph in SQLite with `valid_from / valid_to` and provenance
- a 4-layer wake-up stack (`L0/L1/L2/L3`) that controls how much context gets loaded

Implementation-wise, this is the strongest example of:

- raw evidence retention
- deterministic addressing
- layered recall with bounded context cost

### 7.2 gBrain implementation pattern

gBrain implements memory as a full knowledge operating system rather than a lightweight memory add-on.

Its core design is:

- one `BrainEngine` abstraction for pages, chunks, links, timeline, versions, raw data, stats, and migrations
- one contract-first operation layer shared by CLI, MCP, and other callers
- one graph/timeline projection system built from page writes and link extraction

Its retrieval discipline is much heavier than Beacon's current recall:

- keyword search
- vector search
- RRF fusion
- compiled-truth boost
- cosine re-score
- backlink boost
- dedup

It also includes durable background work via `Minions`, which is a transactional job queue with:

- idempotency keys
- parent/child jobs
- retries
- delayed runs
- terminal-state cleanup

Implementation-wise, gBrain is the strongest example of:

- hybrid retrieval engineering
- graph-backed knowledge projection
- durable background maintenance jobs

### 7.3 Evolver implementation pattern

Evolver is not primarily a memory store. It is an evolution-control system over memory and runtime history.

Its core design is:

- scan recent memory/history/event streams
- extract signals from logs and outcomes
- suppress over-processed signals
- detect repair loops, empty cycles, and failure streaks
- emit the next structured evolution prompt

This makes it much closer to:

- memory governance
- friction governance
- evolution control

than to:

- raw memory storage
- graph retrieval

Implementation-wise, Evolver is the strongest example of:

- recurrence detection
- saturation detection
- repair-loop suppression
- failure-ratio-aware control

### 7.4 Hermes implementation pattern

Hermes is best understood as a host-agent runtime with a closed learning loop, not as a memory kernel-first project.

From the public README, the visible design emphasis is:

- agent-curated memory
- periodic nudges
- autonomous skill creation
- cross-session search
- user modeling
- scheduler + subagents + messaging surfaces

Architecturally, the useful inference is:

- memory sits behind the host agent experience
- recall quality is part of the product feeling
- memory, skills, and user model are integrated into one runtime surface

But compared with MemPalace and gBrain, Hermes exposes less of a clean, separable memory-core architecture in the repository entry docs. This section is therefore partly an inference from the README surface, not only from low-level source inspection.

### 7.5 Beacon current implementation pattern

Beacon currently implements memory as a workflow-native JSON memory surface.

Its core design is:

- canonical typed memory in `memory-v1.json`
- legacy projections preserved for compatibility
- workflow lifecycle events in `workflow-lifecycle.json`
- stage/run/attempt/evidence traceability
- memory/friction candidate convergence via `memory-friction-evolution`

Its recall path is still shallow compared with MemPalace and gBrain:

- `keyword`: direct substring match
- `semantic`: term-overlap ratio
- `hybrid`: direct-match-or-overlap

So Beacon today is strongest at:

- lifecycle traceability
- release/debug evidence closure
- workflow-stage memory

and weakest at:

- raw evidence retention
- graph-backed recall
- ranking discipline across many artifacts

## 8. Implementation Comparison

### 8.1 By storage model

| Project | Truth layer | Index / projection layer | Notes |
|---|---|---|---|
| MemPalace | verbatim drawers | closets + temporal KG | best raw-memory split |
| gBrain | pages/chunks/raw data | links + timeline + graph + search indexes | full knowledge OS |
| Evolver | event/history inputs | signals + evolution events | governance, not main storage |
| Hermes | host runtime memory surface | search + skills + user model | integrated runtime product |
| Beacon current | typed JSON memory + lifecycle | flat summaries + evidence refs | workflow-native but shallow |

### 8.2 By retrieval model

| Project | Retrieval path | Strength | Main limitation |
|---|---|---|---|
| MemPalace | drawer search + closet boost + layered loading | preserves verbatim recall | less complete knowledge plane |
| gBrain | keyword + vector + RRF + cosine + backlinks + dedup | strongest ranking stack | system complexity is high |
| Evolver | signal extraction over history | strongest governance signal loop | not for content recall |
| Hermes | cross-session search + summarization | strong user-facing continuity | memory core less explicit |
| Beacon current | substring + overlap ratio | simple and local | not true semantic/hybrid retrieval |

### 8.3 By operational model

| Project | Background work | Determinism | Fit for Beacon |
|---|---|---|---|
| MemPalace | background filing/hooks | medium | high for evidence capture |
| gBrain | Minions queue | high | high for projection maintenance |
| Evolver | evolution loop | high | high for friction governance |
| Hermes | scheduler + subagents | medium-high | medium for UX ideas |
| Beacon current | workflow/debug toolkits | high | base layer already exists |

### 8.4 Architectural conclusion

There is no single open-source project here that Beacon should copy wholesale.

The correct split is:

- learn `memory truth + layered recall` mostly from MemPalace
- learn `knowledge projection + retrieval ranking` mostly from gBrain
- learn `governance heuristics` mostly from Evolver
- learn `host experience packaging` only selectively from Hermes

## 9. Dependencies / Infra Chain

| Project | Core storage | Retrieval | Graph | Background execution | Fit for Beacon |
|---|---|---|---|---|---|
| MemPalace | ChromaDB + SQLite | drawer + closet hybrid | local temporal KG | hooks/background filing | High |
| gBrain | PGLite or Postgres | keyword + vector + RRF + backlink | links + timeline + graph traversal | Minions queue | High but selective |
| Evolver | local memory/history dirs | signal extraction | evolution graph/event view | evolution loop | Medium-High |
| Hermes | agent runtime + pluggable memory | cross-session search | user modeling / skills | scheduler + subagents | Medium |
| Beacon current | JSON files under `.beacon` | simple text overlap search | stage-event graph only | workflow/debug toolkits | Base |

## 10. Confirmed Facts

### Beacon should absorb now

1. `MemPalace`-style raw evidence retention
2. `MemPalace`-style layered recall
3. `gBrain`-style artifact graph projection
4. `Evolver`-style friction suppression and empty-cycle detection

### Beacon should not absorb wholesale

1. full `gBrain` brain OS
2. full `MemPalace` naming and MCP surface
3. `Hermes` host-agent runtime
4. `gBrain` person/company enrichment and social graph

## 11. Inferred Structure

### Best absorption split

- `memory plane`: learn mostly from `MemPalace`
- `knowledge plane`: learn mostly from `gBrain`
- `evolution control plane`: learn mostly from `Evolver`
- `host runtime / UX`: optionally learn from `Hermes`

### Beacon-compatible target

Beacon should become:

- `workflow-native knowledge system`

not:

- `general personal brain`

That means every absorbed feature must strengthen:

- PRD traceability
- story/test coverage
- implementation/release evidence closure
- debug recurrence learning

## 12. Recommended Next Steps

### P0: absorb immediately

1. Add a raw evidence layer under `.beacon/memory/evidence/`
   - store decisive excerpts from research, review, debug, QA, implementation summary
   - every entry must keep `source_path`, `anchor`, `excerpt`, `artifact_type`, `feature`, `version`
2. Keep `memory-v1.json` as the index/summary plane
   - do not replace it
   - add `evidence_ids` and `artifact_refs` instead of stuffing everything into `content`
3. Add stage context packs
   - `think/prd/test-case/implement/qa/release` should load compact evidence packs, similar to MemPalace L1/L2

### P1: absorb next

1. Add a deterministic artifact graph
   - nodes: `prd`, `user-story`, `test-case`, `implementation-summary`, `qa-result`, `debug-issue`, `release-decision`, `research-doc`
   - edges: `derived_from`, `implements`, `verifies`, `blocks`, `supersedes`, `evidence_for`
2. Upgrade recall
   - keep existing keyword path
   - add optional embedding/BM25 path for research and evidence docs
   - do not require database migration first
3. Add debug/friction control heuristics
   - recurring issue suppression
   - empty-cycle alerts
   - repeated-repair detection

### P2: absorb only if Beacon iteration pressure justifies it

1. Add deterministic background jobs for:
   - evidence projection
   - graph rebuild
   - memory compaction
   - debug recurrence summarization
2. Consider a light local SQLite store only if JSON files become too flat

### Explicitly avoid for now

1. Do not introduce a second memory silo beside `.beacon/memory`
2. Do not import `wings/rooms/drawers` terminology directly into user-facing Beacon flows
3. Do not turn Beacon into a people/company CRM brain
4. Do not make Postgres/pgvector a prerequisite

## 13. Proposed Beacon Work Items

### Slice A: evidence-backed memory

- new file family: `.beacon/memory/evidence/*.json`
- extend `memory-v1.json` items with:
  - `evidence_ids`
  - `artifact_refs`
  - `material_type`
  - `feature`
  - `version`

### Slice B: knowledge projection

- new file: `.beacon/state/knowledge-projection/latest.json`
- deterministic edge builder over docs and evidence manifests

### Slice C: smarter friction evolution

- extend `memory-friction-evolution` with:
  - repeated-candidate suppression
  - empty-cycle detection
  - repair-loop policy
  - “keep/review/discard” confidence that considers recurrence trend, not only static count

## 14. Key Source Refs

- Beacon
  - [`beacon/utils/memory.py`](../../../../beacon/utils/memory.py)
  - [`beacon/utils/workflow_memory.py`](../../../../beacon/utils/workflow_memory.py)
  - [`beacon/utils/memory_friction_evolution.py`](../../../../beacon/utils/memory_friction_evolution.py)
  - [`.beacon/memory/feedback.json`](../../../../.beacon/memory/feedback.json)
- MemPalace
  - [`oss-sync/memory-agents/mempalace/CLAUDE.md`](../../../../../oss-sync/memory-agents/mempalace/CLAUDE.md)
  - [`oss-sync/memory-agents/mempalace/mempalace/palace.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/palace.py)
  - [`oss-sync/memory-agents/mempalace/mempalace/searcher.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/searcher.py)
  - [`oss-sync/memory-agents/mempalace/mempalace/knowledge_graph.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/knowledge_graph.py)
  - [`oss-sync/memory-agents/mempalace/mempalace/layers.py`](../../../../../oss-sync/memory-agents/mempalace/mempalace/layers.py)
- gBrain
  - [`oss-sync/memory-agents/gbrain/CLAUDE.md`](../../../../../oss-sync/memory-agents/gbrain/CLAUDE.md)
  - [`oss-sync/memory-agents/gbrain/src/core/operations.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/operations.ts)
  - [`oss-sync/memory-agents/gbrain/src/core/engine.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/engine.ts)
  - [`oss-sync/memory-agents/gbrain/src/core/search/hybrid.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/search/hybrid.ts)
  - [`oss-sync/memory-agents/gbrain/src/core/minions/queue.ts`](../../../../../oss-sync/memory-agents/gbrain/src/core/minions/queue.ts)
- Evolver
  - [`oss-sync/memory-agents/evolver/README.md`](../../../../../oss-sync/memory-agents/evolver/README.md)
  - [`oss-sync/memory-agents/evolver/src/gep/signals.js`](../../../../../oss-sync/memory-agents/evolver/src/gep/signals.js)
- Hermes
  - [`oss-sync/memory-agents/hermes-agent/README.md`](../../../../../oss-sync/memory-agents/hermes-agent/README.md)
