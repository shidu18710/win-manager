"""
Configuration management commands
"""
import click
import sys
import os
from typing import Optional

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from win_manager.core.config_manager import ConfigManager
from ..utils.validation import validate_config_key, validate_file_path
from ..utils.helpers import get_error_message, confirm_action


@click.group()
def config():
    """配置管理命令"""
    pass


@config.command()
@click.option('--key', callback=validate_config_key, help='显示特定配置项')
@click.option('--section', help='显示特定配置节')
@click.pass_context
def show(ctx, key: Optional[str], section: Optional[str]):
    """显示当前配置"""
    try:
        output = ctx.obj['output']
        
        output.info("显示配置")
        
        # 获取CLI配置
        cli_config = ctx.obj['cli_config']
        
        # 创建核心配置管理器
        core_config = ConfigManager()
        
        if key:
            # 显示特定配置项
            cli_value = cli_config.get(key)
            core_value = core_config.get(key)
            
            config_data = {
                'key': key,
                'cli_config_value': cli_value,
                'core_config_value': core_value
            }
            output.print(config_data, f"配置项: {key}")
            
        elif section:
            # 显示特定配置节
            cli_section = cli_config.get(section, {})
            core_section = core_config.get(section, {})
            
            config_data = {
                'section': section,
                'cli_config': cli_section,
                'core_config': core_section
            }
            output.print(config_data, f"配置节: {section}")
            
        else:
            # 显示所有配置
            config_data = {
                'cli_config': cli_config.config,
                'core_config': core_config.config
            }
            output.print(config_data, "完整配置")
            
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@config.command()
@click.argument('key', callback=validate_config_key)
@click.argument('value')
@click.option('--target', type=click.Choice(['cli', 'core', 'both']), default='both',
              help='设置目标配置')
@click.pass_context
def set(ctx, key: str, value: str, target: str):
    """设置配置值"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"设置配置: {key} = {value}")
        
        # 尝试转换值类型
        parsed_value = _parse_config_value(value)
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'key': key,
                'value': parsed_value,
                'target': target,
                'dry_run': True
            }
            output.print(result_data, f"将设置 {key} = {parsed_value}")
            return
        
        # 设置配置
        if target in ['cli', 'both']:
            cli_config = ctx.obj['cli_config']
            cli_config.set(key, parsed_value)
            cli_config.save()
        
        if target in ['core', 'both']:
            core_config = ConfigManager()
            core_config.set(key, parsed_value)
            core_config.save_config()
        
        result_data = {
            'key': key,
            'value': parsed_value,
            'target': target
        }
        output.print(result_data, f"配置设置成功: {key} = {parsed_value}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@config.command()
@click.argument('key', callback=validate_config_key)
@click.option('--target', type=click.Choice(['cli', 'core', 'both']), default='both',
              help='获取目标配置')
@click.pass_context
def get(ctx, key: str, target: str):
    """获取配置值"""
    try:
        output = ctx.obj['output']
        
        output.info(f"获取配置: {key}")
        
        result_data = {'key': key}
        
        if target in ['cli', 'both']:
            cli_config = ctx.obj['cli_config']
            result_data['cli_value'] = cli_config.get(key)
        
        if target in ['core', 'both']:
            core_config = ConfigManager()
            result_data['core_value'] = core_config.get(key)
        
        output.print(result_data, f"配置值: {key}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@config.command()
@click.option('--key', callback=validate_config_key, help='重置特定配置项')
@click.option('--target', type=click.Choice(['cli', 'core', 'both']), default='both',
              help='重置目标配置')
@click.option('--confirm', is_flag=True, help='确认重置')
@click.pass_context
def reset(ctx, key: Optional[str], target: str, confirm: bool):
    """重置配置"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        if key:
            output.info(f"重置配置项: {key}")
            action_desc = f"重置配置项 {key}"
        else:
            output.info("重置所有配置")
            action_desc = "重置所有配置"
        
        if not confirm and not dry_run:
            if not confirm_action(f"确定要{action_desc}吗？此操作不可撤销。"):
                output.info("操作已取消")
                return
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'key': key,
                'target': target,
                'action': 'reset',
                'dry_run': True
            }
            output.print(result_data, f"将{action_desc}")
            return
        
        # 重置配置
        if target in ['cli', 'both']:
            cli_config = ctx.obj['cli_config']
            if key:
                # 重置特定配置项（设置为默认值）
                cli_config.set(key, None)
                cli_config.save()
            else:
                # 重置所有配置
                cli_config.reset()
        
        if target in ['core', 'both']:
            core_config = ConfigManager()
            if key:
                # 重置特定配置项
                core_config.set(key, None)
                core_config.save_config()
            else:
                # 重置所有配置
                core_config.reset_config()
        
        result_data = {
            'key': key,
            'target': target,
            'action': 'reset'
        }
        output.print(result_data, f"{action_desc}成功")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@config.command()
@click.argument('path', callback=validate_file_path)
@click.option('--format', type=click.Choice(['json', 'yaml']), default='yaml',
              help='导出格式')
@click.option('--target', type=click.Choice(['cli', 'core', 'both']), default='both',
              help='导出目标配置')
@click.pass_context
def export(ctx, path: str, format: str, target: str):
    """导出配置"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"导出配置到: {path}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'path': path,
                'format': format,
                'target': target,
                'dry_run': True
            }
            output.print(result_data, f"将导出配置到: {path}")
            return
        
        # 收集配置数据
        export_data = {}
        
        if target in ['cli', 'both']:
            cli_config = ctx.obj['cli_config']
            export_data['cli_config'] = cli_config.config
        
        if target in ['core', 'both']:
            core_config = ConfigManager()
            export_data['core_config'] = core_config.config
        
        # 导出配置
        if format == 'json':
            import json
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        else:  # yaml
            import yaml
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
        
        result_data = {
            'path': path,
            'format': format,
            'target': target,
            'size': os.path.getsize(path)
        }
        output.print(result_data, f"配置导出成功: {path}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@config.command()
@click.argument('path', callback=validate_file_path)
@click.option('--target', type=click.Choice(['cli', 'core', 'both']), default='both',
              help='导入目标配置')
@click.pass_context
def import_config(ctx, path: str, target: str):
    """导入配置"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"导入配置从: {path}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'path': path,
                'target': target,
                'dry_run': True
            }
            output.print(result_data, f"将导入配置从: {path}")
            return
        
        # 读取配置文件
        if path.endswith('.json'):
            import json
            with open(path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
        else:  # yaml
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                import_data = yaml.safe_load(f)
        
        # 导入配置
        if target in ['cli', 'both'] and 'cli_config' in import_data:
            cli_config = ctx.obj['cli_config']
            cli_config.config.update(import_data['cli_config'])
            cli_config.save()
        
        if target in ['core', 'both'] and 'core_config' in import_data:
            core_config = ConfigManager()
            for key, value in import_data['core_config'].items():
                core_config.set(key, value)
            core_config.save_config()
        
        result_data = {
            'path': path,
            'target': target,
            'imported_items': len(import_data)
        }
        output.print(result_data, f"配置导入成功: {path}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


def _parse_config_value(value: str):
    """解析配置值"""
    # 尝试解析为布尔值
    if value.lower() in ['true', 'false']:
        return value.lower() == 'true'
    
    # 尝试解析为整数
    try:
        return int(value)
    except ValueError:
        pass
    
    # 尝试解析为浮点数
    try:
        return float(value)
    except ValueError:
        pass
    
    # 尝试解析为列表（逗号分隔）
    if ',' in value:
        return [item.strip() for item in value.split(',')]
    
    # 默认返回字符串
    return value


# 注册命令到主CLI
def register_config_commands(cli_group):
    """注册配置命令到主CLI"""
    cli_group.add_command(config)