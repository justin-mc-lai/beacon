# Beacon v1.3.12 Execution Index

## 目标

本版本执行面服务于 `host-llm requirement deepening and human-loop closure` 主线。

目标不是新增生命周期，也不是替换 `implement / qa / release`，而是让既有 `prd -> user-story -> test-case` 更像 requirement compiler，而不只是 requirement projection。

## 当前执行结论

- requirement clarity：进行中
- implementation focus：
  - host-native requirement deepening contract
  - gap register / supplement protocol
  - PRD-centered story discovery
  - risk- and state-aware test-case expansion
  - human-loop re-freeze semantics
  - unified requirement convergence contract

## 关键执行引用

- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.3.11/SUMMARY.md`
- `docs/beacon/v1.3.11/execution/index.md`
- `docs/beacon/v1.3.12/execution/beacon-v1.3.12-one-page-runbook.md`
- `docs/beacon/v1.3.12/prd/beacon-v1.3.12-host-llm-requirement-deepening-and-human-loop-closure.md`
- `docs/beacon/v1.3.12/execution/requirement-convergence-contract.md`
- `beacon/commands/prd.py`
- `beacon/commands/user_story.py`
- `beacon/commands/test_case.py`
- `beacon/utils/requirement_parsing.py`
- `beacon/utils/semantic_runtime.py`

## 当前非目标

- 不新增新的一级公开主命令
- 不把 requirement deepening 升级成独立 public stage
- 不让 host LLM 直接改写 frozen truth 而绕过人类确认
- 不把 `doctor sync-materials` 当作正常 requirement compile 主路径
- 不改变 `implement / qa / release` 的闭环角色
- `./evo-harness-contract.md`
- `./evo-scorecard-contract.md`
