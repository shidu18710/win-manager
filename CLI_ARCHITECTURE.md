# Win-Manager CLI 架构文档

## 概述

Win-Manager CLI 是一个功能强大的命令行界面，提供对 Win-Manager 所有核心功能的访问。该架构基于 Click 框架设计，提供直观的命令结构和丰富的参数选项。

## 命令结构

### 主命令
```
win-manager [全局选项] <子命令> [子命令选项]
```

### 全局选项
- `--config PATH` - 指定配置文件路径
- `--output FORMAT` - 输出格式 (json, yaml, table, text)
- `--verbose, -v` - 详细输出
- `--quiet, -q` - 静默模式
- `--dry-run` - 模拟运行，不实际执行操作

## 子命令分组

### 1. 布局管理 (layout)

#### layout apply
应用窗口布局
```bash
win-manager layout apply <layout_type> [选项]
```

**参数:**
- `layout_type` - 布局类型 (cascade, grid, stack)

**选项:**
- `--target TEXT` - 目标窗口过滤 (进程名、窗口标题等)
- `--exclude TEXT` - 排除窗口过滤 (可重复使用)
- `--columns INTEGER` - 网格布局列数
- `--padding INTEGER` - 窗口间距
- `--offset-x INTEGER` - 瀑布布局 X 偏移
- `--offset-y INTEGER` - 瀑布布局 Y 偏移
- `--stack-position [center|left|right]` - 堆叠位置
- `--window-width DIMENSION` - 窗口宽度 (像素值如800或百分比如50%)
- `--window-height DIMENSION` - 窗口高度 (像素值如600或百分比如75%)

**示例:**
```bash
win-manager layout apply grid --columns 3 --padding 10
win-manager layout apply cascade --target "chrome.exe"
win-manager layout apply stack --stack-position center --exclude "explorer.exe"
win-manager layout apply stack --window-width 800 --window-height 600
win-manager layout apply stack --window-width 60% --window-height 80%
```

#### layout undo
撤销上一次布局
```bash
win-manager layout undo
```

#### layout save
保存当前布局为自定义布局
```bash
win-manager layout save <name> [选项]
```

**参数:**
- `name` - 自定义布局名称

**选项:**
- `--description TEXT` - 布局描述

#### layout list
列出所有可用布局
```bash
win-manager layout list
```

### 2. 窗口管理 (window)

#### window list
列出所有可管理的窗口
```bash
win-manager window list [选项]
```

**选项:**
- `--filter TEXT` - 过滤条件 (进程名、标题等)
- `--include-minimized` - 包含最小化窗口
- `--sort-by [title|process|pid]` - 排序方式
- `--detailed` - 显示详细信息

#### window info
显示特定窗口信息
```bash
win-manager window info <window_id>
```

**参数:**
- `window_id` - 窗口ID或标题

#### window move
移动窗口
```bash
win-manager window move <window_id> --x <x> --y <y> [选项]
```

**参数:**
- `window_id` - 窗口ID或标题
- `--x INTEGER` - X 坐标
- `--y INTEGER` - Y 坐标

**选项:**
- `--width INTEGER` - 窗口宽度
- `--height INTEGER` - 窗口高度

#### window resize
调整窗口大小
```bash
win-manager window resize <window_id> --width <width> --height <height>
```

#### window minimize
最小化窗口
```bash
win-manager window minimize <window_id>
```

#### window maximize
最大化窗口
```bash
win-manager window maximize <window_id>
```

#### window restore
恢复窗口
```bash
win-manager window restore <window_id>
```

### 3. 配置管理 (config)

#### config show
显示当前配置
```bash
win-manager config show [选项]
```

**选项:**
- `--key TEXT` - 显示特定配置项
- `--section TEXT` - 显示特定配置节

#### config set
设置配置值
```bash
win-manager config set <key> <value>
```

**参数:**
- `key` - 配置键 (支持点号表示法)
- `value` - 配置值

#### config get
获取配置值
```bash
win-manager config get <key>
```

#### config reset
重置配置
```bash
win-manager config reset [选项]
```

**选项:**
- `--key TEXT` - 重置特定配置项
- `--confirm` - 确认重置

#### config export
导出配置
```bash
win-manager config export <path> [选项]
```

**参数:**
- `path` - 导出路径

**选项:**
- `--format [json|yaml]` - 导出格式

#### config import
导入配置
```bash
win-manager config import <path>
```

### 4. 热键管理 (hotkey)

#### hotkey list
列出所有已注册的热键
```bash
win-manager hotkey list
```

#### hotkey add
添加热键
```bash
win-manager hotkey add <key_combination> <action> [选项]
```

**参数:**
- `key_combination` - 热键组合 (如 ctrl+alt+g)
- `action` - 执行动作

**选项:**
- `--description TEXT` - 热键描述
- `--target TEXT` - 目标窗口过滤

#### hotkey remove
移除热键
```bash
win-manager hotkey remove <key_combination>
```

#### hotkey start
启动热键监听
```bash
win-manager hotkey start
```

#### hotkey stop
停止热键监听
```bash
win-manager hotkey stop
```

### 5. 工具命令 (tool)

#### tool status
显示系统状态
```bash
win-manager tool status
```

#### tool test
运行系统测试
```bash
win-manager tool test [选项]
```

**选项:**
- `--component TEXT` - 测试特定组件
- `--verbose` - 详细输出

#### tool benchmark
运行性能基准测试
```bash
win-manager tool benchmark [选项]
```

**选项:**
- `--windows INTEGER` - 测试窗口数量
- `--iterations INTEGER` - 迭代次数

#### tool cleanup
清理临时文件和缓存
```bash
win-manager tool cleanup
```

## 快捷命令

为了提高使用效率，提供以下快捷命令：

```bash
# 快速应用布局
win-manager grid    # 等同于 layout apply grid
win-manager cascade # 等同于 layout apply cascade  
win-manager stack   # 等同于 layout apply stack

# 快速撤销
win-manager undo    # 等同于 layout undo

# 快速列出窗口
win-manager ls      # 等同于 window list

# 快捷命令也支持窗口大小选项
win-manager stack --window-width 1000 --window-height 700
win-manager stack --window-width 50% --window-height 75%
```

## 输出格式

### JSON 格式
```json
{
  "success": true,
  "data": {
    "windows_processed": 5,
    "layout_applied": "grid"
  },
  "message": "Grid layout applied successfully"
}
```

### YAML 格式
```yaml
success: true
data:
  windows_processed: 5
  layout_applied: grid
message: Grid layout applied successfully
```

### 表格格式
```
┌─────────┬──────────────────┬─────────────┬────────────┐
│ Window  │ Title            │ Process     │ Position   │
├─────────┼──────────────────┼─────────────┼────────────┤
│ 1       │ Chrome Browser   │ chrome.exe  │ (0,0,800,600) │
│ 2       │ VS Code          │ code.exe    │ (800,0,800,600) │
└─────────┴──────────────────┴─────────────┴────────────┘
```

### 文本格式
```
✅ Grid layout applied successfully
📊 Windows processed: 5
🎯 Layout type: grid
```

## 错误处理

CLI 提供统一的错误处理机制：

- **退出码 0**: 操作成功
- **退出码 1**: 一般错误
- **退出码 2**: 配置错误
- **退出码 3**: 权限错误
- **退出码 4**: 资源不可用错误

## 配置文件

CLI 支持配置文件来设置默认行为：

```yaml
# ~/.win-manager/cli-config.yaml
default:
  output_format: table
  verbose: false
  
layout:
  default_type: grid
  grid_columns: 2
  grid_padding: 10
  
hotkeys:
  enable_on_start: true
  
filters:
  exclude_processes:
    - explorer.exe
    - dwm.exe
```

## 实现技术栈

### 核心框架
- **Click** - 命令行界面框架
- **Rich** - 丰富的文本和表格输出
- **Typer** - 可选的现代 CLI 框架 (如需要)

### 依赖库
- **PyYAML** - YAML 支持
- **Colorama** - 跨平台颜色支持
- **Tabulate** - 表格格式化

### 项目结构
```
src/win_manager/cli/
├── __init__.py
├── main.py          # 主命令入口
├── commands/        # 命令实现
│   ├── __init__.py
│   ├── layout.py    # 布局命令
│   ├── window.py    # 窗口命令
│   ├── config.py    # 配置命令
│   ├── hotkey.py    # 热键命令
│   └── tool.py      # 工具命令
├── utils/           # CLI 工具
│   ├── __init__.py
│   ├── output.py    # 输出格式化
│   ├── validation.py # 参数验证
│   └── helpers.py   # 辅助函数
└── config/          # CLI 配置
    ├── __init__.py
    └── cli_config.py
```

## 开发计划

### 第一阶段：基础框架
1. 设置 Click 框架和基本命令结构
2. 实现全局选项和配置系统
3. 创建基本的输出格式化功能
4. 实现错误处理和日志系统

### 第二阶段：核心命令
1. 实现布局管理命令 (layout)
2. 实现窗口管理命令 (window)
3. 实现配置管理命令 (config)
4. 添加基本的参数验证

### 第三阶段：高级功能
1. 实现热键管理命令 (hotkey)
2. 实现工具命令 (tool)
3. 添加快捷命令支持
4. 实现配置文件支持

### 第四阶段：优化和完善
1. 添加自动补全支持
2. 实现更丰富的输出格式
3. 添加性能优化
4. 完善文档和帮助系统

## 使用示例

### 基本使用
```bash
# 应用网格布局
win-manager layout apply grid

# 列出所有窗口
win-manager window list

# 设置默认布局
win-manager config set window_management.default_layout grid

# 添加热键
win-manager hotkey add "ctrl+alt+g" "layout apply grid"
```

### 高级使用
```bash
# 应用带过滤的布局
win-manager layout apply grid --target "chrome.exe" --exclude "explorer.exe"

# 应用堆叠布局并指定窗口大小
win-manager layout apply stack --stack-position center --window-width 1200 --window-height 800

# 使用百分比指定窗口大小
win-manager layout apply stack --stack-position center --window-width 80% --window-height 90%

# 导出配置
win-manager config export ~/.win-manager/backup.yaml

# 运行性能测试
win-manager tool benchmark --windows 100 --iterations 10
```

### 组合使用
```bash
# 设置详细输出并应用布局
win-manager --verbose layout apply cascade --offset-x 40 --offset-y 40

# 静默模式配置设置
win-manager --quiet config set filters.ignore_minimized true
```

---

此架构文档提供了 Win-Manager CLI 的完整设计规范，为实现提供了清晰的指导和参考。