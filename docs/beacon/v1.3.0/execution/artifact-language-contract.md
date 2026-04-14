# Beacon 工件语言策略契约

- 文档线: `v1.3.0`
- 镜像源: `beacon/artifact-language-policy.json`
- 镜像规则: 本文档是机器可读语言策略 artifact 的人类可读中文镜像；两侧必须同步更新。

## 目的

为未来所有 Beacon artifact 类型提供统一的“中人 / 英机”生成规范。

## 默认策略

- 人类主语言: `zh-CN`
- 机器主语言: `en`
- 基础规则: 不得为了展示层本地化而重命名机器稳定主键。

## 工件类型

| 类型 | 面向对象 | 默认语言 | 覆盖范围 | 说明 |
| --- | --- | --- | --- | --- |
| 人类主读需求材料 | 人类 | zh-CN | `["summary", "prd", "user-story", "qa/test-cases", "execution/index", "execution/contracts"]` | 面向人类的规划、需求与导航材料默认使用中文。 |
| 机器主读契约与运行工件 | 机器 | en | `[".machine", "runtime_state", "json_contracts", "evidence_payloads"]` | 机器契约与运行工件优先保持英文键名与机器友好结构。 |
| 机器契约的人类中文镜像 | 人类 | zh-CN | `["execution/*-contract.md"]` | 机器可读契约的人类中文镜像；机器 artifact 仍是事实源。 |

## 镜像同步规则

- source of truth: `机器可读 artifact`
- 中文镜像: `人类可读中文 Markdown`
- enforce:
  - source JSON artifact
  - 中文镜像 Markdown
  - 统一渲染器或确定性转换
  - 源码中的 render 函数
  - 若两侧漂移，测试必须失败

## 全局规则

- 面向人类的规划与需求材料应默认使用中文。
- 面向机器的契约与运行工件应默认使用英文或机器稳定主键。
- 本地化不得改变机器字段名。
- 任何新增镜像 artifact 类型都必须同时定义 source JSON、中文镜像 Markdown、render 函数与漂移测试。
