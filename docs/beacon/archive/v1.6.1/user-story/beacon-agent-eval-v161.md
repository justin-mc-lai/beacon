# User Story: beacon-agent-eval-v161

**Feature**: `beacon-agent-eval-v161`
**Version**: `v1.6.1`
**Status**: `bootstrap-generated / review-required / not-yet-frozen`
**Date**: `2026-06-15`
**Language**: `zh`

## Story

作为目标用户，我希望系统能够稳定地完成该需求主流程，以便快速完成业务动作。

### 需求描述

v1.6.1 Agent Eval full parity：统一 eval 分数面、能力目录全 harness 覆盖、live/replay/simulated 分层 runner、with_skill vs baseline 行为证据、继承 v1.6.0 skill-eval benchmark 契约并闭合 AC-018..022、program harness 与 public CLI 纳入 catalog、产出 composite 0-100 scorecard（runtime_evidence_only，不替代 formal QA/release）

## Outline

<!-- FILL: Mermaid diagram showing the user journey through key paths.
     Use flowchart LR for user journey. Each node maps to an AC. -->

```mermaid
flowchart LR
    A[User starts] --> B[Action 1]
    B --> C[Outcome]
```

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-001 | happy-path | 用户可以完成「beacon-agent-eval-v161」主流程，满足：v1.6.1 Agent Eval full parity：统一 eval 分数面、能力目录全 harness 覆盖、live/replay/simulated 分层 runner、with_skill vs baseline 行为证据、继承 v1.6.0 skill-eval benchmark 契约并闭合 AC-018..022、program harness 与 public CLI 纳入 catalog、产出 composite 0-100 scorecard（runtime_evidence_only，不替代 formal QA/release） |
| AC-002 | validation | 输入校验规则明确，非法输入会返回可读错误。 |
| AC-003 | error-handling | 依赖失败时系统可恢复并提供下一步指引。 |
| AC-004 | observability | 关键步骤具备可追踪日志与最小化诊断信息。 |
| AC-005 | security | 仅授权用户可执行敏感操作，越权请求被拒绝。 |

## Test Story Map

| Test ID | Covers | Scenario |
|---------|--------|----------|
<!-- FILL: TC-001 | AC-001 | <scenario> -->

## References

- Research: `docs/beacon/archive/v1.6.1/research/beacon-agent-eval-v161.md`
- PRD: `docs/beacon/archive/v1.6.1/prd/beacon-agent-eval-v161.md`
- Test cases: `docs/beacon/archive/v1.6.1/qa/test-cases/beacon-agent-eval-v161.md`
