# Beacon Revision Delta

- feature: `beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor`
- version: `v1.4.0`
- revision_id: `R2`
- source_revision_id: `R1`
- status: `ready`
- cleanup_required: `False`
- removed_requirement_count: `0`
- added_requirement_count: `7`

## Removed Requirement Surfaces
- none

## Added Requirement Surfaces
- `FR-009A` Beacon 自仓库的 package/runtime/docs/release truth 收敛到单一 canonical release manifest。
- `FR-009B` `beacon/__init__.py`、version truth 兼容表面、skill/rules 版本标记与运行期版本输出都改为 manifest-driven projection。
- `FR-009C` Beacon 提供 `beacon doctor sync-version-surfaces` 与 `beacon doctor verify-version-surfaces` 的正式治理闭环。
- `AC-105` Beacon 自仓库只存在一个 canonical release manifest 作为版本编辑源。
- `AC-106` 所有受管版本表面都能回溯到同一 manifest。
- `AC-107` `sync-version-surfaces` 能把 drifted version surfaces 重新校准到 canonical manifest。
- `AC-108` `verify-version-surfaces --strict` 在发现 drift 时返回阻断 verdict。
