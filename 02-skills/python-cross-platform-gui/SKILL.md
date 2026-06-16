---
name: python-cross-platform-gui
description: Cross-platform Python GUI development with tkinter. Use when building desktop tools that need GUI interfaces on Windows, macOS, and Linux. Covers macOS Tcl/Tk compatibility, CLI fallbacks, path resolution, and launcher scripts.
---

# Cross-Platform Python GUI

---

## Epistemic Standards

This skill operates under shared epistemic principles. When beginning non-trivial
work, load and apply: `shared/epistemic-standards.md`

Core obligations: surface assumptions before acting on them; verify sources are
recent *and* relevant (standards version frequently); name rejected alternatives;
distinguish user framing from evidence; make uncertainty explicit.

---

## Artifact Standards

This skill follows shared artifact naming, versioning, and delivery conventions.
Load when producing or receiving any file: `shared/artifact-standards.md`

Core obligations: name every artifact with context_descriptor_vN.N_YYYY-MM-DD.ext;
never silently overwrite — increment the version; deliver runnable code as a
double-click zip (macOS default, other platforms additive); all outputs must be
immediately usable without a terminal.

---

## macOS Tcl/Tk Compatibility

System Python on macOS uses outdated Tcl/Tk (8.5.9) causing crashes:

```
macOS 26 (2601) or later required, have instead 16 (1601) !
Abort trap: 6
```

### Solutions

**Homebrew Python 3.11+:**
```bash
brew install python@3.11
brew install python-tk@3.11
/opt/homebrew/bin/python3.11 -m tkinter  # Verify
```

**GUI Import Guard:**
```python
def safe_import_tkinter():
    try:
        import tkinter as tk
        return tk
    except ImportError:
        return None

# Only import when GUI explicitly needed
if use_gui:
    tk = safe_import_tkinter()
    if tk is None:
        print("GUI unavailable, using CLI mode")
        use_gui = False
```

## CLI Fallback Pattern

Always provide CLI alternative for macOS compatibility:

```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', action='store_true', help='Force CLI mode')
    args, remaining = parser.parse_known_args()
    
    if args.cli or sys.platform == 'darwin':
        run_cli_mode()
    else:
        try:
            run_gui_mode()
        except Exception:
            run_cli_mode()
```

## Path Resolution

Use `__file__` for script-relative paths, not current working directory:

```python
from pathlib import Path

# Script location
SCRIPT_DIR = Path(__file__).parent.resolve()

# Project root (if script is in subfolder)
PROJECT_ROOT = SCRIPT_DIR.parent

# Config file
CONFIG_PATH = PROJECT_ROOT / 'config.json'

# Output folder
OUTPUT_DIR = PROJECT_ROOT / 'output'
```

## Type Hints Compatibility

Python 3.8/3.9 don't support `str | None` syntax:

```python
# WRONG (requires 3.10+)
def process(name: str | None = None) -> str | None:

# CORRECT (3.8+ compatible)
from typing import Optional
def process(name: Optional[str] = None) -> Optional[str]:
```

## Cross-Platform Launchers

### Windows (SETUP.bat)
```batch
@echo off
cd /d "%~dp0"
python exporter.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Script failed
    pause
    exit /b 1
)
pause
```

### Mac/Linux (SETUP.sh)
```bash
#!/bin/bash
cd "$(dirname "$0")"

# Try multiple Python paths
if [ -f "/opt/homebrew/bin/python3.11" ]; then
    PYTHON="/opt/homebrew/bin/python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    echo "Python not found"
    exit 1
fi

$PYTHON exporter.py --cli
```

Make executable: `chmod +x SETUP.sh`

## Debug vs Production Versions

Provide both:

```python
# Production
logging.basicConfig(level=logging.INFO)

# Debug version
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
```

Or use flag:
```python
DEBUG = '--debug' in sys.argv
log_level = logging.DEBUG if DEBUG else logging.INFO
```
