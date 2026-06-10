# 测试：Beacon Loop Native Runner and Automation Retirement

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-001 | contract | `beacon --help` / command catalog tests | `automation` 不再作为 active command surface 暴露；如有 stub，只能阻断并提示 `beacon-loop goal`。 |
| AC-001 | TC-002 | negative | `rg "beacon-automation-queue|beacon-hourly-qa|repair-window" beacon automation tests` | 旧 automation queue/job/launchd 业务入口被删除或不再被 active tests/docs 引导。 |
| AC-002 | TC-003 | package | `cd packages/beacon-loop && npm run build` | `packages/beacon-loop` 能构建独立 `beacon-loop` CLI。 |
| AC-003 | TC-004 | contract | `beacon-loop --help` | help 只暴露 `goal`，不暴露 `lfg`。 |
| AC-003 | TC-005 | negative | `beacon-loop lfg "x"` | `lfg` 不是可执行 alias、deprecated alias 或 compatibility route。 |
| AC-004 | TC-006 | integration | `beacon-loop goal "<goal>" --dry-run --json` | run package 包含 `beacon truth-map resolve ... --json` 的 resolver refs。 |
| AC-005 | TC-007 | negative | `beacon-loop goal "<missing-feature>" --json` | feature package 缺失或 resolver blocked 时 fail closed，并推荐 `beacon-gen-change`。 |
| AC-006 | TC-008 | integration | `beacon-loop goal "<goal>" --dry-run --json` | 创建 `.beacon/loop/runs/<run-id>/run-package.json`、`prompt.md`、`notes.md`、`output-schema.json`、`evidence.json` 和 `summary.md`。 |
| AC-007 | TC-009 | negative | dirty worktree fixture | 默认 dirty worktree 阻断；未显式 controlled mode 时不启动 agent loop。 |
| AC-008 | TC-010 | runner | mocked agent success/failure tests | success iteration commit；failure iteration rollback；commit failure 保留 repair state。 |
| AC-009 | TC-011 | runner | `beacon-loop resume <run-id> --json` | resume 读取既有 run metadata、notes 和 branch/worktree 状态继续，而不是新建无关 run。 |
| AC-010 | TC-012 | integration | `beacon-loop import-evidence <run-id> --json` | 调用 Beacon implementation evidence import，并记录 source refs、summary refs 和 changed files/services。 |
| AC-011 | TC-013 | negative | inspect `beacon-loop` result payloads | `beacon-loop` 不输出 QA pass、release ready 或 feature complete verdict。 |
| AC-012 | TC-014 | docs | `rg "beacon-loop lfg|\\blfg\\b" docs beacon packages tests` | active docs/help/tests/command catalog 不出现 `lfg` route；只允许本 feature truth 中的禁止性说明。 |
| AC-013 | TC-015 | test-suite | focused pytest/npm tests | 旧 automation tests 被移除或改为 retirement negative tests；新增 `beacon-loop` build、CLI、runner、evidence tests。 |
| AC-014 | TC-016 | contract | inspect run artifacts | `.beacon/loop/runs/**` artifacts 标记 runtime process record，不写 `.machine` requirement projection。 |
| AC-015 | TC-017 | CLI | `beacon-loop doctor --json` | doctor 检查 Beacon CLI、Node runtime、agent backend、git/worktree 和 evidence import prerequisites。 |

## 验证说明

本测试包只定义 acceptance coverage。`beacon-loop` 的 runtime artifacts 不能替代 `features/<slug>/{truth,tests,tasks,evidence}.md`，也不能替代 Beacon QA/release verdict。
