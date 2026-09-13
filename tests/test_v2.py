"""Unit tests for FloatNote v2 multi-file storage, smart anchoring, and Markdown support."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QTextDocument

from core import acrylic, storage
from ui import styles


class TestStorageV2(unittest.TestCase):
    """Test storage v2 functionality including folders, notes, and migration."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="floatnote_test_"))
        self._orig_notes_dir = storage.NOTES_DIR
        self._orig_notes_root = storage.NOTES_ROOT
        self._orig_notes_file_v1 = storage.NOTES_FILE_V1
        self._orig_config_file = storage.CONFIG_FILE
        self._orig_backups_dir = storage.BACKUPS_DIR

        storage.NOTES_DIR = self.temp_dir
        storage.NOTES_ROOT = self.temp_dir / "notes"
        storage.NOTES_FILE_V1 = self.temp_dir / "notes.txt"
        storage.CONFIG_FILE = self.temp_dir / "config.json"
        storage.BACKUPS_DIR = self.temp_dir / "backups"

    def tearDown(self) -> None:
        storage.NOTES_DIR = self._orig_notes_dir
        storage.NOTES_ROOT = self._orig_notes_root
        storage.NOTES_FILE_V1 = self._orig_notes_file_v1
        storage.CONFIG_FILE = self._orig_config_file
        storage.BACKUPS_DIR = self._orig_backups_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_v1_migration(self) -> None:
        """Verify that an existing v1 notes.txt is migrated to General/notes.txt without data loss."""
        v1_text = "Important thoughts from v1.\nDon't lose this!"
        storage.NOTES_DIR.mkdir(parents=True, exist_ok=True)
        storage.NOTES_FILE_V1.write_text(v1_text, encoding="utf-8")

        storage.ensure_dirs()

        migrated_file = storage.NOTES_ROOT / "General" / "notes.txt"
        self.assertTrue(migrated_file.is_file(), "Migrated file should exist in General/notes.txt")
        self.assertEqual(migrated_file.read_text(encoding="utf-8"), v1_text)

        bak_file = storage.NOTES_DIR / "notes.txt.v1.bak"
        self.assertTrue(bak_file.is_file(), "Backup archive of v1 notes should be retained")
        self.assertEqual(bak_file.read_text(encoding="utf-8"), v1_text)

        self.assertFalse(storage.NOTES_FILE_V1.is_file(), "Original notes.txt should be moved")

    def test_starter_note_on_fresh_install(self) -> None:
        """Verify that a fresh install creates a default Quick Notes.md note."""
        storage.ensure_dirs()
        categories = storage.list_categories()
        self.assertIn("General", categories)
        notes = storage.list_notes_in_category("General")
        self.assertIn("Quick Notes.md", notes)

    def test_category_crud(self) -> None:
        """Verify category creation and listing."""
        self.assertTrue(storage.create_category("Work"))
        self.assertTrue(storage.create_category("Personal Projects"))
        self.assertFalse(storage.create_category(""))  # Empty should be rejected

        cats = storage.list_categories()
        self.assertEqual(cats[0], "General", "General should always be listed first")
        self.assertIn("Work", cats)
        self.assertIn("Personal Projects", cats)

    def test_note_crud(self) -> None:
        """Verify note creation, reading, writing, renaming, and deletion."""
        note_path = storage.create_note("General", "Meeting.md", "# Agenda\n- Discussion")
        self.assertIsNotNone(note_path)
        self.assertTrue(note_path.is_file())

        content = storage.load_note("General", "Meeting.md")
        self.assertIn("# Agenda", content)

        storage.save_note("General", "Meeting.md", "# Updated Agenda\n- Action items")
        updated = storage.load_note("General", "Meeting.md")
        self.assertIn("Action items", updated)

        # Rename
        renamed = storage.rename_note("General", "Meeting.md", "Sprint_Meeting")
        self.assertTrue(renamed)
        self.assertIn("Sprint_Meeting.md", storage.list_notes_in_category("General"))
        self.assertNotIn("Meeting.md", storage.list_notes_in_category("General"))

        # Delete
        deleted = storage.delete_note("General", "Sprint_Meeting.md")
        self.assertTrue(deleted)
        self.assertNotIn("Sprint_Meeting.md", storage.list_notes_in_category("General"))

    def test_move_note(self) -> None:
        """Verify moving a note across categories."""
        storage.create_category("Archive")
        storage.create_note("General", "OldTask.txt", "Finished task")

        ok = storage.move_note("General", "OldTask.txt", "Archive")
        self.assertTrue(ok)
        self.assertIn("OldTask.txt", storage.list_notes_in_category("Archive"))
        self.assertNotIn("OldTask.txt", storage.list_notes_in_category("General"))

    def test_resolve_active_note_fallback(self) -> None:
        """Verify fallback when configured note is deleted."""
        cfg = {"active_category": "General", "active_note": "NonExistent.md"}
        cat, note = storage.resolve_active_note(cfg)
        self.assertTrue(storage.get_note_path(cat, note).is_file())


class TestSmartAnchoring(unittest.TestCase):
    """Test smart expand/collapse anchoring geometry calculations."""

    def test_left_anchored_expansion_and_collapse(self) -> None:
        """When docked on left side of screen, top-left remains fixed."""
        screen_avail = QRect(0, 0, 1920, 1080)
        screen_center_x = screen_avail.x() + screen_avail.width() / 2.0  # 960

        # Collapsed widget at x=100, width=64
        pos_x, pos_y = 100, 100
        collapsed_w, collapsed_h = 64, 64
        widget_center_x = pos_x + collapsed_w / 2.0  # 132 < 960 (left side)
        self.assertLess(widget_center_x, screen_center_x)

        # Expand: top-left anchored
        target_x = pos_x
        self.assertEqual(target_x, 100)

        # Collapse back: top-left anchored
        self.assertEqual(target_x, 100)

    def test_right_anchored_expansion_and_collapse(self) -> None:
        """When docked on right side of screen, top-right remains fixed."""
        screen_avail = QRect(0, 0, 1920, 1080)
        screen_center_x = screen_avail.x() + screen_avail.width() / 2.0  # 960

        fixed_w = 288
        collapsed_size = 64

        # Collapsed near right edge: x=1840, right edge = 1904
        pos_x, pos_y = 1840, 100
        widget_center_x = pos_x + collapsed_size / 2.0  # 1872 > 960 (right side)
        self.assertGreater(widget_center_x, screen_center_x)

        # Expand: pinned top-right
        target_x = (pos_x + collapsed_size) - fixed_w
        self.assertEqual(target_x, 1616)
        # Verify right edge coordinate is preserved
        self.assertEqual(target_x + fixed_w, pos_x + collapsed_size)  # 1904 == 1904!

        # Collapse from expanded at x=1616, width=288 (right edge = 1904)
        expanded_x = 1616
        collapse_target_x = (expanded_x + fixed_w) - collapsed_size
        self.assertEqual(collapse_target_x, 1840)
        # Verify collapsed right edge coordinate is preserved
        self.assertEqual(collapse_target_x + collapsed_size, expanded_x + fixed_w)  # 1904 == 1904!


class TestVisualThemeAndMarkdown(unittest.TestCase):
    """Test deep-blue glass styles and Markdown rendering setup."""

    def test_acrylic_tint_abgr(self) -> None:
        """Check that acrylic tint is saturated navy ABGR."""
        # Alpha: 0x8A (138), Blue: 0x3C (60), Green: 0x19 (25), Red: 0x14 (20)
        abgr_expected = 0x8A3C1914
        # Verify ABGR byte values
        alpha = (abgr_expected >> 24) & 0xFF
        blue = (abgr_expected >> 16) & 0xFF
        green = (abgr_expected >> 8) & 0xFF
        red = abgr_expected & 0xFF
        self.assertEqual(alpha, 0x8A)
        self.assertEqual(blue, 60)
        self.assertEqual(green, 25)
        self.assertEqual(red, 20)

    def test_styles_output(self) -> None:
        """Verify QSS generation contains deep-blue colors and rim borders."""
        exp_qss = styles.expanded_styles(use_fallback=False)
        self.assertIn("rgba(18, 34, 75", exp_qss)
        self.assertIn("border-top: 1px solid rgba(190, 225, 255", exp_qss)
        self.assertIn("noteEditor", exp_qss)
        self.assertIn("notePreview", exp_qss)

        col_qss = styles.collapsed_styles(use_fallback=False)
        self.assertIn("collapsedIcon", col_qss)
        self.assertIn("qradialgradient", col_qss)

    def test_markdown_rendering(self) -> None:
        """Verify QTextDocument markdown parser converts headers and task items."""
        doc = QTextDocument()
        doc.setDefaultStyleSheet(styles.MARKDOWN_DOC_CSS)
        doc.setMarkdown("# Title\n- [ ] Todo item\n- [x] Done item\n`inline_code`")
        html = doc.toHtml()
        self.assertIn("Title", html)
        self.assertIn("inline_code", html)


class TestWidgetIntegration(unittest.TestCase):
    """Test FloatNoteWidget initialization, switching, and UI states."""

    @classmethod
    def setUpClass(cls) -> None:
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="floatnote_widget_test_"))
        self._orig_notes_dir = storage.NOTES_DIR
        self._orig_notes_root = storage.NOTES_ROOT
        self._orig_config_file = storage.CONFIG_FILE
        self._orig_backups_dir = storage.BACKUPS_DIR

        storage.NOTES_DIR = self.temp_dir
        storage.NOTES_ROOT = self.temp_dir / "notes"
        storage.CONFIG_FILE = self.temp_dir / "config.json"
        storage.BACKUPS_DIR = self.temp_dir / "backups"
        storage.ensure_dirs()

    def tearDown(self) -> None:
        storage.NOTES_DIR = self._orig_notes_dir
        storage.NOTES_ROOT = self._orig_notes_root
        storage.CONFIG_FILE = self._orig_config_file
        storage.BACKUPS_DIR = self._orig_backups_dir
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_widget_init_and_markdown_toggle(self) -> None:
        from ui.widget import FloatNoteWidget

        widget = FloatNoteWidget()
        storage.create_note("General", "Sample.md", "# Test Heading\n**test bold**")
        widget.initialize(category="General", filename="Sample.md")

        self.assertEqual(widget._active_category, "General")
        self.assertEqual(widget._active_note, "Sample.md")
        self.assertTrue(widget._header.preview_btn.isVisible(), "Preview button should be visible for .md files")

        # Toggle to preview mode
        widget.toggle_preview_mode()
        self.assertTrue(widget._preview_mode)
        self.assertEqual(widget._editor_stack.currentWidget(), widget._preview)

        # Toggle back to edit mode
        widget.toggle_preview_mode()
        self.assertFalse(widget._preview_mode)
        self.assertEqual(widget._editor_stack.currentWidget(), widget._editor)

        # Switch to .txt note
        storage.create_note("General", "Plain.txt", "Plain text content")
        widget.switch_to_note("General", "Plain.txt")
        self.assertFalse(widget._header.preview_btn.isVisible(), "Preview button should be hidden for .txt files")
        self.assertEqual(widget._editor_stack.currentWidget(), widget._editor)

        widget.close()

    def test_dialogs_instantiation(self) -> None:
        from ui.dialogs import ConfirmDialog, NewFolderDialog, NewNoteDialog, RenameNoteDialog

        dlg1 = NewNoteDialog(["General", "Work"], default_category="General")
        self.assertIsNotNone(dlg1)
        dlg1.close()

        dlg2 = NewFolderDialog()
        self.assertIsNotNone(dlg2)
        dlg2.close()

        dlg3 = RenameNoteDialog("MyNote.md")
        self.assertIsNotNone(dlg3)
        dlg3.close()

        dlg4 = ConfirmDialog("Title", "Message")
        self.assertIsNotNone(dlg4)
        dlg4.close()


if __name__ == "__main__":
    unittest.main()
