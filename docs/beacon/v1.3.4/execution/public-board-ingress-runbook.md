# Beacon 公共看板外网暴露 Runbook

## 目标

- 给 Beacon 管理看板提供只读外网访问能力。
- 外网域名固定为 `https://beacon.lbeaconcc.icu/`。
- 复用现有 HAPI 所在 Cloudflare tunnel，但不复用 HAPI Hub 语义。

## 边界冻结

- 公开面只暴露 `pb_public` 静态看板，不暴露 PocketBase admin。
- PocketBase / SQLite 仍然是 projection，不是 Beacon 正式真相。
- 项目正式真相仍然是各项目本地 `docs/beacon` 与 `.beacon`。
- 不新增第二个公开 HAPI Hub，不改变 `https://hapi.lbeaconcc.icu/`。
- `omc`、`omx` 不进入 Beacon 管理看板，也不进入该公共域名。

## 架构

1. MacBook 本地重建 runtime-ledger，并生成 `~/.beacon/runtime-ledger/pocketbase/pb_public/`
2. 将 `pb_public` 同步到 Mac mini
3. Mac mini 用本地静态服务在 `127.0.0.1:18090` 提供只读看板
4. Mac mini 现有 shared tunnel 增加：
   - `beacon.lbeaconcc.icu -> http://127.0.0.1:18090`
5. Cloudflare DNS 将 `beacon.lbeaconcc.icu` 绑定到 tunnel `7626a1f7-08f2-4b63-86f0-64a3bddca0b8`

## 服务标签

- Mac mini static board launchd:
  - `com.beacon.public-board`
- Mac mini shared ingress:
  - `com.hapi.mini.primary-cloudflared`

## 标准操作

1. 先在 MacBook 重建真实项目投影：
   - `beacon doctor rebuild-runtime-ledger --project-root <project>`
2. 再执行仓库脚本：
   - `scripts/setup_public_board_ingress.sh`
3. 验证：
   - Mac mini 本地 `curl -I http://127.0.0.1:18090/`
   - 公网 `curl -I https://beacon.lbeaconcc.icu/`

## 只读核查

- `scripts/setup_public_board_ingress.sh --verify-only`

适用场景：

- 判断 Mac mini 静态服务是否仍在线
- 判断 tunnel 配置是否仍包含 Beacon hostname
- 判断公网只读看板是否可达

## 风险与回滚

风险：

- 如果把 Beacon 域名错误指向 `127.0.0.1:3006`，会污染 HAPI 入口语义。
- 如果暴露 PocketBase admin，会泄露控制面与机器路径，不符合 Beacon 边界。
- 如果直接公开 MacBook 本机服务，会再次回到非稳定入口模式。

回滚：

1. 从 Mac mini `config-primary-hapi.yml` 删除 `beacon.lbeaconcc.icu` ingress
2. `launchctl kickstart -k gui/$(id -u)/com.hapi.mini.primary-cloudflared`
3. 可选：停用 `com.beacon.public-board`
4. 可选：Cloudflare DNS 删除或覆盖 `beacon.lbeaconcc.icu`

## 可验收结果

- 访问 `https://beacon.lbeaconcc.icu/` 时，打开的是 Beacon 管理看板首页
- 首页包含角色化入口
- 项目详情可看到版本文档列表
- 点击文档后可在网页中只读查看内容
- 整个公开面不出现 PocketBase admin 入口
