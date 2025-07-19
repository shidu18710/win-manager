"""
Window management commands
"""
import click
import sys
import os
from typing import List, Optional

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from win_manager.core.window_manager import WindowManager
from ..utils.validation import (
    validate_window_target, validate_sort_by, validate_coordinates,
    validate_size_dimension, validate_filter_pattern
)
from ..utils.helpers import get_error_message, format_window_list


@click.group()
def window():
    """窗口管理命令"""
    pass


@window.command()
@click.option('--filter', 'filter_pattern', callback=validate_filter_pattern,
              help='过滤条件 (进程名、标题等)')
@click.option('--include-minimized', is_flag=True, help='包含最小化窗口')
@click.option('--sort-by', type=click.Choice(['title', 'process', 'pid', 'size']),
              callback=validate_sort_by, help='排序方式')
@click.option('--detailed', is_flag=True, help='显示详细信息')
@click.pass_context
def list(ctx, filter_pattern: Optional[str], include_minimized: bool, 
         sort_by: Optional[str], detailed: bool):
    """列出所有可管理的窗口"""
    try:
        output = ctx.obj['output']
        
        output.info("获取窗口列表")
        
        # 创建窗口管理器
        manager = WindowManager()
        
        # 获取窗口列表
        if include_minimized:
            windows = manager.get_window_list()
        else:
            windows = manager.get_manageable_windows()
        
        # 应用过滤器
        if filter_pattern:
            filtered_windows = []
            for window in windows:
                if (filter_pattern.lower() in window.title.lower() or 
                    filter_pattern.lower() in window.process_name.lower()):
                    filtered_windows.append(window)
            windows = filtered_windows
        
        # 转换为字典格式
        window_data = []
        for window in windows:
            window_info = {
                'id': window.hwnd,
                'title': window.title,
                'process': window.process_name,
                'pid': window.pid,
                'position': f"({window.rect[0]}, {window.rect[1]})",
                'size': f"{window.rect[2]}x{window.rect[3]}" if len(window.rect) >= 4 else "N/A",
                'visible': window.is_visible,
                'resizable': window.is_resizable
            }
            
            if detailed:
                window_info.update({
                    'rect': window.rect,
                    'class_name': getattr(window, 'class_name', 'N/A'),
                    'style': getattr(window, 'style', 'N/A')
                })
            
            window_data.append(window_info)
        
        # 排序
        if sort_by:
            if sort_by == 'title':
                window_data.sort(key=lambda x: x['title'])
            elif sort_by == 'process':
                window_data.sort(key=lambda x: x['process'])
            elif sort_by == 'pid':
                window_data.sort(key=lambda x: x['pid'])
            elif sort_by == 'size':
                window_data.sort(key=lambda x: x['size'])
        
        output.print(window_data, f"找到 {len(window_data)} 个窗口")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@window.command()
@click.argument('window_id', callback=validate_window_target)
@click.pass_context
def info(ctx, window_id: str):
    """显示特定窗口信息"""
    try:
        output = ctx.obj['output']
        
        output.info(f"获取窗口信息: {window_id}")
        
        # 创建窗口管理器
        manager = WindowManager()
        
        # 获取所有窗口
        windows = manager.get_window_list()
        
        # 查找目标窗口
        target_window = None
        for window in windows:
            if (str(window.hwnd) == window_id or 
                window_id.lower() in window.title.lower()):
                target_window = window
                break
        
        if not target_window:
            output.error(f"找不到窗口: {window_id}")
            sys.exit(1)
        
        # 构建详细信息
        window_info = {
            'id': target_window.hwnd,
            'title': target_window.title,
            'process': target_window.process_name,
            'pid': target_window.pid,
            'position': {
                'x': target_window.rect[0],
                'y': target_window.rect[1]
            },
            'size': {
                'width': target_window.rect[2] if len(target_window.rect) >= 4 else 0,
                'height': target_window.rect[3] if len(target_window.rect) >= 4 else 0
            },
            'rect': target_window.rect,
            'visible': target_window.is_visible,
            'resizable': target_window.is_resizable,
            'class_name': getattr(target_window, 'class_name', 'N/A'),
            'style': getattr(target_window, 'style', 'N/A')
        }
        
        output.print(window_info, f"窗口信息: {target_window.title}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@window.command()
@click.argument('window_id', callback=validate_window_target)
@click.option('--x', type=int, callback=validate_coordinates, required=True, help='X 坐标')
@click.option('--y', type=int, callback=validate_coordinates, required=True, help='Y 坐标')
@click.option('--width', type=int, callback=validate_size_dimension, help='窗口宽度')
@click.option('--height', type=int, callback=validate_size_dimension, help='窗口高度')
@click.pass_context
def move(ctx, window_id: str, x: int, y: int, width: Optional[int], height: Optional[int]):
    """移动窗口"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"移动窗口: {window_id} 到 ({x}, {y})")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'window_id': window_id,
                'target_position': {'x': x, 'y': y},
                'target_size': {'width': width, 'height': height} if width and height else None,
                'dry_run': True
            }
            output.print(result_data, f"将移动窗口到 ({x}, {y})")
            return
        
        # 这里应该实现实际的窗口移动逻辑
        # 目前只是模拟
        output.warning("窗口移动功能需要实际的Windows API实现")
        result_data = {
            'window_id': window_id,
            'target_position': {'x': x, 'y': y},
            'target_size': {'width': width, 'height': height} if width and height else None,
            'status': 'simulated'
        }
        output.print(result_data, f"模拟移动窗口到 ({x}, {y})")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@window.command()
@click.argument('window_id', callback=validate_window_target)
@click.option('--width', type=int, callback=validate_size_dimension, required=True, help='窗口宽度')
@click.option('--height', type=int, callback=validate_size_dimension, required=True, help='窗口高度')
@click.pass_context
def resize(ctx, window_id: str, width: int, height: int):
    """调整窗口大小"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"调整窗口大小: {window_id} 到 {width}x{height}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'window_id': window_id,
                'target_size': {'width': width, 'height': height},
                'dry_run': True
            }
            output.print(result_data, f"将调整窗口大小到 {width}x{height}")
            return
        
        # 这里应该实现实际的窗口调整大小逻辑
        # 目前只是模拟
        output.warning("窗口调整大小功能需要实际的Windows API实现")
        result_data = {
            'window_id': window_id,
            'target_size': {'width': width, 'height': height},
            'status': 'simulated'
        }
        output.print(result_data, f"模拟调整窗口大小到 {width}x{height}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@window.command()
@click.argument('window_id', callback=validate_window_target)
@click.pass_context
def minimize(ctx, window_id: str):
    """最小化窗口"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"最小化窗口: {window_id}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'window_id': window_id,
                'action': 'minimize',
                'dry_run': True
            }
            output.print(result_data, f"将最小化窗口: {window_id}")
            return
        
        # 这里应该实现实际的窗口最小化逻辑
        # 目前只是模拟
        output.warning("窗口最小化功能需要实际的Windows API实现")
        result_data = {
            'window_id': window_id,
            'action': 'minimize',
            'status': 'simulated'
        }
        output.print(result_data, f"模拟最小化窗口: {window_id}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@window.command()
@click.argument('window_id', callback=validate_window_target)
@click.pass_context
def maximize(ctx, window_id: str):
    """最大化窗口"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"最大化窗口: {window_id}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'window_id': window_id,
                'action': 'maximize',
                'dry_run': True
            }
            output.print(result_data, f"将最大化窗口: {window_id}")
            return
        
        # 这里应该实现实际的窗口最大化逻辑
        # 目前只是模拟
        output.warning("窗口最大化功能需要实际的Windows API实现")
        result_data = {
            'window_id': window_id,
            'action': 'maximize',
            'status': 'simulated'
        }
        output.print(result_data, f"模拟最大化窗口: {window_id}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@window.command()
@click.argument('window_id', callback=validate_window_target)
@click.pass_context
def restore(ctx, window_id: str):
    """恢复窗口"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"恢复窗口: {window_id}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'window_id': window_id,
                'action': 'restore',
                'dry_run': True
            }
            output.print(result_data, f"将恢复窗口: {window_id}")
            return
        
        # 这里应该实现实际的窗口恢复逻辑
        # 目前只是模拟
        output.warning("窗口恢复功能需要实际的Windows API实现")
        result_data = {
            'window_id': window_id,
            'action': 'restore',
            'status': 'simulated'
        }
        output.print(result_data, f"模拟恢复窗口: {window_id}")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


# 注册命令到主CLI
def register_window_commands(cli_group):
    """注册窗口命令到主CLI"""
    cli_group.add_command(window)