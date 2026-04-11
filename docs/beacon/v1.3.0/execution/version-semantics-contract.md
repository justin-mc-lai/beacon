# Beacon 版本语义契约

- 文档线: `v1.3.0`
- 镜像源: `beacon/version-semantics.json`
- 镜像规则: 本文档是机器可读版本语义 artifact 的人类可读中文镜像；两侧必须同步更新。

## 目的

Beacon 版本语义的统一中文说明入口。 机器侧以 `beacon/version-semantics.json` 为准，人类侧通过本镜像理解字段语义、状态含义、解析入口与使用规则。

## 规范字段

| 字段 | 类型 | 中文说明 | 示例 |
| --- | --- | --- | --- |
| `package_version` | 包版本 | 已安装 Beacon 包版本。 | `1.3.0` |
| `runtime_version` | 运行版本 | CLI 与受管上下文当前使用的 Beacon runtime/toolkit 版本线。 | `v1.3.0` |
| `docs_default_line` | 文档版本 | 当命令使用 auto/latest 解析文档目标时默认命中的文档线。 | `v1.3.0` |
| `current_runtime_release_line` | 发布真相 | 当前被视为正式 runtime 发布真相的 Beacon 版本线。 | `v1.3.0` |
| `planning_lines` | 规划版本 | 已开启规划但尚未提升为当前 runtime release 的未来文档线。 | `[]` |
| `partial_runtime_supplement_lines` | 补充增强 | 已有局部 runtime 增强、但仍未替代当前 runtime release 的规划版本线。 | `["v1.2.1"]` |

## 状态值

| 状态值 | 中文说明 |
| --- | --- |
| `historical_release` | 历史正式版本线，已不是当前 runtime release。 |
| `planning_only` | 仅规划中的版本线，已有 docs/package 规划但尚未成为 runtime release。 |
| `planning_with_partial_runtime_supplement` | 带局部 runtime 增强的规划版本线，但仍不是当前 runtime release。 |
| `current_runtime_release` | 当前 Beacon runtime 正式发布线。 |

## 解析入口契约

| 语义面 | 统一入口 |
| --- | --- |
| 文档目标解析 | `resolve_docs_version()` |
| 运行目标解析 | `resolve_runtime_version()` |
| 统一版本上下文 | `describe_project_version_context()` |
| 发布真相状态判断 | `release_truth_status()` |

## 消费面

- `ask`：自然语言入口
- `help`：阶段导航
- `status`：状态面板
- `doctor`：诊断与修复建议
- `init`：项目初始化
- `version`：版本规划

## 规则

- 不得把文档目标解析与运行目标解析混为一谈。
- 未经更新本 contract，不得为现有版本字段新增语义重叠的别名。
- 命令应暴露统一的 version_context 与 version_semantics，而不是各自重解释原始字段。

## 镜像同步契约

1. `beacon/version-semantics.json` 是机器可读单一事实源。
2. `docs/beacon/<version>/execution/version-semantics-contract.md` 是人类可读中文镜像。
3. 后续变更必须同时更新两侧。
4. 若 Markdown 镜像与 JSON artifact 漂移，测试必须失败。
