"""
Layout management commands
"""
import click
import sys
import os
from typing import List, Optional, Dict

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from win_manager.core.window_manager import WindowManager
from ..utils.validation import (
    validate_layout_type, validate_window_target, validate_positive_integer,
    validate_non_negative_integer, validate_stack_position, DIMENSION_TYPE
)
from ..utils.helpers import get_error_message


@click.group()
def layout():
    """布局管理命令"""
    pass


@layout.command()
@click.argument('layout_type', callback=validate_layout_type)
@click.option('--target', multiple=True, callback=validate_window_target, 
              help='目标窗口过滤 (进程名、窗口标题等)')
@click.option('--exclude', multiple=True, callback=validate_window_target,
              help='排除窗口过滤 (可重复使用)')
@click.option('--columns', type=int, callback=validate_positive_integer,
              help='网格布局列数')
@click.option('--padding', type=int, callback=validate_non_negative_integer,
              help='窗口间距')
@click.option('--offset-x', type=int, callback=validate_non_negative_integer,
              help='瀑布布局 X 偏移')
@click.option('--offset-y', type=int, callback=validate_non_negative_integer,
              help='瀑布布局 Y 偏移')
@click.option('--stack-position', type=click.Choice(['center', 'left', 'right']),
              callback=validate_stack_position, help='堆叠位置')
@click.option('--window-width', type=DIMENSION_TYPE,
              help='窗口宽度 (像素值如800或百分比如50%)')
@click.option('--window-height', type=DIMENSION_TYPE,
              help='窗口高度 (像素值如600或百分比如75%)')
@click.pass_context
def apply(ctx, layout_type: str, target: tuple, exclude: tuple, columns: Optional[int],
          padding: Optional[int], offset_x: Optional[int], offset_y: Optional[int],
          stack_position: Optional[str], window_width: Optional[Dict], window_height: Optional[Dict]):
    """应用窗口布局"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"应用布局: {layout_type}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'layout_type': layout_type,
                'target_filters': list(target) if target else [],
                'exclude_filters': list(exclude) if exclude else [],
                'options': {
                    'columns': columns,
                    'padding': padding,
                    'offset_x': offset_x,
                    'offset_y': offset_y,
                    'stack_position': stack_position,
                    'window_width': window_width,
                    'window_height': window_height
                },
                'dry_run': True
            }
            output.print(result_data, f"将应用 {layout_type} 布局")
            return
        
        # 创建窗口管理器
        manager = WindowManager()
        
        # 获取可管理的窗口
        windows = manager.get_manageable_windows()
        
        # 应用过滤器
        if target:
            # 过滤目标窗口
            filtered_windows = []
            for window in windows:
                for target_filter in target:
                    if (target_filter.lower() in window.title.lower() or 
                        target_filter.lower() in window.process_name.lower()):
                        filtered_windows.append(window)
                        break
            windows = filtered_windows
        
        if exclude:
            # 排除窗口
            filtered_windows = []
            for window in windows:
                should_exclude = False
                for exclude_filter in exclude:
                    if (exclude_filter.lower() in window.title.lower() or 
                        exclude_filter.lower() in window.process_name.lower()):
                        should_exclude = True
                        break
                if not should_exclude:
                    filtered_windows.append(window)
            windows = filtered_windows
        
        if not windows:
            output.warning("没有找到可管理的窗口")
            result_data = {
                'windows_processed': 0,
                'layout_applied': None
            }
            output.print(result_data, "没有窗口可以应用布局")
            return
        
        # 应用布局
        layout_options = {}
        if columns is not None:
            layout_options['columns'] = columns
        if padding is not None:
            layout_options['padding'] = padding
        if offset_x is not None:
            layout_options['offset_x'] = offset_x
        if offset_y is not None:
            layout_options['offset_y'] = offset_y
        if stack_position is not None:
            layout_options['stack_position'] = stack_position
        if window_width is not None:
            layout_options['window_width'] = window_width
        if window_height is not None:
            layout_options['window_height'] = window_height
        
        success = manager.organize_windows(layout_type, **layout_options)
        
        if success:
            result_data = {
                'windows_processed': len(windows),
                'layout_applied': layout_type,
                'target_filters': list(target) if target else [],
                'exclude_filters': list(exclude) if exclude else [],
                'options': {
                    'columns': columns,
                    'padding': padding,
                    'offset_x': offset_x,
                    'offset_y': offset_y,
                    'stack_position': stack_position,
                    'window_width': window_width,
                    'window_height': window_height
                }
            }
            output.print(result_data, f"{layout_type} 布局应用成功")
        else:
            output.error(f"{layout_type} 布局应用失败")
            sys.exit(1)
            
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@layout.command()
@click.pass_context
def undo(ctx):
    """撤销上一次布局"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info("撤销上一次布局")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            output.print({'action': 'undo_layout', 'dry_run': True}, "将撤销上一次布局")
            return
        
        # 创建窗口管理器
        manager = WindowManager()
        
        # 撤销布局
        success = manager.undo_layout()
        
        if success:
            output.print({'action': 'undo_layout', 'success': True}, "布局撤销成功")
        else:
            output.error("布局撤销失败")
            sys.exit(1)
            
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@layout.command()
@click.argument('name')
@click.option('--description', help='布局描述')
@click.pass_context
def save(ctx, name: str, description: Optional[str]):
    """保存当前布局为自定义布局"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info(f"保存自定义布局: {name}")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            result_data = {
                'name': name,
                'description': description,
                'dry_run': True
            }
            output.print(result_data, f"将保存自定义布局: {name}")
            return
        
        # 这里应该实现保存自定义布局的逻辑
        # 目前只是模拟
        output.warning("自定义布局保存功能尚未实现")
        result_data = {
            'name': name,
            'description': description,
            'status': 'not_implemented'
        }
        output.print(result_data, f"自定义布局保存功能尚未实现")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@layout.command()
@click.pass_context
def list(ctx):
    """列出所有可用布局"""
    try:
        output = ctx.obj['output']
        
        output.info("列出可用布局")
        
        # 创建窗口管理器
        manager = WindowManager()
        
        # 获取可用布局
        layouts = manager.get_available_layouts()
        
        # 格式化布局信息
        layout_info = []
        for layout in layouts:
            layout_info.append({
                'name': layout,
                'description': _get_layout_description(layout),
                'type': 'built-in'
            })
        
        output.print(layout_info, f"找到 {len(layouts)} 个可用布局")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


def _get_layout_description(layout_name: str) -> str:
    """获取布局描述"""
    descriptions = {
        'cascade': '瀑布布局 - 窗口呈阶梯状排列',
        'grid': '网格布局 - 窗口均匀分布在屏幕上',
        'stack': '堆叠布局 - 窗口重叠排列在中心位置'
    }
    return descriptions.get(layout_name, '未知布局')


# 注册命令到主CLI
def register_layout_commands(cli_group):
    """注册布局命令到主CLI"""
    cli_group.add_command(layout)