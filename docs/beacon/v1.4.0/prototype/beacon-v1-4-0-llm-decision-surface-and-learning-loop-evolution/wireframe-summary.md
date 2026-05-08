# 线框草图汇总：beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution

**Feature**: `beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution`
**Version**: `v1.4.0`
**Mode**: `wireframe`
**Generated At**: `2026-05-08T00:00:00Z`

## 页面清单

| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |
|---------|----------|------|--------|----------|
| `intent-router` | Intent Router | Web, PC | P0 | 收束 freeform intent，明确 route 推荐、change 必要性与禁止路径。 |
| `decision-surface-overview` | Decision Surface Overview | Web, PC | P0 | 展示六个核心 skill 的统一 decision surface 结构与当前覆盖状态。 |
| `skill-surface-detail` | Skill Surface Detail | Web, PC | P0 | 冻结单个 skill 的 inputs、protocol、anti-inertia、learning、backstop 结构。 |
| `learning-disclosure-center` | Learning Disclosure Center | Web, PC | P1 | 展示 feature -> host -> runner -> domain 的 learning hint 披露、降级与来源。 |
| `reasoning-contract-review` | Reasoning Contract Review | Web, PC | P1 | 展示 diagram / semantic 输入如何驱动 PRD、story、test-case 深度推理。 |
| `guardrail-cutover-audit` | Guardrail Cutover Audit | Web, PC | P0 | 冻结 Python guardrail、dual-read consistency 与 implement-ready 判定。 |

## 跳转关系图

```text
[intent-router] -- 点击核心 skill 卡片 --> [decision-surface-overview]
[intent-router] -- 点击需要改 truth 的推荐 --> [guardrail-cutover-audit]
[decision-surface-overview] -- 点击单个 skill --> [skill-surface-detail]
[decision-surface-overview] -- 点击 reasoning input --> [reasoning-contract-review]
[decision-surface-overview] -- 点击 learning hint --> [learning-disclosure-center]
[skill-surface-detail] -- 点击返回 --> [decision-surface-overview]
[learning-disclosure-center] -- 点击返回 --> [decision-surface-overview]
[reasoning-contract-review] -- 点击返回 --> [decision-surface-overview]
[guardrail-cutover-audit] -- 点击返回 --> [intent-router]
[guardrail-cutover-audit] -- 点击继续实现 --> [decision-surface-overview]
```

## 冻结检查点

- [x] 页面清单完整
- [x] 跳转逻辑完整
- [x] route / state / navigation / interaction contract 已显式覆盖
- [x] 关联 requirement 可追踪
- [x] 仅保留 wireframe freeze 语义
