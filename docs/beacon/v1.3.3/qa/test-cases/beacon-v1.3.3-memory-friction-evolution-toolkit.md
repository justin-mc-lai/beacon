# 测试用例：Beacon v1.3.3 记忆进化与摩擦演进 Toolkit

**Feature**: `beacon-v1.3.3-memory-friction-evolution-toolkit`  
**Version**: `v1.3.3`  
**Date**: `2026-04-17`  
**Status**: `planning line`

## 测试目标

验证 memory/friction toolkit 在 optional analysis 面可执行、可回放、可写回，且不扩张主 6+3 认知负担。

## 测试用例

## TC-001：memory-only 模式输出候选

- Given：存在 feedback/decision memory 数据
- When：执行 `beacon memory-friction-evolution run --mode memory --json`
- Then：输出候选列表不为空，且含 `friction_summary/evidence_refs/recommended_command`
- Covers：`AC-002`, `AC-003`

## TC-002：friction-only 模式输出候选

- Given：存在 `.beacon/debug/issues/*.json`
- When：执行 `beacon memory-friction-evolution run --mode friction --json`
- Then：输出候选包含 debug friction 信号，且推荐命令可执行
- Covers：`AC-002`, `AC-003`

## TC-003：both 模式合并候选并去重

- Given：memory 与 friction 信号同时存在
- When：执行 `beacon memory-friction-evolution run --mode both --json`
- Then：候选集合完成合并且无重复 candidate id
- Covers：`AC-003`

## TC-004：并行 lighthouse 产物不冲突

- Given：目标项目可运行 lighthouse
- When：执行 `beacon memory-friction-evolution run --mode both --with-lighthouse --json`
- Then：toolkit 报告与 lighthouse 报告均落盘，路径互不覆盖
- Covers：`AC-001`

## TC-005：max-turns 防止无限循环

- Given：输入候选数量大于 Top-N
- When：执行 `beacon memory-friction-evolution run --max-turns 2 --json`
- Then：turn 数量不超过 2，且 `decision.should_exit=true`
- Covers：`AC-004`

## TC-006：writeback 仅通过 memory upsert

- Given：存在可 keep/review 的候选
- When：执行 `beacon memory-friction-evolution run --writeback --json`
- Then：写回 entries 来源标识为 `memory-friction-evolution.writeback`
- And：未创建新的 memory silo 文件
- Covers：`AC-005`

## TC-007：命令面保持 optional

- Given：默认 `beacon --help`
- When：检查主帮助命令面
- Then：toolkit 不出现在默认主教学路径，仅在 labs/hidden 可访问
- Covers：`AC-006`

## 建议执行节奏

1. 先跑 TC-001 ~ TC-003，验证候选输出契约。  
2. 再跑 TC-004 ~ TC-005，验证并行与 loop 有界性。  
3. 最后跑 TC-006 ~ TC-007，验证写回路径与命令面边界。  
