"""Native Win32 RegisterHotKey wrapper with a message-only window."""

from __future__ import annotations

import ctypes
from ctypes import WINFUNCTYPE, byref, c_int, c_void_p, windll
from ctypes.wintypes import DWORD, HINSTANCE, HWND, LPARAM, MSG, UINT, WPARAM

from PySide6.QtCore import QAbstractNativeEventFilter, QObject, Signal

# Win32 constants
WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
HOTKEY_ID = 1

HWND_MESSAGE = -3

user32 = windll.user32
kernel32 = windll.kernel32

LRESULT = ctypes.c_ssize_t  # pointer-sized signed int, matches Win32 LRESULT

user32.DefWindowProcW.restype = LRESULT
user32.DefWindowProcW.argtypes = [HWND, UINT, WPARAM, LPARAM]

WNDPROC = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)


class _HotkeyWindow:
    """Hidden message-only window that receives WM_HOTKEY."""

    def __init__(self, callback) -> None:
        self._callback = callback
        self._hwnd: int | None = None
        self._wndproc_ref = WNDPROC(self._window_proc)

    def create(self) -> bool:
        class_name = "GlassNotesHotkeyClass"
        hinstance = HINSTANCE(kernel32.GetModuleHandleW(None))

        from ctypes import Structure, c_int32, c_uint32, c_wchar_p

        class WNDCLASSEXW(Structure):
            _fields_ = [
                ("cbSize", c_uint32),
                ("style", c_uint32),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", c_int32),
                ("cbWndExtra", c_int32),
                ("hInstance", HINSTANCE),
                ("hIcon", c_void_p),
                ("hCursor", c_void_p),
                ("hbrBackground", c_void_p),
                ("lpszMenuName", c_wchar_p),
                ("lpszClassName", c_wchar_p),
                ("hIconSm", c_void_p),
            ]

        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.style = 0
        wc.lpfnWndProc = self._wndproc_ref
        wc.cbClsExtra = 0
        wc.cbWndExtra = 0
        wc.hInstance = hinstance
        wc.hIcon = None
        wc.hCursor = None
        wc.hbrBackground = None
        wc.lpszMenuName = None
        wc.lpszClassName = class_name
        wc.hIconSm = None

        atom = user32.RegisterClassExW(byref(wc))
        if atom == 0 and kernel32.GetLastError() != 1410:  # ERROR_CLASS_ALREADY_EXISTS
            return False

        hwnd = user32.CreateWindowExW(
            0,
            class_name,
            "GlassNotesHotkey",
            0,
            0,
            0,
            0,
            0,
            HWND(HWND_MESSAGE),
            None,
            hinstance,
            None,
        )
        if not hwnd:
            return False

        self._hwnd = int(hwnd)
        return True

    def _window_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_HOTKEY and wparam == HOTKEY_ID:
            if self._callback:
                self._callback()
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    @property
    def hwnd(self) -> int:
        return self._hwnd or 0

    def destroy(self) -> None:
        if self._hwnd:
            user32.DestroyWindow(HWND(self._hwnd))
            self._hwnd = None


class HotkeyNativeEventFilter(QAbstractNativeEventFilter):
    """Also listen for WM_HOTKEY on the Qt main window as a backup path."""

    def __init__(self, callback) -> None:
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, event_type, message):
        if event_type != b"windows_generic_MSG":
            return False, 0
        try:
            msg = MSG.from_address(int(message))
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                if self._callback:
                    self._callback()
                return True, 0
        except (TypeError, ValueError):
            pass
        return False, 0


class GlobalHotkeyManager(QObject):
    """Register Ctrl+Shift+N globally and emit activated() when pressed."""

    activated = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._hotkey_window: _HotkeyWindow | None = None
        self._filter: HotkeyNativeEventFilter | None = None
        self._registered = False

    def register(self) -> bool:
        """Create message window and register the global hotkey."""
        if self._registered:
            return True

        def on_hotkey():
            self.activated.emit()

        self._hotkey_window = _HotkeyWindow(on_hotkey)
        if not self._hotkey_window.create():
            return False

        vk_n = ord("N")
        ok = user32.RegisterHotKey(
            HWND(self._hotkey_window.hwnd),
            HOTKEY_ID,
            MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT,
            vk_n,
        )
        if not ok:
            self._hotkey_window.destroy()
            self._hotkey_window = None
            return False

        self._filter = HotkeyNativeEventFilter(on_hotkey)
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            app.installNativeEventFilter(self._filter)

        self._registered = True
        return True

    def unregister(self) -> None:
        """Release hotkey and destroy message window."""
        if self._hotkey_window and self._hotkey_window.hwnd:
            user32.UnregisterHotKey(HWND(self._hotkey_window.hwnd), HOTKEY_ID)

        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app and self._filter:
            app.removeNativeEventFilter(self._filter)

        if self._hotkey_window:
            self._hotkey_window.destroy()
            self._hotkey_window = None

        self._filter = None
        self._registered = False
