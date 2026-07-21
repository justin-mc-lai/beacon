# 生产热修（mainline hotfix）

## 规则

1. 识别：生产 / 线上 / 事故 / hotfix / 紧急回滚 → `--mode hotfix`
2. baseline 默认 = `current_runtime_release_line`（**不 bump**）
3. 分支 = `hotfix/<baseline>-<slug>` 从生产基线拉出并登记
4. **禁止** `beacon/v*/feature-*` 长开发 worktree 流
5. **禁止** 在裸 `main` 上直接 commit 业务（先 `git switch -c hotfix/...`）
6. `forward_port` 默认 `main`；`rollback_notes` 发布前必填
7. `beacon release check --profile hotfix` + **人工** release
8. 发布后 forward-port 到开发/规划线

## CLI

```bash
beacon goal hotfix-plan "生产：…" -p . --json
# → hotfix_branch, recommended_commands, baseline_ref
```
