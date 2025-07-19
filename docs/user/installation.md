# 📦 安装指南

本指南将帮助您在Windows系统上安装和配置Win-Manager。

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 10 或更高版本
- **Python**: 3.8.1 或更高版本
- **权限**: 管理员权限（推荐，用于窗口操作）
- **内存**: 至少 100MB 可用内存

### 推荐配置
- **操作系统**: Windows 11
- **Python**: 3.11 或更高版本
- **内存**: 512MB 可用内存

## 🛠️ 安装方法

### 方法1：使用 uv (推荐)

[uv](https://github.com/astral-sh/uv) 是现代的Python包管理器，安装速度更快：

```bash
# 1. 安装 uv (如果还没有)
pip install uv

# 2. 克隆项目
git clone https://github.com/shidu18710/win-manager.git
cd win-manager

# 3. 同步依赖
uv sync
```

### 方法2：使用传统 pip

```bash
# 1. 克隆项目
git clone https://github.com/shidu18710/win-manager.git
cd win-manager

# 2. 创建虚拟环境 (推荐)
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 方法3：开发模式安装

如果您想要修改代码或贡献到项目：

```bash
# 克隆并安装为可编辑模式
git clone https://github.com/shidu18710/win-manager.git
cd win-manager
pip install -e .
```

## ⚙️ 验证安装

### 检查命令行工具

```bash
# 检查CLI是否正常工作
win-manager --help

# 测试基本功能
win-manager ls
```

### 检查Python模块

```python
# 测试Python接口
from win_manager.core.window_manager import WindowManager

manager = WindowManager()
windows = manager.get_manageable_windows()
print(f"找到 {len(windows)} 个可管理的窗口")
```

## 🔧 配置设置

### 配置文件位置

Win-Manager的配置文件会自动创建在：
```
~/.win-manager/config.json
```

### 基本配置

首次运行时，会自动创建默认配置。您可以通过以下命令查看配置：

```bash
# 查看当前配置
win-manager config show

# 修改默认布局
win-manager config set window_management.default_layout grid
```

### 热键配置

如果您想使用全局热键，需要确保：
1. 程序有足够的权限
2. 热键组合没有被其他程序占用

```bash
# 查看热键配置
win-manager hotkey list

# 添加自定义热键
win-manager hotkey add "ctrl+alt+g" "layout apply grid"
```

## 🚀 快速测试

完成安装后，试试这些命令：

```bash
# 1. 查看帮助
win-manager --help

# 2. 列出所有窗口
win-manager ls

# 3. 应用网格布局
win-manager grid

# 4. 撤销布局
win-manager undo
```

## ❗ 常见问题

### 问题1：权限错误
**症状**: 运行时提示权限不足
**解决方案**: 
```bash
# 以管理员身份运行命令提示符，然后执行命令
```

### 问题2：找不到模块
**症状**: `ModuleNotFoundError`
**解决方案**:
```bash
# 确保在正确的虚拟环境中
# 重新安装依赖
pip install -r requirements.txt
```

### 问题3：热键不工作
**症状**: 设置的热键无响应
**解决方案**:
1. 检查热键是否被其他程序占用
2. 确保程序有足够权限
3. 重启热键服务：
```bash
win-manager hotkey stop
win-manager hotkey start
```

### 问题4：窗口操作失败
**症状**: 无法移动或调整窗口
**解决方案**:
1. 检查目标窗口是否可调整大小
2. 确保程序有管理员权限
3. 检查是否有安全软件阻止操作

## 📚 下一步

安装完成后，建议您：

1. 📖 阅读 [快速开始指南](quickstart.md)
2. 📚 查看 [用户手册](user-guide.md) 了解完整功能
3. 💻 浏览 [CLI参考](cli-reference.md) 学习所有命令

## 🆘 获取帮助

如果遇到问题：

1. 🔍 查看 [故障排除指南](troubleshooting.md)
2. 📋 在 [GitHub Issues](https://github.com/shidu18710/win-manager/issues) 报告问题
3. 📖 阅读 [开发者文档](../developer/architecture.md) 了解技术细节

---

**恭喜！您已成功安装 Win-Manager！** 🎉