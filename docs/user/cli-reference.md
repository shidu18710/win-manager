# 💻 CLI 参考手册

Win-Manager 命令行工具的完整参考文档。

## 📖 概述

Win-Manager提供两种命令行接口：
1. **简单CLI** - 基于argparse的基础接口
2. **完整CLI** - 基于Click的功能丰富接口（推荐）

## 🌟 快捷命令

最常用的快捷命令，可直接使用：

### 布局命令

```bash
# 网格布局
win-manager grid [选项]

# 瀑布布局  
win-manager cascade [选项]

# 堆叠布局
win-manager stack [选项]

# 撤销布局
win-manager undo
```

### 窗口列表

```bash
# 列出窗口
win-manager ls [选项]
```

## 🏗️ 完整命令结构

### 全局选项

所有命令都支持的全局选项：

```bash
win-manager [全局选项] <命令> [命令选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--config PATH` | 指定配置文件路径 | 自动检测 |
| `--output FORMAT` | 输出格式: json, yaml, table, text | table |
| `--verbose, -v` | 详细输出 | false |
| `--quiet, -q` | 静默模式 | false |
| `--dry-run` | 模拟运行，不实际执行 | false |

**示例：**
```bash
win-manager --verbose --output json grid --columns 3
win-manager --quiet cascade
win-manager --dry-run --output yaml layout apply stack
```

## 📐 布局管理命令

### layout apply

应用指定的窗口布局：

```bash
win-manager layout apply <布局类型> [选项]
```

**布局类型：**
- `cascade` - 瀑布布局
- `grid` - 网格布局  
- `stack` - 堆叠布局

**通用选项：**
| 选项 | 类型 | 说明 |
|------|------|------|
| `--target TEXT` | 多个 | 目标窗口过滤（进程名、标题） |
| `--exclude TEXT` | 多个 | 排除窗口过滤 |

**网格布局选项：**
| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|-------|
| `--columns INTEGER` | 整数 | 网格列数 | 自动计算 |
| `--padding INTEGER` | 整数 | 窗口间距（像素） | 10 |

**瀑布布局选项：**
| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|-------|
| `--offset-x INTEGER` | 整数 | X轴偏移量（像素） | 30 |
| `--offset-y INTEGER` | 整数 | Y轴偏移量（像素） | 30 |

**堆叠布局选项：**
| 选项 | 类型 | 说明 | 默认值 |
|------|------|------|-------|
| `--stack-position CHOICE` | center/left/right | 堆叠位置 | center |
| `--window-width DIMENSION` | 尺寸 | 窗口宽度 | 80%屏幕 |
| `--window-height DIMENSION` | 尺寸 | 窗口高度 | 80%屏幕 |

**尺寸格式：**
- 像素值：`800`, `1200`
- 百分比：`50%`, `75%`, `100%`

**示例：**
```bash
# 基础布局
win-manager layout apply grid
win-manager layout apply cascade --offset-x 40

# 目标过滤
win-manager layout apply grid --target chrome.exe --exclude explorer.exe

# 堆叠布局自定义
win-manager layout apply stack --stack-position center --window-width 1024 --window-height 768
win-manager layout apply stack --window-width 70% --window-height 85%

# 网格布局自定义
win-manager layout apply grid --columns 3 --padding 15
```

### layout undo

撤销最后一次布局更改：

```bash
win-manager layout undo
```

### layout list

列出所有可用布局：

```bash
win-manager layout list
```

## 🪟 窗口管理命令

### window list

列出窗口信息：

```bash
win-manager window list [选项]
```

**选项：**
| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--filter TEXT` | 过滤条件（进程名、标题） | 无 |
| `--include-minimized` | 包含最小化窗口 | false |
| `--sort-by CHOICE` | 排序方式: title/process/pid/size | title |
| `--detailed` | 显示详细信息 | false |

**示例：**
```bash
win-manager window list
win-manager window list --filter chrome --detailed
win-manager window list --include-minimized --sort-by process
```

### window info

显示特定窗口的详细信息：

```bash
win-manager window info <窗口标识>
```

**示例：**
```bash
win-manager window info "Google Chrome"
win-manager window info chrome.exe
```

### window 操作命令

**移动窗口：**
```bash
win-manager window move <窗口标识> --x <X坐标> --y <Y坐标> [--width <宽度>] [--height <高度>]
```

**调整大小：**
```bash
win-manager window resize <窗口标识> --width <宽度> --height <高度>
```

**窗口状态：**
```bash
win-manager window minimize <窗口标识>
win-manager window maximize <窗口标识>
win-manager window restore <窗口标识>
```

## ⚙️ 配置管理命令

### config show

显示当前配置：

```bash
win-manager config show [选项]
```

**选项：**
| 选项 | 说明 |
|------|------|
| `--key TEXT` | 显示特定配置项 |
| `--section TEXT` | 显示特定配置节 |

**示例：**
```bash
win-manager config show
win-manager config show --key window_management.default_layout
win-manager config show --section filters
```

### config set/get

设置和获取配置值：

```bash
win-manager config set <键> <值>
win-manager config get <键>
```

**常用配置键：**
- `window_management.default_layout`
- `filters.ignore_minimized`
- `filters.ignore_fixed_size`
- `hotkeys.grid_layout`

**示例：**
```bash
win-manager config set window_management.default_layout grid
win-manager config get filters.ignore_minimized
```

### config export/import

导出和导入配置：

```bash
win-manager config export <文件路径> [--format json|yaml]
win-manager config import <文件路径>
```

**示例：**
```bash
win-manager config export ./my-config.yaml --format yaml
win-manager config import ./backup-config.json
```

## 🔥 热键管理命令

### hotkey list

列出所有已注册的热键：

```bash
win-manager hotkey list
```

### hotkey add/remove

添加和移除热键：

```bash
win-manager hotkey add <热键组合> <动作> [--description <描述>]
win-manager hotkey remove <热键组合>
```

**热键格式：**
- `ctrl+alt+g`
- `ctrl+shift+c`
- `alt+f1`

**示例：**
```bash
win-manager hotkey add "ctrl+alt+g" "layout apply grid" --description "网格布局"
win-manager hotkey add "ctrl+alt+u" "layout undo" --description "撤销布局"
win-manager hotkey remove "ctrl+alt+g"
```

### hotkey start/stop

启动和停止热键监听：

```bash
win-manager hotkey start
win-manager hotkey stop
```

## 🛠️ 工具命令

### tool status

显示系统状态：

```bash
win-manager tool status
```

### tool test

运行系统测试：

```bash
win-manager tool test [--component <组件>] [--verbose]
```

### tool benchmark

运行性能基准测试：

```bash
win-manager tool benchmark [--windows <数量>] [--iterations <次数>]
```

**示例：**
```bash
win-manager tool benchmark --windows 100 --iterations 10
```

### tool cleanup

清理临时文件和缓存：

```bash
win-manager tool cleanup
```

## 🎯 简单CLI接口

除了完整CLI，还提供简单接口：

```bash
python src/win_manager/main.py [选项]
```

**选项：**
| 选项 | 说明 |
|------|------|
| `--layout LAYOUT` | 应用布局: cascade/grid/stack |
| `--list` | 列出所有窗口 |
| `--undo` | 撤销布局 |
| `--gui` | 启动GUI（未实现） |

**示例：**
```bash
python src/win_manager/main.py --layout grid
python src/win_manager/main.py --list
python src/win_manager/main.py --undo
```

## 📊 输出格式示例

### Table格式（默认）
```
┌─────────┬──────────────────┬─────────────┬────────────┐
│ 窗口ID   │ 标题              │ 进程名       │ 状态        │
├─────────┼──────────────────┼─────────────┼────────────┤
│ 1       │ Google Chrome    │ chrome.exe  │ 正常        │
└─────────┴──────────────────┴─────────────┴────────────┘
```

### JSON格式
```json
{
  "success": true,
  "data": {
    "windows": [
      {
        "id": 1,
        "title": "Google Chrome",
        "process": "chrome.exe",
        "rect": [100, 100, 800, 600]
      }
    ]
  }
}
```

### YAML格式
```yaml
success: true
data:
  windows:
    - id: 1
      title: Google Chrome
      process: chrome.exe
      rect: [100, 100, 800, 600]
```

## 🚨 错误代码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 配置错误 |
| 3 | 权限错误 |
| 4 | 资源不可用 |

## 💡 使用技巧

### 1. 批量操作
```bash
# 链式命令
win-manager grid && win-manager hotkey start
```

### 2. 脚本使用
```bash
# 获取JSON输出用于脚本处理
WINDOWS=$(win-manager --output json window list)
```

### 3. 别名设置
```bash
# 在.bashrc或PowerShell配置中添加
alias wm='win-manager'
alias wmg='win-manager grid'
alias wmc='win-manager cascade'
alias wmu='win-manager undo'
```

### 4. 配置模板
```bash
# 导出当前配置作为模板
win-manager config export ./config-template.yaml
```

---

**📚 相关文档：**
- [快速开始](quickstart.md) - 5分钟上手指南
- [用户手册](user-guide.md) - 完整功能说明
- [故障排除](troubleshooting.md) - 常见问题解决