# Beacon v1.6.13 — 批次1：人话契约 + spend 账本 + 失败模式回归 + skill 文案卫生

## 定位

`v1.6.13` 是当前交付线。批次 1 把四项能力落地：F4 人话契约推广到 7 个 core skill、
D2 spend 账本（长任务预算）、D3 失败模式用例库（对抗式审查输入）、
F2/F3/F5 skill 文案规范化（共享块去重、版本锚点单一源、mode_id 前缀统一）。

## Program

- 批次 1（4 个 lake）：
  - `beacon-v1613-f4-plain-language-contract`（人话契约）
  - `beacon-v1613-d2-spend-ledger`（预算账本）
  - `beacon-v1613-d3-failure-mode-catalog`（失败模式用例库）
  - `beacon-v1613-f235-skill-copy-hygiene`（文案扫尾）
- truth canonical: `main`（实现与验收在 worktree，验收后合并）

## 核心结果

1. 7 个 beacon core skill 输出契约强制 `plain_language_delivery_summary`（普通人可懂）。
2. goal 预算从回合上限升级为 spend 账本（幂等 CAS、quiet skip 不扣、配额耗尽 halt）。
3. 失败模式目录（≥5 条 + rubric）接入 QA/release 对抗式审查。
4. 共享守则单一来源、复制 bug 清零、过期版本锚点清理、truth-review → eval-truth-review。

## 发布面

- runtime: `v1.6.12`（本批次以 docs/truth 面交付为主，runtime 未升级）
- 正式版本面：SUMMARY / features truth 已冻结
