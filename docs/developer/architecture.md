# 🏗️ 系统架构

Win-Manager 的架构设计遵循清晰的层次结构和现代软件工程原则，确保代码的可维护性、可扩展性和高性能。

## 📐 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                            │
├─────────────────────┬───────────────────────────────────────┤
│   简单CLI (main.py)  │     完整CLI (cli/main.py)           │
│   基于 argparse     │     基于 Click 框架                  │
└─────────────────────┴───────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      门面模式 - 核心协调层                    │
├─────────────────────────────────────────────────────────────┤
│              WindowManager (主要门面)                       │
│         统一协调所有子系统的交互                             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        核心业务层                            │
├───────────────┬─────────────────┬─────────────────────────────┤
│ WindowDetector│  LayoutEngine   │    WindowController        │
│ 窗口发现和枚举 │  布局算法策略    │    窗口控制和操作           │
└───────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                       支持服务层                             │
├──────────────┬──────────────────┬───────────────────────────┤
│ ConfigManager│   HotkeyManager  │    ExceptionHandler       │
│ 配置管理     │   全局热键管理    │    异常处理和日志          │
└──────────────┴──────────────────┴───────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                        平台抽象层                            │
├─────────────────────────────────────────────────────────────┤
│         Windows API 集成 (pywin32, pyautogui)              │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 设计原则

### 1. 单一职责原则 (SRP)
每个组件都有明确的单一职责：
- **WindowDetector**: 只负责窗口发现和信息提取
- **WindowController**: 只负责窗口位置和大小控制
- **LayoutEngine**: 只负责布局算法计算
- **ConfigManager**: 只负责配置管理

### 2. 开放封闭原则 (OCP)
系统对扩展开放，对修改封闭：
- 新布局类型通过扩展 `LayoutEngine` 添加
- 新的窗口过滤规则通过配置文件扩展
- 新的输出格式通过策略模式扩展

### 3. 依赖倒置原则 (DIP)
高层模块不依赖低层模块：
- `WindowManager` 依赖接口，而非具体实现
- 布局算法通过策略模式解耦
- 平台相关代码隔离在底层

## 🧱 核心组件详解

### WindowManager (门面模式)
```python
class WindowManager:
    """主要门面类，协调所有子系统"""
    
    def __init__(self):
        self.detector = WindowDetector()      # 窗口检测
        self.controller = WindowController()  # 窗口控制  
        self.layout_engine = LayoutEngine()   # 布局引擎
        self.config = ConfigManager()         # 配置管理
        self.state_manager = StateManager()   # 状态管理
```

**职责**:
- 统一对外接口
- 协调子系统交互
- 维护操作历史
- 处理业务流程

### WindowDetector (信息专家)
```python
class WindowDetector:
    """窗口发现和信息提取专家"""
    
    def get_manageable_windows(self) -> List[WindowInfo]:
        """获取所有可管理窗口"""
        
    def filter_windows(self, windows: List[WindowInfo]) -> List[WindowInfo]:
        """根据规则过滤窗口"""
```

**特性**:
- 高性能窗口枚举 (500+窗口 < 0.01s)
- 智能过滤系统窗口
- 支持进程名和标题过滤
- 窗口状态检测

### LayoutEngine (策略模式)
```python
class LayoutEngine:
    """布局算法策略管理器"""
    
    def __init__(self):
        self.strategies = {
            'grid': GridLayoutStrategy(),
            'cascade': CascadeLayoutStrategy(), 
            'stack': StackLayoutStrategy()
        }
    
    def calculate_layout(self, layout_type: str, windows: List[WindowInfo]) -> List[WindowRect]:
        """计算窗口布局"""
        return self.strategies[layout_type].calculate(windows)
```

**布局策略**:
- **GridLayoutStrategy**: 网格布局算法
- **CascadeLayoutStrategy**: 瀑布布局算法
- **StackLayoutStrategy**: 堆叠布局算法

### WindowController (控制器)
```python
class WindowController:
    """窗口操作控制器"""
    
    def move_window(self, handle: int, rect: WindowRect) -> bool:
        """移动窗口到指定位置"""
        
    def batch_move_windows(self, moves: List[Tuple[int, WindowRect]]) -> BatchResult:
        """批量移动窗口"""
```

**特性**:
- 原子性操作保证
- 批量操作优化
- 错误恢复机制
- 权限检查

## 🔧 关键设计模式

### 1. 门面模式 (Facade Pattern)
**应用**: `WindowManager` 作为系统的统一入口

**优势**:
- 简化复杂子系统的使用
- 减少客户端与子系统的耦合
- 提供清晰的API接口

### 2. 策略模式 (Strategy Pattern)
**应用**: 布局算法的实现

```python
# 策略接口
class LayoutStrategy:
    def calculate(self, windows: List[WindowInfo]) -> List[WindowRect]:
        pass

# 具体策略
class GridLayoutStrategy(LayoutStrategy):
    def calculate(self, windows: List[WindowInfo]) -> List[WindowRect]:
        # 网格布局算法实现
        pass
```

**优势**:
- 算法族可互换
- 易于扩展新布局
- 遵循开放封闭原则

### 3. 状态模式 (State Pattern)
**应用**: 窗口状态管理和撤销功能

```python
class WindowState:
    """窗口状态快照"""
    def __init__(self, window_id: int, rect: WindowRect, state: str):
        self.window_id = window_id
        self.rect = rect
        self.state = state

class StateManager:
    """状态管理器"""
    def save_state(self, windows: List[WindowInfo]) -> StateSnapshot:
        """保存当前状态"""
    
    def restore_state(self, snapshot: StateSnapshot) -> bool:
        """恢复到指定状态"""
```

### 4. 建造者模式 (Builder Pattern)
**应用**: 配置对象的构建

```python
class ConfigBuilder:
    """配置建造者"""
    def __init__(self):
        self.config = {}
    
    def with_window_filters(self, filters: List[str]) -> 'ConfigBuilder':
        self.config['filters'] = filters
        return self
    
    def with_layout_settings(self, settings: dict) -> 'ConfigBuilder':
        self.config['layout'] = settings
        return self
    
    def build(self) -> Config:
        return Config(self.config)
```

## 📊 数据流图

```
用户命令 → WindowManager → [并行处理]
                            ├─ WindowDetector.get_windows()
                            ├─ StateManager.save_current_state()
                            └─ ConfigManager.get_layout_config()
                                     ↓
LayoutEngine.calculate_layout() ← [数据汇总]
                                     ↓
WindowController.batch_move() ← [布局结果]
                                     ↓
结果反馈 ← StateManager.save_new_state()
```

## 🚀 性能优化策略

### 1. 批量操作优化
```python
# 避免逐个操作窗口
for window in windows:
    controller.move_window(window.handle, new_rect)  # ❌ 低效

# 使用批量操作
controller.batch_move_windows([(w.handle, rect) for w, rect in zip(windows, rects)])  # ✅ 高效
```

### 2. 异步处理
```python
import asyncio

class AsyncWindowController:
    async def move_window_async(self, handle: int, rect: WindowRect):
        """异步窗口移动"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._move_window_sync, handle, rect)
```

### 3. 缓存优化
```python
class WindowDetector:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 100  # ms
    
    @lru_cache(maxsize=128)
    def get_window_info(self, handle: int) -> WindowInfo:
        """缓存窗口信息"""
        pass
```

### 4. 内存管理
- 使用 `__slots__` 减少对象内存占用
- 及时释放窗口句柄引用
- 限制状态历史深度

## 🔒 安全设计

### 1. 权限检查
```python
def check_window_access(handle: int) -> bool:
    """检查是否有权限操作窗口"""
    try:
        # 尝试获取窗口信息
        win32gui.GetWindowText(handle)
        return True
    except win32gui.error:
        return False
```

### 2. 异常隔离
```python
@exception_handler
def move_window(self, handle: int, rect: WindowRect) -> bool:
    """带异常处理的窗口移动"""
    try:
        return self._move_window_impl(handle, rect)
    except WindowOperationError as e:
        self.logger.error(f"Failed to move window {handle}: {e}")
        return False
```

### 3. 输入验证
```python
def validate_window_rect(rect: WindowRect) -> bool:
    """验证窗口矩形参数"""
    return (rect.width > 0 and rect.height > 0 and 
            rect.x >= 0 and rect.y >= 0)
```

## 🧪 测试架构

### 测试分层
```
集成测试 (Integration Tests)
    ├─ 端到端窗口管理流程测试
    ├─ CLI命令集成测试
    └─ 配置集成测试

组件测试 (Component Tests)  
    ├─ WindowManager 组件测试
    ├─ LayoutEngine 策略测试
    └─ WindowController 控制测试

单元测试 (Unit Tests)
    ├─ 各个类的方法测试
    ├─ 工具函数测试
    └─ 边界条件测试

性能测试 (Performance Tests)
    ├─ 大量窗口处理测试
    ├─ 内存使用测试
    └─ 响应时间测试
```

### 测试覆盖率目标
- **单元测试**: > 90%
- **集成测试**: > 80%
- **关键路径**: 100%

## 📈 扩展点

### 1. 新布局类型
```python
class CustomLayoutStrategy(LayoutStrategy):
    """自定义布局策略"""
    def calculate(self, windows: List[WindowInfo]) -> List[WindowRect]:
        # 实现自定义布局算法
        pass

# 注册新策略
layout_engine.register_strategy('custom', CustomLayoutStrategy())
```

### 2. 新的窗口过滤器
```python
class ProcessFilterStrategy(FilterStrategy):
    """进程名过滤策略"""
    def should_include(self, window: WindowInfo) -> bool:
        return window.process_name in self.allowed_processes
```

### 3. 新的输出格式
```python
class XMLOutputFormatter(OutputFormatter):
    """XML格式输出"""
    def format(self, data: dict) -> str:
        return dict_to_xml(data)
```

## 🔄 部署架构

### 1. 独立可执行文件
```bash
# 使用 PyInstaller 打包
pyinstaller --onefile --windowed src/win_manager/cli/main.py
```

### 2. Python 包安装
```bash
# 开发模式安装
pip install -e .

# 正式安装
pip install win-manager
```

### 3. 系统服务模式
```python
# 作为 Windows 服务运行
class WinManagerService(win32serviceutil.ServiceFramework):
    def SvcRun(self):
        # 启动热键监听服务
        hotkey_manager.start()
```

---

**📚 相关文档：**
- [API参考](api-reference.md) - 详细的API文档
- [核心模块](core-modules.md) - 各模块详细说明
- [性能分析](performance.md) - 性能特征和优化
- [开发环境](../contributor/development-setup.md) - 开发环境配置