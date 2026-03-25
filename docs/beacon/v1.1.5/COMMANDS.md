# Beacon v1.1.5 Commands Hub

> Top-level navigation entry for all human-facing command docs in Beacon v1.1.5.

---

## What this page is for

This page is the **single human-primary entrypoint** for command usage in Beacon v1.1.5.

Use it when you want to:

- find the right command doc fast
- choose the right level of detail
- jump from “I am new” to “I need the full command tree”
- move from external-user docs to operator docs without reading `.machine/`

---

## Recommended reading order

### If you are brand new

1. `getting-started-10-minutes.md`
2. `execution/command-guide-readme.md`
3. `execution/scenario-quick-reference.md`

### If you already know Beacon a little

1. `execution/scenario-quick-reference.md`
2. `execution/command-reference.md`

### If you need cross-language sharing

1. `execution/command-reference-bilingual.md`

---

## Command docs map

| Document | Best for | What you get |
| --- | --- | --- |
| `getting-started-10-minutes.md` | New users | A short guided walkthrough from install to release checks |
| `execution/command-guide-readme.md` | External users | README-style intro, top commands, common workflows |
| `execution/scenario-quick-reference.md` | Busy operators | “I need X, what command do I use?” lookup |
| `execution/command-reference.md` | Power users / maintainers | Full command tree, command families, hidden/advanced surfaces |
| `execution/command-reference-bilingual.md` | Mixed Chinese/English teams | Bilingual quick guide and scenario mapping |

---

## Quick “where should I start?” table

| Need | Start here |
| --- | --- |
| I want the shortest possible introduction | `getting-started-10-minutes.md` |
| I want a README-style overview | `execution/command-guide-readme.md` |
| I know the task, not the command | `execution/scenario-quick-reference.md` |
| I need the full CLI tree | `execution/command-reference.md` |
| I need English + Chinese in one page | `execution/command-reference-bilingual.md` |

---

## The 5 highest-value commands in v1.1.5

```bash
beacon ask "<goal>" --project-root . --version v1.1.5 --plan-only --json
beacon workflow start "<feature>" --project . --version v1.1.5
beacon doctor verify-materials --project-root . --version v1.1.5 --json
beacon gate check release --project-root . --version v1.1.5 --json
beacon release check v1.1.5 --project .
```

If you only remember one flow, remember this:

```text
ask → workflow start → think/user-story/prd/test-case → doctor → gate → release
```

---

## Related v1.1.5 human-primary docs

- `SUMMARY.md`
- `release/v1.1.5.md`
- `execution/index.md`
- `execution/boundaries.md`

These should still be read before expanding `.machine/` or `.beacon/`.
