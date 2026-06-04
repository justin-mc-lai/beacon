# Beacon v1.1.7 Commands Hub

> Top-level navigation entry for all human-facing command docs in Beacon v1.1.7.

---

## What this page is for

This page is the **single human-primary entrypoint** for command usage in Beacon v1.1.7.

Use it when you want to:

- find the right command doc fast
- choose the right level of detail
- jump from “I am new” to “I need the full command tree”
- move from external-user docs to operator docs without reading `.machine/`

---

## Recommended reading order

### If you are brand new

1. `USAGE.md`
2. `getting-started-10-minutes.md`
3. `execution/command-guide-readme.md`
4. `execution/scenario-quick-reference.md`

### If you already know Beacon a little

1. `execution/scenario-quick-reference.md`
2. `execution/command-reference.md`

### If you need cross-language sharing

1. `execution/command-reference-bilingual.md`

---

## Command docs map

| Document | Best for | What you get |
| --- | --- | --- |
| `USAGE.md` | Most users | End-to-end practical usage from draft/freeze to implement/reopen/release |
| `getting-started-10-minutes.md` | New users | A short guided walkthrough from install to release checks |
| `execution/command-guide-readme.md` | External users | README-style intro, top commands, common workflows |
| `execution/scenario-quick-reference.md` | Busy operators | “I need X, what command do I use?” lookup |
| `execution/command-reference.md` | Power users / maintainers | Full command tree, command families, hidden/advanced surfaces |
| `execution/command-reference-bilingual.md` | Mixed Chinese/English teams | Bilingual quick guide and scenario mapping |

---

## Quick “where should I start?” table

| Need | Start here |
| --- | --- |
| I want the full practical v1.1.7 usage path | `USAGE.md` |
| I want the shortest possible introduction | `getting-started-10-minutes.md` |
| I want a README-style overview | `execution/command-guide-readme.md` |
| I know the task, not the command | `execution/scenario-quick-reference.md` |
| I need the full CLI tree | `execution/command-reference.md` |
| I need English + Chinese in one page | `execution/command-reference-bilingual.md` |

---

## The 5 highest-value commands in v1.1.7

```bash
beacon ask "<goal>" --project-root . --version v1.1.7 --plan-only --json
beacon workflow start "<feature>" --project . --version v1.1.7
beacon doctor verify-materials --project-root . --version v1.1.7 --json
beacon gate check release --project-root . --version v1.1.7 --json
beacon release check v1.1.7 --project .
```

If you only remember one flow, remember this:

```text
ask → workflow start → think/user-story/prd/test-case → doctor → gate → release
```

## v1.1.7 project-skill fast lane

如果你的项目需要接入特定 skill / 特定验收工作流，先看这组命令：

```bash
beacon skill registry list --json
beacon profile create rolo rolo-uat --example rolo-uat --json
beacon skill bind "<feature>" --profile rolo-uat --version v1.1.7
beacon verify run "<feature>" --profile rolo-uat --json
beacon orchestrate run "<feature>" --profile rolo-uat --dry-run --json
```

这组命令用于：

- 注册 / 查看 multi-skill
- 为项目建立 profile
- 把 feature 绑定到项目 profile
- 让 Beacon 按 profile 执行项目特定 verify / orchestration

---

## Related v1.1.7 human-primary docs

- `USAGE.md`
- `SUMMARY.md`
- `release/v1.1.7.md`
- `execution/index.md`
- `execution/boundaries.md`

These should still be read before expanding `.machine/` or `.beacon/`.

## v1.1.7 lifecycle closure fast lane

```bash
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon implement run "<feature>" --project-root . --version v1.1.7 --runner native-team --json
beacon doctor advise --project-root . --version v1.1.7 --feature "<feature>" --json
beacon reopen "<feature>" --project-root . --version v1.1.7 --reason change-request
```
