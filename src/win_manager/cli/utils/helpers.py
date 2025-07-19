"""
Helper utilities for CLI
"""
import logging
import sys
from typing import Any, Dict, List, Optional


def setup_logging(verbose: bool = False, quiet: bool = False):
    """设置日志系统"""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def validate_layout_type(layout_type: str) -> bool:
    """验证布局类型"""
    valid_layouts = ['cascade', 'grid', 'stack']
    return layout_type in valid_layouts


def validate_output_format(format: str) -> bool:
    """验证输出格式"""
    valid_formats = ['json', 'yaml', 'table', 'text']
    return format in valid_formats


def validate_window_id(window_id: str) -> bool:
    """验证窗口ID"""
    # 简单验证 - 可以是数字ID或窗口标题
    if window_id.isdigit():
        return True
    return len(window_id.strip()) > 0


def validate_hotkey(hotkey: str) -> bool:
    """验证热键格式"""
    # 简单验证热键格式：modifier+key
    if '+' not in hotkey:
        return False
    
    parts = hotkey.split('+')
    if len(parts) < 2:
        return False
    
    valid_modifiers = ['ctrl', 'alt', 'shift', 'win']
    modifiers = parts[:-1]
    key = parts[-1]
    
    # 检查修饰符
    for modifier in modifiers:
        if modifier.lower() not in valid_modifiers:
            return False
    
    # 检查键
    return len(key) > 0


def format_window_info(window_info: Dict[str, Any]) -> Dict[str, Any]:
    """格式化窗口信息"""
    return {
        'id': window_info.get('hwnd', 'N/A'),
        'title': window_info.get('title', 'N/A'),
        'process': window_info.get('process_name', 'N/A'),
        'position': f"({window_info.get('rect', (0, 0, 0, 0))[0]}, {window_info.get('rect', (0, 0, 0, 0))[1]})",
        'size': f"{window_info.get('rect', (0, 0, 0, 0))[2]}x{window_info.get('rect', (0, 0, 0, 0))[3]}",
        'visible': window_info.get('visible', False),
        'resizable': window_info.get('resizable', False)
    }


def format_window_list(windows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """格式化窗口列表"""
    return [format_window_info(window) for window in windows]


def parse_position(position_str: str) -> tuple:
    """解析位置字符串"""
    # 格式: "x,y" 或 "x,y,width,height"
    try:
        parts = position_str.split(',')
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
        elif len(parts) == 4:
            return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
        else:
            raise ValueError("位置格式错误")
    except ValueError:
        raise ValueError(f"无效的位置格式: {position_str}")


def parse_size(size_str: str) -> tuple:
    """解析大小字符串"""
    # 格式: "width,height" 或 "widthxheight"
    try:
        if 'x' in size_str:
            parts = size_str.split('x')
        else:
            parts = size_str.split(',')
        
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
        else:
            raise ValueError("大小格式错误")
    except ValueError:
        raise ValueError(f"无效的大小格式: {size_str}")


def get_error_message(error: Exception) -> str:
    """获取错误消息"""
    error_type = type(error).__name__
    return f"{error_type}: {str(error)}"


def confirm_action(message: str) -> bool:
    """确认操作"""
    try:
        response = input(f"{message} (y/N): ").lower().strip()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        return False


def truncate_string(text: str, max_length: int = 50) -> str:
    """截断字符串"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_bytes(bytes_value: int) -> str:
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"