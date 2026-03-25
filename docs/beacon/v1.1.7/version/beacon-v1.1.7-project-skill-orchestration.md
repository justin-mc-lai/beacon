# 版本规划：Beacon v1.1.7 项目级 skill 编排与验收门禁

## 版本定位

- target_version: `v1.1.7`
- base_version: `v1.1.7`
- strategy: `bump:patch`
- owner: `Beacon Team`
- generated_at: `2026-03-25`

## 目标与范围

- 主题：让 Beacon 支持项目特定 skill profile、多 skill 编排、强证据验收
- 目标：解决多服务项目“文档通过但真实链路未验证”的漏测问题
- 范围：skill registry / profile / orchestration / evidence gate / contract drift / Rolo 适配样板

## 版本演进动机

真实问题来源：

- `Rolo v1.3.0 / KZFJ-1110` 需求写明支持图片、GIF、视频
- 前端上传也允许 `gif/mp4/mov/webm`
- 下游 STS 服务只允许 `jpg/png/pdf`
- 现有验收记录只验证了 OSS JSON 发布，不等于素材上传链路通过

这说明 Beacon 当前缺少：

1. 项目真实验收路径建模
2. 多服务依赖链 contract drift 识别
3. must-run acceptance case 的证据阻断

## 本版输出目标

1. Beacon 支持**内置 multi-skill registry**
2. Beacon 支持**project-specific skill profile**
3. Beacon 支持**skill-backed orchestration runner**
4. Beacon 支持**required evidence gate**
5. Beacon 支持**多服务 contract drift 诊断**
6. 以 `rolo` 为样板提供可落地 profile 示例，但不把设计绑死在 rolo 上

## 追溯

建议后续继续补：

- `beacon verify run <feature> --profile rolo-uat`
- `beacon orchestrate run <feature> --profile rolo-uat`
- `beacon review accept <feature>` 前的 required evidence 检查
