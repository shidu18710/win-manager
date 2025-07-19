# ⚙️ 配置系统详解

Win-Manager 的配置系统采用分层架构，支持默认配置、用户自定义、运行时修改等多种配置来源，提供灵活且强大的配置管理能力。

## 🎯 设计目标

### 核心特性
1. **分层配置** - 支持默认值、用户配置、运行时配置的分层覆盖
2. **类型安全** - 配置值的类型验证和自动转换
3. **实时更新** - 支持运行时配置修改和立即生效
4. **文件持久化** - 配置的保存和加载
5. **配置验证** - 配置值的合法性检查

### 设计原则
- **优先级明确** - 运行时 > 用户 > 默认配置
- **向后兼容** - 新版本保持对旧配置的兼容
- **错误容忍** - 配置错误不影响系统基本功能

## 🏗️ 架构设计

### 配置层次结构

```
ConfigManager
├── RuntimeConfig (运行时配置)
│   └── 临时修改，内存中存储
├── UserConfig (用户配置)
│   └── ~/.win-manager/config.json
├── DefaultConfig (默认配置)
│   └── 硬编码在代码中
└── SchemaValidator (配置验证)
    └── 类型检查和值验证
```

### 配置查找流程

```python
def get_config_value(key: str) -> any:
    """配置值查找流程"""
    # 1. 检查运行时配置
    if key in runtime_config:
        return runtime_config[key]
    
    # 2. 检查用户配置文件
    if key in user_config:
        return user_config[key]
    
    # 3. 检查默认配置
    if key in default_config:
        return default_config[key]
    
    # 4. 返回None或默认值
    return None
```

## 🔧 核心实现

### ConfigManager 类

```python
import json
import os
import logging
from typing import Any, Dict, Optional, Union
from copy import deepcopy

class ConfigManager:
    """分层配置管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 配置层
        self.default_config = self._load_default_config()
        self.user_config = self._load_user_config()
        self.runtime_config = {}
        
        # 配置验证器
        self.validator = ConfigValidator()
        
    def get(self, key: str, default_value: Any = None) -> Any:
        """获取配置值，支持嵌套键"""
        try:
            # 分层查找
            for config_layer in [self.runtime_config, self.user_config, self.default_config]:
                value = self._get_nested_value(config_layer, key)
                if value is not None:
                    return value
            
            return default_value
            
        except Exception as e:
            self.logger.warning(f"Error getting config key '{key}': {e}")
            return default_value
    
    def set(self, key: str, value: Any, persist: bool = False) -> bool:
        """设置配置值"""
        try:
            # 验证配置值
            validated_value = self.validator.validate(key, value)
            
            # 设置运行时配置
            self._set_nested_value(self.runtime_config, key, validated_value)
            
            # 可选持久化
            if persist:
                self._set_nested_value(self.user_config, key, validated_value)
                return self.save_config()
            
            return True
            
        except ValueError as e:
            self.logger.error(f"Invalid config value for '{key}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error setting config '{key}': {e}")
            return False
    
    def _get_nested_value(self, config: Dict, key: str) -> Any:
        """获取嵌套字典中的值"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, config: Dict, key: str, value: Any) -> None:
        """在嵌套字典中设置值"""
        keys = key.split('.')
        current = config
        
        # 导航到父字典
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # 设置最终值
        current[keys[-1]] = value
```

### 默认配置定义

```python
def _load_default_config(self) -> Dict:
    """加载默认配置"""
    return {
        "window_management": {
            "default_layout": "cascade",
            "save_state": True,
            "auto_restore": True,
            "max_undo_levels": 10,
            "ignore_system_windows": True
        },
        
        "filters": {
            "ignore_minimized": True,
            "ignore_fixed_size": True,
            "min_window_size": [100, 100],
            "excluded_processes": [
                # 系统进程
                "dwm.exe", "explorer.exe", "winlogon.exe",
                "csrss.exe", "smss.exe", "wininit.exe",
                "services.exe", "lsass.exe", "svchost.exe",
                
                # 常见系统工具
                "taskmgr.exe", "dllhost.exe", "rundll32.exe",
                "conhost.exe", "fontdrvhost.exe"
            ],
            "excluded_window_classes": [
                "Shell_TrayWnd", "DV2ControlHost", "MsgrIMEWindowClass",
                "IME", "Default IME", "MSCTFIME UI"
            ]
        },
        
        "layouts": {
            "grid": {
                "default_columns": None,  # 自动计算
                "default_padding": 10,
                "min_window_size": [200, 150],
                "adaptive_columns": True,
                "max_columns": 6
            },
            "cascade": {
                "offset_x": 30,
                "offset_y": 30,
                "window_size_ratio": 0.7,
                "max_cascade_count": 15
            },
            "stack": {
                "default_position": "center",
                "default_size_ratio": 0.8,
                "available_positions": ["center", "left", "right", "top", "bottom"]
            }
        },
        
        "hotkeys": {
            "enabled": True,
            "global_hotkeys": True,
            "bindings": {
                "grid_layout": "ctrl+alt+g",
                "cascade_layout": "ctrl+alt+c",
                "stack_layout": "ctrl+alt+s",
                "undo": "ctrl+alt+u",
                "window_list": "ctrl+alt+l"
            }
        },
        
        "ui": {
            "output_format": "table",
            "available_formats": ["table", "json", "yaml", "text"],
            "show_detailed_info": False,
            "color_output": True,
            "max_title_length": 50
        },
        
        "performance": {
            "cache_window_info": True,
            "cache_timeout_ms": 100,
            "batch_operations": True,
            "max_batch_size": 50,
            "async_operations": False
        },
        
        "advanced": {
            "log_level": "INFO",
            "log_file": None,  # None表示只输出到控制台
            "debug_mode": False,
            "performance_monitoring": False,
            "auto_backup_config": True,
            "backup_count": 5
        }
    }
```

### 配置验证器

```python
from typing import Any, Callable, Dict, List, Union

class ConfigValidator:
    """配置值验证器"""
    
    def __init__(self):
        self.validation_rules = self._build_validation_rules()
    
    def validate(self, key: str, value: Any) -> Any:
        """验证并转换配置值"""
        if key in self.validation_rules:
            validator_func = self.validation_rules[key]
            return validator_func(value)
        
        # 没有特定验证规则，返回原值
        return value
    
    def _build_validation_rules(self) -> Dict[str, Callable]:
        """构建验证规则"""
        return {
            # 窗口管理
            "window_management.default_layout": self._validate_layout_name,
            "window_management.max_undo_levels": self._validate_positive_int,
            
            # 过滤器
            "filters.min_window_size": self._validate_window_size,
            "filters.excluded_processes": self._validate_process_list,
            
            # 布局配置
            "layouts.grid.default_columns": self._validate_columns,
            "layouts.grid.default_padding": self._validate_padding,
            "layouts.cascade.offset_x": self._validate_offset,
            "layouts.cascade.offset_y": self._validate_offset,
            "layouts.cascade.window_size_ratio": self._validate_ratio,
            "layouts.stack.default_position": self._validate_stack_position,
            
            # 热键
            "hotkeys.bindings.*": self._validate_hotkey,
            
            # UI
            "ui.output_format": self._validate_output_format,
            "ui.max_title_length": self._validate_positive_int,
            
            # 性能
            "performance.cache_timeout_ms": self._validate_positive_int,
            "performance.max_batch_size": self._validate_positive_int,
            
            # 高级
            "advanced.log_level": self._validate_log_level,
            "advanced.backup_count": self._validate_positive_int
        }
    
    def _validate_layout_name(self, value: str) -> str:
        """验证布局名称"""
        valid_layouts = ["cascade", "grid", "stack"]
        if value not in valid_layouts:
            raise ValueError(f"Invalid layout name. Must be one of: {valid_layouts}")
        return value
    
    def _validate_positive_int(self, value: Union[int, str]) -> int:
        """验证正整数"""
        try:
            int_value = int(value)
            if int_value <= 0:
                raise ValueError("Value must be positive")
            return int_value
        except (ValueError, TypeError):
            raise ValueError("Value must be a positive integer")
    
    def _validate_window_size(self, value: List) -> List[int]:
        """验证窗口尺寸"""
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("Window size must be a list of two integers [width, height]")
        
        try:
            width, height = int(value[0]), int(value[1])
            if width < 50 or height < 50:
                raise ValueError("Window size must be at least 50x50")
            return [width, height]
        except (ValueError, TypeError):
            raise ValueError("Window size values must be integers")
    
    def _validate_process_list(self, value: List) -> List[str]:
        """验证进程列表"""
        if not isinstance(value, list):
            raise ValueError("Process list must be a list of strings")
        
        validated_list = []
        for process in value:
            if isinstance(process, str) and process.strip():
                validated_list.append(process.strip().lower())
        
        return validated_list
    
    def _validate_columns(self, value: Union[int, None]) -> Union[int, None]:
        """验证网格列数"""
        if value is None:
            return None
        
        try:
            int_value = int(value)
            if int_value < 1 or int_value > 10:
                raise ValueError("Columns must be between 1 and 10")
            return int_value
        except (ValueError, TypeError):
            raise ValueError("Columns must be an integer or None")
    
    def _validate_padding(self, value: Union[int, str]) -> int:
        """验证间距"""
        try:
            int_value = int(value)
            if int_value < 0 or int_value > 100:
                raise ValueError("Padding must be between 0 and 100")
            return int_value
        except (ValueError, TypeError):
            raise ValueError("Padding must be an integer")
    
    def _validate_offset(self, value: Union[int, str]) -> int:
        """验证偏移量"""
        try:
            int_value = int(value)
            if int_value < 0 or int_value > 200:
                raise ValueError("Offset must be between 0 and 200")
            return int_value
        except (ValueError, TypeError):
            raise ValueError("Offset must be an integer")
    
    def _validate_ratio(self, value: Union[float, str]) -> float:
        """验证比例值"""
        try:
            float_value = float(value)
            if float_value < 0.1 or float_value > 1.0:
                raise ValueError("Ratio must be between 0.1 and 1.0")
            return float_value
        except (ValueError, TypeError):
            raise ValueError("Ratio must be a float")
    
    def _validate_stack_position(self, value: str) -> str:
        """验证堆叠位置"""
        valid_positions = ["center", "left", "right", "top", "bottom"]
        if value not in valid_positions:
            raise ValueError(f"Stack position must be one of: {valid_positions}")
        return value
    
    def _validate_hotkey(self, value: str) -> str:
        """验证热键格式"""
        import re
        
        # 简单的热键格式验证
        hotkey_pattern = r'^(ctrl|alt|shift|win)(\+(ctrl|alt|shift|win|[a-z0-9]))*$'
        if not re.match(hotkey_pattern, value.lower()):
            raise ValueError("Invalid hotkey format")
        return value.lower()
    
    def _validate_output_format(self, value: str) -> str:
        """验证输出格式"""
        valid_formats = ["table", "json", "yaml", "text"]
        if value not in valid_formats:
            raise ValueError(f"Output format must be one of: {valid_formats}")
        return value
    
    def _validate_log_level(self, value: str) -> str:
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return value.upper()
```

## 📁 配置文件管理

### 配置文件位置

```python
def _get_config_directory(self) -> str:
    """获取配置目录"""
    if os.name == 'nt':  # Windows
        # 使用APPDATA环境变量
        appdata = os.environ.get('APPDATA')
        if appdata:
            config_dir = os.path.join(appdata, 'WinManager')
        else:
            config_dir = os.path.join(os.environ.get('USERPROFILE', ''), '.win-manager')
    else:
        # Unix-like系统
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'win-manager')
    
    # 确保目录存在
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def _get_config_path(self) -> str:
    """获取主配置文件路径"""
    return os.path.join(self._get_config_directory(), 'config.json')

def _get_backup_path(self, backup_index: int = 0) -> str:
    """获取备份配置文件路径"""
    backup_name = f"config.backup.{backup_index}.json"
    return os.path.join(self._get_config_directory(), backup_name)
```

### 配置保存和加载

```python
def save_config(self) -> bool:
    """保存配置到文件"""
    try:
        config_path = self._get_config_path()
        
        # 创建备份
        if self.get("advanced.auto_backup_config", True):
            self._create_config_backup()
        
        # 合并配置
        merged_config = self._merge_configs()
        
        # 保存到文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, indent=2, ensure_ascii=False, sort_keys=True)
        
        # 更新用户配置
        self.user_config = merged_config
        self.runtime_config = {}
        
        self.logger.info(f"Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to save configuration: {e}")
        return False

def _load_user_config(self) -> Dict:
    """从文件加载用户配置"""
    config_path = self._get_config_path()
    
    if not os.path.exists(config_path):
        self.logger.info("No user configuration file found, using defaults")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
        
        # 验证配置
        validated_config = self._validate_config(user_config)
        
        self.logger.info(f"User configuration loaded from {config_path}")
        return validated_config
        
    except json.JSONDecodeError as e:
        self.logger.error(f"Invalid JSON in config file: {e}")
        return self._load_backup_config()
    except Exception as e:
        self.logger.error(f"Failed to load user config: {e}")
        return {}

def _load_backup_config(self) -> Dict:
    """从备份文件加载配置"""
    backup_count = self.get("advanced.backup_count", 5)
    
    for i in range(backup_count):
        backup_path = self._get_backup_path(i)
        
        if os.path.exists(backup_path):
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_config = json.load(f)
                
                self.logger.info(f"Loaded configuration from backup: {backup_path}")
                return backup_config
                
            except Exception as e:
                self.logger.warning(f"Failed to load backup {backup_path}: {e}")
                continue
    
    self.logger.warning("No valid backup configuration found")
    return {}
```

### 配置备份系统

```python
def _create_config_backup(self) -> None:
    """创建配置备份"""
    try:
        config_path = self._get_config_path()
        
        if not os.path.exists(config_path):
            return
        
        backup_count = self.get("advanced.backup_count", 5)
        
        # 滚动备份 - 从最老的开始
        for i in range(backup_count - 1, 0, -1):
            old_backup = self._get_backup_path(i - 1)
            new_backup = self._get_backup_path(i)
            
            if os.path.exists(old_backup):
                if os.path.exists(new_backup):
                    os.remove(new_backup)
                os.rename(old_backup, new_backup)
        
        # 创建新备份
        newest_backup = self._get_backup_path(0)
        if os.path.exists(newest_backup):
            os.remove(newest_backup)
        
        import shutil
        shutil.copy2(config_path, newest_backup)
        
        self.logger.debug(f"Configuration backup created: {newest_backup}")
        
    except Exception as e:
        self.logger.warning(f"Failed to create config backup: {e}")

def _merge_configs(self) -> Dict:
    """合并所有配置层"""
    merged = deepcopy(self.default_config)
    
    # 深度合并用户配置
    self._deep_merge(merged, self.user_config)
    
    # 深度合并运行时配置
    self._deep_merge(merged, self.runtime_config)
    
    return merged

def _deep_merge(self, target: Dict, source: Dict) -> None:
    """深度合并字典"""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            self._deep_merge(target[key], value)
        else:
            target[key] = value
```

## 🔍 配置模式和验证

### 配置模式定义

```python
from typing import Dict, Any
import jsonschema

class ConfigSchema:
    """配置模式定义"""
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """获取JSON Schema配置模式"""
        return {
            "type": "object",
            "properties": {
                "window_management": {
                    "type": "object",
                    "properties": {
                        "default_layout": {
                            "type": "string",
                            "enum": ["cascade", "grid", "stack"]
                        },
                        "save_state": {"type": "boolean"},
                        "auto_restore": {"type": "boolean"},
                        "max_undo_levels": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 50
                        }
                    }
                },
                "filters": {
                    "type": "object",
                    "properties": {
                        "ignore_minimized": {"type": "boolean"},
                        "ignore_fixed_size": {"type": "boolean"},
                        "min_window_size": {
                            "type": "array",
                            "items": {"type": "integer", "minimum": 50},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "excluded_processes": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "layouts": {
                    "type": "object",
                    "properties": {
                        "grid": {
                            "type": "object",
                            "properties": {
                                "default_columns": {
                                    "oneOf": [
                                        {"type": "null"},
                                        {"type": "integer", "minimum": 1, "maximum": 10}
                                    ]
                                },
                                "default_padding": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 100
                                }
                            }
                        },
                        "cascade": {
                            "type": "object",
                            "properties": {
                                "offset_x": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 200
                                },
                                "offset_y": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 200
                                },
                                "window_size_ratio": {
                                    "type": "number",
                                    "minimum": 0.1,
                                    "maximum": 1.0
                                }
                            }
                        }
                    }
                }
            }
        }

def _validate_config(self, config: Dict) -> Dict:
    """使用JSON Schema验证配置"""
    try:
        schema = ConfigSchema.get_schema()
        jsonschema.validate(config, schema)
        return config
    except jsonschema.ValidationError as e:
        self.logger.warning(f"Configuration validation failed: {e.message}")
        # 返回部分有效的配置
        return self._sanitize_config(config)
    except Exception as e:
        self.logger.error(f"Unexpected error during config validation: {e}")
        return {}

def _sanitize_config(self, config: Dict) -> Dict:
    """清理无效的配置项"""
    sanitized = {}
    
    for key, value in config.items():
        try:
            if isinstance(value, dict):
                sanitized_child = self._sanitize_config(value)
                if sanitized_child:
                    sanitized[key] = sanitized_child
            else:
                # 简单值验证
                validated_value = self.validator.validate(key, value)
                sanitized[key] = validated_value
        except Exception as e:
            self.logger.warning(f"Skipping invalid config item '{key}': {e}")
            continue
    
    return sanitized
```

## 🔧 高级配置功能

### 配置迁移

```python
class ConfigMigrator:
    """配置迁移器 - 处理版本升级时的配置兼容性"""
    
    def __init__(self):
        self.migration_rules = {
            "1.0.0": self._migrate_from_1_0_0,
            "1.1.0": self._migrate_from_1_1_0,
            "2.0.0": self._migrate_from_2_0_0
        }
    
    def migrate_config(self, config: Dict, from_version: str, to_version: str) -> Dict:
        """迁移配置"""
        current_config = deepcopy(config)
        
        # 找到迁移路径
        migration_path = self._get_migration_path(from_version, to_version)
        
        for version in migration_path:
            if version in self.migration_rules:
                current_config = self.migration_rules[version](current_config)
        
        return current_config
    
    def _migrate_from_1_0_0(self, config: Dict) -> Dict:
        """从1.0.0版本迁移"""
        # 示例：重命名配置键
        if "window_filter" in config:
            config["filters"] = config.pop("window_filter")
        
        # 示例：添加新的默认值
        if "layouts" not in config:
            config["layouts"] = {}
        
        return config
    
    def _get_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """获取迁移路径"""
        # 简化实现，实际应该基于语义版本号
        return [to_version]
```

### 配置预设

```python
class ConfigPresets:
    """配置预设管理"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.presets = self._load_builtin_presets()
    
    def _load_builtin_presets(self) -> Dict[str, Dict]:
        """加载内置预设"""
        return {
            "developer": {
                "description": "开发者模式 - 针对编程工作优化",
                "config": {
                    "window_management.default_layout": "grid",
                    "layouts.grid.default_columns": 2,
                    "layouts.grid.default_padding": 15,
                    "filters.excluded_processes": ["chrome.exe", "code.exe", "cmd.exe"],
                    "hotkeys.enabled": True
                }
            },
            
            "office": {
                "description": "办公模式 - 适合文档处理",
                "config": {
                    "window_management.default_layout": "cascade",
                    "layouts.cascade.offset_x": 40,
                    "layouts.cascade.offset_y": 40,
                    "layouts.cascade.window_size_ratio": 0.8
                }
            },
            
            "gaming": {
                "description": "游戏模式 - 最小干扰",
                "config": {
                    "window_management.default_layout": "stack",
                    "layouts.stack.default_position": "center",
                    "hotkeys.enabled": False,
                    "filters.ignore_minimized": False
                }
            },
            
            "presentation": {
                "description": "演示模式 - 适合屏幕分享",
                "config": {
                    "window_management.default_layout": "stack",
                    "layouts.stack.default_position": "center",
                    "layouts.stack.default_size_ratio": 0.9,
                    "ui.show_detailed_info": False
                }
            }
        }
    
    def apply_preset(self, preset_name: str) -> bool:
        """应用预设"""
        if preset_name not in self.presets:
            return False
        
        preset_config = self.presets[preset_name]["config"]
        
        try:
            for key, value in preset_config.items():
                self.config_manager.set(key, value)
            return True
        except Exception:
            return False
    
    def get_available_presets(self) -> Dict[str, str]:
        """获取可用预设"""
        return {
            name: preset["description"] 
            for name, preset in self.presets.items()
        }
    
    def create_custom_preset(self, name: str, description: str, config: Dict) -> bool:
        """创建自定义预设"""
        try:
            self.presets[name] = {
                "description": description,
                "config": config,
                "custom": True
            }
            return True
        except Exception:
            return False
```

### 配置监控和回调

```python
from typing import Callable, List

class ConfigWatcher:
    """配置变更监控器"""
    
    def __init__(self):
        self.callbacks: Dict[str, List[Callable]] = {}
    
    def watch(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """监视配置键的变更"""
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
    
    def notify_change(self, key: str, old_value: Any, new_value: Any) -> None:
        """通知配置变更"""
        # 精确匹配
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    logging.getLogger(__name__).error(f"Config callback error: {e}")
        
        # 通配符匹配
        for pattern, callback_list in self.callbacks.items():
            if "*" in pattern and self._match_pattern(pattern, key):
                for callback in callback_list:
                    try:
                        callback(key, old_value, new_value)
                    except Exception as e:
                        logging.getLogger(__name__).error(f"Config callback error: {e}")
    
    def _match_pattern(self, pattern: str, key: str) -> bool:
        """简单的通配符匹配"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

# 集成到ConfigManager中
class EnhancedConfigManager(ConfigManager):
    """增强的配置管理器，支持变更监控"""
    
    def __init__(self):
        super().__init__()
        self.watcher = ConfigWatcher()
    
    def set(self, key: str, value: Any, persist: bool = False) -> bool:
        """设置配置值，并触发变更通知"""
        old_value = self.get(key)
        
        success = super().set(key, value, persist)
        
        if success and old_value != value:
            self.watcher.notify_change(key, old_value, value)
        
        return success
    
    def watch_config(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """监视配置变更"""
        self.watcher.watch(key, callback)

# 使用示例
def on_layout_changed(key: str, old_value: Any, new_value: Any):
    print(f"Layout changed from {old_value} to {new_value}")

config_manager = EnhancedConfigManager()
config_manager.watch_config("window_management.default_layout", on_layout_changed)
```

## 📊 配置统计和诊断

### 配置使用统计

```python
class ConfigStats:
    """配置使用统计"""
    
    def __init__(self):
        self.access_count = {}
        self.modification_count = {}
        self.last_access = {}
    
    def record_access(self, key: str) -> None:
        """记录配置访问"""
        self.access_count[key] = self.access_count.get(key, 0) + 1
        self.last_access[key] = time.time()
    
    def record_modification(self, key: str) -> None:
        """记录配置修改"""
        self.modification_count[key] = self.modification_count.get(key, 0) + 1
    
    def get_most_accessed_configs(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取最常访问的配置"""
        return sorted(
            self.access_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
    
    def get_stats_report(self) -> Dict:
        """生成统计报告"""
        return {
            "total_configs_accessed": len(self.access_count),
            "total_accesses": sum(self.access_count.values()),
            "total_modifications": sum(self.modification_count.values()),
            "most_accessed": self.get_most_accessed_configs(5)
        }
```

## 🛠️ 配置工具和CLI

### 配置命令行工具

```python
import click

@click.group()
def config():
    """配置管理命令"""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str):
    """设置配置值"""
    config_manager = ConfigManager()
    
    # 尝试解析值的类型
    parsed_value = _parse_config_value(value)
    
    if config_manager.set(key, parsed_value, persist=True):
        click.echo(f"✓ 设置 {key} = {parsed_value}")
    else:
        click.echo(f"✗ 设置失败", err=True)

@config.command()
@click.argument('key')
def get_config(key: str):
    """获取配置值"""
    config_manager = ConfigManager()
    value = config_manager.get(key)
    
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"配置键 '{key}' 不存在", err=True)

@config.command()
def show_config():
    """显示所有配置"""
    config_manager = ConfigManager()
    merged_config = config_manager._merge_configs()
    
    import json
    click.echo(json.dumps(merged_config, indent=2, ensure_ascii=False))

def _parse_config_value(value: str) -> Any:
    """解析配置值的类型"""
    # 布尔值
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # 数字
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    # JSON数组或对象
    if value.startswith(('[', '{')):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    
    # 字符串
    return value
```

---

**📚 相关文档：**
- [架构设计](architecture.md) - 系统架构概览
- [核心模块](core-modules.md) - 核心组件详解
- [API参考](api-reference.md) - 完整API文档
- [CLI参考](../user/cli-reference.md) - 命令行接口