# 页面：Learning 披露中心

**平台**: `Web, PC`
**优先级**: `P1`

## 页面文案
标题：Learning 披露中心
副标题：本次推荐采用了哪些 learning hint，这些 hint 是否仍可信，是否只作为参考。
主动作：返回意图路由器, 返回项目详情

## 页面结构
采用的 learning hint
渐进披露层级
stale / superseded 标记

## 页面线框
```text
+-----------------------------+
| 采用的 learning hint |
+-----------------------------+
| 渐进披露层级 |
+-----------------------------+
| stale / superseded 标记 |
+-----------------------------+
| 不能作为 truth 的提示 |
+-----------------------------+
| 返回 route 判断 |
+-----------------------------+
```

## 页面状态
已披露：learning hint 与使用层级已经明确展示。
经验过期：存在 stale 或 superseded learning，只能作为弱提示。
无相关经验：没有匹配 feature / host / runner / domain 的 learning hint。
读取中：正在读取 learning plane。
读取失败：learning 读取失败，不影响 truth/gate 判断。

## 页面跳转
返回意图路由器 -> `intent-router`
返回项目详情 -> `project-detail`
