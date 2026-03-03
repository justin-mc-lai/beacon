# Test Cases: workflow-memory-lifecycle-alignment

## Overview

**Feature**: workflow-memory-lifecycle-alignment  
**Version**: v1.0.1  
**Source**: user-story/workflow-memory-lifecycle-alignment.md

---

## AC → TC Mapping

| AC ID | TC ID | Layer | Scenario | Expected |
|------|------|-------|----------|----------|
| AC-001 | TC-001 | unit | 运行 auto workflow，检查 6 阶段均有 start/context/finish/writeback | closure_complete=true |
| AC-002 | TC-002 | unit | release 事件存在时，不要求 release 拥有 workflow 四件套 | 不产生假缺阶段 |
| AC-003 | TC-003 | unit | 无显式 run_id 时，默认选择最近 workflow run | run_id=run-* |
| AC-004 | TC-004 | unit | 显式 run_id 指向 release:* 时，按指定 run 计算 | 结果可解释且兼容 |
| AC-005 | TC-005 | unit | release 证据缺失时执行 release memory profile 校验 | blocked + reason_code |
| AC-006 | TC-006 | unit | workflow_memory fixture 从 4 阶段升级到 6 阶段 | 测试通过 |
| AC-007 | TC-007 | unit | gate_memory_closure fixture 从 4 阶段升级到 6 阶段 | 测试通过 |
| AC-008 | TC-008 | smoke | release 专用校验成功路径（证据完整） | pass |
| AC-008 | TC-009 | smoke | release 专用校验失败路径（证据缺失） | blocked |

---

## Execution Checklist

- [ ] 执行 workflow lifecycle tests（6阶段）
- [ ] 执行 gate memory closure tests（6阶段）
- [ ] 执行 release profile tests（成功/失败路径）
- [ ] 验证 report/status/resume memory metrics 输出一致

