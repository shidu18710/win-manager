"""
Output formatting utilities for CLI
"""
import json
import yaml
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from tabulate import tabulate
import sys


class OutputManager:
    """输出管理器"""
    
    def __init__(self, format: str = 'table', verbose: bool = False, quiet: bool = False):
        self.format = format
        self.verbose = verbose
        self.quiet = quiet
        self.console = Console()
    
    def _clean_text(self, text: str) -> str:
        """清理文本中的特殊字符以避免编码问题"""
        if not isinstance(text, str):
            return str(text)
        
        # 移除零宽度字符和其他问题字符
        clean_text = text.replace('\u200b', '')  # 零宽度空格
        clean_text = clean_text.replace('\u200c', '')  # 零宽度不连字符
        clean_text = clean_text.replace('\u200d', '')  # 零宽度连字符
        clean_text = clean_text.replace('\ufeff', '')  # 字节顺序标记
        
        return clean_text
    
    def _clean_data(self, data: Any) -> Any:
        """递归清理数据结构中的文本"""
        if isinstance(data, str):
            return self._clean_text(data)
        elif isinstance(data, dict):
            return {key: self._clean_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_data(item) for item in data]
        else:
            return data
    
    def print(self, data: Any, message: str = "", success: bool = True):
        """打印数据"""
        if self.quiet:
            return
        
        # 清理数据
        data = self._clean_data(data)
        message = self._clean_text(message)
        
        if self.format == 'json':
            self._print_json(data, message, success)
        elif self.format == 'yaml':
            self._print_yaml(data, message, success)
        elif self.format == 'table':
            self._print_table(data, message, success)
        elif self.format == 'text':
            self._print_text(data, message, success)
        else:
            raise ValueError(f"不支持的输出格式: {self.format}")
    
    
    def _print_json(self, data: Any, message: str, success: bool):
        """JSON格式输出"""
        output = {
            "success": success,
            "data": data,
            "message": message
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    def _print_yaml(self, data: Any, message: str, success: bool):
        """YAML格式输出"""
        output = {
            "success": success,
            "data": data,
            "message": message
        }
        print(yaml.dump(output, default_flow_style=False, allow_unicode=True))
    
    def _print_table(self, data: Any, message: str, success: bool):
        """表格格式输出"""
        if message:
            icon = "√" if success else "×"
            self.console.print(f"{icon} {message}")
        
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                self._print_dict_table(data)
            else:
                self._print_list_table(data)
        elif isinstance(data, dict):
            self._print_dict_info(data)
        elif data is not None:
            self.console.print(str(data))
    
    def _print_text(self, data: Any, message: str, success: bool):
        """文本格式输出"""
        if message:
            icon = "√" if success else "×"
            print(f"{icon} {message}")
        
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"• {key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data, 1):
                print(f"{i}. {item}")
        elif data is not None:
            print(str(data))
    
    def _print_dict_table(self, data: List[Dict]):
        """打印字典列表为表格"""
        if not data:
            return
        
        table = Table()
        
        # 添加列
        keys = data[0].keys()
        for key in keys:
            table.add_column(key, style="cyan")
        
        # 添加行
        for item in data:
            row = [str(item.get(key, '')) for key in keys]
            table.add_row(*row)
        
        self.console.print(table)
    
    def _print_list_table(self, data: List):
        """打印列表为表格"""
        table = Table()
        table.add_column("Index", style="cyan")
        table.add_column("Value", style="white")
        
        for i, item in enumerate(data, 1):
            table.add_row(str(i), str(item))
        
        self.console.print(table)
    
    def _print_dict_info(self, data: Dict):
        """打印字典信息"""
        table = Table()
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        self.console.print(table)
    
    def error(self, message: str):
        """输出错误信息"""
        if self.format == 'json':
            error_data = {
                "success": False,
                "error": message,
                "data": None
            }
            print(json.dumps(error_data, ensure_ascii=False, indent=2))
        elif self.format == 'yaml':
            error_data = {
                "success": False,
                "error": message,
                "data": None
            }
            print(yaml.dump(error_data, default_flow_style=False, allow_unicode=True))
        else:
            self.console.print(f"× 错误: {message}", style="red")
    
    def warning(self, message: str):
        """输出警告信息"""
        if not self.quiet:
            if self.format in ['json', 'yaml']:
                # 在结构化输出中，警告通常不单独输出
                pass
            else:
                self.console.print(f"! 警告: {message}", style="yellow")
    
    def info(self, message: str):
        """输出信息"""
        if self.verbose and not self.quiet:
            if self.format in ['json', 'yaml']:
                # 在结构化输出中，信息通常不单独输出
                pass
            else:
                self.console.print(f"i 信息: {message}", style="blue")
    
    def success(self, message: str):
        """输出成功信息"""
        if not self.quiet:
            if self.format in ['json', 'yaml']:
                # 在结构化输出中，成功消息通常包含在主要输出中
                pass
            else:
                self.console.print(f"√ {message}", style="green")
    
    def progress(self, message: str):
        """输出进度信息"""
        if self.verbose and not self.quiet and self.format not in ['json', 'yaml']:
            self.console.print(f"→ {message}", style="cyan")
    
    def print_section(self, title: str, data: Any = None):
        """打印分节信息"""
        if self.quiet:
            return
        
        if self.format in ['json', 'yaml']:
            if data is not None:
                self.print(data, title)
        else:
            panel = Panel(str(data) if data else "", title=title, border_style="blue")
            self.console.print(panel)