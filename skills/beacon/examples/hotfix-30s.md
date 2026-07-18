# Hotfix 30 秒（v1.6.8）

```bash
# 1) 锁定生产基线
beacon goal run "生产：支付重复扣款" --mode hotfix \
  --from-version v1.6.7 \
  --forward-port beacon/v1.6.8/main \
  --rollback-notes "revert commit <sha> / feature flag off"

# 2) 或只出计划
beacon goal hotfix-plan "生产：支付重复扣款" \
  --from-version v1.6.7 \
  --forward-port main \
  --rollback-notes "revert X"

# 3) change → implement → qa（最小）→ release profile=hotfix
# 4) forward-port 合并到 next 线
```
