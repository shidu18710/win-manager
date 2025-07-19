"""
Parameter validation utilities
"""
import click
from typing import Any, Dict, List, Optional, Union


def validate_window_target(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证窗口目标参数"""
    if value is None:
        return value
    
    # 可以是窗口ID、进程名或窗口标题
    value_str = str(value).strip()
    if not value_str:
        raise click.BadParameter("窗口目标不能为空")
    
    return value_str


def validate_layout_type(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证布局类型"""
    if value is None:
        return value
    
    valid_layouts = ['cascade', 'grid', 'stack']
    if value not in valid_layouts:
        raise click.BadParameter(f"无效的布局类型: {value}。有效选项: {', '.join(valid_layouts)}")
    
    return value


def validate_positive_integer(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证正整数"""
    if value is None:
        return value
    
    try:
        int_value = int(value)
        if int_value <= 0:
            raise click.BadParameter(f"{param.name} 必须是正整数")
        return int_value
    except ValueError:
        raise click.BadParameter(f"{param.name} 必须是整数")


def validate_non_negative_integer(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证非负整数"""
    if value is None:
        return value
    
    try:
        int_value = int(value)
        if int_value < 0:
            raise click.BadParameter(f"{param.name} 必须是非负整数")
        return int_value
    except ValueError:
        raise click.BadParameter(f"{param.name} 必须是整数")


def validate_hotkey_combination(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证热键组合"""
    if value is None:
        return value
    
    hotkey = str(value).strip().lower()
    if not hotkey:
        raise click.BadParameter("热键组合不能为空")
    
    # 检查基本格式
    if '+' not in hotkey:
        raise click.BadParameter("热键组合必须包含修饰符，格式: modifier+key")
    
    parts = hotkey.split('+')
    if len(parts) < 2:
        raise click.BadParameter("热键组合格式错误，格式: modifier+key")
    
    valid_modifiers = ['ctrl', 'alt', 'shift', 'win']
    modifiers = parts[:-1]
    key = parts[-1]
    
    # 检查修饰符
    for modifier in modifiers:
        if modifier not in valid_modifiers:
            raise click.BadParameter(f"无效的修饰符: {modifier}。有效选项: {', '.join(valid_modifiers)}")
    
    # 检查键
    if not key:
        raise click.BadParameter("热键组合必须包含键名")
    
    return hotkey


def validate_config_key(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证配置键"""
    if value is None:
        return value
    
    key = str(value).strip()
    if not key:
        raise click.BadParameter("配置键不能为空")
    
    # 检查键格式（支持点号表示法）
    if '..' in key or key.startswith('.') or key.endswith('.'):
        raise click.BadParameter("配置键格式错误，不能包含连续的点号或以点号开头/结尾")
    
    return key


def validate_file_path(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证文件路径"""
    if value is None:
        return value
    
    import os
    path = str(value).strip()
    if not path:
        raise click.BadParameter("文件路径不能为空")
    
    # 检查路径是否存在（对于输入文件）
    if param.name in ['config', 'import_path'] and not os.path.exists(path):
        raise click.BadParameter(f"文件不存在: {path}")
    
    return path


def validate_stack_position(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证堆叠位置"""
    if value is None:
        return value
    
    valid_positions = ['center', 'left', 'right']
    if value not in valid_positions:
        raise click.BadParameter(f"无效的堆叠位置: {value}。有效选项: {', '.join(valid_positions)}")
    
    return value


def validate_sort_by(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证排序字段"""
    if value is None:
        return value
    
    valid_fields = ['title', 'process', 'pid', 'size']
    if value not in valid_fields:
        raise click.BadParameter(f"无效的排序字段: {value}。有效选项: {', '.join(valid_fields)}")
    
    return value


def validate_coordinates(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证坐标"""
    if value is None:
        return value
    
    try:
        coord_value = int(value)
        # 坐标可以是负数（多显示器环境）
        return coord_value
    except ValueError:
        raise click.BadParameter(f"{param.name} 必须是整数")


def validate_size_dimension(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证尺寸参数"""
    if value is None:
        return value
    
    try:
        size_value = int(value)
        if size_value <= 0:
            raise click.BadParameter(f"{param.name} 必须是正整数")
        return size_value
    except ValueError:
        raise click.BadParameter(f"{param.name} 必须是整数")


def validate_filter_pattern(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证过滤模式"""
    if value is None:
        return value
    
    pattern = str(value).strip()
    if not pattern:
        raise click.BadParameter("过滤模式不能为空")
    
    # 这里可以添加更复杂的模式验证，比如正则表达式
    return pattern


def validate_component_name(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    """验证组件名称"""
    if value is None:
        return value
    
    valid_components = ['detector', 'controller', 'layout', 'config', 'hotkey', 'all']
    if value not in valid_components:
        raise click.BadParameter(f"无效的组件名称: {value}。有效选项: {', '.join(valid_components)}")
    
    return value


class PositionType(click.ParamType):
    """位置参数类型"""
    name = 'position'
    
    def convert(self, value, param, ctx):
        if value is None:
            return None
        
        try:
            # 格式: "x,y" 或 "x,y,width,height"
            parts = value.split(',')
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]))
            elif len(parts) == 4:
                return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
            else:
                self.fail(f"位置格式错误，应为 'x,y' 或 'x,y,width,height'", param, ctx)
        except ValueError:
            self.fail(f"无效的位置格式: {value}", param, ctx)


class SizeType(click.ParamType):
    """大小参数类型"""
    name = 'size'
    
    def convert(self, value, param, ctx):
        if value is None:
            return None
        
        try:
            # 格式: "width,height" 或 "widthxheight"
            if 'x' in value:
                parts = value.split('x')
            else:
                parts = value.split(',')
            
            if len(parts) == 2:
                width, height = int(parts[0]), int(parts[1])
                if width <= 0 or height <= 0:
                    self.fail("宽度和高度必须是正整数", param, ctx)
                return (width, height)
            else:
                self.fail("大小格式错误，应为 'width,height' 或 'widthxheight'", param, ctx)
        except ValueError:
            self.fail(f"无效的大小格式: {value}", param, ctx)


class DimensionType(click.ParamType):
    """尺寸参数类型 - 支持像素值和百分比"""
    name = 'dimension'
    
    def convert(self, value, param, ctx):
        if value is None:
            return None
        
        value_str = str(value).strip()
        if not value_str:
            self.fail("尺寸值不能为空", param, ctx)
        
        # 检查是否是百分比
        if value_str.endswith('%'):
            try:
                percentage = float(value_str[:-1])
                if percentage <= 0 or percentage > 100:
                    self.fail("百分比值必须在 0-100 之间", param, ctx)
                return {'type': 'percentage', 'value': percentage}
            except ValueError:
                self.fail(f"无效的百分比格式: {value_str}", param, ctx)
        else:
            # 像素值
            try:
                pixel_value = int(value_str)
                if pixel_value <= 0:
                    self.fail("像素值必须是正整数", param, ctx)
                return {'type': 'pixels', 'value': pixel_value}
            except ValueError:
                self.fail(f"无效的像素值: {value_str}", param, ctx)


# 自定义参数类型实例
POSITION_TYPE = PositionType()
SIZE_TYPE = SizeType()
DIMENSION_TYPE = DimensionType()