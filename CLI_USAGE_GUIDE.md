# Win-Manager CLI 使用指南

## 快速开始

Win-Manager CLI 提供了强大的命令行界面来管理 Windows 窗口。以下是一些基本使用示例：

### 1. 查看帮助信息
```bash
# 查看主帮助
win-manager --help

# 查看特定命令帮助
win-manager layout --help
win-manager window --help
```

### 2. 基本布局操作

#### 快捷命令（推荐）
```bash
# 应用网格布局
win-manager grid

# 应用网格布局，指定3列
win-manager grid --columns 3

# 应用瀑布布局
win-manager cascade

# 应用堆叠布局
win-manager stack --stack-position center

# 应用堆叠布局并指定窗口大小
win-manager stack --stack-position center --window-width 800 --window-height 600

# 使用百分比指定窗口大小
win-manager stack --stack-position center --window-width 70% --window-height 85%

# 撤销布局
win-manager undo
```

#### 完整命令
```bash
# 应用网格布局到所有窗口
win-manager layout apply grid

# 应用网格布局，只针对Chrome窗口
win-manager layout apply grid --target chrome.exe

# 应用瀑布布局，排除资源管理器
win-manager layout apply cascade --exclude explorer.exe

# 应用堆叠布局并指定窗口大小
win-manager layout apply stack --stack-position center --window-width 1000 --window-height 700

# 使用百分比指定窗口大小
win-manager layout apply stack --stack-position center --window-width 60% --window-height 75%

# 列出所有可用布局
win-manager layout list
```

### 3. 窗口管理

```bash
# 列出所有窗口
win-manager ls

# 列出所有窗口（包括最小化的）
win-manager window list --include-minimized

# 根据进程名过滤窗口
win-manager window list --filter chrome

# 显示特定窗口信息
win-manager window info "Google Chrome"

# 移动窗口
win-manager window move "记事本" --x 100 --y 100

# 调整窗口大小
win-manager window resize "记事本" --width 800 --height 600
```

### 4. 配置管理

```bash
# 查看当前配置
win-manager config show

# 设置配置值
win-manager config set layout.default_type grid

# 获取配置值
win-manager config get layout.default_type

# 导出配置
win-manager config export ./my-config.yaml

# 导入配置
win-manager config import ./my-config.yaml
```

### 5. 热键管理

```bash
# 列出所有热键
win-manager hotkey list

# 添加热键
win-manager hotkey add "ctrl+alt+g" "layout apply grid"

# 删除热键
win-manager hotkey remove "ctrl+alt+g"

# 启动热键监听
win-manager hotkey start
```

### 6. 系统工具

```bash
# 查看系统状态
win-manager tool status

# 运行系统测试
win-manager tool test

# 运行性能测试
win-manager tool benchmark --windows 100

# 清理临时文件
win-manager tool cleanup
```

## 高级功能

### 1. 输出格式

```bash
# JSON格式输出
win-manager --output json layout list

# YAML格式输出
win-manager --output yaml tool status

# 表格格式输出（默认）
win-manager --output table window list

# 文本格式输出
win-manager --output text config show
```

### 2. 详细模式和静默模式

```bash
# 详细输出
win-manager --verbose layout apply grid

# 静默模式
win-manager --quiet layout apply grid

# 模拟运行（不实际执行）
win-manager --dry-run layout apply grid
```

### 3. 复杂过滤

```bash
# 多个目标过滤
win-manager grid --target chrome.exe --target notepad.exe

# 多个排除过滤
win-manager cascade --exclude explorer.exe --exclude dwm.exe

# 组合过滤
win-manager stack --target chrome --exclude "Google Chrome - 隐身"
```

### 4. 布局参数自定义

```bash
# 自定义网格布局
win-manager grid --columns 4 --padding 5

# 自定义瀑布布局
win-manager cascade --offset-x 40 --offset-y 30

# 自定义堆叠布局
win-manager stack --stack-position left

# 指定精确的窗口大小
win-manager stack --window-width 1200 --window-height 800 --stack-position center

# 使用百分比设置相对窗口大小
win-manager stack --window-width 75% --window-height 90% --stack-position center
```

## 配置文件

CLI 支持配置文件来设置默认行为。配置文件位于 `~/.win-manager/cli-config.yaml`：

```yaml
default:
  output_format: table
  verbose: false

layout:
  default_type: grid
  grid_columns: 2
  grid_padding: 10
  cascade_offset_x: 30
  cascade_offset_y: 30
  stack_position: center

hotkeys:
  enable_on_start: true

filters:
  exclude_processes:
    - explorer.exe
    - dwm.exe
  include_minimized: false

output:
  show_colors: true
  show_icons: true
  table_style: grid
```

## 实际使用场景

### 场景1: 开发环境布局
```bash
# 为开发设置网格布局，排除系统窗口
win-manager grid --exclude explorer.exe --exclude dwm.exe --columns 2

# 为代码编辑器设置特定布局
win-manager cascade --target code.exe --target notepad++.exe
```

### 场景2: 演示模式
```bash
# 堆叠所有窗口到中心
win-manager stack --stack-position center

# 堆叠窗口并设置统一的演示尺寸
win-manager stack --stack-position center --window-width 1024 --window-height 768

# 使用百分比设置适应性尺寸
win-manager stack --stack-position center --window-width 80% --window-height 75%

# 只显示特定应用的窗口
win-manager grid --target chrome.exe --target powerpoint.exe
```

### 场景3: 日常办公
```bash
# 查看当前所有窗口
win-manager ls --sort-by process

# 应用默认布局
win-manager grid

# 快速撤销
win-manager undo
```

## 故障排除

### 1. 编码问题
如果遇到字符编码问题，可以：
```bash
# 使用文本输出格式
win-manager --output text layout list

# 使用JSON格式避免特殊字符
win-manager --output json tool status
```

### 2. 权限问题
```bash
# 检查系统状态
win-manager tool status

# 运行系统测试
win-manager tool test
```

### 3. 调试模式
```bash
# 使用详细模式查看详细信息
win-manager --verbose --dry-run layout apply grid

# 检查配置
win-manager config show
```

## 常用命令组合

```bash
# 开发者日常工作流
win-manager ls --filter code                 # 查看代码编辑器
win-manager grid --target code.exe           # 整理代码窗口
win-manager config set layout.default_type grid  # 设置默认布局

# 演示准备
win-manager --quiet stack --stack-position center  # 静默整理窗口
win-manager --quiet stack --window-width 1024 --window-height 768  # 设置演示窗口大小
win-manager --quiet stack --window-width 75% --window-height 80%  # 使用百分比设置窗口大小
win-manager hotkey add "ctrl+alt+1" "grid"         # 设置快捷键
win-manager hotkey start                           # 启动热键监听

# 系统维护
win-manager tool status                      # 检查系统状态
win-manager tool test                        # 运行测试
win-manager tool cleanup                     # 清理临时文件
```

这个CLI工具提供了完整的窗口管理功能，支持各种使用场景和自定义需求。