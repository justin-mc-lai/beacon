# Beacon CLI

> Evidence-first Product Workflow Kernel. Beacon 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环。

[![PyPI version](https://img.shields.io/pypi/v/beacon)](https://pypi.org/project/beacon/)
[![Python](https://img.shields.io/pypi/pyversions/beacon)](https://pypi.org/project/beacon/)

---

## 1. 当前版本是什么

Beacon 当前运行时发布口径是 **v1.4.5**。

> 当前发布线：`v1.4.5`

- **CLI 入口**：`beacon <subcommand>`
- **标准 skill 包**：`skills/beacon/`
- **当前包版本**：`1.4.5`
- **最新已接受文档线**：`v1.4.5`
- **文档主源**：`docs/beacon/<version>/`
- **状态目录**：`.beacon/`

当前主口径：

- `docs/beacon/` 是唯一维护的信息源
- `.beacon/` 是运行时状态，不替代正式交付文档
- 新生成的 AGENTS / CLAUDE managed block 也遵循以上口径
- 当前发布请优先以 `docs/beacon/v1.4.5/` 为准
- 当前架构、命令与 release 说明统一以 `docs/beacon/v1.4.5/` 为准

如果你只记一条：

> **Beacon 现在是 v1.4.5，写文档看 `docs/beacon/v1.4.5/`，执行命令用 `beacon <subcommand>`。**

---

## 2. 当前能力边界

### In scope

- 需求主链编排：`prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- 证据与放行治理：`doctor`、`gate`、`release`、`report`
- 历史 truth 隔离与治理：`archive`
- 版本化 requirement materials：`docs/beacon/<version>/`
- 主机侧帮助与导航：`help`、`status`、`doctor`、`archive`
- Codex HUD 接线与诊断：`debug codex-fixed-hud`、`doctor setup-codex-hud-hook`、`doctor verify-codex-hud-hook`

### Out of scope

- 直接替代业务代码实现
- 直接替代生产运维 / 发布平台
- 在 core surface 中公开 team / Ralph / bridge 细节
- 把外部 skill runner 当作默认 onboarding 路径

### v1.3.9 为什么重要

`v1.3.9` 把 Beacon 的公开 runtime line 正式提升到新的 current release，并把 truth lifecycle governance 收口到同一条发布线：

- runtime truth 已提升到 `v1.3.9`
- PRD executable diagram truth 已进入规划与 gate 推理面
- implement prompt boundary verdict 已进入 gate / release 闭环
- `archive` 已成为正式 support command 与 host-visible skill
- `skills/beacon/`、managed context、release docs 统一收敛到同一公开版本线

当前推荐阅读顺序：

- `docs/beacon/v1.3.9/SUMMARY.md`
- `docs/beacon/v1.3.9/execution/index.md`
- `docs/beacon/v1.3.9/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.9/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.3.9/execution/boundaries.md`
- `docs/beacon/v1.3.9/release/v1.3.9.md`

---

## 3. 当前推荐命令

### 安装

```bash
pip install beacon
# 或
cd beacon && pip install -e ".[dev]"
```

### Host 安装矩阵

Beacon 的安装分两层：

- CLI / Python 包：`beacon`
- host-visible skills：按宿主类型挂到统一 skill 根或 project-local agent surface

CLI 安装：

```bash
pip install beacon
# 或
cd beacon && pip install -e ".[dev]"
```

host-visible skills 安装必须遵守单一技能根约束，否则会出现：

- Beacon 公共 skill 重复发现
- Codex picker 同名 skill 成对出现
- 安装源漂移到旧副本
- 把 `beacon-change` 误解成 `beacon change` CLI 子命令

统一 host matrix：

| Host | 安装模式 | Canonical Root | 安装命令 | 校验命令 |
|------|----------|----------------|----------|----------|
| Codex / agent | 全局 symlink | `~/.agents/skills/beacon -> <repo>/skills/beacon` | `ln -sfn <repo>/skills/beacon ~/.agents/skills/beacon` | `find ~/.agents/skills/beacon -maxdepth 2 -name SKILL.md \| sort` |
| Claude Code 主 skill | 全局 symlink | `~/.claude/skills/beacon -> <repo>` | `ln -sfn <repo> ~/.claude/skills/beacon` | `readlink ~/.claude/skills/beacon` |
| Claude Code 子 skills | 全局 symlink | `~/.claude/skills/beacon-* -> <repo>/skills/beacon/<subskill>` | 由 Beacon repo 安装布局提供 | `find ~/.claude/skills -maxdepth 1 -name 'beacon-*' \| sort` |
| Trae | project-local agent surface | `<project>/.trae/skills/` | `beacon doctor setup-agent-surface --project-root <project> --agent trae` | `beacon doctor verify-agent-surface --project-root <project> --agent trae --strict` |
| Cursor | project-local agent surface | `<project>/.cursor/skills/` | `beacon doctor setup-agent-surface --project-root <project> --agent cursor` | `beacon doctor verify-agent-surface --project-root <project> --agent cursor --strict` |
| Windsurf | project-local agent surface | `<project>/.windsurf/skills/` | `beacon doctor setup-agent-surface --project-root <project> --agent windsurf` | `beacon doctor verify-agent-surface --project-root <project> --agent windsurf --strict` |

### 全局安装约束

当前唯一允许的安装口径：

- Beacon skill 源：
  - `<repo>/skills/beacon/`
- Codex / agent 发现根：
  - `~/.agents/skills/beacon -> <repo>/skills/beacon`
- Claude Code 主 skill：
  - `~/.claude/skills/beacon -> <repo>`
- Claude Code 子 skills：
  - `~/.claude/skills/beacon-* -> <repo>/skills/beacon/<subskill>`
- project-local agent surfaces：
  - Trae: `<project>/.trae/skills/`
  - Cursor: `<project>/.cursor/skills/`
  - Windsurf: `<project>/.windsurf/skills/`

明确禁止：

- `~/.codex/skills/beacon`
- `~/.codex/skills/beacon/skills/beacon`
- 同时存在多个 `name: beacon` 的本地副本或历史备份链接

推荐清理并重装：

```bash
rm -rf ~/.codex/skills/beacon
rm -f ~/.agents/skills/beacon
rm -f ~/.claude/skills/beacon
mkdir -p ~/.agents/skills
mkdir -p ~/.claude/skills
ln -sf /absolute/path/to/beacon/skills/beacon ~/.agents/skills/beacon
ln -sf /absolute/path/to/beacon ~/.claude/skills/beacon
```

安装后校验：

```bash
beacon --version
beacon --help
find ~/.agents/skills/beacon -maxdepth 2 -name SKILL.md | sort
readlink ~/.claude/skills/beacon
beacon doctor verify-agent-surface --project-root . --agent windsurf --strict
```

如果你看到 `Beacon Change` 这个 host skill，请记住：

- `beacon-change` 是宿主 skill 路由名
- CLI 对应动作仍然是 `beacon reopen ...`
- Beacon 不提供 `beacon change ...` 一级子命令

### 当前推荐命令风格

```bash
beacon <subcommand> ...
```

### Quick Start / 30-second path

如果你只想用最短路径快速跑通 Beacon v1.4.5，先执行：

```bash
beacon help --project-root . --version v1.4.5 --feature "<feature>" --json
beacon prd bootstrap "<feature>" --project-root . --version v1.4.5 --dry-run --json
beacon implement plan "<feature>" --project . --version v1.4.5 --json
beacon qa run "<feature>" --project . --version v1.4.5 --json
beacon gate check release --project-root . --version v1.4.5 --json
beacon release check v1.4.5 --project .
```

### Compatibility Entry Points

以下入口仍保留给兼容性与文档示例使用：

```bash
beacon workflow start "<feature>" --version v1.4.5 --project-root .
beacon think start "<feature>" --project-root . --version v1.4.5
beacon ask "请生成用户故事并给出验收标准" --project-root . --json
```

### Codex HUD Hook

用 doctor 托管 Codex HUD，而不是手工改散落配置：

```bash
beacon doctor setup-codex-hud-hook --project-root . --version v1.4.5 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.4.5 --json
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.4.5"}' \
  | beacon debug codex-fixed-hud --project-root . --version v1.4.5 --json
```

### Command Docs / 命令文档入口

- `docs/beacon/v1.4.5/SUMMARY.md`
- `docs/beacon/v1.4.5/execution/index.md`
- `docs/beacon/v1.4.5/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.5/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.4.5/execution/boundaries.md`
- `docs/beacon/v1.4.5/release/v1.4.5.md`

---

## 4. 当前交付工件

当前 release line 的正式工件：

- `docs/beacon/v1.4.5/SUMMARY.md`
- `docs/beacon/v1.4.5/prd/`
- `docs/beacon/v1.4.5/user-story/`
- `docs/beacon/v1.4.5/qa/test-cases/`
- `docs/beacon/v1.4.5/execution/`
- `docs/beacon/v1.4.5/release/v1.4.5.md`

当前 HUD/doctor 相关状态输出：

- `.beacon/state/hud-hook/setup-codex-hud-hook.json`
- `.beacon/state/hud-hook/verify-codex-hud-hook.json`
- `.beacon/debug/`

标准打包入口：

- `skills/beacon/`
- `.claude-plugin/plugin.json`
- `.codex/INSTALL.md`

---

## 5. 当前验证命令

```bash
beacon doctor verify-context --project-root . --strict --json
beacon doctor verify-materials --project-root . --version v1.4.5 --json
beacon doctor setup-codex-hud-hook --project-root . --version v1.4.5 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.4.5 --json
beacon gate check release --project-root . --version v1.4.5 --json
beacon release scorecard v1.4.5 --project . --json
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.4.5"}' \
  | beacon debug codex-fixed-hud --project-root . --version v1.4.5 --json
```

---

## 6. 后续迭代版本文档编写约定

- 根 README 只保留当前 release line、当前命令面、当前验证面、当前工件面、后续文档约定。
- 任何新的 release line 都先更新 `beacon/version-truth.json`、`beacon/__init__.py`、`pyproject.toml`，再更新 README / root `SKILL.md` / `skills/beacon/`。
- 当前 line 的 README 链接只能指向仓内真实存在的 `docs/beacon/<version>/...` 文件。
- 历史版本说明保留在各自 `docs/beacon/<version>/release/`，不要再把旧 release 细节混入当前推荐命令段。
- Codex/Claude 安装说明必须明确唯一技能根，并显式避免重复安装到 `~/.codex/skills/beacon`。
- 后续新增 host-visible skill 时，必须同步写明它是 host skill 还是 CLI 子命令，避免出现 `beacon-change` / `beacon change` 这类误读。

## 7. 当前运行线：v1.4.5

`v1.4.5` 已经是 Beacon 当前的 runtime 发布线。

这一线当前应以 `docs/beacon/v1.4.5/` 下的正式工件为准，重点包括：

- current runtime truth:
  - `beacon/version-truth.json`、`beacon/__init__.py`、`pyproject.toml` 统一提升到 `v1.4.5`
- current delivery tree:
  - 当前 requirement / execution / release 正式工件统一以 `docs/beacon/v1.4.5/` 为准
- current release governance:
  - `release scorecard`、`gate check release`、`release check` 已对齐 `v1.4.5`
- current branch contract:
  - `project-version-metadata` 当前 canonical branch 已对齐 `beacon/v1.4.5`

建议把 `v1.4.5` 作为当前架构与交付口径阅读：

- `docs/beacon/v1.4.5/SUMMARY.md`
- `docs/beacon/v1.4.5/execution/index.md`
- `docs/beacon/v1.4.5/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.5/prd/`
- `docs/beacon/v1.4.5/user-story/`
- `docs/beacon/v1.4.5/release/v1.4.5.md`

---

**版本**: v1.4.5
