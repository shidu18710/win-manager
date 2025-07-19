"""
Hotkey management commands
"""
import click
import sys
import os
from typing import Optional

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from win_manager.utils.hotkey_manager import HotkeyManager
from ..utils.validation import validate_hotkey_combination, validate_window_target
from ..utils.helpers import get_error_message


@click.group()
def hotkey():
    """热键管理命令"""
    pass


@hotkey.command()
@click.pass_context
def list(ctx):
    """列出所有已注册的热键"""
    try:
        output = ctx.obj['output']
        
        output.info("列出已注册的热键")
        
        # 创建热键管理器
        hotkey_manager = HotkeyManager()
        
        # 获取已注册的热键
        registered_hotkeys = hotkey_manager.get_registered_hotkeys()
        
        # 格式化热键信息
        hotkey_data = []
        for hotkey_combo in registered_hotkeys:
            hotkey_data.append({
                'hotkey': hotkey_combo,
                'description': _get_hotkey_description(hotkey_combo),
                'status': 'registered'
            })
        
        output.print(hotkey_data, f"找到 {len(hotkey_data)} 个已注册的热键")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@hotkey.command()
@click.argument('key_combination', callback=validate_hotkey_combination)
@click.argument('action')
@click.option('--description', help='热键描述')
@click.option('--target', callback=validate_window_target, help='目标窗口过滤')
@click.pass_context
def add(ctx, key_combination: str, action: str, description: Optional[str], target: Optional[str]):
    """添加热键"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"添加热键: {key_combination} -> {action}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'hotkey': key_combination,
                'action': action,
                'description': description,
                'target': target,
                'dry_run': True
            }
            output.print(result_data, f"将添加热键: {key_combination}")
            return
        
        # 创建热键管理器
        hotkey_manager = HotkeyManager()
        
        # 创建热键回调函数
        def hotkey_callback():
            output.info(f"热键触发: {key_combination} -> {action}")
            # 这里应该根据action执行相应的操作
            _execute_hotkey_action(action, target, output)
        
        # 注册热键
        success = hotkey_manager.register_hotkey(key_combination, hotkey_callback)
        
        if success:
            result_data = {
                'hotkey': key_combination,
                'action': action,
                'description': description,
                'target': target,
                'status': 'registered'
            }
            output.print(result_data, f"热键添加成功: {key_combination}")
        else:
            output.error(f"热键添加失败: {key_combination}")
            sys.exit(1)
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@hotkey.command()
@click.argument('key_combination', callback=validate_hotkey_combination)
@click.pass_context
def remove(ctx, key_combination: str):
    """移除热键"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"移除热键: {key_combination}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'hotkey': key_combination,
                'action': 'remove',
                'dry_run': True
            }
            output.print(result_data, f"将移除热键: {key_combination}")
            return
        
        # 创建热键管理器
        hotkey_manager = HotkeyManager()
        
        # 移除热键
        success = hotkey_manager.unregister_hotkey(key_combination)
        
        if success:
            result_data = {
                'hotkey': key_combination,
                'action': 'remove',
                'status': 'success'
            }
            output.print(result_data, f"热键移除成功: {key_combination}")
        else:
            output.error(f"热键移除失败: {key_combination}")
            sys.exit(1)
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@hotkey.command()
@click.pass_context
def start(ctx):
    """启动热键监听"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info("启动热键监听")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'action': 'start_listening',
                'dry_run': True
            }
            output.print(result_data, "将启动热键监听")
            return
        
        # 创建热键管理器
        hotkey_manager = HotkeyManager()
        
        # 启动热键监听
        success = hotkey_manager.start()
        
        if success:
            result_data = {
                'action': 'start_listening',
                'status': 'success'
            }
            output.print(result_data, "热键监听启动成功")
            
            # 显示已注册的热键
            registered_hotkeys = hotkey_manager.get_registered_hotkeys()
            if registered_hotkeys:
                output.info("已注册的热键:")
                for hotkey_combo in registered_hotkeys:
                    output.info(f"  - {hotkey_combo}")
                output.info("按 Ctrl+C 停止监听")
                
                # 保持监听直到用户中断
                try:
                    input("按回车键停止监听...")
                except KeyboardInterrupt:
                    pass
                
                # 停止监听
                hotkey_manager.stop()
                output.info("热键监听已停止")
            else:
                output.warning("没有已注册的热键")
        else:
            output.error("热键监听启动失败")
            sys.exit(1)
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@hotkey.command()
@click.pass_context
def stop(ctx):
    """停止热键监听"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info("停止热键监听")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'action': 'stop_listening',
                'dry_run': True
            }
            output.print(result_data, "将停止热键监听")
            return
        
        # 创建热键管理器
        hotkey_manager = HotkeyManager()
        
        # 停止热键监听
        success = hotkey_manager.stop()
        
        if success:
            result_data = {
                'action': 'stop_listening',
                'status': 'success'
            }
            output.print(result_data, "热键监听停止成功")
        else:
            output.error("热键监听停止失败")
            sys.exit(1)
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


def _get_hotkey_description(hotkey_combo: str) -> str:
    """获取热键描述"""
    # 这里可以根据实际注册的热键返回描述
    # 目前返回通用描述
    return f"热键组合: {hotkey_combo}"


def _execute_hotkey_action(action: str, target: Optional[str], output):
    """执行热键动作"""
    try:
        from win_manager.core.window_manager import WindowManager
        
        # 创建窗口管理器
        manager = WindowManager()
        
        # 解析动作
        if action.startswith('layout apply '):
            layout_type = action.replace('layout apply ', '')
            success = manager.organize_windows(layout_type)
            if success:
                output.success(f"应用 {layout_type} 布局成功")
            else:
                output.error(f"应用 {layout_type} 布局失败")
        
        elif action == 'layout undo':
            success = manager.undo_layout()
            if success:
                output.success("撤销布局成功")
            else:
                output.error("撤销布局失败")
        
        elif action.startswith('window '):
            # 窗口操作
            window_action = action.replace('window ', '')
            if target:
                output.info(f"执行窗口操作: {window_action} 目标: {target}")
                # 这里应该实现具体的窗口操作
                output.warning("窗口操作需要实际的Windows API实现")
            else:
                output.warning("窗口操作需要指定目标窗口")
        
        else:
            output.warning(f"未知的热键动作: {action}")
            
    except Exception as e:
        output.error(f"执行热键动作失败: {get_error_message(e)}")


# 注册命令到主CLI
def register_hotkey_commands(cli_group):
    """注册热键命令到主CLI"""
    cli_group.add_command(hotkey)