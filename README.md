# Win-Manager 📱

一个功能强大的Windows窗口管理工具，可以帮助您轻松管理和组织桌面窗口。

## ✨ 主要功能

### 🪟 窗口管理
- **智能窗口检测**: 自动检测所有可管理的窗口
- **多种布局模式**: 瀑布、网格、堆叠等多种布局
- **窗口控制**: 移动、调整大小、最小化/最大化
- **智能过滤**: 自动过滤系统窗口和不适合的窗口

### ⚡ 布局系统
- **瀑布布局** (Cascade): 窗口层叠排列，便于快速切换
- **网格布局** (Grid): 窗口均匀分布，最大化屏幕利用率
- **堆叠布局** (Stack): 窗口重叠排列，节省空间

### 🔥 热键支持
- **全局热键**: 设置自定义热键快速管理窗口
- **后台运行**: 无需切换到应用即可使用
- **组合键支持**: 支持Ctrl+Alt+键等组合热键

### ⚙️ 配置管理
- **灵活配置**: 支持自定义配置所有功能
- **进程过滤**: 排除特定进程的窗口
- **配置导入导出**: 方便配置备份和共享

## 🚀 快速开始

### 1. 安装依赖
```bash
# 使用 uv 安装 (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 基本使用
```python
from win_manager.core.window_manager import WindowManager

# 创建窗口管理器
manager = WindowManager()

# 获取可管理的窗口
windows = manager.get_manageable_windows()
print(f"找到 {len(windows)} 个窗口")

# 应用网格布局
success = manager.organize_windows("grid")
if success:
    print("✅ 网格布局应用成功")

# 撤销布局
manager.undo_layout()
```

### 3. 运行演示
```bash
# 快速演示
python quick_demo.py

# 完整演示
python demo_usage.py
```

## 📖 详细功能说明

### 窗口布局类型

#### 1. 瀑布布局 (Cascade)
```python
manager.organize_windows("cascade")
```
- 窗口呈阶梯状排列
- 便于快速切换不同窗口
- 适合需要同时查看多个窗口的场景

#### 2. 网格布局 (Grid)
```python
manager.organize_windows("grid")
```
- 窗口均匀分布在屏幕上
- 最大化屏幕空间利用率
- 适合需要并排比较多个窗口的场景

#### 3. 堆叠布局 (Stack)
```python
manager.organize_windows("stack")
```
- 窗口重叠排列在中心位置
- 节省桌面空间
- 适合临时整理桌面的场景

### 热键设置

```python
from win_manager.utils.hotkey_manager import HotkeyManager

# 创建热键管理器
hotkey_manager = HotkeyManager()

# 注册热键
def apply_grid_layout():
    manager.organize_windows("grid")

hotkey_manager.register_hotkey("ctrl+alt+g", apply_grid_layout)

# 启动热键监听
hotkey_manager.start()
```

### 配置管理

```python
from win_manager.core.config_manager import ConfigManager

# 创建配置管理器
config = ConfigManager()

# 修改配置
config.set("window_management.default_layout", "grid")
config.set("filters.ignore_minimized", True)

# 添加排除进程
config.add_excluded_process("explorer.exe")

# 保存配置
config.save_config()
```

## 🎯 使用场景

### 1. 开发工作
- 同时打开多个IDE窗口
- 并排显示代码和文档
- 快速切换不同项目窗口

### 2. 办公应用
- 整理桌面上的办公软件窗口
- 并排比较多个文档
- 快速组织会议时的多个应用

### 3. 多任务处理
- 同时处理多个任务时的窗口管理
- 快速切换不同工作模式
- 保持桌面整洁有序

## 📊 性能特点

### 🚀 高性能
- **500个窗口处理时间**: < 0.01秒
- **内存占用**: 每1000个窗口仅需 ~5MB
- **布局计算**: 200个窗口 < 0.001秒

### 🔧 稳定性
- **测试覆盖率**: 88%
- **单元测试**: 202个测试全部通过
- **异常处理**: 完善的错误处理机制

## 🛠️ 开发和测试

### 运行测试
```bash
# 运行所有测试
uv run python -m pytest tests/ -v

# 运行特定测试
uv run python -m pytest tests/test_window_manager.py -v

# 运行性能测试
uv run python -m pytest tests/test_performance.py -v -s

# 生成覆盖率报告
uv run python -m pytest tests/ --cov=src/win_manager --cov-report=html
```

### 项目结构
```
win-manager/
├── src/win_manager/        # 源代码
│   ├── core/               # 核心模块
│   │   ├── window_manager.py
│   │   ├── window_detector.py
│   │   ├── window_controller.py
│   │   ├── layout_manager.py
│   │   └── config_manager.py
│   └── utils/              # 工具模块
│       ├── exception_handler.py
│       └── hotkey_manager.py
├── tests/                  # 测试文件
├── quick_demo.py          # 快速演示
├── demo_usage.py          # 完整演示
└── README.md              # 说明文档
```

## 🤝 贡献

欢迎贡献代码！请确保：
1. 所有测试通过
2. 代码符合项目风格
3. 添加必要的测试用例

## 📄 许可证

本项目采用 MIT 许可证。

## 🆘 常见问题

### Q: 为什么某些窗口不能被管理？
A: 系统会自动过滤以下类型的窗口：
- 系统窗口（如任务栏）
- 最小化的窗口
- 不可调整大小的窗口
- 过小的窗口（< 100px）

### Q: 热键不生效怎么办？
A: 请确保：
- 热键组合没有被其他软件占用
- 程序以管理员权限运行
- 热键格式正确（如：ctrl+alt+g）

### Q: 布局应用失败怎么办？
A: 可能的原因：
- 没有找到可管理的窗口
- 窗口被其他程序锁定
- 权限不足，建议以管理员身份运行

---

**Win-Manager** - 让您的Windows桌面更加整洁有序！ 🎉