"""Windows DWM acrylic / mica effect helper via ctypes."""

from __future__ import annotations

import ctypes
from ctypes import Structure, byref, c_int, c_uint, c_void_p, sizeof, windll
from ctypes.wintypes import DWORD, HWND

# DWM attributes
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_SYSTEMBACKDROP_TYPE = 38

DWMSBT_AUTO = 0
DWMSBT_MAINWINDOW = 2
DWMSBT_TRANSIENTWINDOW = 3
DWMSBT_TABBEDWINDOW = 4

# SetWindowCompositionAttribute accent states
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
WCA_ACCENT_POLICY = 19


class ACCENTPOLICY(Structure):
    _fields_ = [
        ("AccentState", c_int),
        ("AccentFlags", c_int),
        ("GradientColor", c_uint),
        ("AnimationId", c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute", c_int),
        ("Data", c_void_p),
        ("SizeOfData", c_int),
    ]


def get_hwnd(qwindow) -> int:
    """Extract native HWND from a QWindow or QWidget."""
    try:
        return int(qwindow.winId())
    except (AttributeError, TypeError):
        return 0


def apply_acrylic(hwnd: int, dark: bool = True) -> bool:
    """
    Apply native Windows acrylic/mica blur to a window handle.
    Returns True on success, False if all methods fail.
    """
    if not hwnd:
        return False

    success = False
    if _apply_dwm_backdrop(hwnd, dark):
        success = True
    elif _apply_composition_acrylic(hwnd, dark):
        success = True

    if success:
        _ensure_interactive_window(hwnd)

    return success


def _apply_dwm_backdrop(hwnd: int, dark: bool) -> bool:
    """Try DwmSetWindowAttribute with system backdrop types."""
    try:
        dwm = windll.dwmapi
    except OSError:
        return False

    try:
        if dark:
            dark_val = c_int(1)
            dwm.DwmSetWindowAttribute(
                HWND(hwnd),
                DWORD(DWMWA_USE_IMMERSIVE_DARK_MODE),
                byref(dark_val),
                DWORD(sizeof(dark_val)),
            )

        for backdrop in (DWMSBT_TRANSIENTWINDOW, DWMSBT_MAINWINDOW, DWMSBT_TABBEDWINDOW):
            backdrop_val = c_int(backdrop)
            hr = dwm.DwmSetWindowAttribute(
                HWND(hwnd),
                DWORD(DWMWA_SYSTEMBACKDROP_TYPE),
                byref(backdrop_val),
                DWORD(sizeof(backdrop_val)),
            )
            if hr == 0:
                return True
    except OSError:
        pass
    return False


def _apply_composition_acrylic(hwnd: int, dark: bool) -> bool:
    """Fallback using SetWindowCompositionAttribute."""
    try:
        user32 = windll.user32
        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        SetWindowCompositionAttribute.argtypes = [HWND, c_void_p]
        SetWindowCompositionAttribute.restype = c_int
    except (OSError, AttributeError):
        return False

    # ABGR: 0xAABBGGRR — semi-transparent dark blue tint for "dark" mode
    # Use RGB(20,25,60) with alpha 0xBB -> ABGR = 0xBB 3C 19 14 => 0xBB3C1914
    if dark:
        gradient_color = 0xBB3C1914
    else:
        gradient_color = 0xBBF0F0F0

    accent = ACCENTPOLICY()
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.AccentFlags = 2
    accent.GradientColor = gradient_color
    accent.AnimationId = 0

    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = ctypes.cast(byref(accent), c_void_p)
    data.SizeOfData = sizeof(accent)

    try:
        ok = bool(SetWindowCompositionAttribute(HWND(hwnd), byref(data)))
    except OSError:
        return False

    return ok


def _ensure_interactive_window(hwnd: int) -> None:
    """Ensure the window is not marked transparent for input at the extended style level."""
    try:
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x20
        user32 = windll.user32
        try:
            GetWindowLongPtr = user32.GetWindowLongPtrW
            SetWindowLongPtr = user32.SetWindowLongPtrW
            GetWindowLongPtr.argtypes = [HWND, c_int]
            GetWindowLongPtr.restype = ctypes.c_ssize_t
            SetWindowLongPtr.argtypes = [HWND, c_int, ctypes.c_ssize_t]
            SetWindowLongPtr.restype = ctypes.c_ssize_t
        except AttributeError:
            GetWindowLongPtr = user32.GetWindowLongW
            SetWindowLongPtr = user32.SetWindowLongW
            GetWindowLongPtr.argtypes = [HWND, c_int]
            GetWindowLongPtr.restype = c_int
            SetWindowLongPtr.argtypes = [HWND, c_int, c_int]
            SetWindowLongPtr.restype = c_int

        current = GetWindowLongPtr(HWND(hwnd), GWL_EXSTYLE)
        if current & WS_EX_TRANSPARENT:
            new = current & ~WS_EX_TRANSPARENT
            SetWindowLongPtr(HWND(hwnd), GWL_EXSTYLE, new)
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            SetWindowPos = user32.SetWindowPos
            SetWindowPos.argtypes = [HWND, HWND, c_int, c_int, c_int, c_int, c_uint]
            SetWindowPos.restype = c_int
            SetWindowPos(HWND(hwnd), HWND(0), 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED)
    except Exception:
        pass
