"""Dialogs for note and category creation, renaming, and deletion in FloatNote."""

from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core import storage
from ui import styles


class BaseGlassDialog(QDialog):
    """Base dialog styled with FloatNote's deep-blue glass theme."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(styles.DIALOG_STYLE)
        self.setFixedWidth(280)


class NewNoteDialog(BaseGlassDialog):
    """Dialog to create a new note with folder and format selection."""

    def __init__(
        self,
        categories: list[str],
        default_category: str = "General",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Note")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title_lbl = QLabel("Create New Note", self)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #a5d2ff;")
        layout.addWidget(title_lbl)

        # Name input
        name_lbl = QLabel("Note Name:", self)
        layout.addWidget(name_lbl)
        self._name_edit = QLineEdit(self)
        self._name_edit.setPlaceholderText("e.g. Ideas, Project notes")
        layout.addWidget(self._name_edit)

        # Folder / Category selection
        cat_lbl = QLabel("Folder:", self)
        layout.addWidget(cat_lbl)
        self._cat_combo = QComboBox(self)
        for cat in categories:
            self._cat_combo.addItem(cat)
        self._cat_combo.addItem("+ New Folder...")
        idx = self._cat_combo.findText(default_category)
        if idx >= 0:
            self._cat_combo.setCurrentIndex(idx)
        self._cat_combo.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self._cat_combo)

        # Extra input for new folder if selected
        self._new_folder_edit = QLineEdit(self)
        self._new_folder_edit.setPlaceholderText("New folder name")
        self._new_folder_edit.hide()
        layout.addWidget(self._new_folder_edit)

        # Format selector
        format_lbl = QLabel("Format:", self)
        layout.addWidget(format_lbl)
        format_row = QHBoxLayout()
        format_row.setSpacing(16)
        self._md_radio = QRadioButton("Markdown (.md)", self)
        self._md_radio.setChecked(True)
        self._txt_radio = QRadioButton("Plain text (.txt)", self)
        self._btn_group = QButtonGroup(self)
        self._btn_group.addButton(self._md_radio)
        self._btn_group.addButton(self._txt_radio)
        format_row.addWidget(self._md_radio)
        format_row.addWidget(self._txt_radio)
        format_row.addStretch()
        layout.addLayout(format_row)

        # Error label
        self._error_lbl = QLabel("", self)
        self._error_lbl.setStyleSheet("color: #ff8a8a; font-size: 11px;")
        self._error_lbl.hide()
        layout.addWidget(self._error_lbl)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        create_btn = QPushButton("Create", self)
        create_btn.setObjectName("dialogBtn")
        create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(create_btn)

        layout.addLayout(btn_row)

    def _on_combo_changed(self, index: int) -> None:
        if self._cat_combo.currentText() == "+ New Folder...":
            self._new_folder_edit.show()
            self._new_folder_edit.setFocus()
        else:
            self._new_folder_edit.hide()
        self.adjustSize()

    def _on_create(self) -> None:
        raw_name = self._name_edit.text().strip()
        if not raw_name:
            self._show_error("Note name cannot be empty")
            return

        clean_name = storage.sanitize_name(raw_name)
        if not clean_name:
            self._show_error("Invalid note name")
            return

        # Ensure correct extension
        ext = ".md" if self._md_radio.isChecked() else ".txt"
        if not (clean_name.endswith(".md") or clean_name.endswith(".txt")):
            clean_name += ext

        # Resolve category
        if self._cat_combo.currentText() == "+ New Folder...":
            raw_folder = self._new_folder_edit.text().strip()
            if not raw_folder:
                self._show_error("Folder name cannot be empty")
                return
            category = storage.sanitize_name(raw_folder)
        else:
            category = self._cat_combo.currentText()

        # Check collision
        if storage.get_note_path(category, clean_name).is_file():
            self._show_error("A note with this name already exists")
            return

        self._result = (category, clean_name)
        self.accept()

    def _show_error(self, msg: str) -> None:
        self._error_lbl.setText(msg)
        self._error_lbl.show()
        self.adjustSize()

    def get_result(self) -> tuple[str, str]:
        return getattr(self, "_result", (storage.DEFAULT_CATEGORY, "note.md"))


class NewFolderDialog(BaseGlassDialog):
    """Dialog to create a new folder/category."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Folder")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title_lbl = QLabel("Create New Folder", self)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #a5d2ff;")
        layout.addWidget(title_lbl)

        name_lbl = QLabel("Folder Name:", self)
        layout.addWidget(name_lbl)
        self._name_edit = QLineEdit(self)
        self._name_edit.setPlaceholderText("e.g. Work, Personal, Snippets")
        layout.addWidget(self._name_edit)

        self._error_lbl = QLabel("", self)
        self._error_lbl.setStyleSheet("color: #ff8a8a; font-size: 11px;")
        self._error_lbl.hide()
        layout.addWidget(self._error_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        create_btn = QPushButton("Create", self)
        create_btn.setObjectName("dialogBtn")
        create_btn.clicked.connect(self._on_create)
        btn_row.addWidget(create_btn)

        layout.addLayout(btn_row)

    def _on_create(self) -> None:
        raw_name = self._name_edit.text().strip()
        clean = storage.sanitize_name(raw_name)
        if not clean:
            self._error_lbl.setText("Folder name cannot be empty")
            self._error_lbl.show()
            return
        self._result = clean
        self.accept()

    def get_result(self) -> str:
        return getattr(self, "_result", "New Folder")


class RenameNoteDialog(BaseGlassDialog):
    """Dialog to rename a note."""

    def __init__(self, current_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Rename Note")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title_lbl = QLabel("Rename Note", self)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #a5d2ff;")
        layout.addWidget(title_lbl)

        # Display clean stem in edit field
        self._orig_ext = Path(current_name).suffix
        stem = Path(current_name).stem

        name_lbl = QLabel("New Name:", self)
        layout.addWidget(name_lbl)
        self._name_edit = QLineEdit(self)
        self._name_edit.setText(stem)
        self._name_edit.selectAll()
        layout.addWidget(self._name_edit)

        self._error_lbl = QLabel("", self)
        self._error_lbl.setStyleSheet("color: #ff8a8a; font-size: 11px;")
        self._error_lbl.hide()
        layout.addWidget(self._error_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        rename_btn = QPushButton("Rename", self)
        rename_btn.setObjectName("dialogBtn")
        rename_btn.clicked.connect(self._on_rename)
        btn_row.addWidget(rename_btn)

        layout.addLayout(btn_row)

    def _on_rename(self) -> None:
        raw_name = self._name_edit.text().strip()
        clean = storage.sanitize_name(raw_name)
        if not clean:
            self._error_lbl.setText("Note name cannot be empty")
            self._error_lbl.show()
            return

        if not Path(clean).suffix and self._orig_ext:
            clean += self._orig_ext

        self._result = clean
        self.accept()

    def get_result(self) -> str:
        return getattr(self, "_result", "")


class ConfirmDialog(BaseGlassDialog):
    """Confirmation prompt dialog for deletions."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Delete",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title_lbl = QLabel(title, self)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffa8a8;")
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message, self)
        msg_lbl.setWordWrap(True)
        layout.addWidget(msg_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        action_btn = QPushButton(confirm_text, self)
        action_btn.setObjectName("dialogBtn")
        action_btn.setStyleSheet(
            "QPushButton#dialogBtn { background: rgba(220, 40, 50, 160); border: 1px solid rgba(255, 120, 120, 80); }"
            "QPushButton#dialogBtn:hover { background: rgba(240, 55, 65, 200); }"
        )
        action_btn.clicked.connect(self.accept)
        btn_row.addWidget(action_btn)

        layout.addLayout(btn_row)
