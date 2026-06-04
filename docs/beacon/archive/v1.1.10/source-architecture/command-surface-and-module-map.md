# Beacon v1.1.10 Command Surface And Module Map

## 命令入口从哪里来

CLI 真实入口很薄：

1. `beacon/main.py` 固定 import path
2. `beacon/cli_factory.py` 调 `build_app()`
3. `build_app()` 统一注册命令

所以读 Beacon 命令面，最先看：

- `beacon/main.py`
- `beacon/cli_factory.py`
- `beacon/command_catalog.py`

## 命令分层

`cli_factory.py` 当前把命令分成：

- `core`
- `support`
- `advanced`
- `labs`
- `bridge`
- `deprecated`

这意味着 Beacon 不是“所有命令都同级”的工具，而是有产品化主面和兼容/实验侧面。

## 主要命令簇

| Area | Representative Commands | Main Source |
| --- | --- | --- |
| Requirement authoring | `think`, `user-story`, `prd`, `test-case`, `workflow` | `beacon/commands/*` |
| QA / verification | `auto-test`, `qa`, `verify`, `test-progress` | `beacon/commands/qa.py`, `verify.py`, `auto_test.py` |
| Governance | `gate`, `release`, `review`, `report`, `status` | `beacon/commands/gate.py`, `release.py`, `report.py`, `status.py` |
| Runtime and repair | `doctor`, `debug`, `resume`, `feedback` | `beacon/commands/doctor.py`, `debug.py`, `resume.py`, `feedback.py` |
| Project execution | `implement`, `skill`, `profile`, `orchestrate` | `beacon/commands/implement.py`, `skill.py`, `verify.py`, `orchestrate.py` |

## 阅读建议

如果你只想知道“命令是怎么挂上去的”，读 `cli_factory.py` 就够了。

如果你想知道“某个命令写了哪些工件”，要继续看对应 `commands/*.py` 和相关 `utils/*.py`。

## 关键理解

Beacon 的命令层只是路由层。

大多数真实复杂度不在命令函数本身，而在：

- state helpers
- artifact path helpers
- writeback logic
- project skill/profile/orchestration
- QA / release scoring
