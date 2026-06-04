# Beacon v1.3.1 Version Evolution Blueprint

## 当前版本定位

- 版本：`v1.3.1`
- 状态：`accepted supplement line`
- 相对上一线：`v1.3.0`

## 版本路线图

```text
v1.3.0
  runtime 与 host-visible skill pack 收口
        |
        v
v1.3.1
  人类心智继续做减法
  + 并行 feature package contract
  + change 文档 contract
  + 版本演进图进入正式交付面
  + freeze clarity / technical review 前置门固化
  - “一个版本只对应一份 PRD”的隐含假设
  - 把 brainstorm 当成独立长期人类阶段的倾向
        |
        v
next
  再考虑把 change / contract 进一步 materialize 成自动产物
```

## 新增

- 同一版本支持多个并行 feature package 的正式 contract
- 独立 `change` 文档交付面
- 版本级新增 / 删除 / 修复演进视图
- release 对 feature package 聚合真相的要求

## 删除 / 收敛

- 收敛“一个版本默认只服务一份 PRD”的旧心智
- 收敛“人类需要自己拼 implementation summary + technical archive 才知道版本改了什么”的旧方式
- 收敛把 `brainstorm` 作为独立长期主阶段的倾向

## 修复

- 修复版本交付层缺少独立 change 文档的缺口
- 修复并行 feature package 一对一文档链未显式定义的缺口
- 修复 release 无法直观看到新增 / 删除 / 修复分类的问题

## 保留

- 人类 6 段主闭环
- `implement` / `qa` 单入口
- machine lanes 的内部自由度
- 旧项目按 docs version 同步 materials 的方向
- deterministic implementation contract 前置门

## 对实现的含义

`v1.3.1` 不要求立刻重写现有命令面。

它优先要求：

1. 把已存在的 feature-slug 平铺实现明确成 contract
2. 把版本 change / evolution 变成显式交付物
3. 让后续自动化产物生成建立在已有 summary / technical archive 之上
