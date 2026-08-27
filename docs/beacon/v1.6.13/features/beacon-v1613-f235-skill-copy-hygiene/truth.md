---
slug: beacon-v1613-f235-skill-copy-hygiene
version: v1.6.13
status: frozen
language: zh
domain_required: false
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
package_maturity: filled
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.13/features/beacon-v1613-f235-skill-copy-hygiene/truth.md
  user_story: docs/beacon/v1.6.13/features/beacon-v1613-f235-skill-copy-hygiene/truth.md
  test_case: docs/beacon/v1.6.13/features/beacon-v1613-f235-skill-copy-hygiene/tests.md
---

# Requirement Truth: beacon-v1613-f235-skill-copy-hygiene (v1.6.13)

## 人话

给 beacon 的 skill 文档做一次**"抄写卫生"大扫除**。之前共享规则靠复制粘贴，已经贴出 bug。这次做三件事：

1. **共享规则只放一份**：所有模式文件都引用的那段"共同守则"，抽出来放一个文件，别的只引用，不再各抄各的（顺手修掉两处复制出的 bug：一处连写三个同名命令）
2. **版本号只写一处**：模式文件里不再写死旧版本号（之前写 v1.5.2，实际已到 v1.6.12），改从单一来源取
3. **名字统一**：`truth-review` 改成带统一前缀的名字（`eval-truth-review`），旧的还认（兼容别名）

效果：翻任何文件都不会看到自相矛盾的版本号或重复定义；改一处共享规则，处处生效。

- 能做：抽共享块、修复制 bug、统一版本锚点、统一命名前缀并保留旧名兼容
- 不能做：不改各模式的功能语义；不重写 7 个 skill 的正文内容（那是 L1 人话契约的范围）
- 怎样算完：共享块单一引用生效、两个复制 bug 消失、模式内无硬编码过期版本、前缀统一且旧名可用

## User Intent

清理 beacon skill 模式文件的"复制粘贴卫生"问题（F2/F3/F5）：共享块去重、修复复制 bug、版本锚点单一化、mode_id 前缀统一。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: beacon-v1613-planning-source-audit-2026-08-27 F2/F3/F5
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | F5：共享块单一来源 | must | AC-001 | covered |
| INT-002 | F5：修复复制 bug | must | AC-002 | covered |
| INT-003 | F2：版本锚点单一源 | must | AC-003 | covered |
| INT-004 | F3：mode_id 前缀统一 | must | AC-004 | covered |

## 用户旅程

1. 触发：开发者/agent 打开任意 beacon mode 文件
2. 关键操作：读到共享守则（来自单一引用）；版本号来自单一来源；名字统一
3. 结果：不再看到互相矛盾的版本号或重复的共享块；改一处守则处处生效
4. 异常：旧名 `truth-review` 仍可路由（legacy alias），不破坏存量引用

## First principles

- 系统边界：只动 skill 文档结构与引用，不改功能语义
- 不可变：共享守则内容保持不变（只是换了存放与引用方式）
- 可推翻假设：版本锚点抽到 INDEX/package map 为单一 source，mode 内不留硬编码

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| SharedPreamble | content, ref_path | 单一来源的共享块 |
| ModeFile | mode_id, refs, version_anchor | ~20 个 mode 文件 |
| ModeIdAlias | legacy, canonical | truth-review → eval-truth-review |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 共享 preamble / HARD GATE / GIT_ADMISSION 抽到单一共享文件（`references/shared/`），~20 个 mode 文件改为引用，不再逐字复制——触发 `extract_shared` 进入 deduped 状态。 |
| AC-002 | deduped 状态要求：修复已知复制 bug（`pln-brainstorm.md` 三个同名 `beacon-gen-truth`、`gen-truth.md` 旧版自指残留），复制式残留清零。 |
| AC-003 | `fix_copy_bugs` 后：mode 文件内无硬编码过期版本号（v1.4.x/v1.5.x 等）；版本锚点单一来源（INDEX/package map），grep 过期版本计数为 0（保留历史归档除外）——进入 anchored 状态。 |
| AC-004 | `unify_prefix` 触发：`truth-review` 更名为 `eval-truth-review`（统一 eval-* 前缀），并保留 legacy alias 路由；旧引用可用——进入 closed 状态。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| deduped | scaffold | refs_updated |
| anchored | deduped | grep_clean |
| closed | anchored | alias_added |

## Illegal transitions

- 共享块仍多份复制且漂移（复制残留）
- 模式内仍写死过期版本（锚点漂移）

## FSM 五元组

> domain_required=false（skill 文档层湖），元状态即可。

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | extract_shared | refs_updated | deduped | — |
| deduped | fix_copy_bugs | grep_clean | anchored | — |
| anchored | unify_prefix | alias_added | closed | — |

**终态：** closed（卫生达标）

### invalid / illegal

- 共享块仍多份复制且漂移（illegal：复制残留）
- 模式内仍写死过期版本（illegal：锚点漂移）

## Non-goals

- 不改各 mode 的功能语义/输出契约正文
- 不重写 7 个 SKILL.md 的正文（L1 人话契约覆盖）
- 不动归档历史文档

## Freeze readiness

- [x] Intent Matrix must 无 missing
- [x] 用户旅程非「待补」占位
- [x] First principles / Domain Model 已具体化
- [x] 元状态 FSM + illegal
- [x] 每 AC ≥ 1 TC（Command+Assertion）+ exec-layer TC
- [x] tasks 均有 ac= + evidence= 绑定
- [x] package_maturity: filled
- [x] `beacon truth review` pass 后再 freeze

### Gap vs gold (订单支付示例)

- 对照：`docs/beacon/v1.6.13/features/truth-gold-order-pay-v1610/truth.md`
- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`

## Source Excerpt

```markdown
beacon-v1613-f235-skill-copy-hygiene
源审计：docs/beacon/research/beacon-v1613-planning-source-audit-2026-08-27.md §3 F2/F3/F5
证据：pln-brainstorm.md:33（三个同名）、gen-truth.md:44（自指残留）、各 mode「v1.5.2/v1.4.3」过期锚点
```
