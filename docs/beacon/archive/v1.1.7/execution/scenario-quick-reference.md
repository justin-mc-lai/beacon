# Beacon v1.1.7 Scenario Quick Reference

> Fast lookup sheet organized by operator intent.

---

## 1. I only know the goal, not the command

**Use first**

```bash
beacon ask "<goal>" --project-root . --version v1.1.7 --plan-only --json
```

**When to escalate**

- Want router internals / confidence / boundary reasoning:

```bash
beacon prompt optimize "<goal>" --project-root . --version v1.1.7 --json
```

---

## 2. I want to start a brand-new feature package

**Fast path**

```bash
beacon workflow start "<feature>" --project . --version v1.1.7
```

**Step-by-step path**

```bash
beacon think start "<feature>" --project . --version v1.1.7
beacon user-story create "<feature>" --project . --version v1.1.7
beacon prd create "<feature>" --project . --version v1.1.7
beacon test-case create "<feature>" --project . --version v1.1.7
```

Use this path when you want explicit checkpoints between requirement stages.

---

## 3. I need to continue an interrupted workflow

```bash
beacon status --board --project-root . --version v1.1.7
beacon resume continue --run-id <run-id> --project-root . --version v1.1.7 --auto --hud
```

If you do not know the run id yet:

```bash
beacon recall list --project-root .
beacon resume <run-id> --project-root . --version v1.1.7
```

---

## 4. I need to generate implementation output through an adapter

```bash
beacon skill list --json
beacon implement list-runners --json
beacon implement run "<feature>" --runner omx --project . --version v1.1.7 --json
```

Use `skill prefer` first if the project should default to a specific runner:

```bash
beacon skill prefer omx --project-root . --scope project
```

---

## 5. I need to repair an old package into the v1.1.7 layered layout

```bash
beacon doctor repair-package --project-root . --version v1.1.7 --json
```

Then immediately verify:

```bash
beacon doctor verify-materials --project-root . --version v1.1.7 --json
beacon doctor verify-delivery --project-root . --version v1.1.7 --json
```

Use this when you are moving execution / QA machine JSON into `.machine/`.

---

## 6. I need release readiness / gate evidence

```bash
beacon status --board --project-root . --version v1.1.7
beacon doctor verify-materials --project-root . --version v1.1.7 --json
beacon doctor verify-delivery --project-root . --version v1.1.7 --json
beacon gate check release --project-root . --version v1.1.7 --json
beacon release check v1.1.7 --project .
```

Use this exact pack before claiming release-ready.

---

## 7. I need to inspect source-of-truth / machine-surface state

```bash
beacon status --board --project-root . --version v1.1.7
```

What to read in the board:

- `source_of_truth.root`
- `source_of_truth.machine_root`
- `source_of_truth.formal_package_closure`
- `coverage.story/ac/tc`
- `memory.next_stage`

---

## 8. I need prompt routing diagnostics

```bash
beacon prompt catalog --project-root . --version v1.1.7 --json
beacon prompt optimize "<goal>" --project-root . --version v1.1.7 --json
beacon debug confidence show --project-root .
```

If you want router events persisted:

```bash
beacon debug enable --project-root .
beacon debug sync-prompts --project-root .
```

---

## 9. I need prototype work

```bash
beacon prototype create "<feature>" --project . --version v1.1.7
beacon prototype review "<feature>" --project . --version v1.1.7
beacon prototype freeze "<feature>" --project . --version v1.1.7
```

Use when UI visualization is part of the requirement chain.

---

## 10. I need post-implementation review

```bash
beacon review spec "<feature>" --project . --version v1.1.7 --json
beacon review quality "<feature>" --project . --version v1.1.7 --json
```

Use `spec` first for spec drift, then `quality` for release-quality posture.

---

## 11. I need memory / feedback closure

```bash
beacon feedback extract latest --project-root . --version v1.1.7 --json
beacon feedback apply latest --project-root . --version v1.1.7 --json
beacon remember add "<insight>" --project-root .
beacon recall memory "<query>" --project-root .
```

Use this when you want verification learnings reflected in future runs.

---

## 12. I need PM / analysis templates outside the core chain

**Preferred surface**

```bash
beacon labs analyze create "<topic>" --project . --version v1.1.7
beacon labs roadmap create "<topic>" --project . --version v1.1.7
beacon labs ui-spec create "<topic>" --project . --version v1.1.7
```

Use labs when the task is analytic or planning-heavy, not workflow closure.

---

## 13. I need team / bridge operations

**Preferred surface**

```bash
beacon bridge team start "<task>" --project .
beacon bridge run workflow --feature "<feature>" --project-root . --version v1.1.7
```

**Direct hidden aliases**

```bash
beacon team start "<task>" --project .
beacon run workflow --feature "<feature>" --project-root . --version v1.1.7
beacon ralph-bridge start "<task>" --project . --version v1.1.7
```

Use these only when you explicitly need bridge/runtime collaboration flows.

---

## 14. Shortest “what should I use?” table

| Scenario | Command shortlist |
| --- | --- |
| Natural-language planning | `ask`, `prompt optimize` |
| New requirement package | `workflow start`, `think`, `user-story`, `prd`, `test-case` |
| Implementation execution | `skill list`, `implement list-runners`, `implement run` |
| Package repair / migration | `doctor repair-package` |
| Materials verification | `doctor verify-materials` |
| Delivery verification | `doctor verify-delivery` |
| Release gate | `gate check release`, `release check` |
| Prototype work | `prototype create/review/freeze` |
| Prompt router debug | `prompt catalog`, `debug confidence`, `debug sync-prompts` |
| Memory closure | `feedback`, `remember`, `recall` |
| PM / research templates | `labs ...` |
| Team / bridge runtime | `bridge ...`, `team`, `ralph-bridge` |

---

## 15. Recommended v1.1.7 reading order for operators

1. `docs/beacon/archive/v1.1.7/SUMMARY.md`
2. `docs/beacon/archive/v1.1.7/execution/index.md`
3. `docs/beacon/archive/v1.1.7/execution/command-reference.md`
4. `docs/beacon/archive/v1.1.7/execution/scenario-quick-reference.md`
5. Only then expand `.machine/` and `.beacon/` when audit/debug/gate needs it

## I need lifecycle closure / freeze / reopen guidance

```bash
beacon help --project-root . --version v1.1.7 --feature "<feature>" --json
beacon doctor advise --project-root . --version v1.1.7 --feature "<feature>" --json
beacon freeze "<feature>" --project-root . --version v1.1.7
beacon reopen "<feature>" --project-root . --version v1.1.7 --reason change-request
beacon implement run "<feature>" --project . --version v1.1.7 --runner native-team --json
```

## I need project-specific verify / orchestration

```bash
beacon skill registry list --json
beacon profile create rolo rolo-uat --example rolo-uat --json
beacon skill bind "<feature>" --profile rolo-uat --version v1.1.7
beacon verify run "<feature>" --project . --version v1.1.7 --profile rolo-uat --json
beacon orchestrate run "<feature>" --project . --version v1.1.7 --profile rolo-uat --dry-run --json
```
