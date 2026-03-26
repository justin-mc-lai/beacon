# Beacon v1.1.8 Version Evolution Blueprint

## 当前版本定位

- 版本：`v1.1.8`
- 状态：`implemented, acceptance-verified, release-ready`
- 相对上一线：`v1.1.7`

## 与 v1.1.7 的核心增量

### 项目接管
- `init` 增强为 project lifecycle onboarding 入口
- 新增 architecture blueprint / version evolution blueprint / project onboarding state

### 交付闭环
- prototype baseline 进入正式设计与实现闭环
- implement 新增 technical archive
- qa 成为正式主入口并保留 auto-test alias

### 反馈闭环
- debug 从 prompt/run capture 扩展到 `.beacon/debug/` canonical feedback surface
- 支持 issue harvest / idea export

## Capability Map

| 能力 | v1.1.7 | v1.1.8 |
| --- | --- | --- |
| profile / orchestrate / evidence gate | implemented | retained |
| qa primary surface | planned | implemented |
| session governance | missing | implemented |
| technical implementation archive | missing | implemented |
| project onboarding state | missing | implemented |
| runtime debug issue/idea harvest | missing | implemented |

## 下一步演进方向

- 正式发布 `v1.1.8` release artifact
- 将 `qa` 更深替代 `auto-test` 历史心智
- 继续增强 project onboarding state 的自动推进
- 让 review / report / evolution-summary 更深消费 technical archive 与 debug issues
