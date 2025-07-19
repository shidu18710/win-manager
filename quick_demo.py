#!/usr/bin/env python3
"""
Win-Manager 快速使用示例
简单的窗口管理操作
"""

import os
import sys

# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from win_manager.core.window_manager import WindowManager


def quick_demo():
    """快速演示窗口管理功能"""
    print("🪟 Win-Manager 快速演示")
    print("-" * 30)
    
    # 创建窗口管理器
    manager = WindowManager()
    
    # 1. 获取可管理的窗口
    print("1. 获取窗口列表...")
    windows = manager.get_manageable_windows()
    print(f"   找到 {len(windows)} 个可管理的窗口")
    
    if not windows:
        print("   ⚠️ 没有找到可管理的窗口")
        print("   💡 请打开一些应用程序窗口后再试")
        return
    
    # 显示窗口信息
    print("\n2. 窗口信息:")
    for i, window in enumerate(windows[:5]):  # 只显示前5个
        print(f"   {i+1}. {window.title}")
    
    if len(windows) > 5:
        print(f"   ... 还有 {len(windows)-5} 个窗口")
    
    # 2. 应用布局
    print("\n3. 应用窗口布局...")
    
    # 尝试应用网格布局
    print("   - 尝试网格布局...")
    success = manager.organize_windows("grid")
    if success:
        print("   ✅ 网格布局应用成功！")
    else:
        print("   ❌ 网格布局应用失败")
    
    # 获取可用布局
    print("\n4. 可用的布局类型:")
    layouts = manager.get_available_layouts()
    for layout in layouts:
        print(f"   - {layout}")
    
    print("\n🎉 快速演示完成！")


if __name__ == "__main__":
    try:
        quick_demo()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("💡 请确保在Windows系统上运行此脚本")