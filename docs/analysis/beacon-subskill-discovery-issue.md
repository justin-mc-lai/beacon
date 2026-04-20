# Beacon 子 Skill 在 Claude Code 中无法选中的根因分析

## 问题描述

Beacon 子 skill 在 Codex 中可以正常引用（6+3 模式），但在当前的 Claude Code 中无法选中子 skill 命令。

## 根本原因

### **Symlink 指向错误的目录层级**

**问题核心：**
```bash
# 当前错误的 symlink
~/.claude/skills/beacon -> /Users/apple/Developer/Personal/products/beacon

# 正确的 symlink 应该是
~/.claude/skills/beacon -> /Users/apple/Developer/Personal/products/beacon/skills/beacon
```

**为什么这会导致问题：**

1. **Claude Code 期望的结构：**
   ```
   ~/.claude/skills/beacon/
   ├── SKILL.md                    ← 主 skill
   ├── metadata.json
   ├── beacon-prd/SKILL.md         ← 子 skill
   ├── beacon-implement/SKILL.md   ← 子 skill
   └── ...
   ```

2. **当前实际的结构（symlink 指向项目根）：**
   ```
   ~/.claude/skills/beacon/
   ├── beacon/                     ← 多了一层！
   ├── docs/
   ├── tests/
   ├── skills/
   │   └── beacon/                 ← 真正的 skills 在这里
   │       ├── SKILL.md
   │       ├── beacon-prd/
   │       └── ...
   └── ...
   ```

3. **Claude Code 的 skill 发现逻辑：**
   - 扫描 `~/.claude/skills/` 下的每个目录
   - 在每个目录中查找 `SKILL.md` 和子目录中的 `SKILL.md`
   - **但只扫描一层子目录**，不会递归到 `skills/beacon/beacon-prd/`

### 对比 Superpowers 的正确安装

**Superpowers 通过 plugin marketplace 安装：**
```
~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1/
└── skills/                         ← 直接是 skills 目录
    ├── brainstorming/SKILL.md
    ├── writing-plans/SKILL.md
    └── ...
```

**Beacon 的 Codex 安装文档（正确）：**
```bash
# Codex 安装
ln -s /absolute/path/to/beacon/skills/beacon ~/.agents/skills/beacon
```

**Beacon 的 Claude 安装（错误）：**
```bash
# 当前错误的安装
ln -s /Users/apple/Developer/Personal/products/beacon ~/.claude/skills/beacon
```

### Claude Code 的 Skill 扫描行为

**Claude Code 扫描逻辑：**
```
~/.claude/skills/beacon/
├── SKILL.md                    ← 扫描这里 ✅
├── subdir1/SKILL.md            ← 扫描一层子目录 ✅
├── subdir2/SKILL.md            ← 扫描一层子目录 ✅
└── subdir1/nested/SKILL.md     ← 不扫描二层 ❌
```

**当前 Beacon 的实际结构（因为 symlink 错误）：**
```
~/.claude/skills/beacon/        ← symlink 指向项目根
├── beacon/                     ← 项目代码目录
├── docs/                       ← 文档目录
├── tests/                      ← 测试目录
└── skills/                     ← 真正的 skills 在这里
    └── beacon/                 ← 第二层！
        ├── SKILL.md            ← Claude 找不到（太深了）
        ├── beacon-prd/         ← 第三层！
        └── ...
```

**Claude Code 只能看到：**
- `~/.claude/skills/beacon/SKILL.md` ← 不存在（在 skills/beacon/ 下）
- `~/.claude/skills/beacon/beacon/` ← 被当作子 skill 目录，但没有 SKILL.md
- `~/.claude/skills/beacon/skills/` ← 被当作子 skill 目录，但没有 SKILL.md

## 验证证据

1. **Symlink 指向错误：**
   ```bash
   $ readlink ~/.claude/skills/beacon
   /Users/apple/Developer/Personal/products/beacon  # ← 指向项目根，错误！
   
   # 应该是：
   /Users/apple/Developer/Personal/products/beacon/skills/beacon
   ```

2. **真正的 skills 目录在第二层：**
   ```bash
   $ ls ~/.claude/skills/beacon/skills/beacon/
   beacon-prd/  beacon-implement/  beacon-help/  ...  # ← 这些在第二层
   ```

3. **Claude Code 的 skill 列表中只显示顶层 `beacon`：**
   - 系统提示中列出的可用 skill 只有 `beacon`
   - 没有 `beacon-prd`, `beacon-implement` 等子 skill

## 解决方案

### 方案 A：修正 Symlink 指向（推荐，立即可用）

**问题根源：**
Symlink 指向了项目根目录，而不是 skills 目录。

**解决步骤：**
```bash
# 1. 删除错误的 symlink
rm ~/.claude/skills/beacon

# 2. 创建正确的 symlink（指向 skills/beacon 目录）
ln -s /Users/apple/Developer/Personal/products/beacon/skills/beacon ~/.claude/skills/beacon

# 3. 验证
ls -la ~/.claude/skills/beacon/
# 应该看到：
# SKILL.md
# metadata.json
# beacon-prd/
# beacon-implement/
# ...
```

**修正后的结构：**
```
~/.claude/skills/beacon/        ← 直接指向 skills/beacon
├── SKILL.md                    ← Claude 能发现 ✅
├── metadata.json
├── beacon-prd/SKILL.md         ← Claude 能发现 ✅
├── beacon-implement/SKILL.md   ← Claude 能发现 ✅
└── ...
```

**优点：**
- 立即可用，无需等待
- 与 Codex 安装方式一致
- 保持 Beacon 的原始设计（6+3 封装）
- 符合 Superpowers 的安装模式
- 不需要修改任何代码

**这就是 Beacon 的 `.codex/INSTALL.md` 中的正确安装方式！**

### 方案 B：扁平化安装（备选）

如果方案 A 仍然无法工作，则将所有子 skill 提升到 `~/.claude/skills/` 顶层：

```bash
cd ~/.claude/skills
for skill in beacon/beacon-*/; do
  skill_name=$(basename "$skill")
  ln -s "$(pwd)/beacon/$skill_name" "$skill_name"
done
```

**缺点：**
- 破坏了 Beacon 的包装设计
- 增加了 `~/.claude/skills/` 目录的混乱度
- 与 Codex 安装方式不一致

## 临时解决方案

在 Claude Code 支持嵌套 skill 之前，可以通过以下方式手动调用：

```bash
# 直接调用 beacon CLI
bash ~/.claude/skills/beacon/skills/beacon/scripts/run_beacon.sh prd create "Feature"

# 或使用顶层 beacon skill 作为路由器
/beacon prd create "Feature"
```

## 结论

**问题根因：Symlink 指向错误**

Beacon 的 6+3 人类表面设计（`using-beacon + 9 public subskills`）在 Codex 和 Claude Code 中都应该正常工作，因为两者都支持一层子目录的 skill 发现。

**真正的问题是：**
```bash
# 错误的安装
~/.claude/skills/beacon -> /path/to/beacon (项目根)

# 正确的安装（参考 .codex/INSTALL.md）
~/.claude/skills/beacon -> /path/to/beacon/skills/beacon
```

这不是平台差异问题，而是**安装路径错误**。Superpowers 通过 plugin marketplace 自动安装到正确的路径，而 Beacon 需要手动创建 symlink，当前的 symlink 指向了错误的目录层级。

**立即修复：**
```bash
rm ~/.claude/skills/beacon
ln -s /Users/apple/Developer/Personal/products/beacon/skills/beacon ~/.claude/skills/beacon
```

修复后，所有 9 个子 skill（beacon-prd, beacon-implement, beacon-help 等）都应该能在 Claude Code 中正常选中和调用。
