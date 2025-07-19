# 📐 布局系统设计

Win-Manager 的布局系统采用策略模式设计，提供灵活、可扩展的窗口排列算法。本文档深入探讨布局系统的设计原理、算法实现和扩展方法。

## 🎯 设计目标

### 核心目标
1. **算法可插拔** - 支持动态添加新的布局算法
2. **参数可配置** - 每种布局支持丰富的自定义参数
3. **性能优化** - 高效的位置计算，支持大量窗口
4. **智能适应** - 根据屏幕尺寸和窗口数量智能调整

### 设计原则
- **单一职责** - 每个布局类只负责一种排列逻辑
- **开放封闭** - 对扩展开放，对修改封闭
- **策略模式** - 运行时可切换不同的布局算法

## 🏗️ 架构设计

### 核心组件关系

```
LayoutEngine (策略管理器)
    ├── LayoutManager (抽象策略)
    │   ├── GridLayout (网格布局)
    │   ├── CascadeLayout (瀑布布局)
    │   ├── StackLayout (堆叠布局)
    │   └── CustomLayout (自定义布局)
    └── ScreenManager (屏幕信息管理)
```

### 类图设计

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

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
    
    def get_layout_info(self) -> Dict[str, any]:
        """获取布局信息"""
        return {
            "name": self.__class__.__name__,
            "description": self.__doc__ or "No description available"
        }
```

## 📊 内置布局算法

### 1. GridLayout - 网格布局

#### 算法原理
网格布局将窗口均匀分布在一个矩形网格中，自动计算最优的行列数。

#### 核心算法
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
        columns = self._calculate_optimal_columns(window_count, screen_rect)
        rows = (window_count + columns - 1) // columns
        
        # 可用空间计算
        available_width, available_height = self._calculate_available_space(
            screen_rect, columns, rows
        )
        
        # 窗口尺寸计算
        window_width = max(200, available_width // columns)
        window_height = max(150, available_height // rows)
        
        # 位置分配
        for i, window in enumerate(windows):
            row, col = divmod(i, columns)
            x, y = self._calculate_window_position(
                screen_rect, row, col, window_width, window_height
            )
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions
    
    def _calculate_optimal_columns(
        self, 
        window_count: int, 
        screen_rect: Tuple[int, int, int, int]
    ) -> int:
        """计算最优列数"""
        if self.columns is not None:
            return self.columns
        
        # 基于屏幕宽高比的智能计算
        screen_width = screen_rect[2] - screen_rect[0]
        screen_height = screen_rect[3] - screen_rect[1]
        aspect_ratio = screen_width / screen_height
        
        # 黄金比例优化
        optimal_columns = max(1, int(math.sqrt(window_count * aspect_ratio)))
        
        # 考虑最小窗口大小限制
        max_columns_by_width = screen_width // (200 + self.padding)
        
        return min(optimal_columns, max_columns_by_width, window_count)
    
    def _calculate_available_space(
        self, 
        screen_rect: Tuple[int, int, int, int], 
        columns: int, 
        rows: int
    ) -> Tuple[int, int]:
        """计算可用空间"""
        screen_width = screen_rect[2] - screen_rect[0]
        screen_height = screen_rect[3] - screen_rect[1]
        
        available_width = screen_width - (self.padding * (columns + 1))
        available_height = screen_height - (self.padding * (rows + 1))
        
        return available_width, available_height
    
    def _calculate_window_position(
        self, 
        screen_rect: Tuple[int, int, int, int],
        row: int, 
        col: int, 
        window_width: int, 
        window_height: int
    ) -> Tuple[int, int]:
        """计算单个窗口位置"""
        x = screen_rect[0] + self.padding + col * (window_width + self.padding)
        y = screen_rect[1] + self.padding + row * (window_height + self.padding)
        return x, y
```

#### 特性和参数
- **自适应列数**: 根据屏幕比例和窗口数量自动计算
- **最小尺寸保证**: 确保窗口不会过小
- **边距控制**: 可配置窗口间距
- **固定列数**: 支持手动指定列数

### 2. CascadeLayout - 瀑布布局

#### 算法原理
瀑布布局以阶梯状方式排列窗口，便于快速切换和查看多个窗口。

#### 核心算法
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
        
        # 标准窗口大小 (屏幕的70%)
        window_width = int((screen_right - screen_left) * 0.7)
        window_height = int((screen_bottom - screen_top) * 0.7)
        
        # 计算最大偏移循环数
        max_cascade_count = self._calculate_max_cascade_count(
            screen_rect, window_width, window_height
        )
        
        for i, window in enumerate(windows):
            # 循环偏移防止超出屏幕
            cascade_index = i % max_cascade_count
            
            x = screen_left + (cascade_index * self.offset_x)
            y = screen_top + (cascade_index * self.offset_y)
            
            positions[window.hwnd] = (x, y, window_width, window_height)
        
        return positions
    
    def _calculate_max_cascade_count(
        self, 
        screen_rect: Tuple[int, int, int, int],
        window_width: int, 
        window_height: int
    ) -> int:
        """计算最大层叠数量"""
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        max_offset_x = (screen_right - screen_left - window_width) // self.offset_x
        max_offset_y = (screen_bottom - screen_top - window_height) // self.offset_y
        
        return max(1, min(max_offset_x, max_offset_y))
```

#### 特性和参数
- **循环重叠**: 避免窗口超出屏幕边界
- **可配置偏移**: 自定义X和Y方向的偏移量
- **固定尺寸**: 所有窗口使用统一的大小比例

### 3. StackLayout - 堆叠布局

#### 算法原理
堆叠布局将所有窗口放置在同一位置，适用于临时整理或专注模式。

#### 核心算法
```python
class StackLayout(LayoutManager):
    """堆叠布局 - 重叠展示算法"""
    
    def __init__(
        self, 
        stack_position: str = "center",
        window_width: Optional[Dict] = None,
        window_height: Optional[Dict] = None
    ):
        self.stack_position = stack_position  # "center", "left", "right"
        self.window_width = window_width
        self.window_height = window_height
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        
        if not windows:
            return positions
        
        # 计算窗口尺寸
        window_width, window_height = self._calculate_window_size(screen_rect)
        
        # 计算堆叠位置
        stack_x, stack_y = self._calculate_stack_position(
            screen_rect, window_width, window_height
        )
        
        # 所有窗口使用相同位置
        for window in windows:
            positions[window.hwnd] = (stack_x, stack_y, window_width, window_height)
        
        return positions
    
    def _calculate_window_size(
        self, 
        screen_rect: Tuple[int, int, int, int]
    ) -> Tuple[int, int]:
        """计算窗口尺寸"""
        screen_width = screen_rect[2] - screen_rect[0]
        screen_height = screen_rect[3] - screen_rect[1]
        
        # 宽度计算
        if self.window_width:
            if self.window_width['type'] == 'percentage':
                width = int(screen_width * self.window_width['value'] / 100)
            else:  # pixels
                width = self.window_width['value']
        else:
            width = int(screen_width * 0.8)  # 默认80%
        
        # 高度计算
        if self.window_height:
            if self.window_height['type'] == 'percentage':
                height = int(screen_height * self.window_height['value'] / 100)
            else:  # pixels
                height = self.window_height['value']
        else:
            height = int(screen_height * 0.8)  # 默认80%
        
        return width, height
    
    def _calculate_stack_position(
        self, 
        screen_rect: Tuple[int, int, int, int],
        window_width: int, 
        window_height: int
    ) -> Tuple[int, int]:
        """计算堆叠位置"""
        screen_left, screen_top, screen_right, screen_bottom = screen_rect
        
        position_strategies = {
            "center": lambda: (
                screen_left + (screen_right - screen_left - window_width) // 2,
                screen_top + (screen_bottom - screen_top - window_height) // 2
            ),
            "left": lambda: (screen_left + 50, screen_top + 50),
            "right": lambda: (screen_right - window_width - 50, screen_top + 50),
            "top": lambda: (
                screen_left + (screen_right - screen_left - window_width) // 2,
                screen_top + 50
            ),
            "bottom": lambda: (
                screen_left + (screen_right - screen_left - window_width) // 2,
                screen_bottom - window_height - 50
            )
        }
        
        strategy = position_strategies.get(self.stack_position, position_strategies["center"])
        return strategy()
```

## 🔧 扩展新布局

### 创建自定义布局

#### 1. 圆形布局示例
```python
import math

class CircularLayout(LayoutManager):
    """圆形布局 - 窗口围绕中心点排列"""
    
    def __init__(self, radius: int = 300, window_size: Tuple[int, int] = (400, 300)):
        self.radius = radius
        self.window_width, self.window_height = window_size
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        window_count = len(windows)
        
        if window_count == 0:
            return positions
        
        # 计算屏幕中心点
        center_x = (screen_rect[0] + screen_rect[2]) // 2
        center_y = (screen_rect[1] + screen_rect[3]) // 2
        
        # 计算角度步长
        angle_step = 2 * math.pi / window_count
        
        for i, window in enumerate(windows):
            # 计算极坐标
            angle = i * angle_step
            
            # 转换为笛卡尔坐标
            x = center_x + int(self.radius * math.cos(angle)) - self.window_width // 2
            y = center_y + int(self.radius * math.sin(angle)) - self.window_height // 2
            
            # 确保窗口在屏幕内
            x = max(screen_rect[0], min(x, screen_rect[2] - self.window_width))
            y = max(screen_rect[1], min(y, screen_rect[3] - self.window_height))
            
            positions[window.hwnd] = (x, y, self.window_width, self.window_height)
        
        return positions
```

#### 2. 螺旋布局示例
```python
class SpiralLayout(LayoutManager):
    """螺旋布局 - 窗口沿螺旋线排列"""
    
    def __init__(self, spiral_step: int = 30, turns: float = 2.0):
        self.spiral_step = spiral_step
        self.turns = turns
    
    def calculate_positions(
        self, 
        windows: List[WindowInfo], 
        screen_rect: Tuple[int, int, int, int]
    ) -> Dict[int, Tuple[int, int, int, int]]:
        positions = {}
        window_count = len(windows)
        
        if window_count == 0:
            return positions
        
        center_x = (screen_rect[0] + screen_rect[2]) // 2
        center_y = (screen_rect[1] + screen_rect[3]) // 2
        
        max_radius = min(
            (screen_rect[2] - screen_rect[0]) // 2,
            (screen_rect[3] - screen_rect[1]) // 2
        ) - 200
        
        for i, window in enumerate(windows):
            # 螺旋参数
            t = (i / window_count) * self.turns * 2 * math.pi
            radius = (i / window_count) * max_radius
            
            # 螺旋坐标
            x = center_x + int(radius * math.cos(t))
            y = center_y + int(radius * math.sin(t))
            
            positions[window.hwnd] = (x, y, 400, 300)
        
        return positions
```

### 注册自定义布局

```python
# 在LayoutEngine中注册新布局
def register_custom_layouts(layout_engine: LayoutEngine):
    """注册所有自定义布局"""
    
    # 注册圆形布局
    layout_engine.add_custom_layout("circular", CircularLayout())
    
    # 注册螺旋布局
    layout_engine.add_custom_layout("spiral", SpiralLayout())
    
    # 注册带参数的布局
    layout_engine.add_custom_layout(
        "large_circular", 
        CircularLayout(radius=400, window_size=(500, 400))
    )

# 使用自定义布局
manager = WindowManager()
layout_engine = manager.layout_engine

# 注册自定义布局
register_custom_layouts(layout_engine)

# 应用自定义布局
manager.organize_windows("circular")
manager.organize_windows("spiral")
```

## 📊 布局算法性能分析

### 时间复杂度分析

| 布局类型 | 时间复杂度 | 空间复杂度 | 适用窗口数 |
|---------|-----------|-----------|----------|
| Grid | O(n) | O(n) | 1-100+ |
| Cascade | O(n) | O(n) | 1-50 |
| Stack | O(n) | O(n) | 1-∞ |
| Circular | O(n) | O(n) | 1-20 |
| Spiral | O(n) | O(n) | 1-30 |

### 性能基准测试

```python
import time
from typing import List

class LayoutPerformanceTester:
    """布局性能测试器"""
    
    def __init__(self, layout_engine: LayoutEngine):
        self.layout_engine = layout_engine
    
    def benchmark_layout(
        self, 
        layout_name: str, 
        window_counts: List[int], 
        iterations: int = 10
    ) -> Dict[int, float]:
        """测试特定布局的性能"""
        results = {}
        
        for count in window_counts:
            # 生成测试窗口
            test_windows = self._generate_test_windows(count)
            
            # 多次测试取平均值
            total_time = 0
            for _ in range(iterations):
                start_time = time.perf_counter()
                
                self.layout_engine.apply_layout(layout_name, test_windows)
                
                end_time = time.perf_counter()
                total_time += (end_time - start_time)
            
            average_time = total_time / iterations
            results[count] = average_time
        
        return results
    
    def _generate_test_windows(self, count: int) -> List[WindowInfo]:
        """生成测试用窗口"""
        windows = []
        for i in range(count):
            window = WindowInfo(
                hwnd=i,
                title=f"Test Window {i}",
                process_name="test.exe",
                pid=1000 + i,
                rect=(0, 0, 800, 600),
                is_visible=True,
                is_resizable=True
            )
            windows.append(window)
        return windows

# 性能测试示例
def run_performance_tests():
    layout_engine = LayoutEngine()
    tester = LayoutPerformanceTester(layout_engine)
    
    # 测试不同窗口数量
    window_counts = [1, 5, 10, 25, 50, 100]
    layouts = ["grid", "cascade", "stack"]
    
    for layout in layouts:
        print(f"\n=== {layout.upper()} 布局性能测试 ===")
        results = tester.benchmark_layout(layout, window_counts)
        
        for count, time_taken in results.items():
            print(f"{count:3d} 窗口: {time_taken*1000:.2f}ms")
```

## 🎯 布局选择策略

### 智能布局推荐

```python
class LayoutRecommendationEngine:
    """布局推荐引擎"""
    
    def __init__(self):
        self.recommendation_rules = {
            1: "stack",              # 单窗口
            (2, 4): "grid",          # 2-4个窗口用网格
            (5, 10): "cascade",      # 5-10个窗口用瀑布
            (11, float('inf')): "grid"  # 更多窗口用网格
        }
    
    def recommend_layout(
        self, 
        window_count: int, 
        screen_aspect_ratio: float,
        user_preference: Optional[str] = None
    ) -> str:
        """推荐最适合的布局"""
        
        # 用户偏好优先
        if user_preference:
            return user_preference
        
        # 基于窗口数量的基础推荐
        base_recommendation = self._get_base_recommendation(window_count)
        
        # 基于屏幕比例的调整
        if screen_aspect_ratio > 2.0:  # 超宽屏
            if base_recommendation == "cascade":
                return "grid"  # 超宽屏更适合网格
        
        return base_recommendation
    
    def _get_base_recommendation(self, window_count: int) -> str:
        """基于窗口数量获取基础推荐"""
        for count_range, layout in self.recommendation_rules.items():
            if isinstance(count_range, tuple):
                min_count, max_count = count_range
                if min_count <= window_count <= max_count:
                    return layout
            elif window_count == count_range:
                return layout
        
        return "grid"  # 默认推荐
```

## 🔧 配置驱动的布局系统

### 布局配置文件

```yaml
# layout_config.yaml
layouts:
  grid:
    default_columns: 3
    default_padding: 10
    min_window_size: [200, 150]
    adaptive_columns: true
    
  cascade:
    offset_x: 30
    offset_y: 30
    window_size_ratio: 0.7
    max_cascade_count: 10
    
  stack:
    default_position: "center"
    default_size_ratio: 0.8
    available_positions: ["center", "left", "right", "top", "bottom"]
    
  custom_layouts:
    circular:
      radius: 300
      window_size: [400, 300]
      enabled: true
      
    spiral:
      spiral_step: 30
      turns: 2.0
      enabled: false
```

### 配置驱动的布局工厂

```python
class ConfigurableLayoutFactory:
    """可配置的布局工厂"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def create_layout(self, layout_name: str, **overrides) -> LayoutManager:
        """根据配置创建布局实例"""
        layout_config = self.config.get("layouts", {}).get(layout_name, {})
        
        # 合并配置和覆盖参数
        final_config = {**layout_config, **overrides}
        
        layout_creators = {
            "grid": lambda cfg: GridLayout(
                columns=cfg.get("columns"),
                padding=cfg.get("padding", 10)
            ),
            "cascade": lambda cfg: CascadeLayout(
                offset_x=cfg.get("offset_x", 30),
                offset_y=cfg.get("offset_y", 30)
            ),
            "stack": lambda cfg: StackLayout(
                stack_position=cfg.get("position", "center"),
                window_width=cfg.get("window_width"),
                window_height=cfg.get("window_height")
            )
        }
        
        creator = layout_creators.get(layout_name)
        if creator:
            return creator(final_config)
        else:
            raise ValueError(f"Unknown layout: {layout_name}")
```

## 📈 布局系统监控

### 布局使用统计

```python
class LayoutUsageTracker:
    """布局使用统计跟踪"""
    
    def __init__(self):
        self.usage_stats = {}
        self.performance_stats = {}
    
    def track_layout_usage(
        self, 
        layout_name: str, 
        window_count: int, 
        execution_time: float,
        success: bool
    ):
        """记录布局使用情况"""
        if layout_name not in self.usage_stats:
            self.usage_stats[layout_name] = {
                "total_uses": 0,
                "success_count": 0,
                "window_counts": [],
                "execution_times": []
            }
        
        stats = self.usage_stats[layout_name]
        stats["total_uses"] += 1
        if success:
            stats["success_count"] += 1
        stats["window_counts"].append(window_count)
        stats["execution_times"].append(execution_time)
    
    def get_most_used_layout(self) -> str:
        """获取最常用的布局"""
        if not self.usage_stats:
            return "grid"
        
        return max(self.usage_stats.keys(), 
                  key=lambda x: self.usage_stats[x]["total_uses"])
    
    def get_layout_report(self) -> dict:
        """生成布局使用报告"""
        report = {}
        
        for layout_name, stats in self.usage_stats.items():
            avg_windows = sum(stats["window_counts"]) / len(stats["window_counts"])
            avg_time = sum(stats["execution_times"]) / len(stats["execution_times"])
            success_rate = stats["success_count"] / stats["total_uses"]
            
            report[layout_name] = {
                "usage_count": stats["total_uses"],
                "success_rate": success_rate,
                "avg_window_count": avg_windows,
                "avg_execution_time": avg_time
            }
        
        return report
```

---

**📚 相关文档：**
- [架构设计](architecture.md) - 系统整体架构
- [核心模块](core-modules.md) - 核心组件详解
- [API参考](api-reference.md) - 完整API文档
- [性能分析](performance.md) - 性能优化策略