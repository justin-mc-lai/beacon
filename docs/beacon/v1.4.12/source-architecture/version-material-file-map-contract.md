# 源码架构: version-material-file-map-contract

- version: `v1.4.12`
- feature: `version-material-file-map-contract`
- brainstorm_revision: `R2` -- 旧版本不做兼容，无 compat glob fallback

## 运行时布局

新增模块：

```
beacon/
├── commands/
│   └── manifest.py              ← CLI 面: beacon manifest <子命令>
├── utils/
│   └── manifest.py              ← 核心: load_manifest, save_manifest, compute_feature_paths, load_manifest_or_fail
```

受影响的已有模块（glob → manifest 迁移，无 compat fallback）：

```
beacon/utils/
├── material_sync.py             ← _discover_features → load_manifest_or_fail
├── material_audit.py            ← _feature_names → load_manifest_or_fail
├── docs_structure_contract.py   ← glob release_root → manifest version_level_paths
├── branch_governance.py         ← fnmatch → manifest 配置读取
├── implement_adapters.py        ← 无变更 (已确定性)
├── design_contract.py           ← 无变更 (已确定性)
├── artifact_paths.py            ← 无变更 (已确定性)
beacon/commands/
├── release.py                   ← glob patterns → manifest paths
├── implement/commands.py        ← glob */state.json → manifest + feature status
├── design.py                    ← glob *.md → manifest design paths
```

## 写路径

### Canonical 写入: manifest

```
beacon manifest add-feature --version <v> --feature <slug>
  -> resolve_version(project_root, version)
  -> validate_slug(slug)
  -> compute_feature_paths(project_root, version, slug)
     返回包含全部固定路径的 dict
  -> 读取已有 manifest 或 fail (v1.4.12+ 不存在时 fail, 不 fallback)
  -> 添加 feature 条目
  -> 写入 .machine/manifest/version-features.json
  -> 写入事务记录 .beacon/transactions/manifest-<txid>.json
  -> 返回 feature manifest 片段
```

### 写入: manifest sync（仅用于初始化或紧急修复）

```
beacon manifest sync --version <v>
  -> 扫描磁盘文件重建 manifest (仅首次初始化或紧急修复)
  -> 与已有 manifest 比对（如存在）
  -> 报告: added_features, removed_features, path_mismatches
  -> 写入 manifest
```

### 读模型: load_manifest_or_fail

```python
def load_manifest_or_fail(project_root: Path, version: str) -> dict[str, Any]:
    """v1.4.12+ 强制 manifest，不存在则 raise ManifestMissingError。"""
    manifest_path = project_root / "docs" / "beacon" / version / ".machine" / "manifest" / "version-features.json"
    if not manifest_path.exists():
        raise ManifestMissingError(version)
    return json.loads(manifest_path.read_text(encoding="utf-8"))
```

**不存在 `_build_legacy_manifest_from_glob` 函数。** 旧版本不被 v1.4.12+ 代码路径服务。

### 从 glob 切换到 manifest 的消费者

| 消费者 | 当前读取方式 | 新读取方式 |
|----------|-------------|----------|
| `_discover_features` | `glob(user-story/*.md)` | `load_manifest_or_fail()[features]` |
| `_feature_names` | `glob(prd/).union(user-story/).union(test-cases/)` | `load_manifest_or_fail()[features][*][slug]` |
| `build_material_audit` (research) | `glob(research/*.md)` | `load_manifest_or_fail()[version_level_paths]` |
| `build_material_audit` (release) | `glob(release/*.md)` | `load_manifest_or_fail()[version_level_paths]` |
| `build_material_audit` (execution) | `glob(implementation-plan-*.json)` | `load_manifest_or_fail()[features][*][execution_paths]` |
| release.py | `glob(*.json)`, `glob(technical-implementation-*.json)` | `load_manifest_or_fail()` |
| design.py list | `glob(design_dir/*.md)` | `load_manifest_or_fail()[version_level_paths]` |
| implement status | `glob(*/state.json)` | `load_manifest_or_fail()` + feature status |

### 投影: manifest 到 SUMMARY 同步

`beacon doctor sync-materials` 保持 `SUMMARY.md` Frozen Feature Packages 列表与 manifest 同步。

## 合约边界 (R2)

### 范围内

- `beacon/commands/manifest.py` -- CLI 面
- `beacon/utils/manifest.py` -- 核心 manifest 逻辑
- `_discover_features`, `_feature_names`, `build_material_audit` 迁移至 manifest 读取
- `docs_structure_contract.py`, `release.py`, `implement/commands.py`, `design.py`, `branch_governance.py` glob 消除
- manifest 读写和路径计算的回归测试

### 范围外

- 不修改已有 truth 文件内容
- 不修改 v1.4.11 或更早版本的目录结构
- 不包含格式校验 (归 `unified-truth-template-cli-contract`)
- 不设置 compat glob fallback
- 不修改 .beacon/state/ 或 runtime-ledger 投影机制

### 事务保证

- manifest 写入产生事务记录 `.beacon/transactions/manifest-*.json`
- manifest 读取是幂等且只读的
- manifest sync 是显式操作；无自动后台协调

### 显式边界声明

`beacon manifest` 不是新的 lifecycle stage，是 truth surface 的确定性索引服务。manifest 是 truth 文档的注册表，不是 truth 本身。`manifest_path_exists` 不等价于 `requirement_closure`。
