"""
Main entry point for Win-Manager.
"""

import sys
import argparse
from .core.window_manager import WindowManager


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Win-Manager - Windows window management tool")
    parser.add_argument("--layout", "-l", choices=["cascade", "grid", "stack"], 
                       help="Layout to apply to windows")
    parser.add_argument("--list", action="store_true", help="List all windows")
    parser.add_argument("--undo", action="store_true", help="Undo last layout change")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    
    args = parser.parse_args()
    
    # Initialize window manager
    wm = WindowManager()
    
    if args.list:
        # List all windows
        windows = wm.get_window_list()
        print(f"Found {len(windows)} windows:")
        for i, window in enumerate(windows, 1):
            print(f"{i:2d}. {window['title'][:50]:<50} ({window['process_name']})")
            if window['is_resizable']:
                print(f"     Resizable: Yes | Minimized: {window['is_minimized']} | Maximized: {window['is_maximized']}")
            else:
                print(f"     Resizable: No  | Fixed size window")
        return
    
    if args.undo:
        # Undo last layout change
        if wm.undo_layout():
            print("Successfully restored windows to previous state")
        else:
            print("No previous state to restore or restore failed")
        return
    
    if args.layout:
        # Apply specified layout
        if wm.organize_windows(args.layout):
            print(f"Successfully applied {args.layout} layout")
        else:
            print(f"Failed to apply {args.layout} layout")
        return
    
    if args.gui:
        # Launch GUI (to be implemented)
        print("GUI mode not yet implemented")
        return
    
    # Default behavior - show manageable windows and ask for action
    manageable_windows = wm.get_manageable_windows()
    
    if not manageable_windows:
        print("No manageable windows found.")
        print("Try running with --list to see all windows.")
        return
    
    print(f"Found {len(manageable_windows)} manageable windows:")
    for i, window in enumerate(manageable_windows, 1):
        print(f"{i:2d}. {window.title[:50]:<50} ({window.process_name})")
    
    print("\nAvailable actions:")
    print("1. Cascade layout")
    print("2. Grid layout") 
    print("3. Stack layout")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            wm.organize_windows("cascade")
            print("Applied cascade layout")
        elif choice == "2":
            wm.organize_windows("grid")
            print("Applied grid layout")
        elif choice == "3":
            wm.organize_windows("stack")
            print("Applied stack layout")
        elif choice == "4":
            print("Goodbye!")
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
