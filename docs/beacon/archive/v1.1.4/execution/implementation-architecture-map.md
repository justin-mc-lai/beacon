# Beacon implementation architecture map（v1.1.4 Draft）

## 1. 目标

给出 Beacon 在 `v1.1.4` 中围绕 implementation 的统一架构图，明确以下对象的关系：

- `skill`
- `implement`
- `review`
- `workflow`
- `bridge`
- `docs/beacon`
- `.beacon/implement`

文档目标是回答三个问题：

1. 哪些模块负责控制面，哪些负责执行面；
2. 哪些目录保存长期事实，哪些目录保存运行时原始状态；
3. implementation 完成后，结果如何流入 review / verify / gate / release。

---

## 2. 总体分层图

```text
┌─────────────────────────────────────────────────────────────┐
│                       User / Operator                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Beacon CLI Surface                      │
│                                                             │
│  skill       implement       review       workflow          │
│  (control)   (execution)     (writeback)  (orchestration)  │
└─────────────────────────────────────────────────────────────┘
             │             │             │             │
             │             │             │             │
             ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Beacon Contract / State Layer              │
│                                                             │
│  docs/beacon/<version>/        .beacon/implement/<run_id>/  │
│  .beacon/state/                .beacon/memory/              │
│  .beacon/evidence-manifest     .beacon/runs/                │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Skill / Runner Layer               │
│                                                             │
│   OMX runner     gstack handoff     custom adapters         │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Bridge / Runtime Channel                  │
│                                                             │
│   run / team / ralph-bridge / OMC / OMX runtime            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 职责分层

## 3.1 `skill` —— Control / Preference Plane

### 职责
- 检测可用 skill 工具
- 管理 adapter registry
- 设置用户/项目偏好
- 输出 adapter diagnostics

### 不负责
- 真正执行 implementation
- 写 implementation summary
- 直接推进 workflow stage

### 关键词
- detect
- list
- register
- prefer
- doctor

---

## 3.2 `implement` —— Execution Adapter Plane

### 职责
- 解析 implementation runner
- 读取 Beacon source-of-truth artifacts
- 生成 request contract
- 调用外部 runner / skill
- 消费 result contract
- 写 implementation marker / summary
- 触发 review/writeback 链路

### 不负责
- 自己变成调度器/team runtime
- 替代外部 skill 的执行引擎
- 直接替代 verify/gate/release

---

## 3.3 `review` —— Formal Writeback Plane

### 职责
- `review spec`：判断哪些需求物料需要回填
- `review quality`：判断 verify/gate-ready
- 输出 formal review artifacts

### 不负责
- 自己执行实现
- 自己执行完整 verify pipeline

---

## 3.4 `workflow` —— Main-chain Orchestration Plane

### 职责
- 维护 canonical workflow state model
- 推进主链：
  `think -> user-story -> prd -> [prototype] -> test-case -> implementation -> verify -> gate`
- 在 implementation 阶段委托给 `implement run`

### 不负责
- 持有每个 runner 的细节配置
- 替代 `skill` 做偏好管理

---

## 3.5 `bridge` —— Experimental Runtime Plane

### 职责
- 连接外部 runtime / team / orchestration 通道
- 提供实验性 bridge 能力
- 与 OMC/OMX/team-runtime 协作

### 不负责
- 成为正式 implementation 产品面
- 持有 implementation request/result/writeback 契约

> 结论：`implement` 与 `bridge` 必须分层存在。

---

## 4. Source of Truth 与 Runtime 分层

## 4.1 长期事实源：`docs/beacon/<version>/`

```text
docs/beacon/<version>/
├── SUMMARY.md
├── user-story/
├── prd/
├── qa/test-cases/
├── prototype/
└── execution/
```

### 这里保存
- 正式需求物料
- execution 层 formal docs
- implementation summary
- review outputs

### 这里不保存
- 原始 stdout/stderr
- runner 临时 request/result
- shell/raw logs

---

## 4.2 运行时原始状态：`.beacon/implement/<run_id>/`

```text
.beacon/implement/<run_id>/
├── request.json
├── request.md
├── result.json
├── stdout.log
├── stderr.log
└── command.txt
```

### 这里保存
- implementation 执行请求
- 外部 runner 结果
- 原始日志
- handoff 包

### 这里不应冒充
- PRD
- User Story
- Test Case
- 正式 execution 文档

---

## 5. 控制流图（Control Flow）

```text
User
  -> beacon skill prefer omx
  -> beacon workflow continue
      -> workflow resolves next stage = implementation
      -> workflow delegates to beacon implement run
          -> implement resolves adapter via skill/config
          -> implement writes request
          -> implement invokes external runner
          -> implement reads result
          -> implement writes marker + summary
          -> implement triggers review spec
          -> (later) verify -> review quality -> gate
```

---

## 6. 数据流图（Data Flow）

```text
docs/beacon/<version>/user-story/*.md
               │
docs/beacon/<version>/prd/*.md
               │
docs/beacon/<version>/qa/test-cases/*.md
               │
docs/beacon/<version>/prototype/*
               │
               ▼
        beacon implement run
               │
               ├── writes .beacon/implement/<run_id>/request.json
               ├── invokes external runner / skill
               ├── reads .beacon/implement/<run_id>/result.json
               │
               ▼
   .beacon/state/implementation-<feature>.json
               │
               ▼
 docs/beacon/<version>/execution/implementation-summary-<feature>.json
 docs/beacon/<version>/execution/implementation-summary-<feature>.md
               │
               ▼
        beacon review spec / quality
               │
               ▼
         verify -> gate -> release
```

---

## 7. 状态流图（State Flow）

```text
[Not Started]
     │
     ▼
[skill configured]
     │
     ▼
[implement request generated]
     │
     ▼
[external runner executing]
     │
     ├── fail -> [implement blocked]
     │            reason_code:
     │            runner_not_configured /
     │            runner_execution_failed /
     │            runner_result_missing /
     │            runner_result_invalid
     │
     ▼
[implement completed]
     │
     ▼
[implementation marker + summary written]
     │
     ▼
[review spec]
     │
     ├── writeback required -> [artifact update required]
     │                         -> update docs -> verify
     │
     ▼
[verify]
     │
     ▼
[review quality]
     │
     ▼
[gate-ready]
     │
     ▼
[gate-pass]
     │
     ▼
[release]
```

---

## 8. 与 OMX / gstack 的适配位置

```text
skill plane
  ├── omx adapter      -> command-skill
  ├── gstack adapter   -> handoff / claude-skill
  └── custom adapter   -> command / command-skill / handoff

implement plane
  └── consumes resolved adapter and executes via unified contract
```

### 结论
- OMX 适合 execution adapter
- gstack 更适合 handoff / claude-skill adapter
- Beacon 统一 request/result/writeback 协议，避免为每个工具单独改主链

---

## 9. 关键接口关系

| 模块 | 输入 | 输出 |
|---|---|---|
| `skill` | project/global config, environment | resolved adapter / preferred tool |
| `implement` | feature + source-of-truth + adapter | request/result/marker/summary |
| `review spec` | implementation result + docs | artifact update decision |
| `review quality` | verify evidence + docs | gate-ready decision |
| `workflow` | state + next stage | delegates to implement / verify / gate |
| `bridge` | runtime target | execution channel only |

---

## 10. 关键设计约束

1. `skill` 和 `implement` 必须拆开：一个管偏好/配置，一个管执行/回填；
2. `implement` 必须有 formal writeback，不只是 shell command wrapper；
3. `docs/beacon/<version>/execution/` 是长期 summary 层；
4. `.beacon/implement/` 是 raw runtime 层；
5. `bridge` 不能吞并 `implement` 的职责；
6. `review` 必须是 implementation 之后的正式回路。

---

## 11. 成功标准

- 用户能通过 `skill` 声明自己偏好的实现 skill 工具；
- `implement` 能消费 skill registry 结果并执行 implementation；
- implementation 结果能流入 marker / summary / review / gate；
- 架构分层足够清楚，不让 Beacon 滑向 scheduler/orchestrator。
