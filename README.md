# Win-Manager

> 🪟 智能的 Windows 窗口管理工具，让您的桌面井然有序

Win-Manager 是一个功能强大的 Windows 窗口管理工具，提供自动布局、智能识别和快捷操作，帮助您创建整洁高效的工作环境。

![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## ✨ 核心特性

- **🎯 智能窗口检测** - 自动识别和管理可调整窗口，过滤系统窗口
- **📐 多种布局模式** - 瀑布、网格、堆叠等布局，一键整理桌面
- **⚡ 双重界面** - 既有简单CLI也有功能完整的命令行工具
- **🔧 灵活配置** - 支持自定义配置、热键和窗口过滤规则
- **↩️ 撤销功能** - 一键恢复到布局前的窗口状态
- **🚀 高性能** - 500个窗口处理时间 < 0.01秒

## 🚀 快速开始

### 📋 5分钟上手
1. **安装软件** → 详见 [安装指南](docs/user/installation.md)
2. **快速试用** → 跟随 [快速开始教程](docs/user/quickstart.md)
3. **深入学习** → 查看 [用户指南](docs/user/user-guide.md)

### 💡 一键体验
```bash
# 快捷命令
win-manager grid      # 网格布局
win-manager cascade   # 瀑布布局  
win-manager stack     # 堆叠布局
win-manager undo      # 撤销布局
```

### 🔧 程序化接口
```python
from win_manager.core.window_manager import WindowManager

manager = WindowManager()
manager.organize_windows("grid")  # 应用网格布局
```

### 🗺️ 学习路径指南
根据您的角色选择合适的学习路径：

**👤 最终用户**
```
README → 安装指南 → 快速开始 → CLI参考 → 用户指南
```

**💻 开发者**  
```
README → 架构设计 → 核心模块 → API参考 → 性能分析
```

**🤝 贡献者**
```
README → 贡献指南 → 开发环境 → 代码规范 → 测试指南
```

> 📖 **完整文档导航**: [文档导航中心](docs/navigation.md)

## 📚 文档导航

### 👥 用户文档
- [📦 安装指南](docs/user/installation.md) - 详细的安装和配置步骤
- [⚡ 快速开始](docs/user/quickstart.md) - 5分钟上手教程
- [📖 用户手册](docs/user/user-guide.md) - 完整功能使用指南
- [💻 CLI参考](docs/user/cli-reference.md) - 命令行工具完整参考
- [🛠️ 故障排除](docs/user/troubleshooting.md) - 常见问题解决方案

### 🛠️ 开发者文档
- [🏗️ 架构设计](docs/developer/architecture.md) - 系统架构和设计模式
- [📋 API参考](docs/developer/api-reference.md) - 完整的API文档
- [🔧 核心模块](docs/developer/core-modules.md) - 核心组件详解
- [📐 布局系统](docs/developer/layout-system.md) - 布局引擎设计
- [⚙️ 配置系统](docs/developer/configuration.md) - 配置管理详解
- [⚡ 性能分析](docs/developer/performance.md) - 性能特征和优化

### 🤝 贡献者文档
- [🔧 开发环境](docs/contributor/development-setup.md) - 开发环境配置
- [📏 代码规范](docs/contributor/coding-standards.md) - 代码风格和规范
- [🧪 测试指南](docs/contributor/testing-guide.md) - 测试编写和运行
- [🚀 构建发布](docs/contributor/build-release.md) - 构建和发布流程

### 📚 参考资料
- [📋 更新日志](docs/reference/changelog.md) - 版本变更记录
- [📄 许可证](docs/reference/license.md) - 开源许可信息
- [🙏 致谢](docs/reference/acknowledgments.md) - 依赖和贡献者致谢

## 🎯 使用场景

| 场景 | 描述 | 推荐布局 |
|------|------|----------|
| 🖥️ **开发工作** | 多个IDE、终端、浏览器窗口 | Grid网格布局 |
| 📊 **办公应用** | 文档、表格、邮件并排查看 | Cascade瀑布布局 |
| 🎯 **专注模式** | 临时整理，保持桌面整洁 | Stack堆叠布局 |
| 🔄 **快速切换** | 在不同工作状态间切换 | 热键 + 撤销功能 |

## 📊 技术特性

- **🏗️ 架构**: 模块化设计，策略模式，门面模式
- **🧪 测试**: 88%覆盖率，202个测试，包含性能测试
- **⚡ 性能**: 500窗口<0.01s，内存占用~5MB/1000窗口
- **🔧 工具**: Black、Flake8、MyPy、Pytest

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](docs/contributor/development-setup.md) 了解如何参与项目开发。

## 📄 许可证

本项目采用 [Apache-2.0 许可证](LICENSE)。

---

**让您的 Windows 桌面更加整洁有序！** 🎉