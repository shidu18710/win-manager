"""
Unit tests for ConfigManager.
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, mock_open

# Add src to path for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from win_manager.core.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    def test_init_default_config_dir(self):
        """Test ConfigManager initialization with default config directory."""
        with patch('os.path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = '/home/user'
            config = ConfigManager()
            
            assert config.config_dir == Path('/home/user/.win-manager')
            mock_expanduser.assert_called_once_with('~')
    
    def test_init_custom_config_dir(self):
        """Test ConfigManager initialization with custom config directory."""
        custom_dir = '/custom/config'
        config = ConfigManager(config_dir=custom_dir)
        
        assert config.config_dir == Path(custom_dir)
        assert config.config_file == Path(custom_dir) / 'config.json'
    
    def test_default_config_structure(self):
        """Test that default config has required structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Check main sections exist
            assert 'window_management' in config.default_config
            assert 'filters' in config.default_config
            assert 'hotkeys' in config.default_config
            assert 'ui' in config.default_config
            assert 'advanced' in config.default_config
            
            # Check specific values
            assert config.default_config['window_management']['default_layout'] == 'cascade'
            assert config.default_config['filters']['ignore_fixed_size'] == True
            assert config.default_config['hotkeys']['organize_windows'] == 'ctrl+alt+o'
    
    def test_load_config_no_file(self):
        """Test loading config when no config file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Should load default config
            assert config.config == config.default_config
    
    def test_load_config_with_file(self):
        """Test loading config from existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a config file
            config_file = Path(temp_dir) / 'config.json'
            test_config = {
                'window_management': {
                    'default_layout': 'grid'
                },
                'custom_setting': 'test_value'
            }
            
            with open(config_file, 'w') as f:
                json.dump(test_config, f)
            
            config = ConfigManager(config_dir=temp_dir)
            
            # Should merge with defaults
            assert config.config['window_management']['default_layout'] == 'grid'
            assert config.config['custom_setting'] == 'test_value'
            # Should still have defaults for missing keys
            assert config.config['filters']['ignore_fixed_size'] == True
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / 'config.json'
            
            # Create invalid JSON
            with open(config_file, 'w') as f:
                f.write('invalid json content')
            
            config = ConfigManager(config_dir=temp_dir)
            
            # Should fallback to default config
            assert config.config == config.default_config
    
    def test_save_config(self):
        """Test saving config to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Modify config
            config.set('window_management.default_layout', 'stack')
            
            # Save config
            result = config.save_config()
            assert result == True
            
            # Verify file was created and contains correct data
            assert config.config_file.exists()
            with open(config.config_file, 'r') as f:
                saved_config = json.load(f)
            
            assert saved_config['window_management']['default_layout'] == 'stack'
    
    def test_get_config_value(self):
        """Test getting config values using dot notation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Test existing values
            assert config.get('window_management.default_layout') == 'cascade'
            assert config.get('filters.ignore_fixed_size') == True
            
            # Test non-existing values
            assert config.get('non.existing.key') is None
            assert config.get('non.existing.key', 'default') == 'default'
    
    def test_set_config_value(self):
        """Test setting config values using dot notation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Set existing value
            config.set('window_management.default_layout', 'grid')
            assert config.get('window_management.default_layout') == 'grid'
            
            # Set new nested value
            config.set('new.nested.key', 'test_value')
            assert config.get('new.nested.key') == 'test_value'
    
    def test_excluded_processes(self):
        """Test excluded processes management."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Get initial excluded processes
            excluded = config.get_excluded_processes()
            assert 'explorer.exe' in excluded
            
            # Add new process
            config.add_excluded_process('test.exe')
            excluded = config.get_excluded_processes()
            assert 'test.exe' in excluded
            
            # Don't add duplicate
            config.add_excluded_process('test.exe')
            excluded = config.get_excluded_processes()
            assert excluded.count('test.exe') == 1
            
            # Remove process
            config.remove_excluded_process('test.exe')
            excluded = config.get_excluded_processes()
            assert 'test.exe' not in excluded
    
    def test_hotkey_management(self):
        """Test hotkey configuration management."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Get existing hotkey
            hotkey = config.get_hotkey('organize_windows')
            assert hotkey == 'ctrl+alt+o'
            
            # Set new hotkey
            config.set_hotkey('organize_windows', 'ctrl+shift+o')
            hotkey = config.get_hotkey('organize_windows')
            assert hotkey == 'ctrl+shift+o'
            
            # Get non-existing hotkey
            hotkey = config.get_hotkey('non_existing')
            assert hotkey is None
    
    def test_export_config(self):
        """Test exporting config to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Modify config
            config.set('test_key', 'test_value')
            
            # Export to file
            export_file = Path(temp_dir) / 'export.json'
            result = config.export_config(str(export_file))
            assert result == True
            
            # Verify exported file
            assert export_file.exists()
            with open(export_file, 'r') as f:
                exported_config = json.load(f)
            
            assert exported_config['test_key'] == 'test_value'
    
    def test_import_config(self):
        """Test importing config from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Create import file
            import_file = Path(temp_dir) / 'import.json'
            import_config = {
                'window_management': {
                    'default_layout': 'imported_layout'
                },
                'imported_key': 'imported_value'
            }
            
            with open(import_file, 'w') as f:
                json.dump(import_config, f)
            
            # Import config
            result = config.import_config(str(import_file))
            assert result == True
            
            # Verify imported values
            assert config.get('window_management.default_layout') == 'imported_layout'
            assert config.get('imported_key') == 'imported_value'
    
    def test_import_config_invalid_file(self):
        """Test importing config from invalid file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Try to import non-existing file
            result = config.import_config('/non/existing/file.json')
            assert result == False
    
    def test_reset_to_default(self):
        """Test resetting config to default values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            # Modify config
            config.set('window_management.default_layout', 'modified')
            assert config.get('window_management.default_layout') == 'modified'
            
            # Reset to default
            config.reset_to_default()
            assert config.get('window_management.default_layout') == 'cascade'
    
    def test_merge_configs(self):
        """Test config merging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ConfigManager(config_dir=temp_dir)
            
            default = {
                'section1': {
                    'key1': 'default1',
                    'key2': 'default2'
                },
                'section2': {
                    'key3': 'default3'
                }
            }
            
            user = {
                'section1': {
                    'key1': 'user1',
                    'key4': 'user4'
                },
                'section3': {
                    'key5': 'user5'
                }
            }
            
            merged = config._merge_configs(default, user)
            
            # Check merged values
            assert merged['section1']['key1'] == 'user1'  # User override
            assert merged['section1']['key2'] == 'default2'  # Default preserved
            assert merged['section1']['key4'] == 'user4'  # User addition
            assert merged['section2']['key3'] == 'default3'  # Default section preserved
            assert merged['section3']['key5'] == 'user5'  # User section added


if __name__ == '__main__':
    pytest.main([__file__])