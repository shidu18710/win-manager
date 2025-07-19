"""
CLI main entry point for Win-Manager
"""
import sys
import click
from typing import Optional, Dict

from .utils.output import OutputManager
from .utils.helpers import setup_logging
from .config.cli_config import CLIConfig
from .utils.validation import DIMENSION_TYPE

# 导入所有命令模块
from .commands.layout import register_layout_commands
from .commands.window import register_window_commands
from .commands.config import register_config_commands
from .commands.hotkey import register_hotkey_commands
from .commands.tool import register_tool_commands


@click.group()
@click.option('--config', type=click.Path(exists=True), help='指定配置文件路径')
@click.option('--output', type=click.Choice(['json', 'yaml', 'table', 'text']),
              default='table', help='输出格式')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--quiet', '-q', is_flag=True, help='静默模式')
@click.option('--dry-run', is_flag=True, help='模拟运行，不实际执行操作')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], output: str, verbose: bool,
        quiet: bool, dry_run: bool):
    """Win-Manager 命令行工具 - 强大的 Windows 窗口管理工具"""
    # 确保 context 对象存在
    ctx.ensure_object(dict)

    # 设置全局配置
    ctx.obj['config_path'] = config
    ctx.obj['output_format'] = output
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    ctx.obj['dry_run'] = dry_run

    # 初始化配置管理器
    cli_config = CLIConfig(config_path=config)
    ctx.obj['cli_config'] = cli_config

    # 初始化输出管理器
    output_manager = OutputManager(format=output, verbose=verbose, quiet=quiet)
    ctx.obj['output'] = output_manager

    # 设置日志
    setup_logging(verbose=verbose, quiet=quiet)


# 快捷命令 - 直接应用布局
@cli.command()
@click.option('--target', multiple=True, help='目标窗口过滤')
@click.option('--exclude', multiple=True, help='排除窗口过滤')
@click.option('--columns', type=int, help='网格列数')
@click.option('--padding', type=int, help='窗口间距')
@click.pass_context
def grid(ctx, target: tuple, exclude: tuple, columns: Optional[int], padding: Optional[int]):
    """快捷命令: 应用网格布局"""
    from .commands.layout import apply
    ctx.invoke(apply, layout_type='grid', target=target, exclude=exclude,
               columns=columns, padding=padding, offset_x=None, offset_y=None,
               stack_position=None, window_width=None, window_height=None)


@cli.command()
@click.option('--target', multiple=True, help='目标窗口过滤')
@click.option('--exclude', multiple=True, help='排除窗口过滤')
@click.option('--offset-x', type=int, help='X 偏移')
@click.option('--offset-y', type=int, help='Y 偏移')
@click.pass_context
def cascade(ctx, target: tuple, exclude: tuple, offset_x: Optional[int], offset_y: Optional[int]):
    """快捷命令: 应用瀑布布局"""
    from .commands.layout import apply
    ctx.invoke(apply, layout_type='cascade', target=target, exclude=exclude,
               columns=None, padding=None, offset_x=offset_x, offset_y=offset_y,
               stack_position=None, window_width=None, window_height=None)


@cli.command()
@click.option('--target', multiple=True, help='目标窗口过滤')
@click.option('--exclude', multiple=True, help='排除窗口过滤')
@click.option('--stack-position', type=click.Choice(['center', 'left', 'right']),
              help='堆叠位置')
@click.option('--window-width', type=DIMENSION_TYPE, help='窗口宽度 (像素值如800或百分比如50%)')
@click.option('--window-height', type=DIMENSION_TYPE, help='窗口高度 (像素值如600或百分比如75%)')
@click.pass_context
def stack(ctx, target: tuple, exclude: tuple, stack_position: Optional[str],
          window_width: Optional[Dict], window_height: Optional[Dict]):
    """快捷命令: 应用堆叠布局"""
    from .commands.layout import apply
    ctx.invoke(apply, layout_type='stack', target=target, exclude=exclude,
               columns=None, padding=None, offset_x=None, offset_y=None,
               stack_position=stack_position, window_width=window_width, window_height=window_height)


@cli.command()
@click.pass_context
def undo(ctx):
    """快捷命令: 撤销布局"""
    from .commands.layout import undo
    ctx.invoke(undo)


@cli.command()
@click.option('--filter', 'filter_pattern', help='过滤条件')
@click.option('--include-minimized', is_flag=True, help='包含最小化窗口')
@click.option('--sort-by', type=click.Choice(['title', 'process', 'pid', 'size']),
              help='排序方式')
@click.pass_context
def ls(ctx, filter_pattern: Optional[str], include_minimized: bool, sort_by: Optional[str]):
    """快捷命令: 列出窗口"""
    from .commands.window import list
    ctx.invoke(list, filter_pattern=filter_pattern, include_minimized=include_minimized,
               sort_by=sort_by, detailed=False)


def main():
    """主入口函数"""
    try:
        # 注册所有命令组
        register_layout_commands(cli)
        register_window_commands(cli)
        register_config_commands(cli)
        register_hotkey_commands(cli)
        register_tool_commands(cli)

        # 启动CLI
        cli()
    except KeyboardInterrupt:
        click.echo("\n操作被用户中断", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
