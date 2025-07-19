# 📏 代码规范

本文档定义了 Win-Manager 项目的代码规范，确保代码的一致性、可读性和可维护性。

## 🎯 总体原则

1. **可读性优先**: 代码应该易于理解和维护
2. **一致性**: 遵循统一的编码风格
3. **简洁性**: 避免不必要的复杂性
4. **文档化**: 重要逻辑需要充分注释

## 🐍 Python 代码规范

### 基础规范
遵循 [PEP 8](https://pep8.org/) 标准，主要要点：

#### 缩进和空格
```python
# ✅ 正确 - 使用4个空格缩进
def process_windows(windows: List[WindowInfo]) -> bool:
    if not windows:
        return False
    
    for window in windows:
        process_single_window(window)
    
    return True

# ❌ 错误 - 使用Tab或不一致缩进
def process_windows(windows):
	if not windows:
  		return False
```

#### 行长度
```python
# ✅ 正确 - 行长度不超过88个字符
def calculate_grid_layout(
    windows: List[WindowInfo], 
    columns: int, 
    padding: int
) -> Dict[int, Tuple[int, int, int, int]]:
    pass

# ❌ 错误 - 行过长
def calculate_grid_layout(windows: List[WindowInfo], columns: int, padding: int) -> Dict[int, Tuple[int, int, int, int]]:
    pass
```

#### 导入语句
```python
# ✅ 正确 - 导入顺序: 标准库 → 第三方 → 本地
import os
import sys
from typing import List, Dict, Optional

import win32gui
import win32con
from click import command, option

from win_manager.core.window_detector import WindowInfo
from win_manager.utils.exception_handler import exception_handler

# ❌ 错误 - 混乱的导入顺序
from win_manager.core.window_detector import WindowInfo
import os
import win32gui
import sys
```

### 命名规范

#### 变量和函数
```python
# ✅ 正确 - snake_case
window_count = len(windows)
process_name = "chrome.exe"

def get_manageable_windows() -> List[WindowInfo]:
    pass

def calculate_window_position(index: int, grid_params: GridParams) -> Tuple[int, int]:
    pass

# ❌ 错误 - camelCase 或其他风格
windowCount = len(windows)
processName = "chrome.exe"

def getManageableWindows():
    pass
```

#### 类名
```python
# ✅ 正确 - PascalCase
class WindowManager:
    pass

class LayoutEngine:
    pass

class ConfigurationError(Exception):
    pass

# ❌ 错误 - snake_case 或其他风格
class window_manager:
    pass

class layout_Engine:
    pass
```

#### 常量
```python
# ✅ 正确 - SCREAMING_SNAKE_CASE
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
MAX_UNDO_LEVELS = 50

# 模块级常量放在文件顶部
SYSTEM_PROCESSES = [
    "dwm.exe",
    "explorer.exe", 
    "winlogon.exe"
]

# ❌ 错误 - 小写或其他风格
default_window_width = 800
maxUndoLevels = 50
```

### 类型提示

#### 必须使用类型提示
```python
# ✅ 正确 - 完整的类型提示
from typing import List, Dict, Optional, Tuple, Union

def move_window(
    hwnd: int, 
    x: int, 
    y: int, 
    width: int, 
    height: int
) -> bool:
    """移动窗口到指定位置."""
    pass

def get_window_info(hwnd: int) -> Optional[WindowInfo]:
    """获取窗口信息，如果窗口不存在返回None."""
    pass

# ❌ 错误 - 缺少类型提示
def move_window(hwnd, x, y, width, height):
    pass

def get_window_info(hwnd):
    pass
```

#### 复杂类型的定义
```python
# ✅ 正确 - 使用类型别名提高可读性
from typing import TypeAlias

WindowRect: TypeAlias = Tuple[int, int, int, int]
PositionMap: TypeAlias = Dict[int, WindowRect]
WindowFilter: TypeAlias = Callable[[WindowInfo], bool]

def apply_layout(
    layout_name: str, 
    windows: List[WindowInfo]
) -> PositionMap:
    pass
```

### 文档字符串

#### 函数文档
```python
# ✅ 正确 - Google风格文档字符串
def calculate_grid_layout(
    windows: List[WindowInfo], 
    columns: Optional[int] = None,
    padding: int = 10
) -> Dict[int, Tuple[int, int, int, int]]:
    """计算网格布局的窗口位置.
    
    根据指定的列数和间距，计算所有窗口在网格中的位置。
    如果不指定列数，将根据窗口数量和屏幕比例自动计算最优列数。
    
    Args:
        windows: 需要排列的窗口列表
        columns: 网格列数，None表示自动计算
        padding: 窗口间的间距，单位像素
        
    Returns:
        字典，键为窗口句柄，值为(x, y, width, height)元组
        
    Raises:
        ValueError: 当列数小于1时
        
    Example:
        >>> windows = [window1, window2, window3]
        >>> positions = calculate_grid_layout(windows, columns=2)
        >>> print(len(positions))
        3
    """
    pass

# ❌ 错误 - 缺少或不完整的文档
def calculate_grid_layout(windows, columns=None, padding=10):
    # Calculate grid layout
    pass
```

#### 类文档
```python
# ✅ 正确 - 完整的类文档
class WindowManager:
    """窗口管理器主类.
    
    WindowManager是系统的核心类，实现了门面模式，为窗口管理
    的各个子系统提供统一的接口。负责协调窗口检测、布局计算、
    窗口控制等核心功能。
    
    Attributes:
        detector: 窗口检测器实例
        controller: 窗口控制器实例
        layout_engine: 布局引擎实例
        config: 配置管理器实例
        
    Example:
        >>> manager = WindowManager()
        >>> windows = manager.get_manageable_windows()
        >>> success = manager.organize_windows("grid")
    """
    
    def __init__(self):
        """初始化窗口管理器."""
        self.detector = WindowDetector()
        self.controller = WindowController()
        self.layout_engine = LayoutEngine()
        self.config = ConfigManager()
```

### 异常处理

#### 具体的异常类型
```python
# ✅ 正确 - 捕获具体异常
def get_window_info(hwnd: int) -> Optional[WindowInfo]:
    """获取窗口信息."""
    try:
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return WindowInfo(hwnd, title, get_process_name(pid), ...)
    except win32gui.error as e:
        logger.warning(f"Failed to get window info for {hwnd}: {e}")
        return None
    except OSError as e:
        logger.error(f"System error when accessing window {hwnd}: {e}")
        return None

# ❌ 错误 - 捕获所有异常
def get_window_info(hwnd):
    try:
        # ... 代码 ...
        return window_info
    except:  # 太宽泛的异常捕获
        return None
```

#### 自定义异常
```python
# ✅ 正确 - 定义有意义的异常类
class WindowOperationError(Exception):
    """窗口操作失败异常."""
    
    def __init__(self, hwnd: int, operation: str, reason: str):
        self.hwnd = hwnd
        self.operation = operation
        self.reason = reason
        super().__init__(f"Window {hwnd} {operation} failed: {reason}")

class LayoutCalculationError(Exception):
    """布局计算失败异常."""
    pass

class ConfigurationError(Exception):
    """配置错误异常."""
    pass

# 使用自定义异常
def move_window(hwnd: int, x: int, y: int, width: int, height: int) -> None:
    """移动窗口."""
    if not win32gui.IsWindow(hwnd):
        raise WindowOperationError(hwnd, "move", "Invalid window handle")
    
    result = win32gui.SetWindowPos(hwnd, 0, x, y, width, height, flags)
    if not result:
        raise WindowOperationError(hwnd, "move", "SetWindowPos failed")
```

### 日志记录

#### 正确的日志使用
```python
import logging

# ✅ 正确 - 使用模块级logger
logger = logging.getLogger(__name__)

class WindowDetector:
    """窗口检测器."""
    
    def enumerate_windows(self) -> List[WindowInfo]:
        """枚举所有窗口."""
        logger.info("Starting window enumeration")
        windows = []
        
        try:
            # 枚举逻辑
            logger.debug(f"Found {len(windows)} total windows")
            
            # 过滤逻辑
            filtered_windows = self._filter_windows(windows)
            logger.info(f"Filtered to {len(filtered_windows)} manageable windows")
            
            return filtered_windows
            
        except Exception as e:
            logger.error(f"Window enumeration failed: {e}", exc_info=True)
            raise

# ❌ 错误 - 使用print或root logger
def enumerate_windows():
    print("Starting enumeration")  # 不要使用print
    logging.error("Error occurred")  # 不要使用root logger
```

#### 日志级别使用
```python
# ✅ 正确 - 合适的日志级别
logger.debug("Detailed debugging information")  # 调试信息
logger.info("Normal operation completed")       # 一般信息
logger.warning("Something unexpected happened") # 警告
logger.error("Operation failed")                # 错误
logger.critical("System cannot continue")       # 严重错误

# ❌ 错误 - 错误的日志级别
logger.error("Window enumeration started")      # 应该用info
logger.info("Critical system failure")          # 应该用critical
```

## 🏗️ 架构规范

### 模块组织
```python
# ✅ 正确 - 清晰的模块结构
win_manager/
├── core/                 # 核心业务逻辑
│   ├── __init__.py
│   ├── window_manager.py
│   ├── window_detector.py
│   ├── window_controller.py
│   └── layout_manager.py
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── exception_handler.py
│   └── hotkey_manager.py
└── cli/                  # CLI接口
    ├── __init__.py
    ├── main.py
    └── commands/
```

### 依赖注入
```python
# ✅ 正确 - 构造函数依赖注入
class WindowManager:
    """窗口管理器."""
    
    def __init__(
        self,
        detector: Optional[WindowDetector] = None,
        controller: Optional[WindowController] = None,
        layout_engine: Optional[LayoutEngine] = None
    ):
        self.detector = detector or WindowDetector()
        self.controller = controller or WindowController()
        self.layout_engine = layout_engine or LayoutEngine()

# ❌ 错误 - 硬编码依赖
class WindowManager:
    def __init__(self):
        self.detector = WindowDetector()  # 硬编码，难以测试
        self.controller = WindowController()
```

### 接口设计
```python
# ✅ 正确 - 清晰的抽象接口
from abc import ABC, abstractmethod

class LayoutStrategy(ABC):
    """布局策略抽象基类."""
    
    @abstractmethod
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        """计算窗口位置."""
        pass

class GridLayout(LayoutStrategy):
    """网格布局实现."""
    
    def calculate_positions(self, windows, screen_rect):
        # 具体实现
        pass
```

## 🧪 测试规范

### 测试文件组织
```python
# ✅ 正确 - 测试文件命名和组织
tests/
├── test_window_manager.py        # 对应 window_manager.py
├── test_window_detector.py       # 对应 window_detector.py
├── test_layout_manager.py        # 对应 layout_manager.py
├── integration/                  # 集成测试
│   ├── test_full_workflow.py
│   └── test_cli_integration.py
└── fixtures/                     # 测试数据
    ├── __init__.py
    └── window_data.py
```

### 测试函数命名
```python
# ✅ 正确 - 描述性的测试名称
def test_get_manageable_windows_returns_empty_list_when_no_windows():
    """测试没有窗口时返回空列表."""
    pass

def test_grid_layout_calculates_correct_positions_for_4_windows():
    """测试网格布局为4个窗口计算正确位置."""
    pass

def test_window_manager_raises_error_when_invalid_layout_specified():
    """测试指定无效布局时抛出异常."""
    pass

# ❌ 错误 - 不清晰的测试名称
def test_windows():
    pass

def test_layout():
    pass

def test_error():
    pass
```

### 测试结构
```python
# ✅ 正确 - 清晰的测试结构
def test_grid_layout_with_4_windows_and_2_columns():
    """测试4个窗口2列的网格布局."""
    # Arrange - 准备测试数据
    windows = create_test_windows(4)
    layout = GridLayout(columns=2, padding=10)
    screen_rect = (0, 0, 1920, 1080)
    
    # Act - 执行被测试的操作
    positions = layout.calculate_positions(windows, screen_rect)
    
    # Assert - 验证结果
    assert len(positions) == 4
    assert all(isinstance(pos, tuple) and len(pos) == 4 for pos in positions.values())
    
    # 验证网格排列
    hwnd1, hwnd2 = windows[0].hwnd, windows[1].hwnd
    x1, y1, _, _ = positions[hwnd1]
    x2, y2, _, _ = positions[hwnd2]
    assert x2 > x1  # 第二个窗口在右侧
    assert y1 == y2  # 同一行
```

## 🔧 工具配置

### pre-commit 钩子
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
```

### pyproject.toml 配置
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
```

## 📝 提交规范

### Commit 消息格式
```bash
# ✅ 正确 - 使用约定式提交
feat: add circular layout algorithm
fix: resolve window enumeration memory leak
docs: update API documentation for LayoutEngine
test: add unit tests for ConfigManager
refactor: simplify window filtering logic

# ❌ 错误 - 不清晰的提交消息
Update code
Fix bug
Add stuff
```

### 分支命名
```bash
# ✅ 正确 - 清晰的分支命名
feature/circular-layout
bugfix/memory-leak-enumeration
hotfix/critical-crash-issue
docs/api-documentation-update

# ❌ 错误 - 模糊的分支命名
my-changes
fix
update
branch1
```

---

**📚 相关文档：**
- [开发环境](development-setup.md) - 开发环境配置
- [测试指南](testing-guide.md) - 测试编写指南
- [架构设计](../developer/architecture.md) - 系统架构设计
- [API参考](../developer/api-reference.md) - API使用文档