# Beacon Feature Change Document

- feature: `beacon-operator-workbench-and-board-launcher`
- feature_slug: `beacon-operator-workbench-and-board-launcher`
- version: `v1.3.11`
- status: `reopened-for-semantic-and-prototype-closure`

## Scope
- software semantic governance for operator surfaces
- operator workbench prototype projection closure
- preview anti-drift and recover-first first-screen contract
- prototype UI copy de-explanation and contract-to-UI projection split

## Added
- `software-semantic-profile` 作为 prototype/workbench 的正式语义合同，约束标题、状态文案、动作文案、字段约束、异常文案的标准句式与禁用词。
- `ui-copy-projection-contract` 作为 page intent 到 UI copy 的唯一投影面，禁止把 `why / reasoning / review guidance / asset-catalog wording` 直接渲染到首屏。
- `operator-workbench-first-screen-contract` 要求首屏先显示 `当前状态 / 当前阻塞 / 下一步动作 / 恢复路径`，禁止让 run 列表、路径、历史噪声占据首屏。
- `semantic-lint-and-freeze-gate` 要求 prototype freeze、preview render、board export 前统一校验术语一致性、禁用词、状态枚举、正反约束、默认值显式性。
- `contract-to-ui-projection-split` 作为正式模型边界，要求 `first_screen_contract / state_visibility_contract / page_intent_contract` 默认属于内部治理合同，禁止未经降噪投影直接变成终态 UI 解释文案。
- `production-ui-copy-profile` 作为正式投影子合同，要求 normal/ready 状态默认输出对象、关键数据与主动作，不默认输出“当前状态 / 下一步动作 / 恢复路径”说明块。
- `de-explanation-default` 作为正式默认行为，要求 loading、ready、marketing hero、mobile home、login entry 等表面优先输出克制产品文案，只有 error / blocked / empty-risk / high-friction onboarding 场景允许显式恢复说明上屏。

## Removed / Reduced
- 降低“preview 只是 design asset catalog 也可交付”的错误口径。
- 降低“页面自己解释需求、自己生成设计语气”的自由投影空间。
- 降低“Review / monitor / trends / health” 一类通用 SaaS 动词覆盖具体业务动作的语义漂移。
- 降低“prototype 审阅合同直接投射成前端首屏解释块”的错误实现自由度。
- 降低“加载态、登录态、首页首屏默认展示治理型说明文案”的错误默认值。

## Fixed
- 明确 workbench / board / prototype 的首屏对象必须是 operator judgment，而不是 design summary、route summary 或 artifact catalog。
- 明确 `ux-prd / page-spec / pages / component-catalog / preview` 之间需要受同一语义合同约束，不能每层各写一套解释话术。
- 明确 preview 渲染的是 `operator workbench prototype`，不是 `design asset catalog projected from prototype truth`。
- 明确文案必须满足正式、克制、严谨、专业、简洁、准确的企业软件语义规范，不得再输出主观词、弱约束词、口语化表达、设计愿景话术。
- 明确 public board 与 writable operator workbench 虽可共享状态源，但语义边界、标题体系、动作体系必须统一受 semantic profile 管控。
- 明确 `当前状态 / 下一步动作 / 恢复路径` 属于 requirement/prototype 层判断合同，不等于 production UI 必须逐字逐块直出。
- 明确 UI copy projection 必须区分 `internal contract copy` 与 `production-visible copy`，前者服务审阅和可测性，后者服务正式产品界面。
- 明确首屏“先完成判断”不等于“必须把判断过程写成解释性段落展示给用户”。

## Not Added
- 未把 prototype 子链路升级为视觉设计系统重做项目。
- 未让 workbench 成为 requirement truth 编辑器。
- 未要求本次 change 同时解决品牌层视觉风格重构。
- 未要求所有页面都删除状态反馈；本次只禁止把中间治理合同默认直投到正常态 UI。

## Refresh Route
- `prd revise`: `docs/beacon/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md`
- `user-story refresh`: `docs/beacon/v1.3.11/user-story/beacon-operator-workbench-and-board-launcher.md`
- `test-case refresh`: `docs/beacon/v1.3.11/qa/test-cases/beacon-operator-workbench-and-board-launcher.md`
- `prototype refresh`: `docs/beacon/v1.3.11/prototype/beacon-operator-workbench-and-board-launcher/`
- `implement delta`: `beacon/utils/prototype_utils.py`, preview renderer, prototype compiler, board/workbench copy projector

## Traceability Refs
- `docs/beacon/v1.3.11/prd/beacon-operator-workbench-and-board-launcher.md`
- `docs/beacon/v1.3.11/user-story/beacon-operator-workbench-and-board-launcher.md`
- `docs/beacon/v1.3.11/qa/test-cases/beacon-operator-workbench-and-board-launcher.md`
- `docs/beacon/v1.3.11/prototype/beacon-operator-workbench-and-board-launcher/ux-prd.md`
- `docs/beacon/v1.3.11/prototype/beacon-operator-workbench-and-board-launcher/page-specs/execution-board.json`
- `docs/beacon/v1.3.11/prototype/beacon-operator-workbench-and-board-launcher/preview.html`
