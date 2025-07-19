"""
Global hotkey management for Win-Manager.
"""

import threading
import logging
from typing import Dict, Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Listener


class HotkeyManager:
    """Manages global hotkeys for the application."""
    
    def __init__(self):
        self.hotkeys: Dict[str, Callable] = {}
        self.listener: Optional[Listener] = None
        self.pressed_keys = set()
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """Register a global hotkey."""
        try:
            # Parse hotkey string (e.g., "ctrl+alt+o")
            parsed_hotkey = self._parse_hotkey(hotkey)
            if parsed_hotkey:
                self.hotkeys[parsed_hotkey] = callback
                self.logger.info(f"Registered hotkey: {hotkey}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to register hotkey {hotkey}: {e}")
            return False
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """Unregister a global hotkey."""
        try:
            parsed_hotkey = self._parse_hotkey(hotkey)
            if parsed_hotkey and parsed_hotkey in self.hotkeys:
                del self.hotkeys[parsed_hotkey]
                self.logger.info(f"Unregistered hotkey: {hotkey}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to unregister hotkey {hotkey}: {e}")
            return False
    
    def start(self) -> bool:
        """Start the hotkey listener."""
        if self.running:
            return True
        
        try:
            self.listener = Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.running = True
            self.logger.info("Hotkey manager started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start hotkey manager: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the hotkey listener."""
        if not self.running:
            return True
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            self.running = False
            self.pressed_keys.clear()
            self.logger.info("Hotkey manager stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop hotkey manager: {e}")
            return False
    
    def _parse_hotkey(self, hotkey: str) -> Optional[str]:
        """Parse hotkey string into a normalized format."""
        try:
            # Convert to lowercase and split
            parts = [part.strip().lower() for part in hotkey.split('+')]
            
            # Normalize key names
            normalized_parts = []
            for part in parts:
                if part in ['ctrl', 'control']:
                    normalized_parts.append('ctrl')
                elif part in ['alt', 'option']:
                    normalized_parts.append('alt')
                elif part in ['shift']:
                    normalized_parts.append('shift')
                elif part in ['win', 'windows', 'cmd', 'super']:
                    normalized_parts.append('win')
                else:
                    normalized_parts.append(part)
            
            # Sort to ensure consistent order
            normalized_parts.sort()
            return '+'.join(normalized_parts)
        except Exception:
            return None
    
    def _on_press(self, key):
        """Handle key press events."""
        try:
            # Convert key to string
            key_str = self._key_to_string(key)
            if key_str:
                self.pressed_keys.add(key_str)
                
                # Check if current combination matches any registered hotkey
                current_combo = '+'.join(sorted(self.pressed_keys))
                if current_combo in self.hotkeys:
                    # Execute callback in separate thread to avoid blocking
                    threading.Thread(
                        target=self.hotkeys[current_combo],
                        daemon=True
                    ).start()
                    
        except Exception as e:
            self.logger.error(f"Error in key press handler: {e}")
    
    def _on_release(self, key):
        """Handle key release events."""
        try:
            key_str = self._key_to_string(key)
            if key_str and key_str in self.pressed_keys:
                self.pressed_keys.remove(key_str)
        except Exception as e:
            self.logger.error(f"Error in key release handler: {e}")
    
    def _key_to_string(self, key) -> Optional[str]:
        """Convert key object to string representation."""
        try:
            if isinstance(key, KeyCode):
                if key.char:
                    return key.char.lower()
                else:
                    return f"key_{key.vk}"
            elif isinstance(key, Key):
                key_name = key.name.lower()
                # Map special keys
                key_mapping = {
                    'ctrl_l': 'ctrl',
                    'ctrl_r': 'ctrl',
                    'alt_l': 'alt',
                    'alt_r': 'alt',
                    'shift_l': 'shift',
                    'shift_r': 'shift',
                    'cmd': 'win',
                    'cmd_l': 'win',
                    'cmd_r': 'win'
                }
                return key_mapping.get(key_name, key_name)
            return None
        except Exception:
            return None
    
    def get_registered_hotkeys(self) -> list:
        """Get list of registered hotkeys."""
        return list(self.hotkeys.keys())
    
    def is_running(self) -> bool:
        """Check if the hotkey manager is running."""
        return self.running