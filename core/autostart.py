"""Windows startup registry entry management."""

from __future__ import annotations

import sys
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GlassNotes"


def _open_run_key(access: int = winreg.KEY_READ):
    return winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, access)


def is_enabled() -> bool:
    """Return True if GlassNotes is registered to run at login."""
    try:
        with _open_run_key() as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def enable(exe_path: str) -> bool:
    """Register GlassNotes to run at Windows startup."""
    try:
        with _open_run_key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
        return True
    except OSError:
        return False


def disable() -> bool:
    """Remove GlassNotes from Windows startup."""
    try:
        with _open_run_key(winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        return True
    except FileNotFoundError:
        return True
    except OSError:
        return False


def get_executable_path() -> str:
    """Return the path used for autostart registration."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return sys.executable
