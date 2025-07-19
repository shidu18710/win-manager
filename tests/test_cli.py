"""
CLI tests for Win-Manager
"""
import pytest
import click
from click.testing import CliRunner
import json
import yaml
import tempfile
import os

# 导入CLI模块
from win_manager.cli.main import cli


class TestCLIBasic:
    """基本CLI测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_help_command(self):
        """测试帮助命令"""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Win-Manager' in result.output
        assert 'Commands:' in result.output
    
    def test_version_and_status(self):
        """测试版本和状态"""
        result = self.runner.invoke(cli, ['tool', 'status'])
        assert result.exit_code == 0
        # 应该包含系统信息
        assert 'system' in result.output.lower()
    
    def test_json_output(self):
        """测试JSON输出格式"""
        result = self.runner.invoke(cli, ['--output', 'json', 'layout', 'list'])
        assert result.exit_code == 0
        
        # 验证JSON格式
        try:
            data = json.loads(result.output)
            assert isinstance(data, dict)
            assert 'success' in data
            assert 'data' in data
        except json.JSONDecodeError:
            pytest.fail("输出不是有效的JSON格式")
    
    def test_yaml_output(self):
        """测试YAML输出格式"""
        result = self.runner.invoke(cli, ['--output', 'yaml', 'layout', 'list'])
        assert result.exit_code == 0
        
        # 验证YAML格式
        try:
            data = yaml.safe_load(result.output)
            assert isinstance(data, dict)
            assert 'success' in data
            assert 'data' in data
        except yaml.YAMLError:
            pytest.fail("输出不是有效的YAML格式")
    
    def test_dry_run_mode(self):
        """测试模拟运行模式"""
        result = self.runner.invoke(cli, ['--dry-run', 'grid', '--columns', '3'])
        assert result.exit_code == 0
        assert 'dry_run' in result.output.lower()
    
    def test_verbose_mode(self):
        """测试详细模式"""
        result = self.runner.invoke(cli, ['--verbose', 'layout', 'list'])
        assert result.exit_code == 0
        # 详细模式应该包含更多信息
        assert len(result.output) > 0
    
    def test_quiet_mode(self):
        """测试静默模式"""
        result = self.runner.invoke(cli, ['--quiet', 'layout', 'list'])
        assert result.exit_code == 0
        # 静默模式下输出应该更少


class TestLayoutCommands:
    """布局命令测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_layout_list(self):
        """测试布局列表"""
        result = self.runner.invoke(cli, ['layout', 'list'])
        assert result.exit_code == 0
        assert 'cascade' in result.output.lower()
        assert 'grid' in result.output.lower()
        assert 'stack' in result.output.lower()
    
    def test_layout_apply_dry_run(self):
        """测试布局应用（模拟运行）"""
        result = self.runner.invoke(cli, ['--dry-run', 'layout', 'apply', 'grid'])
        assert result.exit_code == 0
        assert 'grid' in result.output.lower()
        assert 'dry_run' in result.output.lower()
    
    def test_layout_apply_with_options(self):
        """测试带选项的布局应用"""
        result = self.runner.invoke(cli, ['--dry-run', 'layout', 'apply', 'grid', 
                                         '--columns', '3', '--padding', '10'])
        assert result.exit_code == 0
        assert 'columns' in result.output.lower()
        assert 'padding' in result.output.lower()
    
    def test_layout_apply_with_filters(self):
        """测试带过滤器的布局应用"""
        result = self.runner.invoke(cli, ['--dry-run', 'layout', 'apply', 'cascade',
                                         '--target', 'chrome.exe', '--exclude', 'explorer.exe'])
        assert result.exit_code == 0
        assert 'target' in result.output.lower()
        assert 'exclude' in result.output.lower()
    
    def test_layout_undo(self):
        """测试撤销布局"""
        result = self.runner.invoke(cli, ['--dry-run', 'layout', 'undo'])
        assert result.exit_code == 0
        assert 'undo' in result.output.lower()
    
    def test_shortcut_commands(self):
        """测试快捷命令"""
        # 测试grid快捷命令
        result = self.runner.invoke(cli, ['--dry-run', 'grid', '--columns', '2'])
        assert result.exit_code == 0
        assert 'grid' in result.output.lower()
        
        # 测试cascade快捷命令
        result = self.runner.invoke(cli, ['--dry-run', 'cascade', '--offset-x', '30'])
        assert result.exit_code == 0
        assert 'cascade' in result.output.lower()
        
        # 测试stack快捷命令
        result = self.runner.invoke(cli, ['--dry-run', 'stack', '--stack-position', 'center'])
        assert result.exit_code == 0
        assert 'stack' in result.output.lower()
        
        # 测试undo快捷命令
        result = self.runner.invoke(cli, ['--dry-run', 'undo'])
        assert result.exit_code == 0
        assert 'undo' in result.output.lower()


class TestWindowCommands:
    """窗口命令测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_window_list(self):
        """测试窗口列表"""
        result = self.runner.invoke(cli, ['window', 'list'])
        assert result.exit_code == 0
        # 应该找到一些窗口
        assert 'window' in result.output.lower() or len(result.output) > 0
    
    def test_window_list_with_options(self):
        """测试带选项的窗口列表"""
        result = self.runner.invoke(cli, ['window', 'list', '--include-minimized', 
                                         '--sort-by', 'title'])
        assert result.exit_code == 0
    
    def test_window_operations_dry_run(self):
        """测试窗口操作（模拟运行）"""
        # 测试移动窗口
        result = self.runner.invoke(cli, ['--dry-run', 'window', 'move', 'test', 
                                         '--x', '100', '--y', '100'])
        assert result.exit_code == 0
        assert 'move' in result.output.lower()
        
        # 测试调整大小
        result = self.runner.invoke(cli, ['--dry-run', 'window', 'resize', 'test',
                                         '--width', '800', '--height', '600'])
        assert result.exit_code == 0
        assert 'resize' in result.output.lower()
    
    def test_ls_shortcut(self):
        """测试ls快捷命令"""
        result = self.runner.invoke(cli, ['ls'])
        assert result.exit_code == 0


class TestConfigCommands:
    """配置命令测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_config_show(self):
        """测试配置显示"""
        result = self.runner.invoke(cli, ['config', 'show'])
        assert result.exit_code == 0
        # 应该包含配置信息
        assert 'config' in result.output.lower()
    
    def test_config_set_get(self):
        """测试配置设置和获取"""
        # 设置配置
        result = self.runner.invoke(cli, ['--dry-run', 'config', 'set', 
                                         'test.key', 'test_value'])
        assert result.exit_code == 0
        
        # 获取配置
        result = self.runner.invoke(cli, ['config', 'get', 'test.key'])
        assert result.exit_code == 0
    
    def test_config_export_import(self):
        """测试配置导出和导入"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        try:
            # 导出配置
            result = self.runner.invoke(cli, ['--dry-run', 'config', 'export', temp_file])
            assert result.exit_code == 0
            
            # 导入配置
            result = self.runner.invoke(cli, ['--dry-run', 'config', 'import', temp_file])
            assert result.exit_code == 0
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestHotkeyCommands:
    """热键命令测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_hotkey_list(self):
        """测试热键列表"""
        result = self.runner.invoke(cli, ['hotkey', 'list'])
        assert result.exit_code == 0
        # 应该显示热键列表（可能为空）
        assert 'hotkey' in result.output.lower() or '0' in result.output
    
    def test_hotkey_add_remove(self):
        """测试热键添加和删除"""
        # 添加热键
        result = self.runner.invoke(cli, ['--dry-run', 'hotkey', 'add', 
                                         'ctrl+alt+t', 'layout apply grid'])
        assert result.exit_code == 0
        assert 'hotkey' in result.output.lower()
        
        # 删除热键
        result = self.runner.invoke(cli, ['--dry-run', 'hotkey', 'remove', 'ctrl+alt+t'])
        assert result.exit_code == 0
        assert 'remove' in result.output.lower()


class TestToolCommands:
    """工具命令测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_tool_status(self):
        """测试工具状态"""
        result = self.runner.invoke(cli, ['tool', 'status'])
        assert result.exit_code == 0
        assert 'system' in result.output.lower()
        assert 'win_manager' in result.output.lower()
    
    def test_tool_test(self):
        """测试工具测试"""
        result = self.runner.invoke(cli, ['tool', 'test', '--component', 'detector'])
        assert result.exit_code == 0
        assert 'test' in result.output.lower()
    
    def test_tool_benchmark(self):
        """测试工具基准测试"""
        result = self.runner.invoke(cli, ['tool', 'benchmark', '--windows', '10', 
                                         '--iterations', '2'])
        assert result.exit_code == 0
        assert 'benchmark' in result.output.lower()
    
    def test_tool_cleanup(self):
        """测试工具清理"""
        result = self.runner.invoke(cli, ['--dry-run', 'tool', 'cleanup'])
        assert result.exit_code == 0
        assert 'cleanup' in result.output.lower()


class TestErrorHandling:
    """错误处理测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
    
    def test_invalid_layout_type(self):
        """测试无效布局类型"""
        result = self.runner.invoke(cli, ['layout', 'apply', 'invalid_layout'])
        assert result.exit_code != 0
        assert 'invalid' in result.output.lower() or 'error' in result.output.lower()
    
    def test_invalid_output_format(self):
        """测试无效输出格式"""
        result = self.runner.invoke(cli, ['--output', 'invalid_format', 'layout', 'list'])
        assert result.exit_code != 0
    
    def test_invalid_hotkey_format(self):
        """测试无效热键格式"""
        result = self.runner.invoke(cli, ['--dry-run', 'hotkey', 'add', 'invalid_hotkey', 'test'])
        assert result.exit_code != 0
    
    def test_missing_required_args(self):
        """测试缺少必需参数"""
        result = self.runner.invoke(cli, ['window', 'move', 'test'])
        assert result.exit_code != 0
        assert 'required' in result.output.lower() or 'missing' in result.output.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])