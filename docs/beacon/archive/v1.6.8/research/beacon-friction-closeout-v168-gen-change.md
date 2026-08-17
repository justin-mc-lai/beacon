# Research / Change Intent — Friction Closeout v1.6.8

- **date**: 2026-07-19T10:41:45.910252+00:00
- **skill**: beacon-gen-change
- **status**: truth_authoring (frozen R1 packages)
- **not**: implementation / qa_verdict / release_verdict

## User GO

开 `$beacon-gen-change` v1.6.8 热修 program：

`runtime-install-truth + longrun-contract-align + release-profile-wiring + fsm-implement-order`

四湖挂 **同一 GoalRun 主轴**。

## Why (from audit)

1. 全局 editable 跟随脏分支 → 版本漂
2. longrun_default 合同 true vs 代码 opt-in + env 暗门
3. ReleaseProfile 有函数但 release check 未接线
4. domain FSM 未锁 implement 任务序 → 空中楼阁

## Out of scope

- 云 CD / 自动 prod 回滚执行
- 默认 BEACON_V2=1
- 第二公共入口
