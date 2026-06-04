# PRD: Beacon 人机协作分层、memory 投影收口与 `.machine` 迁移（v1.1.5）

## 1. 背景

Beacon 当前已经形成：
- requirement materials
- execution artifacts
- QA matrices
- memory / lifecycle / feedback
- doctor / gate / report / status

问题不在于 Beacon 缺少结构化工件，而在于：

> 人类和机器被迫阅读同一层产物。

结果是：
- 人类看到过多 JSON，认知负担过高；
- 机器需要读的东西也暴露在主阅读路径中；
- 项目 package 在规模变大后（例如多 feature / 多 slice）会出现明显的“文档心智爆炸”。

## 2. 第一性原理结论

从原始问题出发：

### 人类需要什么
- 能帮助决策、评审、推进、验收的 Markdown 主入口

### 机器需要什么
- 可稳定解析、可被校验、可被 doctor/gate/report/status 消费的结构化 JSON

### Beacon 应负责什么
- 定义人类面 / 机器面 / runtime 面的边界
- 定义 memory 的投影结构
- 定义 doctor 的修复职责

### Beacon 不应负责什么
- 为旧结构做长期兼容保活
- 在 v1.1.5 中维持双轨目录长期并存

## 3. 目标

1. 把 `docs/beacon/<version>/.machine/` 定义为机器正式读取面
2. 把人类正式阅读路径收口到 Markdown 主入口
3. 把 Beacon memory 模块定义成四层结构
4. 定义 `doctor` 的破坏性修复职责
5. 保证新规范下 status/report/gate 仍能读取正确的 machine 和 memory 信息

## 4. 目录分层规范

## 4.1 Human Primary Surface

```text
SUMMARY.md
release/<version>.md
execution/index.md
execution/boundaries.md
execution/service-slice-map.md
qa/test-cases/index.md
qa/test-cases/<feature>.md
user-story/<feature>.md
prd/<feature>.md
architecture/*.md
```

规则：
- 人类默认从这里进入；
- README / SUMMARY / release 只引用这些主入口；
- 不把 JSON 列为 primary artifact。

## 4.2 Machine Secondary Surface

```text
docs/beacon/<version>/.machine/
├── execution/
│   ├── config.json
│   ├── source.json
│   ├── git-alignment.json
│   ├── change-impact.json
│   ├── delivery-manifest.json
│   └── terminal.json
└── qa/
    ├── <feature>.ac-test-matrix.json
    └── <feature>.qa9-matrix.json
```

规则：
- 机器工件仍属于 `docs/beacon/<version>/` 的正式事实源；
- 但默认不进入人类主阅读路径；
- `doctor` / `gate` / `report` / `status` / automation 以此为读取目标。

## 4.3 Runtime Internal Surface

```text
.beacon/
├── memory/
├── state/
├── runs/
└── implement/
```

规则：
- `.beacon/` 不是正式交付文档；
- 仅用于 runtime 和原始证据。

## 5. Memory 4-Layer Model

## 5.1 Canonical Store
- `memory-v1.json`
- canonical memory items
- revision / supersede / upsert / content_hash

## 5.2 Workflow Lifecycle
- `workflow-lifecycle.json`
- stage_started / stage_context_injected / stage_finished / stage_failed / memory_writeback
- attempt / retry / closure_complete / next_stage

## 5.3 Feedback Assimilation
- gate / auto-test / manual / debug -> feedback candidate -> memory revision
- `feedback extract/apply/sync`

## 5.4 Consumption / Projection
- `status`
- `report`
- `recall`
- gate strict memory closure checks
- governance metrics / memory metrics

结论：
- 人类不直接主读 raw memory JSON；
- 人类主要读 memory projection；
- 机器主要读 raw memory store 与 lifecycle artifacts。

## 6. LLM / Agent Reading Contract

LLM 与机器默认读取：
1. `docs/beacon/<version>/.machine/`
2. `docs/beacon/<version>/` 的人类主文档
3. `.beacon/memory/*`

但对人类采用渐进式披露：
- 先看 Markdown 主入口；
- 机器细节只在需要 doctor / gate / status / debug 时展开。

## 7. Doctor 修复职责

`doctor` 在 v1.1.5 中应具备：
1. 路径修复：把旧 execution/qa JSON 迁到 `.machine/`
2. 索引修复：补 `execution/index.md` / `qa/test-cases/index.md`
3. 引用修复：更新 `SUMMARY.md` / `release/<version>.md` / 相关入口引用
4. package 体检：确认人类主入口与机器读取面都完整

## 8. 非目标

- 不做长期兼容方案
- 不在 v1.1.5 维持双写结构作为正式目标
- 不把 Beacon 变成 runtime orchestrator
- 不讨论外部 runner 的额外新能力

## 9. 成功标准

- 人类主入口明显简化
- machine artifacts 有明确归位
- memory 模型有正式分层文档
- doctor 能把旧包修到新结构
- gate/report/status 不因结构升级而失效
