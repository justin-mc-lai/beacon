# Beacon v1.1.10 Workflow And Artifact Flow

## Beacon 不是只写文档

Beacon 的关键价值在于：

```text
requirement
→ machine projection
→ implementation
→ QA evidence
→ gate / release
→ feedback / rewrite
```

源码架构理解必须围绕工件流，而不是只围绕模块名。

## 三类工件

### 1. Human-readable docs

位置：

- `docs/beacon/<version>/`

作用：

- 给人类阅读和协作

### 2. Machine materials

位置：

- `docs/beacon/<version>/.machine/`

作用：

- 给 workflow 和自动化命令消费

### 3. Runtime evidence/state

位置：

- `.beacon/`

作用：

- 给执行过程、session、evidence、implement raw、debug loop 使用

## 典型 artifact flow

### Requirement side

```text
user-story.md / prd.md / test-cases.md
→ .machine/user-story/*.json
→ .machine/qa/*.json
→ .machine/execution/*.revision.json
```

### Implementation side

```text
.beacon/implement/<run_id>/*
→ execution/implementation-summary-*.md
→ execution/technical-implementation-*.md
→ .machine/execution/technical-implementation-*.json
→ .machine/execution/requirement-rewrite-input-*.json
```

### QA side

```text
.beacon/qa/status.json
.beacon/qa/sessions/*
.beacon/evidence/*
→ release_scorecard / gate_report / learning_loop inputs
```

## 为什么 source-architecture 也要进这条流

因为架构文档不是“读后即弃”的解释。

它必须跟着：

- command surface changes
- state model changes
- artifact path changes
- workflow changes

一起演进。
