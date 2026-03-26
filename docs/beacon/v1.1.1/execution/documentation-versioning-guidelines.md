# Beacon v1.1.1 Documentation Versioning Guidelines

## 目标

统一后续迭代版本的文档写法，避免再次出现“实现版本、README 口径、交付工件版本”三者脱节。

## 单一事实源

- `docs/beacon/<version>/`：canonical source
- `.beacon/`：runtime state and evidence
- `README.md`：只描述**当前发布线**

## README 规则

README 只允许保留以下 5 类当前信息：

1. 当前版本是什么
2. 当前能力边界
3. 当前推荐命令
4. 当前交付工件
5. 当前验证命令

历史版本内容只能出现在：

- 兼容说明
- 附录
- 历史参考链接

## 新版本文档最低集

每个新版本至少包含：

```text
docs/beacon/<version>/
├── user-story/
├── prd/
├── qa/test-cases/
└── execution/
    ├── boundaries.md
    └── acceptance-regression-audit.md
```

## 发布时更新顺序

1. bump package/runtime version
   - `pyproject.toml`
   - `beacon/__init__.py`
2. 更新 managed context version
   - `beacon/utils/context_files.py`
   - `AGENTS.md`
   - `CLAUDE.md`
3. 更新 `README.md` 当前发布线口径
4. 生成 acceptance audit
5. 校验 `docs/beacon` 与运行时证据一致性

## 推荐命令

```bash
python3 -m pytest -q
beacon gate check release --project-root . --version <version>
beacon release check <version> --project .
beacon report latest acceptance-audit --project-root . --version <version> --feature <feature> --run-regression --write
```

## 禁止项

- 不要重新引入 `docs/product` 作为交付树
- 不要把历史版本写成 README 当前能力说明
- 不要手工维护 acceptance audit 统计数字
- 不要在 README 中混用多代“当前版本”描述
