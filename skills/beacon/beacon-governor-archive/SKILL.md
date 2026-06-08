---
name: beacon-governor-archive
description: Beacon v1.6.0 governor skill migrated from `beacon-archive`. Use when the user wants Beacon archive governance to plan/apply/status/explain historical requirement isolation without turning archive into a new lifecycle stage.
---

# Beacon Governor Archive

This skill routes archive governance through Beacon's support-command surface.

Archive is not a new lifecycle stage. The lifecycle remains:

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

Use archive when historical requirement truth must stay traceable but stop contaminating the current delivery plane.

## Decision boundary

- Use **`beacon-governor-archive`** when historical requirement truth must stay traceable but stop polluting the **active delivery plane**.
- **Do not** use archive to edit frozen `truth.md`; route scope changes to **`beacon-change`**.
- **Do not** confuse with **`doctor metadata archive-version`** (governance branch blocks only).
- Default delivery commands (`implement`, `qa`, `release`) bind to **catalog active versions** under `docs/beacon/<v>/`.
- Inspect / lineage / inventory may read **`docs/beacon/archive/<v>/`** with explicit `--version`.

## Four operator verbs

| Verb | Intent | Primary commands |
|------|--------|------------------|
| **status** | Where are active vs archived version trees? | `beacon archive catalog status`, `beacon archive status` |
| **history** | How did a feature evolve across versions? | `beacon archive lineage <slug>` |
| **map** | What capabilities exist on the active plane? | `beacon archive inventory` |
| **cutover** | Roll the active window and relocate old trees | `beacon archive catalog plan`, `catalog apply --confirm`, `catalog bootstrap --confirm` |

## Minimal tool set

```bash
beacon archive explain
beacon archive catalog plan|apply|bootstrap|status
beacon archive plan|apply|status
beacon archive lineage <slug> [--from v] [--to v]
beacon archive inventory [--version auto] [--include-archived]
beacon doctor verify-version-truth-catalog --strict
```

## Use for

- `beacon archive plan`
- `beacon archive apply`
- `beacon archive status`
- `beacon archive explain`
- `beacon archive catalog plan|apply|bootstrap|status`
- `beacon archive lineage`
- `beacon archive inventory`
- Separating `active` truth from `archived-learnable` and `archived-reference-only`

## Operator rule

Prefer:

- `beacon archive ...`

Keep brainstorm read-only. If the task is still discussing archival strategy, stay on `beacon-brainstorm`. Once the user wants formal archive truth written, route to `beacon-governor-archive`.

## Scenario examples

### Example A — Release cutover: roll the active window

**When**: Shipping a new release line; active window stays at 3.

```bash
beacon archive catalog plan --project-root . --version v1.5.3 --json
beacon archive catalog apply --project-root . --version v1.5.3 --confirm --json
beacon doctor verify-version-truth-catalog --project-root . --strict
```

**Done when**: catalog lists the new active trio; the rolled-off version `truth_root` points at `docs/beacon/archive/<version>/`.

### Example B — Audit historical feature truth (read-only)

**Scenario:** Audit a feature in an archived version without entering implement/qa.

```bash
beacon archive status --project-root . --version v1.4.11 --feature <slug> --json
beacon truth-map resolve <slug> --project . --version v1.4.11 --json
```

**Done when**: paths and archive status are returned; no implement/qa on archived version without `--include-archived`.

### Example C — Trace cross-version evolution

```bash
beacon archive lineage <slug> --project-root . --from v1.4.10 --to v1.5.2 --json
```

**Done when**: ordered hops include `truth_path`, optional `change_path`, and revision metadata.

### Example D — Capability inventory before planning

```bash
beacon archive inventory --project-root . --version auto --json
```

**Done when**: feature × AC matrix covers active versions only unless `--include-archived`.

### Example E — Retire a shipped feature inside an active version

```bash
beacon archive plan --project-root . --version v1.5.2 --feature <slug> \
  --archive-status archived-reference-only --reason shipped-and-superseded --json
beacon archive apply --project-root . --version v1.5.2 --feature <slug> \
  --archive-status archived-reference-only --json
```

**Done when**: help routes away from implement; truth files remain readable.

### Example F — Learn from history without overriding active truth

```bash
beacon archive apply --project-root . --version v1.4.11 --feature <slug> \
  --archive-status archived-learnable --reason pattern-source --json
beacon learn recall --topic "<pattern>" --json
```

**Done when**: learn cites archived refs only; active-plane truth is unchanged.

## Examples

- 适用例：
  - “这批旧 requirement 需要保留可追溯性，但不能继续污染当前交付面。”
  - “我想看 archive 现在的状态、计划或解释。”
  - “发布新版本后，如何把旧版本目录迁到 archive 并更新 catalog？”
- 不适用例：
  - “我还在讨论要不要归档、归档策略对不对。” -> 应先去 `beacon-brainstorm`
  - “我要改冻结后的 truth.md。” -> 应去 `beacon-change`


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。

## v1.6.0 Harness Migration

- Harness：`governor`。
- 来源迁移：`beacon-archive` -> `beacon-governor-archive`。
- 主要作用：历史需求隔离。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`governor`。
- 来源迁移：`beacon-archive` -> `beacon-governor-archive`。
- 主要作用：历史需求隔离。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
