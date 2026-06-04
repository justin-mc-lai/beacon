# Beacon v1.1.7 命令面草案（原生 implement + 生命周期闭环）

## 1. 目标

v1.1.7 的命令面要表达的不是“更多命令”，而是更清晰的生命周期动作。

## 2. 建议命令

### 生命周期命令

```bash
beacon freeze <feature> --project-root . --version v1.1.7
beacon reopen <feature> --project-root . --version v1.1.7 --reason "change request"
beacon review accept <feature> --project-root . --version v1.1.7
```

### 导航命令

```bash
beacon help --project-root . --version v1.1.7 --feature <feature>
beacon help --project-root . --version v1.1.7 --feature <feature> --json
beacon doctor advise --project-root . --version v1.1.7 --feature <feature>
```

### implement 命令增强

```bash
beacon implement run "Feature" --runner native-single --project-root . --version v1.1.7
beacon implement run "Feature" --runner native-team   --project-root . --version v1.1.7
```

### workflow 命令增强

```bash
beacon workflow start "Feature" --project-root . --version v1.1.7
beacon workflow continue --project-root . --version v1.1.7 --run-id <run>
```

要求：
- `workflow continue` 必须识别当前 revision 与 item 闭环状态
- 若当前 revision 已 superseded，必须切到当前 active revision

### status 命令增强

```bash
beacon status --board --project-root . --version v1.1.7
```

新增展示目标：
- next_step.action
- next_step.command
- readiness / closure / test / quality scores
- current revision id
- current revision status
- story coverage
- AC verified ratio
- TEST passed ratio
- blocked reason

## 3. 命令面语义原则

1. `freeze` 是正式动作，不是隐式状态变化
2. `reopen` 是创建新 revision 的动作，不是修改当前 revision
3. `accept` 是正式动作，不是 gate pass 的副产物
4. `implement run` 默认要有 native runner 可选
5. `help` 必须输出当前阶段、下一步、推荐命令与评分
6. `doctor advise` 必须输出 blocked reason 与修复建议

## 4. 与现有命令的兼容原则

- adapter runner 继续保留
- 原 `implement run --runner omx/omc/gstack` 继续可用
- 但 Beacon 默认闭环不再依赖 adapter

## 5. 结论

命令面草案的本质是：

> 把原本隐式、文档式、外接式的动作，升级成生命周期语义明确的正式命令。

