"""
CLI Configuration Manager
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class CLIConfig:
    """CLI配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        home_dir = Path.home()
        config_dir = home_dir / '.win-manager'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'cli-config.yaml')
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'default': {
                'output_format': 'table',
                'verbose': False,
            },
            'layout': {
                'default_type': 'grid',
                'grid_columns': 2,
                'grid_padding': 10,
                'cascade_offset_x': 30,
                'cascade_offset_y': 30,
                'stack_position': 'center',
            },
            'hotkeys': {
                'enable_on_start': True,
            },
            'filters': {
                'exclude_processes': ['explorer.exe', 'dwm.exe'],
                'include_minimized': False,
            },
            'output': {
                'show_colors': True,
                'show_icons': True,
                'table_style': 'grid',
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f) or {}
                    # 合并默认配置和加载的配置
                    return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.config_path}: {e}")
                return default_config
        else:
            # 创建默认配置文件
            self._save_config(default_config)
            return default_config
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"警告: 无法保存配置文件: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点号表示法）"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值（支持点号表示法）"""
        keys = key.split('.')
        config = self.config
        
        # 导航到正确的位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def save(self):
        """保存当前配置"""
        self._save_config(self.config)
    
    def reset(self):
        """重置配置为默认值"""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        self.config = self._load_config()
    
    def export(self, path: str, format: str = 'yaml'):
        """导出配置"""
        if format.lower() == 'yaml':
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        elif format.lower() == 'json':
            import json
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def import_config(self, path: str):
        """导入配置"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"配置文件不存在: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.yaml') or path.endswith('.yml'):
                imported_config = yaml.safe_load(f)
            elif path.endswith('.json'):
                import json
                imported_config = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {path}")
        
        self.config = self._merge_configs(self.config, imported_config)
        self.save()