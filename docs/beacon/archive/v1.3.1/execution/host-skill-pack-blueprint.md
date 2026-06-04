# Beacon v1.3.1 Host Skill Pack Blueprint

## Purpose

`v1.3.1` 的极简人类面不能只停留在文档里。

它还必须变成：

- Codex 可发现的 host skills
- Claude agent 可发现的 host skills
- 能被自然 prompt 触发的最小 Beacon 入口

## Core decision

Beacon 不应把当前宽命令面全部暴露给 host agent。

Beacon 只应公开：

### One umbrella routing skill

- `using-beacon`

### Nine public human-facing subskills

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`

### Compatibility root skill

- `beacon`

## Packaging rule

Beacon 的 host skill 安装根保持为：

- `skills/beacon/`

目标结构：

```text
skills/beacon/
  SKILL.md
  metadata.json
  scripts/run_beacon.sh
  using-beacon/SKILL.md
  beacon-prd/SKILL.md
  beacon-user-story/SKILL.md
  beacon-test-case/SKILL.md
  beacon-implement/SKILL.md
  beacon-qa/SKILL.md
  beacon-release/SKILL.md
  beacon-help/SKILL.md
  beacon-status/SKILL.md
  beacon-doctor/SKILL.md
```

## Discovery rule

### Codex

- `~/.agents/skills/beacon` -> `skills/beacon/`

`~/.agents/skills/beacon` is the canonical Codex install root.

Do not also install the same Beacon pack under `~/.codex/skills/beacon`, or Codex may discover duplicated public skills.

### Claude

- `~/.claude/skills/beacon` -> `skills/beacon/`

并补 `/.claude-plugin/plugin.json`，为后续 plugin packaging 保留 metadata 入口。

## Routing rule

### `using-beacon`

它是 umbrella router，不是另一个宽命令面。

它负责把用户意图导向：

1. requirement clarification / spec -> `beacon-prd`
2. story / AC / acceptance mapping -> `beacon-user-story`
3. test / acceptance case design -> `beacon-test-case`
4. implementation handoff / execution -> `beacon-implement`
5. verification / acceptance / new findings -> `beacon-qa`
6. release readiness -> `beacon-release`
7. blocked / lost / broken context -> `beacon-help` / `beacon-status` / `beacon-doctor`

### Hidden lanes

以下能力继续存在，但不应成为 host-visible public skills：

- standalone `brainstorm`
- `team`
- `implement-team`
- `qa-team`
- learning lane
- auto research lane

## Acceptance

当下面条件都满足时，视为 `v1.3.1` host-skill pack 最小闭环成立：

1. repo 内存在 `skills/beacon/` 安装根
2. repo 内存在 `using-beacon + 9 public subskills`
3. Codex 安装文档存在并指向 `skills/beacon/`
4. Claude plugin metadata 存在
5. `v1.3.1` 文档把这些 host skills 视为极简人类面的触发层
6. tests 锁定 public skill set，不允许把宽命令面重新泄漏给 host-visible layer
