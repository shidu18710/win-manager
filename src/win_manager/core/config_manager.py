"""
Configuration management system.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Default to user's AppData directory
            config_dir = os.path.join(os.path.expanduser("~"), ".win-manager")
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_config = {
            "window_management": {
                "default_layout": "cascade",
                "cascade_offset_x": 30,
                "cascade_offset_y": 30,
                "grid_columns": None,
                "grid_padding": 10,
                "stack_position": "center"
            },
            "filters": {
                "ignore_fixed_size": True,
                "ignore_minimized": True,
                "ignore_system_windows": True,
                "excluded_processes": [
                    "explorer.exe",
                    "winlogon.exe",
                    "csrss.exe",
                    "dwm.exe"
                ]
            },
            "hotkeys": {
                "organize_windows": "ctrl+alt+o",
                "cascade_layout": "ctrl+alt+c",
                "grid_layout": "ctrl+alt+g",
                "stack_layout": "ctrl+alt+s",
                "undo_layout": "ctrl+alt+u"
            },
            "ui": {
                "show_system_tray": True,
                "start_minimized": False,
                "confirm_actions": True,
                "show_notifications": True
            },
            "advanced": {
                "save_window_states": True,
                "restore_on_startup": False,
                "check_updates": True,
                "log_level": "INFO"
            }
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        import copy
        
        if not self.config_file.exists():
            return copy.deepcopy(self.default_config)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Merge with default config to ensure all keys exist
            merged_config = self._merge_configs(self.default_config, config)
            return merged_config
        except (json.JSONDecodeError, IOError):
            return copy.deepcopy(self.default_config)
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with default config."""
        import copy
        merged = copy.deepcopy(default)
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        import copy
        self.config = copy.deepcopy(self.default_config)
    
    def get_excluded_processes(self) -> list:
        """Get list of excluded processes."""
        return self.get("filters.excluded_processes", [])
    
    def add_excluded_process(self, process_name: str) -> None:
        """Add process to exclusion list."""
        excluded = self.get_excluded_processes()
        if process_name not in excluded:
            excluded.append(process_name)
            self.set("filters.excluded_processes", excluded)
    
    def remove_excluded_process(self, process_name: str) -> None:
        """Remove process from exclusion list."""
        excluded = self.get_excluded_processes()
        if process_name in excluded:
            excluded.remove(process_name)
            self.set("filters.excluded_processes", excluded)
    
    def get_hotkey(self, action: str) -> Optional[str]:
        """Get hotkey for action."""
        return self.get(f"hotkeys.{action}")
    
    def set_hotkey(self, action: str, hotkey: str) -> None:
        """Set hotkey for action."""
        self.set(f"hotkeys.{action}", hotkey)
    
    def export_config(self, file_path: str) -> bool:
        """Export configuration to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Import configuration from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.config = self._merge_configs(self.default_config, config)
            return True
        except (json.JSONDecodeError, IOError):
            return False