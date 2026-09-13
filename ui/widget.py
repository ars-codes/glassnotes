"""FloatNote v2 main sticky-note widget with multi-file and Markdown preview support."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QCursor,
    QFont,
    QIcon,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QStyle,
    QStyleOption,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core.acrylic import apply_acrylic
from core import storage
from ui import styles
from ui.dialogs import ConfirmDialog, NewFolderDialog, NewNoteDialog, RenameNoteDialog

FIXED_WIDTH = 288
COLLAPSED_SIZE = 64
HEADER_HEIGHT = 32
RESIZE_HANDLE_HEIGHT = 6
MIN_HEIGHT = 120
ANIMATION_MS = 150
SAVE_DEBOUNCE_MS = 500
CORNER_RADIUS = styles.CORNER_RADIUS
MIN_VISIBLE = 50


def _load_app_icon() -> QIcon:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent

    # Check for requested floatnote_icon.ico first
    ico_v2 = base / "assets" / "floatnote_icon.ico"
    if ico_v2.is_file():
        return QIcon(str(ico_v2))

    ico = base / "assets" / "icon.ico"
    if ico.is_file():
        return QIcon(str(ico))

    png = base / "floatnote.png"
    if png.is_file():
        return QIcon(str(png))
    return QIcon()


def _get_rounded_icon(icon: QIcon, size: int) -> QIcon:
    if icon.isNull():
        return icon
    pixmap = icon.pixmap(QSize(size, size))
    if pixmap.isNull():
        return icon

    rounded = QPixmap(size, size)
    rounded.fill(Qt.GlobalColor.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)

    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return QIcon(rounded)


class HeaderBar(QWidget):
    """Draggable title bar with file menu, title, preview toggle, collapse and close buttons."""

    menu_clicked = Signal()
    preview_clicked = Signal()
    collapse_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("headerBar")
        self._drag_pos: QPoint | None = None
        self._main_window: FloatNoteWidget | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(2)

        self.menu_btn = QPushButton("≡", self)
        self.menu_btn.setObjectName("menuBtn")
        self.menu_btn.setToolTip("File Menu (Ctrl+M)")
        self.menu_btn.clicked.connect(self.menu_clicked.emit)
        layout.addWidget(self.menu_btn)

        self.title_label = QLabel("FloatNote", self)
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label, 1)

        self.preview_btn = QPushButton("👁", self)
        self.preview_btn.setObjectName("previewBtn")
        self.preview_btn.setToolTip("Toggle Markdown Preview (Ctrl+P)")
        self.preview_btn.clicked.connect(self.preview_clicked.emit)
        layout.addWidget(self.preview_btn)

        collapse_btn = QPushButton("−", self)
        collapse_btn.setObjectName("headerBtn")
        collapse_btn.setToolTip("Collapse")
        collapse_btn.clicked.connect(self.collapse_clicked.emit)
        layout.addWidget(collapse_btn)

        close_btn = QPushButton("×", self)
        close_btn.setProperty("class", "close")
        close_btn.setObjectName("closeBtn")
        close_btn.setToolTip("Hide")
        close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self._main_window if self._main_window is not None else self.window()
            self._drag_pos = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            window = self._main_window if self._main_window is not None else self.window()
            if hasattr(window, "move_window"):
                window.move_window(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)


class MarkdownBrowser(QTextBrowser):
    """QTextBrowser that returns to edit mode upon double click."""

    double_clicked = Signal()

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class ResizeHandle(QFrame):
    """Bottom-edge vertical resize grip."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("resizeHandle")
        self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self._dragging = False
        self._start_global_y = 0
        self._start_height = 0
        self._main_window: FloatNoteWidget | None = None

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self._main_window if self._main_window is not None else self.window()
            self._dragging = True
            self._start_global_y = int(event.globalPosition().y())
            self._start_height = window.height()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            window = self._main_window if self._main_window is not None else self.window()
            delta = int(event.globalPosition().y()) - self._start_global_y
            if hasattr(window, "_clamp_height"):
                new_height = window._clamp_height(self._start_height + delta)
            else:
                new_height = self._start_height + delta
            window.resize(FIXED_WIDTH, new_height)
            if hasattr(window, "persist_geometry"):
                window.persist_geometry()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._dragging = False
        super().mouseReleaseEvent(event)


class DraggableButton(QPushButton):
    """A button that can be clicked or dragged to move its parent window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._is_dragging = False
        self._main_window = None

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self._main_window if self._main_window is not None else self.window()
            self._drag_pos = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
            self._is_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            window = self._main_window if self._main_window is not None else self.window()
            delta = event.globalPosition().toPoint() - window.frameGeometry().topLeft() - self._drag_pos
            if delta.manhattanLength() > 3:
                self._is_dragging = True
                if hasattr(window, "move_window"):
                    window.move_window(event.globalPosition().toPoint() - self._drag_pos)
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        if self._is_dragging:
            self._is_dragging = False
            self.setDown(False)
            return
        super().mouseReleaseEvent(event)


class FloatNoteWidget(QWidget):
    """Frameless always-on-top sticky note with smart expand/collapse anchoring."""

    visibility_changed = Signal(bool)
    notes_saved = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("glassRoot")

        self._config = storage.load_config()
        self._collapsed = bool(self._config.get("window", {}).get("collapsed", False))
        self._saved_height = int(self._config.get("window", {}).get("height", 320))
        self._saved_height = self._clamp_height(self._saved_height)
        self._use_fallback = False
        self._acrylic_applied = False
        self._visible_state = bool(self._config.get("visible", True))
        self._animating = False

        self._active_category, self._active_note = storage.resolve_active_note(self._config)
        self._preview_mode = bool(self._config.get("preview_mode", False))

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(SAVE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_save)

        self._animation = QPropertyAnimation(self, b"geometry", self)
        self._animation.setDuration(ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._animation.finished.connect(self._on_animation_finished)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(FIXED_WIDTH)

        self._build_ui()
        self._setup_shortcuts()
        self._apply_styles()

        font = QFont()
        font.setFamilies(["Segoe UI Variable", "Segoe UI", "sans-serif"])
        font.setPointSize(10)
        self.setFont(font)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def _build_ui(self) -> None:
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self._expanded_container = QWidget(self)
        expanded_layout = QVBoxLayout(self._expanded_container)
        expanded_layout.setContentsMargins(0, 0, 0, 0)
        expanded_layout.setSpacing(0)

        self._header = HeaderBar(self._expanded_container)
        self._header._main_window = self
        self._header.menu_clicked.connect(self._open_file_menu)
        self._header.preview_clicked.connect(self.toggle_preview_mode)
        self._header.collapse_clicked.connect(self.collapse)
        self._header.close_clicked.connect(self.hide_widget)
        expanded_layout.addWidget(self._header)

        # Stacked editor and Markdown preview
        self._editor_stack = QStackedWidget(self._expanded_container)

        self._editor = QPlainTextEdit(self._editor_stack)
        self._editor.setObjectName("noteEditor")
        self._editor.setFrameShape(QFrame.Shape.NoFrame)
        self._editor.setTabChangesFocus(False)
        self._editor.setPlaceholderText("Jot something down…")
        self._editor.textChanged.connect(self._schedule_save)
        self._editor_stack.addWidget(self._editor)

        self._preview = MarkdownBrowser(self._editor_stack)
        self._preview.setObjectName("notePreview")
        self._preview.setFrameShape(QFrame.Shape.NoFrame)
        self._preview.setOpenExternalLinks(True)
        self._preview.document().setDefaultStyleSheet(styles.MARKDOWN_DOC_CSS)
        self._preview.double_clicked.connect(lambda: self.set_preview_mode(False))
        self._editor_stack.addWidget(self._preview)

        expanded_layout.addWidget(self._editor_stack, 1)

        self._resize_handle = ResizeHandle(self._expanded_container)
        self._resize_handle._main_window = self
        expanded_layout.addWidget(self._resize_handle)

        self._root_layout.addWidget(self._expanded_container)

        # Collapsed circular icon button
        self._collapsed_btn = DraggableButton(self)
        self._collapsed_btn._main_window = self
        self._collapsed_btn.setObjectName("collapsedIcon")
        app_icon = _load_app_icon()
        if not app_icon.isNull():
            rounded_icon = _get_rounded_icon(app_icon, COLLAPSED_SIZE)
            self._collapsed_btn.setIcon(rounded_icon)
            self._collapsed_btn.setIconSize(QSize(COLLAPSED_SIZE, COLLAPSED_SIZE))
        else:
            self._collapsed_btn.setText("N")
        self._collapsed_btn.setToolTip("Expand FloatNote")
        self._collapsed_btn.clicked.connect(self.expand)
        self._root_layout.addWidget(self._collapsed_btn)
        self._collapsed_btn.hide()

    def _setup_shortcuts(self) -> None:
        # Ctrl+P / Ctrl+E toggle preview
        QShortcut(QKeySequence("Ctrl+P"), self, self.toggle_preview_mode)
        QShortcut(QKeySequence("Ctrl+E"), self, self.toggle_preview_mode)
        # Ctrl+N create new note
        QShortcut(QKeySequence("Ctrl+N"), self, self._create_new_note)
        # Ctrl+M open file menu
        QShortcut(QKeySequence("Ctrl+M"), self, self._open_file_menu)
        # Ctrl+S flush save immediately
        QShortcut(QKeySequence("Ctrl+S"), self, self.flush_pending_save)

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

    def initialize(self, category: str | None = None, filename: str | None = None) -> None:
        """Load note content and restore window geometry."""
        if category and filename:
            self._active_category = category
            self._active_note = filename
        else:
            self._active_category, self._active_note = storage.resolve_active_note(self._config)

        self._load_active_note_content()

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

        if self._visible_state:
            self.show()
        else:
            self.hide()

    def _load_active_note_content(self) -> None:
        """Load content of current active note into editor and setup preview."""
        content = storage.load_note(self._active_category, self._active_note)
        self._editor.blockSignals(True)
        self._editor.setPlainText(content)
        self._editor.blockSignals(False)

        # Update header title
        self._update_header_title()

        # Handle Markdown vs Plain text
        is_md = self._active_note.lower().endswith(".md")
        self._header.preview_btn.setVisible(is_md)

        if is_md and self._preview_mode:
            self.set_preview_mode(True)
        else:
            self.set_preview_mode(False)

    def _update_header_title(self) -> None:
        display_name = Path(self._active_note).stem
        self._header.title_label.setText(display_name)
        self._header.title_label.setToolTip(f"{self._active_category} / {self._active_note}")

    def switch_to_note(self, category: str, filename: str) -> None:
        """Flush current note, switch active note, and load its content."""
        self.flush_pending_save()
        self._active_category = category
        self._active_note = filename
        self._config["active_category"] = category
        self._config["active_note"] = filename
        storage.save_config(self._config)

        self._load_active_note_content()

    def toggle_preview_mode(self) -> None:
        """Toggle Markdown preview mode (for .md files only)."""
        if not self._active_note.lower().endswith(".md"):
            return
        self.set_preview_mode(not self._preview_mode)

    def set_preview_mode(self, enabled: bool) -> None:
        """Enable or disable Markdown rendered view."""
        self._preview_mode = enabled
        self._config["preview_mode"] = enabled
        storage.save_config(self._config)

        if enabled and self._active_note.lower().endswith(".md"):
            self.flush_pending_save()
            text = self._editor.toPlainText()
            self._preview.setMarkdown(text)
            self._preview.document().setDefaultStyleSheet(styles.MARKDOWN_DOC_CSS)
            self._editor_stack.setCurrentWidget(self._preview)
            self._header.preview_btn.setText("✏️")
            self._header.preview_btn.setToolTip("Edit Note (Ctrl+P)")
            self._preview.setFocus()
        else:
            self._editor_stack.setCurrentWidget(self._editor)
            self._header.preview_btn.setText("👁")
            self._header.preview_btn.setToolTip("Preview Markdown (Ctrl+P)")
            if not self._collapsed:
                self._editor.setFocus()

    def _open_file_menu(self) -> None:
        """Display the file management and folder organization menu."""
        menu = QMenu(self)
        menu.setStyleSheet(styles.MENU_STYLE)

        new_note_act = QAction("📄  New Note...", menu)
        new_note_act.setShortcut("Ctrl+N")
        new_note_act.triggered.connect(self._create_new_note)
        menu.addAction(new_note_act)

        new_folder_act = QAction("📁  New Folder...", menu)
        new_folder_act.triggered.connect(self._create_new_folder)
        menu.addAction(new_folder_act)

        menu.addSeparator()

        # Folders and their files
        categories = storage.list_categories()
        for cat in categories:
            cat_menu = QMenu(f"📁 {cat}", menu)
            cat_menu.setStyleSheet(styles.MENU_STYLE)
            notes = storage.list_notes_in_category(cat)
            if not notes:
                empty_act = QAction("(empty)", cat_menu)
                empty_act.setEnabled(False)
                cat_menu.addAction(empty_act)
            else:
                for note in notes:
                    is_active = (cat == self._active_category and note == self._active_note)
                    prefix = "✓  " if is_active else "    "
                    note_act = QAction(f"{prefix}{note}", cat_menu)
                    note_act.triggered.connect(
                        lambda checked=False, c=cat, n=note: self.switch_to_note(c, n)
                    )
                    cat_menu.addAction(note_act)
            menu.addMenu(cat_menu)

        menu.addSeparator()

        rename_act = QAction("✏️  Rename Active Note...", menu)
        rename_act.triggered.connect(self._rename_active_note)
        menu.addAction(rename_act)

        delete_act = QAction("🗑️  Delete Active Note...", menu)
        delete_act.triggered.connect(self._delete_active_note)
        menu.addAction(delete_act)

        menu.addSeparator()

        open_folder_act = QAction("📂  Open Notes Folder", menu)
        open_folder_act.triggered.connect(self._open_notes_folder)
        menu.addAction(open_folder_act)

        # Popup menu under menu button
        btn_rect = self._header.menu_btn.rect()
        global_pos = self._header.menu_btn.mapToGlobal(btn_rect.bottomLeft())
        menu.exec(global_pos)

    def _create_new_note(self) -> None:
        cats = storage.list_categories()
        dlg = NewNoteDialog(cats, default_category=self._active_category, parent=self)
        dlg.move(self.x() + 4, self.y() + 30)
        if dlg.exec():
            cat, name = dlg.get_result()
            storage.create_note(cat, name, "")
            self.switch_to_note(cat, name)

    def _create_new_folder(self) -> None:
        dlg = NewFolderDialog(parent=self)
        dlg.move(self.x() + 4, self.y() + 30)
        if dlg.exec():
            folder_name = dlg.get_result()
            storage.create_category(folder_name)

    def _rename_active_note(self) -> None:
        dlg = RenameNoteDialog(self._active_note, parent=self)
        dlg.move(self.x() + 4, self.y() + 30)
        if dlg.exec():
            new_name = dlg.get_result()
            if new_name and new_name != self._active_note:
                self.flush_pending_save()
                ok = storage.rename_note(self._active_category, self._active_note, new_name)
                if ok:
                    self._active_note = new_name
                    self._config["active_note"] = new_name
                    storage.save_config(self._config)
                    self._update_header_title()
                    is_md = self._active_note.lower().endswith(".md")
                    self._header.preview_btn.setVisible(is_md)

    def _delete_active_note(self) -> None:
        dlg = ConfirmDialog(
            "Delete Note",
            f"Delete '{self._active_note}' permanently?",
            confirm_text="Delete",
            parent=self,
        )
        dlg.move(self.x() + 4, self.y() + 30)
        if dlg.exec():
            cat = self._active_category
            note = self._active_note
            storage.delete_note(cat, note)
            # Resolve next note
            next_cat, next_note = storage.resolve_active_note(self._config)
            self.switch_to_note(next_cat, next_note)

    def _open_notes_folder(self) -> None:
        storage.ensure_dirs()
        os.startfile(str(storage.NOTES_DIR))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._apply_acrylic_effect)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

    def _apply_acrylic_effect(self) -> None:
        if self._acrylic_applied:
            return
        hwnd = self.winId()
        ok = apply_acrylic(hwnd, dark=True)
        self._use_fallback = not ok
        self._acrylic_applied = True
        self._apply_styles()

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
        storage.save_config(self._config)

    def _schedule_save(self) -> None:
        self._save_timer.start()

    def _flush_save(self) -> None:
        text = self._editor.toPlainText()
        storage.save_note(self._active_category, self._active_note, text)
        self.notes_saved.emit(text)
        if self._preview_mode and self._active_note.lower().endswith(".md"):
            self._preview.setMarkdown(text)
            self._preview.document().setDefaultStyleSheet(styles.MARKDOWN_DOC_CSS)

    def flush_pending_save(self) -> None:
        """Force immediate save (e.g. on note switch or quit)."""
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
        """Run collapse/expand animation with smart anchoring based on screen side."""
        self._animating = True
        start = self.geometry()
        pos = self.pos()

        screen = QApplication.screenAt(self.geometry().center())
        if not screen:
            screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        # Determine if widget is on the right side of the current monitor
        widget_center_x = self.x() + self.width() / 2.0
        screen_center_x = avail.x() + avail.width() / 2.0
        is_right_side = widget_center_x > screen_center_x

        target_h = self._clamp_height(self._saved_height)

        if expanding:
            if is_right_side:
                # Anchor top-right: keep right edge at pos.x() + COLLAPSED_SIZE
                target_x = (pos.x() + COLLAPSED_SIZE) - FIXED_WIDTH
            else:
                # Anchor top-left: keep left edge at pos.x()
                target_x = pos.x()
            target_y = pos.y()

            # Clamp to available monitor area so it never renders off-screen
            target_x = max(avail.x(), min(target_x, avail.x() + avail.width() - FIXED_WIDTH))
            target_y = max(avail.y(), min(target_y, avail.y() + avail.height() - target_h))
            end = QRect(target_x, target_y, FIXED_WIDTH, target_h)
        else:
            if is_right_side:
                # Anchor top-right: keep right edge at pos.x() + FIXED_WIDTH
                target_x = (pos.x() + FIXED_WIDTH) - COLLAPSED_SIZE
            else:
                # Anchor top-left: keep left edge at pos.x()
                target_x = pos.x()
            target_y = pos.y()

            # Clamp to available monitor area
            target_x = max(avail.x(), min(target_x, avail.x() + avail.width() - COLLAPSED_SIZE))
            target_y = max(avail.y(), min(target_y, avail.y() + avail.height() - COLLAPSED_SIZE))
            end = QRect(target_x, target_y, COLLAPSED_SIZE, COLLAPSED_SIZE)

        self._pending_end_rect = end
        self._pending_expand = expanding

        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()

    def _on_animation_finished(self) -> None:
        expanding = getattr(self, "_pending_expand", False)
        end = getattr(self, "_pending_end_rect", self.geometry())
        self._animating = False

        if expanding:
            self.setFixedWidth(FIXED_WIDTH)
            self.setMinimumHeight(MIN_HEIGHT)
            self.setMaximumHeight(self._max_height())
            self.setGeometry(end)
            self._expanded_container.show()
            self._collapsed_btn.hide()
            self._root_layout.setContentsMargins(0, 0, 0, 0)
            if self._preview_mode and self._active_note.lower().endswith(".md"):
                self._preview.setFocus()
            else:
                self._editor.setFocus()
        else:
            self.setFixedSize(COLLAPSED_SIZE, COLLAPSED_SIZE)
            self.setGeometry(end)
            self._expanded_container.hide()
            self._collapsed_btn.show()
            self._root_layout.setContentsMargins(0, 0, 0, 0)

        self._apply_styles()
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
            if self._preview_mode and self._active_note.lower().endswith(".md"):
                self._preview.setFocus()
            else:
                self._editor.setFocus()
        self._visible_state = True
        self._config["visible"] = True
        storage.save_config(self._config)
        self.visibility_changed.emit(True)

    def hide_widget(self) -> None:
        self.hide()
        self._visible_state = False
        self._config["visible"] = False
        storage.save_config(self._config)
        self.visibility_changed.emit(False)

    def is_widget_visible(self) -> bool:
        return self._visible_state and self.isVisible()
