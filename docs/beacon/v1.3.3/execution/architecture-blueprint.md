# Beacon v1.3.3 Architecture Blueprint

## 目标

把 Beacon 从“核心 workflow + 外部 skill orchestration 混叙事”的状态，进一步收敛为：

```text
Core
  = minimal human lifecycle
  + host-native implement / qa
  + contract / evidence / gate kernel

Compatibility
  = external runners
  + external skill orchestration
  + deprecated bridge surfaces
```

## 1. Core architecture

`v1.3.3` 里的 core 应继续只围绕以下能力组织：

### Human-facing

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`
- `help`
- `status`
- `doctor`

### Machine-internal

- host-native subagent/team execution
- embedded runtime/delegation prechecks
- requirement clarity / technical review contracts
- QA evidence, scorecard, gate, and release closure

核心规则：

> 人类只面对主链；复杂执行逻辑继续留在机器内部。

## 2. Compatibility architecture

外部兼容面继续保留，但必须退出核心叙事：

- external adapters:
  - `omx`
  - `omc`
  - `gstack`
- external orchestration surfaces:
  - `skill`
  - `profile`
  - `orchestrate`
- bridge residue:
  - `ralph-bridge`

兼容面的目标：

- 为历史项目保留迁移路径
- 为特种项目保留显式 opt-in 能力
- 不再作为默认教学路径

## 3. QA architecture target

`qa` 在 `v1.3.3` 中继续保留 `v1.3.2` 的正式地位：

- 它是第二执行面
- 它围绕冻结材料推进
- 它产出 browser evidence / scorecard / repair handoff

但要进一步收口：

- 默认不自动执行外部 orchestration
- 默认先返回 Beacon 内部 closure judgment
- 只有显式 compatibility mode 才允许进入外部命令链

## 4. Contract architecture target

要保留的不是外部 skill 本身，而是这些 contract 能力：

- required evidence
- required cases
- contract drift
- project verification policy

在 `v1.3.3` 中，这些 contract 必须与 external execution 解耦：

```text
project contract evaluation
!=
external command execution
```

## 5. Documentation architecture target

文档结构也要反映这次瘦身：

- root README 只教 current core path
- `skills/beacon/` 只教 current core path
- external/compatibility 叙事只进：
  - compatibility docs
  - migration docs
  - advanced operator docs

## 6. Implementation direction

优先实现顺序：

1. 文案和命令面收口
2. `qa` 默认路径去隐式 orchestration
3. adapter / registry / bridge 分层
4. core tests vs compatibility tests 分层
5. project contract 与 external execution 解耦

## 7. 完成判定

`v1.3.3` 可以进入实现的前提是：

1. core/compatibility 边界已经讲清
2. 不会破坏 `v1.3.2` 已验收主线
3. 每个拟动区域都能归到“收口”而不是“加新能力”
