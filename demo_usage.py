#!/usr/bin/env python3
"""
Win-Manager 使用演示脚本
演示如何使用 win-manager 进行简单的窗口管理
"""

import os
import sys
import time

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from win_manager.core.window_manager import WindowManager
from win_manager.core.config_manager import ConfigManager
from win_manager.utils.hotkey_manager import HotkeyManager


def demo_basic_window_operations():
    """演示基本窗口操作"""
    print("=== 基本窗口管理演示 ===")
    
    # 创建窗口管理器
    manager = WindowManager()
    
    # 1. 获取当前所有可管理的窗口
    print("\n1. 获取可管理的窗口...")
    windows = manager.get_manageable_windows()
    print(f"找到 {len(windows)} 个可管理的窗口:")
    
    for i, window in enumerate(windows[:5]):  # 只显示前5个
        print(f"  {i+1}. {window.title} ({window.process_name})")
    
    if len(windows) > 5:
        print(f"  ... 还有 {len(windows)-5} 个窗口")
    
    # 2. 应用不同的布局
    if windows:
        print("\n2. 应用布局...")
        
        # 瀑布布局
        print("  - 应用瀑布布局...")
        success = manager.organize_windows("cascade")
        if success:
            print("    ✅ 瀑布布局应用成功")
        else:
            print("    ❌ 瀑布布局应用失败")
        
        time.sleep(2)  # 等待2秒查看效果
        
        # 网格布局
        print("  - 应用网格布局...")
        success = manager.organize_windows("grid")
        if success:
            print("    ✅ 网格布局应用成功")
        else:
            print("    ❌ 网格布局应用失败")
        
        time.sleep(2)
        
        # 堆叠布局
        print("  - 应用堆叠布局...")
        success = manager.organize_windows("stack")
        if success:
            print("    ✅ 堆叠布局应用成功")
        else:
            print("    ❌ 堆叠布局应用失败")
    
    # 3. 撤销布局
    print("\n3. 撤销布局...")
    success = manager.undo_layout()
    if success:
        print("    ✅ 布局撤销成功")
    else:
        print("    ❌ 布局撤销失败")


def demo_configuration():
    """演示配置管理"""
    print("\n=== 配置管理演示 ===")
    
    # 创建配置管理器
    config = ConfigManager()
    
    # 1. 查看默认配置
    print("\n1. 默认配置设置:")
    print(f"  - 默认布局: {config.get('window_management.default_layout')}")
    print(f"  - 忽略最小化窗口: {config.get('filters.ignore_minimized')}")
    print(f"  - 日志级别: {config.get('advanced.log_level')}")
    
    # 2. 修改配置
    print("\n2. 修改配置...")
    config.set("window_management.default_layout", "grid")
    config.set("ui.show_notifications", True)
    
    # 3. 添加排除进程
    print("\n3. 添加排除进程...")
    config.add_excluded_process("explorer.exe")
    config.add_excluded_process("winlogon.exe")
    
    excluded = config.get_excluded_processes()
    print(f"  排除的进程: {excluded}")
    
    # 4. 保存配置
    print("\n4. 保存配置...")
    success = config.save_config()
    if success:
        print("    ✅ 配置保存成功")
    else:
        print("    ❌ 配置保存失败")


def demo_hotkey_setup():
    """演示热键设置"""
    print("\n=== 热键管理演示 ===")
    
    # 创建热键管理器
    hotkey_manager = HotkeyManager()
    
    # 创建窗口管理器用于热键回调
    window_manager = WindowManager()
    
    # 定义热键回调函数
    def cascade_layout():
        print("🔥 热键触发: 应用瀑布布局")
        window_manager.organize_windows("cascade")
    
    def grid_layout():
        print("🔥 热键触发: 应用网格布局")
        window_manager.organize_windows("grid")
    
    def stack_layout():
        print("🔥 热键触发: 应用堆叠布局")
        window_manager.organize_windows("stack")
    
    # 注册热键
    print("\n1. 注册热键...")
    hotkeys = [
        ("ctrl+alt+1", cascade_layout, "瀑布布局"),
        ("ctrl+alt+2", grid_layout, "网格布局"),
        ("ctrl+alt+3", stack_layout, "堆叠布局")
    ]
    
    for hotkey, callback, desc in hotkeys:
        success = hotkey_manager.register_hotkey(hotkey, callback)
        if success:
            print(f"  ✅ {hotkey} -> {desc}")
        else:
            print(f"  ❌ {hotkey} -> {desc} (注册失败)")
    
    # 显示已注册的热键
    registered = hotkey_manager.get_registered_hotkeys()
    print(f"\n2. 已注册的热键: {registered}")
    
    # 启动热键监听
    print("\n3. 启动热键监听...")
    success = hotkey_manager.start()
    if success:
        print("    ✅ 热键监听已启动")
        print("    💡 现在可以使用以下热键:")
        print("       - Ctrl+Alt+1: 瀑布布局")
        print("       - Ctrl+Alt+2: 网格布局")
        print("       - Ctrl+Alt+3: 堆叠布局")
        print("       - 按任意键继续...")
        input()  # 等待用户输入
    else:
        print("    ❌ 热键监听启动失败")
    
    # 停止热键监听
    print("\n4. 停止热键监听...")
    success = hotkey_manager.stop()
    if success:
        print("    ✅ 热键监听已停止")
    else:
        print("    ❌ 热键监听停止失败")


def demo_advanced_features():
    """演示高级功能"""
    print("\n=== 高级功能演示 ===")
    
    manager = WindowManager()
    
    # 1. 获取可用布局
    print("\n1. 可用的布局类型:")
    layouts = manager.get_available_layouts()
    for layout in layouts:
        print(f"  - {layout}")
    
    # 2. 获取详细窗口信息
    print("\n2. 详细窗口信息:")
    windows = manager.get_window_list()
    for i, window in enumerate(windows[:3]):  # 只显示前3个
        print(f"  窗口 {i+1}:")
        print(f"    - 标题: {window.title}")
        print(f"    - 进程: {window.process_name}")
        print(f"    - 句柄: {window.hwnd}")
        print(f"    - 位置: {window.rect}")
        print(f"    - 可见: {window.visible}")
        print(f"    - 可调整: {window.resizable}")
    
    # 3. 单独控制窗口
    if windows:
        print(f"\n3. 单独控制窗口示例 (使用第一个窗口):")
        first_window = windows[0]
        print(f"  操作窗口: {first_window.title}")
        
        # 获取窗口状态
        print("  - 检查窗口状态...")
        # 这里在实际使用中会调用真实的Windows API
        print("    (在实际运行中会显示窗口的最小化/最大化状态)")


def main():
    """主演示函数"""
    print("🪟 Win-Manager 窗口管理演示")
    print("=" * 50)
    
    try:
        # 演示基本功能
        demo_basic_window_operations()
        
        # 演示配置管理
        demo_configuration()
        
        # 演示热键功能
        print("\n是否演示热键功能? (y/n): ", end="")
        if input().lower() == 'y':
            demo_hotkey_setup()
        
        # 演示高级功能
        demo_advanced_features()
        
        print("\n🎉 演示完成！")
        print("\n💡 提示:")
        print("  - 这是一个模拟演示，实际使用时会操作真实窗口")
        print("  - 在Windows系统上运行时，所有功能都会正常工作")
        print("  - 建议在有多个窗口打开时测试布局功能")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断，演示结束")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        print("这可能是因为某些Windows API在非Windows系统上无法使用")


if __name__ == "__main__":
    main()