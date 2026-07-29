"""GlassNotes main sticky-note widget."""

from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QCursor, QFont, QPainterPath, QRegion
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.acrylic import apply_acrylic
from core.storage import load_config, save_config, save_notes
from ui import styles

FIXED_WIDTH = 288
COLLAPSED_SIZE = 48
HEADER_HEIGHT = 32
RESIZE_HANDLE_HEIGHT = 6
MIN_HEIGHT = 120
ANIMATION_MS = 150
SAVE_DEBOUNCE_MS = 500
CORNER_RADIUS = styles.CORNER_RADIUS
MIN_VISIBLE = 50


class HeaderBar(QWidget):
    """Draggable title bar with collapse and close buttons."""

    collapse_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("headerBar")
        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 6, 0)
        layout.setSpacing(2)

        title = QLabel("GlassNotes", self)
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addStretch()

        collapse_btn = QPushButton("−", self)
        collapse_btn.setObjectName("headerBtn")
        collapse_btn.setToolTip("Collapse")
        collapse_btn.clicked.connect(self.collapse_clicked.emit)
        layout.addWidget(collapse_btn)

        close_btn = QPushButton("×", self)
        close_btn.setObjectName("headerBtn")
        close_btn.setProperty("class", "close")
        close_btn.setObjectName("closeBtn")
        close_btn.setToolTip("Hide")
        close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            window = self.window()
            self._drag_pos = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            window = self.window()
            if hasattr(window, "move_window"):
                window.move_window(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)


class ResizeHandle(QFrame):
    """Bottom-edge vertical resize grip."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("resizeHandle")
        self.setCursor(QCursor(Qt.SizeVerCursor))
        self._dragging = False
        self._start_global_y = 0
        self._start_height = 0

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            window = self.window()
            self._dragging = True
            self._start_global_y = int(event.globalPosition().y())
            self._start_height = window.height()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            window = self.window()
            delta = int(event.globalPosition().y()) - self._start_global_y
            new_height = window._clamp_height(self._start_height + delta)
            window.resize(FIXED_WIDTH, new_height)
            if hasattr(window, "persist_geometry"):
                window.persist_geometry()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._dragging = False
        super().mouseReleaseEvent(event)


class GlassNotesWidget(QWidget):
    """Frameless always-on-top sticky note with collapse animation."""

    visibility_changed = Signal(bool)
    notes_saved = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("glassRoot")

        self._config = load_config()
        self._collapsed = bool(self._config.get("window", {}).get("collapsed", False))
        self._saved_height = int(self._config.get("window", {}).get("height", 320))
        self._saved_height = self._clamp_height(self._saved_height)
        self._use_fallback = False
        self._acrylic_applied = False
        self._visible_state = bool(self._config.get("visible", True))
        self._animating = False

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(SAVE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_save)

        self._animation = QPropertyAnimation(self, b"geometry", self)
        self._animation.setDuration(ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.finished.connect(self._on_animation_finished)

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedWidth(FIXED_WIDTH)

        self._build_ui()
        self._apply_styles()

        font = QFont()
        font.setFamilies(["Segoe UI Variable", "Segoe UI", "sans-serif"])
        font.setPointSize(10)
        self.setFont(font)

    def _build_ui(self) -> None:
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self._expanded_container = QWidget(self)
        expanded_layout = QVBoxLayout(self._expanded_container)
        expanded_layout.setContentsMargins(0, 0, 0, 0)
        expanded_layout.setSpacing(0)

        self._header = HeaderBar(self._expanded_container)
        self._header.collapse_clicked.connect(self.collapse)
        self._header.close_clicked.connect(self.hide_widget)
        expanded_layout.addWidget(self._header)

        self._editor = QPlainTextEdit(self._expanded_container)
        self._editor.setObjectName("noteEditor")
        self._editor.setFrameShape(QFrame.NoFrame)
        self._editor.setTabChangesFocus(False)
        self._editor.setPlaceholderText("Jot something down…")
        self._editor.textChanged.connect(self._schedule_save)
        expanded_layout.addWidget(self._editor, 1)

        self._resize_handle = ResizeHandle(self._expanded_container)
        expanded_layout.addWidget(self._resize_handle)

        self._root_layout.addWidget(self._expanded_container)

        self._collapsed_btn = QPushButton("N", self)
        self._collapsed_btn.setObjectName("collapsedIcon")
        self._collapsed_btn.setToolTip("Expand GlassNotes")
        self._collapsed_btn.clicked.connect(self.expand)
        self._root_layout.addWidget(self._collapsed_btn)
        self._collapsed_btn.hide()

    def _apply_styles(self) -> None:
        if self._collapsed:
            self.setStyleSheet(styles.collapsed_styles(self._use_fallback))
        else:
            self.setStyleSheet(styles.expanded_styles(self._use_fallback))

    def _max_height(self) -> int:
        screen = QApplication.primaryScreen()
        if screen:
            return max(MIN_HEIGHT, int(screen.availableGeometry().height() * 0.8))
        return 600

    def _clamp_height(self, height: int) -> int:
        return max(MIN_HEIGHT, min(height, self._max_height()))

    def initialize(self, note_text: str) -> None:
        """Load note content and restore window geometry."""
        self._editor.blockSignals(True)
        self._editor.setPlainText(note_text)
        self._editor.blockSignals(False)

        win = self._config.get("window", {})
        x = int(win.get("x", 100))
        y = int(win.get("y", 100))

        if self._collapsed:
            self.setFixedSize(COLLAPSED_SIZE, COLLAPSED_SIZE)
            self._expanded_container.hide()
            self._collapsed_btn.show()
            self._collapsed_btn.setFixedSize(COLLAPSED_SIZE, COLLAPSED_SIZE)
            self._root_layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.setFixedWidth(FIXED_WIDTH)
            self.setMinimumHeight(MIN_HEIGHT)
            self.setMaximumHeight(self._max_height())
            self.resize(FIXED_WIDTH, self._saved_height)
            self._expanded_container.show()
            self._collapsed_btn.hide()

        self.move(x, y)
        self._clamp_to_screen()
        self._update_rounded_mask()

        if self._visible_state:
            self.show()
        else:
            self.hide()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._apply_acrylic_effect)
        self._update_rounded_mask()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_rounded_mask()

    def _apply_acrylic_effect(self) -> None:
        if self._acrylic_applied:
            return
        hwnd = int(self.winId())
        ok = apply_acrylic(hwnd, dark=True)
        self._use_fallback = not ok
        self._acrylic_applied = True
        self._apply_styles()

    def _update_rounded_mask(self) -> None:
        path = QPainterPath()
        if self._collapsed:
            path.addEllipse(0, 0, self.width(), self.height())
        else:
            path.addRoundedRect(
                0, 0, self.width(), self.height(), CORNER_RADIUS, CORNER_RADIUS
            )
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def move_window(self, top_left: QPoint) -> None:
        self.move(top_left)
        self._clamp_to_screen()
        self.persist_geometry()

    def _clamp_to_screen(self) -> None:
        """Ensure at least MIN_VISIBLE px of the window is on a connected monitor."""
        screens = QApplication.screens()
        if not screens:
            return

        frame = self.frameGeometry()
        visible_on_any = False
        for screen in screens:
            available = screen.availableGeometry()
            intersection = frame.intersected(available)
            if intersection.width() >= MIN_VISIBLE and intersection.height() >= MIN_VISIBLE:
                visible_on_any = True
                break

        if visible_on_any:
            return

        primary = QApplication.primaryScreen()
        if not primary:
            return
        available = primary.availableGeometry()
        if self._collapsed:
            x = available.x() + (available.width() - COLLAPSED_SIZE) // 2
            y = available.y() + (available.height() - COLLAPSED_SIZE) // 2
            self.move(x, y)
        else:
            x = available.x() + (available.width() - FIXED_WIDTH) // 2
            y = available.y() + (available.height() - self.height()) // 2
            self.move(x, y)

    def persist_geometry(self) -> None:
        self._config.setdefault("window", {})
        pos = self.pos()
        self._config["window"]["x"] = pos.x()
        self._config["window"]["y"] = pos.y()
        if not self._collapsed:
            self._saved_height = self.height()
            self._config["window"]["height"] = self._saved_height
        self._config["window"]["collapsed"] = self._collapsed
        save_config(self._config)

    def _schedule_save(self) -> None:
        self._save_timer.start()

    def _flush_save(self) -> None:
        text = self._editor.toPlainText()
        save_notes(text)
        self.notes_saved.emit(text)

    def flush_pending_save(self) -> None:
        """Force immediate save (e.g. on quit)."""
        if self._save_timer.isActive():
            self._save_timer.stop()
        self._flush_save()

    def set_note_text(self, text: str) -> None:
        self._editor.blockSignals(True)
        self._editor.setPlainText(text)
        self._editor.blockSignals(False)

    def collapse(self) -> None:
        if self._collapsed or self._animating:
            return
        self._saved_height = self.height()
        self._collapsed = True
        self._run_collapse_animation(expanding=False)

    def expand(self) -> None:
        if not self._collapsed or self._animating:
            return
        self._collapsed = False
        self._run_collapse_animation(expanding=True)

    def _run_collapse_animation(self, expanding: bool) -> None:
        self._animating = True
        start = self.geometry()
        pos = self.pos()

        if expanding:
            end = QRect(pos.x(), pos.y(), FIXED_WIDTH, self._clamp_height(self._saved_height))
        else:
            end = QRect(pos.x(), pos.y(), COLLAPSED_SIZE, COLLAPSED_SIZE)

        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._pending_expand = expanding
        self._animation.start()

    def _on_animation_finished(self) -> None:
        expanding = getattr(self, "_pending_expand", False)
        self._animating = False

        if expanding:
            self.setFixedWidth(FIXED_WIDTH)
            self.setMinimumHeight(MIN_HEIGHT)
            self.setMaximumHeight(self._max_height())
            self.resize(FIXED_WIDTH, self._clamp_height(self._saved_height))
            self._expanded_container.show()
            self._collapsed_btn.hide()
            self._root_layout.setContentsMargins(0, 0, 0, 0)
            self._editor.setFocus()
        else:
            self.setFixedSize(COLLAPSED_SIZE, COLLAPSED_SIZE)
            self._expanded_container.hide()
            self._collapsed_btn.show()
            self._root_layout.setContentsMargins(0, 0, 0, 0)

        self._apply_styles()
        self._update_rounded_mask()
        self.persist_geometry()

    def toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide_widget()
        else:
            self.show_widget()

    def show_widget(self) -> None:
        self._clamp_to_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        if not self._collapsed:
            self._editor.setFocus()
        self._visible_state = True
        self._config["visible"] = True
        save_config(self._config)
        self.visibility_changed.emit(True)

    def hide_widget(self) -> None:
        self.hide()
        self._visible_state = False
        self._config["visible"] = False
        save_config(self._config)
        self.visibility_changed.emit(False)

    def is_widget_visible(self) -> bool:
        return self._visible_state and self.isVisible()
