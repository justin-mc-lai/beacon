# 版本默认（双轴）

> **Runtime = 螺丝刀型号；项目交付线 = 工件编号。**  
> 新项目从 **v0.0.1** 起号，不是从 Beacon 的 v1.6.9 起号。

## 两轴

| 轴 | 含义 |
|----|------|
| `runtime_version` | 本机 Beacon/Loom CLI 能力线 |
| `project_docs_version` | 当前仓库产品版本（`docs/beacon/<ver>/`） |

## 无 `-v` 时（normal）

| 项目类型 | 默认 project_docs |
|----------|-------------------|
| 外项目 greenfield（无 docs 线） | **v0.0.1** |
| 外项目已有 v0.2.3 | **v0.2.4**（项目内 patch+1） |
| Beacon 自仓 monorepo | 自驱规则（planning 或相对自身 release 的 patch） |

## Hotfix

- baseline = **该项目生产基线**（自仓才用 `current_runtime_release_line`）
- **不 bump**
- 登记 `hotfix/*` 分支，禁止裸 main 直写

## 禁止

- 用 toolkit 的 v1.6.x 当外项目默认产品版本  
- silent major/minor bump  
