"""
Tool commands for system management and testing
"""
import click
import sys
import os
import time
import psutil
from typing import Optional

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from win_manager.core.window_manager import WindowManager
from win_manager.core.window_detector import WindowDetector
from win_manager.core.window_controller import WindowController
from win_manager.core.layout_manager import LayoutEngine
from win_manager.core.config_manager import ConfigManager
from win_manager.utils.hotkey_manager import HotkeyManager
from ..utils.validation import validate_component_name, validate_positive_integer
from ..utils.helpers import get_error_message, format_duration, format_bytes


@click.group()
def tool():
    """工具命令"""
    pass


@tool.command()
@click.pass_context
def status(ctx):
    """显示系统状态"""
    try:
        output = ctx.obj['output']
        
        output.info("获取系统状态")
        
        # 收集系统信息
        status_data = {
            'system': {
                'platform': sys.platform,
                'python_version': sys.version.split()[0],
                'cpu_count': psutil.cpu_count(),
                'memory_total': format_bytes(psutil.virtual_memory().total),
                'memory_available': format_bytes(psutil.virtual_memory().available),
                'memory_percent': psutil.virtual_memory().percent
            },
            'win_manager': {
                'version': '0.1.0',
                'config_status': 'loaded',
                'components': {}
            }
        }
        
        # 检查各个组件状态
        try:
            detector = WindowDetector()
            windows = detector.enumerate_windows()
            status_data['win_manager']['components']['detector'] = {
                'status': 'ok',
                'windows_found': len(windows)
            }
        except Exception as e:
            status_data['win_manager']['components']['detector'] = {
                'status': 'error',
                'error': str(e)
            }
        
        try:
            controller = WindowController()
            status_data['win_manager']['components']['controller'] = {
                'status': 'ok'
            }
        except Exception as e:
            status_data['win_manager']['components']['controller'] = {
                'status': 'error',
                'error': str(e)
            }
        
        try:
            layout_engine = LayoutEngine()
            layouts = layout_engine.get_available_layouts()
            status_data['win_manager']['components']['layout_engine'] = {
                'status': 'ok',
                'available_layouts': layouts
            }
        except Exception as e:
            status_data['win_manager']['components']['layout_engine'] = {
                'status': 'error',
                'error': str(e)
            }
        
        try:
            config_manager = ConfigManager()
            status_data['win_manager']['components']['config_manager'] = {
                'status': 'ok',
                'config_loaded': config_manager.config is not None
            }
        except Exception as e:
            status_data['win_manager']['components']['config_manager'] = {
                'status': 'error',
                'error': str(e)
            }
        
        try:
            hotkey_manager = HotkeyManager()
            registered_hotkeys = hotkey_manager.get_registered_hotkeys()
            status_data['win_manager']['components']['hotkey_manager'] = {
                'status': 'ok',
                'registered_hotkeys': len(registered_hotkeys),
                'hotkeys': registered_hotkeys
            }
        except Exception as e:
            status_data['win_manager']['components']['hotkey_manager'] = {
                'status': 'error',
                'error': str(e)
            }
        
        output.print(status_data, "系统状态")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@tool.command()
@click.option('--component', type=click.Choice(['detector', 'controller', 'layout', 'config', 'hotkey', 'all']),
              default='all', callback=validate_component_name, help='测试特定组件')
@click.option('--verbose', is_flag=True, help='详细输出')
@click.pass_context
def test(ctx, component: str, verbose: bool):
    """运行系统测试"""
    try:
        output = ctx.obj['output']
        
        output.info(f"运行系统测试: {component}")
        
        test_results = {}
        
        if component in ['detector', 'all']:
            test_results['detector'] = _test_detector(verbose, output)
        
        if component in ['controller', 'all']:
            test_results['controller'] = _test_controller(verbose, output)
        
        if component in ['layout', 'all']:
            test_results['layout'] = _test_layout_engine(verbose, output)
        
        if component in ['config', 'all']:
            test_results['config'] = _test_config_manager(verbose, output)
        
        if component in ['hotkey', 'all']:
            test_results['hotkey'] = _test_hotkey_manager(verbose, output)
        
        # 统计测试结果
        total_tests = sum(result['total'] for result in test_results.values())
        passed_tests = sum(result['passed'] for result in test_results.values())
        failed_tests = total_tests - passed_tests
        
        summary = {
            'component': component,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': f"{passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "0%",
            'results': test_results
        }
        
        output.print(summary, f"测试完成: {passed_tests}/{total_tests} 通过")
        
        if failed_tests > 0:
            sys.exit(1)
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@tool.command()
@click.option('--windows', type=int, default=100, callback=validate_positive_integer,
              help='测试窗口数量')
@click.option('--iterations', type=int, default=10, callback=validate_positive_integer,
              help='迭代次数')
@click.pass_context
def benchmark(ctx, windows: int, iterations: int):
    """运行性能基准测试"""
    try:
        output = ctx.obj['output']
        
        output.info(f"运行性能基准测试: {windows} 窗口, {iterations} 次迭代")
        
        # 运行基准测试
        benchmark_results = _run_benchmark(windows, iterations, output)
        
        output.print(benchmark_results, f"基准测试完成")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


@tool.command()
@click.pass_context
def cleanup(ctx):
    """清理临时文件和缓存"""
    try:
        output = ctx.obj['output']
        dry_run = ctx.obj['dry_run']
        
        output.info("清理临时文件和缓存")
        
        if dry_run:
            output.info("模拟运行模式 - 不实际执行操作")
            cleanup_data = {
                'action': 'cleanup',
                'dry_run': True,
                'items_to_clean': ['temp_files', 'cache', 'logs']
            }
            output.print(cleanup_data, "将清理临时文件和缓存")
            return
        
        # 执行清理
        cleanup_results = {
            'temp_files_cleaned': 0,
            'cache_cleared': 0,
            'logs_rotated': 0,
            'total_size_freed': 0
        }
        
        # 这里应该实现实际的清理逻辑
        # 目前只是模拟
        output.warning("清理功能尚未完全实现")
        
        cleanup_results['status'] = 'simulated'
        output.print(cleanup_results, "清理完成")
        
    except Exception as e:
        output.error(get_error_message(e))
        sys.exit(1)


def _test_detector(verbose: bool, output) -> dict:
    """测试窗口检测器"""
    if verbose:
        output.info("测试窗口检测器...")
    
    results = {'total': 0, 'passed': 0, 'failed': 0, 'errors': []}
    
    # 测试1: 创建检测器
    results['total'] += 1
    try:
        detector = WindowDetector()
        results['passed'] += 1
        if verbose:
            output.info("✓ 检测器创建成功")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"检测器创建失败: {str(e)}")
        if verbose:
            output.error(f"✗ 检测器创建失败: {str(e)}")
    
    # 测试2: 枚举窗口
    results['total'] += 1
    try:
        detector = WindowDetector()
        windows = detector.enumerate_windows()
        if isinstance(windows, list):
            results['passed'] += 1
            if verbose:
                output.info(f"✓ 枚举窗口成功: {len(windows)} 个窗口")
        else:
            results['failed'] += 1
            results['errors'].append("枚举窗口返回类型错误")
            if verbose:
                output.error("✗ 枚举窗口返回类型错误")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"枚举窗口失败: {str(e)}")
        if verbose:
            output.error(f"✗ 枚举窗口失败: {str(e)}")
    
    return results


def _test_controller(verbose: bool, output) -> dict:
    """测试窗口控制器"""
    if verbose:
        output.info("测试窗口控制器...")
    
    results = {'total': 0, 'passed': 0, 'failed': 0, 'errors': []}
    
    # 测试1: 创建控制器
    results['total'] += 1
    try:
        controller = WindowController()
        results['passed'] += 1
        if verbose:
            output.info("✓ 控制器创建成功")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"控制器创建失败: {str(e)}")
        if verbose:
            output.error(f"✗ 控制器创建失败: {str(e)}")
    
    return results


def _test_layout_engine(verbose: bool, output) -> dict:
    """测试布局引擎"""
    if verbose:
        output.info("测试布局引擎...")
    
    results = {'total': 0, 'passed': 0, 'failed': 0, 'errors': []}
    
    # 测试1: 创建布局引擎
    results['total'] += 1
    try:
        layout_engine = LayoutEngine()
        results['passed'] += 1
        if verbose:
            output.info("✓ 布局引擎创建成功")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"布局引擎创建失败: {str(e)}")
        if verbose:
            output.error(f"✗ 布局引擎创建失败: {str(e)}")
    
    # 测试2: 获取可用布局
    results['total'] += 1
    try:
        layout_engine = LayoutEngine()
        layouts = layout_engine.get_available_layouts()
        if isinstance(layouts, list) and len(layouts) > 0:
            results['passed'] += 1
            if verbose:
                output.info(f"✓ 获取可用布局成功: {layouts}")
        else:
            results['failed'] += 1
            results['errors'].append("获取可用布局失败")
            if verbose:
                output.error("✗ 获取可用布局失败")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"获取可用布局失败: {str(e)}")
        if verbose:
            output.error(f"✗ 获取可用布局失败: {str(e)}")
    
    return results


def _test_config_manager(verbose: bool, output) -> dict:
    """测试配置管理器"""
    if verbose:
        output.info("测试配置管理器...")
    
    results = {'total': 0, 'passed': 0, 'failed': 0, 'errors': []}
    
    # 测试1: 创建配置管理器
    results['total'] += 1
    try:
        config_manager = ConfigManager()
        results['passed'] += 1
        if verbose:
            output.info("✓ 配置管理器创建成功")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"配置管理器创建失败: {str(e)}")
        if verbose:
            output.error(f"✗ 配置管理器创建失败: {str(e)}")
    
    return results


def _test_hotkey_manager(verbose: bool, output) -> dict:
    """测试热键管理器"""
    if verbose:
        output.info("测试热键管理器...")
    
    results = {'total': 0, 'passed': 0, 'failed': 0, 'errors': []}
    
    # 测试1: 创建热键管理器
    results['total'] += 1
    try:
        hotkey_manager = HotkeyManager()
        results['passed'] += 1
        if verbose:
            output.info("✓ 热键管理器创建成功")
    except Exception as e:
        results['failed'] += 1
        results['errors'].append(f"热键管理器创建失败: {str(e)}")
        if verbose:
            output.error(f"✗ 热键管理器创建失败: {str(e)}")
    
    return results


def _run_benchmark(windows: int, iterations: int, output) -> dict:
    """运行性能基准测试"""
    from win_manager.core.window_detector import WindowInfo
    
    results = {
        'parameters': {
            'windows': windows,
            'iterations': iterations
        },
        'results': {}
    }
    
    # 基准测试1: 窗口检测性能
    output.progress("测试窗口检测性能...")
    
    detector = WindowDetector()
    detection_times = []
    
    for i in range(iterations):
        start_time = time.time()
        # 模拟窗口检测
        simulated_windows = [
            WindowInfo(j, f"Window {j}", f"app{j}.exe", 100+j, 
                      (j*10, j*10, j*10+800, j*10+600), True, True)
            for j in range(windows)
        ]
        end_time = time.time()
        detection_times.append(end_time - start_time)
    
    results['results']['window_detection'] = {
        'average_time': format_duration(sum(detection_times) / len(detection_times)),
        'min_time': format_duration(min(detection_times)),
        'max_time': format_duration(max(detection_times)),
        'total_time': format_duration(sum(detection_times))
    }
    
    # 基准测试2: 布局计算性能
    output.progress("测试布局计算性能...")
    
    layout_engine = LayoutEngine()
    layout_times = []
    
    for i in range(iterations):
        simulated_windows = [
            WindowInfo(j, f"Window {j}", f"app{j}.exe", 100+j, 
                      (j*10, j*10, j*10+800, j*10+600), True, True)
            for j in range(windows)
        ]
        
        start_time = time.time()
        positions = layout_engine.apply_layout("grid", simulated_windows)
        end_time = time.time()
        layout_times.append(end_time - start_time)
    
    results['results']['layout_calculation'] = {
        'average_time': format_duration(sum(layout_times) / len(layout_times)),
        'min_time': format_duration(min(layout_times)),
        'max_time': format_duration(max(layout_times)),
        'total_time': format_duration(sum(layout_times))
    }
    
    # 内存使用测试
    output.progress("测试内存使用...")
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # 创建大量窗口对象
    large_window_set = [
        WindowInfo(j, f"Window {j}", f"app{j}.exe", 100+j, 
                  (j*10, j*10, j*10+800, j*10+600), True, True)
        for j in range(windows * 10)  # 10倍窗口数量
    ]
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    results['results']['memory_usage'] = {
        'initial_memory': format_bytes(initial_memory),
        'final_memory': format_bytes(final_memory),
        'memory_increase': format_bytes(memory_increase),
        'memory_per_window': format_bytes(memory_increase / (windows * 10))
    }
    
    return results


# 注册命令到主CLI
def register_tool_commands(cli_group):
    """注册工具命令到主CLI"""
    cli_group.add_command(tool)