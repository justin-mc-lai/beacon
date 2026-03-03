# PRD: UI 假通过防护增强（v1.0.1）

## 1. 背景

当前自动测试存在“逻辑通过但无真实操作证据”的风险，影响 Verify/Gate 的可信度与发布质量。

## 2. 目标

1. 强化 UI 验证的真实性
2. 强化关键动作证据的完整性
3. 强化 AC→TC→Evidence 的可审计性

## 3. 需求

### 3.1 功能需求

- FR-001（对应 AC-001）：UI 层缺少真实执行命令时，不得通过
- FR-002（对应 AC-002）：关键动作证据必须全量覆盖
- FR-003（对应 AC-003）：证据路径必须存在且结构可读
- FR-004（对应 AC-004）：状态产物输出可读 reason_code 与缺失项
- FR-005（对应 AC-005）：gate 严格模式拦截证据链断裂

### 3.2 非功能需求

- NFR-001：保持 CLI 兼容（`beacon` 与 `beacon-<subcommand>`）
- NFR-002：失败信息具备稳定 reason code，便于 CI 聚合

## 4. 验收条目（AC）

| ID | 条目 |
|----|------|
| AC-001 | 无真实 UI 命令不得 PASS |
| AC-002 | 关键动作证据缺失即 FAIL |
| AC-003 | 证据文件必须存在且可解析 |
| AC-004 | status 输出应包含可诊断字段 |
| AC-005 | gate strict/debug 必须识别执行缺口 |
| AC-006 | workflow verify 与 auto-test 行为一致 |
| AC-007 | 参数/断言异常不得 silent pass |

## 5. 里程碑

- M1：规则严格化（P0）
- M2：证据校验收敛（P1）
- M3：真实 UI 自动化补齐（P2）

## 6. 关联文档

- `research/ui-test-false-pass-and-coverage-research.md`
- `user-story/ui-test-false-pass-hardening.md`
