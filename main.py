"""FloatNote — lightweight sticky-notes widget for Windows."""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path

# High-DPI setup must happen before QApplication is created.
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from core import autostart, storage
from core.hotkey import GlobalHotkeyManager
from ui.widget import FloatNoteWidget

APP_NAME = "FloatNote"


def resource_path(relative: str) -> Path:
    """Resolve bundled or dev asset paths."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent
    return base / relative


def load_app_icon() -> QIcon:
    ico = resource_path("assets/icon.ico")
    if ico.is_file():
        return QIcon(str(ico))
    png = Path(__file__).resolve().parent / "floatnote.png"
    if png.is_file():
        return QIcon(str(png))
    return QIcon()


def open_notes_folder() -> None:
    folder = storage.NOTES_DIR
    storage.ensure_dirs()
    os.startfile(str(folder))


def main() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    storage.ensure_dirs()

    icon = load_app_icon()
    app.setWindowIcon(icon)

    widget = FloatNoteWidget()
    widget.setWindowIcon(icon)
    widget.initialize(storage.load_notes())

    hotkey = GlobalHotkeyManager()
    hotkey.activated.connect(widget.toggle_visibility)
    hotkey.register()

    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip(APP_NAME)

    menu = QMenu()

    show_hide_action = QAction("Show", menu)
    hide_action = QAction("Hide", menu)
    autostart_action = QAction("Start with Windows", menu)
    autostart_action.setCheckable(True)
    open_folder_action = QAction("Open Notes Folder", menu)
    exit_action = QAction("Exit", menu)

    menu.addAction(show_hide_action)
    menu.addAction(hide_action)
    menu.addSeparator()
    menu.addAction(autostart_action)
    menu.addAction(open_folder_action)
    menu.addSeparator()
    menu.addAction(exit_action)

    tray.setContextMenu(menu)

    def refresh_autostart_check() -> None:
        autostart_action.setChecked(autostart.is_enabled())

    def on_autostart_toggled(checked: bool) -> None:
        exe_path = autostart.get_executable_path()
        if checked:
            ok = autostart.enable(exe_path)
            if not ok:
                autostart_action.blockSignals(True)
                autostart_action.setChecked(False)
                autostart_action.blockSignals(False)
        else:
            autostart.disable()
        refresh_autostart_check()

    def sync_tray_show_hide(visible: bool) -> None:
        show_hide_action.setVisible(not visible)
        hide_action.setVisible(visible)

    def on_show() -> None:
        widget.show_widget()

    def on_hide() -> None:
        widget.hide_widget()

    def on_exit() -> None:
        widget.flush_pending_save()
        storage.create_backup()
        hotkey.unregister()
        app.quit()

    show_hide_action.triggered.connect(on_show)
    hide_action.triggered.connect(on_hide)
    autostart_action.triggered.connect(on_autostart_toggled)
    open_folder_action.triggered.connect(open_notes_folder)
    exit_action.triggered.connect(on_exit)
    widget.visibility_changed.connect(sync_tray_show_hide)

    tray.activated.connect(
        lambda reason: widget.toggle_visibility()
        if reason == QSystemTrayIcon.ActivationReason.Trigger
        else None
    )

    refresh_autostart_check()
    sync_tray_show_hide(widget.is_widget_visible())

    if not QSystemTrayIcon.isSystemTrayAvailable():
        widget.show_widget()
    else:
        tray.show()

    def on_about_to_quit() -> None:
        widget.flush_pending_save()
        storage.create_backup()
        hotkey.unregister()

    app.aboutToQuit.connect(on_about_to_quit)

    # Allow Ctrl+C to terminate the Qt event loop cleanly from a console.
    try:
        from PySide6.QtCore import QTimer
        signal.signal(signal.SIGINT, lambda sig, frame: app.quit())
        sig_timer = QTimer()
        sig_timer.start(500)
        sig_timer.timeout.connect(lambda: None)
    except Exception:
        pass

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
