---
slug: truth-gold-order-pay-v1610
version: v1.6.10
revision_id: R3
materials_status: current
---

| TC ID | AC ID | Command | Assertion |
|-------|-----|---------|-----------|
| TC-PAY-001 | AC-PAY-001 | `rg -n "PayRequested" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 存在 |
| TC-PAY-002 | AC-PAY-002 | `rg -n "非 created|拒绝" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 拒绝 |
| TC-PAY-003 | AC-PAY-003 | `rg -n "幂等|record_success_once" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 幂等 |
| TC-PAY-010 | AC-PAY-010 | `rg -n "PaymentFailed" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 失败 |
| TC-PAY-011 | AC-PAY-011 | `rg -n "paid 再 PayRequested|paid 再" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 拒绝再付 |
| TC-PAY-020 | AC-PAY-020 | `rg -n "created→paid|跳态" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | illegal |
| TC-PAY-021 | AC-PAY-021 | `rg -n "无 success|without success" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | illegal |
| TC-PAY-022 | AC-PAY-022 | `rg -n "PayTimeout|closed" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 关单 |
| TC-PAY-023 | AC-PAY-023 | `rg -n "closed 再" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | closed 拒绝 |
| TC-RF-001 | AC-RF-001 | `rg -n "RefundRequested|refunding" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 退款 |
| TC-RF-002 | AC-RF-002 | `rg -n "RefundSucceeded|refunded" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 退成功 |
| TC-RF-003 | AC-RF-003 | `rg -n "shipped" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 拦截 |
| TC-RF-004 | AC-RF-004 | `rg -n "refunded 再" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 终态 |
| TC-PAY-030 | AC-PAY-030 | `test -f skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md` | 示例 |
| TC-PAY-031 | AC-PAY-031 | `rg -n "closed|refunding|refunded" skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md` | 状态集 |
| TC-PAY-032 | AC-PAY-032 | `rg -n "Event \| Guard|Guard" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 五元组 |
| TC-PAY-033 | AC-PAY-033 | `rg -n "Intent Coverage Matrix|INT-PAY-01" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md` | 矩阵 |
| TC-PAY-034 | AC-PAY-034 | `rg -c "TC-PAY-|TC-RF-" docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/tests.md` | TC 行数≥15 |
