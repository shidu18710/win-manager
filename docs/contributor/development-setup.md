# 🔧 开发环境配置

本指南将帮助您设置 Win-Manager 的完整开发环境，包括依赖安装、代码质量工具配置和测试环境准备。

## 📋 系统要求

### 开发环境要求
- **操作系统**: Windows 10/11 (必需，因为项目使用Windows API)
- **Python**: 3.8.1+ (推荐 3.11+)
- **Git**: 2.30+
- **编辑器**: VS Code / PyCharm / 您喜欢的编辑器

### 推荐工具
- **uv**: 现代Python包管理器 (推荐)
- **Windows Terminal**: 更好的终端体验
- **Git Bash**: Unix风格的Git工具

## 🚀 快速开始

### 1. 克隆项目
```bash
# 克隆仓库
git clone https://github.com/shidu18710/win-manager.git
cd win-manager

# 查看项目结构
tree /f
```

### 2. 环境设置

#### 选项A: 使用 uv (推荐)
```bash
# 安装 uv
pip install uv

# 同步项目依赖
uv sync

# 激活虚拟环境
# Windows Command Prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Git Bash
source .venv/Scripts/activate
```

#### 选项B: 使用传统 pip
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows Command Prompt
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# Git Bash
source venv/Scripts/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. 验证安装
```bash
# 检查核心功能
python -c "from win_manager.core.window_manager import WindowManager; print('✓ 核心模块加载成功')"

# 检查CLI工具
win-manager --help

# 运行简单测试
python -c "
from win_manager.core.window_manager import WindowManager
manager = WindowManager()
windows = manager.get_manageable_windows()
print(f'✓ 检测到 {len(windows)} 个可管理窗口')
"
```

## 🛠️ 开发工具配置

### 代码格式化 - Black
```bash
# 安装
pip install black

# 格式化代码
black src/ tests/

# 检查格式
black --check src/ tests/

# 配置文件: pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # 排除目录
  \.git
  | \.venv
  | build
  | dist
)/
'''
```

### 代码检查 - Flake8
```bash
# 安装
pip install flake8

# 检查代码
flake8 src/ tests/

# 配置文件: .flake8
[flake8]
max-line-length = 88
exclude = .git,__pycache__,build,dist,.venv
ignore = E203,W503
per-file-ignores = __init__.py:F401
```

### 类型检查 - MyPy
```bash
# 安装
pip install mypy

# 类型检查
mypy src/

# 配置文件: mypy.ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

### 测试框架 - Pytest
```bash
# 安装
pip install pytest pytest-cov pytest-mock

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_window_manager.py

# 生成覆盖率报告
pytest --cov=src/win_manager --cov-report=html

# 配置文件: pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

## 📁 项目结构

```
win-manager/
├── src/                          # 源代码
│   └── win_manager/
│       ├── core/                 # 核心模块
│       ├── cli/                  # CLI实现
│       ├── utils/                # 工具模块
│       └── main.py               # 简单CLI入口
├── tests/                        # 测试代码
│   ├── test_*.py                # 单元测试
│   └── integration/             # 集成测试
├── docs/                        # 文档
│   ├── user/                    # 用户文档
│   ├── developer/               # 开发者文档
│   └── contributor/             # 贡献者文档
├── scripts/                     # 构建脚本
├── requirements.txt             # 运行时依赖
├── requirements-dev.txt         # 开发依赖
├── pyproject.toml              # 项目配置
├── .gitignore                  # Git忽略文件
└── README.md                   # 项目说明
```

## 🧪 测试环境

### 运行测试
```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/ -m "not integration"

# 运行集成测试
pytest tests/ -m integration

# 运行性能测试
pytest tests/test_performance.py -v -s

# 生成HTML覆盖率报告
pytest --cov=src/win_manager --cov-report=html
# 查看报告: htmlcov/index.html
```

### 测试数据准备
```bash
# 创建测试用的模拟窗口
python scripts/create_test_windows.py

# 清理测试数据
python scripts/cleanup_test_data.py
```

### 调试测试
```bash
# 使用PDB调试
pytest --pdb tests/test_window_manager.py::test_specific_function

# 只运行失败的测试
pytest --lf

# 停在第一个失败
pytest -x
```

## 🔧 IDE配置

### VS Code配置
创建 `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    },
    "editor.rulers": [88],
    "editor.formatOnSave": true
}
```

创建 `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Win-Manager CLI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/win_manager/cli/main.py",
            "args": ["--help"],
            "console": "integratedTerminal"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/"],
            "console": "integratedTerminal"
        }
    ]
}
```

### PyCharm配置
1. 打开项目设置 (Ctrl+Alt+S)
2. 配置Python解释器: `.venv/Scripts/python.exe`
3. 设置代码风格:
   - Editor → Code Style → Python → Black compatible
4. 配置测试运行器:
   - Tools → Python Integrated Tools → Testing → pytest

## 🔍 开发工作流

### 1. 功能开发流程
```bash
# 1. 创建功能分支
git checkout -b feature/new-layout-algorithm

# 2. 开发代码
# ... 编写代码 ...

# 3. 运行代码质量检查
black src/ tests/
flake8 src/ tests/
mypy src/

# 4. 运行测试
pytest

# 5. 提交代码
git add .
git commit -m "feat: add new layout algorithm"

# 6. 推送分支
git push origin feature/new-layout-algorithm
```

### 2. 调试技巧
```python
# 使用日志调试
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug information")

# 使用断点调试
import pdb; pdb.set_trace()

# 性能分析
import cProfile
cProfile.run('your_function()')
```

### 3. 常用开发命令
```bash
# 代码质量一键检查
python scripts/quality_check.py

# 运行完整测试套件
python scripts/run_all_tests.py

# 生成文档
python scripts/generate_docs.py

# 构建分发包
python scripts/build_package.py
```

## 📊 开发工具脚本

### quality_check.py
```python
#!/usr/bin/env python3
"""代码质量检查脚本"""

import subprocess
import sys

def run_command(cmd, description):
    """运行命令并检查结果"""
    print(f"\n{'='*50}")
    print(f"运行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*50}")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """主函数"""
    checks = [
        ("black --check src/ tests/", "代码格式检查"),
        ("flake8 src/ tests/", "代码风格检查"),
        ("mypy src/", "类型检查"),
        ("pytest --tb=short", "单元测试"),
    ]
    
    all_passed = True
    
    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✅ 所有检查通过!")
        sys.exit(0)
    else:
        print("❌ 部分检查失败，请修复后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🐛 故障排除

### 常见问题

#### 1. 导入错误
```bash
# 问题: ModuleNotFoundError
# 解决: 确保PYTHONPATH包含src目录
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# 或者使用可编辑安装
pip install -e .
```

#### 2. 权限问题
```bash
# 问题: 窗口操作失败
# 解决: 以管理员身份运行
# 右键点击终端 → "以管理员身份运行"
```

#### 3. 依赖冲突
```bash
# 问题: 包版本冲突
# 解决: 重建虚拟环境
rm -rf .venv
uv sync
```

#### 4. 测试失败
```bash
# 问题: 测试环境问题
# 解决: 确保有足够的测试窗口
python scripts/create_test_windows.py
```

### 调试技巧

#### 1. 详细日志
```python
# 在代码中添加详细日志
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### 2. 分步调试
```python
# 分步调试复杂操作
def debug_window_operation():
    manager = WindowManager()
    
    print("1. 获取窗口列表...")
    windows = manager.get_manageable_windows()
    print(f"   找到 {len(windows)} 个窗口")
    
    print("2. 计算布局...")
    positions = manager.layout_engine.apply_layout("grid", windows)
    print(f"   计算了 {len(positions)} 个位置")
    
    print("3. 应用布局...")
    # ... 继续调试
```

## 🎯 开发最佳实践

### 1. 代码风格
- 遵循PEP 8标准
- 使用类型提示
- 编写清晰的文档字符串
- 保持函数简单，单一职责

### 2. 测试实践
- 编写测试驱动开发(TDD)
- 保持高测试覆盖率(>80%)
- 编写有意义的测试用例
- 模拟外部依赖

### 3. 性能考虑
- 避免不必要的API调用
- 使用批量操作
- 实现合理的缓存策略
- 监控内存使用

### 4. 安全实践
- 验证所有输入
- 处理权限问题
- 不在代码中硬编码敏感信息
- 遵循最小权限原则

---

**📚 相关文档：**
- [代码规范](coding-standards.md) - 详细的编码标准
- [测试指南](testing-guide.md) - 测试编写指南
- [构建发布](build-release.md) - 构建和发布流程
- [架构设计](../developer/architecture.md) - 系统架构文档