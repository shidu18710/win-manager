# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Win-Manager is a powerful Windows window management tool written in Python that provides both CLI and programmatic interfaces for organizing windows on the desktop. The project uses a layered architecture with core functionality separated from CLI implementation.

## Development Commands

### Setup & Installation
```bash
# Install dependencies (recommended)
uv sync

# Alternative installation
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/test_window_manager.py -v

# Run with coverage report
uv run python -m pytest tests/ --cov=src/win_manager --cov-report=html

# Run performance tests
uv run python -m pytest tests/test_performance.py -v -s
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Running the Application
```bash
# CLI mode
win-manager --help
win-manager grid
win-manager layout apply cascade --target chrome.exe
win-manager stack --window-width 800 --window-height 600
win-manager stack --window-width 60% --window-height 75%

# Direct Python execution
python src/win_manager/main.py --layout grid
python quick_demo.py
python demo_usage.py
```

## Architecture

### Core Components (`src/win_manager/core/`)
- **WindowManager**: Main orchestrator that coordinates all components
- **WindowDetector**: Discovers and enumerates windows using Windows API
- **WindowController**: Controls window positions, sizes, and states  
- **LayoutEngine**: Calculates window arrangements (cascade, grid, stack)
- **ConfigManager**: Handles configuration files and settings

### CLI Implementation (`src/win_manager/cli/`)
- **main.py**: Click-based CLI entry point with command groups
- **commands/**: Individual command implementations (layout, window, config, hotkey, tool)
- **utils/**: CLI utilities for output formatting and validation
- **config/**: CLI-specific configuration management

### Key Dependencies
- **pywin32**: Windows API access for window management
- **pyautogui**: Window manipulation utilities
- **click**: CLI framework
- **rich**: Terminal output formatting
- **psutil**: Process information
- **pynput**: Hotkey support

## Key Design Patterns

### Dual Entry Points
The project supports both:
1. Simple programmatic interface via `src/win_manager/main.py`
2. Full CLI interface via `src/win_manager/cli/main.py` (entry point: `win-manager` command)

### Configuration System
- Uses layered configuration with defaults and user overrides
- Supports YAML configuration files
- Process exclusion lists for filtering windows
- Layout-specific parameters (grid columns, cascade offsets, etc.)

### Window Filtering
Windows are filtered based on:
- Process exclusion lists (system processes like explorer.exe, dwm.exe)
- Size constraints (minimum 100px width/height)
- Window state (minimized, resizable)
- Window types (system windows, UI elements)

### Layout Types
- **Cascade**: Staggered window arrangement with configurable offsets
- **Grid**: Uniform grid distribution with configurable columns and padding
- **Stack**: Overlapping windows at specified position (center, left, right) with optional custom window sizes (pixels or percentages)

## Testing Strategy

The project has comprehensive test coverage including:
- Unit tests for all core components
- Integration tests for window management workflows
- Performance tests with benchmarks (500+ windows in <0.01s)
- CLI command testing
- Exception handling validation

## Important Notes

- Windows-specific implementation using win32 APIs
- Requires appropriate permissions for window manipulation
- Performance optimized for handling hundreds of windows
- Supports undo functionality by storing window states
- CLI provides both full commands and shortcut aliases (e.g., `grid`, `ls`, `undo`)
- Rich output formatting with multiple format options (JSON, YAML, table, text)
- Window size customization for stack layout with `--window-width` and `--window-height` options supporting both pixel values (e.g., 800) and percentages (e.g., 50%)