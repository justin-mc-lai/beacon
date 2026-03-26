# Beacon v1.1.8 Boundaries

## In Scope

- 项目接管入口：`init`、project onboarding、architecture blueprint、version evolution blueprint
- 需求交付闭环：prototype baseline、implement technical archive、qa/browser acceptance
- 反馈闭环：debug runtime feedback、issue harvest、idea export
- 正式 docs/machine/runtime 三层工件

## Out of Scope

- 通用浏览器守护进程平台替代品
- 通用 CI/CD 调度系统
- 非 Beacon 生命周期内的业务部署编排
- 自动逆向完整业务架构图

## Human / Machine / Runtime Split

### Human Primary
- `docs/beacon/v1.1.8/SUMMARY.md`
- `docs/beacon/v1.1.8/execution/*.md`
- `docs/beacon/v1.1.8/release/v1.1.8.md`

### Machine Secondary
- `docs/beacon/v1.1.8/.machine/execution/*.json`
- `docs/beacon/v1.1.8/.machine/user-story/*.json`
- `docs/beacon/v1.1.8/.machine/qa/*.json`

### Runtime Internal
- `.beacon/implement/`
- `.beacon/debug/`
- `.beacon/qa/`
- `.beacon/state/`

## Release-Line Rule

v1.1.8 当前是正式 release line：

- 包版本：`1.1.8`
- toolkit 版本：`v1.1.8`
- 正式文档线：`docs/beacon/v1.1.8/`
