# 📋 API 参考

Win-Manager 提供了完整的 Python API，可以让您在应用程序中集成窗口管理功能。本文档详细描述了所有可用的类、方法和接口。

## 📦 主要模块

### 1. 核心模块 (`win_manager.core`)
- **WindowManager** - 主要门面类，协调所有功能
- **WindowDetector** - 窗口发现和信息提取
- **WindowController** - 窗口位置和状态控制
- **LayoutEngine** - 布局算法引擎
- **ConfigManager** - 配置管理

### 2. 工具模块 (`win_manager.utils`)
- **HotkeyManager** - 全局热键管理
- **ExceptionHandler** - 异常处理和日志

### 3. CLI模块 (`win_manager.cli`)
- **CLI命令实现** - Click框架命令行接口

## 🏗️ WindowManager 类

主要的门面类，提供所有窗口管理功能的统一接口。

### 构造函数

```python
class WindowManager:
    def __init__(self)
```

**示例：**
```python
from win_manager.core.window_manager import WindowManager

manager = WindowManager()
```

### 核心方法

#### get_manageable_windows()
获取所有可管理的窗口列表。

```python
def get_manageable_windows(self) -> List[WindowInfo]
```

**返回值：** `List[WindowInfo]` - 窗口信息对象列表

**示例：**
```python
windows = manager.get_manageable_windows()
for window in windows:
    print(f"窗口: {window.title}, 进程: {window.process_name}")
```

#### organize_windows()
使用指定布局整理窗口。

```python
def organize_windows(
    self, 
    layout_name: Optional[str] = None, 
    **layout_options
) -> bool
```

**参数：**
- `layout_name` (str, 可选): 布局名称 (`"cascade"`, `"grid"`, `"stack"`)
- `**layout_options`: 布局特定选项

**返回值：** `bool` - 操作是否成功

**布局选项：**

**Grid布局：**
```python
manager.organize_windows("grid", columns=3, padding=15)
```

**Cascade布局：**
```python
manager.organize_windows("cascade", offset_x=40, offset_y=40)
```

**Stack布局：**
```python
manager.organize_windows("stack", 
    stack_position="center",
    window_width={"type": "percentage", "value": 80},
    window_height={"type": "pixels", "value": 600}
)
```

#### 便捷方法

```python
def cascade_windows(self) -> bool:
    """应用瀑布布局"""

def grid_windows(self) -> bool:
    """应用网格布局"""

def stack_windows(self) -> bool:
    """应用堆叠布局"""

def undo_layout(self) -> bool:
    """撤销最后一次布局更改"""
```

#### 窗口操作方法

```python
def focus_window(self, hwnd: int) -> bool:
    """将窗口置于前台"""

def minimize_window(self, hwnd: int) -> bool:
    """最小化窗口"""

def maximize_window(self, hwnd: int) -> bool:
    """最大化窗口"""

def restore_window(self, hwnd: int) -> bool:
    """恢复窗口"""
```

#### 信息获取方法

```python
def get_window_list(self) -> List[Dict[str, any]]:
    """获取所有窗口的详细信息"""

def get_available_layouts(self) -> List[str]:
    """获取可用布局列表"""

def get_config(self) -> ConfigManager:
    """获取配置管理器"""
```

## 🔍 WindowDetector 类

负责窗口发现和信息提取。

### 主要方法

```python
class WindowDetector:
    def enumerate_windows(self) -> List[WindowInfo]:
        """枚举所有窗口"""
    
    def get_window_info(self, hwnd: int) -> Optional[WindowInfo]:
        """获取指定窗口的信息"""
    
    def find_windows_by_title(self, title_pattern: str) -> List[WindowInfo]:
        """根据标题查找窗口"""
    
    def find_windows_by_process(self, process_name: str) -> List[WindowInfo]:
        """根据进程名查找窗口"""
```

### WindowInfo 数据类

```python
@dataclass
class WindowInfo:
    hwnd: int                    # 窗口句柄
    title: str                   # 窗口标题
    process_name: str            # 进程名
    pid: int                     # 进程ID
    rect: Tuple[int, int, int, int]  # 窗口矩形 (left, top, right, bottom)
    is_visible: bool             # 是否可见
    is_resizable: bool           # 是否可调整大小
```

## 🎮 WindowController 类

负责窗口的实际控制操作。

### 主要方法

```python
class WindowController:
    def move_window(self, hwnd: int, x: int, y: int, width: int, height: int) -> bool:
        """移动窗口到指定位置和大小"""
    
    def bring_to_front(self, hwnd: int) -> bool:
        """将窗口置于前台"""
    
    def minimize_window(self, hwnd: int) -> bool:
        """最小化窗口"""
    
    def maximize_window(self, hwnd: int) -> bool:
        """最大化窗口"""
    
    def restore_window(self, hwnd: int) -> bool:
        """恢复窗口"""
    
    def is_window_minimized(self, hwnd: int) -> bool:
        """检查窗口是否最小化"""
    
    def is_window_maximized(self, hwnd: int) -> bool:
        """检查窗口是否最大化"""
    
    def save_window_state(self, hwnd: int) -> bool:
        """保存窗口状态"""
    
    def restore_window_state(self, hwnd: int) -> bool:
        """恢复窗口状态"""
```

## 📐 LayoutEngine 类

布局算法引擎，支持多种布局策略。

### 主要方法

```python
class LayoutEngine:
    def apply_layout(
        self, 
        layout_name: str, 
        windows: List[WindowInfo], 
        **layout_options
    ) -> Dict[int, Tuple[int, int, int, int]]:
        """应用布局并返回位置映射"""
    
    def get_available_layouts(self) -> List[str]:
        """获取可用布局列表"""
    
    def add_custom_layout(self, name: str, layout: LayoutManager):
        """添加自定义布局"""
    
    def get_screen_rect(self) -> Tuple[int, int, int, int]:
        """获取主屏幕矩形"""
```

### 自定义布局

您可以通过继承 `LayoutManager` 创建自定义布局：

```python
from win_manager.core.layout_manager import LayoutManager

class CircleLayout(LayoutManager):
    """圆形布局示例"""
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        # 实现圆形布局算法
        positions = {}
        center_x = (screen_rect[2] - screen_rect[0]) // 2
        center_y = (screen_rect[3] - screen_rect[1]) // 2
        radius = 300
        
        for i, window in enumerate(windows):
            angle = 2 * math.pi * i / len(windows)
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            positions[window.hwnd] = (x, y, 400, 300)
        
        return positions

# 注册自定义布局
layout_engine = LayoutEngine()
layout_engine.add_custom_layout("circle", CircleLayout())
```

## ⚙️ ConfigManager 类

配置管理器，处理应用程序设置。

### 主要方法

```python
class ConfigManager:
    def get(self, key: str, default_value=None):
        """获取配置值"""
    
    def set(self, key: str, value):
        """设置配置值"""
    
    def get_excluded_processes(self) -> List[str]:
        """获取排除的进程列表"""
    
    def add_excluded_process(self, process_name: str):
        """添加排除的进程"""
    
    def remove_excluded_process(self, process_name: str):
        """移除排除的进程"""
    
    def save_config(self) -> bool:
        """保存配置到文件"""
    
    def load_config(self) -> bool:
        """从文件加载配置"""
    
    def reset_to_defaults(self):
        """重置为默认配置"""
```

### 配置键参考

**窗口管理设置：**
```python
config.get("window_management.default_layout", "cascade")
config.get("window_management.save_state", True)
config.get("window_management.auto_restore", True)
```

**过滤设置：**
```python
config.get("filters.ignore_minimized", True)
config.get("filters.ignore_fixed_size", True)
config.get("filters.min_window_size", [100, 100])
```

**布局设置：**
```python
config.get("layouts.grid.default_columns", 3)
config.get("layouts.grid.default_padding", 10)
config.get("layouts.cascade.offset_x", 30)
config.get("layouts.cascade.offset_y", 30)
```

## 🔥 HotkeyManager 类

全局热键管理器。

### 主要方法

```python
class HotkeyManager:
    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """注册全局热键"""
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """取消注册热键"""
    
    def start(self) -> bool:
        """启动热键监听"""
    
    def stop(self) -> bool:
        """停止热键监听"""
    
    def get_registered_hotkeys(self) -> list:
        """获取已注册的热键列表"""
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
```

### 热键格式

支持的热键格式：
- `"ctrl+alt+g"` - Ctrl + Alt + G
- `"ctrl+shift+w"` - Ctrl + Shift + W  
- `"alt+f1"` - Alt + F1
- `"win+d"` - Windows + D

### 使用示例

```python
from win_manager.utils.hotkey_manager import HotkeyManager
from win_manager.core.window_manager import WindowManager

hotkey_manager = HotkeyManager()
window_manager = WindowManager()

# 注册热键
hotkey_manager.register_hotkey(
    "ctrl+alt+g", 
    lambda: window_manager.grid_windows()
)

hotkey_manager.register_hotkey(
    "ctrl+alt+c", 
    lambda: window_manager.cascade_windows()
)

# 启动监听
hotkey_manager.start()
```

## 🚨 异常处理

### 常见异常类型

```python
class WindowOperationError(Exception):
    """窗口操作失败异常"""

class LayoutCalculationError(Exception):
    """布局计算失败异常"""

class ConfigurationError(Exception):
    """配置错误异常"""

class HotkeyRegistrationError(Exception):
    """热键注册失败异常"""
```

### 异常处理最佳实践

```python
from win_manager.core.window_manager import WindowManager
from win_manager.utils.exception_handler import exception_handler

@exception_handler
def organize_windows_safely():
    try:
        manager = WindowManager()
        result = manager.organize_windows("grid")
        if not result:
            print("布局应用失败")
    except WindowOperationError as e:
        print(f"窗口操作错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
```

## 📊 完整使用示例

### 基础使用

```python
from win_manager.core.window_manager import WindowManager

# 创建管理器
manager = WindowManager()

# 获取窗口列表
windows = manager.get_manageable_windows()
print(f"找到 {len(windows)} 个可管理窗口")

# 应用网格布局
success = manager.organize_windows("grid", columns=3, padding=15)
if success:
    print("网格布局应用成功")

# 撤销布局
manager.undo_layout()
```

### 高级使用 - 筛选特定窗口

```python
from win_manager.core.window_manager import WindowManager
from win_manager.core.window_detector import WindowDetector

manager = WindowManager()
detector = WindowDetector()

# 只管理Chrome窗口
chrome_windows = detector.find_windows_by_process("chrome.exe")
if chrome_windows:
    # 使用自定义方法应用布局
    layout_engine = manager.layout_engine
    positions = layout_engine.apply_layout("grid", chrome_windows, columns=2)
    
    # 应用位置
    controller = manager.controller
    for hwnd, (x, y, width, height) in positions.items():
        controller.move_window(hwnd, x, y, width, height)
```

### 配置和热键集成

```python
from win_manager.core.window_manager import WindowManager
from win_manager.utils.hotkey_manager import HotkeyManager

# 初始化
manager = WindowManager()
hotkey_manager = HotkeyManager()

# 配置设置
config = manager.get_config()
config.set("layouts.grid.default_columns", 4)
config.add_excluded_process("notepad.exe")

# 注册热键
hotkey_manager.register_hotkey("ctrl+alt+1", lambda: manager.grid_windows())
hotkey_manager.register_hotkey("ctrl+alt+2", lambda: manager.cascade_windows())
hotkey_manager.register_hotkey("ctrl+alt+u", lambda: manager.undo_layout())

# 启动热键服务
hotkey_manager.start()

print("窗口管理器已启动，热键已激活")
```

### 自定义布局实现

```python
import math
from win_manager.core.layout_manager import LayoutManager, LayoutEngine
from win_manager.core.window_detector import WindowInfo
from typing import List, Dict, Tuple

class DiagonalLayout(LayoutManager):
    """对角线布局 - 窗口沿对角线排列"""
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        window_width = 400
        window_height = 300
        step_x = (screen_right - screen_left - window_width) // (len(windows) + 1)
        step_y = (screen_bottom - screen_top - window_height) // (len(windows) + 1)
        
        for i, window in enumerate(windows):
            x = screen_left + step_x * (i + 1)
            y = screen_top + step_y * (i + 1)
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions

# 使用自定义布局
manager = WindowManager()
layout_engine = manager.layout_engine
layout_engine.add_custom_layout("diagonal", DiagonalLayout())

# 应用自定义布局
manager.organize_windows("diagonal")
```

## 🔗 类型提示

Win-Manager 完全支持类型提示，便于IDE自动完成和类型检查：

```python
from typing import List, Dict, Optional, Tuple, Callable
from win_manager.core.window_manager import WindowManager
from win_manager.core.window_detector import WindowInfo

def process_windows(manager: WindowManager) -> List[Dict[str, any]]:
    """处理窗口并返回信息列表"""
    windows: List[WindowInfo] = manager.get_manageable_windows()
    window_data: List[Dict[str, any]] = []
    
    for window in windows:
        data: Dict[str, any] = {
            "title": window.title,
            "process": window.process_name,
            "rect": window.rect
        }
        window_data.append(data)
    
    return window_data
```

---

**📚 相关文档：**
- [架构设计](architecture.md) - 系统设计原理
- [核心模块](core-modules.md) - 各模块详细说明
- [用户手册](../user/user-guide.md) - 功能使用指南
- [CLI参考](../user/cli-reference.md) - 命令行接口