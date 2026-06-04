---
name: beacon-archive
description: Use when the user wants Beacon archive governance to plan/apply/status/explain historical requirement isolation without turning archive into a new lifecycle stage.
---

# Beacon Archive

This skill routes archive governance through Beacon's support-command surface.

Archive is not a new lifecycle stage. The lifecycle remains:

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

Use archive when historical requirement truth must stay traceable but stop contaminating the current delivery plane.

## Decision boundary

- Use **`beacon-archive`** when historical requirement truth must stay traceable but stop polluting the **active delivery plane**.
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

Keep brainstorm read-only. If the task is still discussing archival strategy, stay on `beacon-brainstorm`. Once the user wants formal archive truth written, route to `beacon-archive`.

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
