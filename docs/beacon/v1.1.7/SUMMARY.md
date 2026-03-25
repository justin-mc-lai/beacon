# Beacon v1.1.7 Summary

**主题**: 项目特定 skill profile、多 skill 内建能力、编排式 verify / accept gate  
**状态**: Planned  
**日期**: 2026-03-25

---

## 本版目标

v1.1.7 的目标不是继续补单点命令，而是补上 Beacon 在真实多服务项目里的“执行适配层”：

> 让 Beacon 不只会生成需求和通用 QA，而是能按项目特定工作流真正触发 skill、编排执行、收集证据，并在验收前自动阻断漏测场景。

这版重点来自真实问题抽象：

- Rolo v1.3.0 的 `KZFJ-1110` 文档 / 前端都声明支持 GIF / 视频素材；
- 真实下游 STS 服务只支持 `JPG/PNG/PDF`；
- 结果出现“文档通过、页面看似完成、UAT 实际失败”的合同漂移。

因此 v1.1.7 需要新增：

1. **Beacon 内置 multi-skill 能力**
2. **Project Profile / Project Skill Adapter**
3. **编排式 verify runner 与 evidence gate**
4. **must-run acceptance evidence**
5. **多服务 contract drift 检测**
6. **以 Rolo 作为真实验证样板，但保持通用设计**

---

## 本版核心问题定义

Beacon v1.1.7 已具备：

- lifecycle closure
- freeze / reopen
- native-single / native-team
- help / doctor advise / status / scoring
- formal review accept

但还缺少：

- 按项目接入特定执行 skill 的标准机制
- 按项目定义“真实验收路径”的 profile
- 用 skill 编排 UAT / gateway / pipeline / SQL / logs 的执行器
- 自动把“必须跑过的测试场景”变成 accept 前的阻断条件

---

## v1.1.7 期望结果

Beacon v1.1.7 完成后，应支持：

```text
需求冻结
→ 选择项目 profile
→ Beacon 调用项目 skill 编排实现/验证
→ 收集接口/UI/log/SQL/pipeline evidence
→ quality review
→ evidence gate
→ accept / block
```

并且：

- 一个项目可以声明多个 skills
- 一个 feature / stage 可以绑定特定 skill
- 一个项目可以用 profile 声明自己的 verify / delivery / debug 工作流
- accept 不再只看“测试好像跑过”，而是看 required evidence 是否齐全

---

## 本版新增物料

- `version/beacon-v1.1.7-project-skill-orchestration.md`
- `prd/beacon-project-skill-orchestration.md`
- `user-story/beacon-project-skill-orchestration.md`
- `qa/test-cases/beacon-project-skill-orchestration.md`
- `qa/test-cases/index.md`
- `execution/index.md`

---

## 一句话总结

> v1.1.7 要把 Beacon 从“有通用工作流能力的内核”升级为“能按项目 profile 调用多 skill、执行编排、收集证据并阻断验收漏测的交付内核”。
