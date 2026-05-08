# Guardrail Cutover Audit

- 主问题：当前为什么还不能 cut over，或为什么已经可以进入 implement？
- 必须冻结：
  - dual-read consistency
  - blocked reason
  - fallback path
  - guardrail verdict
  - implement-ready 判定
