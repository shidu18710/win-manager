# 🔧 核心模块详解

Win-Manager 采用模块化设计，每个核心模块都有明确的职责和清晰的接口。本文档深入探讨各个核心模块的实现细节、设计决策和扩展方法。

## 📋 模块概览

```
win_manager/
├── core/                    # 核心业务逻辑
│   ├── window_manager.py    # 主要门面类
│   ├── window_detector.py   # 窗口发现和枚举
│   ├── window_controller.py # 窗口控制和操作
│   ├── layout_manager.py    # 布局引擎和策略
│   └── config_manager.py    # 配置管理
├── utils/                   # 工具和支持服务
│   ├── hotkey_manager.py    # 全局热键管理
│   └── exception_handler.py # 异常处理装饰器
└── cli/                     # 命令行接口
    ├── main.py              # CLI入口点
    ├── commands/            # 命令实现
    └── utils/               # CLI工具
```

## 🏗️ window_manager.py - 门面模块

### 设计原理

`WindowManager` 类实现了门面模式(Facade Pattern)，为复杂的窗口管理子系统提供了简化的统一接口。

### 核心职责

1. **子系统协调**: 协调所有核心组件的交互
2. **业务流程管理**: 管理完整的窗口操作流程
3. **状态管理**: 维护操作历史用于撤销功能
4. **错误处理**: 统一的异常处理和日志记录

### 关键实现细节

#### 1. 组件初始化
```python
def __init__(self):
    self.detector = WindowDetector()       # 窗口检测器
    self.controller = WindowController()   # 窗口控制器
    self.layout_engine = LayoutEngine()    # 布局引擎
    self.config = ConfigManager()          # 配置管理器
    
    # 日志配置
    log_level = getattr(logging, self.config.get("advanced.log_level", "INFO"))
    logging.basicConfig(level=log_level)
    self.logger = logging.getLogger(__name__)
```

#### 2. 窗口过滤逻辑
```python
def get_manageable_windows(self) -> List[WindowInfo]:
    """智能窗口过滤算法"""
    all_windows = self.detector.enumerate_windows()
    manageable_windows = []
    
    # 配置驱动的过滤规则
    ignore_fixed_size = self.config.get("filters.ignore_fixed_size", True)
    ignore_minimized = self.config.get("filters.ignore_minimized", True)
    excluded_processes = self.config.get_excluded_processes()
    
    for window in all_windows:
        # 多层次过滤策略
        if self._should_exclude_window(window, excluded_processes, 
                                     ignore_fixed_size, ignore_minimized):
            continue
        manageable_windows.append(window)
    
    return manageable_windows
```

#### 3. 布局应用流程
```python
def organize_windows(self, layout_name: Optional[str] = None, **layout_options) -> bool:
    """完整的布局应用流程"""
    try:
        # 1. 获取目标窗口
        windows = self.get_manageable_windows()
        if not windows:
            return False
        
        # 2. 计算布局位置
        positions = self.layout_engine.apply_layout(layout_name, windows, **layout_options)
        
        # 3. 批量应用位置
        success_count = 0
        for hwnd, (x, y, width, height) in positions.items():
            if self.controller.move_window(hwnd, x, y, width, height):
                success_count += 1
        
        # 4. 记录结果
        self.logger.info(f"Successfully organized {success_count}/{len(windows)} windows")
        return success_count > 0
        
    except Exception as e:
        self.logger.error(f"Error organizing windows: {e}")
        return False
```

### 扩展点

1. **新的窗口操作**: 在 `WindowManager` 中添加新的高级操作
2. **业务流程定制**: 修改 `organize_windows` 的流程
3. **状态管理扩展**: 增强撤销功能，支持多步撤销

## 🔍 window_detector.py - 窗口检测模块

### 设计原理

`WindowDetector` 专注于窗口发现、信息提取和初步过滤，封装了Windows API的复杂性。

### 核心技术

#### 1. 高性能窗口枚举
```python
def enumerate_windows(self) -> List[WindowInfo]:
    """优化的窗口枚举算法"""
    windows = []
    
    def enum_window_proc(hwnd, lparam):
        try:
            # 快速预过滤
            if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                return True
            
            # 提取窗口信息
            window_info = self._extract_window_info(hwnd)
            if window_info:
                windows.append(window_info)
                
        except Exception as e:
            # 静默处理异常，继续枚举
            pass
        return True
    
    # 使用Windows API枚举
    win32gui.EnumWindows(enum_window_proc, 0)
    return windows
```

#### 2. 窗口信息提取
```python
def _extract_window_info(self, hwnd: int) -> Optional[WindowInfo]:
    """提取完整窗口信息"""
    try:
        # 基本信息
        title = win32gui.GetWindowText(hwnd)
        if not title.strip():  # 跳过无标题窗口
            return None
        
        # 进程信息
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = self._get_process_name(pid)
        
        # 窗口矩形
        rect = win32gui.GetWindowRect(hwnd)
        
        # 窗口状态
        is_visible = win32gui.IsWindowVisible(hwnd)
        is_resizable = self._check_resizable(hwnd)
        
        return WindowInfo(
            hwnd=hwnd,
            title=title,
            process_name=process_name,
            pid=pid,
            rect=rect,
            is_visible=is_visible,
            is_resizable=is_resizable
        )
    except Exception:
        return None
```

#### 3. 智能过滤系统
```python
def _should_exclude_window(self, window: WindowInfo) -> bool:
    """多维度窗口过滤"""
    # 1. 尺寸过滤
    left, top, right, bottom = window.rect
    if (right - left) < 100 or (bottom - top) < 100:
        return True
    
    # 2. 系统窗口过滤
    system_classes = ['Shell_TrayWnd', 'DV2ControlHost', 'MsgrIMEWindowClass']
    window_class = win32gui.GetClassName(window.hwnd)
    if window_class in system_classes:
        return True
    
    # 3. 特殊标题过滤
    invisible_titles = ['Default IME', 'MSCTFIME UI', '']
    if window.title in invisible_titles:
        return True
    
    return False
```

### 性能优化

#### 1. 缓存机制
```python
class WindowDetector:
    def __init__(self):
        self._cache = {}
        self._cache_timestamp = 0
        self._cache_timeout = 100  # ms
    
    @lru_cache(maxsize=256)
    def _get_process_name(self, pid: int) -> str:
        """缓存进程名查询"""
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown"
```

#### 2. 异步枚举(可选)
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def enumerate_windows_async(self) -> List[WindowInfo]:
    """异步窗口枚举"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, self.enumerate_windows)
```

## 🎮 window_controller.py - 窗口控制模块

### 设计原理

`WindowController` 负责所有的窗口操作，包括移动、调整大小、状态变更等，并提供操作历史以支持撤销功能。

### 核心功能

#### 1. 原子性窗口操作
```python
def move_window(self, hwnd: int, x: int, y: int, width: int, height: int) -> bool:
    """原子性窗口移动操作"""
    try:
        # 1. 验证窗口句柄
        if not win32gui.IsWindow(hwnd):
            return False
        
        # 2. 保存当前状态(用于撤销)
        self.save_window_state(hwnd)
        
        # 3. 应用新位置
        result = win32gui.SetWindowPos(
            hwnd, 0, x, y, width, height,
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE
        )
        
        # 4. 验证操作结果
        if result:
            self.logger.debug(f"Moved window {hwnd} to ({x}, {y}, {width}, {height})")
        
        return bool(result)
        
    except Exception as e:
        self.logger.error(f"Failed to move window {hwnd}: {e}")
        return False
```

#### 2. 批量操作优化
```python
def batch_move_windows(self, moves: List[Tuple[int, int, int, int, int]]) -> BatchResult:
    """批量窗口移动，提高性能"""
    successful_moves = []
    failed_moves = []
    
    # 预处理：验证所有窗口句柄
    valid_moves = [(hwnd, x, y, w, h) for hwnd, x, y, w, h in moves 
                   if win32gui.IsWindow(hwnd)]
    
    # 批量保存状态
    for hwnd, _, _, _, _ in valid_moves:
        self.save_window_state(hwnd)
    
    # 批量移动
    for hwnd, x, y, width, height in valid_moves:
        try:
            if self._move_window_impl(hwnd, x, y, width, height):
                successful_moves.append(hwnd)
            else:
                failed_moves.append(hwnd)
        except Exception as e:
            failed_moves.append(hwnd)
            self.logger.error(f"Batch move failed for window {hwnd}: {e}")
    
    return BatchResult(successful_moves, failed_moves)
```

#### 3. 状态管理系统
```python
class WindowState:
    """窗口状态快照"""
    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self.rect = win32gui.GetWindowRect(hwnd)
        self.is_maximized = win32gui.IsZoomed(hwnd)
        self.is_minimized = win32gui.IsIconic(hwnd)
        self.timestamp = time.time()

class WindowController:
    def __init__(self):
        self.window_states: Dict[int, WindowState] = {}
    
    def save_window_state(self, hwnd: int) -> bool:
        """保存窗口状态快照"""
        try:
            self.window_states[hwnd] = WindowState(hwnd)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save state for window {hwnd}: {e}")
            return False
    
    def restore_window_state(self, hwnd: int) -> bool:
        """恢复窗口状态"""
        if hwnd not in self.window_states:
            return False
        
        state = self.window_states[hwnd]
        try:
            if state.is_maximized:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            elif state.is_minimized:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            else:
                x, y, right, bottom = state.rect
                width, height = right - x, bottom - y
                return self.move_window(hwnd, x, y, width, height)
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore state for window {hwnd}: {e}")
            return False
```

## 📐 layout_manager.py - 布局引擎模块

### 设计原理

`LayoutEngine` 采用策略模式实现不同的布局算法，使系统易于扩展新的布局类型。

### 策略模式实现

#### 1. 抽象策略接口
```python
from abc import ABC, abstractmethod

class LayoutManager(ABC):
    """布局策略抽象基类"""
    
    @abstractmethod
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        """计算窗口位置的抽象方法"""
        pass
```

#### 2. 具体策略实现

**网格布局策略**:
```python
class GridLayout(LayoutManager):
    """网格布局 - 智能网格分布算法"""
    
    def __init__(self, columns: Optional[int] = None, padding: int = 10):
        self.columns = columns
        self.padding = padding
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        window_count = len(windows)
        
        if window_count == 0:
            return positions
        
        # 智能列数计算
        if self.columns is None:
            # 基于黄金比例的智能布局
            screen_width = screen_rect[2] - screen_rect[0]
            screen_height = screen_rect[3] - screen_rect[1]
            aspect_ratio = screen_width / screen_height
            
            # 优化列数选择
            columns = max(1, int(math.sqrt(window_count * aspect_ratio)))
        else:
            columns = self.columns
        
        rows = (window_count + columns - 1) // columns
        
        # 动态尺寸计算
        available_width = screen_rect[2] - screen_rect[0] - (self.padding * (columns + 1))
        available_height = screen_rect[3] - screen_rect[1] - (self.padding * (rows + 1))
        
        window_width = max(200, available_width // columns)
        window_height = max(150, available_height // rows)
        
        # 位置分配
        for i, window in enumerate(windows):
            row = i // columns
            col = i % columns
            
            x = screen_rect[0] + self.padding + col * (window_width + self.padding)
            y = screen_rect[1] + self.padding + row * (window_height + self.padding)
            
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions
```

**瀑布布局策略**:
```python
class CascadeLayout(LayoutManager):
    """瀑布布局 - 层叠展示算法"""
    
    def __init__(self, offset_x: int = 30, offset_y: int = 30):
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        # 计算标准窗口大小 (屏幕的70%)
        window_width = int((screen_right - screen_left) * 0.7)
        window_height = int((screen_bottom - screen_top) * 0.7)
        
        # 计算最大偏移次数
        max_offset_x = (screen_right - screen_left - window_width) // self.offset_x
        max_offset_y = (screen_bottom - screen_top - window_height) // self.offset_y
        max_offsets = min(max_offset_x, max_offset_y)
        
        for i, window in enumerate(windows):
            # 循环偏移，防止窗口超出屏幕
            offset_count = i % (max_offsets + 1)
            
            x = screen_left + (offset_count * self.offset_x)
            y = screen_top + (offset_count * self.offset_y)
            
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions
```

#### 3. 策略管理器
```python
class LayoutEngine:
    """布局引擎 - 策略管理和执行"""
    
    def __init__(self):
        self.strategies = {
            "cascade": CascadeLayout(),
            "grid": GridLayout(),
            "stack": StackLayout()
        }
    
    def apply_layout(
        self, 
        layout_name: str, 
        windows: List[WindowInfo], 
        **layout_options
    ) -> Dict[int, Tuple[int, int, int, int]]:
        """动态策略选择和参数注入"""
        if layout_name not in self.strategies:
            raise ValueError(f"Unknown layout: {layout_name}")
        
        # 动态创建策略实例以支持参数自定义
        strategy = self._create_strategy_with_options(layout_name, layout_options)
        screen_rect = self.get_screen_rect()
        
        return strategy.calculate_positions(windows, screen_rect)
    
    def _create_strategy_with_options(self, layout_name: str, options: dict) -> LayoutManager:
        """根据选项创建策略实例"""
        if layout_name == "grid":
            return GridLayout(
                columns=options.get("columns"),
                padding=options.get("padding", 10)
            )
        elif layout_name == "cascade":
            return CascadeLayout(
                offset_x=options.get("offset_x", 30),
                offset_y=options.get("offset_y", 30)
            )
        elif layout_name == "stack":
            return StackLayout(
                stack_position=options.get("stack_position", "center"),
                window_width=options.get("window_width"),
                window_height=options.get("window_height")
            )
        else:
            return self.strategies[layout_name]
```

### 扩展新布局

```python
class CircularLayout(LayoutManager):
    """圆形布局示例"""
    
    def __init__(self, radius: int = 300):
        self.radius = radius
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        window_count = len(windows)
        
        if window_count == 0:
            return positions
        
        # 计算屏幕中心
        center_x = (screen_rect[0] + screen_rect[2]) // 2
        center_y = (screen_rect[1] + screen_rect[3]) // 2
        
        # 计算每个窗口的角度
        angle_step = 2 * math.pi / window_count
        
        for i, window in enumerate(windows):
            angle = i * angle_step
            
            # 极坐标转换为笛卡尔坐标
            x = center_x + int(self.radius * math.cos(angle)) - 200
            y = center_y + int(self.radius * math.sin(angle)) - 150
            
            positions[window.hwnd] = (x, y, 400, 300)
        
        return positions

# 注册新布局
layout_engine = LayoutEngine()
layout_engine.add_custom_layout("circular", CircularLayout())
```

## ⚙️ config_manager.py - 配置管理模块

### 设计原理

`ConfigManager` 提供层次化配置管理，支持默认值、用户自定义、运行时修改等特性。

### 配置系统架构

#### 1. 分层配置结构
```python
class ConfigManager:
    """分层配置管理器"""
    
    def __init__(self):
        self.default_config = self._load_default_config()
        self.user_config = self._load_user_config()
        self.runtime_config = {}
    
    def get(self, key: str, default_value=None):
        """分层查找配置值"""
        # 优先级: runtime > user > default > parameter
        for config_layer in [self.runtime_config, self.user_config, self.default_config]:
            if self._has_nested_key(config_layer, key):
                return self._get_nested_value(config_layer, key)
        
        return default_value
    
    def _get_nested_value(self, config: dict, key: str):
        """支持点号分隔的嵌套键访问"""
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
```

#### 2. 默认配置定义
```python
def _load_default_config(self) -> dict:
    """加载默认配置"""
    return {
        "window_management": {
            "default_layout": "cascade",
            "save_state": True,
            "auto_restore": True,
            "max_undo_levels": 10
        },
        "filters": {
            "ignore_minimized": True,
            "ignore_fixed_size": True,
            "min_window_size": [100, 100],
            "excluded_processes": [
                "dwm.exe", "explorer.exe", "winlogon.exe",
                "csrss.exe", "smss.exe", "wininit.exe"
            ]
        },
        "layouts": {
            "grid": {
                "default_columns": 3,
                "default_padding": 10,
                "min_window_size": [200, 150]
            },
            "cascade": {
                "offset_x": 30,
                "offset_y": 30,
                "window_size_ratio": 0.7
            },
            "stack": {
                "default_position": "center",
                "default_size_ratio": 0.8
            }
        },
        "hotkeys": {
            "enabled": True,
            "bindings": {
                "grid_layout": "ctrl+alt+g",
                "cascade_layout": "ctrl+alt+c",
                "stack_layout": "ctrl+alt+s",
                "undo": "ctrl+alt+u"
            }
        },
        "advanced": {
            "log_level": "INFO",
            "performance_mode": False,
            "cache_window_info": True,
            "batch_operations": True
        }
    }
```

#### 3. 配置文件管理
```python
def _get_config_path(self) -> str:
    """获取配置文件路径"""
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.environ.get('USERPROFILE', ''), '.win-manager')
    else:
        config_dir = os.path.join(os.path.expanduser('~'), '.win-manager')
    
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'config.json')

def save_config(self) -> bool:
    """保存配置到文件"""
    try:
        config_path = self._get_config_path()
        
        # 合并用户配置和运行时修改
        merged_config = self._merge_configs(self.user_config, self.runtime_config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, indent=2, ensure_ascii=False)
        
        # 更新用户配置
        self.user_config = merged_config
        self.runtime_config = {}
        
        return True
    except Exception as e:
        self.logger.error(f"Failed to save config: {e}")
        return False

def _load_user_config(self) -> dict:
    """从文件加载用户配置"""
    try:
        config_path = self._get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        self.logger.warning(f"Failed to load user config: {e}")
    
    return {}
```

### 配置验证和类型转换

```python
def set(self, key: str, value, validate: bool = True):
    """设置配置值，支持验证"""
    if validate:
        value = self._validate_and_convert(key, value)
    
    self._set_nested_value(self.runtime_config, key, value)

def _validate_and_convert(self, key: str, value):
    """配置值验证和类型转换"""
    validation_rules = {
        "layouts.grid.default_columns": (int, lambda x: 1 <= x <= 10),
        "layouts.cascade.offset_x": (int, lambda x: 0 <= x <= 100),
        "window_management.max_undo_levels": (int, lambda x: 1 <= x <= 50),
        "filters.min_window_size": (list, lambda x: len(x) == 2 and all(isinstance(i, int) for i in x))
    }
    
    if key in validation_rules:
        expected_type, validator = validation_rules[key]
        
        # 类型转换
        if not isinstance(value, expected_type):
            value = expected_type(value)
        
        # 值验证
        if not validator(value):
            raise ValueError(f"Invalid value for {key}: {value}")
    
    return value
```

## 🔥 hotkey_manager.py - 热键管理模块

### 设计原理

`HotkeyManager` 提供全局热键注册和监听功能，支持多种热键组合和自定义回调。

### 关键技术实现

#### 1. 热键解析和标准化
```python
def _parse_hotkey(self, hotkey: str) -> Optional[str]:
    """热键字符串解析和标准化"""
    try:
        # 分割和清理
        parts = [part.strip().lower() for part in hotkey.split('+')]
        
        # 标准化修饰键名称
        normalized_parts = []
        key_mapping = {
            'ctrl': 'ctrl', 'control': 'ctrl',
            'alt': 'alt', 'option': 'alt',
            'shift': 'shift',
            'win': 'win', 'windows': 'win', 'cmd': 'win', 'super': 'win'
        }
        
        for part in parts:
            normalized_parts.append(key_mapping.get(part, part))
        
        # 排序确保一致性
        normalized_parts.sort()
        return '+'.join(normalized_parts)
        
    except Exception:
        return None
```

#### 2. 全局键盘监听
```python
def _on_press(self, key):
    """按键事件处理"""
    try:
        key_str = self._key_to_string(key)
        if key_str:
            self.pressed_keys.add(key_str)
            
            # 检查热键组合
            current_combo = '+'.join(sorted(self.pressed_keys))
            if current_combo in self.hotkeys:
                # 在独立线程中执行回调，避免阻塞
                threading.Thread(
                    target=self._execute_hotkey_callback,
                    args=(current_combo,),
                    daemon=True
                ).start()
                
    except Exception as e:
        self.logger.error(f"Error in key press handler: {e}")

def _execute_hotkey_callback(self, combo: str):
    """执行热键回调"""
    try:
        callback = self.hotkeys[combo]
        callback()
    except Exception as e:
        self.logger.error(f"Error executing hotkey callback for {combo}: {e}")
```

#### 3. 线程安全的热键管理
```python
import threading
from threading import Lock

class HotkeyManager:
    def __init__(self):
        self.hotkeys: Dict[str, Callable] = {}
        self.listener: Optional[Listener] = None
        self.pressed_keys = set()
        self.running = False
        self._lock = Lock()  # 线程同步锁
    
    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """线程安全的热键注册"""
        with self._lock:
            parsed_hotkey = self._parse_hotkey(hotkey)
            if parsed_hotkey:
                self.hotkeys[parsed_hotkey] = callback
                return True
            return False
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """线程安全的热键注销"""
        with self._lock:
            parsed_hotkey = self._parse_hotkey(hotkey)
            if parsed_hotkey and parsed_hotkey in self.hotkeys:
                del self.hotkeys[parsed_hotkey]
                return True
            return False
```

## 📊 性能监控和优化

### 性能度量

```python
import time
import functools
from typing import Dict

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def measure_time(self, operation_name: str):
        """装饰器：测量方法执行时间"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                
                execution_time = end_time - start_time
                if operation_name not in self.metrics:
                    self.metrics[operation_name] = []
                self.metrics[operation_name].append(execution_time)
                
                return result
            return wrapper
        return decorator
    
    def get_average_time(self, operation_name: str) -> float:
        """获取平均执行时间"""
        if operation_name in self.metrics:
            times = self.metrics[operation_name]
            return sum(times) / len(times)
        return 0.0

# 使用示例
monitor = PerformanceMonitor()

@monitor.measure_time("window_enumeration")
def enumerate_windows(self) -> List[WindowInfo]:
    # 窗口枚举实现
    pass
```

### 内存优化

```python
class OptimizedWindowInfo:
    """优化的窗口信息类"""
    __slots__ = ['hwnd', 'title', 'process_name', 'pid', 'rect', 'is_visible', 'is_resizable']
    
    def __init__(self, hwnd: int, title: str, process_name: str, pid: int, 
                 rect: tuple, is_visible: bool, is_resizable: bool):
        self.hwnd = hwnd
        self.title = title
        self.process_name = process_name
        self.pid = pid
        self.rect = rect
        self.is_visible = is_visible
        self.is_resizable = is_resizable
```

## 🔧 扩展和自定义

### 添加新的布局算法

```python
class HexagonLayout(LayoutManager):
    """六边形布局示例"""
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        
        # 六边形布局实现
        # ... 算法实现
        
        return positions

# 注册到引擎
layout_engine.add_custom_layout("hexagon", HexagonLayout())
```

### 自定义窗口过滤器

```python
class CustomWindowFilter:
    """自定义窗口过滤器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def should_include_window(self, window: WindowInfo) -> bool:
        """自定义过滤逻辑"""
        # 自定义过滤规则
        if window.process_name in ['chrome.exe', 'firefox.exe']:
            return True
        
        if 'Visual Studio' in window.title:
            return True
        
        return False
```

---

**📚 相关文档：**
- [架构设计](architecture.md) - 系统整体设计
- [API参考](api-reference.md) - 详细API文档  
- [性能分析](performance.md) - 性能特征分析
- [开发环境](../contributor/development-setup.md) - 开发环境配置