# ⚡ 快速开始

在5分钟内上手Win-Manager！本指南将带您快速体验核心功能。

## 🎯 学习目标

完成本指南后，您将能够：
- ✅ 运行Win-Manager并查看窗口列表
- ✅ 应用三种基本布局（网格、瀑布、堆叠）
- ✅ 使用撤销功能恢复窗口状态
- ✅ 掌握基本的CLI命令

## 📋 开始前准备

确保您已经：
- ✅ [安装了Win-Manager](installation.md)
- ✅ 打开了几个窗口（如浏览器、记事本、文件管理器等）

## 🚀 第一步：查看窗口

让我们先看看Win-Manager能检测到哪些窗口：

```bash
# 列出所有可管理的窗口
win-manager ls
```

**期望输出：**
```
┌─────────┬──────────────────────────┬─────────────┬────────────────┐
│ 窗口ID   │ 标题                      │ 进程名       │ 是否可调整      │
├─────────┼──────────────────────────┼─────────────┼────────────────┤
│ 1       │ Google Chrome            │ chrome.exe  │ ✓              │
│ 2       │ 记事本                    │ notepad.exe │ ✓              │
│ 3       │ 资源管理器                │ explorer.exe│ ✓              │
└─────────┴──────────────────────────┴─────────────┴────────────────┘
```

💡 **提示**: 如果看不到任何窗口，请确保有打开的应用程序，并且它们不是最小化状态。

## 🎯 第二步：体验布局功能

### 🔲 网格布局 - 整齐排列

```bash
# 应用网格布局
win-manager grid
```

所有窗口会被整齐地排列成网格状：
```
┌─────────┬─────────┐
│ Chrome  │ 记事本   │
├─────────┼─────────┤
│ 资源管理器│ (空)    │
└─────────┴─────────┘
```

### 🔄 瀑布布局 - 层次展示

```bash
# 应用瀑布布局
win-manager cascade
```

窗口会呈阶梯状排列，便于快速切换：
```
Chrome
  ├─记事本
    ├─资源管理器
```

### 📚 堆叠布局 - 集中管理

```bash
# 应用堆叠布局（居中）
win-manager stack --stack-position center
```

所有窗口重叠在屏幕中央，节省空间。

## ↩️ 第三步：撤销操作

不喜欢当前布局？一键恢复：

```bash
# 撤销最后一次布局更改
win-manager undo
```

所有窗口会回到布局前的位置！

## 🔧 第四步：自定义参数

### 网格布局自定义

```bash
# 指定3列网格，间距为15像素
win-manager grid --columns 3 --padding 15
```

### 堆叠布局自定义

```bash
# 堆叠到左侧，并设置窗口大小
win-manager stack --stack-position left --window-width 800 --window-height 600

# 使用百分比设置窗口大小
win-manager stack --window-width 70% --window-height 80%
```

### 目标特定窗口

```bash
# 只整理Chrome窗口
win-manager grid --target chrome.exe

# 排除资源管理器窗口
win-manager cascade --exclude explorer.exe
```

## 🎮 第五步：尝试完整CLI

Win-Manager还有功能完整的命令结构：

```bash
# 使用完整命令格式
win-manager layout apply grid --columns 2
win-manager layout apply cascade --offset-x 40 --offset-y 30
win-manager layout undo

# 查看窗口详细信息
win-manager window list --detailed --sort-by process
```

## 💡 实用技巧

### 快速清理桌面
```bash
# 一键整理 → 临时集中 → 按需撤销
win-manager stack    # 集中所有窗口
# ... 专注工作 ...
win-manager undo     # 恢复原状
```

### 开发环境布局
```bash
# 只整理开发相关窗口
win-manager grid --target code.exe --target chrome.exe --columns 2
```

### 演示模式
```bash
# 设置统一的演示窗口大小
win-manager stack --window-width 1024 --window-height 768 --stack-position center
```

## 🎯 常用命令速查

| 命令 | 功能 | 示例 |
|------|------|------|
| `win-manager ls` | 列出窗口 | `win-manager ls --sort-by process` |
| `win-manager grid` | 网格布局 | `win-manager grid --columns 3` |
| `win-manager cascade` | 瀑布布局 | `win-manager cascade --offset-x 50` |
| `win-manager stack` | 堆叠布局 | `win-manager stack --stack-position center` |
| `win-manager undo` | 撤销布局 | `win-manager undo` |

## 🔍 输出格式

Win-Manager支持多种输出格式：

```bash
# JSON格式 - 适合脚本使用
win-manager --output json ls

# YAML格式 - 易读格式
win-manager --output yaml window list

# 静默模式 - 不显示详细信息
win-manager --quiet grid
```

## ❗ 注意事项

1. **权限问题**: 某些系统窗口需要管理员权限才能操作
2. **窗口过滤**: 系统会自动过滤不可调整大小的窗口
3. **撤销限制**: 撤销功能只能恢复最后一次布局更改

## 🎉 恭喜！

您已经掌握了Win-Manager的基本使用方法！

## 📚 下一步学习

现在您可以：

1. 📖 深入学习 [用户手册](user-guide.md) - 了解所有功能
2. 💻 查看 [CLI参考](cli-reference.md) - 掌握所有命令
3. 🔧 配置 [热键和自动化](user-guide.md#热键配置) - 提高效率
4. 🛠️ 学习 [故障排除](troubleshooting.md) - 解决常见问题

**开始享受更整洁的桌面体验吧！** ✨

---

💡 **小贴士**: 将常用命令添加到Windows快捷方式中，或设置热键，让窗口管理变得更加便捷！