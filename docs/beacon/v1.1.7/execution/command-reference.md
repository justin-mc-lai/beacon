# Beacon v1.1.7 Command Reference

> Human-primary operator guide for the Beacon v1.1.7 CLI surface.

---

## 1. Recommended usage style in v1.1.7

- Default entrypoint: `beacon <subcommand>`
- Package version / runtime line: `v1.1.7`
- Formal docs source of truth: `docs/beacon/v1.1.7/`
- Governance / audit commands usually prefer `--project-root .`
- Workflow / material generation commands usually prefer `--project .`
- For release-sensitive operations, explicitly pin `--version v1.1.7`
- Prefer:
  - `beacon labs <command>` over hidden direct lab aliases
  - `beacon bridge <command>` over hidden direct bridge aliases
  - `beacon ask` over direct `prompt` unless you need router internals

---

## 2. Full command tree

```text
beacon
├─ ask
├─ resume
├─ profile
│  ├─ create
│  └─ show
├─ doctor
│  ├─ diagnose
│  ├─ setup
│  ├─ uninstall
│  ├─ setup-context
│  ├─ verify-context
│  ├─ verify-materials
│  ├─ verify-delivery
│  ├─ repair-package
│  ├─ verify-config
│  ├─ verify-git-alignment
│  ├─ setup-agent-md
│  └─ verify-agent-md
├─ gate
│  ├─ list
│  ├─ check
│  ├─ config
│  ├─ status
│  ├─ think
│  ├─ user-story
│  ├─ prd
│  ├─ test-case
│  ├─ prototype
│  └─ release
├─ init
│  ├─ run
│  └─ init-project
├─ status
│  └─ show-status
├─ report
│  ├─ generate
│  └─ acceptance-audit
├─ review
│  ├─ spec
│  ├─ quality
│  └─ accept
├─ skill
│  ├─ detect
│  ├─ list
│  ├─ show
│  ├─ register
│  ├─ prefer
│  ├─ bind
│  ├─ doctor
│  └─ registry
│     └─ list
├─ implement
│  ├─ list-runners
│  ├─ run
│  └─ status
├─ verify
│  └─ run
├─ orchestrate
│  └─ run
├─ debug
│  ├─ watch
│  ├─ status
│  ├─ enable
│  ├─ disable
│  ├─ sync-prompts
│  ├─ capture
│  └─ confidence
│     ├─ show
│     └─ set
├─ feedback
│  ├─ extract
│  ├─ apply
│  └─ sync
├─ think
│  ├─ start
│  ├─ status
│  ├─ confirm
│  ├─ question
│  ├─ conflict
│  └─ summarize
├─ user-story
│  ├─ create
│  └─ list
├─ prd
│  ├─ create
│  └─ list
├─ test-case
│  ├─ create
│  ├─ list
│  └─ gate
├─ workflow
│  ├─ start
│  ├─ continue
│  ├─ hud
│  ├─ status
│  ├─ gate
│  └─ run
├─ version
│  ├─ create
│  └─ list
├─ evolution-summary
│  ├─ create
│  └─ list
├─ auto-test
│  ├─ create
│  ├─ status
│  └─ import-qa-use
├─ test-progress
│  ├─ show
│  ├─ update
│  └─ sync
├─ release
│  ├─ create
│  └─ check
├─ prototype
│  ├─ create
│  ├─ preview
│  ├─ review
│  ├─ freeze
│  ├─ status
│  └─ list
├─ recall
│  ├─ run
│  ├─ list
│  └─ memory
├─ remember
│  ├─ add
│  ├─ search
│  └─ list
├─ labs
│  ├─ analyze
│  │  ├─ create
│  │  └─ list
│  ├─ api-design
│  │  ├─ create
│  │  └─ list
│  ├─ brainstorm
│  │  ├─ create
│  │  └─ list
│  ├─ data-dictionary
│  │  ├─ create
│  │  └─ list
│  ├─ design
│  │  ├─ create
│  │  └─ list
│  ├─ jtbd
│  │  ├─ create
│  │  └─ list
│  ├─ kano
│  │  ├─ create
│  │  └─ list
│  ├─ moscow
│  │  ├─ create
│  │  └─ list
│  ├─ persona
│  │  ├─ create
│  │  └─ list
│  ├─ roadmap
│  │  ├─ create
│  │  └─ list
│  ├─ ui-spec
│  │  ├─ create
│  │  └─ list
│  └─ wireframe
│     ├─ create
│     └─ list
├─ bridge
│  ├─ run
│  ├─ team
│  └─ ralph
├─ prompt               (hidden / advanced)
│  ├─ optimize
│  └─ catalog
├─ run                  (hidden / bridge direct alias)
│  └─ workflow
├─ team                 (hidden / bridge direct alias)
│  ├─ start
│  ├─ status
│  ├─ advance
│  ├─ review
│  ├─ evaluate
│  ├─ stop
│  ├─ report
│  └─ list
├─ ralph-bridge         (hidden / bridge direct alias)
│  ├─ start
│  ├─ status
│  └─ stop
├─ analyze              (hidden / direct labs alias)
├─ api-design           (hidden / direct labs alias)
├─ brainstorm           (hidden / direct labs alias)
├─ data-dictionary      (hidden / direct labs alias)
├─ design               (hidden / direct labs alias)
├─ jtbd                 (hidden / direct labs alias)
├─ kano                 (hidden / direct labs alias)
├─ moscow               (hidden / direct labs alias)
├─ persona              (hidden / direct labs alias)
├─ roadmap              (hidden / direct labs alias)
├─ ui-spec              (hidden / direct labs alias)
├─ wireframe            (hidden / direct labs alias)
├─ save                 (hidden / compatibility)
│  └─ run
└─ work                 (hidden / compatibility alias of workflow start)
```

---

## 3. Command families

### 3.1 Core workflow surface

#### `beacon ask`
- 用途：自然语言入口；默认只出 plan，不直接执行。
- 适合：用户还没有明确命令，只知道目标。
- 常用示例：
  - `beacon ask "梳理 Beacon v1.1.7 人机分层交付闭环" --project-root . --version v1.1.7 --plan-only --json`
  - `beacon ask "生成用户故事并给出验收标准" --project-root . --version v1.1.7 --execute --json`

#### `beacon think`
- 用途：需求澄清、事实确认、问题与冲突沉淀。
- 主要子命令：`start` `status` `confirm` `question` `conflict` `summarize`
- 常用示例：
  - `beacon think start "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`
  - `beacon think status --project . --version v1.1.7`
  - `beacon think summarize "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`

#### `beacon user-story`
- 用途：生成和查看用户故事。
- 子命令：`create` `list`
- 常用示例：
  - `beacon user-story create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`
  - `beacon user-story list --project . --version v1.1.7`

#### `beacon prd`
- 用途：生成和查看 PRD。
- 子命令：`create` `list`
- 常用示例：
  - `beacon prd create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`
  - `beacon prd list --project . --version v1.1.7`

#### `beacon prototype`
- 用途：静态单页原型生命周期管理。
- 子命令：`create` `preview` `review` `freeze` `status` `list`
- 常用示例：
  - `beacon prototype create "Beacon dashboard prototype" --project . --version v1.1.7`
  - `beacon prototype review "Beacon dashboard prototype" --project . --version v1.1.7`
  - `beacon prototype freeze "Beacon dashboard prototype" --project . --version v1.1.7`

#### `beacon test-case`
- 用途：生成测试用例、人类可读测试说明和机器可执行 AC matrix。
- 子命令：`create` `list` `gate`
- 常用示例：
  - `beacon test-case create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`
  - `beacon test-case gate "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`

#### `beacon workflow`
- 用途：编排完整主链。
- 子命令：`start` `continue` `hud` `status` `gate` `run`
- 常用示例：
  - `beacon workflow start "Beacon v1.1.7 layered delivery" --project . --version v1.1.7`
  - `beacon workflow continue --project . --version v1.1.7 --auto --interactive --hud`
  - `beacon workflow status --project . --version v1.1.7`

#### `beacon auto-test`
- 用途：统一自动测试证据生成与导入。
- 子命令：`create` `status` `import-qa-use`
- 常用示例：
  - `beacon auto-test create "Beacon v1.1.7 release smoke" --project . --version v1.1.7`
  - `beacon auto-test status --project . --version v1.1.7`

#### `beacon gate`
- 用途：阶段 gate、release gate、QA policy 检查。
- 子命令：`list` `check` `config` `status` + stage aliases
- 常用示例：
  - `beacon gate check release --project-root . --version v1.1.7 --json`
  - `beacon gate check test-case --project-root . --version v1.1.7 --json`
  - `beacon gate status --project-root . --version v1.1.7`

#### `beacon release`
- 用途：release checklist 生成与 readiness 检查。
- 子命令：`create` `check`
- 常用示例：
  - `beacon release create v1.1.7 --project .`
  - `beacon release check v1.1.7 --project .`

---

### 3.2 Governance / support surface

#### `beacon doctor`
- 用途：环境、上下文、交付工件、git 对齐、版本迁移修复。
- 关键子命令：
  - `setup-context` / `verify-context`
  - `verify-materials` / `verify-delivery`
  - `repair-package`
  - `verify-config` / `verify-git-alignment`
- 常用示例：
  - `beacon doctor --project-root . --json`
  - `beacon doctor setup-context --project-root .`
  - `beacon doctor verify-context --project-root . --strict`
  - `beacon doctor verify-materials --project-root . --version v1.1.7 --json`
  - `beacon doctor verify-delivery --project-root . --version v1.1.7 --json`
  - `beacon doctor repair-package --project-root . --version v1.1.7 --json`

#### `beacon init`
- 用途：初始化 Beacon 项目结构与上下文块。
- 子命令：`run` `init-project`
- 常用示例：
  - `beacon init --project-root . --version v1.1.7 --apply`
  - `beacon init run --project . --version v1.1.7 --apply`

#### `beacon status`
- 用途：查看 workflow、memory、coverage、source-of-truth 状态。
- 子命令：`show-status`
- 常用示例：
  - `beacon status --board --project-root . --version v1.1.7`
  - `beacon status --project-root . --version v1.1.7 --run-id <run-id>`

#### `beacon report`
- 用途：生成人类/机器报告与 acceptance audit。
- 子命令：`generate` `acceptance-audit`
- 常用示例：
  - `beacon report --machine latest --project-root . --version v1.1.7`
  - `beacon report latest acceptance-audit --project-root . --version v1.1.7 --feature beacon-human-machine-artifact-layering --write`

#### `beacon review`
- 用途：实现后 review。
- 子命令：`spec` `quality`
- 常用示例：
  - `beacon review spec "Beacon v1.1.7 layered delivery" --project . --version v1.1.7 --json`
  - `beacon review quality "Beacon v1.1.7 layered delivery" --project . --version v1.1.7 --json`

#### `beacon skill`
- 用途：实现 runner / adapter 注册与诊断。
- 子命令：`detect` `list` `show` `register` `prefer` `doctor`
- 常用示例：
  - `beacon skill list --json`
  - `beacon skill detect --project-root . --json`
  - `beacon skill prefer omx --project-root . --scope project`
  - `beacon skill doctor --project-root . --json`

#### `beacon implement`
- 用途：通过 skill adapter 执行实现阶段。
- 子命令：`list-runners` `run` `status`
- 常用示例：
  - `beacon implement list-runners --json`
  - `beacon implement run "Beacon layered delivery" --runner omx --project . --version v1.1.7 --json`
  - `beacon implement status --project-root . --version v1.1.7`

#### `beacon resume`
- 用途：恢复 / 继续 run 或 workflow。
- 主要模式：`resume <run_id>` / `resume continue` / `resume restore`
- 常用示例：
  - `beacon resume <run-id> --project-root . --version v1.1.7`
  - `beacon resume continue --run-id <run-id> --project-root . --version v1.1.7 --auto --hud`

#### `beacon debug`
- 用途：prompt router 调试、debug mode、置信度阈值管理。
- 子命令：`watch` `status` `enable` `disable` `sync-prompts` `capture` `confidence show/set`
- 常用示例：
  - `beacon debug enable --project-root .`
  - `beacon debug status --project-root .`
  - `beacon debug sync-prompts --project-root .`
  - `beacon debug confidence show --project-root .`
  - `beacon debug confidence set 0.68 --project-root .`

#### `beacon feedback`
- 用途：把验证反馈吸收进 memory。
- 子命令：`extract` `apply` `sync`
- 常用示例：
  - `beacon feedback extract latest --project-root . --version v1.1.7 --json`
  - `beacon feedback apply latest --project-root . --version v1.1.7 --json`
  - `beacon feedback sync latest --project-root .`

#### `beacon remember`
- 用途：写入 memory。
- 子命令：`add` `search` `list`
- 常用示例：
  - `beacon remember add "v1.1.7 uses .machine as machine secondary surface" --project-root .`
  - `beacon remember search ".machine" --project-root .`

#### `beacon recall`
- 用途：恢复 session 或查询 memory。
- 子命令：`run` `list` `memory`
- 常用示例：
  - `beacon recall list --project-root .`
  - `beacon recall memory ".machine" --project-root .`

#### `beacon version`
- 用途：版本规划与版本工件追踪。
- 子命令：`create` `list`
- 常用示例：
  - `beacon version create "Beacon v1.1.7 rollout" --project . --version v1.1.7`
  - `beacon version list --project .`

#### `beacon evolution-summary`
- 用途：从真实 run / memory / evidence 生成版本演进总结。
- 子命令：`create` `list`
- 常用示例：
  - `beacon evolution-summary create "Beacon v1.1.7" --project . --version v1.1.7`
  - `beacon evolution-summary list --project . --version v1.1.7`

#### `beacon test-progress`
- 用途：跟踪测试进度。
- 子命令：`show` `update` `sync`
- 常用示例：
  - `beacon test-progress show --project-root . --version v1.1.7`
  - `beacon test-progress sync --project-root . --version v1.1.7`

---

### 3.3 Labs surface

> 推荐调用方式：`beacon labs <command>`

#### `beacon labs analyze`
- 用途：竞品分析
- 子命令：`create` `list`
- 示例：
  - `beacon labs analyze create "Beacon vs OpenSpec vs GSD" --project . --version v1.1.7`

#### `beacon labs api-design`
- 用途：API 设计文档
- 示例：
  - `beacon labs api-design create "Implementation runner contract" --project . --version v1.1.7`

#### `beacon labs brainstorm`
- 用途：发散式问题探索
- 示例：
  - `beacon labs brainstorm create "Beacon human/machine layering follow-ups" --project . --version v1.1.7`

#### `beacon labs data-dictionary`
- 用途：数据字典
- 示例：
  - `beacon labs data-dictionary create "Beacon memory schema" --project . --version v1.1.7`

#### `beacon labs design`
- 用途：Design Thinking 文档
- 示例：
  - `beacon labs design create "Beacon operator experience" --project . --version v1.1.7`

#### `beacon labs jtbd`
- 用途：JTBD 分析
- 示例：
  - `beacon labs jtbd create "Why teams adopt Beacon" --project . --version v1.1.7`

#### `beacon labs kano`
- 用途：KANO 分类
- 示例：
  - `beacon labs kano create "Beacon release readiness features" --project . --version v1.1.7`

#### `beacon labs moscow`
- 用途：MoSCoW 优先级
- 示例：
  - `beacon labs moscow create "Beacon v1.1.7 roadmap scope" --project . --version v1.1.7`

#### `beacon labs persona`
- 用途：用户画像
- 示例：
  - `beacon labs persona create "Beacon release operator" --project . --version v1.1.7`

#### `beacon labs roadmap`
- 用途：产品路线图
- 示例：
  - `beacon labs roadmap create "Beacon v1.2.x planning" --project . --version v1.1.7`

#### `beacon labs ui-spec`
- 用途：UI 设计规范
- 示例：
  - `beacon labs ui-spec create "Prototype shell spec" --project . --version v1.1.7`

#### `beacon labs wireframe`
- 用途：线框图/页面结构说明
- 示例：
  - `beacon labs wireframe create "Operator dashboard layout" --project . --version v1.1.7`

---

### 3.4 Bridge / hidden / compatibility surface

#### `beacon bridge`
- 用途：承载 bridge/runtime 高级入口。
- 子命令：`run` `team` `ralph`
- 常用示例：
  - `beacon bridge run workflow --project-root . --version v1.1.7`
  - `beacon bridge team start "Beacon v1.1.7 rollout" --project .`

#### `beacon prompt`
- 用途：直接查看 router plan 和 router contract。
- 子命令：`optimize` `catalog`
- 常用示例：
  - `beacon prompt catalog --project-root . --version v1.1.7 --json`
  - `beacon prompt optimize "帮我梳理 Beacon v1.1.7 特性" --project-root . --version v1.1.7 --json`

#### `beacon run`
- 用途：bridge direct alias；统一运行 workflow/team/auto-test 风格任务。
- 子命令：`workflow`
- 常用示例：
  - `beacon run workflow --feature "Beacon v1.1.7 rollout" --project-root . --version v1.1.7 --json`

#### `beacon team`
- 用途：team 协作状态机；推荐高级场景使用。
- 子命令：`start` `status` `advance` `review` `evaluate` `stop` `report` `list`
- 常用示例：
  - `beacon team start "Beacon v1.1.7 rollout" --runtime tmux --project .`
  - `beacon team status --project-root .`
  - `beacon team report --project-root . --json`

#### `beacon ralph-bridge`
- 用途：Ralph/OMC bridge。
- 子命令：`start` `status` `stop`
- 常用示例：
  - `beacon ralph-bridge start "Beacon rollout" --project . --version v1.1.7`

#### Hidden direct lab aliases

下面这些命令等价于 `beacon labs <command>`，通常只在脚本兼容或熟悉内部 surface 时使用：

- `beacon analyze`
- `beacon api-design`
- `beacon brainstorm`
- `beacon data-dictionary`
- `beacon design`
- `beacon jtbd`
- `beacon kano`
- `beacon moscow`
- `beacon persona`
- `beacon roadmap`
- `beacon ui-spec`
- `beacon wireframe`

示例：

- `beacon analyze create "Beacon vs OpenSpec vs GSD" --project . --version v1.1.7`
- `beacon roadmap list --project . --version v1.1.7`

#### `beacon save`
- 用途：兼容保存当前 session。
- 子命令：`run`
- 常用示例：
  - `beacon save run --project-root .`

#### `beacon work`
- 用途：`workflow start` 的兼容别名。
- 常用示例：
  - `beacon work "Beacon v1.1.7 layered delivery" --project . --version v1.1.7 --auto`

---

## 4. Minimal recommended v1.1.7 command packs

### 4.1 Start a new requirement

```bash
beacon workflow start "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon think start "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon user-story create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon prd create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
beacon test-case create "Beacon v1.1.7 layered delivery" --project . --version v1.1.7
```

### 4.2 Prepare implementation

```bash
beacon skill list --json
beacon implement list-runners --json
beacon implement run "Beacon layered delivery" --runner omx --project . --version v1.1.7 --json
```

### 4.3 Repair / validate a release package

```bash
beacon doctor repair-package --project-root . --version v1.1.7 --json
beacon doctor verify-materials --project-root . --version v1.1.7 --json
beacon doctor verify-delivery --project-root . --version v1.1.7 --json
beacon gate check release --project-root . --version v1.1.7 --json
beacon release check v1.1.7 --project .
```

### 4.4 Debug prompt routing

```bash
beacon prompt catalog --project-root . --version v1.1.7 --json
beacon prompt optimize "帮我梳理 Beacon v1.1.7 命令能力" --project-root . --version v1.1.7 --json
beacon debug confidence show --project-root .
```

## 5. v1.1.7 lifecycle-native commands

- `beacon help --project-root . --version v1.1.7 --feature "<feature>" --json`
- `beacon doctor advise --project-root . --version v1.1.7 --feature "<feature>" --json`
- `beacon freeze "<feature>" --project-root . --version v1.1.7`
- `beacon reopen "<feature>" --project-root . --version v1.1.7 --reason change-request`
- `beacon implement run "<feature>" --project . --version v1.1.7 --runner native-single --json`
- `beacon implement run "<feature>" --project . --version v1.1.7 --runner native-team --json`
- `beacon review accept "<feature>" --project . --version v1.1.7 --json`

## 5.1 v1.1.7 project-skill commands

- `beacon skill registry list --json`
- `beacon profile create rolo rolo-uat --example rolo-uat --json`
- `beacon profile show rolo-uat --json`
- `beacon skill bind "<feature>" --profile rolo-uat --version v1.1.7`
- `beacon verify run "<feature>" --project . --version v1.1.7 --profile rolo-uat --json`
- `beacon orchestrate run "<feature>" --project . --version v1.1.7 --profile rolo-uat --dry-run --json`
