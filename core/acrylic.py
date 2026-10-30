"""Windows DWM acrylic / mica effect helper via ctypes."""

from __future__ import annotations

import ctypes
from ctypes import Structure, byref, c_int, c_uint, c_void_p, sizeof, windll
from ctypes.wintypes import DWORD, HWND

# DWM attributes
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_SYSTEMBACKDROP_TYPE = 38

DWMSBT_AUTO = 0
DWMSBT_MAINWINDOW = 2        # Mica
DWMSBT_TRANSIENTWINDOW = 3   # Acrylic
DWMSBT_TABBEDWINDOW = 4      # Tabbed Mica

# SetWindowCompositionAttribute accent states
ACCENT_DISABLED = 0
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
ACCENT_ENABLE_HOSTBACKDROP = 5  # Windows 11 host backdrop
WCA_ACCENT_POLICY = 19


class MARGINS(Structure):
    _fields_ = [
        ("cxLeftWidth", c_int),
        ("cxRightWidth", c_int),
        ("cyTopHeight", c_int),
        ("cyBottomHeight", c_int),
    ]


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

    # Step 1: Set dark mode if requested
    if dark:
        _set_dark_mode(hwnd)

    # Step 2: Try SetWindowCompositionAttribute acrylic (Win10 1803+, Win11)
    # This provides the most reliable frosted glass without requiring frame extension
    success = _apply_composition_acrylic(hwnd, dark)

    # Step 3: Try DWM system backdrop (Windows 11 22H2+)
    if not success:
        # Extend frame into client area ONLY for DWM backdrop, as it causes 
        # opaque grey backgrounds on some systems if acrylic fails.
        _extend_frame_into_client_area(hwnd)
        success = _apply_dwm_backdrop(hwnd)

    # Step 4: Last resort — basic blur behind (Win10 older builds)
    if not success:
        success = _apply_blur_behind(hwnd, dark)

    if success:
        _ensure_interactive_window(hwnd)

    return success


def _extend_frame_into_client_area(hwnd: int) -> None:
    """Extend the DWM frame into the entire client area (-1 margins)."""
    try:
        dwm = windll.dwmapi
        margins = MARGINS(-1, -1, -1, -1)
        dwm.DwmExtendFrameIntoClientArea(HWND(hwnd), byref(margins))
    except (OSError, Exception):
        pass


def _set_dark_mode(hwnd: int) -> None:
    """Enable immersive dark mode on the window."""
    try:
        dwm = windll.dwmapi
        dark_val = c_int(1)
        dwm.DwmSetWindowAttribute(
            HWND(hwnd),
            DWORD(DWMWA_USE_IMMERSIVE_DARK_MODE),
            byref(dark_val),
            DWORD(sizeof(dark_val)),
        )
    except (OSError, Exception):
        pass


def _apply_dwm_backdrop(hwnd: int) -> bool:
    """Try DwmSetWindowAttribute with system backdrop types (Win11 22H2+)."""
    try:
        dwm = windll.dwmapi
    except OSError:
        return False

    try:
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
    """Acrylic blur using SetWindowCompositionAttribute (Win10 1803+, Win11)."""
    try:
        user32 = windll.user32
        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        SetWindowCompositionAttribute.argtypes = [HWND, c_void_p]
        SetWindowCompositionAttribute.restype = c_int
    except (OSError, AttributeError):
        return False

    # ABGR: 0xAA_BB_GG_RR — neutral charcoal/gray glass tint
    # Alpha ~0x8A (138/255), Blue 0x14 (20), Green 0x14 (20), Red 0x14 (20)
    if dark:
        gradient_color = 0x8A141414
    else:
        gradient_color = 0x82F0F0F0

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


def _apply_blur_behind(hwnd: int, dark: bool) -> bool:
    """Basic blur behind as last resort (older Win10 builds)."""
    try:
        user32 = windll.user32
        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        SetWindowCompositionAttribute.argtypes = [HWND, c_void_p]
        SetWindowCompositionAttribute.restype = c_int
    except (OSError, AttributeError):
        return False

    if dark:
        gradient_color = 0xCC141414
    else:
        gradient_color = 0xCCF0F0F0

    accent = ACCENTPOLICY()
    accent.AccentState = ACCENT_ENABLE_BLURBEHIND
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
