# Beacon v1.1.10 Overall System Map

## 一句话定位

Beacon 是一个把 requirement materials、implementation、QA evidence、gate/release judgement 和 feedback loop 收进同一套版本化工件的 CLI 内核。

## 核心代码分层

```text
beacon/main.py
→ beacon/cli_factory.py
→ beacon/commands/*
→ beacon/utils/*
→ beacon/adapters/*
→ docs/beacon/<version> + .machine + .beacon runtime state
```

## 主要目录职责

| Path | Responsibility |
| --- | --- |
| `beacon/main.py` | CLI 入口，固定 import path，构建 app |
| `beacon/cli_factory.py` | 注册命令面，定义 core/support/labs/bridge |
| `beacon/commands/` | 用户可见命令入口 |
| `beacon/utils/` | 状态、工件、流程、评分、runtime helper |
| `beacon/adapters/` | browser / runner / 执行适配层 |
| `docs/beacon/<version>/` | 人类主读 requirement / execution / release docs |
| `docs/beacon/<version>/.machine/` | 机器工件与 workflow 机器投影 |
| `.beacon/` | 运行态状态、session、evidence、implement raw、debug state |

## Beacon 的三类真相面

### 1. Human primary

- `SUMMARY.md`
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `release/`
- `source-architecture/`

### 2. Machine secondary

- `.machine/user-story/*.json`
- `.machine/qa/*.json`
- `.machine/execution/*.json`

### 3. Runtime internal

- `.beacon/qa/`
- `.beacon/implement/`
- `.beacon/state/`
- `.beacon/debug/`

## 当前主循环

```text
requirement docs
→ machine materials
→ implementation
→ QA / verify
→ gate / release
→ feedback / learning / rewrite
```

源码层的重点不是单个模块，而是这些面之间是否还能对齐。
