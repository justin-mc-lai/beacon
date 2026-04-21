# Beacon CLI

> Evidence-first Product Workflow Kernel. Beacon 把需求澄清、用户故事、PRD、测试用例、执行证据与 gate/release 收敛到一个可审计闭环。

[![PyPI version](https://img.shields.io/pypi/v/beacon)](https://pypi.org/project/beacon/)
[![Python](https://img.shields.io/pypi/pyversions/beacon)](https://pypi.org/project/beacon/)

---

## 1. 当前版本是什么

Beacon 当前运行时发布口径是 **v1.3.6**。

> 当前发布线：`v1.3.6`

- **CLI 入口**：`beacon <subcommand>`
- **标准 skill 包**：`skills/beacon/`
- **当前包版本**：`1.3.6`
- **最新已接受文档线**：`v1.3.6`
- **文档主源**：`docs/beacon/<version>/`
- **状态目录**：`.beacon/`

当前主口径：

- `docs/beacon/` 是唯一维护的信息源
- `.beacon/` 是运行时状态，不替代正式交付文档
- 新生成的 AGENTS / CLAUDE managed block 也遵循以上口径
- 当前发布请优先以 `docs/beacon/v1.3.6/` 为准
- 当前架构、命令与 release 说明统一以 `docs/beacon/v1.3.6/` 为准

如果你只记一条：

> **Beacon 现在是 v1.3.6，写文档看 `docs/beacon/v1.3.6/`，执行命令用 `beacon <subcommand>`。**

---

## 2. 当前能力边界

### In scope

- 需求主链编排：`prd -> user-story -> test-case -> implement -> qa -> release`
- 证据与放行治理：`doctor`、`gate`、`release`、`report`
- 版本化 requirement materials：`docs/beacon/<version>/`
- 主机侧帮助与导航：`help`、`status`、`doctor`
- Codex HUD 接线与诊断：`debug codex-fixed-hud`、`doctor setup-codex-hud-hook`、`doctor verify-codex-hud-hook`

### Out of scope

- 直接替代业务代码实现
- 直接替代生产运维 / 发布平台
- 在 core surface 中公开 team / Ralph / bridge 细节
- 把外部 skill runner 当作默认 onboarding 路径

### v1.3.6 为什么重要

`v1.3.6` 把 Beacon 的当前发布口径收敛到更小、更稳定的主机面：

- runtime truth 已提升到 `v1.3.6`
- 6+3 人类 surface 继续保持最小化
- Codex fixed HUD 走 doctor 托管接线，而不是手工散落配置
- `skills/beacon/` 与仓内 docs/release line 对齐到同一版本

当前推荐阅读顺序：

- `docs/beacon/v1.3.6/SUMMARY.md`
- `docs/beacon/v1.3.6/execution/index.md`
- `docs/beacon/v1.3.6/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.6/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.3.6/execution/boundaries.md`
- `docs/beacon/v1.3.6/release/v1.3.6.md`

---

## 3. 当前推荐命令

### 安装

```bash
pip install beacon
# 或
cd beacon && pip install -e ".[dev]"
```

### 全局安装约束

Beacon 的全局安装必须遵守单一技能根约束，否则会出现：

- Beacon 公共 skill 重复发现
- Codex picker 同名 skill 成对出现
- 安装源漂移到旧副本
- 把 `beacon-change` 误解成 `beacon change` CLI 子命令

当前唯一允许的安装口径：

- Beacon skill 源：
  - `<repo>/skills/beacon/`
- Codex / agent 发现根：
  - `~/.agents/skills/beacon -> <repo>/skills/beacon`
- Claude Code 主 skill：
  - `~/.claude/skills/beacon -> <repo>`
- Claude Code 子 skills：
  - `~/.claude/skills/beacon-* -> <repo>/skills/beacon/<subskill>`

明确禁止：

- `~/.codex/skills/beacon`
- `~/.codex/skills/beacon/skills/beacon`
- 同时存在多个 `name: beacon` 的本地副本或历史备份链接

推荐清理并重装：

```bash
rm -rf ~/.codex/skills/beacon
rm -f ~/.agents/skills/beacon
mkdir -p ~/.agents/skills
ln -sf /absolute/path/to/beacon/skills/beacon ~/.agents/skills/beacon
```

安装后校验：

```bash
beacon --version
beacon --help
find ~/.agents/skills/beacon -maxdepth 2 -name SKILL.md | sort
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

如果你只想用最短路径快速跑通 Beacon v1.3.6，先执行：

```bash
beacon help --project-root . --version v1.3.6 --feature "<feature>" --json
beacon prd bootstrap "<feature>" --project-root . --version v1.3.6 --dry-run --json
beacon implement plan "<feature>" --project . --version v1.3.6 --json
beacon qa run "<feature>" --project . --version v1.3.6 --json
beacon gate check release --project-root . --version v1.3.6 --json
beacon release check v1.3.6 --project .
```

### Compatibility Entry Points

以下入口仍保留给兼容性与文档示例使用：

```bash
beacon workflow start "<feature>" --version v1.3.6 --project-root .
beacon think start "<feature>" --project-root . --version v1.3.6
beacon ask "请生成用户故事并给出验收标准" --project-root . --json
```

### Codex HUD Hook

用 doctor 托管 Codex HUD，而不是手工改散落配置：

```bash
beacon doctor setup-codex-hud-hook --project-root . --version v1.3.6 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.6 --json
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.3.6"}' \
  | beacon debug codex-fixed-hud --project-root . --version v1.3.6 --json
```

### Command Docs / 命令文档入口

- `docs/beacon/v1.3.6/SUMMARY.md`
- `docs/beacon/v1.3.6/execution/index.md`
- `docs/beacon/v1.3.6/execution/architecture-blueprint.md`
- `docs/beacon/v1.3.6/execution/project-skill-qa-evolution-blueprint.md`
- `docs/beacon/v1.3.6/execution/boundaries.md`
- `docs/beacon/v1.3.6/release/v1.3.6.md`

---

## 4. 当前交付工件

当前 release line 的正式工件：

- `docs/beacon/v1.3.6/SUMMARY.md`
- `docs/beacon/v1.3.6/prd/`
- `docs/beacon/v1.3.6/user-story/`
- `docs/beacon/v1.3.6/qa/test-cases/`
- `docs/beacon/v1.3.6/execution/`
- `docs/beacon/v1.3.6/release/v1.3.6.md`

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
beacon doctor verify-materials --project-root . --version v1.3.6 --json
beacon doctor setup-codex-hud-hook --project-root . --version v1.3.6 --apply --json
beacon doctor verify-codex-hud-hook --project-root . --version v1.3.6 --json
beacon gate check release --project-root . --version v1.3.6 --json
beacon release scorecard v1.3.6 --project . --json
printf '%s' '{"hook_event_name":"UserPromptSubmit","prompt":"继续推进 Beacon v1.3.6"}' \
  | beacon debug codex-fixed-hud --project-root . --version v1.3.6 --json
```

---

## 6. 后续迭代版本文档编写约定

- 根 README 只保留当前 release line、当前命令面、当前验证面、当前工件面、后续文档约定。
- 任何新的 release line 都先更新 `beacon/version-truth.json`、`beacon/__init__.py`、`pyproject.toml`，再更新 README / root `SKILL.md` / `skills/beacon/`。
- 当前 line 的 README 链接只能指向仓内真实存在的 `docs/beacon/<version>/...` 文件。
- 历史版本说明保留在各自 `docs/beacon/<version>/release/`，不要再把旧 release 细节混入当前推荐命令段。
- Codex/Claude 安装说明必须明确唯一技能根，并显式避免重复安装到 `~/.codex/skills/beacon`。
- 后续新增 host-visible skill 时，必须同步写明它是 host skill 还是 CLI 子命令，避免出现 `beacon-change` / `beacon change` 这类误读。

## 7. 当前运行线：v1.3.6

`v1.3.6` 已经是 Beacon 当前的 runtime 发布线。

这一线的主题是：

- 宿主原生 LLM 优先：
  - Claude / Codex skill 环境下，默认优先复用宿主语义能力
- Beacon CLI 去大脑化：
  - CLI 负责 truth read、contract validation、canonical projection、freeze / review / gate / release
- 全命令共用 delivery kernel：
  - `implement / qa / release / help / status / doctor` 共享统一 delivery contract 与 read model
- provider 降级为 fallback：
  - `BEACON_LLM_API_KEY` 仅保留给纯 CLI / provider fallback 场景

建议把 `v1.3.6` 作为当前架构与交付口径阅读：

- `docs/beacon/v1.3.6/SUMMARY.md`
- `docs/beacon/v1.3.6/execution/index.md`
- `docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`
- `docs/beacon/v1.3.6/prd/beacon-v1-3-6-host-native-llm-orchestration-and-full-command-runtime-refactor.md`
- `docs/beacon/v1.3.6/release/v1.3.6.md`
- `docs/beacon/v1.3.6/release/runtime-promotion-checklist.md`

---

**版本**: v1.3.6
